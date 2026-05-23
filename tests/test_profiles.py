import unittest

from profiles import (
    ActionMapper,
    ProfileManager,
    ProfileValidationError,
    validate_profile,
)


class ProfileSystemTests(unittest.TestCase):
    def test_manager_loads_bundled_profile_by_id(self):
        manager = ProfileManager()

        office = manager.load_profile("office")
        loaded_ids = [
            manager.load_profile(profile_id).id
            for profile_id in manager.available_profile_ids()
        ]

        self.assertEqual(office.id, "office")
        self.assertEqual(
            loaded_ids,
            ["custom", "entertainment", "game_2d", "office"],
        )

    def test_mapper_maps_gesture_event_to_action(self):
        mapper = ActionMapper(ProfileManager().load_profile("office"))

        action = mapper.action_for("swipe_right")

        self.assertEqual(action["action"], "keyboard.hotkey")
        self.assertEqual(action["keys"], ["ctrl", "tab"])

    def test_mapper_keeps_drag_events_granular(self):
        mapper = ActionMapper(ProfileManager().load_profile("office"))

        self.assertEqual(mapper.action_for("pinch_hold")["action"], "mouse.down")
        self.assertEqual(mapper.action_for("drag_move")["action"], "mouse.move")
        self.assertEqual(mapper.action_for("drag_release")["action"], "mouse.up")

    def test_validation_rejects_duplicate_gesture_event(self):
        with self.assertRaises(ProfileValidationError):
            validate_profile(
                {
                    "id": "bad",
                    "name": "Bad",
                    "description": "Duplicate events",
                    "mouse": {},
                    "gesture_filter": {},
                    "functions": [
                        {
                            "id": "first",
                            "name": "First",
                            "gesture_event": "pinch_tap",
                            "action": "mouse.left_click",
                        },
                        {
                            "id": "second",
                            "name": "Second",
                            "gesture_event": "pinch_tap",
                            "action": "mouse.right_click",
                        },
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
