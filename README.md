# COOL — Cooperative Optimisation of Urban Loads

**Mission:** Deploy a decentralised agentic cooling swarm for Singapore commercial buildings.  
**Target metric:** Maximise Carbon ROI via inter-building energy trading.

This repo implements the MVP described in `architecture.json` and laid out in `CODEBASE_PLAN.md`.

## Structure

```
thermal_commons_mvp/
├── config/         # Settings (Pydantic), constants
├── models/         # Telemetry, Bid/Ask, Trade, GridStress
├── simulation/     # CityLearn gym, grid stress generator
├── interface/      # BACnet BMS driver (BAC0)
├── agents/         # BaseAgent, RbcAgent, MarketMaker, BidGenerator
├── market/         # OrderBook, TradeExecution
├── api/            # FastAPI: telemetry & market routes
├── dashboard/      # Streamlit: gauges, carbon counter, trade log, PyDeck map
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

## Run

From the **project root** (parent of `thermal_commons_mvp/`), with the package on `PYTHONPATH` or installed (`pip install -e .`):

| Component   | Command |
|------------|---------|
| **Simulation** | `python -m thermal_commons_mvp.simulation.city_gym` or `cool-sim` |
| **API**        | `uvicorn thermal_commons_mvp.api.main:app --reload` or `cool-api` |
| **Dashboard**  | `streamlit run thermal_commons_mvp/dashboard/app.py` or `cool-dash` |

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

See `CODEBASE_PLAN.md` for full mapping to architecture and streams.
