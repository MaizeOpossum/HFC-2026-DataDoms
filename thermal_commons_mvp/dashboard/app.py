"""Streamlit entrypoint: left col (Live Gauges), right col (Trade Log), Carbon Counter, 3D map."""

import sys
from pathlib import Path

# Ensure project root is on the path when run via: streamlit run thermal_commons_mvp/dashboard/app.py
_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent.parent
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from thermal_commons_mvp.dashboard.components.building_charts import render_building_bar_chart, render_time_series_chart
from thermal_commons_mvp.dashboard.components.carbon_counter import render_carbon_counter
from thermal_commons_mvp.dashboard.components.styling import inject_custom_css, inject_custom_js
from thermal_commons_mvp.dashboard.components.trade_log import render_trade_log
from thermal_commons_mvp.dashboard.components.district_map import render_district_map
from thermal_commons_mvp.dashboard.simulation_engine import make_initial_state, step

st.set_page_config(
    page_title="COOL — Market Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

# Inject modern styling
inject_custom_css()
inject_custom_js()

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
    
    # Charts side by side - grouped with their controls
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        render_building_bar_chart(
            telemetry_by_building=sim.get("telemetry"),
            grid_stress=sim.get("grid_stress"),
        )
    
    with chart_col2:
        render_time_series_chart(
            history=sim.get("history"),
        )
    
    # Trade log section
    render_trade_log(
        trades=sim.get("trades"),
        bid_to_building=sim.get("bid_to_building", {}),
        ask_to_building=sim.get("ask_to_building", {}),
    )

    # Singapore district map: buildings colored by temperature / power / grid stress
    render_district_map(
        telemetry_by_building=sim.get("telemetry"),
        grid_stress=sim.get("grid_stress"),
    )


def main() -> None:
    # Night Galaxy header
    st.markdown(
        """
        <div style="
            text-align: center; 
            margin-bottom: 3rem; 
            padding: 2rem; 
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.4) 0%, rgba(76, 29, 149, 0.3) 100%);
            border-radius: 16px;
            border: 1px solid rgba(139, 92, 246, 0.3);
            backdrop-filter: blur(10px);
            box-shadow: 0 0 40px rgba(139, 92, 246, 0.2);
        ">
            <h1 style="margin-bottom: 0.5rem; font-size: 3.5rem;">🌡️ COOL</h1>
            <p style="font-size: 1.3rem; color: #E5E7EB; margin-top: 0; font-weight: 500;">
                Cooperative Optimisation of Urban Loads
            </p>
            <p style="font-size: 1rem; color: #9CA3AF; margin-top: 0.75rem;">
                ⚡ Real-time Carbon ROI via inter-building energy trading • 
                🤖 50 AI-powered buildings • 
                🏙️ Singapore District Network
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    live_simulation()


if __name__ == "__main__":
    main()


def run_dashboard() -> None:
    """Entrypoint for `cool-dash` console script: run Streamlit programmatically."""
    import sys
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__, "--server.headless", "true"]
    stcli.main()
