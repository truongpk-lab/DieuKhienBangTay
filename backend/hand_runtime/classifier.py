import json
from collections import Counter, deque
from pathlib import Path

import cv2
import joblib
import numpy as np

from .feature_utils import extract_landmark_features

from . import config
from .geometry import corrected_label


class HandGestureClassifier:
    def __init__(self, base_dir=None):
        self.base_dir = (
            Path(base_dir)
            if base_dir is not None
            else Path(__file__).resolve().parent
        )
        self.model_dir = self.base_dir / "trained_model"
        self.model_path = self.model_dir / "best_hand_gesture_model.joblib"
        self.label_map_path = self.model_dir / "label_mapping.json"

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Chua tim thay model: {self.model_path}. Hay chay train_model.py truoc."
            )
        if not self.label_map_path.exists():
            raise FileNotFoundError(
                f"Chua tim thay label map: {self.label_map_path}. Hay chay train_model.py truoc."
            )

        self.model = joblib.load(self.model_path)
        self.id_to_label = self.load_id_to_label()
        self.expected_feature_count = self.get_expected_feature_count()
        self.prediction_buffer = deque(maxlen=config.PREDICTION_BUFFER_SIZE)
        self.current_stable_label = "none"
        self.hog = cv2.HOGDescriptor(
            (config.MODEL_IMAGE_SIZE, config.MODEL_IMAGE_SIZE),
            (16, 16),
            (8, 8),
            (8, 8),
            9,
        )

    def load_id_to_label(self):
        with self.label_map_path.open("r", encoding="utf-8") as file:
            label_to_id = json.load(file)
        return {int(idx): label for label, idx in label_to_id.items()}

    def get_expected_feature_count(self):
        if hasattr(self.model, "n_features_in_"):
            return int(self.model.n_features_in_)

        classifier = getattr(self.model, "named_steps", {}).get("classifier")
        if classifier is not None and hasattr(classifier, "n_features_in_"):
            return int(classifier.n_features_in_)

        return None

    def reset(self):
        self.prediction_buffer.clear()
        self.current_stable_label = "none"

    def extract_image_features(self, image):
        resized = cv2.resize(image, (config.MODEL_IMAGE_SIZE, config.MODEL_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        edges = cv2.Canny(equalized, 60, 140)
        hog_features = self.hog.compute(equalized).flatten()
        gray_features = equalized.astype(np.float32).flatten() / 255.0
        edge_features = edges.astype(np.float32).flatten() / 255.0
        return np.concatenate([gray_features, edge_features, hog_features]).astype(np.float32)

    def extract_prediction_features(self, hand_landmarks, processed_preview):
        landmark_features = extract_landmark_features(hand_landmarks.landmark)
        if self.expected_feature_count in (None, landmark_features.shape[0]):
            return landmark_features.reshape(1, -1)

        image_features = self.extract_image_features(processed_preview)
        if image_features.shape[0] == self.expected_feature_count:
            return image_features.reshape(1, -1)

        raise ValueError(
            "So chieu feature cua model khong khop voi landmark hoac anh. "
            "Hay chay lai process_hand_gesture_dataset.py va train_model.py."
        )

    def stable_label(self):
        if not self.prediction_buffer:
            self.current_stable_label = "none"
            return self.current_stable_label

        top_label, top_count = Counter(self.prediction_buffer).most_common(1)[0]
        if top_count >= config.STABLE_MIN_COUNT:
            self.current_stable_label = top_label
        else:
            self.current_stable_label = "none"
        return self.current_stable_label

    def predict(self, hand_landmarks, processed_preview):
        features = self.extract_prediction_features(hand_landmarks, processed_preview)
        pred_id = int(self.model.predict(features)[0])
        model_label = self.id_to_label.get(pred_id, f"class_{pred_id}")
        pred_label, label_source = corrected_label(model_label, hand_landmarks.landmark)
        self.prediction_buffer.append(pred_label)
        stable_label = self.stable_label()
        return {
            "label": pred_label,
            "model_label": model_label,
            "label_source": label_source,
            "stable_label": stable_label,
        }
