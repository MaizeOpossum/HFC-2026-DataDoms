"""Submit bid/ask, order book snapshot, trade history."""

from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from thermal_commons_mvp.api.dependencies import get_order_book, get_trade_execution
from thermal_commons_mvp.models.bids import BidStatus

router = APIRouter()


class BidSubmit(BaseModel):
    building_id: str
    price_per_kwh: float
    quantity_kwh: float
    side: str = "buy"


class AskSubmit(BaseModel):
    building_id: str
    price_per_kwh: float
    quantity_kwh: float


@router.get("/book")
def order_book_snapshot(
    ob=Depends(get_order_book),
) -> dict[str, Any]:
    """Return current order book snapshot."""
    snap = ob.snapshot()
    return {
        "bids": [{"id": b.id, "building_id": b.building_id, "price_per_kwh": b.price_per_kwh, "quantity_kwh": b.quantity_kwh} for b in snap.bids],
        "asks": [{"id": a.id, "building_id": a.building_id, "price_per_kwh": a.price_per_kwh, "quantity_kwh": a.quantity_kwh} for a in snap.asks],
        "at": snap.at.isoformat() if snap.at else None,
    }


@router.get("/trades")
def trade_history(tex=Depends(get_trade_execution)) -> dict[str, List[dict[str, Any]]]:
    """Return executed trades."""
    trades = tex.get_trades()
    return {
        "trades": [
            {
                "id": t.id,
                "bid_id": t.bid_id,
                "ask_id": t.ask_id,
                "price_per_kwh": t.price_per_kwh,
                "quantity_kwh": t.quantity_kwh,
                "executed_at": t.executed_at.isoformat() if t.executed_at else None,
            }
            for t in trades
        ]
    }


@router.post("/bid")
def submit_bid(
    body: BidSubmit,
    ob=Depends(get_order_book),
) -> dict[str, str]:
    """Register a new bid (stub: stores in memory)."""
    from thermal_commons_mvp.models.bids import Bid, BidType
    import uuid
    bid = Bid(
        id=f"bid-{uuid.uuid4().hex[:8]}",
        building_id=body.building_id,
        price_per_kwh=body.price_per_kwh,
        quantity_kwh=body.quantity_kwh,
        bid_type=BidType.BUY,
        status=BidStatus.OPEN,
        created_at=datetime.now(timezone.utc),
    )
    ob.add_bid(bid)
    return {"id": bid.id, "status": "open"}


@router.post("/ask")
def submit_ask(
    body: AskSubmit,
    ob=Depends(get_order_book),
) -> dict[str, str]:
    """Register a new ask (stub: stores in memory)."""
    from thermal_commons_mvp.models.bids import Ask, BidType
    import uuid
    ask = Ask(
        id=f"ask-{uuid.uuid4().hex[:8]}",
        building_id=body.building_id,
        price_per_kwh=body.price_per_kwh,
        quantity_kwh=body.quantity_kwh,
        bid_type=BidType.SELL,
        status=BidStatus.OPEN,
        created_at=datetime.now(timezone.utc),
    )
    ob.add_ask(ask)
    return {"id": ask.id, "status": "open"}
