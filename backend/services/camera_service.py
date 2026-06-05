"""OpenCV camera service for the runtime backend."""

from __future__ import annotations

from threading import Lock
from typing import Any

from backend.runtime_state import RuntimeState, runtime_state

try:
    import cv2  # type: ignore[import-not-found]

    CV2_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    cv2 = None
    CV2_AVAILABLE = False


class CameraService:
    def __init__(self, state: RuntimeState = runtime_state):
        self.state = state
        self._capture: Any | None = None
        self._camera_index = 0
        self._lock = Lock()

    @property
    def active(self) -> bool:
        return self._capture is not None and bool(self._capture.isOpened())

    @property
    def camera_index(self) -> int:
        return self._camera_index

    def status(self) -> dict[str, str | bool | int | None]:
        return {
            "status": self.state.camera_status,
            "active": self.active,
            "cameraIndex": self._camera_index,
            "mock": False,
        }

    def list_cameras(self, max_devices: int = 5) -> list[dict[str, str | bool]]:
        if not CV2_AVAILABLE:
            self.state.camera_status = "OpenCV is not installed"
            return []

        devices: list[dict[str, str | bool]] = []
        for index in range(max_devices):
            capture = cv2.VideoCapture(index)
            try:
                if capture.isOpened():
                    devices.append(
                        {
                            "id": str(index),
                            "label": f"Camera {index}",
                            "status": "available",
                            "mock": False,
                        }
                    )
            finally:
                capture.release()

        self.state.camera_status = "Camera ready" if devices else "No camera found"
        return devices

    def start(self, camera_id: str | int | None = None) -> dict[str, str | bool | int | None]:
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV is not installed. Run: py -3 -m pip install -r backend\\requirements.txt")

        with self._lock:
            if self.active:
                self.state.camera_status = f"Camera {self._camera_index} streaming"
                return self.status()

            self._camera_index = self._parse_camera_id(camera_id)
            capture = cv2.VideoCapture(self._camera_index)
            if not capture.isOpened():
                capture.release()
                self._capture = None
                self.state.camera_status = f"Camera {self._camera_index} unavailable"
                raise RuntimeError(f"Cannot open camera {self._camera_index}. Check camera connection and permissions.")

            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self._capture = capture
            self.state.camera_status = f"Camera {self._camera_index} streaming"
            self.state.add_log("system", self.state.camera_status)
            return self.status()

    def read(self):
        with self._lock:
            if not self.active:
                return False, None
            return self._capture.read()

    def stop(self) -> dict[str, str | bool | int | None]:
        with self._lock:
            if self._capture is not None:
                self._capture.release()
            self._capture = None
            self.state.camera_status = "Camera released"
            self.state.add_log("system", self.state.camera_status)
            return self.status()

    def _parse_camera_id(self, camera_id: str | int | None) -> int:
        if camera_id is None or camera_id == "":
            return 0
        try:
            return int(camera_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"camera_id must be numeric for OpenCV cameras: {camera_id}") from exc
