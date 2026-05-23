"""Phase 17 smoke test for versioned model registry behavior."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.model_registry import ModelRegistry


def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        registry_path = Path(tmp_dir) / "models" / "model_registry.json"
        registry = ModelRegistry(registry_path)

        first = registry.add_model(
            model_id="static_20260523_000001",
            model_type="static",
            path=Path(tmp_dir) / "models" / "static_1" / "model.joblib",
            profiles=["office"],
            labels=["Pinch Index", "Open Palm Move"],
            metrics={"accuracy": 0.91, "macro_f1": 0.9},
            sample_count=24,
            created_at="2026-05-23T00:00:01Z",
            set_active=True,
        )
        second = registry.add_model(
            model_id="static_20260523_000002",
            model_type="static",
            path=Path(tmp_dir) / "models" / "static_2" / "model.joblib",
            profiles=["office", "game_2d"],
            labels=["Pinch Index", "Open Palm Move", "Rapid Punch"],
            metrics={"accuracy": 0.94, "macro_f1": 0.93},
            sample_count=36,
            created_at="2026-05-23T00:00:02Z",
        )
        dynamic = registry.add_model(
            model_id="dynamic_20260523_000001",
            model_type="dynamic",
            path=Path(tmp_dir) / "models" / "dynamic_1" / "model.joblib",
            profiles=["office"],
            labels=["Pinch Drag Drop"],
            metrics={"accuracy": 0.88},
            sample_count=12,
            created_at="2026-05-23T00:00:03Z",
            set_active=True,
        )

        models = registry.list_models()
        assert len(models) == 3
        assert first["dataset"]["sample_count"] == 24
        assert dynamic["type"] == "dynamic"

        active_static = registry.get_active_model("static")
        assert active_static is not None
        assert active_static["model_id"] == first["model_id"]

        registry.set_active_model(second["model_id"])
        active_static = registry.get_active_model("static")
        assert active_static is not None
        assert active_static["model_id"] == second["model_id"]

        rolled_back = registry.rollback("static")
        assert rolled_back is not None
        assert rolled_back["model_id"] == first["model_id"]
        assert registry.get_active_model("static")["model_id"] == first["model_id"]

        assert registry.get_active_model("dynamic")["model_id"] == dynamic["model_id"]
        assert registry.rollback("dynamic") is None

    print("phase17 model registry fake model ok")


if __name__ == "__main__":
    main()
