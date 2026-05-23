from fastapi import APIRouter

from backend.schemas import TrainingSessionRequest, TrainingStatusResponse
from backend.services.training_service import TrainingService

router = APIRouter(prefix="/api/training", tags=["training"])
training_service = TrainingService()


@router.get("/status", response_model=TrainingStatusResponse)
def training_status() -> dict:
    return training_service.status()


@router.post("/session/start", response_model=TrainingStatusResponse)
def start_session(request: TrainingSessionRequest) -> dict:
    return training_service.start(
        profile_id=request.profile_id,
        function_id=request.function_id,
        mode=request.mode,
        target_samples=request.target_samples,
    )


@router.post("/session/stop", response_model=TrainingStatusResponse)
def stop_session() -> dict:
    return training_service.stop()


@router.post("/session/save", response_model=TrainingStatusResponse)
def save_session() -> dict:
    return training_service.save()


@router.post("/session/cancel", response_model=TrainingStatusResponse)
def cancel_session() -> dict:
    return training_service.cancel()
