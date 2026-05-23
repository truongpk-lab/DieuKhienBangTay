from typing import Any

from fastapi import APIRouter, HTTPException

from backend.schemas import ProfileSummary
from backend.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
profile_service = ProfileService()


@router.get("", response_model=list[ProfileSummary])
def list_profiles() -> list[dict[str, str]]:
    return profile_service.list_profiles()


@router.get("/{profile_id}")
def get_profile(profile_id: str) -> dict[str, Any]:
    try:
        return profile_service.get_profile(profile_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{profile_id}/activate")
def activate_profile(profile_id: str) -> dict[str, Any]:
    try:
        return profile_service.activate(profile_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
