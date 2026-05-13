from math import atan2, cos, sin

import numpy as np


EXPECTED_LANDMARK_COUNT = 21


def landmark_value(point, key):
    if isinstance(point, dict):
        return float(point.get(key, 0.0))
    return float(getattr(point, key, 0.0))


def mirror_landmarks(landmarks):
    mirrored = []
    for point in landmarks:
        x = 1.0 - landmark_value(point, "x")
        y = landmark_value(point, "y")
        z = landmark_value(point, "z")

        if isinstance(point, dict):
            mirrored_point = dict(point)
            mirrored_point["x"] = x
            mirrored_point["y"] = y
            mirrored_point["z"] = z
        else:
            mirrored_point = {"x": x, "y": y, "z": z}

        mirrored.append(mirrored_point)
    return mirrored


def transform_landmarks(landmarks, scale=1.0, rotation_degrees=0.0, jitter_std=0.0, seed=None):
    points = landmarks_to_array(landmarks)
    rng = np.random.default_rng(seed)
    center = points[0, :2].copy()

    angle = np.deg2rad(rotation_degrees)
    rotation = np.array(
        [
            [cos(angle), -sin(angle)],
            [sin(angle), cos(angle)],
        ],
        dtype=np.float32,
    )

    transformed = points.copy()
    xy = (points[:, :2] - center) * scale
    transformed[:, :2] = xy @ rotation.T + center

    if jitter_std > 0:
        transformed[:, :2] += rng.normal(0.0, jitter_std, size=(EXPECTED_LANDMARK_COUNT, 2)).astype(np.float32)
        transformed[:, 2] += rng.normal(0.0, jitter_std * 0.5, size=EXPECTED_LANDMARK_COUNT).astype(np.float32)

    transformed[:, 0] = np.clip(transformed[:, 0], 0.0, 1.0)
    transformed[:, 1] = np.clip(transformed[:, 1], 0.0, 1.0)

    augmented = []
    for original, values in zip(landmarks, transformed):
        if isinstance(original, dict):
            point = dict(original)
            point["x"] = float(values[0])
            point["y"] = float(values[1])
            point["z"] = float(values[2])
        else:
            point = {
                "x": float(values[0]),
                "y": float(values[1]),
                "z": float(values[2]),
            }
        augmented.append(point)

    return augmented


def landmarks_to_array(landmarks):
    points = list(landmarks)
    if len(points) != EXPECTED_LANDMARK_COUNT:
        raise ValueError(f"Can {EXPECTED_LANDMARK_COUNT} landmarks, nhan duoc {len(points)}")

    values = []
    for point in points:
        values.append(
            [
                landmark_value(point, "x"),
                landmark_value(point, "y"),
                landmark_value(point, "z"),
            ]
        )
    return np.array(values, dtype=np.float32)


def normalize_landmarks(landmarks):
    points = landmarks_to_array(landmarks)
    wrist = points[0].copy()
    centered = points - wrist

    palm_size = np.linalg.norm(points[9, :2] - points[0, :2])
    if palm_size < 1e-6:
        palm_size = np.linalg.norm(points[:, :2].max(axis=0) - points[:, :2].min(axis=0))
    if palm_size < 1e-6:
        palm_size = 1.0

    normalized = centered / palm_size
    return points, normalized.astype(np.float32), float(palm_size)


def finger_distance_features(points, palm_size):
    pairs = [
        (4, 8),
        (4, 12),
        (4, 16),
        (4, 20),
        (8, 12),
        (12, 16),
        (16, 20),
        (8, 0),
        (12, 0),
        (16, 0),
        (20, 0),
    ]
    distances = []
    for first, second in pairs:
        distance = np.linalg.norm(points[first] - points[second]) / palm_size
        distances.append(distance)
    return np.array(distances, dtype=np.float32)


def finger_angle_features(points):
    chains = [
        (0, 1, 2, 3, 4),
        (0, 5, 6, 7, 8),
        (0, 9, 10, 11, 12),
        (0, 13, 14, 15, 16),
        (0, 17, 18, 19, 20),
    ]
    angles = []
    for chain in chains:
        base = points[chain[1], :2] - points[chain[0], :2]
        tip = points[chain[-1], :2] - points[chain[1], :2]
        angles.append(atan2(tip[1], tip[0]) - atan2(base[1], base[0]))
    return np.array(angles, dtype=np.float32)


def extract_landmark_features(landmarks):
    points, normalized, palm_size = normalize_landmarks(landmarks)
    flat_xyz = normalized.flatten()
    flat_xy = normalized[:, :2].flatten()
    distances = finger_distance_features(points, palm_size)
    angles = finger_angle_features(points)
    return np.concatenate([flat_xyz, flat_xy, distances, angles]).astype(np.float32)
