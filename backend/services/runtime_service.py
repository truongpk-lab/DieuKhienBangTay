"""Runtime lifecycle service for camera, hand tracking, and gesture actions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state
from profiles.action_mapper import ActionMapper

from .camera_service import CameraService
from .hand_tracker_service import HandTrackerService
from .profile_service import ProfileService
from .settings_service import SettingsService


class RuntimeService:
    """Manage runtime state behind /api/runtime endpoints.

    The service is intentionally conservative: it coordinates existing services
    and adapters without changing MouseController behavior.
    """

    def __init__(
        self,
        state: RuntimeState = runtime_state,
        camera_service: CameraService | None = None,
        hand_tracker_service: HandTrackerService | None = None,
        profile_service: ProfileService | None = None,
        settings_service: SettingsService | None = None,
    ):
        self.state = state
        self.camera_service = camera_service or CameraService(state=state)
        self.hand_tracker_service = hand_tracker_service or HandTrackerService(state=state)
        self.profile_service = profile_service or ProfileService(state=state)
        self.settings_service = settings_service or SettingsService(state=state)

    def status(self) -> dict[str, Any]:
        return self.state.runtime_payload()

    def start(self) -> dict[str, Any]:
        if self.state.active and self.state.mode == "active":
            self.state.add_log("system", "Runtime already active")
            return self.status()

        self._set_mode("starting", "Starting")
        self.state.last_error = None
        self.state.add_log("system", "Runtime tracking starting")

        try:
            self._sync_active_profile()
            settings = self.settings_service.get_settings()
            self.camera_service.start(settings.camera_id)
            self.hand_tracker_service.start(self.camera_service, on_gesture=self.handle_gesture_event)
            self.state.active = True
            self.state.current_gesture = "Waiting"
            self.state.current_action = "Ready"
            self._set_mode("active", "Active Tracking")
            self.state.add_log("system", "Runtime tracking started")
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            self.camera_service.stop()
            self._handle_error("Runtime start failed", exc)
        return self.status()

    def stop(self) -> dict[str, Any]:
        if not self.state.active and self.state.mode == "idle":
            self.state.add_log("system", "Runtime already stopped")
            return self.status()

        self._set_mode("stopping", "Stopping")
        self.state.add_log("system", "Runtime tracking stopping")

        try:
            self.hand_tracker_service.stop()
            self.camera_service.stop()
            self.state.active = False
            self.state.current_gesture = "Idle"
            self.state.current_action = "None"
            self._set_mode("idle", "Paused")
            self.state.last_error = None
            self.state.add_log("system", "Runtime tracking stopped")
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            self._handle_error("Runtime stop failed", exc)
        return self.status()

    def pause(self) -> dict[str, Any]:
        if not self.state.active:
            self.state.add_log("system", "Runtime pause ignored: not active")
            return self.status()

        if self.state.mode == "paused":
            self.state.add_log("system", "Runtime already paused")
            return self.status()

        self.hand_tracker_service.stop()
        self._set_mode("paused", "Paused")
        self.state.current_gesture = "Paused"
        self.state.current_action = "None"
        self.state.add_log("system", "Runtime paused")
        return self.status()

    def resume(self) -> dict[str, Any]:
        if not self.state.active:
            self.state.add_log("system", "Runtime resume redirected to start")
            return self.start()

        if self.state.mode == "active":
            self.state.add_log("system", "Runtime already active")
            return self.status()

        settings = self.settings_service.get_settings()
        if not self.camera_service.active:
            self.camera_service.start(settings.camera_id)
        self.hand_tracker_service.start(self.camera_service, on_gesture=self.handle_gesture_event)
        self._set_mode("active", "Active Tracking")
        self.state.current_gesture = "Waiting"
        self.state.current_action = "Ready"
        self.state.last_error = None
        self.state.add_log("system", "Runtime resumed")
        return self.status()

    def recenter(self) -> dict[str, Any]:
        if not self.state.active:
            self.state.add_log("system", "Recenter requested while runtime is idle")
            return self.status()

        self.state.current_gesture = "Recenter"
        self.state.current_action = "Calibration"
        self.state.add_log("system", "Runtime recentered")
        return self.status()

    def handle_gesture_event(
        self,
        gesture_event: str | Mapping[str, Any],
        payload: Mapping[str, Any] | None = None,
        execute: bool = False,
    ) -> dict[str, Any]:
        """Resolve a runtime gesture event through the active profile mapper."""

        profile = self.profile_service.active_profile()
        mapper = ActionMapper(profile=profile)
        event_name = self._event_name(gesture_event)
        mapping = mapper.map_gesture_event(event_name)
        self.state.current_gesture = event_name
        if mapping:
            self.state.current_action = str(mapping["label"])
        self._sync_workflow(event_name, payload or {})
        self.state.add_log("gesture", f"Runtime event: {event_name}")

        result = None
        if execute and mapping:
            try:
                result = mapper.execute_gesture_event(gesture_event, payload)
                self.state.add_log("system", f"Action executed: {mapping['action']}")
            except Exception as exc:
                self.state.last_error = f"Action failed for {event_name}: {exc}"
                self.state.add_log("error", self.state.last_error)

        return {
            "gestureEvent": event_name,
            "mapping": mapping,
            "executed": bool(execute and mapping),
            "result": result,
            "workflow": self.workflow_state(),
        }

    def workflow_state(self) -> dict[str, Any]:
        return self.state.workflow_payload()

    def set_workflow_state(
        self,
        state: str,
        event: str | None = None,
        pinch_distance: float = 0.0,
        confidence: float = 0.0,
    ) -> dict[str, Any]:
        self.state.workflow_state = state
        self.state.workflow_event = event or state
        self.state.pinch_distance = float(pinch_distance)
        self.state.workflow_confidence = float(confidence)
        self.state.add_log("gesture", f"Workflow state: {self.state.workflow_state}")
        return self.workflow_state()

    def reset_workflow(self) -> dict[str, Any]:
        return self.set_workflow_state("idle", "idle", 0.0, 0.0)

    def _set_mode(self, mode: str, tracking_status: str) -> None:
        self.state.mode = mode
        self.state.tracking_status = tracking_status

    def _sync_active_profile(self) -> None:
        profile = self.profile_service.active_profile()
        self.state.current_profile_id = str(profile["id"])
        self.state.current_profile = str(profile["name"])

    def _handle_error(self, prefix: str, exc: Exception) -> None:
        self.state.active = False
        self.state.mode = "error"
        self.state.tracking_status = "Error"
        self.state.last_error = f"{prefix}: {exc}"
        self.state.add_log("system", self.state.last_error)

    def _sync_workflow(self, event_name: str, payload: Mapping[str, Any]) -> None:
        transitions = {
            "pinch_start": "pinch_candidate",
            "pinch_hold": "holding",
            "drag_start": "holding",
            "drag_move": "dragging",
            "drag_release": "released",
            "pinch_cancel": "cancelled",
        }
        if event_name not in transitions:
            return
        self.state.workflow_state = transitions[event_name]
        self.state.workflow_event = event_name
        self.state.pinch_distance = float(payload.get("pinch_distance", payload.get("pinchDistance", 0.0)) or 0.0)
        self.state.workflow_confidence = float(payload.get("confidence", 0.0) or 0.0)

    def _event_name(self, gesture_event: str | Mapping[str, Any]) -> str:
        if isinstance(gesture_event, Mapping):
            return str(gesture_event.get("gesture_event") or gesture_event.get("event") or "")
        return gesture_event


runtime_service = RuntimeService()
