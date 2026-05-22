from .profile_schema import Profile, validate_profile


class ActionMapper:
    def __init__(self, profile):
        self.profile = (
            profile if isinstance(profile, Profile) else validate_profile(profile)
        )
        self._actions_by_event = self._build_event_map()

    def _build_event_map(self):
        actions = {}
        for function in self.profile.functions:
            function_action = function.get("action")
            if function_action is not None:
                actions[function["gesture_event"]] = self._mapping(
                    function,
                    function_action,
                )

            for step in function.get("action_sequence", []):
                actions[step["event"]] = self._mapping(function, step["action"], step)
        return actions

    @staticmethod
    def _mapping(function, action, source=None):
        source = function if source is None else source
        mapping = {
            "function_id": function["id"],
            "gesture_event": source.get("event", function["gesture_event"]),
            "action": action,
        }
        if "keys" in source:
            mapping["keys"] = list(source["keys"])
        elif "keys" in function:
            mapping["keys"] = list(function["keys"])
        return mapping

    def action_for(self, gesture_event):
        return self._actions_by_event.get(gesture_event)
