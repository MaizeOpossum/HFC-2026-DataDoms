"""Bid and ask models for the energy market."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class BidType(str, Enum):
    """Side of the order."""

    BUY = "buy"
    SELL = "sell"


class BidStatus(str, Enum):
    """Lifecycle of a bid/ask."""

    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Bid:
    """Buy-side order: willingness to pay for load reduction or capacity."""

    id: str
    building_id: str
    price_per_kwh: float
    quantity_kwh: float
    bid_type: BidType = BidType.BUY
    status: BidStatus = BidStatus.OPEN
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate bid values."""
        if self.price_per_kwh <= 0:
            raise ValueError(f"price_per_kwh must be positive, got {self.price_per_kwh}")
        if self.quantity_kwh <= 0:
            raise ValueError(f"quantity_kwh must be positive, got {self.quantity_kwh}")


@dataclass(frozen=True)
class Ask:
    """Sell-side order: offer to shed load or provide capacity."""

    id: str
    building_id: str
    price_per_kwh: float
    quantity_kwh: float
    bid_type: BidType = BidType.SELL
    status: BidStatus = BidStatus.OPEN
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate ask values."""
        if self.price_per_kwh <= 0:
            raise ValueError(f"price_per_kwh must be positive, got {self.price_per_kwh}")
        if self.quantity_kwh <= 0:
            raise ValueError(f"quantity_kwh must be positive, got {self.quantity_kwh}")
