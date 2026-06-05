from fastapi import APIRouter

from backend.schemas import CameraDevice
from backend.services.camera_service import CameraService

router = APIRouter(prefix="/api/cameras", tags=["cameras"])
camera_service = CameraService()


@router.get("", response_model=list[CameraDevice])
def list_cameras() -> list[dict[str, str | bool]]:
    return camera_service.list_cameras()
