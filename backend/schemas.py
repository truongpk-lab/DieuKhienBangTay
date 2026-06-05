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
    micStatus: str = "Microphone idle"
    aiStatus: str = "Gemini disabled"
    lastVoiceCommand: str | None = None
    lastTranscript: str | None = None
    commandConfidence: float = 0.0
    active: bool
    mode: str = "idle"
    lastError: str | None = None
    workflow: dict[str, Any] = Field(default_factory=dict)


class AppVisibilityResponse(BaseModel):
    action: str
    mode: str
    supported: bool
    success: bool
    visible: bool
    message: str
    lastError: str | None = None


class CameraDevice(BaseModel):
    id: str
    label: str
    status: str = "available"
    mock: bool = False


class MicrophoneDevice(BaseModel):
    id: str
    label: str
    status: str = "available"
    mock: bool = False


class AppSettings(BaseModel):
    camera_id: str = "0"
    microphone_id: str | None = None
    hand_mode: Literal["left", "right", "auto"] = "right"
    speed: float = Field(default=1.5, ge=0.1, le=3.0)
    sensitivity: int = Field(default=75, ge=0, le=100)
    smoothing: int = Field(default=3, ge=1, le=5)
    active_profile_id: str = "office"
    auto_hide_on_start: bool = True
    ai_provider: Literal["gemini"] = "gemini"
    voice_commands_enabled: bool = False


class CalibrationResponse(BaseModel):
    ok: bool
    status: str
    message: str
    settings: AppSettings


class ProfileSummary(BaseModel):
    id: str
    name: str
    description: str


class GestureLog(BaseModel):
    time: str
    type: Literal["system", "detection", "gesture", "warning", "error", "training", "voice", "ai"]
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


class TrainingCaptureRequest(BaseModel):
    session_id: str | None = None


class TrainingStatusResponse(BaseModel):
    sessionId: str | None = None
    active: bool
    profileId: str
    functionId: str
    mode: str
    samples: int
    targetSamples: int
    progress: float
    lastError: str | None = None
    preview: list[dict[str, Any]] = Field(default_factory=list)


class TrainingJobResponse(TrainingStatusResponse):
    jobId: str | None = None
    modelId: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class WorkflowStateResponse(BaseModel):
    state: str
    event: str
    pinchDistance: float
    confidence: float
    latency: int
    sensorActive: bool


class WorkflowTestRequest(BaseModel):
    state: Literal["idle", "pinch_candidate", "holding", "dragging", "released", "cancelled"]
    event: str | None = None
    pinch_distance: float = Field(default=0.0, ge=0)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ModelActivateResponse(BaseModel):
    active: dict[str, Any] | None


class MicrophoneStatusResponse(BaseModel):
    active: bool
    status: str
    deviceId: str | None = None
    lastError: str | None = None


class VoiceCommandRequest(BaseModel):
    text: str | None = None
    audio_path: str | None = None
    execute: bool = True


class VoiceCommandResponse(BaseModel):
    ok: bool
    intent: str | None = None
    target: str | None = None
    profile_id: str | None = None
    action: str | None = None
    confidence: float = 0.0
    requires_confirmation: bool = False
    transcript: str | None = None
    executed: bool = False
    result: dict[str, Any] | None = None
    message: str
