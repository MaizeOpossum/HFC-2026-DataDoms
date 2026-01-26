"""Simple order-matching engine (asyncio.Queue-based)."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import uuid

from thermal_commons_mvp.models.bids import Ask, Bid, BidStatus
from thermal_commons_mvp.models.trades import Trade
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class TradeExecution:
    """
    Simple order-matching engine using asyncio.Queue for incoming orders.
    Matches bids vs asks by price (bid >= ask) and quantity.
    """

    def __post_init__(self) -> None:
        self._queue: asyncio.Queue[tuple[Bid, Ask]] = asyncio.Queue()
        self._trades: List[Trade] = []
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start background matching loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._match_loop())
        logger.info("TradeExecution matching loop started")

    async def stop(self) -> None:
        """Stop matching loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None

    def submit(self, bid: Bid, ask: Ask) -> None:
        """Submit a bid/ask pair for matching (e.g. when bid.price >= ask.price)."""
        self._queue.put_nowait((bid, ask))

    async def _match_loop(self) -> None:
        """Consume queue and record trades."""
        while self._running:
            try:
                bid, ask = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                qty = min(bid.quantity_kwh, ask.quantity_kwh)
                price = (bid.price_per_kwh + ask.price_per_kwh) / 2.0
                trade = Trade(
                    id=f"trade-{uuid.uuid4().hex[:8]}",
                    bid_id=bid.id,
                    ask_id=ask.id,
                    price_per_kwh=price,
                    quantity_kwh=qty,
                    executed_at=datetime.now(timezone.utc),
                )
                self._trades.append(trade)
                logger.info("Trade %s: bid=%s ask=%s qty=%.2f price=%.2f", trade.id, bid.id, ask.id, qty, price)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Match loop error: %s", e)

    def get_trades(self) -> List[Trade]:
        """Return list of executed trades."""
        return list(self._trades)
