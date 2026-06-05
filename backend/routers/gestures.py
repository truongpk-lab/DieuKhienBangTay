from fastapi import APIRouter

from backend.schemas import GestureLog, GestureTestEventRequest
from backend.services.gesture_service import GestureService

router = APIRouter(prefix="/api/gestures", tags=["gestures"])
gesture_service = GestureService()


@router.get("/current")
def current_gesture() -> dict:
    return gesture_service.current()


@router.get("/logs", response_model=list[GestureLog])
def gesture_logs() -> list[dict[str, str]]:
    return gesture_service.logs()


@router.delete("/logs", response_model=list[GestureLog])
def clear_gesture_logs() -> list[dict[str, str]]:
    return gesture_service.clear_logs()


@router.post("/test-event")
def test_event(request: GestureTestEventRequest) -> dict:
    return gesture_service.test_event(
        gesture_event=request.gesture_event,
        payload=request.payload,
        execute=request.execute,
    )
