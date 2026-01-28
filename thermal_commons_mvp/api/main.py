"""FastAPI app: async handling of sensor streams and market endpoints."""

from contextlib import asynccontextmanager
from typing import Any, List

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from thermal_commons_mvp.api.dependencies import get_driver, get_order_book, get_trade_execution
from thermal_commons_mvp.api.middleware import RateLimitMiddleware
from thermal_commons_mvp.api.routes import market, telemetry
from thermal_commons_mvp.config import get_settings


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

# Configure CORS based on settings
settings = get_settings()

# Parse CORS origins
if settings.cors_origins == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

# Parse CORS methods
if settings.cors_allow_methods == "*":
    cors_methods = ["*"]
else:
    cors_methods = [method.strip() for method in settings.cors_allow_methods.split(",")]

# Parse CORS headers
if settings.cors_allow_headers == "*":
    cors_headers = ["*"]
else:
    cors_headers = [header.strip() for header in settings.cors_allow_headers.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

# Add rate limiting middleware
if settings.rate_limit_per_minute > 0:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
app.include_router(market.router, prefix="/market", tags=["market"])


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "COOL API"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Avoid browser 404 for automatic favicon requests."""
    return Response(status_code=204)


def main() -> None:
    import uvicorn
    from thermal_commons_mvp.config import get_settings
    s = get_settings()
    uvicorn.run("thermal_commons_mvp.api.main:app", host=s.api_host, port=s.api_port, reload=True)
