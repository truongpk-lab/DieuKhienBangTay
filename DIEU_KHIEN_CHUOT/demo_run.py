import time
from collections import Counter, deque
from types import SimpleNamespace
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from actions.mouse_controller import MouseController, PYAUTOGUI_AVAILABLE
from core.camera_service import CameraService
from core.feature_extractor import FeatureExtractor
from core.gesture_classifier import GestureClassifier
from core.hand_tracker import HandTracker
from hand_feature_utils import landmarks_to_array

PREDICTION_BUFFER_SIZE = 7
STABLE_MIN_COUNT = 4
CLICK_COOLDOWN = 0.5
CLICK_FREEZE_DURATION = 0.35
FAST_CLICK_CONFIRM_FRAMES = 3
GESTURE_SWITCH_FREEZE_DURATION = 0.30
DRAG_PREP_FREEZE_DURATION = 0.25
DRAG_RELEASE_FREEZE_DURATION = 1.0
ACTION_COOLDOWN = 1.0
TAB_SWITCH_COOLDOWN = 0.75
SCROLL_COOLDOWN = 0.12
THREE_FINGER_NAV_MODE = "tabs_then_apps"
TAB_SWITCHES_BEFORE_APP_SWITCH = 4
MOVE_SMOOTHING = 0.50
FAST_MOVE_SMOOTHING = 0.70
HAND_POINT_SMOOTHING = 0.38
MOVE_MARGIN = 0.15
MOVE_DEAD_ZONE = 0
HAND_DEAD_ZONE = 0.0035
HAND_JUMP_GUARD = 0.085
MOVE_RESUME_FRAMES = 2
MOVE_GESTURE_CONFIRM_FRAMES = 3
HAND_REACQUIRE_FRAMES = 2
HAND_REACQUIRE_FREEZE_DURATION = 0.18
MOVE_SENSITIVITY = 2.35
MAX_MOVE_STEP = 96
HAND_EDGE_GUARD = 0.025
CLICK_GESTURES = {"one_finger", "two_fingers"}
MOVE_GESTURES = {"open_hand", "fist"}
NON_MOVING_GESTURES = {"one_finger", "two_fingers", "three_left", "three_right", "three_up", "three_down"}
MODEL_ONLY_GESTURES = {"three_left", "three_right", "three_up", "three_down"}
FINGER_TIP_IDS = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}
FINGER_PIP_IDS = {
    "thumb": 3,
    "index": 6,
    "middle": 10,
    "ring": 14,
    "pinky": 18,
}
FINGER_MCP_IDS = {
    "thumb": 2,
    "index": 5,
    "middle": 9,
    "ring": 13,
    "pinky": 17,
}
class HandGestureDemo:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.model_dir = self.base_dir / "trained_model"
        self.model_path = self.model_dir / "best_hand_gesture_model.joblib"
        self.label_map_path = self.model_dir / "label_mapping.json"

        self.classifier = GestureClassifier(self.model_path, self.label_map_path)
        self.feature_extractor = FeatureExtractor()
        self.hand_tracker = HandTracker()
        self.camera = CameraService(0)

        self.prediction_buffer = deque(maxlen=PREDICTION_BUFFER_SIZE)
        self.mouse = MouseController()
        self.mouse_enabled = self.mouse.enabled
        self.screen_w, self.screen_h = self.mouse.screen_w, self.mouse.screen_h
        self.prev_mouse_x = None
        self.prev_mouse_y = None
        self.sent_mouse_x = None
        self.sent_mouse_y = None
        self.move_resume_frames = 0
        self.move_gesture_label = None
        self.move_gesture_frames = 0
        self.hand_anchor_x = None
        self.hand_anchor_y = None
        self.filtered_hand_x = None
        self.filtered_hand_y = None
        self.mouse_anchor_x = None
        self.mouse_anchor_y = None
        self.last_click_time = 0.0
        self.raw_click_candidate = None
        self.raw_click_count = 0
        self.move_freeze_until = 0.0
        self.last_action_time = 0.0
        self.last_tab_app_direction = None
        self.tab_switch_count = 0
        self.last_scroll_time = 0.0
        self.dragging = False
        self.drag_release_until = 0.0
        self.current_stable_label = "none"
        self.last_stable_label = "none"
        self.last_raw_label = "none"
        self.hand_was_lost = True

    def get_stable_label(self):
        if not self.prediction_buffer:
            self.current_stable_label = "none"
            return self.current_stable_label

        top_label, top_count = Counter(self.prediction_buffer).most_common(1)[0]
        if top_count >= STABLE_MIN_COUNT:
            self.current_stable_label = top_label
        else:
            self.current_stable_label = "none"
        return self.current_stable_label

    def finger_states(self, landmarks):
        points = landmarks_to_array(landmarks)
        wrist = points[0, :2]
        palm_size = np.linalg.norm(points[9, :2] - wrist)
        if palm_size < 1e-6:
            palm_size = 1.0

        states = {}
        for finger in ("index", "middle", "ring", "pinky"):
            tip = points[FINGER_TIP_IDS[finger], :2]
            pip = points[FINGER_PIP_IDS[finger], :2]
            mcp = points[FINGER_MCP_IDS[finger], :2]
            tip_from_wrist = np.linalg.norm(tip - wrist)
            pip_from_wrist = np.linalg.norm(pip - wrist)
            tip_from_mcp = np.linalg.norm(tip - mcp)
            pip_from_mcp = np.linalg.norm(pip - mcp)
            states[finger] = (
                tip_from_wrist > pip_from_wrist + 0.12 * palm_size
                and tip_from_mcp > pip_from_mcp + 0.08 * palm_size
            )

        thumb_tip = points[FINGER_TIP_IDS["thumb"], :2]
        thumb_pip = points[FINGER_PIP_IDS["thumb"], :2]
        index_mcp = points[FINGER_MCP_IDS["index"], :2]
        states["thumb"] = np.linalg.norm(thumb_tip - index_mcp) > np.linalg.norm(thumb_pip - index_mcp) + 0.08 * palm_size
        return states, points, palm_size

    def direction_from_extended_fingers(self, states, points):
        extended_tips = [
            points[FINGER_TIP_IDS[finger], :2]
            for finger in ("index", "middle", "ring", "pinky")
            if states.get(finger)
        ]
        if not extended_tips:
            return None

        wrist = points[0, :2]
        tip_center = np.mean(np.array(extended_tips), axis=0)
        dx, dy = tip_center - wrist
        if abs(dx) > abs(dy):
            return "three_right" if dx > 0 else "three_left"
        return "three_down" if dy > 0 else "three_up"

    def central_three_direction(self, points, palm_size):
        central_fingers = ("index", "middle", "ring")
        tip_vectors = []
        extended_like_count = 0

        for finger in central_fingers:
            tip = points[FINGER_TIP_IDS[finger], :2]
            pip = points[FINGER_PIP_IDS[finger], :2]
            mcp = points[FINGER_MCP_IDS[finger], :2]
            tip_vector = tip - mcp
            tip_vectors.append(tip_vector)

            if np.linalg.norm(tip - mcp) > np.linalg.norm(pip - mcp) + 0.04 * palm_size:
                extended_like_count += 1

        if extended_like_count < 2:
            return None, 0.0

        mean_vector = np.mean(np.array(tip_vectors), axis=0)
        dx, dy = mean_vector
        dominant_axis = max(abs(dx), abs(dy), 1e-6)
        direction_strength = dominant_axis / max(palm_size, 1e-6)

        if direction_strength < 0.45:
            return None, 0.0

        if abs(dx) > abs(dy) * 1.15:
            return ("three_right" if dx > 0 else "three_left"), min(0.9, 0.72 + direction_strength * 0.18)

        if abs(dy) > abs(dx) * 1.05:
            return ("three_down" if dy > 0 else "three_up"), min(0.9, 0.72 + direction_strength * 0.18)

        return None, 0.0

    def geometry_label(self, landmarks):
        states, points, palm_size = self.finger_states(landmarks)
        non_thumb = ["index", "middle", "ring", "pinky"]
        extended_non_thumb = [finger for finger in non_thumb if states.get(finger)]
        extended_count = len(extended_non_thumb)
        central_direction, central_confidence = self.central_three_direction(points, palm_size)

        if extended_count >= 4:
            return "open_hand", 0.95

        if extended_count == 0:
            return "fist", 0.95

        if extended_count == 1 and states.get("index"):
            return "one_finger", 0.9

        if extended_count == 2 and states.get("index") and states.get("middle"):
            return "two_fingers", 0.9

        if extended_count == 3:
            direction = self.direction_from_extended_fingers(states, points)
            if direction is not None:
                return direction, 0.88

        if central_direction is not None and extended_count >= 2:
            return central_direction, central_confidence

        return None, 0.0

    def corrected_label(self, model_label, hand_landmarks):
        geometry_label, confidence = self.geometry_label(hand_landmarks.landmark)
        if geometry_label is None:
            return model_label, "model"

        if model_label == "three_down" and geometry_label == "open_hand":
            _, points, palm_size = self.finger_states(hand_landmarks.landmark)
            central_direction, central_confidence = self.central_three_direction(points, palm_size)
            if central_direction == "three_down" and central_confidence >= 0.78:
                return "three_down", "model+geometry"

        if confidence >= 0.94:
            return geometry_label, "geometry"

        if model_label in MODEL_ONLY_GESTURES and geometry_label in {"open_hand", "fist", "one_finger", "two_fingers"}:
            return geometry_label, "geometry"

        if model_label in {"open_hand", "fist", "one_finger", "two_fingers"} and geometry_label in MODEL_ONLY_GESTURES:
            return model_label, "model"

        return geometry_label, "geometry"

    def reset_mouse_anchor(self, clear_move_gate=True):
        self.prev_mouse_x = None
        self.prev_mouse_y = None
        self.sent_mouse_x = None
        self.sent_mouse_y = None
        self.move_resume_frames = 0
        if clear_move_gate:
            self.move_gesture_label = None
            self.move_gesture_frames = 0
        self.hand_anchor_x = None
        self.hand_anchor_y = None
        self.filtered_hand_x = None
        self.filtered_hand_y = None
        self.mouse_anchor_x = None
        self.mouse_anchor_y = None

    def reanchor_mouse_to_current_position(self, normalized_x, normalized_y):
        current_x, current_y = self.mouse.position()
        self.hand_anchor_x = normalized_x
        self.hand_anchor_y = normalized_y
        self.prev_mouse_x = float(current_x)
        self.prev_mouse_y = float(current_y)
        self.sent_mouse_x = int(current_x)
        self.sent_mouse_y = int(current_y)

    def palm_control_point(self, landmarks):
        ids = [
            self.hand_tracker.hand_landmark.WRIST,
            self.hand_tracker.hand_landmark.INDEX_FINGER_MCP,
            self.hand_tracker.hand_landmark.MIDDLE_FINGER_MCP,
            self.hand_tracker.hand_landmark.RING_FINGER_MCP,
            self.hand_tracker.hand_landmark.PINKY_MCP,
        ]
        return SimpleNamespace(
            x=float(np.mean([landmarks[idx].x for idx in ids])),
            y=float(np.mean([landmarks[idx].y for idx in ids])),
        )

    def handle_hand_lost(self):
        self.prediction_buffer.clear()
        self.current_stable_label = "none"
        self.raw_click_candidate = None
        self.raw_click_count = 0
        self.reset_mouse_anchor()
        if self.dragging and self.mouse_enabled:
            self.mouse.mouse_up()
            self.dragging = False
        self.drag_release_until = 0.0
        self.last_stable_label = "none"
        self.last_raw_label = "none"
        self.hand_was_lost = True

    def prepare_hand_reacquire(self):
        self.reset_mouse_anchor()
        self.prediction_buffer.clear()
        self.current_stable_label = "none"
        self.last_stable_label = "none"
        self.last_raw_label = "none"
        self.raw_click_candidate = None
        self.raw_click_count = 0
        self.move_resume_frames = -HAND_REACQUIRE_FRAMES
        self.move_freeze_until = max(self.move_freeze_until, time.time() + HAND_REACQUIRE_FREEZE_DURATION)
        self.hand_was_lost = False

    def update_move_gesture_gate(self, label):
        if label is None:
            self.move_gesture_label = None
            self.move_gesture_frames = 0
            self.reset_mouse_anchor()
            return False

        if label == self.move_gesture_label:
            self.move_gesture_frames += 1
        else:
            self.move_gesture_label = label
            self.move_gesture_frames = 1
            self.reset_mouse_anchor(clear_move_gate=False)

        if self.move_gesture_frames < MOVE_GESTURE_CONFIRM_FRAMES:
            self.reset_mouse_anchor(clear_move_gate=False)
            return False

        return True

    def update_raw_click_candidate(self, raw_label):
        if raw_label in CLICK_GESTURES:
            if raw_label == self.raw_click_candidate:
                self.raw_click_count += 1
            else:
                self.raw_click_candidate = raw_label
                self.raw_click_count = 1
        else:
            self.raw_click_candidate = None
            self.raw_click_count = 0

    def consume_fast_click(self, button, now):
        self.mouse.click(button=button, clicks=1)
        self.last_click_time = now
        self.move_freeze_until = max(self.move_freeze_until, now + CLICK_FREEZE_DURATION)
        self.prediction_buffer.clear()
        self.current_stable_label = "none"
        self.raw_click_candidate = None
        self.raw_click_count = 0

    def stop_drag(self, now):
        self.mouse.mouse_up()
        self.dragging = False
        self.drag_release_until = now + DRAG_RELEASE_FREEZE_DURATION
        self.reset_mouse_anchor()
        self.update_move_gesture_gate(None)
        self.prediction_buffer.clear()
        self.current_stable_label = "none"
        self.move_freeze_until = max(self.move_freeze_until, now + DRAG_RELEASE_FREEZE_DURATION)

    def move_mouse(self, point, now=None):
        if not self.mouse_enabled:
            return

        current_time = time.time() if now is None else now
        if current_time < self.move_freeze_until:
            self.reset_mouse_anchor()
            return

        if (
            point.x < HAND_EDGE_GUARD
            or point.x > 1 - HAND_EDGE_GUARD
            or point.y < HAND_EDGE_GUARD
            or point.y > 1 - HAND_EDGE_GUARD
        ):
            self.reset_mouse_anchor()
            return

        usable_x = min(max(point.x, MOVE_MARGIN), 1 - MOVE_MARGIN)
        usable_y = min(max(point.y, MOVE_MARGIN), 1 - MOVE_MARGIN)

        normalized_x = (usable_x - MOVE_MARGIN) / (1 - 2 * MOVE_MARGIN)
        normalized_y = (usable_y - MOVE_MARGIN) / (1 - 2 * MOVE_MARGIN)

        if self.filtered_hand_x is None:
            self.filtered_hand_x = normalized_x
            self.filtered_hand_y = normalized_y
        else:
            self.filtered_hand_x = self.filtered_hand_x + (normalized_x - self.filtered_hand_x) * HAND_POINT_SMOOTHING
            self.filtered_hand_y = self.filtered_hand_y + (normalized_y - self.filtered_hand_y) * HAND_POINT_SMOOTHING

        normalized_x = self.filtered_hand_x
        normalized_y = self.filtered_hand_y

        if self.hand_anchor_x is None:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames = self.move_resume_frames + 1 if self.move_resume_frames < 0 else 1
            return

        if self.move_resume_frames < MOVE_RESUME_FRAMES:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames += 1
            if self.move_resume_frames < 0:
                self.filtered_hand_x = normalized_x
                self.filtered_hand_y = normalized_y
            return

        hand_delta_x = normalized_x - self.hand_anchor_x
        hand_delta_y = normalized_y - self.hand_anchor_y
        hand_delta_length = float(np.hypot(hand_delta_x, hand_delta_y))
        if hand_delta_length > HAND_JUMP_GUARD:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames = 1
            return

        small_hand_move = abs(hand_delta_x) < HAND_DEAD_ZONE and abs(hand_delta_y) < HAND_DEAD_ZONE
        if small_hand_move:
            self.hand_anchor_x = normalized_x
            self.hand_anchor_y = normalized_y
            return
        else:
            if abs(hand_delta_x) < HAND_DEAD_ZONE:
                hand_delta_x = 0.0
            if abs(hand_delta_y) < HAND_DEAD_ZONE:
                hand_delta_y = 0.0

            delta_x = hand_delta_x * self.screen_w * MOVE_SENSITIVITY
            delta_y = hand_delta_y * self.screen_h * MOVE_SENSITIVITY
            move_length = float(np.hypot(delta_x, delta_y))
            if move_length > MAX_MOVE_STEP:
                step_scale = MAX_MOVE_STEP / move_length
                delta_x *= step_scale
                delta_y *= step_scale
                move_length = MAX_MOVE_STEP

        base_x, base_y = (
            self.mouse.position()
            if self.prev_mouse_x is None or self.prev_mouse_y is None
            else (self.prev_mouse_x, self.prev_mouse_y)
        )
        target_x = min(max(base_x + delta_x, 0), self.screen_w - 1)
        target_y = min(max(base_y + delta_y, 0), self.screen_h - 1)

        if self.prev_mouse_x is None:
            smooth_x, smooth_y = target_x, target_y
        else:
            smoothing = FAST_MOVE_SMOOTHING if move_length > 45 else MOVE_SMOOTHING
            smooth_x = self.prev_mouse_x + (target_x - self.prev_mouse_x) * smoothing
            smooth_y = self.prev_mouse_y + (target_y - self.prev_mouse_y) * smoothing

        output_x = int(round(smooth_x))
        output_y = int(round(smooth_y))

        self.prev_mouse_x = smooth_x
        self.prev_mouse_y = smooth_y
        self.hand_anchor_x = normalized_x
        self.hand_anchor_y = normalized_y
        self.move_resume_frames = MOVE_RESUME_FRAMES

        if self.sent_mouse_x is not None and self.sent_mouse_y is not None:
            if abs(output_x - self.sent_mouse_x) < MOVE_DEAD_ZONE and abs(output_y - self.sent_mouse_y) < MOVE_DEAD_ZONE:
                return

        if output_x == self.sent_mouse_x and output_y == self.sent_mouse_y:
            return

        self.sent_mouse_x = output_x
        self.sent_mouse_y = output_y
        self.mouse.move_to(output_x, output_y)

    def navigate_large_task(self, direction, now):
        if THREE_FINGER_NAV_MODE == "apps":
            task_direction = "previous" if direction == "left" else "next"
            self.mouse.switch_task(task_direction)
        elif THREE_FINGER_NAV_MODE == "tabs_then_apps":
            if self.last_tab_app_direction != direction:
                self.tab_switch_count = 0
                self.last_tab_app_direction = direction

            if self.tab_switch_count < TAB_SWITCHES_BEFORE_APP_SWITCH:
                self.mouse.switch_tab(direction)
                self.tab_switch_count += 1
            else:
                task_direction = "previous" if direction == "left" else "next"
                self.mouse.switch_task(task_direction)
                self.tab_switch_count = 0
        else:
            self.mouse.switch_tab(direction)
        self.last_action_time = now

    def gesture_change_needs_pointer_lock(self, stable_label, raw_label):
        previous_labels = {self.last_stable_label, self.last_raw_label}
        current_labels = {stable_label, raw_label}

        if current_labels & NON_MOVING_GESTURES:
            return True
        if current_labels & CLICK_GESTURES:
            return True
        if "fist" in previous_labels or "fist" in current_labels:
            return True

        previous_move = previous_labels & MOVE_GESTURES
        current_move = current_labels & MOVE_GESTURES
        if previous_move and current_move and previous_move != current_move:
            return True

        return False

    def apply_mouse_actions(self, stable_label, raw_label, hand_landmarks):
        now = time.time()
        landmarks = hand_landmarks.landmark
        stable_changed = stable_label != self.last_stable_label
        raw_changed = raw_label != self.last_raw_label
        self.update_raw_click_candidate(raw_label)

        if not self.dragging and (stable_changed or raw_changed):
            if self.gesture_change_needs_pointer_lock(stable_label, raw_label):
                self.update_move_gesture_gate(None)
                self.move_freeze_until = max(self.move_freeze_until, now + GESTURE_SWITCH_FREEZE_DURATION)
                self.last_stable_label = stable_label
                self.last_raw_label = raw_label
                return
            self.update_move_gesture_gate(None)

        if not self.dragging and stable_changed:
            self.reset_mouse_anchor()
            if self.last_stable_label in MOVE_GESTURES or stable_label in NON_MOVING_GESTURES:
                self.move_freeze_until = max(self.move_freeze_until, now + GESTURE_SWITCH_FREEZE_DURATION)

        if not self.dragging and raw_label in NON_MOVING_GESTURES:
            self.reset_mouse_anchor()
            self.move_freeze_until = max(self.move_freeze_until, now + GESTURE_SWITCH_FREEZE_DURATION)

        if not self.dragging and (raw_label in CLICK_GESTURES or stable_label in CLICK_GESTURES):
            self.reset_mouse_anchor()
            self.move_freeze_until = max(self.move_freeze_until, now + CLICK_FREEZE_DURATION)

        if raw_label == "fist" and stable_label != "fist" and not self.dragging:
            self.reset_mouse_anchor()
            self.move_freeze_until = max(self.move_freeze_until, now + DRAG_PREP_FREEZE_DURATION)

        if not self.mouse_enabled:
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        if stable_label == "fist" and raw_label == "fist" and not self.dragging:
            self.reset_mouse_anchor()
            self.mouse.mouse_down()
            self.dragging = True

        elif self.dragging and (raw_label != "fist" or stable_label != "fist"):
            self.stop_drag(now)
            stable_label = "none"
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        if stable_label == "none" and not self.dragging:
            self.reset_mouse_anchor()
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        if not self.dragging and now < self.drag_release_until:
            self.reset_mouse_anchor()
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        if stable_label in NON_MOVING_GESTURES:
            self.reset_mouse_anchor()

        movement_label = stable_label
        if stable_label == "none" and self.dragging and raw_label in MOVE_GESTURES:
            movement_label = raw_label
        elif stable_label == "none" and self.dragging:
            self.reset_mouse_anchor()
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        desired_move_label = None
        if now >= self.move_freeze_until:
            if self.dragging and raw_label == "fist" and stable_label == "fist":
                desired_move_label = "fist"
            elif not self.dragging and movement_label in MOVE_GESTURES and movement_label == raw_label:
                desired_move_label = movement_label

        can_move_pointer = self.update_move_gesture_gate(desired_move_label)

        if can_move_pointer:
            control_point = self.palm_control_point(landmarks)
            self.move_mouse(control_point, now=now)

        if (
            raw_label == "one_finger"
            and self.raw_click_count >= FAST_CLICK_CONFIRM_FRAMES
            and not self.dragging
            and now - self.last_click_time > CLICK_COOLDOWN
        ):
            self.consume_fast_click("left", now)

        elif (
            raw_label == "two_fingers"
            and self.raw_click_count >= FAST_CLICK_CONFIRM_FRAMES
            and not self.dragging
            and now - self.last_click_time > CLICK_COOLDOWN
        ):
            self.consume_fast_click("right", now)

        if stable_label == "three_left" and not self.dragging and now - self.last_action_time > TAB_SWITCH_COOLDOWN:
            self.navigate_large_task("left", now)
        elif stable_label == "three_right" and not self.dragging and now - self.last_action_time > TAB_SWITCH_COOLDOWN:
            self.navigate_large_task("right", now)
        elif stable_label == "three_up" and not self.dragging and now - self.last_scroll_time > SCROLL_COOLDOWN:
            self.mouse.scroll(80)
            self.last_scroll_time = now
        elif stable_label == "three_down" and not self.dragging and now - self.last_scroll_time > SCROLL_COOLDOWN:
            self.mouse.scroll(-80)
            self.last_scroll_time = now

        self.last_stable_label = stable_label
        self.last_raw_label = raw_label

    def predict_frame(self, frame):
        results = self.hand_tracker.process(frame)
        if not results.multi_hand_landmarks:
            self.handle_hand_lost()
            return None, None

        hand_landmarks = results.multi_hand_landmarks[0]
        height, width = frame.shape[:2]
        box = self.feature_extractor.get_bounding_box(
            hand_landmarks.landmark,
            width,
            height,
        )
        if box is None:
            self.handle_hand_lost()
            return None, hand_landmarks

        x_min, y_min, x_max, y_max = box
        crop = frame[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            self.handle_hand_lost()
            return None, hand_landmarks

        if self.hand_was_lost:
            self.prepare_hand_reacquire()

        processed_preview = self.feature_extractor.preprocess_crop(crop)
        features = self.feature_extractor.extract_prediction_features(
            hand_landmarks,
            processed_preview,
            self.classifier.expected_feature_count,
        )
        model_label = self.classifier.predict(features)
        pred_label, label_source = self.corrected_label(model_label, hand_landmarks)
        self.prediction_buffer.append(pred_label)
        stable_label = self.get_stable_label()

        self.apply_mouse_actions(stable_label, pred_label, hand_landmarks)

        return {
            "label": pred_label,
            "model_label": model_label,
            "label_source": label_source,
            "stable_label": stable_label,
            "box": (x_min, y_min, x_max, y_max),
            "preview": processed_preview,
        }, hand_landmarks

    def draw_ui(self, frame, prediction, hand_landmarks):
        if hand_landmarks is not None:
            self.hand_tracker.draw_landmarks(frame, hand_landmarks)

        if prediction is None:
            cv2.putText(frame, "Gesture: khong nhan duoc", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            x_min, y_min, x_max, y_max = prediction["box"]
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(frame, f"Predict: {prediction['label']} ({prediction['label_source']})", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            cv2.putText(frame, f"Stable: {prediction['stable_label']}", (10, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 255), 2)
            cv2.putText(frame, f"Model: {prediction['model_label']}", (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 255, 180), 2)

            preview = cv2.resize(prediction["preview"], (160, 160), interpolation=cv2.INTER_AREA)
            frame[10:170, frame.shape[1] - 170:frame.shape[1] - 10] = preview
            cv2.rectangle(frame, (frame.shape[1] - 170, 10), (frame.shape[1] - 10, 170), (255, 255, 255), 2)

        drag_text = "DRAGGING" if self.dragging else "RELEASED"
        cv2.putText(frame, f"Drag: {drag_text}", (10, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        mouse_text = f"Mouse: ON ({self.mouse.backend})" if self.mouse_enabled else "Mouse: OFF"
        cv2.putText(frame, mouse_text, (10, 147), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2)
        lock_text = "Move: LOCKED" if time.time() < self.move_freeze_until else "Move: FREE"
        cv2.putText(frame, lock_text, (10, 172), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)
        cv2.putText(frame, "Open=Move | 1=Left | 2=Right | Fist=Hold drag", (10, 197), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
        if THREE_FINGER_NAV_MODE == "tabs_then_apps":
            nav_text = "3_left/right=tabs then apps"
        elif THREE_FINGER_NAV_MODE == "tabs":
            nav_text = "3_left/right=browser tabs"
        else:
            nav_text = "3_left/right=apps"
        cv2.putText(frame, f"{nav_text} | 3_up/down scroll", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "Nhan Q hoac ESC de thoat", (10, 244), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def run(self):
        if not self.camera.is_opened():
            raise RuntimeError("Khong mo duoc webcam.")

        while True:
            success, frame = self.camera.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            prediction, hand_landmarks = self.predict_frame(frame)
            self.draw_ui(frame, prediction, hand_landmarks)
            cv2.imshow("Hand Gesture Mouse Demo", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

        if self.dragging and self.mouse_enabled:
            self.mouse.mouse_up()

        self.camera.release()
        self.hand_tracker.close()
        cv2.destroyAllWindows()


def main():
    print("Demo nhan dien cu chi va dieu khien chuot")
    print("Can model da train trong thu muc trained_model")
    if not PYAUTOGUI_AVAILABLE:
        print("Khong tim thay pyautogui. Demo se thu dung Windows API de dieu khien chuot.")
    print("Nhan Q hoac ESC de thoat")

    demo = HandGestureDemo()
    demo.run()


if __name__ == "__main__":
    main()
