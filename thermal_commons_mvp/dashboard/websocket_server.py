"""
Standalone WebSocket server: runs simulation in a background thread and broadcasts
trade_executed events to all connected clients. Run with:
  python -m thermal_commons_mvp.dashboard.websocket_server
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager
from queue import Queue
from typing import Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.dashboard.event_bus import TRADE_EXECUTED, get_event_bus
from thermal_commons_mvp.dashboard.simulation_engine import make_initial_state, step

logger = logging.getLogger(__name__)

# In-process queue: sim thread pushes (topic, payload), broadcast task consumes
_broadcast_queue: Queue = Queue()
_connections: Set[WebSocket] = set()


def _on_trade_executed(topic: str, payload: Any) -> None:
    _broadcast_queue.put({"type": topic, "data": payload})


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_event_bus().subscribe(TRADE_EXECUTED, _on_trade_executed)
    settings = get_settings()
    interval = max(0.5, float(settings.dashboard_refresh_seconds))

    def run_sim_loop() -> None:
        state = make_initial_state()
        while True:
            step(state)
            time.sleep(interval)

    sim_thread = threading.Thread(target=run_sim_loop, daemon=True)
    sim_thread.start()
    broadcast_task = asyncio.create_task(_broadcast_worker())
    logger.info("WebSocket server: simulation thread started (interval=%.1fs)", interval)

    yield

    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass
    get_event_bus().unsubscribe(TRADE_EXECUTED, _on_trade_executed)


app = FastAPI(title="COOL WebSocket", lifespan=lifespan)


@app.websocket("/ws/trades")
async def ws_trades(websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _connections.discard(websocket)


async def _broadcast_worker() -> None:
    loop = asyncio.get_event_loop()
    while True:
        try:
            msg = await loop.run_in_executor(None, _broadcast_queue.get)
            dead = set()
            for ws in _connections:
                try:
                    await ws.send_json(msg)
                except Exception:
                    dead.add(ws)
            for ws in dead:
                _connections.discard(ws)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("Broadcast worker error: %s", e)


def run() -> None:
    import uvicorn
    s = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=s.api_port + 1, log_level="info")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
