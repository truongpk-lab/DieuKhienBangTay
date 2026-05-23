"""Profile service backed by profiles/configs/*.json."""

from __future__ import annotations

from typing import Any

from backend.runtime_state import RuntimeState, runtime_state
from profiles.profile_manager import ProfileManager


class ProfileService:
    def __init__(
        self,
        manager: ProfileManager | None = None,
        state: RuntimeState = runtime_state,
    ):
        self.manager = manager or ProfileManager()
        self.state = state

    def list_profiles(self) -> list[dict[str, str]]:
        return self.manager.list_profiles()

    def get_profile(self, profile_id: str) -> dict[str, Any]:
        return self.manager.load_profile(profile_id)

    def activate(self, profile_id: str) -> dict[str, Any]:
        profile = self.manager.set_active_profile(profile_id)
        self.state.current_profile_id = str(profile["id"])
        self.state.current_profile = str(profile["name"])
        self.state.add_log("system", f"Profile activated: {profile['name']}")
        return profile

    def active_profile(self) -> dict[str, Any]:
        return self.manager.load_profile(self.state.current_profile_id)
