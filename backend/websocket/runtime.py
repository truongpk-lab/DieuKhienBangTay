import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.runtime_state import runtime_state

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/runtime")
async def runtime_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(
                {
                    "type": "runtime",
                    "runtime": runtime_state.runtime_payload(),
                    "logs": runtime_state.logs[-20:],
                }
            )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
