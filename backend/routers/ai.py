from __future__ import annotations

from fastapi import APIRouter

from backend.schemas import VoiceCommandRequest, VoiceCommandResponse
from backend.services.app_visibility_service import app_visibility_service
from backend.services.gemini_command_service import ALLOWED_INTENTS, gemini_command_service
from backend.services.runtime_service import runtime_service
from backend.routers.training import training_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/command", response_model=VoiceCommandResponse)
def ai_command(request: VoiceCommandRequest) -> dict:
    try:
        command = gemini_command_service.parse_command(text=request.text, audio_path=request.audio_path)
    except Exception as exc:
        return {
            "ok": False,
            "confidence": 0.0,
            "requires_confirmation": False,
            "executed": False,
            "result": None,
            "message": str(exc),
        }

    intent = command["intent"]
    confidence = float(command.get("confidence", 0.0))
    requires_confirmation = bool(command.get("requires_confirmation", False))
    transcript = command.get("transcript") or request.text
    if intent not in ALLOWED_INTENTS or confidence < 0.7 or requires_confirmation or not request.execute:
        runtime_service.state.add_log("warning", f"Voice command not executed: {intent} ({confidence:.2f})")
        return _response(command, transcript, False, None, "Voice command parsed but not executed.")

    result = _execute_intent(intent, command)
    runtime_service.state.add_log("voice", f"Voice command executed: {intent}")
    return _response(command, transcript, True, result, "Voice command executed.")


def _execute_intent(intent: str, command: dict) -> dict:
    if intent == "start":
        return {"runtime": runtime_service.start()}
    if intent == "stop":
        return {"runtime": runtime_service.stop(), "visibility": app_visibility_service.show()}
    if intent == "pause":
        return {"runtime": runtime_service.pause()}
    if intent == "resume":
        return {"runtime": runtime_service.resume()}
    if intent == "recenter":
        return {"runtime": runtime_service.recenter()}
    if intent == "switch_profile":
        profile_id = command.get("profile_id")
        if not profile_id:
            raise ValueError("switch_profile requires profile_id")
        return {"profile": runtime_service.profile_service.activate(str(profile_id))}
    if intent == "show_app":
        return {"visibility": app_visibility_service.show()}
    if intent == "hide_app":
        return {"visibility": app_visibility_service.hide()}
    if intent == "training_start":
        return {"training": training_service.start("office", "drag_drop", "image", 30)}
    if intent == "training_stop":
        return {"training": training_service.stop()}
    raise ValueError(f"Intent requires confirmation or is not executable through voice: {intent}")


def _response(command: dict, transcript: str | None, executed: bool, result: dict | None, message: str) -> dict:
    return {
        "ok": True,
        "intent": command.get("intent"),
        "target": command.get("target"),
        "profile_id": command.get("profile_id"),
        "action": command.get("action"),
        "confidence": float(command.get("confidence", 0.0)),
        "requires_confirmation": bool(command.get("requires_confirmation", False)),
        "transcript": transcript,
        "executed": executed,
        "result": result,
        "message": message,
    }
