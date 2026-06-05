from fastapi import APIRouter

from backend.schemas import AppVisibilityResponse
from backend.services.app_visibility_service import app_visibility_service
from backend.services.runtime_service import runtime_service
from desktop.hotkey_controller import HotkeyController
from desktop.tray_controller import TrayController

router = APIRouter(prefix="/api/app", tags=["app"])
tray_controller = TrayController(
    on_show=app_visibility_service.show,
    on_start=runtime_service.start,
    on_stop=runtime_service.stop,
    on_exit=runtime_service.stop,
)
hotkey_controller = HotkeyController(
    on_stop=runtime_service.stop,
    on_show=app_visibility_service.show,
)


@router.get("/status", response_model=AppVisibilityResponse)
def app_status() -> dict:
    return app_visibility_service.status()


@router.post("/minimize", response_model=AppVisibilityResponse)
def minimize_app() -> dict:
    return app_visibility_service.minimize()


@router.post("/hide", response_model=AppVisibilityResponse)
def hide_app() -> dict:
    return app_visibility_service.hide()


@router.post("/show", response_model=AppVisibilityResponse)
def show_app() -> dict:
    return app_visibility_service.show()


@router.post("/toggle", response_model=AppVisibilityResponse)
def toggle_app() -> dict:
    return app_visibility_service.toggle()


@router.post("/emergency-stop")
def emergency_stop() -> dict:
    runtime = runtime_service.stop()
    visibility = app_visibility_service.show()
    return {"ok": True, "runtime": runtime, "visibility": visibility}


@router.post("/tray/start")
def start_tray() -> dict:
    return tray_controller.start()


@router.post("/tray/stop")
def stop_tray() -> dict:
    return tray_controller.stop()


@router.post("/hotkey/start")
def start_hotkey() -> dict:
    return hotkey_controller.start()


@router.post("/hotkey/stop")
def stop_hotkey() -> dict:
    return hotkey_controller.stop()
