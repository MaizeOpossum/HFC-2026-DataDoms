# COOL — Cooperative Optimisation of Urban Loads

**Mission:** Deploy a decentralised agentic cooling swarm for Singapore commercial buildings.  
**Target metric:** Maximise Carbon ROI via inter-building energy trading.

This repo implements a **clean, modern dashboard** and an **AI agentic backend** that handles trades between buildings.  
**Canonical planning:** [`architecture.json`](architecture.json) and [`DASHBOARD_AND_AGENTS_PLAN.md`](DASHBOARD_AND_AGENTS_PLAN.md). Codebase layout: [`CODEBASE_PLAN.md`](CODEBASE_PLAN.md).

## Structure

```
thermal_commons_mvp/
├── config/         # Settings (Pydantic), constants
├── models/         # Telemetry, Bid/Ask, Trade, GridStress
├── simulation/     # CityLearn gym, grid stress generator
├── interface/      # BACnet BMS driver (BAC0)
├── agents/         # BaseAgent, MarketMaker, BidGenerator, AIDecisionEngine
├── market/         # OrderBook (matching in simulation_engine)
├── api/            # FastAPI: telemetry & market routes
├── dashboard/      # Streamlit app, simulation_engine, event_bus, websocket_server; carbon, charts, map, Agent Network, trade log
└── utils/          # CarbonCalculator, logging
tests/
├── unit/
└── integration/
```

## Setup

Requires **Python 3.10+**.

```bash
# From project root
pip install -e ".[dev]"
cp .env.example .env   # edit as needed
```

**Optional — CityLearn simulation:** The default install runs the sim in **mock mode** (no CityLearn). For real CityLearn environments, use a **separate virtualenv** and `pip install -e ".[simulation]"` there, since CityLearn pins older gymnasium/pandas.

## Run

From the **project root** (parent of `thermal_commons_mvp/`), with the package on `PYTHONPATH` or installed (`pip install -e .`):

| Component   | Command |
|------------|---------|
| **Simulation** | `python -m thermal_commons_mvp.simulation.city_gym` or `cool-sim` |
| **API**        | `uvicorn thermal_commons_mvp.api.main:app --reload` or `cool-api` |
| **Dashboard**  | `streamlit run thermal_commons_mvp/dashboard/app.py` or `cool-dash` |
| **WebSocket**  | `python -m thermal_commons_mvp.dashboard.websocket_server` or `cool-ws` (broadcasts trade events on `/ws/trades`, port `api_port+1`) |

## Test

```bash
# Unit tests (no FastAPI/CityLearn/BAC0 required for most)
PYTHONPATH=. pytest tests/unit/ -v

# All tests (install deps first: pip install -e ".[dev]" plus project deps)
PYTHONPATH=. pytest tests/ -v
```

## Practices

- **Config:** `config.settings` from env/`.env`; constants in `config.constants`.
- **Types:** Type hints on public APIs; Pydantic/dataclasses for DTOs.
- **Logging:** `get_logger(__name__)` from `utils.logging_utils`.
- **Time:** `datetime.now(timezone.utc)` for timestamps.

See [`DASHBOARD_AND_AGENTS_PLAN.md`](DASHBOARD_AND_AGENTS_PLAN.md) for the dashboard-and-agents plan and [`CODEBASE_PLAN.md`](CODEBASE_PLAN.md) for full mapping to architecture and streams.
