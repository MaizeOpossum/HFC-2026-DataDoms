# COOL — Dashboard & AI Agentic Backend Plan

**Single source of truth** for the clean, modern dashboard and the AI agentic backend that handles trades between buildings. All planning docs and `architecture.json` align with this plan.

---

## Vision

- **Clean, modern dashboard**: Dark theme, glassmorphism, smooth animations, real-time feedback.
- **AI agentic backend**: 50 autonomous agents (one per building) that negotiate and execute energy trades between buildings.
- **Inter-building trades**: Order book, matching engine, and trade execution orchestrated by the simulation engine; agents submit bids/asks based on telemetry, grid stress, and learned history.

---

## Canonical Reference

- **Architecture (technical)**: [`architecture.json`](./architecture.json) — layers, components, data flow, implementation plan.
- **Codebase layout**: [`CODEBASE_PLAN.md`](./CODEBASE_PLAN.md) — package/module breakdown and mapping to architecture.
- **Telemetry**: [`TELEMETRY_CURRENT_IMPLEMENTATION.md`](./TELEMETRY_CURRENT_IMPLEMENTATION.md) — how telemetry is received today and how it will plug into the new architecture.

---

## AI Agentic Backend (Trades Between Buildings)

### Responsibilities

1. **Per-building agents**  
   One `MarketMakerAgent` per building. Each agent:
   - Receives **telemetry** (temp, humidity, power) and **grid stress**.
   - Uses **AIDecisionEngine** to choose strategy and generate bid/ask.
   - Submits orders into a **shared order book**.
   - Learns from **trade history** (success rate, prices) and adapts.

2. **Trade execution**  
   - **Order book** aggregates bids and asks from all buildings.
   - **Matching** runs each simulation step: best bid vs best ask (different buildings), partial fill supported.
   - **Trades** are recorded, carbon savings aggregated, and published to the **event bus** for real-time UI (WebSocket server subscribes and broadcasts when run).

3. **Agent intelligence**  
   - **AIDecisionEngine**: Four strategies — aggressive, conservative, opportunistic, adaptive.
   - **BidGenerator**: Builds `Bid`/`Ask` from AI output or rule-based fallback.
   - **Learning**: Strategy and pricing adapt using recent trade outcomes and context.

### Key Modules

| Layer / concern        | Location | Role |
|------------------------|----------|------|
| Agent interface        | `agents/base_agent.py` | `act(obs) -> action` |
| Market-making agents  | `agents/market_maker.py` | One per building; `submit_orders(telemetry, grid_signal, trade_history)` |
| Bid/ask generation     | `agents/bid_generator.py` | Willingness to trade → Bid/Ask |
| AI decision engine    | `agents/ai_decision_engine.py` | Strategy selection, pricing, reasoning, learning |
| Order book & matching  | `market/order_book.py` | Central book; matching in `simulation_engine._match_orders()` |
| Simulation orchestration | `dashboard/simulation_engine.py` | `step()`: telemetry → agents → book → match → trades |

### Data Flow (Trades Between Buildings)

```
Telemetry (per building) + Grid stress + Trade history
    → Agent.submit_orders()
    → BidGenerator / AIDecisionEngine
    → Bid & Ask into OrderBook
    → _match_orders() → Trades (buyer building ↔ seller building)
    → state["trades"], carbon savings, event_bus.publish(trade_executed) → WebSocket when server running
```

---

## Clean, Modern Dashboard

### Current Stack

- **Streamlit** app: carbon counter, building bar chart, time series, district map, **Agent Network** viz, trade log.
- **District map**: Static PyDeck map; buildings as points (real locations).
- **Agent Network**: HTML/Canvas below the map; ring of building nodes; moving points for trades (seller→buyer); labels on click; flight-detail style info.
- **Refresh**: `@st.fragment(run_every=REFRESH_SECONDS)` (e.g. 3s). Charts and metrics update on refresh; animations are client-side but impacted by iframe recreation.

### Target Stack (from architecture.json)

- **Metrics/charts**: Keep Streamlit; periodic refresh (e.g. 3–5s) is acceptable.
- **Real-time animations**: WebSocket + React component for the Agent Network; trade events pushed so animations don’t depend on Streamlit refresh.
- **Event pipeline**: Simulation engine → event bus → WebSocket → React; optional telemetry stream for live building state.

### Design Principles

- **Theme**: Dark mode, glassmorphism, cyan–red gradients for energy flow.
- **Behaviour**: Real-time feedback for trades; progressive disclosure; smooth, non-janky motion where possible.
- **Consistency**: All planning docs and `architecture.json` describe this same dashboard and backend.

---

## Telemetry

- **In-dashboard simulation today**: Mock data via `_random_telemetry()` in `simulation_engine.py` (no real BMS).
- **API**: BACnet driver in `interface/bacnet_driver.py` used by `GET /telemetry/{building_id}`; currently stubbed/mock.
- **Target**: Single configurable source (BACnet vs mock); simulation engine able to consume BACnet when enabled; telemetry events and WebSocket stream as in `architecture.json` and `TELEMETRY_CURRENT_IMPLEMENTATION.md`.

---

## Planning Docs — How They Relate

| Document | Role |
|----------|------|
| **DASHBOARD_AND_AGENTS_PLAN.md** (this file) | Master plan: clean modern dashboard + AI agentic backend handling trades between buildings. |
| **architecture.json** | Technical architecture: layers, components, events, implementation phases. |
| **CODEBASE_PLAN.md** | Package/module layout and mapping to architecture. |
| **TELEMETRY_CURRENT_IMPLEMENTATION.md** | How telemetry is received and how it ties into the architecture. |

---

## Implementation Status (Summary)

- **Done**: 50 agents, OrderBook, matching, AIDecisionEngine (4 strategies), BidGenerator, MarketMakerAgent, Streamlit dashboard (carbon, charts, static map, Agent Network HTML/Canvas, trade log), mock telemetry, BACnet API (stubbed), **event bus** (`dashboard/event_bus.py`), **trade-event publishing** from `simulation_engine.step()`, **WebSocket server** (`dashboard/websocket_server.py`, run with `python -m thermal_commons_mvp.dashboard.websocket_server` or `cool-ws`).
- **Removed**: Deprecated animated map component, `district_map_new`, superseded planning MDs (animation/map options).
- **Planned** (see `architecture.json`): React Agent Network component with WebSocket client, telemetry integration into simulation, optional BACnet-driven simulation mode.

All planning Markdown files are kept **consistent** with this plan and with `architecture.json`.
