"""Load and manage profile JSON configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.services.storage_service import JsonStorageService

from .profile_schema import validate_profile


class ProfileDict(dict):
    """dict with attribute access for older tests/callers."""

    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


class ProfileManager:
    """Profile loader for the Phase 10 JSON configuration layer."""

    def __init__(
        self,
        config_dir: str | Path | None = None,
        default_profile_id: str = "office",
        storage: JsonStorageService | None = None,
    ):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent / "configs"
        self._active_profile_id = default_profile_id
        self.storage = storage or JsonStorageService()

    def list_profiles(self) -> list[dict[str, str]]:
        """Return available profiles as lightweight UI-friendly metadata."""

        profiles: list[dict[str, str]] = []
        for profile_path in sorted(self.config_dir.glob("*.json")):
            profile = self._load_profile_file(profile_path)
            profiles.append(
                {
                    "id": str(profile["id"]),
                    "name": str(profile["name"]),
                    "description": str(profile["description"]),
                }
            )
        return profiles

    def available_profile_ids(self) -> list[str]:
        """Compatibility helper used by older tests."""

        return sorted(profile_path.stem for profile_path in self.config_dir.glob("*.json"))

    def load_profile(self, profile_id: str) -> dict[str, Any]:
        """Load and validate a profile by id."""

        if not profile_id:
            raise ValueError("profile_id is required")

        profile_path = self.config_dir / f"{profile_id}.json"
        if not profile_path.exists():
            raise FileNotFoundError(f"profile not found: {profile_id}")

        profile = self._load_profile_file(profile_path)
        if profile["id"] != profile_id:
            raise ValueError(
                f"profile id mismatch in {profile_path}: expected {profile_id}, "
                f"got {profile['id']}"
            )
        return ProfileDict(profile)

    def get_active_profile(self) -> dict[str, Any]:
        """Return the currently selected profile."""

        return self.load_profile(self._active_profile_id)

    def set_active_profile(self, profile_id: str) -> dict[str, Any]:
        """Set and return the active profile after validating it can be loaded."""

        profile = self.load_profile(profile_id)
        self._active_profile_id = profile_id
        return profile

    def save_profile(self, profile_id: str, profile: dict[str, Any]) -> dict[str, Any]:
        """Validate and persist a profile JSON file."""

        if not profile_id:
            raise ValueError("profile_id is required")
        if str(profile.get("id", "")).strip() != profile_id:
            raise ValueError("profile id must match profile_id")

        validate_profile(profile)
        profile_path = self.config_dir / f"{profile_id}.json"
        self.storage.write_json(profile_path, profile, backup=True, validator=validate_profile)
        return self.load_profile(profile_id)

    def create_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Create a new profile and fail if its id already exists."""

        profile_id = str(profile.get("id", "")).strip()
        if not profile_id:
            raise ValueError("profile id is required")
        profile_path = self.config_dir / f"{profile_id}.json"
        if profile_path.exists():
            raise FileExistsError(f"profile already exists: {profile_id}")

        payload = self._profile_with_defaults(profile)
        validate_profile(payload)
        self.storage.write_json(profile_path, payload, validator=validate_profile)
        return self.load_profile(profile_id)

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a non-default profile config."""

        if profile_id == "office":
            raise ValueError("office profile cannot be deleted")
        profile_path = self.config_dir / f"{profile_id}.json"
        deleted = self.storage.delete_json(profile_path, backup=True)
        if self._active_profile_id == profile_id:
            self._active_profile_id = "office"
        return deleted

    def _load_profile_file(self, profile_path: Path) -> dict[str, Any]:
        with profile_path.open("r", encoding="utf-8") as profile_file:
            profile = json.load(profile_file)
        validate_profile(profile)
        return profile

    def _profile_with_defaults(self, profile: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(profile["id"]).strip(),
            "name": str(profile.get("name") or profile["id"]).strip(),
            "description": str(profile.get("description") or "Custom gesture profile").strip(),
            "mouse": profile.get("mouse") or {"speed": 1.5, "sensitivity": 75, "smoothing": 3},
            "gesture_filter": profile.get("gesture_filter") or {"hand": "auto", "min_confidence": 0.75},
            "functions": profile.get("functions")
            or [
                {
                    "id": "custom_action",
                    "label": "Tác vụ tùy chỉnh",
                    "gesture_event": "custom_gesture",
                    "gesture": "Custom Gesture",
                    "action": "keyboard.press",
                    "enabled": False,
                    "payload": {"key": "space"},
                }
            ],
        }
