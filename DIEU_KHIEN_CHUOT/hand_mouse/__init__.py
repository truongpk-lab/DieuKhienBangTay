"""Backward-compatible imports for the backend hand runtime package."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.hand_runtime.mouse import DryRunMouseController, MouseController, PYAUTOGUI_AVAILABLE  # noqa: E402,F401

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
