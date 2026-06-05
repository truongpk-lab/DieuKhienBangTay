from __future__ import annotations

import json
from pathlib import Path


def _office_profile() -> dict:
    return {
        "id": "office",
        "name": "Văn phòng",
        "description": "Test profile",
        "mouse": {"speed": 1.5, "sensitivity": 75, "smoothing": 3},
        "gesture_filter": {"hand": "auto"},
        "functions": [
            {
                "id": "drag_drop",
                "label": "Kéo thả",
                "gesture_event": "drag_move",
                "gesture": "Drag Move",
                "action": "mouse.move",
                "enabled": True,
                "payload": {},
            }
        ],
    }


def test_profile_save_load_roundtrip(tmp_path: Path):
    from profiles.profile_manager import ProfileManager

    config_dir = tmp_path / "profiles"
    config_dir.mkdir()
    profile_path = config_dir / "office.json"
    profile_path.write_text(json.dumps(_office_profile(), ensure_ascii=False), encoding="utf-8")

    manager = ProfileManager(config_dir=config_dir)
    profile = manager.load_profile("office")
    profile["description"] = "Updated"

    saved = manager.save_profile("office", profile)

    assert saved["description"] == "Updated"
    assert (config_dir / ".backup").exists()


def test_training_session_capture_and_train(tmp_path: Path):
    from backend.runtime_state import RuntimeState
    from backend.services.training_service import TrainingService
    from training.dataset_collector import DatasetCollector
    from training.model_registry import ModelRegistry

    service = TrainingService(
        state=RuntimeState(),
        collector=DatasetCollector(dataset_dir=tmp_path / "samples"),
        registry=ModelRegistry(registry_path=tmp_path / "models" / "model_registry.json"),
    )

    started = service.start("office", "drag_drop", "image", 2)
    captured = service.capture_sample(started["sessionId"])
    trained = service.train()

    assert started["active"] is True
    assert captured["samples"] == 1
    assert trained["modelId"]


def test_runtime_workflow_state_reset():
    from backend.runtime_state import RuntimeState
    from backend.services.runtime_service import RuntimeService

    runtime = RuntimeService(state=RuntimeState())
    active = runtime.set_workflow_state("dragging", event="drag_move", pinch_distance=12.5, confidence=0.9)
    reset = runtime.reset_workflow()

    assert active["state"] == "dragging"
    assert active["event"] == "drag_move"
    assert reset["state"] == "idle"


def test_keyboard_controller_safe_fallback():
    from actions.keyboard_controller import KeyboardController

    keyboard = KeyboardController(enabled=False)
    result = keyboard.press("space")

    assert result["status"] == "skipped"


def test_backend_app_import_when_fastapi_available():
    import pytest

    pytest.importorskip("fastapi")
    from backend.app import app

    assert app.title == "ACV Gesture Control API"


def test_backend_health_and_runtime_when_fastapi_available():
    import pytest

    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from backend.app import app

    client = TestClient(app)
    assert client.get("/api/health").status_code == 200
    started = client.post("/api/runtime/start").json()
    assert "active" in started
    assert started["mode"] in {"active", "error"}
    assert client.post("/api/runtime/stop").json()["active"] is False
    assert client.get("/api/mic/status").status_code == 200
    ai_response = client.post("/api/ai/command", json={"text": "dung dieu khien", "execute": True}).json()
    assert ai_response["ok"] is False or ai_response["intent"] in {
        "start",
        "stop",
        "pause",
        "resume",
        "recenter",
        "switch_profile",
        "show_app",
        "hide_app",
        "emergency_stop",
        "training_start",
        "training_stop",
    }


def test_action_mapper_and_mouse_adapter_import():
    from actions.mouse_control_adapter import MouseControlAdapter
    from profiles.action_mapper import ActionMapper

    mapper = ActionMapper(profile=_office_profile(), mouse_adapter=MouseControlAdapter())
    mapping = mapper.map_gesture_event("drag_move")

    assert mapping is not None
    assert mapping["action"] == "mouse.move"


def test_settings_persistence(tmp_path: Path):
    import pytest

    pytest.importorskip("pydantic")
    from backend.services.settings_service import SettingsService

    service = SettingsService(settings_path=tmp_path / "settings.json")
    settings = service.get_settings()
    settings.smoothing = 4
    settings.microphone_id = "1"
    settings.voice_commands_enabled = True
    service.save_settings(settings)

    loaded = SettingsService(settings_path=tmp_path / "settings.json").get_settings()
    assert loaded.smoothing == 4
    assert loaded.microphone_id == "1"
    assert loaded.voice_commands_enabled is True


def test_demo_run_import_shape():
    import importlib.util

    demo_path = Path("DIEU_KHIEN_CHUOT") / "demo_run.py"
    spec = importlib.util.spec_from_file_location("demo_run_import_check", demo_path)
    assert spec is not None and spec.loader is not None


def test_hotkey_trigger_stops_and_shows():
    from desktop.hotkey_controller import HotkeyController

    calls: list[str] = []
    controller = HotkeyController(on_stop=lambda: calls.append("stop"), on_show=lambda: calls.append("show"))

    controller.trigger()

    assert calls == ["stop", "show"]


def test_tray_callbacks_are_wired():
    from desktop.tray_controller import TrayController

    calls: list[str] = []
    controller = TrayController(
        on_show=lambda: calls.append("show"),
        on_start=lambda: calls.append("start"),
        on_stop=lambda: calls.append("stop"),
        on_exit=lambda: calls.append("exit"),
    )

    controller._call(controller.on_show)
    controller._call(controller.on_start)
    controller._call(controller.on_stop)
    controller._call(controller.on_exit)

    assert calls == ["show", "start", "stop", "exit"]
