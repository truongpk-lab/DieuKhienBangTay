from fastapi import APIRouter

from backend.runtime_state import runtime_state
from backend.schemas import RuntimeStatusResponse
from backend.services.camera_service import CameraService
from backend.services.hand_tracker_service import HandTrackerService

router = APIRouter(prefix="/api/runtime", tags=["runtime"])
camera_service = CameraService()
hand_tracker_service = HandTrackerService()


@router.get("/status", response_model=RuntimeStatusResponse)
def runtime_status() -> dict:
    return runtime_state.runtime_payload()


@router.post("/start", response_model=RuntimeStatusResponse)
def start_runtime() -> dict:
    camera_service.start()
    hand_tracker_service.start()
    runtime_state.active = True
    runtime_state.tracking_status = "Active Tracking"
    runtime_state.add_log("system", "Runtime tracking started")
    return runtime_state.runtime_payload()


@router.post("/stop", response_model=RuntimeStatusResponse)
def stop_runtime() -> dict:
    camera_service.stop()
    hand_tracker_service.stop()
    runtime_state.active = False
    runtime_state.tracking_status = "Paused"
    runtime_state.add_log("system", "Runtime tracking stopped")
    return runtime_state.runtime_payload()
