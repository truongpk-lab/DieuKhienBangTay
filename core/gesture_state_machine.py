"""Pinch drag-drop gesture state machine.

This module turns hand landmarks into small gesture events. Mouse effects stay
behind ActionMapper or MouseControlAdapter so the existing controller behavior
is preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any


THUMB_TIP_ID = 4
INDEX_TIP_ID = 8
WRIST_ID = 0
PALM_CENTER_IDS = (0, 5, 9, 13, 17)
PALM_SIZE_IDS = (0, 9)
EPSILON = 1e-6


@dataclass(frozen=True)
class GestureStateEvent:
    gesture_event: str
    state: str
    pinch_distance: float
    hand_position: tuple[float, float]
    payload: dict[str, Any]
    result: Any = None


class PinchDragDropStateMachine:
    """Detect pinch-hold drag-drop lifecycle from one hand's 21 landmarks."""

    def __init__(
        self,
        action_mapper=None,
        mouse_adapter=None,
        start_threshold: float = 0.34,
        hold_threshold: float = 0.28,
        release_threshold: float = 0.46,
        min_hold_frames: int = 3,
        hand_position_source: str = "wrist",
    ):
        if min_hold_frames < 1:
            raise ValueError("min_hold_frames must be >= 1")
        if hold_threshold > start_threshold:
            raise ValueError("hold_threshold must be <= start_threshold")
        if release_threshold <= hold_threshold:
            raise ValueError("release_threshold must be > hold_threshold")

        self.action_mapper = action_mapper
        self.mouse_adapter = mouse_adapter
        self.start_threshold = float(start_threshold)
        self.hold_threshold = float(hold_threshold)
        self.release_threshold = float(release_threshold)
        self.min_hold_frames = int(min_hold_frames)
        self.hand_position_source = hand_position_source
        self.state = "idle"
        self.hold_frames = 0
        self.last_hand_position: tuple[float, float] | None = None

    def reset(self) -> None:
        self.state = "idle"
        self.hold_frames = 0
        self.last_hand_position = None

    def update(self, landmarks) -> list[GestureStateEvent]:
        """Process one landmark frame and return emitted gesture events."""

        metrics = self.extract_metrics(landmarks)
        pinch_distance = metrics["pinch_distance"]
        hand_position = metrics["hand_position"]
        events: list[GestureStateEvent] = []

        if self.state == "released":
            self.state = "idle"

        if pinch_distance > self.release_threshold:
            if self.state in {"pinch_candidate", "holding", "dragging"}:
                event_name = "drag_release" if self.state in {"holding", "dragging"} else "pinch_cancel"
                events.append(self._emit(event_name, pinch_distance, hand_position))
                self.state = "released" if event_name == "drag_release" else "idle"
            self.hold_frames = 0
            self.last_hand_position = None
            return events

        if self.state == "idle":
            if pinch_distance <= self.start_threshold:
                self.state = "pinch_candidate"
                self.hold_frames = 1
                self.last_hand_position = hand_position
                events.append(self._emit("pinch_start", pinch_distance, hand_position))
            return events

        if self.state == "pinch_candidate":
            if pinch_distance <= self.hold_threshold:
                self.hold_frames += 1
            else:
                self.hold_frames = max(1, self.hold_frames)

            if self.hold_frames >= self.min_hold_frames:
                self.state = "holding"
                self.last_hand_position = hand_position
                events.append(self._emit("pinch_hold", pinch_distance, hand_position))
                events.append(self._emit("drag_start", pinch_distance, hand_position, dispatch=False))
            return events

        if self.state in {"holding", "dragging"}:
            self.state = "dragging"
            self.last_hand_position = hand_position
            events.append(self._emit("drag_move", pinch_distance, hand_position))
            return events

        return events

    def extract_metrics(self, landmarks) -> dict[str, Any]:
        points = [self._point_xy(point) for point in landmarks]
        if len(points) <= max(INDEX_TIP_ID, *PALM_CENTER_IDS):
            raise ValueError("PinchDragDropStateMachine requires 21 hand landmarks")

        palm_size = self._distance(points[PALM_SIZE_IDS[0]], points[PALM_SIZE_IDS[1]])
        if palm_size < EPSILON:
            palm_size = self._bounding_box_size(points)
        if palm_size < EPSILON:
            palm_size = 1.0

        pinch_distance = (
            self._distance(points[THUMB_TIP_ID], points[INDEX_TIP_ID]) / palm_size
        )
        hand_position = self._hand_position(points)

        return {
            "pinch_distance": float(pinch_distance),
            "hand_position": hand_position,
            "palm_size": float(palm_size),
        }

    def _hand_position(self, points: list[tuple[float, float]]) -> tuple[float, float]:
        if self.hand_position_source == "palm_center":
            count = float(len(PALM_CENTER_IDS))
            return (
                sum(points[index][0] for index in PALM_CENTER_IDS) / count,
                sum(points[index][1] for index in PALM_CENTER_IDS) / count,
            )
        return points[WRIST_ID]

    def _emit(
        self,
        event_name: str,
        pinch_distance: float,
        hand_position: tuple[float, float],
        dispatch: bool = True,
    ) -> GestureStateEvent:
        payload = {
            "gesture_event": event_name,
            "x": hand_position[0],
            "y": hand_position[1],
            "pinch_distance": pinch_distance,
            "state": self.state,
        }
        result = self._dispatch(event_name, payload) if dispatch else None
        return GestureStateEvent(
            gesture_event=event_name,
            state=self.state,
            pinch_distance=pinch_distance,
            hand_position=hand_position,
            payload=payload,
            result=result,
        )

    def _dispatch(self, event_name: str, payload: dict[str, Any]):
        if self.action_mapper is not None:
            return self.action_mapper.handle_event(payload)

        if self.mouse_adapter is None:
            return None

        if event_name == "pinch_hold":
            return self.mouse_adapter.mouse_down()
        if event_name == "drag_move":
            return self.mouse_adapter.move(payload["x"], payload["y"])
        if event_name == "drag_release":
            return self.mouse_adapter.mouse_up()
        return None

    def _point_xy(self, point) -> tuple[float, float]:
        if isinstance(point, dict):
            return float(point["x"]), float(point["y"])
        if hasattr(point, "x") and hasattr(point, "y"):
            return float(point.x), float(point.y)
        return float(point[0]), float(point[1])

    def _distance(self, first: tuple[float, float], second: tuple[float, float]) -> float:
        return hypot(first[0] - second[0], first[1] - second[1])

    def _bounding_box_size(self, points: list[tuple[float, float]]) -> float:
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return hypot(max(xs) - min(xs), max(ys) - min(ys))
