"""Unit tests for OrderBook."""

import uuid
from thermal_commons_mvp.models.bids import Ask, Bid, BidStatus, BidType
from thermal_commons_mvp.market.order_book import OrderBook


def test_add_bid_and_snapshot() -> None:
    ob = OrderBook()
    bid = Bid(
        id="b1",
        building_id="B1",
        price_per_kwh=10.0,
        quantity_kwh=5.0,
        bid_type=BidType.BUY,
        status=BidStatus.OPEN,
    )
    ob.add_bid(bid)
    snap = ob.snapshot()
    assert len(snap.bids) == 1
    assert snap.bids[0].id == "b1"


def test_remove_bid() -> None:
    ob = OrderBook()
    bid = Bid(
        id="b2",
        building_id="B1",
        price_per_kwh=10.0,
        quantity_kwh=5.0,
        bid_type=BidType.BUY,
        status=BidStatus.OPEN,
    )
    ob.add_bid(bid)
    assert ob.remove_bid("b2") is True
    assert ob.remove_bid("b2") is False
    assert len(ob.snapshot().bids) == 0
