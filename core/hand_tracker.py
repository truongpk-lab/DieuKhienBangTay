from types import SimpleNamespace

import numpy as np

try:
    import mediapipe as mp

    MEDIAPIPE_AVAILABLE = True
except ModuleNotFoundError:
    mp = None
    MEDIAPIPE_AVAILABLE = False


class HandTracker:
    def __init__(
        self,
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ):
        if not MEDIAPIPE_AVAILABLE:
            raise ModuleNotFoundError(
                "Chua cai mediapipe. Hay cai bang: pip install mediapipe"
            )

        self.mp = mp
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, rgb_frame):
        return self.hands.process(rgb_frame)

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def palm_control_point(self, landmarks):
        ids = [
            self.mp_hands.HandLandmark.WRIST,
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP,
            self.mp_hands.HandLandmark.PINKY_MCP,
        ]
        return SimpleNamespace(
            x=float(np.mean([landmarks[idx].x for idx in ids])),
            y=float(np.mean([landmarks[idx].y for idx in ids])),
        )

    def close(self):
        self.hands.close()
