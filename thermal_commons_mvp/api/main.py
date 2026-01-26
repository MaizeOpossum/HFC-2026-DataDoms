"""FastAPI app: async handling of sensor streams and market endpoints."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from thermal_commons_mvp.api.dependencies import get_driver, get_order_book, get_trade_execution
from thermal_commons_mvp.api.routes import market, telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop BACnet and trade execution."""
    tex = get_trade_execution()
    await tex.start()
    yield
    await tex.stop()
    get_driver().disconnect()


app = FastAPI(
    title="COOL API",
    description="Cooperative Optimisation of Urban Loads — telemetry and market",
    version="1.0.0-MVP",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
app.include_router(market.router, prefix="/market", tags=["market"])


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "COOL API"}


def main() -> None:
    import uvicorn
    from thermal_commons_mvp.config import get_settings
    s = get_settings()
    uvicorn.run("thermal_commons_mvp.api.main:app", host=s.api_host, port=s.api_port, reload=True)
