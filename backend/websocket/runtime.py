import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.runtime_state import runtime_state

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/runtime")
async def runtime_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    last_gesture_log: tuple[str | None, str | None] | None = None
    last_voice_log: tuple[str | None, str | None] | None = None
    try:
        while True:
            await websocket.send_json(
                {
                    "type": "runtime_update",
                    "runtime": runtime_state.runtime_payload(),
                    "logs": runtime_state.logs[-20:],
                    "voice": {
                        "micStatus": runtime_state.mic_status,
                        "aiStatus": runtime_state.ai_status,
                        "lastVoiceCommand": runtime_state.last_voice_command,
                        "lastTranscript": runtime_state.last_transcript,
                        "commandConfidence": runtime_state.command_confidence,
                    },
                    "training": {
                        "sessionId": runtime_state.training_session_id,
                        "active": runtime_state.training_active,
                        "samples": runtime_state.training_samples,
                        "targetSamples": runtime_state.training_target,
                        "lastError": runtime_state.training_last_error,
                    },
                }
            )
            latest_log = runtime_state.logs[-1] if runtime_state.logs else None
            latest_key = None
            if latest_log:
                latest_key = (latest_log.get("time"), latest_log.get("message"))

            if latest_log and latest_log.get("type") == "gesture" and latest_key != last_gesture_log:
                last_gesture_log = latest_key
                await websocket.send_json({"type": "gesture_event", "event": latest_log.get("message"), "logs": runtime_state.logs[-20:]})
            if latest_log and latest_log.get("type") in {"voice", "ai"} and latest_key != last_voice_log:
                last_voice_log = latest_key
                await websocket.send_json(
                    {
                        "type": "voice_command",
                        "voice": {
                            "micStatus": runtime_state.mic_status,
                            "aiStatus": runtime_state.ai_status,
                            "lastVoiceCommand": runtime_state.last_voice_command,
                            "lastTranscript": runtime_state.last_transcript,
                            "commandConfidence": runtime_state.command_confidence,
                        },
                        "logs": runtime_state.logs[-20:],
                    }
                )
            if runtime_state.training_active:
                await websocket.send_json(
                    {
                        "type": "training_progress",
                        "training": {
                            "sessionId": runtime_state.training_session_id,
                            "samples": runtime_state.training_samples,
                            "targetSamples": runtime_state.training_target,
                            "lastError": runtime_state.training_last_error,
                        },
                    }
                )
            if runtime_state.last_error:
                await websocket.send_json({"type": "error", "message": runtime_state.last_error})
            if runtime_state.training_last_error:
                await websocket.send_json({"type": "warning", "message": runtime_state.training_last_error})
            await asyncio.sleep(1)
    except (WebSocketDisconnect, ConnectionResetError, BrokenPipeError):
        return
    except OSError as exc:
        if getattr(exc, "winerror", None) in {995, 10053, 10054}:
            return
        raise
