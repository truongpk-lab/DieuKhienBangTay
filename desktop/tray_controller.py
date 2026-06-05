"""Optional system tray controller for desktop mode."""

from __future__ import annotations

from typing import Callable


class TrayController:
    def __init__(
        self,
        on_show: Callable[[], object] | None = None,
        on_start: Callable[[], object] | None = None,
        on_stop: Callable[[], object] | None = None,
        on_exit: Callable[[], object] | None = None,
    ):
        self.on_show = on_show
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_exit = on_exit
        self.active = False
        self.last_error: str | None = None
        self._icon = None

    def start(self) -> dict[str, object]:
        if self.active:
            return self.status("Tray already active.")
        try:
            import pystray  # type: ignore[import-not-found]
            from PIL import Image, ImageDraw  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            self.last_error = f"Chua cai optional tray package: {exc.name}"
            return self.status("Tray fallback active only through API.", supported=False)

        image = Image.new("RGB", (64, 64), "#0A0A0C")
        draw = ImageDraw.Draw(image)
        draw.ellipse((12, 12, 52, 52), fill="#00f2ff")
        menu = pystray.Menu(
            pystray.MenuItem("Show App", lambda: self._call(self.on_show)),
            pystray.MenuItem("Start Tracking", lambda: self._call(self.on_start)),
            pystray.MenuItem("Stop Tracking", lambda: self._call(self.on_stop)),
            pystray.MenuItem("Exit", lambda: self._call(self.on_exit)),
        )
        self._icon = pystray.Icon("ACV Gesture Control", image, "ACV Gesture Control", menu)
        self._icon.run_detached()
        self.active = True
        self.last_error = None
        return self.status("Tray active.")

    def stop(self) -> dict[str, object]:
        if self._icon is not None:
            self._icon.stop()
            self._icon = None
        self.active = False
        return self.status("Tray controller stopped.")

    def status(self, message: str = "Tray status.", supported: bool | None = None) -> dict[str, object]:
        return {
            "active": self.active,
            "supported": self.active if supported is None else supported,
            "message": message,
            "lastError": self.last_error,
        }

    def _call(self, callback: Callable[[], object] | None) -> None:
        if callback is not None:
            callback()
