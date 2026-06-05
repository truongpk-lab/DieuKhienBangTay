"""FastAPI app for Phase 18 backend/frontend integration."""

import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import ai, app_control, calibration, cameras, gestures, health, mic, models, profiles, runtime, settings, training
from backend.services.runtime_service import runtime_service
from backend.websocket import runtime as runtime_ws

logger = logging.getLogger("acv.backend")

app = FastAPI(title="ACV Gesture Control API", version="0.18.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(app_control.router)
app.include_router(ai.router)
app.include_router(cameras.router)
app.include_router(mic.router)
app.include_router(settings.router)
app.include_router(calibration.router)
app.include_router(runtime.router)
app.include_router(profiles.router)
app.include_router(gestures.router)
app.include_router(training.router)
app.include_router(models.router)
app.include_router(runtime_ws.router)


@app.on_event("startup")
async def configure_asyncio_disconnect_filter() -> None:
    """Suppress noisy Windows socket-reset traces from browser/WebSocket reconnects."""

    loop = asyncio.get_running_loop()
    previous_handler = loop.get_exception_handler()

    def handle_loop_exception(loop: asyncio.AbstractEventLoop, context: dict) -> None:
        exception = context.get("exception")
        if is_expected_client_disconnect(exception):
            logger.debug("Suppressed expected client disconnect: %s", exception)
            return
        if previous_handler is not None:
            previous_handler(loop, context)
            return
        loop.default_exception_handler(context)

    loop.set_exception_handler(handle_loop_exception)


@app.on_event("shutdown")
async def stop_runtime_on_shutdown() -> None:
    try:
        runtime_service.stop()
    except Exception as exc:  # pragma: no cover - defensive shutdown guard
        logger.warning("Runtime shutdown cleanup failed: %s", exc)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Runtime crash hoặc backend gặp lỗi không mong muốn.",
            "message": str(exc),
            "path": str(request.url.path),
            "code": "internal_error",
        },
    )


def is_expected_client_disconnect(exception: object) -> bool:
    if isinstance(exception, (ConnectionResetError, BrokenPipeError)):
        return True
    if isinstance(exception, OSError):
        return getattr(exception, "winerror", None) in {995, 10053, 10054}
    return False
