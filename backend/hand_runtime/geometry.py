from types import SimpleNamespace

import numpy as np

from .feature_utils import landmarks_to_array

from . import config


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
PALM_CONTROL_IDS = (0, 5, 9, 13, 17)


def finger_states(landmarks):
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
    states["thumb"] = (
        np.linalg.norm(thumb_tip - index_mcp)
        > np.linalg.norm(thumb_pip - index_mcp) + 0.08 * palm_size
    )
    return states, points, palm_size


def direction_from_extended_fingers(states, points):
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


def central_three_direction(points, palm_size):
    central_fingers = ("index", "middle", "ring")
    tip_vectors = []
    extended_like_count = 0

    for finger in central_fingers:
        tip = points[FINGER_TIP_IDS[finger], :2]
        pip = points[FINGER_PIP_IDS[finger], :2]
        mcp = points[FINGER_MCP_IDS[finger], :2]
        tip_vectors.append(tip - mcp)

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


def geometry_label(landmarks):
    states, points, palm_size = finger_states(landmarks)
    non_thumb = ["index", "middle", "ring", "pinky"]
    extended_non_thumb = [finger for finger in non_thumb if states.get(finger)]
    extended_count = len(extended_non_thumb)
    central_direction, central_confidence = central_three_direction(points, palm_size)

    if extended_count >= 4:
        return "open_hand", 0.95

    if extended_count == 0:
        return "fist", 0.95

    if extended_count == 1 and states.get("index"):
        return "one_finger", 0.9

    if extended_count == 2 and states.get("index") and states.get("middle"):
        return "two_fingers", 0.9

    if extended_count == 3:
        direction = direction_from_extended_fingers(states, points)
        if direction is not None:
            return direction, 0.88

    if central_direction is not None and extended_count >= 2:
        return central_direction, central_confidence

    return None, 0.0


def corrected_label(model_label, landmarks):
    detected_label, confidence = geometry_label(landmarks)
    if detected_label is None:
        return model_label, "model"

    if model_label == "three_down" and detected_label == "open_hand":
        _, points, palm_size = finger_states(landmarks)
        central_direction, central_confidence = central_three_direction(points, palm_size)
        if central_direction == "three_down" and central_confidence >= 0.78:
            return "three_down", "model+geometry"

    if confidence >= 0.94:
        return detected_label, "geometry"

    if model_label in config.MODEL_ONLY_GESTURES and detected_label in {
        "open_hand",
        "fist",
        "one_finger",
        "two_fingers",
    }:
        return detected_label, "geometry"

    if model_label in {"open_hand", "fist", "one_finger", "two_fingers"} and detected_label in config.MODEL_ONLY_GESTURES:
        return model_label, "model"

    return detected_label, "geometry"


def pinch_ratio(landmarks):
    points = landmarks_to_array(landmarks)
    palm_size = np.linalg.norm(points[9, :2] - points[0, :2])
    if palm_size < 1e-6:
        palm_size = 1.0
    distance = np.linalg.norm(points[FINGER_TIP_IDS["thumb"], :2] - points[FINGER_TIP_IDS["index"], :2])
    return float(distance / palm_size)


def pinch_active(landmarks, was_active=False):
    ratio = pinch_ratio(landmarks)
    threshold = config.PINCH_OFF_RATIO if was_active else config.PINCH_ON_RATIO
    return ratio <= threshold, ratio


def palm_control_point(landmarks):
    return SimpleNamespace(
        x=float(np.mean([landmarks[idx].x for idx in PALM_CONTROL_IDS])),
        y=float(np.mean([landmarks[idx].y for idx in PALM_CONTROL_IDS])),
    )
