"""MediaPipe/model-backed hand tracking loop for runtime control."""

from __future__ import annotations

import time
from threading import Event, Thread
from typing import Any, Callable

import numpy as np

from backend.runtime_state import RuntimeState, runtime_state
from backend.hand_runtime import config
from backend.hand_runtime.classifier import HandGestureClassifier
from backend.hand_runtime.gesture_state import GestureActionState
from backend.hand_runtime.mouse import MouseController


GestureCallback = Callable[[str, dict[str, Any], bool], dict[str, Any]]

LABEL_TO_EVENT = {
    "open_hand": "open_palm_move",
    "fist": "pinch_hold",
    "one_finger": "pinch_index",
    "two_fingers": "pinch_middle",
    "three_up": "three_up",
    "three_down": "three_down",
    "three_left": "swipe_left",
    "three_right": "swipe_right",
}

EVENT_COOLDOWNS = {
    "pinch_index": 0.45,
    "pinch_middle": 0.45,
    "three_up": 0.12,
    "three_down": 0.12,
    "swipe_left": 0.55,
    "swipe_right": 0.55,
}

try:
    import cv2  # type: ignore[import-not-found]

    CV2_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    cv2 = None
    CV2_AVAILABLE = False

try:
    import mediapipe as mp  # type: ignore[import-not-found]

    MEDIAPIPE_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    mp = None
    MEDIAPIPE_AVAILABLE = False


class HandTrackerService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state
        self._hands: Any | None = None
        self._classifier: HandGestureClassifier | None = None
        self._gestures: GestureActionState | None = None
        self._mouse: MouseController | None = None
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._callback: GestureCallback | None = None
        self._last_event = "none"
        self._last_event_at: dict[str, float] = {}
        self._last_frame_at = time.perf_counter()
        self._hand_was_present = False

    @property
    def active(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> dict[str, str | bool]:
        return {"status": self.state.hand_status, "active": self.active, "mock": False}

    def start(self, camera_service, on_gesture: GestureCallback | None = None) -> dict[str, str | bool]:
        if self.active:
            return self.status()

        self._ensure_runtime()
        self._callback = on_gesture
        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, args=(camera_service,), daemon=True, name="acv-hand-tracker")
        self._thread.start()
        self.state.hand_status = "Hand tracker starting"
        self.state.add_log("system", self.state.hand_status)
        return self.status()

    def stop(self) -> dict[str, str | bool]:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        if self._gestures is not None:
            self._gestures.handle_hand_lost()
        if self._hands is not None:
            self._hands.close()
        self._hands = None
        self._classifier = None
        self._gestures = None
        self._mouse = None
        self._hand_was_present = False
        self.state.hand_landmarks = []
        self.state.hand_status = "Hand tracker stopped"
        self.state.add_log("system", self.state.hand_status)
        return self.status()

    def _ensure_runtime(self) -> None:
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV is not installed. Run: py -3 -m pip install -r backend\\requirements.txt")
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe is not installed. Run: py -3 -m pip install -r backend\\requirements.txt")

        self._classifier = HandGestureClassifier()
        self._mouse = MouseController()
        self._gestures = GestureActionState(self._mouse)
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

    def _run_loop(self, camera_service) -> None:
        assert self._classifier is not None
        assert self._gestures is not None
        assert self._hands is not None

        while not self._stop_event.is_set():
            started = time.perf_counter()
            ok, frame = camera_service.read()
            if not ok or frame is None:
                self.state.hand_status = "Camera frame unavailable"
                time.sleep(0.05)
                continue

            try:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self._hands.process(rgb_frame)
                hands = getattr(results, "multi_hand_landmarks", None) or []
                if not hands:
                    if self._hand_was_present:
                        self.state.add_log("detection", "Hand lost")
                    self._hand_was_present = False
                    self.state.hand_status = "No hand detected"
                    self.state.hand_landmarks = []
                    self._classifier.reset()
                    self._gestures.handle_hand_lost()
                    self._update_timing(started)
                    continue

                if not self._hand_was_present:
                    self._classifier.reset()
                    self._gestures.prepare_hand_reacquire()
                    self.state.add_log("detection", "Hand detected")
                self._hand_was_present = True
                self.state.hand_status = "Hand detected"
                hand_landmarks = hands[0]
                self.state.hand_landmarks = self._serialize_landmarks(hand_landmarks.landmark)
                frame_h, frame_w = frame.shape[:2]
                box = self._get_bounding_box(hand_landmarks.landmark, frame_w, frame_h)
                if box is None:
                    self._classifier.reset()
                    self._gestures.handle_hand_lost()
                    self._update_timing(started)
                    continue

                x_min, y_min, x_max, y_max = box
                crop = frame[y_min:y_max, x_min:x_max]
                if crop.size == 0:
                    self._classifier.reset()
                    self._gestures.handle_hand_lost()
                    self._update_timing(started)
                    continue

                prediction = self._classifier.predict(hand_landmarks, self._preprocess_crop(crop))
                stable_label = str(prediction["stable_label"])
                raw_label = str(prediction["label"])
                event = self._apply_and_resolve_event(stable_label, raw_label, hand_landmarks.landmark)
                self.state.current_gesture = event or stable_label
                self.state.current_action = self._action_label(event, stable_label)
                if event:
                    self._emit_event(event, hand_landmarks.landmark, stable_label, execute=False)
                self._update_timing(started)
            except Exception as exc:  # pragma: no cover - defensive runtime guard
                self.state.hand_status = "Hand tracker error"
                self.state.last_error = f"Hand tracker error: {exc}"
                self.state.add_log("error", self.state.last_error)
                time.sleep(0.1)

    def _get_bounding_box(self, landmarks, image_width: int, image_height: int):
        xs = [int(point.x * image_width) for point in landmarks]
        ys = [int(point.y * image_height) for point in landmarks]
        x_min = max(0, min(xs) - config.BOUNDING_BOX_MARGIN)
        y_min = max(0, min(ys) - config.BOUNDING_BOX_MARGIN)
        x_max = min(image_width, max(xs) + config.BOUNDING_BOX_MARGIN)
        y_max = min(image_height, max(ys) + config.BOUNDING_BOX_MARGIN)
        if x_max <= x_min or y_max <= y_min:
            return None
        return x_min, y_min, x_max, y_max

    def _preprocess_crop(self, crop):
        processed = cv2.resize(crop, (config.PROCESS_SIZE, config.PROCESS_SIZE), interpolation=cv2.INTER_AREA)
        processed = cv2.GaussianBlur(processed, (3, 3), 0)
        return cv2.convertScaleAbs(processed, alpha=1.1, beta=8)

    def _apply_and_resolve_event(self, stable_label: str, raw_label: str, landmarks) -> str | None:
        assert self._gestures is not None
        was_dragging = self._gestures.dragging
        self._gestures.apply(stable_label, raw_label, landmarks)
        is_dragging = self._gestures.dragging

        if is_dragging and not was_dragging:
            return "drag_start"
        if is_dragging:
            return "drag_move"
        if was_dragging and not is_dragging:
            return "drag_release"
        return LABEL_TO_EVENT.get(stable_label)

    def _emit_event(self, event: str, landmarks, label: str, execute: bool) -> None:
        now = time.perf_counter()
        cooldown = EVENT_COOLDOWNS.get(event, 0.0)
        is_continuous = event in {"open_palm_move", "pinch_hold", "drag_move"}
        if not is_continuous and now - self._last_event_at.get(event, 0.0) < cooldown:
            return
        if not is_continuous and event == self._last_event:
            return
        if event == "drag_move" and now - self._last_event_at.get(event, 0.0) < 0.2:
            return

        payload = self._event_payload(landmarks)
        if self._gestures is not None:
            payload["pinch_distance"] = self._gestures.last_pinch_ratio or payload["pinch_distance"]
        self.state.current_gesture = event
        self.state.workflow_confidence = payload["confidence"]
        self.state.add_log("gesture", f"{label} -> {event}")
        self._last_event = event
        self._last_event_at[event] = now
        if self._callback is not None:
            self._callback(event, payload, execute)

    def _event_payload(self, landmarks) -> dict[str, Any]:
        wrist = landmarks[0]
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]
        palm_x = float(np.mean([wrist.x, index_mcp.x, middle_mcp.x, ring_mcp.x, pinky_mcp.x]))
        palm_y = float(np.mean([wrist.y, index_mcp.y, middle_mcp.y, ring_mcp.y, pinky_mcp.y]))
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        palm_size = max(float(np.hypot(middle_mcp.x - wrist.x, middle_mcp.y - wrist.y)), 1e-6)
        pinch_distance = float(np.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y) / palm_size)

        screen_w, screen_h = self._screen_size()
        x = int(max(0.0, min(1.0, palm_x)) * screen_w)
        y = int(max(0.0, min(1.0, palm_y)) * screen_h)
        return {
            "x": x,
            "y": y,
            "hand_x": palm_x,
            "hand_y": palm_y,
            "pinch_distance": pinch_distance,
            "confidence": max(0.0, min(1.0, 1.0 - min(pinch_distance, 1.0))),
        }

    def _serialize_landmarks(self, landmarks) -> list[dict[str, float]]:
        return [
            {
                "x": float(max(0.0, min(1.0, point.x))),
                "y": float(max(0.0, min(1.0, point.y))),
                "z": float(point.z),
            }
            for point in list(landmarks)[:21]
        ]

    def _action_label(self, event: str | None, stable_label: str) -> str:
        labels = {
            "open_palm_move": "Move pointer",
            "pinch_index": "Left click",
            "pinch_middle": "Right click",
            "drag_start": "Drag start",
            "drag_move": "Drag move",
            "drag_release": "Drag release",
            "three_up": "Scroll up",
            "three_down": "Scroll down",
            "swipe_left": "Switch tab left",
            "swipe_right": "Switch tab right",
        }
        return labels.get(event or "", stable_label)

    def _screen_size(self) -> tuple[int, int]:
        try:
            import pyautogui  # type: ignore[import-not-found]

            width, height = pyautogui.size()
            return int(width), int(height)
        except Exception:
            return 1920, 1080

    def _update_timing(self, started: float) -> None:
        now = time.perf_counter()
        elapsed = max(now - started, 1e-6)
        self.state.fps = int(round(1.0 / elapsed))
        self.state.latency = int(round(elapsed * 1000))
        self._last_frame_at = now
