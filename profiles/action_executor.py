"""Execute profile actions through safe controller adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from actions.keyboard_controller import KeyboardController
from actions.mouse_control_adapter import MouseControlAdapter


class ActionExecutor:
    """Dispatch resolved profile actions to mouse or keyboard controllers."""

    MOUSE_ACTIONS = {
        "mouse.move",
        "mouse.left_click",
        "mouse.right_click",
        "mouse.scroll",
        "mouse.down",
        "mouse.up",
        "mouse.drag",
    }

    KEYBOARD_ACTIONS = {
        "game.attack",
        "game.block",
        "game.crouch",
        "game.dash",
        "game.jump",
        "game.left",
        "game.right",
        "game.move_left",
        "game.move_right",
        "game.skill_1",
        "keyboard.copy",
        "keyboard.hotkey",
        "keyboard.paste",
        "keyboard.press",
        "keyboard.release",
        "keyboard.switch_tab",
        "media.fullscreen",
        "media.next",
        "media.play_pause",
        "media.previous",
        "media.seek_backward",
        "media.seek_forward",
        "media.volume_down",
        "media.volume_up",
    }

    def __init__(self, mouse_adapter=None, keyboard_controller=None):
        self.mouse_adapter = mouse_adapter if mouse_adapter is not None else MouseControlAdapter()
        self.keyboard_controller = (
            keyboard_controller if keyboard_controller is not None else KeyboardController()
        )

    def execute(
        self,
        mapping: Mapping[str, Any],
        event_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an action mapping and return execution metadata."""

        action = str(mapping.get("action", ""))
        payload = self._merge_payload(mapping.get("payload", {}), event_payload)

        if action in self.MOUSE_ACTIONS:
            result = self._execute_mouse(action, payload)
        elif action in self.KEYBOARD_ACTIONS:
            result = self._execute_keyboard(action, payload)
        else:
            return {
                "status": "unsupported",
                "action": action,
                "gesture_event": mapping.get("gesture_event"),
            }

        return {
            "status": "executed",
            "action": action,
            "gesture_event": mapping.get("gesture_event"),
            "function_id": mapping.get("function_id"),
            "result": result,
        }

    def _execute_mouse(self, action: str, payload: Mapping[str, Any]):
        if action == "mouse.move":
            x = self._required_number(payload, "x", action)
            y = self._required_number(payload, "y", action)
            return self.mouse_adapter.move(x, y)

        if action == "mouse.left_click":
            return self.mouse_adapter.left_click(clicks=int(payload.get("clicks", 1)))

        if action == "mouse.right_click":
            return self.mouse_adapter.right_click(clicks=int(payload.get("clicks", 1)))

        if action == "mouse.scroll":
            amount = self._required_number(payload, "amount", action)
            return self.mouse_adapter.scroll(amount)

        if action == "mouse.down":
            return self.mouse_adapter.mouse_down()

        if action == "mouse.up":
            return self.mouse_adapter.mouse_up()

        if action == "mouse.drag":
            if "x" in payload and "y" in payload:
                return self.mouse_adapter.drag_move(payload["x"], payload["y"])
            return self.mouse_adapter.mouse_down()

        raise ValueError(f"unsupported mouse action: {action}")

    def _execute_keyboard(self, action: str, payload: Mapping[str, Any]):
        if action == "keyboard.hotkey":
            return self._execute_hotkey(payload, action)

        if action == "keyboard.press":
            key = payload.get("key")
            if not key:
                raise ValueError("keyboard.press requires key")
            return self.keyboard_controller.press(str(key))

        if action == "keyboard.release":
            key = payload.get("key")
            if not key:
                raise ValueError("keyboard.release requires key")
            return self.keyboard_controller.release(str(key))

        if action in {"keyboard.copy", "keyboard.paste", "keyboard.switch_tab"}:
            return self._execute_hotkey(payload, action)

        if action.startswith("media."):
            return self._execute_hotkey(payload, action)

        if action.startswith("game."):
            return self._execute_game_action(payload, action)

        raise ValueError(f"unsupported keyboard action: {action}")

    def _execute_hotkey(self, payload: Mapping[str, Any], action: str):
        keys = payload.get("keys") or payload.get("shortcut") or payload.get("hotkey")
        if isinstance(keys, str):
            keys = [key.strip() for key in keys.replace("+", " ").split() if key.strip()]
        if not keys:
            raise ValueError(f"{action} requires keys, shortcut, or hotkey")
        return self.keyboard_controller.hotkey(*keys)

    def _execute_game_action(self, payload: Mapping[str, Any], action: str):
        aliases = {
            "game.left": "left",
            "game.right": "right",
            "game.move_left": "left",
            "game.move_right": "right",
            "game.jump": "space",
            "game.attack": "j",
            "game.dash": "shift",
        }
        if payload.get("keys") or payload.get("shortcut") or payload.get("hotkey"):
            return self._execute_hotkey(payload, action)

        key = payload.get("key") or aliases.get(action)
        if not key:
            raise ValueError(f"{action} requires key or hotkey payload")

        mode = str(payload.get("mode", "press"))
        if mode == "release":
            return self.keyboard_controller.release(str(key))
        if mode == "hold":
            return self.keyboard_controller.press(str(key))
        return self.keyboard_controller.press(str(key))

    def _merge_payload(
        self,
        mapping_payload: Mapping[str, Any] | None,
        event_payload: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        if isinstance(mapping_payload, Mapping):
            merged.update(mapping_payload)
        if isinstance(event_payload, Mapping):
            merged.update(event_payload)
        return merged

    def _required_number(self, payload: Mapping[str, Any], key: str, action: str):
        value = payload.get(key)
        if not isinstance(value, (int, float)):
            raise ValueError(f"{action} requires numeric payload field: {key}")
        return value
