from fastapi import APIRouter

from backend.schemas import AppSettings, CalibrationResponse
from backend.services.settings_service import settings_service

router = APIRouter(prefix="/api/calibration", tags=["calibration"])


@router.post("/start", response_model=CalibrationResponse)
def start_calibration(settings: AppSettings) -> dict:
    return settings_service.start_calibration(settings)


@router.post("/skip", response_model=CalibrationResponse)
def skip_calibration(settings: AppSettings) -> dict:
    return settings_service.skip_calibration(settings)
