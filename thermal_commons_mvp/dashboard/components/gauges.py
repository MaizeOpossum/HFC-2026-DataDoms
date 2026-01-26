"""Live gauges for temp, humidity, power, grid stress."""

import streamlit as st

# Placeholder: in production, pull from API or simulation
def _sample_telemetry() -> dict:
    return {
        "temp_c": 24.2,
        "humidity_pct": 58.0,
        "power_load_kw": 52.3,
        "grid_stress": "medium",
    }


def render_gauges() -> None:
    """Render live gauges in the left column."""
    st.subheader("Live Gauges")
    d = _sample_telemetry()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Temperature (°C)", f"{d['temp_c']:.1f}", delta=None)
    with c2:
        st.metric("Humidity (%)", f"{d['humidity_pct']:.0f}", delta=None)
    with c3:
        st.metric("Power (kW)", f"{d['power_load_kw']:.1f}", delta=None)
    with c4:
        st.metric("Grid stress", d["grid_stress"], delta=None)
