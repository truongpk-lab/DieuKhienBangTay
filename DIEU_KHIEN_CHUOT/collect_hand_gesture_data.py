import csv
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp


TARGET_SAMPLES_PER_LABEL = 100
AUTO_CAPTURE_INTERVAL = 0.35


LABEL_KEYS = {
    "o": "open_hand",
    "1": "one_finger",
    "2": "two_fingers",
    "f": "fist",
    "r": "three_right",
    "l": "three_left",
    "u": "three_up",
    "d": "three_down",
}


class HandGestureCollector:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.dataset_dir = self.base_dir / "dataset_hand_mouse"
        self.raw_images_dir = self.dataset_dir / "raw_images"
        self.manifest_path = self.dataset_dir / "raw_manifest.csv"

        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.raw_images_dir.mkdir(parents=True, exist_ok=True)

        self.current_label = "open_hand"
        self.sample_counts = self.load_existing_counts()
        self.ensure_manifest()
        self.last_capture_time = 0.0

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self.cap = cv2.VideoCapture(0)

    def load_existing_counts(self):
        counts = {label: 0 for label in LABEL_KEYS.values()}
        if not self.manifest_path.exists():
            return counts

        with self.manifest_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                label = row.get("label", "")
                if label in counts:
                    counts[label] += 1
        return counts

    def ensure_manifest(self):
        if self.manifest_path.exists():
            return

        with self.manifest_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "sample_id",
                    "label",
                    "image_path",
                    "handedness",
                    "captured_at",
                ]
            )

    def next_sample_id(self, label):
        self.sample_counts[label] += 1
        return f"{label}_{self.sample_counts[label]:03d}"

    def save_sample(self, frame, results):
        if not results.multi_hand_landmarks:
            return False, "Chua thay ban tay trong khung hinh."

        handedness = "Unknown"
        if results.multi_handedness:
            handedness = results.multi_handedness[0].classification[0].label

        sample_id = self.next_sample_id(self.current_label)
        label_dir = self.raw_images_dir / self.current_label
        label_dir.mkdir(parents=True, exist_ok=True)

        image_path = label_dir / f"{sample_id}.jpg"
        captured_at = datetime.now().isoformat(timespec="seconds")
        cv2.imwrite(str(image_path), frame)

        with self.manifest_path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    sample_id,
                    self.current_label,
                    image_path.relative_to(self.dataset_dir).as_posix(),
                    handedness,
                    captured_at,
                ]
            )

        return True, f"Da luu {sample_id}"

    def maybe_auto_save(self, frame, results, current_time):
        current_count = self.sample_counts.get(self.current_label, 0)
        if current_count >= TARGET_SAMPLES_PER_LABEL:
            return f"Nhan {self.current_label} da du {TARGET_SAMPLES_PER_LABEL} anh."

        if not results.multi_hand_landmarks:
            return "Dang cho ban tay vao khung hinh."

        if current_time - self.last_capture_time < AUTO_CAPTURE_INTERVAL:
            return f"Dang thu thap {self.current_label}: {current_count}/{TARGET_SAMPLES_PER_LABEL}"

        saved, message = self.save_sample(frame, results)
        if saved:
            self.last_capture_time = current_time
            updated_count = self.sample_counts.get(self.current_label, 0)
            if updated_count >= TARGET_SAMPLES_PER_LABEL:
                return f"Da hoan thanh {self.current_label}: {TARGET_SAMPLES_PER_LABEL} anh."
            return f"Dang thu thap {self.current_label}: {updated_count}/{TARGET_SAMPLES_PER_LABEL}"
        return message

    def draw_overlay(self, frame, results, message):
        current_count = self.sample_counts.get(self.current_label, 0)
        cv2.putText(frame, f"Label: {self.current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"So anh: {current_count}/{TARGET_SAMPLES_PER_LABEL}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2)
        cv2.putText(frame, "O=open | 1=one | 2=two | F=fist", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, "R=3 right | L=3 left | U=3 up | D=3 down", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, "Luu vao dataset_hand_mouse/raw_images", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, "Nhan Q hoac ESC de thoat", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, message, (10, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        y = 250
        for label, count in self.sample_counts.items():
            cv2.putText(frame, f"{label}: {count}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (180, 255, 180), 1)
            y += 22

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def run(self):
        if not self.cap.isOpened():
            raise RuntimeError("Khong mo duoc webcam.")

        message = "San sang thu thap anh vao dataset."

        while True:
            success, frame = self.cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            message = self.maybe_auto_save(frame, results, datetime.now().timestamp())

            self.draw_overlay(frame, results, message)
            cv2.imshow("Collect Hand Gesture Images", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

            key_char = chr(key).lower() if 0 <= key <= 255 else ""
            if key_char in LABEL_KEYS:
                self.current_label = LABEL_KEYS[key_char]
                self.last_capture_time = 0.0
                message = f"Da chuyen nhan sang: {self.current_label}"

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    print("Thu thap anh cu chi ban tay")
    print("Luu anh vao: dataset_hand_mouse/raw_images")
    print("Luu thong tin vao: dataset_hand_mouse/raw_manifest.csv")
    print("Phim nhan: O, 1, 2, F, R, L, U, D")
    print(f"Moi nhan thu thap toi da {TARGET_SAMPLES_PER_LABEL} anh")
    print("Nhan Q hoac ESC de thoat")

    collector = HandGestureCollector()
    collector.run()


if __name__ == "__main__":
    main()
