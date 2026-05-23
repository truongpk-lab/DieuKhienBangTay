"""High-level dataset collector for Training UI samples."""

from __future__ import annotations

import json
import uuid
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .dataset_validator import DatasetValidator
from .image_sample_collector import ImageSampleCollector
from .video_sample_collector import VideoSampleCollector


class DatasetCollector:
    """Create, validate, and save Training UI sample JSON files."""

    def __init__(
        self,
        dataset_dir: str | Path = "data/training_samples",
        validator: DatasetValidator | None = None,
    ):
        self.dataset_dir = Path(dataset_dir)
        self.validator = validator or DatasetValidator()
        self.image_samples = ImageSampleCollector(self.validator)
        self.video_samples = VideoSampleCollector(self.validator)

    def collect_image_sample(
        self,
        *,
        profile: str,
        function_id: str,
        gesture_label: str,
        landmarks: Sequence[Mapping[str, Any]],
        features: Sequence[float] | Mapping[str, Any],
        sample_id: str | None = None,
        created_at: str | None = None,
    ) -> Path:
        sample = self.image_samples.create_sample(
            sample_id=sample_id or self.next_sample_id("image", gesture_label),
            profile=profile,
            function_id=function_id,
            gesture_label=gesture_label,
            created_at=created_at or self.utc_timestamp(),
            landmarks=landmarks,
            features=features,
        )
        return self.save_sample(sample)

    def collect_video_sample(
        self,
        *,
        profile: str,
        function_id: str,
        gesture_label: str,
        duration_sec: float,
        frames: Sequence[Mapping[str, Any]],
        segments: Sequence[Mapping[str, Any] | str] | None = None,
        sample_id: str | None = None,
        created_at: str | None = None,
    ) -> Path:
        sample = self.video_samples.create_sample(
            sample_id=sample_id or self.next_sample_id("video", gesture_label),
            profile=profile,
            function_id=function_id,
            gesture_label=gesture_label,
            duration_sec=duration_sec,
            frames=frames,
            segments=segments,
            created_at=created_at or self.utc_timestamp(),
        )
        return self.save_sample(sample)

    def save_sample(self, sample: Mapping[str, Any]) -> Path:
        """Validate then write one JSON sample.

        Invalid samples raise before creating files, so unlabeled samples or
        samples without hand landmarks are never persisted.
        """

        self.validator.validate(sample)
        sample_path = self.sample_path(sample)
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        with sample_path.open("w", encoding="utf-8") as sample_file:
            json.dump(sample, sample_file, ensure_ascii=False, indent=2)
            sample_file.write("\n")
        return sample_path

    def sample_path(self, sample: Mapping[str, Any]) -> Path:
        profile = str(sample["profile"])
        function_id = str(sample["function_id"])
        data_type = str(sample["data_type"])
        sample_id = str(sample["sample_id"])
        return self.dataset_dir / profile / function_id / data_type / f"{sample_id}.json"

    @staticmethod
    def next_sample_id(data_type: str, gesture_label: str) -> str:
        clean_label = "".join(
            character if character.isalnum() or character in ("_", "-") else "_"
            for character in gesture_label.strip().lower()
        ).strip("_")
        label_part = clean_label or "gesture"
        return f"{data_type}_{label_part}_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def utc_timestamp() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
