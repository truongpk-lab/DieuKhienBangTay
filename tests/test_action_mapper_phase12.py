"""Phase 12 smoke tests for ActionMapper profile-to-adapter execution."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profiles.action_mapper import ActionMapper
from profiles.profile_manager import ProfileManager


class FakeMouseAdapter:
    def __init__(self):
        self.calls = []

    def move(self, x, y):
        self.calls.append(("move", x, y))

    def left_click(self, clicks=1):
        self.calls.append(("left_click", clicks))

    def right_click(self, clicks=1):
        self.calls.append(("right_click", clicks))

    def scroll(self, amount):
        self.calls.append(("scroll", amount))

    def mouse_down(self):
        self.calls.append(("mouse_down",))

    def mouse_up(self):
        self.calls.append(("mouse_up",))


def main():
    profile = ProfileManager().load_profile("office")
    mouse = FakeMouseAdapter()
    mapper = ActionMapper(profile=profile, mouse_adapter=mouse)

    events = [
        {"gesture_event": "pinch_tap"},
        {"gesture_event": "two_finger_tap"},
        {"gesture_event": "three_up"},
        {"gesture_event": "three_down"},
        {"gesture_event": "pinch_hold"},
        {"gesture_event": "drag_move", "x": 640, "y": 360},
        {"gesture_event": "drag_release"},
    ]

    for event in events:
        result = mapper.execute_gesture_event(event)
        assert result is not None, f"missing mapping for {event['gesture_event']}"
        assert result["status"] == "executed", result

    assert mouse.calls == [
        ("left_click", 1),
        ("right_click", 1),
        ("scroll", 5),
        ("scroll", -5),
        ("mouse_down",),
        ("move", 640, 360),
        ("mouse_up",),
    ]
    print("phase12 fake events ok")


if __name__ == "__main__":
    main()
