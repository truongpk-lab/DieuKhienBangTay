"""FastAPI app for Phase 18 backend/frontend integration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import gestures, health, models, profiles, runtime, training
from backend.websocket import runtime as runtime_ws

app = FastAPI(title="ACV Gesture Control API", version="0.18.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(runtime.router)
app.include_router(profiles.router)
app.include_router(gestures.router)
app.include_router(training.router)
app.include_router(models.router)
app.include_router(runtime_ws.router)
