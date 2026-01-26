"""Unit tests for BidGenerator."""

import pytest
from thermal_commons_mvp.agents.bid_generator import BidGenerator
from thermal_commons_mvp.models.bids import Ask, Bid, BidType


def test_generate_ask_returns_ask(sample_telemetry) -> None:
    gen = BidGenerator(building_id="B1")
    ask = gen.generate_ask(sample_telemetry)
    assert isinstance(ask, Ask)
    assert ask.building_id == "B1"
    assert ask.bid_type == BidType.SELL
    assert ask.quantity_kwh >= 0
    assert ask.price_per_kwh > 0


def test_generate_bid_returns_bid(sample_telemetry) -> None:
    gen = BidGenerator(building_id="B1")
    bid = gen.generate_bid(sample_telemetry)
    assert isinstance(bid, Bid)
    assert bid.building_id == "B1"
    assert bid.bid_type == BidType.BUY
    assert bid.quantity_kwh >= 0
