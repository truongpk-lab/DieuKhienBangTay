import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.runtime_state import runtime_state

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/runtime")
async def runtime_socket(websocket: WebSocket) -> None:
    await websocket.accept()
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
            if latest_log and latest_log.get("type") == "gesture":
                await websocket.send_json({"type": "gesture_event", "event": latest_log.get("message"), "logs": runtime_state.logs[-20:]})
            if latest_log and latest_log.get("type") in {"voice", "ai"}:
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
    except WebSocketDisconnect:
        return
