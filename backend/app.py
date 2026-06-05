"""FastAPI app for Phase 18 backend/frontend integration."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import ai, app_control, calibration, cameras, gestures, health, mic, models, profiles, runtime, settings, training
from backend.websocket import runtime as runtime_ws

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
