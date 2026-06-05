"""Train a static gesture classifier from landmark feature samples."""

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
    static_sample_features,
    write_json,
)


def utc_version() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_static_samples(dataset_dir: str | Path) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    import numpy as np

    samples = [load_json(path) for path in find_samples(dataset_dir, "image")]
    feature_rows = [static_sample_features(sample) for sample in samples]
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


def can_stratify(labels: np.ndarray) -> bool:
    import numpy as np

    _, counts = np.unique(labels, return_counts=True)
    return len(counts) > 1 and bool(np.all(counts >= 2))


def build_classifier(labels: np.ndarray):
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    if len(set(labels)) < 2:
        return DummyClassifier(strategy="most_frequent")
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=160,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train(
    dataset_dir: str | Path = "data/training_samples",
    output_dir: str | Path = "models",
    version: str | None = None,
) -> dict[str, Any]:
    x_values, y_values, samples = load_static_samples(dataset_dir)
    if x_values.size == 0:
        raise ValueError(f"no static image samples found in {dataset_dir}")

    version_id = version or f"static_gesture_{utc_version()}"
    model_dir = Path(output_dir) / version_id
    if model_dir.exists():
        raise FileExistsError(f"model version already exists: {model_dir}")
    model_dir.mkdir(parents=True)

    label_mapping = make_label_mapping(y_values)
    classifier = build_classifier(y_values)

    split_metrics: dict[str, Any]
    if len(y_values) >= 4 and can_stratify(y_values):
        from sklearn.model_selection import train_test_split

        class_count = len(set(y_values))
        test_size = max(0.25, class_count / len(y_values))
        x_train, x_test, y_train, y_test = train_test_split(
            x_values,
            y_values,
            test_size=test_size,
            random_state=42,
            stratify=y_values,
        )
        classifier.fit(x_train, y_train)
        split_metrics = evaluate_predictions(y_test, classifier.predict(x_test))
        split_metrics["split"] = "stratified_holdout"
        split_metrics["train_sample_count"] = int(len(y_train))
        split_metrics["test_sample_count"] = int(len(y_test))
    else:
        classifier.fit(x_values, y_values)
        split_metrics = evaluate_predictions(y_values, classifier.predict(x_values))
        split_metrics["split"] = "resubstitution_small_dataset"
        split_metrics["train_sample_count"] = int(len(y_values))
        split_metrics["test_sample_count"] = int(len(y_values))

    model_path = model_dir / "model.joblib"
    import joblib

    payload = {
        "model_type": "static_gesture_classifier",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "feature_source": "landmark_features",
        "sample_count": len(samples),
        "label_mapping": label_mapping,
        "model": classifier,
    }
    joblib.dump(payload, model_path)

    metrics = {
        **split_metrics,
        "model_type": "static_gesture_classifier",
        "sample_count": len(samples),
        "labels": sorted(label_mapping),
        "model_path": str(model_path),
    }
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
    parser = argparse.ArgumentParser(description="Train a static gesture classifier.")
    parser.add_argument("--dataset", default="data/training_samples", help="Training sample directory")
    parser.add_argument("--output-dir", default="models", help="Versioned model output root")
    parser.add_argument("--version", help="Optional unique version directory name")
    args = parser.parse_args()

    result = train(args.dataset, args.output_dir, args.version)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
