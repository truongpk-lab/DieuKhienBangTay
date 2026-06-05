"""Gemini-backed voice command parsing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state


ALLOWED_INTENTS = {
    "start",
    "stop",
    "pause",
    "resume",
    "recenter",
    "switch_profile",
    "show_app",
    "hide_app",
    "emergency_stop",
    "training_start",
    "training_stop",
}

COMMAND_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": sorted(ALLOWED_INTENTS | {"unknown"})},
        "target": {"type": ["string", "null"]},
        "profile_id": {"type": ["string", "null"]},
        "action": {"type": ["string", "null"]},
        "confidence": {"type": "number"},
        "requires_confirmation": {"type": "boolean"},
        "transcript": {"type": ["string", "null"]},
    },
    "required": ["intent", "confidence", "requires_confirmation"],
}


class GeminiCommandService:
    def __init__(self, state: RuntimeState = runtime_state, model: str = "gemini-2.5-flash"):
        self.state = state
        self.model = model

    def status(self) -> dict[str, Any]:
        configured = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        self.state.ai_status = "Gemini ready" if configured else "Gemini API key missing"
        return {"provider": "gemini", "configured": configured, "status": self.state.ai_status}

    def parse_command(self, text: str | None = None, audio_path: str | Path | None = None) -> dict[str, Any]:
        self._ensure_configured()
        try:
            from google import genai  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing google-genai. Run: py -3 -m pip install -r backend\\requirements.txt") from exc

        client = genai.Client()
        prompt = self._prompt(text)
        contents: list[Any] = [prompt]
        uploaded_file = None
        if audio_path:
            uploaded_file = client.files.upload(file=str(audio_path))
            contents.append(uploaded_file)

        response = client.models.generate_content(
            model=self.model,
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": COMMAND_SCHEMA,
            },
        )
        parsed = self._parse_response(getattr(response, "text", ""))
        self._validate(parsed)
        self.state.ai_status = "Gemini ready"
        self.state.last_voice_command = parsed["intent"]
        self.state.last_transcript = parsed.get("transcript") or text
        self.state.command_confidence = float(parsed.get("confidence", 0.0))
        self.state.add_log("ai", f"Gemini command: {parsed['intent']} ({self.state.command_confidence:.2f})")
        return parsed

    def _ensure_configured(self) -> None:
        if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
            self.state.ai_status = "Gemini API key missing"
            raise RuntimeError("GEMINI_API_KEY is missing. AI voice commands are disabled.")

    def _prompt(self, text: str | None) -> str:
        command_text = text or "Listen to the attached audio and classify the user's Vietnamese or English command."
        return (
            "You control ACV Gesture Control. Return only JSON matching the schema. "
            "Allowed intents: start, stop, pause, resume, recenter, switch_profile, "
            "show_app, hide_app, emergency_stop, training_start, training_stop, unknown. "
            "Only use switch_profile for office, entertainment, game_2d, or custom. "
            "Set requires_confirmation true for emergency_stop or confidence below 0.7. "
            f"User command: {command_text}"
        )

    def _parse_response(self, text: str) -> dict[str, Any]:
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Gemini returned invalid JSON: {text[:120]}") from exc
        if not isinstance(value, dict):
            raise RuntimeError("Gemini command response must be a JSON object")
        return value

    def _validate(self, command: dict[str, Any]) -> None:
        intent = str(command.get("intent") or "unknown")
        if intent not in ALLOWED_INTENTS | {"unknown"}:
            raise RuntimeError(f"Gemini command intent is not allowed: {intent}")
        command["intent"] = intent
        command["confidence"] = float(command.get("confidence", 0.0) or 0.0)
        command["requires_confirmation"] = bool(command.get("requires_confirmation", False))


gemini_command_service = GeminiCommandService()
