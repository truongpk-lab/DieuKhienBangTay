import time

import numpy as np

from . import config
from .geometry import palm_control_point, pinch_active


class GestureActionState:
    def __init__(self, mouse):
        self.mouse = mouse
        self.mouse_enabled = mouse.enabled
        self.screen_w, self.screen_h = mouse.screen_w, mouse.screen_h
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
        self.pinch_down = False
        self.last_pinch_ratio = None

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

    def reset_transient_input(self):
        self.raw_click_candidate = None
        self.raw_click_count = 0
        self.current_stable_label = "none"
        self.last_stable_label = "none"
        self.last_raw_label = "none"
        self.pinch_down = False

    def reanchor_mouse_to_current_position(self, normalized_x, normalized_y):
        current_x, current_y = self.mouse.position()
        self.hand_anchor_x = normalized_x
        self.hand_anchor_y = normalized_y
        self.prev_mouse_x = float(current_x)
        self.prev_mouse_y = float(current_y)
        self.sent_mouse_x = int(current_x)
        self.sent_mouse_y = int(current_y)

    def handle_hand_lost(self):
        self.reset_mouse_anchor()
        self.raw_click_candidate = None
        self.raw_click_count = 0
        if self.dragging and self.mouse_enabled:
            self.mouse.mouse_up()
            self.dragging = False
        self.pinch_down = False
        self.drag_release_until = 0.0
        self.last_stable_label = "none"
        self.last_raw_label = "none"

    def prepare_hand_reacquire(self, now=None):
        current_time = time.time() if now is None else now
        self.reset_mouse_anchor()
        self.reset_transient_input()
        self.move_resume_frames = -config.HAND_REACQUIRE_FRAMES
        self.move_freeze_until = max(
            self.move_freeze_until,
            current_time + config.HAND_REACQUIRE_FREEZE_DURATION,
        )

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

        if self.move_gesture_frames < config.MOVE_GESTURE_CONFIRM_FRAMES:
            self.reset_mouse_anchor(clear_move_gate=False)
            return False

        return True

    def update_raw_click_candidate(self, raw_label):
        if raw_label in config.CLICK_GESTURES:
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
        self.move_freeze_until = max(self.move_freeze_until, now + config.CLICK_FREEZE_DURATION)
        self.current_stable_label = "none"
        self.raw_click_candidate = None
        self.raw_click_count = 0

    def stop_drag(self, now):
        self.mouse.mouse_up()
        self.dragging = False
        self.pinch_down = False
        self.drag_release_until = now + config.DRAG_RELEASE_FREEZE_DURATION
        self.reset_mouse_anchor()
        self.update_move_gesture_gate(None)
        self.current_stable_label = "none"
        self.move_freeze_until = max(self.move_freeze_until, now + config.DRAG_RELEASE_FREEZE_DURATION)

    def move_mouse(self, point, now=None, allow_during_freeze=False):
        if not self.mouse_enabled:
            return

        current_time = time.time() if now is None else now
        if current_time < self.move_freeze_until and not allow_during_freeze:
            self.reset_mouse_anchor()
            return

        if (
            point.x < config.HAND_EDGE_GUARD
            or point.x > 1 - config.HAND_EDGE_GUARD
            or point.y < config.HAND_EDGE_GUARD
            or point.y > 1 - config.HAND_EDGE_GUARD
        ):
            self.reset_mouse_anchor()
            return

        usable_x = min(max(point.x, config.MOVE_MARGIN), 1 - config.MOVE_MARGIN)
        usable_y = min(max(point.y, config.MOVE_MARGIN), 1 - config.MOVE_MARGIN)
        normalized_x = (usable_x - config.MOVE_MARGIN) / (1 - 2 * config.MOVE_MARGIN)
        normalized_y = (usable_y - config.MOVE_MARGIN) / (1 - 2 * config.MOVE_MARGIN)

        if self.filtered_hand_x is None:
            self.filtered_hand_x = normalized_x
            self.filtered_hand_y = normalized_y
        else:
            self.filtered_hand_x += (normalized_x - self.filtered_hand_x) * config.HAND_POINT_SMOOTHING
            self.filtered_hand_y += (normalized_y - self.filtered_hand_y) * config.HAND_POINT_SMOOTHING

        normalized_x = self.filtered_hand_x
        normalized_y = self.filtered_hand_y

        if self.hand_anchor_x is None:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames = self.move_resume_frames + 1 if self.move_resume_frames < 0 else 1
            return

        if self.move_resume_frames < config.MOVE_RESUME_FRAMES:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames += 1
            if self.move_resume_frames < 0:
                self.filtered_hand_x = normalized_x
                self.filtered_hand_y = normalized_y
            return

        hand_delta_x = normalized_x - self.hand_anchor_x
        hand_delta_y = normalized_y - self.hand_anchor_y
        hand_delta_length = float(np.hypot(hand_delta_x, hand_delta_y))
        if hand_delta_length > config.HAND_JUMP_GUARD:
            self.reanchor_mouse_to_current_position(normalized_x, normalized_y)
            self.move_resume_frames = 1
            return

        small_hand_move = (
            abs(hand_delta_x) < config.HAND_DEAD_ZONE
            and abs(hand_delta_y) < config.HAND_DEAD_ZONE
        )
        if small_hand_move:
            self.hand_anchor_x = normalized_x
            self.hand_anchor_y = normalized_y
            return

        if abs(hand_delta_x) < config.HAND_DEAD_ZONE:
            hand_delta_x = 0.0
        if abs(hand_delta_y) < config.HAND_DEAD_ZONE:
            hand_delta_y = 0.0

        delta_x = hand_delta_x * self.screen_w * config.MOVE_SENSITIVITY
        delta_y = hand_delta_y * self.screen_h * config.MOVE_SENSITIVITY
        move_length = float(np.hypot(delta_x, delta_y))
        if move_length > config.MAX_MOVE_STEP:
            step_scale = config.MAX_MOVE_STEP / move_length
            delta_x *= step_scale
            delta_y *= step_scale
            move_length = config.MAX_MOVE_STEP

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
            smoothing = config.FAST_MOVE_SMOOTHING if move_length > 45 else config.MOVE_SMOOTHING
            smooth_x = self.prev_mouse_x + (target_x - self.prev_mouse_x) * smoothing
            smooth_y = self.prev_mouse_y + (target_y - self.prev_mouse_y) * smoothing

        output_x = int(round(smooth_x))
        output_y = int(round(smooth_y))
        self.prev_mouse_x = smooth_x
        self.prev_mouse_y = smooth_y
        self.hand_anchor_x = normalized_x
        self.hand_anchor_y = normalized_y
        self.move_resume_frames = config.MOVE_RESUME_FRAMES

        if self.sent_mouse_x is not None and self.sent_mouse_y is not None:
            if (
                abs(output_x - self.sent_mouse_x) < config.MOVE_DEAD_ZONE
                and abs(output_y - self.sent_mouse_y) < config.MOVE_DEAD_ZONE
            ):
                return

        if output_x == self.sent_mouse_x and output_y == self.sent_mouse_y:
            return

        self.sent_mouse_x = output_x
        self.sent_mouse_y = output_y
        self.mouse.move_to(output_x, output_y)

    def navigate_large_task(self, direction, now):
        if config.NAV_MODE == "apps":
            task_direction = "previous" if direction == "left" else "next"
            self.mouse.switch_task(task_direction)
        elif config.NAV_MODE == "tabs_then_apps":
            if self.last_tab_app_direction != direction:
                self.tab_switch_count = 0
                self.last_tab_app_direction = direction

            if self.tab_switch_count < config.TAB_SWITCHES_BEFORE_APP_SWITCH:
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

        if current_labels & config.NON_MOVING_GESTURES:
            return True
        if current_labels & config.CLICK_GESTURES:
            return True
        if "fist" in previous_labels or "fist" in current_labels:
            return True

        previous_move = previous_labels & config.MOVE_GESTURES
        current_move = current_labels & config.MOVE_GESTURES
        if previous_move and current_move and previous_move != current_move:
            return True

        return False

    def apply(self, stable_label, raw_label, landmarks, now=None):
        now = time.time() if now is None else now
        self.current_stable_label = stable_label
        stable_changed = stable_label != self.last_stable_label
        raw_changed = raw_label != self.last_raw_label
        self.update_raw_click_candidate(raw_label)

        is_pinch, ratio = pinch_active(landmarks, self.pinch_down)
        self.last_pinch_ratio = ratio

        if self.mouse_enabled and is_pinch:
            if not self.dragging:
                self.reset_mouse_anchor()
                self.mouse.mouse_down()
                self.dragging = True
                self.pinch_down = True
            can_move_pointer = self.update_move_gesture_gate("pinch")
            if can_move_pointer:
                self.move_mouse(palm_control_point(landmarks), now=now, allow_during_freeze=True)
            self.last_stable_label = stable_label
            self.last_raw_label = raw_label
            return

        if self.dragging and self.pinch_down and not is_pinch:
            self.stop_drag(now)
            self.last_stable_label = "none"
            self.last_raw_label = raw_label
            return

        if not self.dragging and (stable_changed or raw_changed):
            if self.gesture_change_needs_pointer_lock(stable_label, raw_label):
                self.update_move_gesture_gate(None)
                self.move_freeze_until = max(
                    self.move_freeze_until,
                    now + config.GESTURE_SWITCH_FREEZE_DURATION,
                )
                self.last_stable_label = stable_label
                self.last_raw_label = raw_label
                return
            self.update_move_gesture_gate(None)

        if not self.dragging and stable_changed:
            self.reset_mouse_anchor()
            if self.last_stable_label in config.MOVE_GESTURES or stable_label in config.NON_MOVING_GESTURES:
                self.move_freeze_until = max(
                    self.move_freeze_until,
                    now + config.GESTURE_SWITCH_FREEZE_DURATION,
                )

        if not self.dragging and raw_label in config.NON_MOVING_GESTURES:
            self.reset_mouse_anchor()
            self.move_freeze_until = max(
                self.move_freeze_until,
                now + config.GESTURE_SWITCH_FREEZE_DURATION,
            )

        if not self.dragging and (raw_label in config.CLICK_GESTURES or stable_label in config.CLICK_GESTURES):
            self.reset_mouse_anchor()
            self.move_freeze_until = max(self.move_freeze_until, now + config.CLICK_FREEZE_DURATION)

        if raw_label == "fist" and stable_label != "fist" and not self.dragging:
            self.reset_mouse_anchor()
            self.move_freeze_until = max(self.move_freeze_until, now + config.DRAG_PREP_FREEZE_DURATION)

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
            self.last_stable_label = "none"
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

        if stable_label in config.NON_MOVING_GESTURES:
            self.reset_mouse_anchor()

        movement_label = stable_label
        if stable_label == "none" and self.dragging and raw_label in config.MOVE_GESTURES:
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
            elif not self.dragging and movement_label in config.MOVE_GESTURES and movement_label == raw_label:
                desired_move_label = movement_label

        can_move_pointer = self.update_move_gesture_gate(desired_move_label)
        if can_move_pointer:
            self.move_mouse(palm_control_point(landmarks), now=now)

        if (
            raw_label == "one_finger"
            and self.raw_click_count >= config.FAST_CLICK_CONFIRM_FRAMES
            and not self.dragging
            and now - self.last_click_time > config.CLICK_COOLDOWN
        ):
            self.consume_fast_click("left", now)

        elif (
            raw_label == "two_fingers"
            and self.raw_click_count >= config.FAST_CLICK_CONFIRM_FRAMES
            and not self.dragging
            and now - self.last_click_time > config.CLICK_COOLDOWN
        ):
            self.consume_fast_click("right", now)

        if (
            stable_label == "three_left"
            and not self.dragging
            and now - self.last_action_time > config.TAB_SWITCH_COOLDOWN
        ):
            self.navigate_large_task("left", now)
        elif (
            stable_label == "three_right"
            and not self.dragging
            and now - self.last_action_time > config.TAB_SWITCH_COOLDOWN
        ):
            self.navigate_large_task("right", now)
        elif (
            stable_label == "three_up"
            and not self.dragging
            and now - self.last_scroll_time > config.SCROLL_COOLDOWN
        ):
            self.mouse.scroll(80)
            self.last_scroll_time = now
        elif (
            stable_label == "three_down"
            and not self.dragging
            and now - self.last_scroll_time > config.SCROLL_COOLDOWN
        ):
            self.mouse.scroll(-80)
            self.last_scroll_time = now

        self.last_stable_label = stable_label
        self.last_raw_label = raw_label
