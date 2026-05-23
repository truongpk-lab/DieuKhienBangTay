"""Versioned model registry for trained gesture models."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

ModelType = Literal["static", "dynamic"]


class ModelRegistry:
    """Persist model metadata and active model pointers in a JSON registry."""

    def __init__(self, registry_path: str | Path = "models/model_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self._write_registry(self._empty_registry())

    def add_model(
        self,
        model_id: str,
        model_type: ModelType,
        path: str | Path,
        profiles: list[str] | None = None,
        labels: list[str] | None = None,
        metrics: dict[str, Any] | None = None,
        sample_count: int = 0,
        created_at: str | None = None,
        set_active: bool = False,
    ) -> dict[str, Any]:
        """Add a model metadata record without overwriting existing ids."""

        self._validate_model_type(model_type)
        if not model_id:
            raise ValueError("model_id is required")
        if sample_count < 0:
            raise ValueError("sample_count must be greater than or equal to 0")

        registry = self._load_registry()
        if any(model["model_id"] == model_id for model in registry["models"]):
            raise ValueError(f"model_id already exists: {model_id}")

        record = {
            "model_id": model_id,
            "type": model_type,
            "path": str(path),
            "created_at": created_at or self._utc_now(),
            "profiles": list(profiles or []),
            "labels": list(labels or []),
            "metrics": dict(metrics or {}),
            "dataset": {"sample_count": int(sample_count)},
        }
        registry["models"].append(record)
        if set_active:
            registry["active"][model_type] = model_id
        self._write_registry(registry)
        return deepcopy(record)

    def list_models(self, model_type: ModelType | None = None) -> list[dict[str, Any]]:
        """Return all model records, optionally filtered by type."""

        registry = self._load_registry()
        models = registry["models"]
        if model_type is not None:
            self._validate_model_type(model_type)
            models = [model for model in models if model["type"] == model_type]
        return deepcopy(models)

    def get_active_model(self, model_type: ModelType) -> dict[str, Any] | None:
        """Return the active model record for the given model type."""

        self._validate_model_type(model_type)
        registry = self._load_registry()
        active_id = registry["active"].get(model_type)
        if active_id is None:
            return None
        return deepcopy(self._find_model(registry, active_id))

    def set_active_model(self, model_id: str) -> dict[str, Any]:
        """Set an existing model as active for its own type."""

        registry = self._load_registry()
        model = self._find_model(registry, model_id)
        registry["active"][model["type"]] = model_id
        self._write_registry(registry)
        return deepcopy(model)

    def rollback(self, model_type: ModelType) -> dict[str, Any] | None:
        """Activate the newest non-active model for the requested type."""

        self._validate_model_type(model_type)
        registry = self._load_registry()
        current_id = registry["active"].get(model_type)
        candidates = [
            model
            for model in registry["models"]
            if model["type"] == model_type and model["model_id"] != current_id
        ]
        if not candidates:
            return None

        rollback_model = max(candidates, key=lambda model: model["created_at"])
        registry["active"][model_type] = rollback_model["model_id"]
        self._write_registry(registry)
        return deepcopy(rollback_model)

    def _load_registry(self) -> dict[str, Any]:
        with self.registry_path.open("r", encoding="utf-8") as file:
            registry = json.load(file)
        return self._normalize_registry(registry)

    def _write_registry(self, registry: dict[str, Any]) -> None:
        normalized = self._normalize_registry(registry)
        temp_path = self.registry_path.with_suffix(self.registry_path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(normalized, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temp_path.replace(self.registry_path)

    def _normalize_registry(self, registry: dict[str, Any]) -> dict[str, Any]:
        active = registry.get("active") if isinstance(registry.get("active"), dict) else {}
        models = registry.get("models") if isinstance(registry.get("models"), list) else []
        normalized = {
            "active": {
                "static": active.get("static"),
                "dynamic": active.get("dynamic"),
            },
            "models": models,
        }
        for model_type, active_id in normalized["active"].items():
            if active_id is not None:
                model = self._find_model(normalized, active_id)
                if model["type"] != model_type:
                    raise ValueError(f"active {model_type} points to {model['type']} model: {active_id}")
        return normalized

    def _find_model(self, registry: dict[str, Any], model_id: str) -> dict[str, Any]:
        for model in registry["models"]:
            if model.get("model_id") == model_id:
                return model
        raise KeyError(f"model_id not found: {model_id}")

    def _validate_model_type(self, model_type: str) -> None:
        if model_type not in {"static", "dynamic"}:
            raise ValueError("model_type must be 'static' or 'dynamic'")

    def _empty_registry(self) -> dict[str, Any]:
        return {"active": {"static": None, "dynamic": None}, "models": []}

    def _utc_now(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
