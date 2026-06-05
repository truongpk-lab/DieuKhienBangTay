"""Phase 16 smoke test with small fake static and dynamic datasets."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.dataset_collector import DatasetCollector
from training.dataset_validator import DatasetValidator
from training.evaluate_model import evaluate
from training.train_dynamic_gesture import train as train_dynamic
from training.train_static_gesture import train as train_static


def make_landmarks(kind: str, offset: float = 0.0):
    landmarks = [{"x": 0.5, "y": 0.8, "z": 0.0} for _ in range(21)]
    for index in range(21):
        landmarks[index] = {
            "x": 0.35 + (index % 5) * 0.06 + offset,
            "y": 0.82 - (index // 5) * 0.11,
            "z": 0.01 * (index % 3),
        }

    landmarks[0] = {"x": 0.5 + offset, "y": 0.9, "z": 0.0}
    landmarks[9] = {"x": 0.5 + offset, "y": 0.45, "z": 0.0}
    if kind == "pinch":
        landmarks[4] = {"x": 0.46 + offset, "y": 0.35, "z": 0.0}
        landmarks[8] = {"x": 0.48 + offset, "y": 0.34, "z": 0.0}
    else:
        landmarks[4] = {"x": 0.26 + offset, "y": 0.42, "z": 0.0}
        landmarks[8] = {"x": 0.58 + offset, "y": 0.18, "z": 0.0}
    return landmarks


def main():
    validator = DatasetValidator(
        allowed_profiles={
            "office": {"left_click", "move_mouse", "drag_drop"},
        }
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        dataset_dir = Path(tmp_dir) / "samples"
        model_dir = Path(tmp_dir) / "models"
        collector = DatasetCollector(dataset_dir=dataset_dir, validator=validator)

        for index in range(3):
            collector.collect_image_sample(
                profile="office",
                function_id="left_click",
                gesture_label="Pinch Index",
                landmarks=make_landmarks("pinch", index * 0.002),
                features=[],
                sample_id=f"static_pinch_{index}",
                created_at="2026-05-23T00:00:00Z",
            )
            collector.collect_image_sample(
                profile="office",
                function_id="move_mouse",
                gesture_label="Open Palm Move",
                landmarks=make_landmarks("open", index * 0.002),
                features=[],
                sample_id=f"static_open_{index}",
                created_at="2026-05-23T00:00:00Z",
            )

        video_collector = collector.video_samples
        for index in range(2):
            pinch_frames = [
                video_collector.create_frame(t=0.0, landmarks=make_landmarks("pinch", 0.001 * index), features=[]),
                video_collector.create_frame(t=0.4, landmarks=make_landmarks("pinch", 0.004 + 0.001 * index), features=[]),
                video_collector.create_frame(t=0.8, landmarks=make_landmarks("open", 0.006 + 0.001 * index), features=[]),
            ]
            collector.collect_video_sample(
                profile="office",
                function_id="drag_drop",
                gesture_label="Pinch Drag Drop",
                duration_sec=0.9,
                frames=pinch_frames,
                sample_id=f"dynamic_drag_{index}",
                created_at="2026-05-23T00:00:01Z",
            )

            open_frames = [
                video_collector.create_frame(t=0.0, landmarks=make_landmarks("open", 0.001 * index), features=[]),
                video_collector.create_frame(t=0.4, landmarks=make_landmarks("open", 0.002 + 0.001 * index), features=[]),
                video_collector.create_frame(t=0.8, landmarks=make_landmarks("open", 0.003 + 0.001 * index), features=[]),
            ]
            collector.collect_video_sample(
                profile="office",
                function_id="move_mouse",
                gesture_label="Open Palm Sweep",
                duration_sec=0.9,
                frames=open_frames,
                segments=["open_start", "open_move", "open_end"],
                sample_id=f"dynamic_open_{index}",
                created_at="2026-05-23T00:00:02Z",
            )

        static_result = train_static(dataset_dir, model_dir, version="static_fake")
        dynamic_result = train_dynamic(dataset_dir, model_dir, version="dynamic_fake")

        assert Path(static_result["model_path"]).exists()
        assert Path(static_result["label_mapping_path"]).exists()
        assert Path(dynamic_result["model_path"]).exists()
        assert Path(dynamic_result["label_mapping_path"]).exists()

        static_metrics = evaluate(static_result["model_path"], dataset_dir, "image")
        dynamic_metrics = evaluate(dynamic_result["model_path"], dataset_dir, "video")
        assert "macro_f1" in static_metrics
        assert "confusion_matrix" in dynamic_metrics
        assert static_metrics["accuracy"] >= 0.5
        assert dynamic_metrics["accuracy"] >= 0.5

    print("phase16 training pipeline fake data ok")


if __name__ == "__main__":
    main()
