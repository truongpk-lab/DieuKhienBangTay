import csv
import json
import re
from collections import Counter
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC

from hand_feature_utils import extract_landmark_features, mirror_landmarks


IMAGE_SIZE = 64
RANDOM_SEED = 42
TEST_SIZE = 0.3
CROSS_VALIDATION_FOLDS = 5
GROUP_ID_PATTERN = re.compile(r"^(?P<label>.+)_(?P<number>\d{3})$")
FLIP_LABEL_MAP = {
    "three_left": "three_right",
    "three_right": "three_left",
}


def label_for_augmentation(label, augmentation):
    if augmentation == "flip":
        return FLIP_LABEL_MAP.get(label, label)
    return label


def base_sample_id(sample_id):
    if sample_id.endswith("_flip"):
        return sample_id[:-5]
    return sample_id


def parse_group_id(group_id):
    match = GROUP_ID_PATTERN.match(group_id)
    if match is None:
        return group_id, -1
    return match.group("label"), int(match.group("number"))


class HandGestureTrainer:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.processed_dir = self.base_dir / "processed_dataset"
        self.processed_images_dir = self.processed_dir / "processed_images"
        self.processed_landmarks_path = self.processed_dir / "processed_landmarks.csv"
        self.dataset_manifest_path = self.base_dir / "dataset_hand_mouse" / "manifest.csv"
        self.dataset_dir = self.base_dir / "dataset_hand_mouse"
        self.model_dir = self.base_dir / "trained_model"
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model_path = self.model_dir / "best_hand_gesture_model.joblib"
        self.label_map_path = self.model_dir / "label_mapping.json"
        self.metrics_path = self.model_dir / "metrics.json"
        self.report_path = self.model_dir / "classification_report.txt"
        self.confusion_matrix_path = self.model_dir / "confusion_matrix.csv"
        self.model_comparison_path = self.model_dir / "model_comparison.csv"

        self.label_names = []
        self.hog = cv2.HOGDescriptor(
            (IMAGE_SIZE, IMAGE_SIZE),
            (16, 16),
            (8, 8),
            (8, 8),
            9,
        )
        self.feature_source = "image"

    def list_images(self):
        if not self.processed_images_dir.exists():
            raise FileNotFoundError(
                f"Khong tim thay thu muc anh da xu ly: {self.processed_images_dir}"
            )

        image_paths = []
        for path in self.processed_images_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                image_paths.append(path)
        return sorted(image_paths)

    def extract_features(self, image):
        resized = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        edges = cv2.Canny(equalized, 60, 140)
        hog_features = self.hog.compute(equalized).flatten()
        gray_features = equalized.astype(np.float32).flatten() / 255.0
        edge_features = edges.astype(np.float32).flatten() / 255.0
        return np.concatenate([gray_features, edge_features, hog_features]).astype(np.float32)

    def load_image_dataset(self):
        image_paths = self.list_images()
        if not image_paths:
            raise ValueError("Khong co anh nao trong processed_dataset/processed_images.")

        labels = sorted({path.parent.name for path in image_paths})
        self.label_names = labels
        label_to_id = {label: idx for idx, label in enumerate(labels)}

        features = []
        targets = []
        groups = []

        for image_path in image_paths:
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            features.append(self.extract_features(image))
            targets.append(label_to_id[image_path.parent.name])
            groups.append(base_sample_id(image_path.stem))

        if not features:
            raise ValueError("Doc anh that bai, khong tao duoc tap train.")

        return (
            np.array(features, dtype=np.float32),
            np.array(targets, dtype=np.int32),
            label_to_id,
            np.array(groups),
        )

    def load_processed_landmark_dataset(self):
        with self.processed_landmarks_path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))

        rows = [row for row in rows if row.get("label") and row.get("features_json")]
        if not rows:
            raise ValueError("processed_landmarks.csv khong co dong feature hop le.")

        labels = sorted({row["label"] for row in rows})
        self.label_names = labels
        label_to_id = {label: idx for idx, label in enumerate(labels)}

        features = []
        targets = []
        groups = []
        for row in rows:
            try:
                feature_values = json.loads(row["features_json"])
                features.append(np.array(feature_values, dtype=np.float32))
                targets.append(label_to_id[row["label"]])
                groups.append(base_sample_id(row.get("sample_id", "")))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue

        if not features:
            raise ValueError("Khong doc duoc feature landmark nao tu processed_landmarks.csv.")

        return (
            np.vstack(features).astype(np.float32),
            np.array(targets, dtype=np.int32),
            label_to_id,
            np.array(groups),
        )

    def load_raw_landmark_dataset(self):
        if not self.dataset_manifest_path.exists():
            raise FileNotFoundError(f"Khong tim thay manifest: {self.dataset_manifest_path}")

        with self.dataset_manifest_path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))

        labels = sorted({row["label"] for row in rows if row.get("label") and row.get("json_path")})
        self.label_names = labels
        label_to_id = {label: idx for idx, label in enumerate(labels)}

        features = []
        targets = []
        groups = []
        for row in rows:
            label = row.get("label")
            json_path_value = row.get("json_path")
            if label not in label_to_id or not json_path_value:
                continue

            json_path = self.dataset_dir / json_path_value
            try:
                with json_path.open("r", encoding="utf-8") as file:
                    payload = json.load(file)
                landmarks = payload.get("landmarks", [])
                features.append(extract_landmark_features(landmarks))
                targets.append(label_to_id[label])
                groups.append(row.get("sample_id", json_path.stem))
                flipped_label = label_for_augmentation(label, "flip")
                features.append(extract_landmark_features(mirror_landmarks(landmarks)))
                targets.append(label_to_id[flipped_label])
                groups.append(row.get("sample_id", json_path.stem))
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue

        if not features:
            raise ValueError("Khong doc duoc landmark JSON nao tu dataset_hand_mouse/manifest.csv.")

        return (
            np.vstack(features).astype(np.float32),
            np.array(targets, dtype=np.int32),
            label_to_id,
            np.array(groups),
        )

    def load_dataset(self):
        if self.processed_landmarks_path.exists():
            self.feature_source = "processed_landmarks"
            return self.load_processed_landmark_dataset()

        if self.dataset_manifest_path.exists():
            self.feature_source = "raw_landmarks"
            return self.load_raw_landmark_dataset()

        self.feature_source = "processed_images"
        return self.load_image_dataset()

    def temporal_group_split(self, targets, groups):
        if groups is None or len(groups) == 0:
            return None

        grouped = {}
        for group_id in np.unique(groups):
            prefix, number = parse_group_id(str(group_id))
            grouped.setdefault(prefix, []).append((number, str(group_id)))

        test_groups = set()
        for values in grouped.values():
            values = sorted(values, key=lambda item: item[0])
            holdout_count = max(1, int(round(len(values) * TEST_SIZE)))
            test_groups.update(group_id for _, group_id in values[-holdout_count:])

        train_idx = []
        test_idx = []
        for idx, group_id in enumerate(groups):
            if str(group_id) in test_groups:
                test_idx.append(idx)
            else:
                train_idx.append(idx)

        if not train_idx or not test_idx:
            return None

        train_labels = set(targets[train_idx].tolist())
        test_labels = set(targets[test_idx].tolist())
        expected_labels = set(range(len(self.label_names)))
        if train_labels != expected_labels or test_labels != expected_labels:
            return None

        return np.array(train_idx), np.array(test_idx)

    def build_candidates(self):
        return {
            "linear_svm_c0_15": Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LinearSVC(
                            C=0.15,
                            max_iter=12000,
                            class_weight="balanced",
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),
            "linear_svm_c0_35": Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LinearSVC(
                            C=0.35,
                            max_iter=12000,
                            class_weight="balanced",
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),
            "logistic_l2_c0_35": Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LogisticRegression(
                            C=0.35,
                            max_iter=3000,
                            class_weight="balanced",
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),
            "rbf_svm_conservative": Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        SVC(
                            C=1.5,
                            kernel="rbf",
                            gamma="scale",
                            class_weight="balanced",
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),
        }

    def select_best_model(self, x_train, y_train, groups_train=None):
        candidates = self.build_candidates()
        class_counts = Counter(y_train.tolist())
        min_class_count = min(class_counts.values())
        n_splits = min(CROSS_VALIDATION_FOLDS, min_class_count)
        if n_splits < 2:
            raise ValueError("Moi lop can it nhat 2 mau train de cross-validation.")

        use_group_cv = groups_train is not None and len(np.unique(groups_train)) >= n_splits
        if use_group_cv:
            cv = StratifiedGroupKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=RANDOM_SEED,
            )
        else:
            cv = StratifiedKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=RANDOM_SEED,
            )
        comparison_rows = []
        best_name = None
        best_model = None
        best_score = -1.0

        for model_name, model in candidates.items():
            fit_groups = groups_train if use_group_cv else None
            scores = cross_val_score(
                model,
                x_train,
                y_train,
                cv=cv,
                groups=fit_groups,
                scoring="accuracy",
                n_jobs=1,
            )
            mean_score = float(scores.mean())
            std_score = float(scores.std())
            comparison_rows.append(
                {
                    "model_name": model_name,
                    "cv_mean_accuracy": round(mean_score, 6),
                    "cv_std_accuracy": round(std_score, 6),
                }
            )

            if mean_score > best_score:
                best_score = mean_score
                best_name = model_name
                best_model = model

        with self.model_comparison_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["model_name", "cv_mean_accuracy", "cv_std_accuracy"])
            writer.writeheader()
            writer.writerows(comparison_rows)

        return best_name, best_model, best_score

    def save_confusion_matrix(self, matrix):
        with self.confusion_matrix_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["label"] + self.label_names)
            for label, row in zip(self.label_names, matrix):
                writer.writerow([label] + row.tolist())

    def save_outputs(self, model, label_to_id, metrics, report, confusion):
        joblib.dump(model, self.model_path)

        with self.label_map_path.open("w", encoding="utf-8") as file:
            json.dump(label_to_id, file, ensure_ascii=False, indent=2)

        with self.metrics_path.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, ensure_ascii=False, indent=2)

        self.report_path.write_text(report, encoding="utf-8")
        self.save_confusion_matrix(confusion)

    def run(self):
        features, targets, label_to_id, groups = self.load_dataset()
        class_counts = Counter(targets.tolist())
        if min(class_counts.values()) < 2:
            raise ValueError("Moi lop can it nhat 2 mau de chia train/test theo stratify.")

        x_train, x_test, y_train, y_test = train_test_split(
            features,
            targets,
            test_size=TEST_SIZE,
            random_state=RANDOM_SEED,
            stratify=targets,
        )
        groups_train = None
        split_strategy = "stratified_random_70_30"

        best_name, best_model, best_cv_score = self.select_best_model(x_train, y_train, groups_train)
        best_model.fit(x_train, y_train)

        train_pred = best_model.predict(x_train)
        test_pred = best_model.predict(x_test)

        metrics = {
            "num_samples": int(len(features)),
            "num_classes": int(len(self.label_names)),
            "feature_vector_size": int(features.shape[1]),
            "feature_source": self.feature_source,
            "split_strategy": split_strategy,
            "overfit_note": (
                "Accuracy 1.0 on this split means the current collected dataset is easy/separable. "
                "For real generalization, collect more samples across lighting, distance, hand angle, "
                "left/right hands, backgrounds, and different users."
            ),
            "train_samples": int(len(x_train)),
            "test_samples": int(len(x_test)),
            "best_model_name": best_name,
            "best_cv_accuracy": float(best_cv_score),
            "train_accuracy": float(accuracy_score(y_train, train_pred)),
            "test_accuracy": float(accuracy_score(y_test, test_pred)),
            "generalization_gap": float(accuracy_score(y_train, train_pred) - accuracy_score(y_test, test_pred)),
            "class_counts": {
                self.label_names[class_id]: int(count)
                for class_id, count in sorted(class_counts.items())
            },
        }

        report = classification_report(
            y_test,
            test_pred,
            target_names=self.label_names,
            digits=4,
            zero_division=0,
        )
        confusion = confusion_matrix(y_test, test_pred)

        self.save_outputs(best_model, label_to_id, metrics, report, confusion)

        print("Da train xong mo hinh toi uu.")
        print(f"So mau: {metrics['num_samples']}")
        print(f"So lop: {metrics['num_classes']}")
        print(f"Nguon feature: {metrics['feature_source']}")
        print(f"Cach chia train/test: {metrics['split_strategy']}")
        print(f"Model tot nhat: {metrics['best_model_name']}")
        print(f"CV accuracy: {metrics['best_cv_accuracy']:.4f}")
        print(f"Train accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Test accuracy: {metrics['test_accuracy']:.4f}")
        print(f"Do lech train-test: {metrics['generalization_gap']:.4f}")
        print(f"Model: {self.model_path}")
        print(f"So sanh mo hinh: {self.model_comparison_path}")
        print(f"Label map: {self.label_map_path}")
        print(f"Metrics: {self.metrics_path}")
        print(f"Report: {self.report_path}")
        print(f"Confusion matrix: {self.confusion_matrix_path}")


def main():
    trainer = HandGestureTrainer()
    trainer.run()


if __name__ == "__main__":
    main()
