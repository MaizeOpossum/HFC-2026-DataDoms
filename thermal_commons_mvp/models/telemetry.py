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
        """Validate telemetry values and set default timestamp."""
        # Validate temperature range (15-35°C for Singapore buildings)
        if not (15.0 <= self.temp_c <= 35.0):
            raise ValueError(f"temp_c must be between 15.0 and 35.0°C, got {self.temp_c}")
        
        # Validate humidity range (0-100%)
        if not (0.0 <= self.humidity_pct <= 100.0):
            raise ValueError(f"humidity_pct must be between 0.0 and 100.0%, got {self.humidity_pct}")
        
        # Validate power (must be non-negative)
        if self.power_load_kw < 0.0:
            raise ValueError(f"power_load_kw must be non-negative, got {self.power_load_kw}")
        
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc))
