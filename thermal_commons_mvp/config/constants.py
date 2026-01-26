"""Constants and literals for COOL."""

from typing import Final

# Default building id used in CityLearn tropical preset
DEFAULT_BUILDING_ID: Final[str] = "Building_5"

# Comfort / setpoint defaults (C)
DEFAULT_COOLING_SETPOINT_C: Final[float] = 24.0
DEFAULT_HEATING_SETPOINT_C: Final[float] = 21.0

# Grid stress levels for demand-response style signals
class GridStressLevel:
    """Grid stress level enum-style constants."""

    LOW: Final[str] = "low"
    MEDIUM: Final[str] = "medium"
    HIGH: Final[str] = "high"
    CRITICAL: Final[str] = "critical"


# Market defaults
DEFAULT_BID_TTL_SEC: Final[int] = 60
DEFAULT_MIN_PRICE: Final[float] = 0.0
DEFAULT_MAX_PRICE: Final[float] = 100.0
