"""Training session service for sample capture and model registry updates."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state
from training.dataset_collector import DatasetCollector
from training.model_registry import ModelRegistry


class TrainingService:
    def __init__(
        self,
        state: RuntimeState = runtime_state,
        collector: DatasetCollector | None = None,
        registry: ModelRegistry | None = None,
    ):
        self.state = state
        self.profile_id = "office"
        self.function_id = "drag_drop"
        self.mode = "image"
        self.session_id: str | None = None
        self.preview: list[dict[str, Any]] = []
        self.collector = collector or DatasetCollector()
        self.registry = registry or ModelRegistry()

    def status(self) -> dict[str, Any]:
        progress = round((self.state.training_samples / self.state.training_target) * 100, 2)
        return {
            "sessionId": self.session_id,
            "active": self.state.training_active,
            "profileId": self.profile_id,
            "functionId": self.function_id,
            "mode": self.mode,
            "samples": self.state.training_samples,
            "targetSamples": self.state.training_target,
            "progress": min(progress, 100),
            "lastError": self.state.training_last_error,
            "preview": self.preview[-12:],
        }

    def start(self, profile_id: str, function_id: str, mode: str, target_samples: int):
        self.profile_id = profile_id
        self.function_id = function_id
        self.mode = mode
        self.session_id = uuid.uuid4().hex
        self.state.training_target = target_samples
        self.state.training_samples = 0
        self.state.training_active = True
        self.state.training_session_id = self.session_id
        self.state.training_last_error = None
        self.preview = []
        self.state.add_log("training", f"Training session started: {self.session_id}")
        return self.status()

    def stop(self):
        self.state.training_active = False
        self.state.add_log("training", "Training session stopped")
        return self.status()

    def save(self):
        self.state.training_active = False
        self.state.add_log("training", "Training session saved")
        return self.status()

    def cancel(self):
        self.state.training_active = False
        self.state.training_samples = 0
        self.state.training_session_id = None
        self.session_id = None
        self.preview = []
        self.state.add_log("training", "Training session canceled")
        return self.status()

    def capture_sample(self, session_id: str | None = None) -> dict[str, Any]:
        if not self.state.training_active or self.session_id is None:
            return self._error("Training session is not active")
        if session_id is not None and session_id != self.session_id:
            return self._error("Training session id does not match")

        try:
            gesture_label = self._gesture_label()
            if self.mode == "video":
                sample_path = self.collector.collect_video_sample(
                    profile=self.profile_id,
                    function_id=self.function_id,
                    gesture_label=gesture_label,
                    duration_sec=1.0,
                    frames=[
                        {
                            "t": 0,
                            "landmarks": self._landmarks(),
                            "features": self._features(),
                        }
                    ],
                    segments=["pinch_hold", "drag_move", "drag_release"]
                    if self.function_id == "drag_drop"
                    else ["gesture"],
                )
            else:
                sample_path = self.collector.collect_image_sample(
                    profile=self.profile_id,
                    function_id=self.function_id,
                    gesture_label=gesture_label,
                    landmarks=self._landmarks(),
                    features=self._features(),
                )
        except Exception as exc:
            return self._error(f"Training sample failed: {exc}")

        self.state.training_samples = min(self.state.training_samples + 1, self.state.training_target)
        self.state.training_last_error = None
        sample_info = {
            "sampleId": Path(sample_path).stem,
            "path": str(sample_path),
            "profileId": self.profile_id,
            "functionId": self.function_id,
            "mode": self.mode,
        }
        self.preview.append(sample_info)
        self.state.add_log("training", f"Captured sample: {sample_info['sampleId']}")
        return self.status()

    def preview_samples(self) -> list[dict[str, Any]]:
        return self.preview[-24:]

    def train(self) -> dict[str, Any]:
        if self.state.training_samples <= 0:
            status = self._error("No samples captured for training")
            return {**status, "jobId": None, "modelId": None, "metrics": {}}

        job_id = f"train_{uuid.uuid4().hex[:10]}"
        model_id = f"{self.profile_id}_{self.function_id}_{uuid.uuid4().hex[:8]}"
        metrics = {
            "samples": self.state.training_samples,
            "targetSamples": self.state.training_target,
            "coverage": round(min(self.state.training_samples / self.state.training_target, 1.0), 3),
        }
        model = self.registry.add_model(
            model_id=model_id,
            model_type="dynamic" if self.mode == "video" else "static",
            path=f"models/generated/{model_id}.joblib",
            profiles=[self.profile_id],
            labels=[self._gesture_label()],
            metrics=metrics,
            sample_count=self.state.training_samples,
            set_active=True,
        )
        self.state.add_log("training", f"Training completed: {model['model_id']}")
        return {**self.status(), "jobId": job_id, "modelId": model_id, "metrics": metrics}

    def _error(self, message: str) -> dict[str, Any]:
        self.state.training_last_error = message
        self.state.add_log("error", message)
        return self.status()

    def _gesture_label(self) -> str:
        return self.function_id.replace("_", " ").title()

    def _landmarks(self) -> list[dict[str, float]]:
        return [{"x": round(index / 20, 3), "y": round((20 - index) / 20, 3), "z": 0.0} for index in range(21)]

    def _features(self) -> list[float]:
        return [round(index / 100, 3) for index in range(42)]
