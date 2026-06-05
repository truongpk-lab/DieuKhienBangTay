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


@router.put("/{profile_id}")
def save_profile(profile_id: str, profile: dict[str, Any]) -> dict[str, Any]:
    try:
        return profile_service.save_profile(profile_id, profile)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("")
def create_profile(profile: dict[str, Any]) -> dict[str, Any]:
    try:
        return profile_service.create_profile(profile)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{profile_id}")
def delete_profile(profile_id: str) -> dict[str, Any]:
    try:
        return profile_service.delete_profile(profile_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{profile_id}/activate")
def activate_profile(profile_id: str) -> dict[str, Any]:
    try:
        return profile_service.activate(profile_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
