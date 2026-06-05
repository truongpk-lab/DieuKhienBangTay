"""Window controller adapters for desktop shells."""

from __future__ import annotations

from typing import Any


class PyWebviewWindowController:
    def __init__(self, window):
        self.window = window
        self.visible = True

    def status(self) -> dict[str, Any]:
        return self._response("status", True, "Desktop window controller ready.")

    def minimize(self) -> dict[str, Any]:
        return self._call("minimize", visible=True, missing_ok=False)

    def hide(self) -> dict[str, Any]:
        result = self._call("hide", visible=False, missing_ok=False)
        if result["success"]:
            self.visible = False
        return result

    def show(self) -> dict[str, Any]:
        for method_name in ("show", "restore"):
            if hasattr(self.window, method_name):
                result = self._call(method_name, visible=True, missing_ok=False, action="show")
                if result["success"]:
                    self.visible = True
                return result
        return self._response("show", False, "Desktop shell khong ho tro show/restore.", visible=self.visible)

    def toggle(self) -> dict[str, Any]:
        if self.visible:
            return self.hide()
        return self.show()

    def _call(
        self,
        method_name: str,
        visible: bool,
        missing_ok: bool,
        action: str | None = None,
    ) -> dict[str, Any]:
        action_name = action or method_name
        method = getattr(self.window, method_name, None)
        if method is None:
            return self._response(
                action_name,
                missing_ok,
                f"Desktop shell khong ho tro {method_name}.",
                visible=self.visible,
            )
        method()
        self.visible = visible
        return self._response(action_name, True, f"Da gui lenh {action_name} toi desktop shell.", visible=visible)

    def _response(self, action: str, success: bool, message: str, visible: bool | None = None) -> dict[str, Any]:
        return {
            "action": action,
            "mode": "desktop",
            "supported": success,
            "success": success,
            "visible": self.visible if visible is None else visible,
            "message": message,
            "lastError": None if success else message,
        }
