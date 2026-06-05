"""Static image sample collector for the Training UI dataset."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .dataset_validator import DatasetValidator


class ImageSampleCollector:
    """Build and validate image sample JSON payloads."""

    def __init__(self, validator: DatasetValidator | None = None):
        self.validator = validator or DatasetValidator()

    def create_sample(
        self,
        *,
        sample_id: str,
        profile: str,
        function_id: str,
        gesture_label: str,
        created_at: str,
        landmarks: Sequence[Mapping[str, Any]],
        features: Sequence[float] | Mapping[str, Any],
    ) -> dict[str, Any]:
        sample = {
            "sample_id": sample_id,
            "profile": profile,
            "function_id": function_id,
            "gesture_label": gesture_label,
            "data_type": "image",
            "created_at": created_at,
            "landmarks": list(landmarks),
            "features": list(features) if not isinstance(features, Mapping) else dict(features),
        }
        self.validator.validate_image_sample(sample)
        return sample
