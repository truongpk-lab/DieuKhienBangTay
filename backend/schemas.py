"""Pydantic schemas for backend API responses and requests."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class RuntimeStatusResponse(BaseModel):
    currentProfile: str
    currentProfileId: str
    currentGesture: str
    currentAction: str
    fps: int
    accuracy: float
    trackingStatus: str
    latency: int
    cameraStatus: str
    handStatus: str
    active: bool


class ProfileSummary(BaseModel):
    id: str
    name: str
    description: str


class GestureLog(BaseModel):
    time: str
    type: Literal["system", "detection", "gesture"]
    message: str


class GestureTestEventRequest(BaseModel):
    gesture_event: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    execute: bool = False


class TrainingSessionRequest(BaseModel):
    profile_id: str = "office"
    function_id: str = "drag_drop"
    mode: Literal["image", "video"] = "image"
    target_samples: int = Field(default=30, ge=1)


class TrainingStatusResponse(BaseModel):
    active: bool
    profileId: str
    functionId: str
    mode: str
    samples: int
    targetSamples: int
    progress: float


class ModelActivateResponse(BaseModel):
    active: dict[str, Any] | None
