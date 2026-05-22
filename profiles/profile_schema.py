from dataclasses import dataclass
from typing import Any


class ProfileValidationError(ValueError):
    """Raised when a profile config is missing required mapping data."""


@dataclass(frozen=True)
class Profile:
    id: str
    name: str
    description: str
    mouse: dict[str, Any]
    gesture_filter: dict[str, Any]
    functions: tuple[dict[str, Any], ...]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "mouse": dict(self.mouse),
            "gesture_filter": dict(self.gesture_filter),
            "functions": [dict(function) for function in self.functions],
        }


def _require_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ProfileValidationError(f"Profile field '{field_name}' must be a string.")
    return value


def _validate_action(function, field_name):
    action = function.get(field_name)
    if not isinstance(action, str) or not action.strip():
        function_id = function.get("id", "<unknown>")
        raise ProfileValidationError(
            f"Function '{function_id}' field '{field_name}' must be an action string."
        )


def _validate_function(function, seen_ids, seen_events):
    if not isinstance(function, dict):
        raise ProfileValidationError("Each profile function must be an object.")

    function_id = _require_string(function.get("id"), "functions[].id")
    _require_string(function.get("name"), f"functions[{function_id}].name")
    gesture_event = _require_string(
        function.get("gesture_event"),
        f"functions[{function_id}].gesture_event",
    )

    if function_id in seen_ids:
        raise ProfileValidationError(f"Duplicate profile function id '{function_id}'.")
    if gesture_event in seen_events:
        raise ProfileValidationError(f"Duplicate gesture event '{gesture_event}'.")

    if "action" not in function and "action_sequence" not in function:
        raise ProfileValidationError(
            f"Function '{function_id}' needs 'action' or 'action_sequence'."
        )

    if "action" in function:
        _validate_action(function, "action")

    if "action_sequence" in function:
        action_sequence = function["action_sequence"]
        if not isinstance(action_sequence, list) or not action_sequence:
            raise ProfileValidationError(
                f"Function '{function_id}' action_sequence must be a non-empty list."
            )
        for item in action_sequence:
            if not isinstance(item, dict):
                raise ProfileValidationError(
                    f"Function '{function_id}' action_sequence items must be objects."
                )
            step_event = _require_string(
                item.get("event"),
                f"functions[{function_id}].event",
            )
            if step_event == gesture_event or step_event in seen_events:
                raise ProfileValidationError(f"Duplicate gesture event '{step_event}'.")
            _validate_action(item, "action")
            seen_events.add(step_event)

    seen_ids.add(function_id)
    seen_events.add(gesture_event)


def validate_profile(data):
    if not isinstance(data, dict):
        raise ProfileValidationError("Profile config must be an object.")

    for field_name in ("id", "name", "description"):
        _require_string(data.get(field_name), field_name)

    mouse = data.get("mouse")
    gesture_filter = data.get("gesture_filter")
    functions = data.get("functions")
    if not isinstance(mouse, dict):
        raise ProfileValidationError("Profile field 'mouse' must be an object.")
    if not isinstance(gesture_filter, dict):
        raise ProfileValidationError(
            "Profile field 'gesture_filter' must be an object."
        )
    if not isinstance(functions, list):
        raise ProfileValidationError("Profile field 'functions' must be a list.")

    seen_ids = set()
    seen_events = set()
    for function in functions:
        _validate_function(function, seen_ids, seen_events)

    return Profile(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        mouse=mouse,
        gesture_filter=gesture_filter,
        functions=tuple(functions),
    )
