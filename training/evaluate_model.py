"""Model evaluation helpers for Phase 16 training pipelines."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
except ImportError:  # pragma: no cover - exercised only when sklearn is absent.
    accuracy_score = None
    confusion_matrix = None
    precision_recall_fscore_support = None


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return output_path


def find_samples(dataset_dir: str | Path, data_type: str) -> list[Path]:
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        return []
    return sorted(
        path
        for path in dataset_path.rglob("*.json")
        if path.is_file() and _safe_data_type(path) == data_type
    )


def _safe_data_type(path: Path) -> str | None:
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    return payload.get("data_type") if isinstance(payload, Mapping) else None


def numeric_feature_vector(features: Any) -> np.ndarray:
    import numpy as np

    if isinstance(features, Mapping):
        values = [features[key] for key in sorted(features)]
    else:
        values = list(features or [])

    numeric_values: list[float] = []
    for value in values:
        if isinstance(value, (int, float)):
            numeric_values.append(float(value))
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            numeric_values.extend(float(item) for item in value if isinstance(item, (int, float)))

    return np.asarray(numeric_values, dtype=np.float32)


def static_sample_features(sample: Mapping[str, Any]) -> np.ndarray:
    if sample.get("landmarks"):
        from backend.hand_runtime.feature_utils import extract_landmark_features

        return extract_landmark_features(sample["landmarks"])
    features = numeric_feature_vector(sample.get("features"))
    if features.size:
        return features
    raise ValueError(f"static sample has no usable landmark features: {sample.get('sample_id')}")


def sequence_sample_features(sample: Mapping[str, Any], max_feature_count: int | None = None) -> np.ndarray:
    import numpy as np

    frame_vectors = []
    for frame in sample.get("frames", []):
        vector = numeric_feature_vector(frame.get("features"))
        if not vector.size and frame.get("landmarks"):
            from backend.hand_runtime.feature_utils import extract_landmark_features

            vector = extract_landmark_features(frame["landmarks"])
        if vector.size:
            frame_vectors.append(vector)

    if not frame_vectors:
        raise ValueError(f"dynamic sample has no usable frame features: {sample.get('sample_id')}")

    feature_count = max_feature_count or max(vector.size for vector in frame_vectors)
    matrix = np.zeros((len(frame_vectors), feature_count), dtype=np.float32)
    for row, vector in enumerate(frame_vectors):
        clipped = vector[:feature_count]
        matrix[row, : clipped.size] = clipped

    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    delta = matrix[-1] - matrix[0]
    duration = float(sample.get("duration_sec", 0.0))
    frame_count = float(len(frame_vectors))
    segment_count = float(len(sample.get("segments", [])))
    return np.concatenate(
        [
            np.asarray([duration, frame_count, segment_count], dtype=np.float32),
            mean,
            std,
            delta,
        ]
    ).astype(np.float32)


def load_dataset(dataset_dir: str | Path, data_type: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    import numpy as np

    samples = [load_json(path) for path in find_samples(dataset_dir, data_type)]
    labels = [str(sample["gesture_label"]) for sample in samples]

    if data_type == "image":
        feature_rows = [static_sample_features(sample) for sample in samples]
    elif data_type == "video":
        max_count = _max_frame_feature_count(samples)
        feature_rows = [sequence_sample_features(sample, max_count) for sample in samples]
    else:
        raise ValueError("data_type must be image or video")

    if not feature_rows:
        return np.empty((0, 0), dtype=np.float32), np.asarray([], dtype=object), []

    width = max(row.size for row in feature_rows)
    matrix = np.zeros((len(feature_rows), width), dtype=np.float32)
    for index, row in enumerate(feature_rows):
        matrix[index, : row.size] = row
    return matrix, np.asarray(labels, dtype=object), labels


def _max_frame_feature_count(samples: Sequence[Mapping[str, Any]]) -> int:
    max_count = 0
    for sample in samples:
        for frame in sample.get("frames", []):
            vector = numeric_feature_vector(frame.get("features"))
            if not vector.size and frame.get("landmarks"):
                from backend.hand_runtime.feature_utils import extract_landmark_features

                vector = extract_landmark_features(frame["landmarks"])
            max_count = max(max_count, int(vector.size))
    return max_count


def evaluate_predictions(y_true: Sequence[Any], y_pred: Sequence[Any]) -> dict[str, Any]:
    true_values = list(y_true)
    pred_values = list(y_pred)
    labels = sorted({str(label) for label in true_values} | {str(label) for label in pred_values})

    if not true_values:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "macro_f1": 0.0,
            "labels": [],
            "confusion_matrix": [],
        }

    if accuracy_score is not None and precision_recall_fscore_support is not None:
        precision, recall, macro_f1, _ = precision_recall_fscore_support(
            true_values,
            pred_values,
            labels=labels,
            average="macro",
            zero_division=0,
        )
        matrix = (
            confusion_matrix(true_values, pred_values, labels=labels).tolist()
            if confusion_matrix is not None
            else _fallback_confusion_matrix(true_values, pred_values, labels)
        )
        return {
            "accuracy": float(accuracy_score(true_values, pred_values)),
            "precision": float(precision),
            "recall": float(recall),
            "macro_f1": float(macro_f1),
            "labels": labels,
            "confusion_matrix": matrix,
        }

    matrix = _fallback_confusion_matrix(true_values, pred_values, labels)
    correct = sum(1 for true, pred in zip(true_values, pred_values) if true == pred)
    precision, recall, macro_f1 = _fallback_macro_scores(true_values, pred_values, labels)
    return {
        "accuracy": correct / len(true_values),
        "precision": precision,
        "recall": recall,
        "macro_f1": macro_f1,
        "labels": labels,
        "confusion_matrix": matrix,
    }


def _fallback_confusion_matrix(y_true: Sequence[Any], y_pred: Sequence[Any], labels: Sequence[str]) -> list[list[int]]:
    label_to_index = {label: index for index, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]
    for true, pred in zip(y_true, y_pred):
        matrix[label_to_index[str(true)]][label_to_index[str(pred)]] += 1
    return matrix


def _fallback_macro_scores(y_true: Sequence[Any], y_pred: Sequence[Any], labels: Sequence[str]) -> tuple[float, float, float]:
    import numpy as np

    true_counter = Counter(str(label) for label in y_true)
    pred_counter = Counter(str(label) for label in y_pred)
    correct_counter = Counter(str(true) for true, pred in zip(y_true, y_pred) if true == pred)
    precisions = []
    recalls = []
    f1_scores = []
    for label in labels:
        precision = correct_counter[label] / pred_counter[label] if pred_counter[label] else 0.0
        recall = correct_counter[label] / true_counter[label] if true_counter[label] else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1_score)
    return float(np.mean(precisions)), float(np.mean(recalls)), float(np.mean(f1_scores))


def evaluate(model_path: str | Path, dataset_dir: str | Path, data_type: str = "image") -> dict[str, Any]:
    """Load a saved Phase 16 model and evaluate it against dataset samples."""

    import joblib

    payload = joblib.load(model_path)
    model = payload.get("model", payload) if isinstance(payload, Mapping) else payload
    x_values, y_true, _ = load_dataset(dataset_dir, data_type)
    if x_values.size == 0:
        raise ValueError(f"no {data_type} samples found in {dataset_dir}")
    y_pred = model.predict(x_values)
    return evaluate_predictions(y_true, y_pred)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a Phase 16 gesture model.")
    parser.add_argument("--model", required=True, help="Path to model.joblib")
    parser.add_argument("--dataset", default="data/training_samples", help="Training sample directory")
    parser.add_argument("--data-type", choices=("image", "video"), default="image")
    parser.add_argument("--output", help="Optional metrics JSON output path")
    args = parser.parse_args()

    metrics = evaluate(args.model, args.dataset, args.data_type)
    if args.output:
        write_json(args.output, metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
