"""Validation for Training UI dataset samples.

This module only guards the sample collection contract. It does not train or
alter gesture/mouse behavior.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


DRAG_DROP_SEGMENTS = ("pinch_hold", "drag_move", "drag_release")


class DatasetValidationError(ValueError):
    """Raised when a dataset sample is incomplete or references bad metadata."""


class DatasetValidator:
    """Validate static image and dynamic video sample JSON payloads."""

    def __init__(
        self,
        profile_config_dir: str | Path | None = None,
        allowed_profiles: Mapping[str, Sequence[str]] | None = None,
    ):
        self.profile_config_dir = (
            Path(profile_config_dir)
            if profile_config_dir is not None
            else Path(__file__).resolve().parents[1] / "profiles" / "configs"
        )
        self.allowed_profiles = (
            {profile: set(functions) for profile, functions in allowed_profiles.items()}
            if allowed_profiles is not None
            else self._load_allowed_profiles()
        )

    def validate(self, sample: Mapping[str, Any]) -> Mapping[str, Any]:
        """Validate a sample by its data_type and return it unchanged."""

        data_type = sample.get("data_type")
        if data_type == "image":
            return self.validate_image_sample(sample)
        if data_type == "video":
            return self.validate_video_sample(sample)
        raise DatasetValidationError("data_type must be image or video")

    def validate_image_sample(self, sample: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_fields(
            sample,
            (
                "sample_id",
                "profile",
                "function_id",
                "gesture_label",
                "data_type",
                "created_at",
                "landmarks",
                "features",
            ),
        )
        self._validate_common_metadata(sample)
        self._validate_landmarks(sample.get("landmarks"), "landmarks")
        return sample

    def validate_video_sample(self, sample: Mapping[str, Any]) -> Mapping[str, Any]:
        self._require_fields(
            sample,
            (
                "sample_id",
                "profile",
                "function_id",
                "gesture_label",
                "data_type",
                "duration_sec",
                "frames",
                "segments",
            ),
        )
        self._validate_common_metadata(sample)

        frames = sample.get("frames")
        if not isinstance(frames, Sequence) or isinstance(frames, (str, bytes)) or not frames:
            raise DatasetValidationError("frames must be a non-empty list")

        for index, frame in enumerate(frames):
            if not isinstance(frame, Mapping):
                raise DatasetValidationError(f"frames[{index}] must be an object")
            self._require_fields(frame, ("t", "landmarks", "features"))
            if not isinstance(frame["t"], (int, float)):
                raise DatasetValidationError(f"frames[{index}].t must be a number")
            self._validate_landmarks(frame.get("landmarks"), f"frames[{index}].landmarks")

        duration_sec = sample.get("duration_sec")
        if not isinstance(duration_sec, (int, float)) or duration_sec < 0:
            raise DatasetValidationError("duration_sec must be a non-negative number")

        segments = sample.get("segments")
        if not isinstance(segments, Sequence) or isinstance(segments, (str, bytes)) or not segments:
            raise DatasetValidationError("segments must be a non-empty list")

        segment_names = [segment.get("name") if isinstance(segment, Mapping) else segment for segment in segments]
        if sample.get("function_id") == "drag_drop":
            missing_segments = [name for name in DRAG_DROP_SEGMENTS if name not in segment_names]
            if missing_segments:
                raise DatasetValidationError(
                    "drag_drop segments missing: " + ", ".join(missing_segments)
                )

        return sample

    def _validate_common_metadata(self, sample: Mapping[str, Any]) -> None:
        for field_name in ("sample_id", "profile", "function_id"):
            self._require_non_empty_string(sample.get(field_name), field_name)

        gesture_label = sample.get("gesture_label")
        if not isinstance(gesture_label, str) or not gesture_label.strip():
            raise DatasetValidationError("gesture_label is required")

        profile_id = str(sample["profile"])
        function_id = str(sample["function_id"])
        if profile_id not in self.allowed_profiles:
            raise DatasetValidationError(f"invalid profile: {profile_id}")
        if function_id not in self.allowed_profiles[profile_id]:
            raise DatasetValidationError(
                f"invalid function_id for profile {profile_id}: {function_id}"
            )

    def _validate_landmarks(self, landmarks: Any, field_name: str) -> None:
        if landmarks is None:
            raise DatasetValidationError(f"{field_name} is required")
        if not isinstance(landmarks, Sequence) or isinstance(landmarks, (str, bytes)):
            raise DatasetValidationError(f"{field_name} must be a list")
        if not landmarks:
            raise DatasetValidationError(f"{field_name} must not be empty")

    def _load_allowed_profiles(self) -> dict[str, set[str]]:
        allowed_profiles: dict[str, set[str]] = {}
        for profile_path in sorted(self.profile_config_dir.glob("*.json")):
            with profile_path.open("r", encoding="utf-8") as profile_file:
                profile = json.load(profile_file)
            profile_id = str(profile.get("id", "")).strip()
            functions = profile.get("functions", [])
            if profile_id and isinstance(functions, list):
                allowed_profiles[profile_id] = {
                    str(function.get("id", "")).strip()
                    for function in functions
                    if isinstance(function, Mapping) and str(function.get("id", "")).strip()
                }
        return allowed_profiles

    @staticmethod
    def _require_fields(sample: Mapping[str, Any], field_names: Sequence[str]) -> None:
        missing_fields = [field for field in field_names if field not in sample]
        if missing_fields:
            raise DatasetValidationError(
                "sample missing required fields: " + ", ".join(missing_fields)
            )

    @staticmethod
    def _require_non_empty_string(value: Any, field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise DatasetValidationError(f"{field_name} must be a non-empty string")
