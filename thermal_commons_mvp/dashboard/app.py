"""Streamlit entrypoint: left col (Live Gauges), right col (Trade Log), Carbon Counter, 3D map."""

import sys
from pathlib import Path

# Ensure project root is on the path when run via: streamlit run thermal_commons_mvp/dashboard/app.py
_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent.parent
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from thermal_commons_mvp.dashboard.components.carbon_counter import render_carbon_counter
from thermal_commons_mvp.dashboard.components.gauges import render_gauges
from thermal_commons_mvp.dashboard.components.trade_log import render_trade_log
from thermal_commons_mvp.dashboard.components.district_map import render_district_map
from thermal_commons_mvp.dashboard.simulation_engine import make_initial_state, step

st.set_page_config(page_title="COOL — Market Dashboard", layout="wide")

SIM_KEY = "sim"
REFRESH_SECONDS = 3


@st.fragment(run_every=REFRESH_SECONDS)
def live_simulation():
    """Run one simulation step and render gauges, trade log, carbon, map."""
    if SIM_KEY not in st.session_state:
        st.session_state[SIM_KEY] = make_initial_state()
    sim = st.session_state[SIM_KEY]
    step(sim)

    render_carbon_counter(total_kwh_saved=sim.get("total_kwh_saved"))
    left, right = st.columns([1, 1])
    with left:
        render_gauges(
            telemetry_by_building=sim.get("telemetry"),
            grid_stress=sim.get("grid_stress"),
        )
    with right:
        render_trade_log(trades=sim.get("trades"))
    st.caption(f"Simulation step {sim.get('step_count', 0)} — updates every {REFRESH_SECONDS}s. Buildings trade when bid ≥ ask.")

    # Singapore district map: buildings colored by temperature / power / grid stress
    render_district_map(
        telemetry_by_building=sim.get("telemetry"),
        grid_stress=sim.get("grid_stress"),
    )


def main() -> None:
    st.title("COOL — Cooperative Optimisation of Urban Loads")
    st.caption("Real-time Carbon ROI via inter-building energy trading")
    live_simulation()


if __name__ == "__main__":
    main()


def run_dashboard() -> None:
    """Entrypoint for `cool-dash` console script: run Streamlit programmatically."""
    import sys
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__, "--server.headless", "true"]
    stcli.main()
