"""Load and manage profile JSON configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .profile_schema import validate_profile


class ProfileManager:
    """Profile loader for the Phase 10 JSON configuration layer."""

    def __init__(self, config_dir: str | Path | None = None, default_profile_id: str = "office"):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent / "configs"
        self._active_profile_id = default_profile_id

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
        return profile

    def get_active_profile(self) -> dict[str, Any]:
        """Return the currently selected profile."""

        return self.load_profile(self._active_profile_id)

    def set_active_profile(self, profile_id: str) -> dict[str, Any]:
        """Set and return the active profile after validating it can be loaded."""

        profile = self.load_profile(profile_id)
        self._active_profile_id = profile_id
        return profile

    def _load_profile_file(self, profile_path: Path) -> dict[str, Any]:
        with profile_path.open("r", encoding="utf-8") as profile_file:
            profile = json.load(profile_file)
        validate_profile(profile)
        return profile
