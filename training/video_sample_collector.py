"""Dynamic video sample collector for the Training UI dataset."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .dataset_validator import DRAG_DROP_SEGMENTS, DatasetValidator


class VideoSampleCollector:
    """Build and validate dynamic gesture sample JSON payloads."""

    def __init__(self, validator: DatasetValidator | None = None):
        self.validator = validator or DatasetValidator()

    def create_frame(
        self,
        *,
        t: float,
        landmarks: Sequence[Mapping[str, Any]],
        features: Sequence[float] | Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "t": float(t),
            "landmarks": list(landmarks),
            "features": list(features) if not isinstance(features, Mapping) else dict(features),
        }

    def create_drag_drop_segments(self, duration_sec: float) -> list[dict[str, float | str]]:
        segment_count = len(DRAG_DROP_SEGMENTS)
        segment_duration = float(duration_sec) / segment_count if segment_count else 0.0
        return [
            {
                "name": segment_name,
                "start_t": round(index * segment_duration, 4),
                "end_t": round((index + 1) * segment_duration, 4),
            }
            for index, segment_name in enumerate(DRAG_DROP_SEGMENTS)
        ]

    def create_sample(
        self,
        *,
        sample_id: str,
        profile: str,
        function_id: str,
        gesture_label: str,
        duration_sec: float,
        frames: Sequence[Mapping[str, Any]],
        segments: Sequence[Mapping[str, Any] | str] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        sample = {
            "sample_id": sample_id,
            "profile": profile,
            "function_id": function_id,
            "gesture_label": gesture_label,
            "data_type": "video",
            "duration_sec": float(duration_sec),
            "frames": list(frames),
            "segments": (
                list(segments)
                if segments is not None
                else self.create_drag_drop_segments(duration_sec)
            ),
        }
        if created_at is not None:
            sample["created_at"] = created_at
        self.validator.validate_video_sample(sample)
        return sample
