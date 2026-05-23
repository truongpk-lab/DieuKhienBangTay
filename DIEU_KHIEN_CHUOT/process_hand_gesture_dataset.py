import csv
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ModuleNotFoundError:
    mp = None
    MEDIAPIPE_AVAILABLE = False

from hand_feature_utils import extract_landmark_features, mirror_landmarks, transform_landmarks


INPUT_IMAGE_SIZE = 224
BOUNDING_BOX_MARGIN = 30
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
AUGMENT_HORIZONTAL_FLIP = True
TARGET_TOTAL_LANDMARK_SAMPLES = 2000
EXTRA_AUGMENT_PER_LABEL = 50
RANDOM_SEED = 42
FLIP_LABEL_MAP = {
    "three_left": "three_right",
    "three_right": "three_left",
}


def label_for_augmentation(label, augmentation):
    if augmentation == "flip":
        return FLIP_LABEL_MAP.get(label, label)
    return label


def stable_seed(value):
    digest = hashlib.sha256(f"{RANDOM_SEED}:{value}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


class HandImageProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.dataset_dir = self.base_dir / "dataset_hand_mouse"
        self.raw_images_dir = self.dataset_dir / "raw_images"
        self.legacy_images_dir = self.dataset_dir / "images"
        self.processed_dir = self.base_dir / "processed_dataset"
        self.processed_images_dir = self.processed_dir / "processed_images"
        self.processed_manifest_path = self.processed_dir / "processed_manifest.csv"
        self.processed_landmarks_path = self.processed_dir / "processed_landmarks.csv"
        self.skipped_manifest_path = self.processed_dir / "skipped_manifest.csv"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.processed_images_dir.mkdir(parents=True, exist_ok=True)

        self.mp_hands = None
        self.hands = None
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                model_complexity=1,
                min_detection_confidence=0.6,
            )

    def load_manifest_rows(self):
        manifest_path = self.dataset_dir / "manifest.csv"
        if not manifest_path.exists():
            return None

        with manifest_path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    def list_dataset_images(self):
        dataset_source_dir = None
        if self.raw_images_dir.exists():
            dataset_source_dir = self.raw_images_dir
        elif self.legacy_images_dir.exists():
            dataset_source_dir = self.legacy_images_dir
        else:
            raise FileNotFoundError(
                f"Khong tim thay thu muc dataset: {self.raw_images_dir} hoac {self.legacy_images_dir}"
            )

        image_paths = []
        for path in dataset_source_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                image_paths.append(path)
        return sorted(image_paths)

    def list_dataset_samples(self):
        manifest_rows = self.load_manifest_rows()
        if manifest_rows is None:
            return [
                {
                    "sample_id": image_path.stem,
                    "label": image_path.parent.name,
                    "image_path": image_path.relative_to(self.dataset_dir).as_posix(),
                    "json_path": "",
                }
                for image_path in self.list_dataset_images()
            ]

        samples = []
        for row in manifest_rows:
            if row.get("image_path"):
                samples.append(row)
        return samples

    def detect_hand_landmarks(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            return None
        return results.multi_hand_landmarks[0].landmark

    def get_bounding_box(self, landmarks, image_width, image_height):
        xs = [int(point.x * image_width) for point in landmarks]
        ys = [int(point.y * image_height) for point in landmarks]

        x_min = max(0, min(xs) - BOUNDING_BOX_MARGIN)
        y_min = max(0, min(ys) - BOUNDING_BOX_MARGIN)
        x_max = min(image_width, max(xs) + BOUNDING_BOX_MARGIN)
        y_max = min(image_height, max(ys) + BOUNDING_BOX_MARGIN)

        if x_max <= x_min or y_max <= y_min:
            return None
        return x_min, y_min, x_max, y_max

    def preprocess_crop(self, crop):
        resized = cv2.resize(crop, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
        denoised = cv2.GaussianBlur(resized, (3, 3), 0)
        enhanced = cv2.convertScaleAbs(denoised, alpha=1.1, beta=8)
        return enhanced

    def process_one_image(self, image_path):
        if not MEDIAPIPE_AVAILABLE:
            return None, "Thieu mediapipe, bo qua xu ly crop anh"

        image = cv2.imread(str(image_path))
        if image is None:
            return None, "Khong doc duoc anh"

        landmarks = self.detect_hand_landmarks(image)
        if landmarks is None:
            return None, "Khong phat hien ban tay"

        height, width = image.shape[:2]
        box = self.get_bounding_box(landmarks, width, height)
        if box is None:
            return None, "Khong tao duoc bounding box"

        x_min, y_min, x_max, y_max = box
        crop = image[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            return None, "Vung crop rong"

        processed = self.preprocess_crop(crop)
        return processed, None

    def load_landmarks(self, json_path):
        if not json_path.exists():
            return None, "Khong tim thay file landmark JSON"

        try:
            with json_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            landmarks = payload.get("landmarks", [])
            extract_landmark_features(landmarks)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return None, f"Khong doc duoc landmark: {error}"

        return landmarks, None

    def landmark_feature_variants(self, landmarks, sample_id, add_extra_augment):
        feature_variants = [("original", extract_landmark_features(landmarks))]

        if AUGMENT_HORIZONTAL_FLIP:
            flipped_landmarks = mirror_landmarks(landmarks)
            feature_variants.append(("flip", extract_landmark_features(flipped_landmarks)))

        if add_extra_augment:
            rng = np.random.default_rng(stable_seed(sample_id))
            scale = float(rng.uniform(0.94, 1.06))
            rotation = float(rng.uniform(-6.0, 6.0))
            jitter_std = float(rng.uniform(0.002, 0.006))
            augmented_landmarks = transform_landmarks(
                landmarks,
                scale=scale,
                rotation_degrees=rotation,
                jitter_std=jitter_std,
                seed=stable_seed(f"{sample_id}:augment"),
            )
            feature_variants.append(("jitter", extract_landmark_features(augmented_landmarks)))

        return feature_variants

    def save_processed_image(self, input_path, processed_image, label=None, suffix=""):
        if label is None:
            label = input_path.parent.name
        output_label_dir = self.processed_images_dir / label
        output_label_dir.mkdir(parents=True, exist_ok=True)

        output_name = f"{input_path.stem}{suffix}{input_path.suffix}"
        output_path = output_label_dir / output_name
        cv2.imwrite(str(output_path), processed_image)
        return output_path

    def write_manifest(self, processed_rows, landmark_rows, skipped_rows):
        with self.processed_manifest_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["label", "original_path", "processed_path", "width", "height"],
            )
            writer.writeheader()
            writer.writerows(processed_rows)

        fieldnames = [
            "sample_id",
            "label",
            "source_label",
            "image_path",
            "json_path",
            "augmentation",
            "feature_count",
            "features_json",
        ]
        with self.processed_landmarks_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(landmark_rows)

        with self.skipped_manifest_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["label", "original_path", "reason"],
            )
            writer.writeheader()
            writer.writerows(skipped_rows)

    def run(self):
        samples = self.list_dataset_samples()
        processed_rows = []
        landmark_rows = []
        skipped_rows = []
        extra_augment_counts = {}

        for sample in samples:
            label = sample.get("label", "")
            image_path_value = sample.get("image_path", "")
            json_path_value = sample.get("json_path", "")
            image_path = self.dataset_dir / image_path_value
            relative_input = image_path.relative_to(self.base_dir).as_posix()

            if json_path_value:
                json_path = self.dataset_dir / json_path_value
                landmarks, error = self.load_landmarks(json_path)
                if error is None:
                    sample_id = sample.get("sample_id", image_path.stem)
                    current_extra_count = extra_augment_counts.get(label, 0)
                    add_extra_augment = current_extra_count < EXTRA_AUGMENT_PER_LABEL
                    feature_variants = self.landmark_feature_variants(
                        landmarks,
                        sample_id,
                        add_extra_augment=add_extra_augment,
                    )
                    if add_extra_augment:
                        extra_augment_counts[label] = current_extra_count + 1

                    for augmentation, features in feature_variants:
                        output_sample_id = sample_id if augmentation == "original" else f"{sample_id}_{augmentation}"
                        output_label = label_for_augmentation(label, augmentation)
                        landmark_rows.append(
                            {
                                "sample_id": output_sample_id,
                                "label": output_label,
                                "source_label": label,
                                "image_path": image_path_value,
                                "json_path": json_path_value,
                                "augmentation": augmentation,
                                "feature_count": int(features.shape[0]),
                                "features_json": json.dumps(features.tolist(), separators=(",", ":")),
                            }
                        )
                else:
                    skipped_rows.append(
                        {
                            "label": label,
                            "original_path": json_path.relative_to(self.base_dir).as_posix(),
                            "reason": error,
                        }
                    )

            processed_image, error = self.process_one_image(image_path)

            if error is not None:
                if MEDIAPIPE_AVAILABLE or not json_path_value:
                    skipped_rows.append(
                        {
                            "label": label,
                            "original_path": relative_input,
                            "reason": error,
                        }
                    )
                continue

            image_variants = [("original", processed_image)]
            if AUGMENT_HORIZONTAL_FLIP:
                image_variants.append(("flip", cv2.flip(processed_image, 1)))

            for augmentation, variant_image in image_variants:
                suffix = "" if augmentation == "original" else "_flip"
                output_label = label_for_augmentation(label, augmentation)
                output_path = self.save_processed_image(image_path, variant_image, label=output_label, suffix=suffix)
                processed_rows.append(
                    {
                        "label": output_label,
                        "original_path": relative_input,
                        "processed_path": output_path.relative_to(self.base_dir).as_posix(),
                        "width": variant_image.shape[1],
                        "height": variant_image.shape[0],
                    }
                )

        self.write_manifest(processed_rows, landmark_rows, skipped_rows)

        print("Da xu ly xong dataset.")
        print(f"Tong so mau doc duoc: {len(samples)}")
        print(f"So anh xu ly thanh cong: {len(processed_rows)}")
        print(f"So landmark dung de train: {len(landmark_rows)}")
        print(f"Muc tieu landmark sau augment: {TARGET_TOTAL_LANDMARK_SAMPLES}")
        print(f"So mau jitter moi lop: {EXTRA_AUGMENT_PER_LABEL}")
        print(f"So anh bo qua: {len(skipped_rows)}")
        print(f"Thu muc anh da xu ly: {self.processed_images_dir}")
        print(f"Manifest anh da xu ly: {self.processed_manifest_path}")
        print(f"Features landmark da xu ly: {self.processed_landmarks_path}")
        print(f"Manifest anh bo qua: {self.skipped_manifest_path}")


def main():
    processor = HandImageProcessor()
    processor.run()


if __name__ == "__main__":
    main()
