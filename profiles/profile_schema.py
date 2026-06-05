"""Basic schema validation for ACV Gesture Control profile JSON files."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


REQUIRED_PROFILE_FIELDS = {
    "id",
    "name",
    "description",
    "mouse",
    "gesture_filter",
    "functions",
}

REQUIRED_FUNCTION_FIELDS = {
    "id",
    "label",
    "gesture_event",
    "gesture",
    "action",
    "enabled",
}

ALLOWED_ACTIONS = {
    "mouse.move",
    "mouse.left_click",
    "mouse.right_click",
    "mouse.scroll",
    "mouse.down",
    "mouse.up",
    "mouse.drag",
    "keyboard.hotkey",
    "keyboard.press",
    "keyboard.release",
    "keyboard.switch_tab",
    "keyboard.copy",
    "keyboard.paste",
    "media.play_pause",
    "media.next",
    "media.previous",
    "media.volume_up",
    "media.volume_down",
    "media.seek_forward",
    "media.seek_backward",
    "media.fullscreen",
    "game.left",
    "game.right",
    "game.move_left",
    "game.move_right",
    "game.jump",
    "game.attack",
    "game.dash",
    "game.block",
    "game.crouch",
    "game.skill_1",
}


class ProfileValidationError(ValueError):
    """Raised when a profile JSON object does not match the base schema."""


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProfileValidationError(f"{field_name} must be an object")
    return value


def _require_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProfileValidationError(f"{field_name} must be a non-empty string")


def validate_profile(profile: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate and return a profile mapping.

    This intentionally checks only the Phase 10 contract: the profile shape
    expected by the UI and future action mapping layer.
    """

    _require_mapping(profile, "profile")

    missing_fields = sorted(REQUIRED_PROFILE_FIELDS - set(profile.keys()))
    if missing_fields:
        raise ProfileValidationError(
            f"profile is missing required fields: {', '.join(missing_fields)}"
        )

    for field_name in ("id", "name", "description"):
        _require_non_empty_string(profile[field_name], field_name)

    mouse = _require_mapping(profile["mouse"], "mouse")
    gesture_filter = _require_mapping(profile["gesture_filter"], "gesture_filter")

    for field_name in ("speed", "sensitivity", "smoothing"):
        if field_name not in mouse:
            raise ProfileValidationError(f"mouse.{field_name} is required")
        if not isinstance(mouse[field_name], (int, float)):
            raise ProfileValidationError(f"mouse.{field_name} must be a number")

    if "hand" not in gesture_filter:
        raise ProfileValidationError("gesture_filter.hand is required")
    _require_non_empty_string(gesture_filter["hand"], "gesture_filter.hand")

    functions = profile["functions"]
    if not isinstance(functions, Sequence) or isinstance(functions, (str, bytes)):
        raise ProfileValidationError("functions must be a list")
    if not functions:
        raise ProfileValidationError("functions must not be empty")

    seen_ids: set[str] = set()
    seen_gesture_events: set[str] = set()
    for index, function in enumerate(functions):
        function_path = f"functions[{index}]"
        _require_mapping(function, function_path)

        missing_function_fields = sorted(REQUIRED_FUNCTION_FIELDS - set(function.keys()))
        if missing_function_fields:
            raise ProfileValidationError(
                f"{function_path} is missing required fields: "
                f"{', '.join(missing_function_fields)}"
            )

        for field_name in ("id", "label", "gesture_event", "gesture", "action"):
            _require_non_empty_string(function[field_name], f"{function_path}.{field_name}")

        if not isinstance(function["enabled"], bool):
            raise ProfileValidationError(f"{function_path}.enabled must be a boolean")

        function_id = function["id"]
        if function_id in seen_ids:
            raise ProfileValidationError(f"duplicate function id: {function_id}")
        seen_ids.add(function_id)

        gesture_event = function["gesture_event"]
        if function.get("enabled") and gesture_event in seen_gesture_events:
            raise ProfileValidationError(f"duplicate enabled gesture_event: {gesture_event}")
        if function.get("enabled"):
            seen_gesture_events.add(gesture_event)

        action = function["action"]
        if action not in ALLOWED_ACTIONS:
            raise ProfileValidationError(f"unsupported action: {action}")

        payload = function.get("payload", {})
        if payload is not None and not isinstance(payload, Mapping):
            raise ProfileValidationError(f"{function_path}.payload must be an object")

    return profile
