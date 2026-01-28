"""Application settings loaded from environment."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """COOL app settings from env or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # BACnet
    bacnet_ip: Optional[str] = None
    bacnet_port: int = 47808
    bms_poll_interval_sec: int = 10

    # CityLearn
    citylearn_schema_path: Optional[Path] = None
    citylearn_building_id: str = "Building_5"

    # Logging
    log_level: str = "INFO"

    # Carbon (Singapore grid example, kg CO2 per kWh)
    carbon_factor_kg_per_kwh: float = 0.4083

    # Mapbox (reads from MAPBOX_ACCESS_TOKEN env var)
    mapbox_access_token: Optional[str] = None

    # Dashboard
    dashboard_refresh_seconds: int = 3

    # Simulation
    grid_cycle_minutes: int = 4  # short cycle so stress changes visible in demo

    # API Security
    cors_origins: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"  # Comma-separated list or "*" for all
    cors_allow_headers: str = "*"  # Comma-separated list or "*" for all
    api_key: Optional[str] = None  # API key for authentication (optional)
    rate_limit_per_minute: int = 60  # Requests per minute per IP

    # Persistence
    enable_persistence: bool = True  # Enable SQLite persistence
    db_path: Optional[str] = None  # Custom database path (defaults to data/cool_state.db)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
