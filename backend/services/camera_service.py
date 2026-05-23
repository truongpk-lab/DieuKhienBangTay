"""Mock-safe camera service for Phase 18 integration."""

from __future__ import annotations

from backend.runtime_state import RuntimeState, runtime_state


class CameraService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state

    def status(self) -> dict[str, str | bool]:
        return {"status": self.state.camera_status, "mock": True}

    def start(self) -> dict[str, str | bool]:
        self.state.camera_status = "Mock Camera Streaming"
        return self.status()

    def stop(self) -> dict[str, str | bool]:
        self.state.camera_status = "Mock Camera Ready"
        return self.status()
