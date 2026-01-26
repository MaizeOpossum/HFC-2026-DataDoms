# COOL — Codebase Plan

Plan for **thermal_commons_mvp** aligned with `architecture.json`.  
Structured for clarity, testability, and Python 3.10+ best practices.

---

## 1. Top-level layout

```
thermal_commons_mvp/
├── pyproject.toml              # Build, deps, tooling (ruff, pytest, mypy)
├── README.md
├── .env.example
├── config/                     # Configuration & constants
├── models/                     # Domain models & DTOs
├── simulation/                 # Layer 1 edge: CityLearn & grid stress
├── interface/                  # Layer 1 edge: BACnet/BMS
├── agents/                     # Layer 2 swarm: MARL & market logic
├── market/                     # Layer 2: order matching & execution
├── api/                        # Backend: FastAPI
├── dashboard/                  # Layer 3: Streamlit UI
├── utils/                      # Shared utilities (carbon, logging)
└── tests/                      # Unit & integration tests
```

---

## 2. Package & module breakdown

### 2.1 `config/`

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `get_settings` |
| `settings.py` | Pydantic `BaseSettings` from env (API port, BACnet IP, CityLearn schema path, log level) |
| `constants.py` | Literals: building IDs, default setpoints, grid stress levels, market params |

### 2.2 `models/`

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export public schemas |
| `telemetry.py` | `Telemetry` dataclass: temp, humidity, power_load, timestamp, building_id |
| `bids.py` | `Bid`, `Ask`, `BidType` (buy/sell), `BidStatus` |
| `trades.py` | `Trade`, `OrderBookSnapshot` |
| `grid_signal.py` | `GridStressLevel`, `GridStressSignal` (e.g. for demand response) |

### 2.3 `simulation/` — *Stream A*

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `CityLearnGym`, `GridStressGenerator` |
| `city_gym.py` | CityLearn wrapper: `Building_5` tropical preset, `step()` → `[temp, humidity, power_load]`, Gym-like API |
| `grid_stress.py` | `GridStressGenerator`: produces `GridStressSignal` on a schedule or from a simple model |

### 2.4 `interface/` — *Layer 1 BMS*

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `BACnetDriver` |
| `bacnet_driver.py` | BAC0-based driver: connect, read points (temp, humidity, load), optional write; abstract interface for simulation swap |

### 2.5 `agents/` — *Stream B*

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `BaseAgent`, `RbcAgent`, `MarketMakerAgent` |
| `base_agent.py` | Abstract `BaseAgent`: `act(obs) -> action`, interface for RLlib/CityLearn |
| `rbc_agent.py` | Rule-based controller: comfort vs. load, baseline stability |
| `market_maker.py` | Market-making logic: submit bids/asks based on local state and grid stress |
| `bid_generator.py` | `BidGenerator`: willingness to shed load vs. comfort cost → `Bid`/`Ask` |

### 2.6 `market/` — *Stream B*

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `TradeExecution`, `OrderBook` |
| `order_book.py` | In-memory order book (bids/asks), optional persistence |
| `trade_execution.py` | `TradeExecution`: match orders (e.g. via `asyncio.Queue`), emit `Trade` events |

### 2.7 `api/` — *Backend*

| File | Purpose |
|------|--------|
| `__init__.py` | — |
| `main.py` | FastAPI app, CORS, lifespan (start/stop BACnet/simulation/queues) |
| `routes/` | |
| `routes/telemetry.py` | Stream or poll sensor/telemetry (temp, humidity, power_load) |
| `routes/market.py` | Submit bid/ask, order book snapshot, trade history |
| `dependencies.py` | Shared injectables: settings, driver, order book, trade execution |

### 2.8 `dashboard/` — *Stream C*

| File | Purpose |
|------|--------|
| `__init__.py` | — |
| `app.py` | Streamlit entrypoint: layout (e.g. left: Live Gauges, right: Trade Log), refresh rate |
| `components/` | |
| `components/gauges.py` | Live gauges for temp, humidity, power, grid stress |
| `components/carbon_counter.py` | Carbon Counter: aggregate real-time savings from `utils.carbon_calculator` |
| `components/trade_log.py` | Trade log table / feed |
| `components/district_map.py` | 3D district map via PyDeck |

### 2.9 `utils/`

| File | Purpose |
|------|--------|
| `__init__.py` | Re-export `CarbonCalculator`, `get_logger` |
| `carbon_calculator.py` | `CarbonCalculator`: kWh → tCO₂ (configurable factor), aggregate savings |
| `logging_utils.py` | `get_logger(name)` with consistent format and level from config |

---

## 3. Cross-cutting conventions

- **Type hints** everywhere on public functions and class methods.
- **Docstrings**: Google or NumPy style; every public module/class/function has a one-line summary and, if needed, Args/Returns/Raises.
- **Immutability**: Prefer `dataclass(frozen=True)` or `TypedDict` for telemetry/bids/trades where appropriate.
- **Config**: Single source of truth in `config.settings`; no magic numbers in business logic.
- **Logging**: Use `utils.logging_utils.get_logger(__name__)`; level and format driven by config.
- **Async**: FastAPI and trade execution use `async`/`await`; sync code in simulation/agents can run in thread pools where needed.
- **Tests**: `tests/unit/` and `tests/integration/`; mirror package layout; use pytest and (optional) pytest-asyncio for API/agents.

---

## 4. Entrypoints

- **Simulation / local dev**: `python -m thermal_commons_mvp.simulation.city_gym` (or a small `scripts/run_sim.py`).
- **API**: `uvicorn api.main:app --reload` (or `python -m thermal_commons_mvp.api.main`).
- **Dashboard**: `streamlit run dashboard/app.py` (or `python -m streamlit run thermal_commons_mvp.dashboard.app`).
- **CLI** (optional): `thermal_commons_mvp` console script in `pyproject.toml` for “run sim | api | dashboard”.

---

## 5. Dependency groups (pyproject.toml)

- **core**: citylearn, bac0, pydantic-settings, structlog or standard logging.
- **agents**: ray[rllib], gymnasium.
- **api**: fastapi, uvicorn.
- **dashboard**: streamlit, pydeck, pandas.
- **dev**: pytest, pytest-asyncio, ruff, mypy, pre-commit.

---

## 6. Mapping to architecture.json

| Architecture element | Code location |
|----------------------|---------------|
| Layer 1 – BMS Connector (BACnet) | `interface/bacnet_driver.py` |
| Layer 1 – Simulation (mock world) | `simulation/city_gym.py`, `simulation/grid_stress.py` |
| Layer 2 – Agent Grid, MARL | `agents/base_agent.py`, `agents/rbc_agent.py`, `agents/market_maker.py`, `agents/bid_generator.py` |
| Layer 2 – Order matching | `market/order_book.py`, `market/trade_execution.py` |
| Layer 3 – Market Dashboard | `dashboard/app.py`, `dashboard/components/*` |
| Carbon ROI / savings | `utils/carbon_calculator.py`, `dashboard/components/carbon_counter.py` |
| Stream A (simulation) | `simulation/` |
| Stream B (agents + market) | `agents/`, `market/` |
| Stream C (dashboard) | `dashboard/` |

This plan keeps the codebase **structured**, **categorized**, and aligned with **Python best practices** and your architecture.
