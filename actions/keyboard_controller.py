"""Keyboard controller for mapped keyboard/media/game actions."""

from __future__ import annotations


class KeyboardController:
    """Thin pyautogui wrapper with a safe fallback when unavailable."""

    def __init__(self, enabled: bool = True):
        self.enabled = False
        self.last_error: str | None = None
        self._pyautogui = None
        if enabled:
            self._connect()

    def hotkey(self, *keys: str):
        if not self._ready():
            return self._skipped(keys=list(keys))
        self._pyautogui.hotkey(*keys)
        return {"status": "sent", "type": "hotkey", "keys": list(keys)}

    def press(self, key: str):
        if not self._ready():
            return self._skipped(key=key)
        self._pyautogui.press(key)
        return {"status": "sent", "type": "press", "key": key}

    def release(self, key: str):
        if not self._ready():
            return self._skipped(key=key)
        self._pyautogui.keyUp(key)
        return {"status": "sent", "type": "release", "key": key}

    def _connect(self) -> None:
        try:
            import pyautogui  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - depends on OS/display
            self.last_error = f"pyautogui keyboard backend unavailable: {exc}"
            return
        self._pyautogui = pyautogui
        self.enabled = True
        self.last_error = None

    def _ready(self) -> bool:
        return self.enabled and self._pyautogui is not None

    def _skipped(self, **payload):
        return {
            "status": "skipped",
            "reason": self.last_error or "keyboard controller is not connected",
            **payload,
        }
