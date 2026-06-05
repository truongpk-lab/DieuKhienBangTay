from fastapi import APIRouter

from backend.schemas import AppSettings
from backend.services.settings_service import settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=AppSettings)
def get_settings() -> AppSettings:
    return settings_service.get_settings()


@router.put("", response_model=AppSettings)
def save_settings(settings: AppSettings) -> AppSettings:
    return settings_service.save_settings(settings)
