"""Microphone device and recording service for voice commands."""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state

try:
    import sounddevice as sd  # type: ignore[import-not-found]

    SOUNDDEVICE_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    sd = None
    SOUNDDEVICE_AVAILABLE = False


class MicrophoneService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state
        self.active = False
        self.device_id: str | None = None
        self.last_error: str | None = None

    def status(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "status": self.state.mic_status,
            "deviceId": self.device_id,
            "lastError": self.last_error,
        }

    def list_devices(self) -> list[dict[str, str | bool]]:
        if not SOUNDDEVICE_AVAILABLE:
            self.state.mic_status = "sounddevice is not installed"
            self.last_error = "Missing sounddevice. Run: py -3 -m pip install -r backend\\requirements.txt"
            return []

        devices: list[dict[str, str | bool]] = []
        for index, device in enumerate(sd.query_devices()):
            if int(device.get("max_input_channels", 0)) > 0:
                devices.append(
                    {
                        "id": str(index),
                        "label": str(device.get("name") or f"Microphone {index}"),
                        "status": "available",
                        "mock": False,
                    }
                )
        self.state.mic_status = "Microphone ready" if devices else "No microphone found"
        return devices

    def start(self, device_id: str | None = None) -> dict[str, Any]:
        if not SOUNDDEVICE_AVAILABLE:
            self.last_error = "sounddevice is not installed"
            self.state.mic_status = self.last_error
            raise RuntimeError(self.last_error)
        self.device_id = device_id
        self.active = True
        self.last_error = None
        self.state.mic_status = "Microphone active"
        self.state.add_log("voice", self.state.mic_status)
        return self.status()

    def stop(self) -> dict[str, Any]:
        self.active = False
        self.state.mic_status = "Microphone idle"
        self.state.add_log("voice", self.state.mic_status)
        return self.status()

    def record_wav(self, output_path: str | Path, duration_sec: float = 3.0, sample_rate: int = 16000) -> Path:
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice is not installed")
        device = int(self.device_id) if self.device_id not in (None, "") else None
        frames = sd.rec(int(duration_sec * sample_rate), samplerate=sample_rate, channels=1, dtype="int16", device=device)
        sd.wait()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(frames.tobytes())
        return path


microphone_service = MicrophoneService()
