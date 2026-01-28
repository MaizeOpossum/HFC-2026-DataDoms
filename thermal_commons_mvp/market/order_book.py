"""In-memory order book (bids/asks)."""

from datetime import datetime, timezone
from typing import List

from thermal_commons_mvp.models.bids import Ask, Bid, BidStatus
from thermal_commons_mvp.models.trades import OrderBookSnapshot


class OrderBook:
    """In-memory order book for bids and asks."""

    def __init__(self) -> None:
        self._bids: List[Bid] = []
        self._asks: List[Ask] = []

    def add_bid(self, bid: Bid) -> None:
        """Register a new bid (open only)."""
        if bid.status == BidStatus.OPEN:
            self._bids.append(bid)

    def add_ask(self, ask: Ask) -> None:
        """Register a new ask (open only)."""
        if ask.status == BidStatus.OPEN:
            self._asks.append(ask)

    def remove_bid(self, bid_id: str) -> bool:
        """Remove or cancel a bid by id."""
        for i, b in enumerate(self._bids):
            if b.id == bid_id:
                self._bids.pop(i)
                return True
        return False

    def remove_ask(self, ask_id: str) -> bool:
        """Remove or cancel an ask by id."""
        for i, a in enumerate(self._asks):
            if a.id == ask_id:
                self._asks.pop(i)
                return True
        return False

    def update_bid_quantity(self, bid_id: str, new_quantity: float) -> bool:
        """Update bid quantity (for partial fills). Returns True if updated, False if not found."""
        for i, b in enumerate(self._bids):
            if b.id == bid_id:
                if new_quantity <= 0:
                    # Remove if quantity exhausted
                    self._bids.pop(i)
                else:
                    # Replace with updated bid
                    from thermal_commons_mvp.models.bids import Bid, BidStatus, BidType
                    updated_bid = Bid(
                        id=b.id,
                        building_id=b.building_id,
                        price_per_kwh=b.price_per_kwh,
                        quantity_kwh=new_quantity,
                        bid_type=b.bid_type,
                        status=BidStatus.OPEN if new_quantity > 0 else BidStatus.FILLED,
                        created_at=b.created_at,
                        expires_at=b.expires_at,
                    )
                    self._bids[i] = updated_bid
                return True
        return False

    def update_ask_quantity(self, ask_id: str, new_quantity: float) -> bool:
        """Update ask quantity (for partial fills). Returns True if updated, False if not found."""
        for i, a in enumerate(self._asks):
            if a.id == ask_id:
                if new_quantity <= 0:
                    # Remove if quantity exhausted
                    self._asks.pop(i)
                else:
                    # Replace with updated ask
                    from thermal_commons_mvp.models.bids import Ask, BidStatus, BidType
                    updated_ask = Ask(
                        id=a.id,
                        building_id=a.building_id,
                        price_per_kwh=a.price_per_kwh,
                        quantity_kwh=new_quantity,
                        bid_type=a.bid_type,
                        status=BidStatus.OPEN if new_quantity > 0 else BidStatus.FILLED,
                        created_at=a.created_at,
                        expires_at=a.expires_at,
                    )
                    self._asks[i] = updated_ask
                return True
        return False

    def get_bid(self, bid_id: str):
        """Get bid by id, or None if not found."""
        for b in self._bids:
            if b.id == bid_id:
                return b
        return None

    def get_ask(self, ask_id: str):
        """Get ask by id, or None if not found."""
        for a in self._asks:
            if a.id == ask_id:
                return a
        return None

    def open_bids(self) -> List[Bid]:
        """Return open bids (e.g. sorted by price desc for matching)."""
        return [b for b in self._bids if b.status == BidStatus.OPEN]

    def open_asks(self) -> List[Ask]:
        """Return open asks (e.g. sorted by price asc for matching)."""
        return [a for a in self._asks if a.status == BidStatus.OPEN]

    def snapshot(self) -> OrderBookSnapshot:
        """Return current snapshot of the book."""
        return OrderBookSnapshot(
            bids=self.open_bids(),
            asks=self.open_asks(),
            at=datetime.now(timezone.utc),
        )
