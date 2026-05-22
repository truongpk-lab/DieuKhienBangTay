import cv2
import numpy as np

from DIEU_KHIEN_CHUOT.hand_feature_utils import extract_landmark_features


class FeatureExtractor:
    def __init__(
        self,
        process_size=224,
        model_image_size=64,
        bounding_box_margin=30,
    ):
        self.process_size = process_size
        self.model_image_size = model_image_size
        self.bounding_box_margin = bounding_box_margin
        self.hog = cv2.HOGDescriptor(
            (model_image_size, model_image_size),
            (16, 16),
            (8, 8),
            (8, 8),
            9,
        )

    def get_bounding_box(self, landmarks, image_width, image_height):
        xs = [int(point.x * image_width) for point in landmarks]
        ys = [int(point.y * image_height) for point in landmarks]

        x_min = max(0, min(xs) - self.bounding_box_margin)
        y_min = max(0, min(ys) - self.bounding_box_margin)
        x_max = min(image_width, max(xs) + self.bounding_box_margin)
        y_max = min(image_height, max(ys) + self.bounding_box_margin)

        if x_max <= x_min or y_max <= y_min:
            return None
        return x_min, y_min, x_max, y_max

    def preprocess_crop(self, crop):
        processed = cv2.resize(
            crop,
            (self.process_size, self.process_size),
            interpolation=cv2.INTER_AREA,
        )
        processed = cv2.GaussianBlur(processed, (3, 3), 0)
        return cv2.convertScaleAbs(processed, alpha=1.1, beta=8)

    def extract_image_features(self, image):
        resized = cv2.resize(
            image,
            (self.model_image_size, self.model_image_size),
            interpolation=cv2.INTER_AREA,
        )
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        edges = cv2.Canny(equalized, 60, 140)
        hog_features = self.hog.compute(equalized).flatten()
        gray_features = equalized.astype(np.float32).flatten() / 255.0
        edge_features = edges.astype(np.float32).flatten() / 255.0
        return np.concatenate([gray_features, edge_features, hog_features]).astype(
            np.float32
        )

    def extract_prediction_features(
        self,
        hand_landmarks,
        processed_preview,
        expected_feature_count=None,
    ):
        landmark_features = extract_landmark_features(hand_landmarks.landmark)
        if expected_feature_count in (None, landmark_features.shape[0]):
            return landmark_features.reshape(1, -1)

        image_features = self.extract_image_features(processed_preview)
        if image_features.shape[0] == expected_feature_count:
            return image_features.reshape(1, -1)

        raise ValueError(
            "So chieu feature cua model khong khop voi landmark hoac anh. "
            "Hay chay lai process_hand_gesture_dataset.py va train_model.py."
        )
