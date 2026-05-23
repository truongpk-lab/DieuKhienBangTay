from pathlib import Path

import cv2
import numpy as np

from DIEU_KHIEN_CHUOT.hand_feature_utils import extract_landmark_features


PROCESS_SIZE = 224
MODEL_IMAGE_SIZE = 64
BOUNDING_BOX_MARGIN = 30


class FeatureExtractor:
    def __init__(self, expected_feature_count=None):
        self.expected_feature_count = expected_feature_count
        self.hog = cv2.HOGDescriptor(
            (MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE),
            (16, 16),
            (8, 8),
            (8, 8),
            9,
        )

    def extract_features(self, image):
        resized = cv2.resize(image, (MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
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

        image_features = self.extract_features(processed_preview)
        if image_features.shape[0] == self.expected_feature_count:
            return image_features.reshape(1, -1)

        raise ValueError(
            "So chieu feature cua model khong khop voi landmark hoac anh. "
            "Hay chay lai process_hand_gesture_dataset.py va train_model.py."
        )

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
        processed = cv2.resize(crop, (PROCESS_SIZE, PROCESS_SIZE), interpolation=cv2.INTER_AREA)
        processed = cv2.GaussianBlur(processed, (3, 3), 0)
        processed = cv2.convertScaleAbs(processed, alpha=1.1, beta=8)
        return processed
