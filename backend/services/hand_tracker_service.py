"""Mock hand-tracking service placeholder."""

from __future__ import annotations

from backend.runtime_state import RuntimeState, runtime_state


class HandTrackerService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state

    def status(self) -> dict[str, str | bool]:
        return {"status": self.state.hand_status, "mock": True}

    def start(self) -> dict[str, str | bool]:
        self.state.hand_status = "Active Tracking"
        return self.status()

    def stop(self) -> dict[str, str | bool]:
        self.state.hand_status = "Paused"
        return self.status()
