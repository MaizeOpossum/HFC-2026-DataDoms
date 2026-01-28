# Current Telemetry Implementation

**Aligned with** [`architecture.json`](architecture.json) and [`DASHBOARD_AND_AGENTS_PLAN.md`](DASHBOARD_AND_AGENTS_PLAN.md). This doc describes how telemetry is received today and how it fits into the target architecture.

---

## Overview

Telemetry is currently received in **two different ways** depending on the context:

1. **Simulation Engine (Dashboard)**: Uses **mock/random telemetry generation**
2. **API Routes**: Uses **BACnet driver** (with fallback to mock)

## Current Implementation

### 1. Simulation Engine (Dashboard) - **MOCK DATA**

**Location**: `thermal_commons_mvp/dashboard/simulation_engine.py`

**Function**: `_random_telemetry(building_id: str, step: int) -> Telemetry`

```python
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
    return Telemetry(...)
```

**How it works**:
- Called in `step()` function for each of 50 buildings
- Generates deterministic but varying values based on:
  - Building ID (hash-based base values)
  - Step number (time-based variation)
  - Random walk (small variations each step)
- **No real BMS connection** - purely simulated

**Usage in simulation**:
```python
for b in BUILDING_IDS:
    t = _random_telemetry(b, step_n)  # ← Mock data
    telemetry[b] = t
    # Agents use this telemetry to make decisions
    bid_order, ask_order = agents[b].submit_orders(t, grid_signal, ...)
```

### 2. API Routes - **BACNET DRIVER** (with mock fallback)

**Location**: `thermal_commons_mvp/api/routes/telemetry.py`

**Endpoint**: `GET /telemetry/{building_id}`

**How it works**:
- Uses `BACnetDriver` from `thermal_commons_mvp/interface/bacnet_driver.py`
- Attempts to read from real BACnet/IP BMS
- Falls back to mock if BAC0 not available or connection fails

**BACnet Driver Implementation**:
```python
class BAC0Driver(BACnetDriver):
    def read_telemetry(self, building_id: str) -> Telemetry:
        if not BAC0_AVAILABLE or self._bacnet is None:
            return _mock_telemetry(building_id)  # Fallback
        temp, humidity, power = self._read_points(building_id)
        return Telemetry(...)
```

**Current Status**:
- BACnet driver exists but `_read_points()` is a **stub** (returns hardcoded values)
- Real BACnet point addresses need to be configured
- Not integrated into simulation engine

## Architecture Gap

**Problem**: The simulation engine and API use **different telemetry sources**:

- **Dashboard**: Always uses mock data (`_random_telemetry`)
- **API**: Can use BACnet (but currently stubbed)

**Impact**: 
- Dashboard shows simulated data, not real building data
- API can theoretically read real data, but it's not connected to the simulation

## Data Flow

### Current Simulation Flow:
```
simulation_engine.step()
  ↓
For each building (50 buildings):
  ↓
_random_telemetry(building_id, step)  ← MOCK DATA
  ↓
Telemetry object (temp, humidity, power)
  ↓
Agent uses telemetry to generate bids/asks
  ↓
Orders matched, trades executed
```

### Potential Real Data Flow (Not Currently Implemented):
```
BACnet BMS Network
  ↓
BAC0Driver.read_telemetry(building_id)
  ↓
Read from BACnet points (temp, humidity, power)
  ↓
Telemetry object
  ↓
Simulation engine uses real data
  ↓
Agents make decisions based on real building state
```

## Telemetry Model

**Location**: `thermal_commons_mvp/models/telemetry.py`

```python
@dataclass(frozen=True)
class Telemetry:
    building_id: str
    temp_c: float          # Temperature in Celsius (15-35°C)
    humidity_pct: float    # Humidity percentage (0-100%)
    power_load_kw: float  # Power load in kilowatts (≥ 0)
    timestamp: Optional[datetime] = None
```

**Validation**:
- Temperature: 15-35°C (Singapore building range)
- Humidity: 0-100%
- Power: Non-negative

## Integration Points

### Where Telemetry is Used:

1. **Agent Decision Making**:
   - `MarketMakerAgent.submit_orders(telemetry, ...)`
   - `AIDecisionEngine.analyze_and_decide(DecisionContext)` uses `context.telemetry`

2. **Dashboard Visualization**:
   - `render_building_bar_chart(telemetry_by_building, ...)`
   - `render_district_map(telemetry_by_building, ...)`
   - `render_time_series_chart(history)` (history contains telemetry snapshots)

3. **Persistence**:
   - `StateDatabase.save_history()` stores telemetry as JSON
   - `StateDatabase.get_recent_history()` retrieves historical telemetry

## Future Integration (New Architecture)

The new architecture should support:

1. **Unified Telemetry Source**:
   - Single source of truth (BACnet or simulation)
   - Configurable via settings

2. **Real-time Telemetry Events**:
   - Publish telemetry updates via WebSocket
   - React component can visualize real-time building state changes

3. **Hybrid Mode**:
   - Use real BACnet data when available
   - Fall back to simulation for missing buildings
   - Mix real and simulated data seamlessly

## Current Limitations

1. **No Real BMS Integration**: Simulation always uses mock data
2. **BACnet Stub**: `_read_points()` returns hardcoded values
3. **No Telemetry Events**: Telemetry updates not published to event bus
4. **No Real-time Updates**: Telemetry only updated every 3 seconds (Streamlit refresh)

## Recommendations

1. **Integrate BACnet into Simulation**:
   ```python
   # In simulation_engine.py
   driver = BAC0Driver()
   driver.connect()
   for b in BUILDING_IDS:
       t = driver.read_telemetry(b)  # Real data
       telemetry[b] = t
   ```

2. **Add Telemetry Events**:
   ```python
   # Publish telemetry updates
   event_bus.publish('telemetry_updated', {
       'building_id': b,
       'telemetry': t
   })
   ```

3. **WebSocket Telemetry Stream**:
   - New endpoint: `/ws/telemetry`
   - Broadcast telemetry updates in real-time
   - React component subscribes for live updates
