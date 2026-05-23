"""Phase 14 smoke tests for profile-specific gesture actions."""

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


class FakeKeyboardController:
    def __init__(self):
        self.calls = []

    def press(self, key):
        self.calls.append(("press", key))

    def release(self, key):
        self.calls.append(("release", key))

    def hotkey(self, *keys):
        self.calls.append(("hotkey", keys))


def execute_events(profile_id, events):
    profile = ProfileManager().load_profile(profile_id)
    mouse = FakeMouseAdapter()
    keyboard = FakeKeyboardController()
    mapper = ActionMapper(profile=profile, mouse_adapter=mouse, keyboard_controller=keyboard)

    for event in events:
        result = mapper.execute_gesture_event(event)
        assert result is not None, f"missing mapping for {profile_id}: {event}"
        assert result["status"] == "executed", result

    return mouse.calls, keyboard.calls


def test_office_profile_actions():
    mouse_calls, keyboard_calls = execute_events(
        "office",
        [
            {"gesture_event": "three_up"},
            {"gesture_event": "three_down"},
            {"gesture_event": "pinch_hold"},
            {"gesture_event": "drag_move", "x": 640, "y": 360},
            {"gesture_event": "drag_release"},
            {"gesture_event": "three_finger_left_right"},
            {"gesture_event": "pinch_hold_left"},
            {"gesture_event": "pinch_hold_right"},
        ],
    )

    assert mouse_calls == [
        ("scroll", 5),
        ("scroll", -5),
        ("mouse_down",),
        ("move", 640, 360),
        ("mouse_up",),
    ]
    assert keyboard_calls == [
        ("hotkey", ("ctrl", "tab")),
        ("hotkey", ("ctrl", "c")),
        ("hotkey", ("ctrl", "v")),
    ]


def test_entertainment_profile_actions():
    _, keyboard_calls = execute_events(
        "entertainment",
        [
            {"gesture_event": "open_close_palm"},
            {"gesture_event": "swipe_right"},
            {"gesture_event": "swipe_left"},
            {"gesture_event": "swipe_up"},
            {"gesture_event": "swipe_down"},
            {"gesture_event": "open_palm_hold"},
            {"gesture_event": "two_finger_swipe_right"},
            {"gesture_event": "two_finger_swipe_left"},
        ],
    )

    assert keyboard_calls == [
        ("hotkey", ("space",)),
        ("hotkey", ("media_next",)),
        ("hotkey", ("media_previous",)),
        ("hotkey", ("volume_up",)),
        ("hotkey", ("volume_down",)),
        ("hotkey", ("f",)),
        ("hotkey", ("right",)),
        ("hotkey", ("left",)),
    ]


def test_game_2d_profile_actions():
    _, keyboard_calls = execute_events(
        "game_2d",
        [
            {"gesture_event": "tilt_left"},
            {"gesture_event": "tilt_right"},
            {"gesture_event": "swipe_up"},
            {"gesture_event": "swipe_down"},
            {"gesture_event": "rapid_punch"},
            {"gesture_event": "swipe_double"},
            {"gesture_event": "pinch_hold"},
        ],
    )

    assert keyboard_calls == [
        ("press", "a"),
        ("press", "d"),
        ("press", "space"),
        ("press", "s"),
        ("press", "j"),
        ("press", "shift"),
        ("press", "u"),
    ]


def main():
    test_office_profile_actions()
    test_entertainment_profile_actions()
    test_game_2d_profile_actions()
    print("phase14 fake profile actions ok")


if __name__ == "__main__":
    main()
