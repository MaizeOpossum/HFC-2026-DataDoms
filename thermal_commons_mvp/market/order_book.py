"""In-memory order book (bids/asks)."""

from datetime import datetime
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
