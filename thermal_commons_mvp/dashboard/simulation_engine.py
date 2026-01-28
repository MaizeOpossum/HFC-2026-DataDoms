"""Live simulation: multiple buildings, telemetry, bidding, matching, carbon."""

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from thermal_commons_mvp.agents.bid_generator import BidGenerator
from thermal_commons_mvp.agents.market_maker import MarketMakerAgent
from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.market.order_book import OrderBook
from thermal_commons_mvp.models.bids import Ask, Bid
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.models.trades import Trade
from thermal_commons_mvp.persistence.database import StateDatabase
from thermal_commons_mvp.simulation.grid_stress import GridStressGenerator

from thermal_commons_mvp.dashboard.event_bus import get_event_bus, TRADE_EXECUTED

# Generate 50 building IDs: Building_01 through Building_50
BUILDING_IDS = [f"Building_{i:02d}" for i in range(1, 51)]


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
    """Match best bid vs best ask (different buildings); return new trades with partial fill support."""
    trades: List[Trade] = []
    bids = sorted(book.open_bids(), key=lambda b: b.price_per_kwh, reverse=True)
    asks = sorted(book.open_asks(), key=lambda a: a.price_per_kwh)
    
    # Track which orders we've already processed to avoid double-matching
    processed_bid_ids = set()
    processed_ask_ids = set()
    
    for bid in bids:
        if bid.id in processed_bid_ids:
            continue
            
        for ask in asks:
            if ask.id in processed_ask_ids:
                continue
                
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
            
            # Update quantities for partial fills
            remaining_bid_qty = bid.quantity_kwh - qty
            remaining_ask_qty = ask.quantity_kwh - qty
            
            if remaining_bid_qty <= 0:
                book.remove_bid(bid.id)
                processed_bid_ids.add(bid.id)
            else:
                book.update_bid_quantity(bid.id, remaining_bid_qty)
                processed_bid_ids.add(bid.id)
            
            if remaining_ask_qty <= 0:
                book.remove_ask(ask.id)
                processed_ask_ids.add(ask.id)
            else:
                book.update_ask_quantity(ask.id, remaining_ask_qty)
                processed_ask_ids.add(ask.id)
            
            # Update asks list to reflect changes
            asks = book.open_asks()
            break
    return trades


def make_initial_state() -> Dict[str, Any]:
    """State dict for st.session_state: telemetry, book, trades, carbon, grid, step, history."""
    settings = get_settings()
    
    # Initialize database if persistence is enabled
    db = None
    if settings.enable_persistence:
        from pathlib import Path
        db_path = Path(settings.db_path) if settings.db_path else None
        db = StateDatabase(db_path=db_path)
        
        # Load only last 50 trades for performance (reduced from 1000)
        recent_trades = db.get_trades(limit=50)
        recent_history = db.get_recent_history(limit=50)
    else:
        recent_trades = []
        recent_history = []
    
    # Pre-create agents once (cached for performance)
    agents = {
        b: MarketMakerAgent(
            b,
            bid_generator=BidGenerator(building_id=b, use_ai=True)
        )
        for b in BUILDING_IDS
    }
    
    return {
        "telemetry": {b: _random_telemetry(b, 0) for b in BUILDING_IDS},
        "order_book": OrderBook(),
        "trades": recent_trades,
        "total_kwh_saved": sum(t.quantity_kwh for t in recent_trades) if recent_trades else 0.0,
        "grid_stress": "low",
        "step_count": recent_history[-1]["step"] if recent_history else 0,
        "grid_gen": GridStressGenerator(cycle_minutes=settings.grid_cycle_minutes),
        "agents": agents,  # Reuse agents across steps for performance
        "history": recent_history,  # Store historical data for time series
        "max_history": 50,  # Reduced from 100 for performance
        "bid_to_building": {},  # Mapping bid_id -> building_id
        "ask_to_building": {},  # Mapping ask_id -> building_id
        "new_trades": [],  # New trades from current cycle
        "db": db,  # Database instance for persistence
    }


def step(state: Dict[str, Any]) -> None:
    """Advance one simulation tick: update telemetry, submit orders, match, update carbon."""
    state["step_count"] = state.get("step_count", 0) + 1
    step_n = state["step_count"]
    settings = get_settings()
    grid_gen: GridStressGenerator = state.get("grid_gen") or GridStressGenerator(cycle_minutes=settings.grid_cycle_minutes)
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

    # Pass only last 10 trades for context (reduced from 20 for performance)
    recent_trades = state.get("trades", [])[-10:]
    ai_reasoning: Dict[str, str] = {}
    
    # Track bid_id/ask_id -> building_id mapping for trade display
    bid_to_building: Dict[str, str] = {}
    ask_to_building: Dict[str, str] = {}
    
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
    
    # Keep only last 100 trades in memory (prevent unbounded growth)
    all_trades = state.get("trades", []) + new_trades
    state["trades"] = all_trades[-100:]
    state["new_trades"] = new_trades  # Store new trades for this cycle
    state["total_kwh_saved"] = state.get("total_kwh_saved", 0.0) + sum(t.quantity_kwh for t in new_trades)

    # Only publish events if there are new trades (optimization)
    if new_trades:
        bus = get_event_bus()
        for t in new_trades:
            seller_bid = ask_to_building.get(t.ask_id, "")
            buyer_bid = bid_to_building.get(t.bid_id, "")
            bus.publish(TRADE_EXECUTED, {
                "trade_id": t.id,
                "bid_id": t.bid_id,
                "ask_id": t.ask_id,
                "quantity_kwh": t.quantity_kwh,
                "price_per_kwh": t.price_per_kwh,
                "executed_at": t.executed_at.isoformat() if t.executed_at else None,
                "seller_building_id": seller_bid,
                "buyer_building_id": buyer_bid,
                "agent_reasoning_seller": ai_reasoning.get(seller_bid),
                "agent_reasoning_buyer": ai_reasoning.get(buyer_bid),
            })

        # Persist trades to database only if enabled and there are new trades
        db = state.get("db")
        if db:
            try:
                db.save_trades(new_trades)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to persist trades: {e}")
    
    # Store historical snapshot for time series
    history = state.get("history", [])
    history_entry = {
        "step": step_n,
        "timestamp": datetime.now(timezone.utc),
        "telemetry": telemetry,
        "grid_stress": grid_signal.level,
    }
    history.append(history_entry)
    # Keep only last N steps
    max_history = state.get("max_history", 50)
    state["history"] = history[-max_history:]
    
    # Persist history snapshot less frequently (every 5 steps) for performance
    db = state.get("db")
    if db and step_n % 5 == 0:
        try:
            db.save_history_snapshot(
                step=step_n,
                timestamp=datetime.now(timezone.utc),
                telemetry=telemetry,
                grid_stress=grid_signal.level,
                total_kwh_saved=state["total_kwh_saved"],
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to persist history snapshot: {e}")
