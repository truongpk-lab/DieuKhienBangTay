"""Phase 15 smoke test for Training UI dataset collection."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.dataset_collector import DatasetCollector
from training.dataset_validator import DatasetValidationError, DatasetValidator


def make_landmarks():
    return [{"x": index / 20, "y": index / 40, "z": 0.0} for index in range(21)]


def main():
    validator = DatasetValidator(
        allowed_profiles={
            "office": {"drag_drop", "left_click"},
        }
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        collector = DatasetCollector(dataset_dir=tmp_dir, validator=validator)

        image_path = collector.collect_image_sample(
            profile="office",
            function_id="left_click",
            gesture_label="Pinch Index",
            landmarks=make_landmarks(),
            features=[0.1, 0.2, 0.3],
            sample_id="static_fake_001",
            created_at="2026-05-23T00:00:00Z",
        )
        image_sample = json.loads(image_path.read_text(encoding="utf-8"))
        assert image_sample["data_type"] == "image"
        assert image_sample["gesture_label"] == "Pinch Index"
        assert len(image_sample["landmarks"]) == 21

        video_collector = collector.video_samples
        frames = [
            video_collector.create_frame(t=0.0, landmarks=make_landmarks(), features=[0.1]),
            video_collector.create_frame(t=0.5, landmarks=make_landmarks(), features=[0.2]),
            video_collector.create_frame(t=1.0, landmarks=make_landmarks(), features=[0.3]),
        ]
        video_path = collector.collect_video_sample(
            profile="office",
            function_id="drag_drop",
            gesture_label="Pinch Drag Drop",
            duration_sec=1.2,
            frames=frames,
            sample_id="dynamic_fake_001",
            created_at="2026-05-23T00:00:01Z",
        )
        video_sample = json.loads(video_path.read_text(encoding="utf-8"))
        assert video_sample["data_type"] == "video"
        assert [segment["name"] for segment in video_sample["segments"]] == [
            "pinch_hold",
            "drag_move",
            "drag_release",
        ]
        assert all("landmarks" in frame and "features" in frame for frame in video_sample["frames"])

        try:
            collector.collect_image_sample(
                profile="office",
                function_id="left_click",
                gesture_label="",
                landmarks=make_landmarks(),
                features=[0.1],
            )
        except DatasetValidationError:
            pass
        else:
            raise AssertionError("missing label sample should not be saved")

        try:
            collector.collect_image_sample(
                profile="office",
                function_id="left_click",
                gesture_label="Pinch Index",
                landmarks=[],
                features=[0.1],
            )
        except DatasetValidationError:
            pass
        else:
            raise AssertionError("empty landmarks sample should not be saved")

        assert not list(Path(tmp_dir).glob("**/*gesture*.json"))

    print("phase15 dataset collector fake samples ok")


if __name__ == "__main__":
    main()
