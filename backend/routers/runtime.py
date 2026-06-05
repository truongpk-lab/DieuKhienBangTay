from fastapi import APIRouter

from backend.schemas import RuntimeStatusResponse, WorkflowStateResponse, WorkflowTestRequest
from backend.services.runtime_service import runtime_service

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


@router.get("/status", response_model=RuntimeStatusResponse)
def runtime_status() -> dict:
    return runtime_service.status()


@router.post("/start", response_model=RuntimeStatusResponse)
def start_runtime() -> dict:
    return runtime_service.start()


@router.post("/stop", response_model=RuntimeStatusResponse)
def stop_runtime() -> dict:
    return runtime_service.stop()


@router.post("/pause", response_model=RuntimeStatusResponse)
def pause_runtime() -> dict:
    return runtime_service.pause()


@router.post("/resume", response_model=RuntimeStatusResponse)
def resume_runtime() -> dict:
    return runtime_service.resume()


@router.post("/recenter", response_model=RuntimeStatusResponse)
def recenter_runtime() -> dict:
    return runtime_service.recenter()


@router.get("/workflow", response_model=WorkflowStateResponse)
def workflow_state() -> dict:
    return runtime_service.workflow_state()


@router.post("/workflow/test", response_model=WorkflowStateResponse)
def test_workflow_state(request: WorkflowTestRequest) -> dict:
    return runtime_service.set_workflow_state(
        state=request.state,
        event=request.event,
        pinch_distance=request.pinch_distance,
        confidence=request.confidence,
    )


@router.post("/workflow/reset", response_model=WorkflowStateResponse)
def reset_workflow_state() -> dict:
    return runtime_service.reset_workflow()
