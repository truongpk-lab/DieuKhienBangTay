"""Core services for ACV Gesture Control.

Imports are loaded lazily so lightweight modules can be used without camera
runtime dependencies such as cv2.
"""

__all__ = [
    "CameraService",
    "FeatureExtractor",
    "GestureClassifier",
    "GestureStateEvent",
    "HandTracker",
    "PinchDragDropStateMachine",
    "TemporalFilter",
]


def __getattr__(name):
    if name == "CameraService":
        from .camera_service import CameraService

        return CameraService
    if name == "FeatureExtractor":
        from .feature_extractor import FeatureExtractor

        return FeatureExtractor
    if name == "GestureClassifier":
        from .gesture_classifier import GestureClassifier

        return GestureClassifier
    if name == "GestureStateEvent":
        from .gesture_state_machine import GestureStateEvent

        return GestureStateEvent
    if name == "HandTracker":
        from .hand_tracker import HandTracker

        return HandTracker
    if name == "PinchDragDropStateMachine":
        from .gesture_state_machine import PinchDragDropStateMachine

        return PinchDragDropStateMachine
    if name == "TemporalFilter":
        from .temporal_filter import TemporalFilter

        return TemporalFilter
    raise AttributeError(f"module 'core' has no attribute {name!r}")
