"""Mouse action service that routes all mouse actions through MouseControlAdapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from actions.mouse_control_adapter import MouseControlAdapter


class MouseService:
    def __init__(self, adapter: MouseControlAdapter | None = None):
        self.adapter = adapter or MouseControlAdapter()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.adapter.enabled),
            "screen": {"width": self.adapter.screen_w, "height": self.adapter.screen_h},
        }

    def execute(self, action: str, payload: Mapping[str, Any] | None = None):
        payload = payload or {}
        if action == "mouse.move":
            return self.adapter.move(payload["x"], payload["y"])
        if action == "mouse.left_click":
            return self.adapter.left_click(clicks=int(payload.get("clicks", 1)))
        if action == "mouse.right_click":
            return self.adapter.right_click(clicks=int(payload.get("clicks", 1)))
        if action == "mouse.scroll":
            return self.adapter.scroll(payload["amount"])
        if action == "mouse.down":
            return self.adapter.mouse_down()
        if action == "mouse.up":
            return self.adapter.mouse_up()
        if action == "mouse.drag_start":
            return self.adapter.drag_start()
        if action == "mouse.drag_move":
            return self.adapter.drag_move(payload["x"], payload["y"])
        if action == "mouse.drag_release":
            return self.adapter.drag_release()
        raise ValueError(f"unsupported mouse action: {action}")
