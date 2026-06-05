import argparse
from pathlib import Path

import cv2

from . import config
from .mouse import DryRunMouseController, MouseController, PYAUTOGUI_AVAILABLE
from .camera import CameraService
from .classifier import HandGestureClassifier
from .gesture_state import GestureActionState

try:
    import mediapipe as mp

    MEDIAPIPE_AVAILABLE = True
except ModuleNotFoundError:
    mp = None
    MEDIAPIPE_AVAILABLE = False


class HandMouseApp:
    def __init__(self, camera_index=0, dry_run=False, base_dir=None):
        if not MEDIAPIPE_AVAILABLE:
            raise ModuleNotFoundError(
                "Chua cai mediapipe. Hay cai bang: pip install mediapipe"
            )

        self.base_dir = (
            Path(base_dir)
            if base_dir is not None
            else Path(__file__).resolve().parent
        )
        self.classifier = HandGestureClassifier(self.base_dir)
        self.camera = CameraService(camera_index)
        self.mouse = DryRunMouseController() if dry_run else MouseController()
        self.gestures = GestureActionState(self.mouse)
        self.dry_run = dry_run

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.hand_was_lost = True

    def get_bounding_box(self, landmarks, image_width, image_height):
        xs = [int(point.x * image_width) for point in landmarks]
        ys = [int(point.y * image_height) for point in landmarks]

        x_min = max(0, min(xs) - config.BOUNDING_BOX_MARGIN)
        y_min = max(0, min(ys) - config.BOUNDING_BOX_MARGIN)
        x_max = min(image_width, max(xs) + config.BOUNDING_BOX_MARGIN)
        y_max = min(image_height, max(ys) + config.BOUNDING_BOX_MARGIN)

        if x_max <= x_min or y_max <= y_min:
            return None
        return x_min, y_min, x_max, y_max

    def preprocess_crop(self, crop):
        processed = cv2.resize(crop, (config.PROCESS_SIZE, config.PROCESS_SIZE), interpolation=cv2.INTER_AREA)
        processed = cv2.GaussianBlur(processed, (3, 3), 0)
        processed = cv2.convertScaleAbs(processed, alpha=1.1, beta=8)
        return processed

    def handle_hand_lost(self):
        self.classifier.reset()
        self.gestures.handle_hand_lost()
        self.hand_was_lost = True

    def predict_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            self.handle_hand_lost()
            return None, None

        hand_landmarks = results.multi_hand_landmarks[0]
        height, width = frame.shape[:2]
        box = self.get_bounding_box(hand_landmarks.landmark, width, height)
        if box is None:
            self.handle_hand_lost()
            return None, hand_landmarks

        x_min, y_min, x_max, y_max = box
        crop = frame[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            self.handle_hand_lost()
            return None, hand_landmarks

        if self.hand_was_lost:
            self.classifier.reset()
            self.gestures.prepare_hand_reacquire()
            self.hand_was_lost = False

        processed_preview = self.preprocess_crop(crop)
        prediction = self.classifier.predict(hand_landmarks, processed_preview)
        prediction["box"] = (x_min, y_min, x_max, y_max)
        prediction["preview"] = processed_preview

        self.gestures.apply(
            prediction["stable_label"],
            prediction["label"],
            hand_landmarks.landmark,
        )
        return prediction, hand_landmarks

    def draw_ui(self, frame, prediction, hand_landmarks):
        if hand_landmarks is not None:
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        if prediction is None:
            cv2.putText(frame, "Gesture: khong nhan duoc", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            x_min, y_min, x_max, y_max = prediction["box"]
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(frame, f"Predict: {prediction['label']} ({prediction['label_source']})", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            cv2.putText(frame, f"Stable: {prediction['stable_label']}", (10, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 255), 2)
            cv2.putText(frame, f"Model: {prediction['model_label']}", (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 255, 180), 2)
            cv2.putText(frame, f"Pinch: {self.gestures.last_pinch_ratio or 0:.2f}", (10, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            preview = cv2.resize(prediction["preview"], (160, 160), interpolation=cv2.INTER_AREA)
            frame[10:170, frame.shape[1] - 170:frame.shape[1] - 10] = preview
            cv2.rectangle(frame, (frame.shape[1] - 170, 10), (frame.shape[1] - 10, 170), (255, 255, 255), 2)

        drag_text = "DRAGGING" if self.gestures.dragging else "RELEASED"
        cv2.putText(frame, f"Drag: {drag_text}", (10, 147), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        mouse_text = f"Mouse: ON ({self.mouse.backend})" if self.gestures.mouse_enabled else "Mouse: OFF"
        cv2.putText(frame, mouse_text, (10, 172), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2)
        cv2.putText(frame, "Open=Move | 1=Left | 2=Right | Pinch=Hold drag", (10, 197), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
        cv2.putText(frame, f"3_left/right={config.NAV_MODE} | 3_up/down scroll", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "Nhan Q hoac ESC de thoat", (10, 244), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def run(self):
        if not self.camera.is_opened():
            raise RuntimeError("Khong mo duoc webcam.")

        try:
            while True:
                success, frame = self.camera.read()
                if not success:
                    break

                prediction, hand_landmarks = self.predict_frame(frame)
                self.draw_ui(frame, prediction, hand_landmarks)
                cv2.imshow("Hand Gesture Mouse", frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
        finally:
            if self.gestures.dragging and self.gestures.mouse_enabled:
                self.mouse.mouse_up()
            self.camera.release()
            self.hands.close()
            cv2.destroyAllWindows()


def build_parser():
    parser = argparse.ArgumentParser(description="Dieu khien chuot bang cu chi ban tay.")
    parser.add_argument("--camera-index", type=int, default=0, help="Chi so webcam OpenCV.")
    parser.add_argument("--dry-run", action="store_true", help="Ghi nhan action nhung khong dieu khien chuot that.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    print("Ung dung nhan dien cu chi va dieu khien chuot")
    print("Can model da train trong thu muc trained_model")
    if args.dry_run:
        print("Dry-run: khong tac dong chuot/phim that.")
    elif not PYAUTOGUI_AVAILABLE:
        print("Khong tim thay pyautogui. Ung dung se thu dung Windows API de dieu khien chuot.")
    print("Nhan Q hoac ESC de thoat")

    app = HandMouseApp(camera_index=args.camera_index, dry_run=args.dry_run)
    app.run()


if __name__ == "__main__":
    main()
