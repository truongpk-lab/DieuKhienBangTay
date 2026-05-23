from typing import Any

from fastapi import APIRouter, HTTPException

from training.model_registry import ModelRegistry

router = APIRouter(prefix="/api/models", tags=["models"])
model_registry = ModelRegistry()


@router.get("")
def list_models() -> list[dict[str, Any]]:
    return model_registry.list_models()


@router.get("/active")
def active_models() -> dict[str, Any]:
    return {
        "static": model_registry.get_active_model("static"),
        "dynamic": model_registry.get_active_model("dynamic"),
    }


@router.post("/{model_id}/activate")
def activate_model(model_id: str) -> dict[str, Any]:
    try:
        return {"active": model_registry.set_active_model(model_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
