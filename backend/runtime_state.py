"""Shared in-memory runtime state for the backend integration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Any


def _now_label() -> str:
    return datetime.now().strftime("%H:%M:%S")


@dataclass
class RuntimeState:
    """Small mutable state holder used by runtime services and API routers."""

    active: bool = False
    mode: str = "idle"
    current_profile_id: str = "office"
    current_profile: str = "Văn phòng"
    current_gesture: str = "Pinch"
    current_action: str = "Kéo thả"
    fps: int = 60
    accuracy: float = 98.5
    tracking_status: str = "Idle"
    latency: int = 12
    camera_status: str = "Camera idle"
    hand_status: str = "Hand tracker idle"
    mic_status: str = "Microphone idle"
    ai_status: str = "Gemini disabled"
    last_voice_command: str | None = None
    last_transcript: str | None = None
    command_confidence: float = 0.0
    last_error: str | None = None
    training_active: bool = False
    training_samples: int = 24
    training_target: int = 30
    training_session_id: str | None = None
    training_last_error: str | None = None
    workflow_state: str = "idle"
    workflow_event: str = "idle"
    pinch_distance: float = 0.0
    workflow_confidence: float = 0.0
    logs: list[dict[str, str]] = field(
        default_factory=lambda: [
            {"time": "10:42:01", "type": "system", "message": "Backend initialized"},
        ]
    )
    lock: RLock = field(default_factory=RLock, repr=False)

    def runtime_payload(self) -> dict[str, Any]:
        return {
            "currentProfile": self.current_profile,
            "currentProfileId": self.current_profile_id,
            "currentGesture": self.current_gesture,
            "currentAction": self.current_action,
            "fps": self.fps,
            "accuracy": self.accuracy,
            "trackingStatus": self.tracking_status,
            "latency": self.latency,
            "cameraStatus": self.camera_status,
            "handStatus": self.hand_status,
            "micStatus": self.mic_status,
            "aiStatus": self.ai_status,
            "lastVoiceCommand": self.last_voice_command,
            "lastTranscript": self.last_transcript,
            "commandConfidence": self.command_confidence,
            "active": self.active,
            "mode": self.mode,
            "lastError": self.last_error,
            "workflow": self.workflow_payload(),
        }

    def add_log(self, log_type: str, message: str) -> dict[str, str]:
        log = {"time": _now_label(), "type": log_type, "message": message}
        with self.lock:
            self.logs.append(log)
            self.logs = self.logs[-100:]
        return log

    def workflow_payload(self) -> dict[str, Any]:
        return {
            "state": self.workflow_state,
            "event": self.workflow_event,
            "pinchDistance": self.pinch_distance,
            "confidence": self.workflow_confidence,
            "latency": self.latency,
            "sensorActive": self.active,
        }


runtime_state = RuntimeState()
