"""Map gesture events to configured actions and execute them through adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .action_executor import ActionExecutor


class ActionMapper:
    """Resolve enabled profile functions by gesture event."""

    def __init__(
        self,
        profile: dict[str, Any] | None = None,
        executor: ActionExecutor | None = None,
        mouse_adapter=None,
        keyboard_controller=None,
    ):
        self.profile = profile
        self.executor = executor or ActionExecutor(
            mouse_adapter=mouse_adapter,
            keyboard_controller=keyboard_controller,
        )

    def set_profile(self, profile: dict[str, Any]) -> None:
        self.profile = profile

    def list_mappings(self) -> list[dict[str, Any]]:
        if not self.profile:
            return []
        return [function for function in self.profile.get("functions", []) if function.get("enabled")]

    def map_gesture_event(self, gesture_event: str) -> dict[str, Any] | None:
        """Return the configured function for a gesture event, if any."""

        if not gesture_event:
            return None

        for function in self.list_mappings():
            if function.get("gesture_event") == gesture_event:
                return {
                    "profile_id": self.profile.get("id") if self.profile else None,
                    "function_id": function["id"],
                    "label": function["label"],
                    "gesture_event": function["gesture_event"],
                    "gesture": function["gesture"],
                    "action": function["action"],
                    "payload": function.get("payload", {}),
                }
        return None

    def action_for(self, gesture_event: str) -> dict[str, Any] | None:
        """Compatibility API returning the action payload for one gesture."""

        mapping = self.map_gesture_event(gesture_event)
        if mapping is None:
            return None
        action = {
            "action": mapping["action"],
            "gesture_event": mapping["gesture_event"],
            "function_id": mapping["function_id"],
        }
        payload = mapping.get("payload", {})
        if isinstance(payload, Mapping):
            action.update(payload)
            keys = payload.get("keys") or payload.get("shortcut") or payload.get("hotkey")
            if isinstance(keys, str):
                action["keys"] = [key.strip() for key in keys.replace("+", " ").split() if key.strip()]
        return action

    def execute_gesture_event(
        self,
        gesture_event: str | Mapping[str, Any],
        event_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Resolve a gesture event and execute its configured action."""

        event_name, payload = self._normalize_event(gesture_event, event_payload)
        mapping = self.map_gesture_event(event_name)
        if mapping is None:
            return None
        return self.executor.execute(mapping, payload)

    def handle_event(
        self,
        gesture_event: str | Mapping[str, Any],
        event_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Compatibility alias for callers that emit gesture event objects."""

        return self.execute_gesture_event(gesture_event, event_payload)

    def _normalize_event(
        self,
        gesture_event: str | Mapping[str, Any],
        event_payload: Mapping[str, Any] | None,
    ) -> tuple[str, dict[str, Any]]:
        if isinstance(gesture_event, Mapping):
            event_name = str(gesture_event.get("gesture_event") or gesture_event.get("event") or "")
            payload = {key: value for key, value in gesture_event.items() if key not in {"event"}}
            if isinstance(event_payload, Mapping):
                payload.update(event_payload)
            return event_name, payload

        payload = dict(event_payload) if isinstance(event_payload, Mapping) else {}
        return gesture_event, payload
