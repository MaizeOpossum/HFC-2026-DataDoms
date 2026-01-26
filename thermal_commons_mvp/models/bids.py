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
