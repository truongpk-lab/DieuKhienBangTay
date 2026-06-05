"""Optional emergency hotkey controller."""

from __future__ import annotations

from typing import Callable


class HotkeyController:
    def __init__(
        self,
        hotkey: str = "ctrl+alt+g",
        on_stop: Callable[[], object] | None = None,
        on_show: Callable[[], object] | None = None,
    ):
        self.hotkey = hotkey
        self.on_stop = on_stop
        self.on_show = on_show
        self.active = False
        self.last_error: str | None = None
        self._keyboard = None
        self._handler = None

    def start(self) -> dict[str, object]:
        try:
            import keyboard  # type: ignore[import-not-found]
        except ModuleNotFoundError:
            self.last_error = "Chua cai optional package keyboard; hotkey se duoc lam day du o Phase 32."
            return self.status()

        self._keyboard = keyboard
        self._handler = keyboard.add_hotkey(self.hotkey, self.trigger)
        self.active = True
        self.last_error = None
        return self.status()

    def stop(self) -> dict[str, object]:
        if self._keyboard is not None and self._handler is not None:
            self._keyboard.remove_hotkey(self._handler)
            self._handler = None
        self.active = False
        return self.status()

    def trigger(self) -> None:
        if self.on_stop is not None:
            self.on_stop()
        if self.on_show is not None:
            self.on_show()

    def status(self) -> dict[str, object]:
        return {
            "active": self.active,
            "hotkey": self.hotkey,
            "supported": self.active,
            "message": "Emergency hotkey active." if self.active else "Emergency hotkey chua active.",
            "lastError": self.last_error,
        }
