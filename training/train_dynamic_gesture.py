"""Train a lightweight dynamic gesture sequence model."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evaluate_model import (
    evaluate_predictions,
    find_samples,
    load_json,
    sequence_sample_features,
    write_json,
)


class SequencePrototypeClassifier:
    """Small nearest-prototype classifier for early dynamic gesture data."""

    def __init__(self):
        self.prototypes: dict[str, np.ndarray] = {}
        self.labels_: list[str] = []

    def fit(self, x_values: np.ndarray, y_values: np.ndarray) -> "SequencePrototypeClassifier":
        self.labels_ = sorted(set(str(label) for label in y_values))
        for label in self.labels_:
            rows = x_values[y_values == label]
            self.prototypes[label] = rows.mean(axis=0)
        return self

    def predict(self, x_values: np.ndarray) -> np.ndarray:
        import numpy as np

        predictions = []
        for row in x_values:
            best_label = min(
                self.labels_,
                key=lambda label: float(np.linalg.norm(row - self.prototypes[label])),
            )
            predictions.append(best_label)
        return np.asarray(predictions, dtype=object)


def utc_version() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def max_frame_feature_count(samples: list[dict[str, Any]]) -> int:
    max_count = 0
    for sample in samples:
        for frame in sample.get("frames", []):
            features = frame.get("features")
            if isinstance(features, dict):
                count = len(features)
            else:
                count = len(features or [])
            max_count = max(max_count, count)
    return max_count or None


def load_dynamic_samples(dataset_dir: str | Path) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    import numpy as np

    samples = [load_json(path) for path in find_samples(dataset_dir, "video")]
    feature_count = max_frame_feature_count(samples)
    feature_rows = [sequence_sample_features(sample, feature_count) for sample in samples]
    labels = [str(sample["gesture_label"]) for sample in samples]

    if not feature_rows:
        return np.empty((0, 0), dtype=np.float32), np.asarray([], dtype=object), []

    width = max(row.size for row in feature_rows)
    x_values = np.zeros((len(feature_rows), width), dtype=np.float32)
    for index, row in enumerate(feature_rows):
        x_values[index, : row.size] = row
    return x_values, np.asarray(labels, dtype=object), samples


def make_label_mapping(labels: np.ndarray) -> dict[str, int]:
    return {label: index for index, label in enumerate(sorted(set(str(label) for label in labels)))}


def train(
    dataset_dir: str | Path = "data/training_samples",
    output_dir: str | Path = "models",
    version: str | None = None,
) -> dict[str, Any]:
    x_values, y_values, samples = load_dynamic_samples(dataset_dir)
    if x_values.size == 0:
        raise ValueError(f"no dynamic video samples found in {dataset_dir}")

    version_id = version or f"dynamic_gesture_{utc_version()}"
    model_dir = Path(output_dir) / version_id
    if model_dir.exists():
        raise FileExistsError(f"model version already exists: {model_dir}")
    model_dir.mkdir(parents=True)

    model = SequencePrototypeClassifier().fit(x_values, y_values)
    label_mapping = make_label_mapping(y_values)
    metrics = evaluate_predictions(y_values, model.predict(x_values))
    metrics.update(
        {
            "split": "resubstitution_sequence_skeleton",
            "model_type": "dynamic_sequence_prototype",
            "sample_count": len(samples),
            "labels": sorted(label_mapping),
        }
    )

    model_path = model_dir / "model.joblib"
    import joblib

    payload = {
        "model_type": "dynamic_sequence_prototype",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "feature_source": "sequence_landmark_features",
        "sample_count": len(samples),
        "label_mapping": label_mapping,
        "model": model,
    }
    joblib.dump(payload, model_path)

    metrics["model_path"] = str(model_path)
    write_json(model_dir / "label_mapping.json", label_mapping)
    write_json(model_dir / "metrics.json", metrics)
    write_json(model_dir / "confusion_matrix.json", {"labels": metrics["labels"], "matrix": metrics["confusion_matrix"]})
    return {
        "model_dir": str(model_dir),
        "model_path": str(model_path),
        "label_mapping_path": str(model_dir / "label_mapping.json"),
        "metrics": metrics,
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Train a dynamic gesture sequence model.")
    parser.add_argument("--dataset", default="data/training_samples", help="Training sample directory")
    parser.add_argument("--output-dir", default="models", help="Versioned model output root")
    parser.add_argument("--version", help="Optional unique version directory name")
    args = parser.parse_args()

    result = train(args.dataset, args.output_dir, args.version)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
