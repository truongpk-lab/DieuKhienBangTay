"""Application window visibility service.

The backend can control a desktop shell when one registers a window controller.
When the frontend runs in a normal browser, these methods return a clear
fallback response instead of pretending the browser window can be minimized.
"""

from __future__ import annotations

from typing import Any, Protocol


class WindowController(Protocol):
    def minimize(self) -> dict[str, Any]:
        ...

    def hide(self) -> dict[str, Any]:
        ...

    def show(self) -> dict[str, Any]:
        ...

    def toggle(self) -> dict[str, Any]:
        ...

    def status(self) -> dict[str, Any]:
        ...


class AppVisibilityService:
    def __init__(self):
        self._controller: WindowController | None = None
        self.visible = True
        self.last_error: str | None = None

    def register_controller(self, controller: WindowController) -> None:
        self._controller = controller
        self.last_error = None

    def unregister_controller(self) -> None:
        self._controller = None

    def status(self) -> dict[str, Any]:
        if self._controller is None:
            return self._browser_fallback("status", success=True)
        return self._normalize("status", self._controller.status())

    def minimize(self) -> dict[str, Any]:
        if self._controller is None:
            return self._browser_fallback("minimize")
        return self._run_controller_action("minimize", self._controller.minimize)

    def hide(self) -> dict[str, Any]:
        if self._controller is None:
            return self._browser_fallback("hide")
        return self._run_controller_action("hide", self._controller.hide)

    def show(self) -> dict[str, Any]:
        if self._controller is None:
            return self._browser_fallback("show", success=True)
        return self._run_controller_action("show", self._controller.show)

    def toggle(self) -> dict[str, Any]:
        if self._controller is None:
            return self._browser_fallback("toggle")
        return self._run_controller_action("toggle", self._controller.toggle)

    def _run_controller_action(self, action: str, callback) -> dict[str, Any]:
        try:
            result = self._normalize(action, callback())
            self.visible = bool(result["visible"])
            self.last_error = None if result["success"] else result["message"]
            return result
        except Exception as exc:  # pragma: no cover - defensive desktop guard
            self.last_error = f"App visibility {action} failed: {exc}"
            return {
                "action": action,
                "mode": "desktop",
                "supported": True,
                "success": False,
                "visible": self.visible,
                "message": self.last_error,
                "lastError": self.last_error,
            }

    def _normalize(self, action: str, result: dict[str, Any]) -> dict[str, Any]:
        visible = bool(result.get("visible", self.visible))
        success = bool(result.get("success", True))
        message = str(result.get("message") or self._default_message(action, success))
        return {
            "action": action,
            "mode": str(result.get("mode") or "desktop"),
            "supported": bool(result.get("supported", True)),
            "success": success,
            "visible": visible,
            "message": message,
            "lastError": result.get("lastError"),
        }

    def _browser_fallback(self, action: str, success: bool = False) -> dict[str, Any]:
        message = (
            "Dang chay trong browser nen khong the tu an/minimize cua so. "
            "Hay minimize trinh duyet thu cong sau khi runtime active."
        )
        if action in {"show", "status"}:
            message = "Dang chay trong browser; cua so van do nguoi dung dieu khien."
        return {
            "action": action,
            "mode": "browser",
            "supported": False,
            "success": success,
            "visible": True,
            "message": message,
            "lastError": None if success else message,
        }

    def _default_message(self, action: str, success: bool) -> str:
        if not success:
            return f"Desktop shell khong thuc hien duoc lenh {action}."
        return f"Desktop shell da thuc hien lenh {action}."


app_visibility_service = AppVisibilityService()
