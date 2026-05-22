import cv2

try:
    import mediapipe as mp

    MEDIAPIPE_AVAILABLE = True
except ModuleNotFoundError:
    mp = None
    MEDIAPIPE_AVAILABLE = False


class HandTracker:
    def __init__(
        self,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ):
        if not MEDIAPIPE_AVAILABLE:
            raise ModuleNotFoundError(
                "Chua cai mediapipe. Hay cai bang: pip install mediapipe"
            )

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    @property
    def hand_landmark(self):
        return self.mp_hands.HandLandmark

    @property
    def hand_connections(self):
        return self.mp_hands.HAND_CONNECTIONS

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.hand_connections)

    def close(self):
        self.hands.close()
