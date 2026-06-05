"""One-command launcher for ACV Gesture Control."""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import threading
import time
import os
import urllib.request
import webbrowser
from argparse import ArgumentParser
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "dist" / "index.html"
BACKEND_URL = "http://127.0.0.1:8000"


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Launch ACV Gesture Control desktop app.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Start/check backend and frontend artifacts, then exit without opening a window.",
    )
    args = parser.parse_args(argv)

    missing = missing_python_packages()
    if missing:
        print("Missing Python packages:", ", ".join(missing))
        print(r"Run: py -3 -m pip install -r DIEU_KHIEN_CHUOT\requirements.txt")
        return 1
    warn_optional_packages()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("GEMINI_API_KEY is not set; camera gesture control can run, but AI voice commands are disabled.")

    if not FRONTEND_INDEX.exists() and not build_frontend():
        return 1

    if args.self_test:
        return self_test()

    if not port_available(8000) and not wait_for_backend(timeout_sec=1.0):
        print("Port 8000 is already in use and ACV backend health is not responding.")
        return 1

    server = start_backend()
    if not wait_for_backend():
        server.should_exit = True
        print("Backend did not become ready at", BACKEND_URL)
        return 1

    open_desktop_or_browser(server)
    server.should_exit = True
    return 0


def self_test() -> int:
    """Validate the one-command runtime path without opening a GUI window."""

    print("ACV launcher self-test starting from", ROOT)
    if not FRONTEND_INDEX.exists() and not build_frontend():
        return 1

    existing_backend = wait_for_backend(timeout_sec=1.0)
    server = None if existing_backend else start_backend()
    try:
        if not wait_for_backend():
            print("Self-test failed: backend health did not respond.")
            return 1

        health = request_json("/api/health")
        status = request_json("/api/runtime/status")
        mic_status = request_json("/api/mic/status")
        print("health:", health.get("status"))
        print("frontend:", FRONTEND_INDEX)
        print("port 8000:", "existing" if existing_backend else "started")
        print("port 5173:", "free" if port_available(5173) else "in use")
        print("runtime status:", status.get("mode"))
        print("mic status:", mic_status.get("status"))
        print("ai status:", status.get("aiStatus"))
        print("ACV launcher self-test ok")
        return 0
    finally:
        if server is not None:
            server.should_exit = True
            time.sleep(0.5)


def missing_python_packages() -> list[str]:
    missing: list[str] = []
    for package, import_name in (("fastapi", "fastapi"), ("uvicorn", "uvicorn")):
        try:
            __import__(import_name)
        except ModuleNotFoundError:
            missing.append(package)
    return missing


def warn_optional_packages() -> None:
    optional = (
        ("opencv-python", "cv2", "Camera runtime"),
        ("mediapipe", "mediapipe", "Hand tracking"),
        ("google-genai", "google.genai", "Gemini voice commands"),
        ("sounddevice", "sounddevice", "Microphone commands"),
    )
    missing: list[str] = []
    for package, import_name, feature in optional:
        try:
            __import__(import_name)
        except ModuleNotFoundError:
            missing.append(f"{package} ({feature})")
    if missing:
        print("Optional runtime packages missing:", ", ".join(missing))
        print(r"Install all runtime features with: py -3 -m pip install -r DIEU_KHIEN_CHUOT\requirements.txt")


def build_frontend() -> bool:
    npm = shutil.which("npm")
    if npm is None:
        print("Missing npm/node. Install Node.js, then run: cd frontend && npm install")
        return False
    print("frontend/dist missing; building frontend...")
    result = subprocess.run([npm, "run", "build"], cwd=FRONTEND_DIR, check=False)
    return result.returncode == 0 and FRONTEND_INDEX.exists()


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def start_backend():
    import uvicorn

    config = uvicorn.Config(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return server


def wait_for_backend(timeout_sec: float = 10.0) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BACKEND_URL}/api/health", timeout=0.8) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.25)
    return False


def request_json(path: str, method: str = "GET") -> dict[str, Any]:
    request = urllib.request.Request(f"{BACKEND_URL}{path}", method=method)
    with urllib.request.urlopen(request, timeout=2.0) as response:
        import json

        return json.loads(response.read().decode("utf-8"))


def open_desktop_or_browser(server) -> None:
    try:
        import webview  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print("pywebview missing; opening browser fallback.")
        webbrowser.open(FRONTEND_INDEX.as_uri())
        print("Press Ctrl+C to stop backend.")
        try:
            while not server.should_exit:
                time.sleep(0.5)
        except KeyboardInterrupt:
            return
        return

    window = webview.create_window(
        "ACV Gesture Control",
        FRONTEND_INDEX.as_uri(),
        width=1440,
        height=900,
        min_size=(1180, 760),
        background_color="#0A0A0C",
    )
    try:
        from backend.services.app_visibility_service import app_visibility_service
        from desktop.window_controller import PyWebviewWindowController

        app_visibility_service.register_controller(PyWebviewWindowController(window))
    except Exception as exc:
        print("Window visibility registration failed:", exc)
    webview.start(debug=False)


if __name__ == "__main__":
    raise SystemExit(main())
