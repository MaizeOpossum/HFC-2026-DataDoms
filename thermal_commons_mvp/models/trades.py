"""Trade and order-book snapshot models."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from thermal_commons_mvp.models.bids import Ask, Bid


@dataclass(frozen=True)
class Trade:
    """Executed trade between a bid and an ask."""

    id: str
    bid_id: str
    ask_id: str
    price_per_kwh: float
    quantity_kwh: float
    executed_at: Optional[datetime] = None


@dataclass(frozen=True)
class OrderBookSnapshot:
    """Snapshot of current bids and asks."""

    bids: List[Bid]
    asks: List[Ask]
    at: Optional[datetime] = None
