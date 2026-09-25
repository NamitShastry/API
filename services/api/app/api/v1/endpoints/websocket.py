"""WebSocket endpoint streaming sub-second INDEX_TICK and QUOTE_TICKER events."""

from __future__ import annotations

import asyncio
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.engine.flash_engine import FlashEngine
from app.services.pipeline_service import PipelineService

router = APIRouter(tags=["Real-Time Streaming"])


class ConnectionManager:
    """Manages active WebSocket client connections and message broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


ws_manager = ConnectionManager()


# Connect FLASH engine and PipelineService subscribers to ws_manager broadcast
async def _on_index_tick(tick_data: dict):
    await ws_manager.broadcast_json(tick_data)


async def _on_quote_ticker(quote_data: dict):
    await ws_manager.broadcast_json(quote_data)


FlashEngine.register_subscriber(_on_index_tick)
PipelineService.register_ticker_subscriber(_on_quote_ticker)


@router.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """Real-time streaming channel for live index ticks and fare quote ticker events."""
    await ws_manager.connect(websocket)

    # Immediately push the latest state upon connection
    initial_tick = FlashEngine.get_latest_tick().model_dump()
    await websocket.send_json(initial_tick)

    try:
        while True:
            # Client can send ping or subscription filter messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
