from fastapi import APIRouter

from backend.schemas import MicrophoneDevice, MicrophoneStatusResponse
from backend.services.microphone_service import microphone_service
from backend.services.settings_service import settings_service

router = APIRouter(prefix="/api/mic", tags=["microphone"])


@router.get("/status", response_model=MicrophoneStatusResponse)
def mic_status() -> dict:
    return microphone_service.status()


@router.get("/devices", response_model=list[MicrophoneDevice])
def mic_devices() -> list[dict[str, str | bool]]:
    return microphone_service.list_devices()


@router.post("/start", response_model=MicrophoneStatusResponse)
def start_mic() -> dict:
    settings = settings_service.get_settings()
    return microphone_service.start(settings.microphone_id)


@router.post("/stop", response_model=MicrophoneStatusResponse)
def stop_mic() -> dict:
    return microphone_service.stop()
