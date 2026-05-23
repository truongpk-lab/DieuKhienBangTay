"""Mock training session service for Phase 18."""

from __future__ import annotations

from backend.runtime_state import RuntimeState, runtime_state


class TrainingService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state
        self.profile_id = "office"
        self.function_id = "drag_drop"
        self.mode = "image"

    def status(self) -> dict[str, float | int | str | bool]:
        progress = round((self.state.training_samples / self.state.training_target) * 100, 2)
        return {
            "active": self.state.training_active,
            "profileId": self.profile_id,
            "functionId": self.function_id,
            "mode": self.mode,
            "samples": self.state.training_samples,
            "targetSamples": self.state.training_target,
            "progress": min(progress, 100),
        }

    def start(self, profile_id: str, function_id: str, mode: str, target_samples: int):
        self.profile_id = profile_id
        self.function_id = function_id
        self.mode = mode
        self.state.training_target = target_samples
        self.state.training_samples = 0
        self.state.training_active = True
        self.state.add_log("system", "Training session started")
        return self.status()

    def stop(self):
        self.state.training_active = False
        self.state.add_log("system", "Training session stopped")
        return self.status()

    def save(self):
        self.state.training_active = False
        self.state.add_log("system", "Training session saved")
        return self.status()

    def cancel(self):
        self.state.training_active = False
        self.state.training_samples = 0
        self.state.add_log("system", "Training session canceled")
        return self.status()
