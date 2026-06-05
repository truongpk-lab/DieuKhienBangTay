"""JSON-backed application settings for onboarding and runtime defaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state
from backend.schemas import AppSettings


class SettingsService:
    def __init__(
        self,
        settings_path: str | Path | None = None,
        state: RuntimeState = runtime_state,
    ):
        self.settings_path = Path(settings_path) if settings_path else Path("data") / "settings.json"
        self.state = state

    def get_settings(self) -> AppSettings:
        if not self.settings_path.exists():
            settings = AppSettings()
            self.save_settings(settings)
            return settings

        with self.settings_path.open("r", encoding="utf-8") as settings_file:
            return self._parse_settings(json.load(settings_file))

    def save_settings(self, settings: AppSettings | dict[str, Any]) -> AppSettings:
        parsed = settings if isinstance(settings, AppSettings) else self._parse_settings(settings)
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.settings_path.with_suffix(".json.tmp")

        with temp_path.open("w", encoding="utf-8") as settings_file:
            json.dump(self._dump_settings(parsed), settings_file, ensure_ascii=False, indent=2)
            settings_file.write("\n")
        temp_path.replace(self.settings_path)

        self.state.current_profile_id = parsed.active_profile_id
        self.state.add_log("system", "Settings saved")
        return parsed

    def start_calibration(self, settings: AppSettings | dict[str, Any] | None = None) -> dict[str, Any]:
        active_settings = self.save_settings(settings) if settings is not None else self.get_settings()
        self.state.current_gesture = "Calibration"
        self.state.current_action = "Onboarding"
        self.state.add_log("system", "Calibration started from onboarding")
        return {
            "ok": True,
            "status": "calibrating",
            "message": "Calibration started",
            "settings": active_settings,
        }

    def skip_calibration(self, settings: AppSettings | dict[str, Any] | None = None) -> dict[str, Any]:
        active_settings = self.save_settings(settings) if settings is not None else self.get_settings()
        self.state.add_log("system", "Calibration skipped; settings persisted")
        return {
            "ok": True,
            "status": "skipped",
            "message": "Calibration skipped",
            "settings": active_settings,
        }

    def _parse_settings(self, value: dict[str, Any]) -> AppSettings:
        if hasattr(AppSettings, "model_validate"):
            return AppSettings.model_validate(value)
        return AppSettings.parse_obj(value)

    def _dump_settings(self, settings: AppSettings) -> dict[str, Any]:
        if hasattr(settings, "model_dump"):
            return settings.model_dump()
        return settings.dict()


settings_service = SettingsService()
