"""Gesture runtime service and test-event resolver."""

from __future__ import annotations

from typing import Any

from backend.runtime_state import RuntimeState, runtime_state
from profiles.action_mapper import ActionMapper

from .profile_service import ProfileService


class GestureService:
    def __init__(
        self,
        profile_service: ProfileService | None = None,
        state: RuntimeState = runtime_state,
    ):
        self.profile_service = profile_service or ProfileService(state=state)
        self.state = state

    def current(self) -> dict[str, Any]:
        return {
            "gesture": self.state.current_gesture,
            "action": self.state.current_action,
            "profileId": self.state.current_profile_id,
        }

    def logs(self) -> list[dict[str, str]]:
        return list(self.state.logs)

    def test_event(
        self,
        gesture_event: str,
        payload: dict[str, Any] | None = None,
        execute: bool = False,
    ) -> dict[str, Any]:
        profile = self.profile_service.active_profile()
        mapper = ActionMapper(profile=profile)
        mapping = mapper.map_gesture_event(gesture_event)
        self.state.current_gesture = gesture_event
        if mapping:
            self.state.current_action = str(mapping["label"])
        self.state.add_log("gesture", f"Test event: {gesture_event}")

        result = None
        if execute and mapping:
            result = mapper.execute_gesture_event(gesture_event, payload or {})

        return {
            "gestureEvent": gesture_event,
            "mapping": mapping,
            "executed": bool(execute and mapping),
            "result": result,
        }
