"""Streamlit entrypoint: left col (Live Gauges), right col (Trade Log), Carbon Counter, 3D map."""

import streamlit as st

from thermal_commons_mvp.dashboard.components.carbon_counter import render_carbon_counter
from thermal_commons_mvp.dashboard.components.gauges import render_gauges
from thermal_commons_mvp.dashboard.components.trade_log import render_trade_log
from thermal_commons_mvp.dashboard.components.district_map import render_district_map

st.set_page_config(page_title="COOL — Market Dashboard", layout="wide")


def main() -> None:
    st.title("COOL — Cooperative Optimisation of Urban Loads")
    st.caption("Real-time Carbon ROI via inter-building energy trading")

    # Top: Carbon Counter
    render_carbon_counter()

    # Main: two columns
    left, right = st.columns([1, 1])
    with left:
        render_gauges()
    with right:
        render_trade_log()

    # Bottom: 3D district map
    render_district_map()


if __name__ == "__main__":
    main()


def run_dashboard() -> None:
    """Entrypoint for `cool-dash` console script: run Streamlit programmatically."""
    import sys
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__, "--server.headless", "true"]
    stcli.main()
