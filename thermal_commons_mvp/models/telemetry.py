"""Telemetry and sensor readings."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class Telemetry:
    """Single building telemetry: temp, humidity, power_load."""

    building_id: str
    temp_c: float
    humidity_pct: float
    power_load_kw: float
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc))
