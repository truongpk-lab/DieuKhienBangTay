"""Phase 13 smoke test for pinch drag-drop state machine."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.gesture_state_machine import PinchDragDropStateMachine


class FakeMouseAdapter:
    def __init__(self):
        self.calls = []

    def mouse_down(self):
        self.calls.append(("mouse_down",))

    def move(self, x, y):
        self.calls.append(("move", x, y))

    def mouse_up(self):
        self.calls.append(("mouse_up",))


def make_landmarks(thumb_tip, index_tip, wrist=(0.5, 0.5)):
    landmarks = [{"x": wrist[0], "y": wrist[1]} for _ in range(21)]
    landmarks[0] = {"x": wrist[0], "y": wrist[1]}
    landmarks[4] = {"x": thumb_tip[0], "y": thumb_tip[1]}
    landmarks[5] = {"x": wrist[0] - 0.12, "y": wrist[1] - 0.2}
    landmarks[8] = {"x": index_tip[0], "y": index_tip[1]}
    landmarks[9] = {"x": wrist[0], "y": wrist[1] - 1.0}
    landmarks[13] = {"x": wrist[0] + 0.12, "y": wrist[1] - 0.2}
    landmarks[17] = {"x": wrist[0] + 0.2, "y": wrist[1] - 0.05}
    return landmarks


def event_names(events):
    return [event.gesture_event for event in events]


def main():
    mouse = FakeMouseAdapter()
    state_machine = PinchDragDropStateMachine(
        mouse_adapter=mouse,
        start_threshold=0.35,
        hold_threshold=0.25,
        release_threshold=0.45,
        min_hold_frames=2,
    )

    open_hand = make_landmarks((0.2, 0.0), (0.8, 0.0))
    assert event_names(state_machine.update(open_hand)) == []

    pinch_start = make_landmarks((0.40, 0.0), (0.70, 0.0))
    assert event_names(state_machine.update(pinch_start)) == ["pinch_start"]
    assert state_machine.state == "pinch_candidate"

    pinch_hold = make_landmarks((0.45, 0.0), (0.65, 0.0))
    assert event_names(state_machine.update(pinch_hold)) == ["pinch_hold", "drag_start"]
    assert state_machine.state == "holding"

    drag_move = make_landmarks((0.50, 0.0), (0.70, 0.0), wrist=(0.6, 0.55))
    assert event_names(state_machine.update(drag_move)) == ["drag_move"]
    assert state_machine.state == "dragging"

    drag_release = make_landmarks((0.2, 0.0), (0.8, 0.0), wrist=(0.6, 0.55))
    assert event_names(state_machine.update(drag_release)) == ["drag_release"]
    assert state_machine.state == "released"

    assert mouse.calls == [
        ("mouse_down",),
        ("move", 0.6, 0.55),
        ("mouse_up",),
    ]
    print("phase13 fake sequence ok")


if __name__ == "__main__":
    main()
