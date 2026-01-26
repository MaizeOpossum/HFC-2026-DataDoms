"""Grid stress and demand-response signals."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class GridStressSignal:
    """Demand-response style grid stress event."""

    level: str  # low, medium, high, critical
    value: float  # normalised or raw metric
    starts_at: datetime
    ends_at: Optional[datetime] = None


class GridStressLevel:
    """Grid stress level labels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
