"""Live simulation: multiple buildings, telemetry, bidding, matching, carbon."""

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from thermal_commons_mvp.agents.bid_generator import BidGenerator
from thermal_commons_mvp.agents.market_maker import MarketMakerAgent
from thermal_commons_mvp.market.order_book import OrderBook
from thermal_commons_mvp.models.bids import Ask, Bid
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.models.trades import Trade
from thermal_commons_mvp.simulation.grid_stress import GridStressGenerator

# Generate 50 building IDs: Building_01 through Building_50
BUILDING_IDS = [f"Building_{i:02d}" for i in range(1, 51)]
GRID_CYCLE_MINUTES = 4  # short cycle so stress changes visible in demo


def _random_telemetry(building_id: str, step: int) -> Telemetry:
    """Slight random walk so each building behaves differently over time."""
    base_temp = 23.5 + (hash(building_id) % 10) / 10.0
    base_humidity = 55.0 + (hash(building_id + "h") % 15)
    base_power = 45.0 + (hash(building_id + "p") % 25)
    # drift with step so values change each tick
    r = random.Random(step + hash(building_id))
    temp = base_temp + (r.random() - 0.5) * 2.0
    humidity = base_humidity + (r.random() - 0.5) * 10.0
    power = max(10.0, base_power + (r.random() - 0.5) * 20.0)
    return Telemetry(
        building_id=building_id,
        temp_c=round(temp, 1),
        humidity_pct=round(humidity, 0),
        power_load_kw=round(power, 1),
    )


def _match_orders(book: OrderBook) -> List[Trade]:
    """Match best bid vs best ask (different buildings); return new trades."""
    trades: List[Trade] = []
    bids = sorted(book.open_bids(), key=lambda b: b.price_per_kwh, reverse=True)
    asks = sorted(book.open_asks(), key=lambda a: a.price_per_kwh)
    for bid in bids:
        for ask in asks:
            if bid.building_id == ask.building_id:
                continue
            if bid.price_per_kwh < ask.price_per_kwh:
                continue
            qty = min(bid.quantity_kwh, ask.quantity_kwh)
            if qty <= 0:
                continue
            trade = Trade(
                id=f"trade-{uuid.uuid4().hex[:8]}",
                bid_id=bid.id,
                ask_id=ask.id,
                price_per_kwh=(bid.price_per_kwh + ask.price_per_kwh) / 2.0,
                quantity_kwh=qty,
                executed_at=datetime.now(timezone.utc),
            )
            trades.append(trade)
            book.remove_bid(bid.id)
            book.remove_ask(ask.id)
            asks = [a for a in asks if a.id != ask.id]
            break
    return trades


def make_initial_state() -> Dict[str, Any]:
    """State dict for st.session_state: telemetry, book, trades, carbon, grid, step, history."""
    return {
        "telemetry": {b: _random_telemetry(b, 0) for b in BUILDING_IDS},
        "order_book": OrderBook(),
        "trades": [],
        "total_kwh_saved": 0.0,
        "grid_stress": "low",
        "step_count": 0,
        "grid_gen": GridStressGenerator(cycle_minutes=GRID_CYCLE_MINUTES),
        "agents": {
            b: MarketMakerAgent(
                b,
                bid_generator=BidGenerator(building_id=b, use_ai=True)
            )
            for b in BUILDING_IDS
        },
        "history": [],  # Store historical data for time series
        "max_history": 100,  # Keep last 100 steps
        "bid_to_building": {},  # Mapping bid_id -> building_id
        "ask_to_building": {},  # Mapping ask_id -> building_id
    }


def step(state: Dict[str, Any]) -> None:
    """Advance one simulation tick: update telemetry, submit orders, match, update carbon."""
    state["step_count"] = state.get("step_count", 0) + 1
    step_n = state["step_count"]
    grid_gen: GridStressGenerator = state.get("grid_gen") or GridStressGenerator(cycle_minutes=GRID_CYCLE_MINUTES)
    state["grid_gen"] = grid_gen
    grid_signal = grid_gen.get_signal()
    state["grid_stress"] = grid_signal.level

    agents = state.get("agents")
    if agents is None:
        state["agents"] = {
            b: MarketMakerAgent(
                b,
                bid_generator=BidGenerator(building_id=b, use_ai=True)
            )
            for b in BUILDING_IDS
        }
        agents = state["agents"]

    # Fresh book each step so we only match this tick’s orders
    book = OrderBook()
    state["order_book"] = book
    telemetry: Dict[str, Telemetry] = {}

    # Pass trade history to agents for AI learning
    recent_trades = state.get("trades", [])[-20:]  # Last 20 trades for context
    ai_reasoning: Dict[str, str] = {}
    
    # Track bid_id/ask_id -> building_id mapping for trade display
    bid_to_building: Dict[str, str] = state.get("bid_to_building", {})
    ask_to_building: Dict[str, str] = state.get("ask_to_building", {})
    
    for b in BUILDING_IDS:
        t = _random_telemetry(b, step_n)
        telemetry[b] = t
        bid_order, ask_order = agents[b].submit_orders(t, grid_signal, trade_history=recent_trades)
        book.add_bid(bid_order)
        book.add_ask(ask_order)
        # Store mapping for trade display
        bid_to_building[bid_order.id] = bid_order.building_id
        ask_to_building[ask_order.id] = ask_order.building_id
        # Capture AI reasoning
        reasoning = agents[b].get_ai_reasoning()
        if reasoning:
            ai_reasoning[b] = reasoning
    
    # Store mappings in state
    state["bid_to_building"] = bid_to_building
    state["ask_to_building"] = ask_to_building
    state["ai_reasoning"] = ai_reasoning

    state["telemetry"] = telemetry
    new_trades = _match_orders(book)
    state["trades"] = state.get("trades", []) + new_trades
    state["total_kwh_saved"] = state.get("total_kwh_saved", 0.0) + sum(t.quantity_kwh for t in new_trades)
    
    # Store historical snapshot for time series
    history = state.get("history", [])
    history.append({
        "step": step_n,
        "timestamp": datetime.now(timezone.utc),
        "telemetry": telemetry,
        "grid_stress": grid_signal.level,
    })
    # Keep only last N steps
    max_history = state.get("max_history", 100)
    state["history"] = history[-max_history:]
