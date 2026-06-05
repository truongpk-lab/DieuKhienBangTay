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
        profile = self.manager.load_profile(profile_id)
        profile["is_active"] = profile_id == self.state.current_profile_id
        return profile

    def activate(self, profile_id: str) -> dict[str, Any]:
        profile = self.manager.set_active_profile(profile_id)
        self.state.current_profile_id = str(profile["id"])
        self.state.current_profile = str(profile["name"])
        self.state.add_log("system", f"Profile activated: {profile['name']}")
        return profile

    def active_profile(self) -> dict[str, Any]:
        return self.manager.load_profile(self.state.current_profile_id)

    def save_profile(self, profile_id: str, profile: dict[str, Any]) -> dict[str, Any]:
        saved = self.manager.save_profile(profile_id, profile)
        self.state.add_log("system", f"Profile saved: {saved['name']}")
        if profile_id == self.state.current_profile_id:
            self.state.current_profile = str(saved["name"])
        saved["is_active"] = profile_id == self.state.current_profile_id
        return saved

    def create_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        created = self.manager.create_profile(profile)
        self.state.add_log("system", f"Profile created: {created['name']}")
        created["is_active"] = False
        return created

    def delete_profile(self, profile_id: str) -> dict[str, Any]:
        deleted = self.manager.delete_profile(profile_id)
        if not deleted:
            raise FileNotFoundError(f"profile not found: {profile_id}")
        self.state.add_log("system", f"Profile deleted: {profile_id}")
        if self.state.current_profile_id == profile_id:
            self.activate("office")
        return {"ok": True, "deleted": profile_id}
