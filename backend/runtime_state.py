"""Shared in-memory runtime state for the backend integration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def _now_label() -> str:
    return datetime.now().strftime("%H:%M:%S")


@dataclass
class RuntimeState:
    """Small mutable state holder used by mock services and API routers."""

    active: bool = False
    current_profile_id: str = "office"
    current_profile: str = "Văn phòng"
    current_gesture: str = "Pinch"
    current_action: str = "Kéo thả"
    fps: int = 60
    accuracy: float = 98.5
    tracking_status: str = "Idle"
    latency: int = 12
    camera_status: str = "Mock Camera Ready"
    hand_status: str = "Active Tracking"
    training_active: bool = False
    training_samples: int = 24
    training_target: int = 30
    logs: list[dict[str, str]] = field(
        default_factory=lambda: [
            {"time": "10:42:01", "type": "system", "message": "Camera initialized"},
            {"time": "10:42:03", "type": "detection", "message": "Hand detected: Right"},
            {"time": "10:42:05", "type": "gesture", "message": "Pinch detected -> drag_start"},
        ]
    )

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
            "active": self.active,
        }

    def add_log(self, log_type: str, message: str) -> dict[str, str]:
        log = {"time": _now_label(), "type": log_type, "message": message}
        self.logs.append(log)
        self.logs = self.logs[-100:]
        return log


runtime_state = RuntimeState()
