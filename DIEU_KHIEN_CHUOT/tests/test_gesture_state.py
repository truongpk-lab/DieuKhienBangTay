import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
DIEU_ROOT = Path(__file__).resolve().parents[1]
for path in (REPO_ROOT, DIEU_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hand_mouse.actions import DryRunMouseController
from hand_mouse.gesture_state import GestureActionState


def make_landmarks(pinch=False):
    points = [SimpleNamespace(x=0.5, y=0.6, z=0.0) for _ in range(21)]
    points[0] = SimpleNamespace(x=0.5, y=0.8, z=0.0)
    points[5] = SimpleNamespace(x=0.45, y=0.55, z=0.0)
    points[9] = SimpleNamespace(x=0.5, y=0.5, z=0.0)
    points[13] = SimpleNamespace(x=0.55, y=0.55, z=0.0)
    points[17] = SimpleNamespace(x=0.6, y=0.62, z=0.0)

    points[4] = SimpleNamespace(x=0.35, y=0.42, z=0.0)
    points[8] = SimpleNamespace(x=0.58, y=0.25, z=0.0)
    if pinch:
        points[4] = SimpleNamespace(x=0.47, y=0.42, z=0.0)
        points[8] = SimpleNamespace(x=0.49, y=0.42, z=0.0)
    return points


class GestureActionStateTest(unittest.TestCase):
    def make_state(self):
        mouse = DryRunMouseController()
        return GestureActionState(mouse), mouse

    def test_pinch_starts_holds_and_releases_drag(self):
        state, mouse = self.make_state()

        for step in range(3):
            state.apply("open_hand", "open_hand", make_landmarks(pinch=True), now=10.0 + step * 0.1)

        self.assertEqual(mouse.events.count(("mouse_down",)), 1)
        self.assertTrue(state.dragging)

        state.apply("open_hand", "open_hand", make_landmarks(pinch=False), now=10.5)

        self.assertIn(("mouse_up",), mouse.events)
        self.assertFalse(state.dragging)

    def test_hand_lost_releases_active_drag(self):
        state, mouse = self.make_state()

        state.apply("open_hand", "open_hand", make_landmarks(pinch=True), now=20.0)
        state.handle_hand_lost()

        self.assertEqual(mouse.events[:2], [("mouse_down",), ("mouse_up",)])
        self.assertFalse(state.dragging)

    def test_one_and_two_finger_clicks_are_debounced(self):
        state, mouse = self.make_state()

        for step in range(3):
            state.apply("one_finger", "one_finger", make_landmarks(), now=30.0 + step * 0.1)

        self.assertIn(("click", "left", 1), mouse.events)
        self.assertEqual(mouse.events.count(("click", "left", 1)), 1)

        for step in range(3):
            state.apply("two_fingers", "two_fingers", make_landmarks(), now=31.0 + step * 0.1)

        self.assertIn(("click", "right", 1), mouse.events)

    def test_three_finger_actions_use_tabs_and_scroll(self):
        state, mouse = self.make_state()

        state.apply("three_left", "three_left", make_landmarks(), now=40.0)
        state.apply("three_left", "three_left", make_landmarks(), now=40.1)
        state.apply("three_right", "three_right", make_landmarks(), now=41.0)
        state.apply("three_right", "three_right", make_landmarks(), now=41.1)
        state.apply("three_up", "three_up", make_landmarks(), now=42.0)
        state.apply("three_up", "three_up", make_landmarks(), now=42.1)
        state.apply("three_down", "three_down", make_landmarks(), now=42.3)
        state.apply("three_down", "three_down", make_landmarks(), now=42.4)

        self.assertIn(("switch_tab", "left"), mouse.events)
        self.assertIn(("switch_tab", "right"), mouse.events)
        self.assertIn(("scroll", 80), mouse.events)
        self.assertIn(("scroll", -80), mouse.events)

    def test_model_metadata_has_expected_labels(self):
        label_map_path = Path(__file__).resolve().parents[1] / "trained_model" / "label_mapping.json"
        with label_map_path.open("r", encoding="utf-8") as file:
            label_to_id = json.load(file)

        self.assertEqual(
            set(label_to_id),
            {
                "fist",
                "one_finger",
                "open_hand",
                "three_down",
                "three_left",
                "three_right",
                "three_up",
                "two_fingers",
            },
        )


if __name__ == "__main__":
    unittest.main()
