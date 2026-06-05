"""Compatibility package for the backend ACV hand gesture mouse runtime."""

from backend.hand_runtime.mouse import DryRunMouseController, MouseController, PYAUTOGUI_AVAILABLE

__all__ = [
    "DryRunMouseController",
    "HandMouseApp",
    "MouseController",
    "PYAUTOGUI_AVAILABLE",
]


def __getattr__(name):
    if name == "HandMouseApp":
        from backend.hand_runtime.app import HandMouseApp

        return HandMouseApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
