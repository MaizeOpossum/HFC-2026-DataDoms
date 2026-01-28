"""Live gauges for temp, humidity, power, grid stress."""

from typing import Dict, Optional

import streamlit as st


def _sample_telemetry() -> dict:
    return {
        "temp_c": 24.2,
        "humidity_pct": 58.0,
        "power_load_kw": 52.3,
        "grid_stress": "medium",
    }


def render_gauges(
    telemetry_by_building: Optional[Dict[str, object]] = None,
    grid_stress: Optional[str] = None,
    ai_reasoning: Optional[Dict[str, str]] = None,
) -> None:
    """Render live gauges. If telemetry_by_building is provided, show per-building and grid stress."""
    st.subheader("Live Gauges & AI Decisions")
    if telemetry_by_building and len(telemetry_by_building) > 0:
        # Show first 3 buildings expanded, rest collapsed
        building_list = list(telemetry_by_building.items())
        for idx, (building_id, t) in enumerate(building_list):
            expanded = idx < 3
            with st.expander(f"🤖 {building_id} — AI Agent", expanded=expanded):
                row = st.columns(4)
                row[0].metric("Temp.", f"{getattr(t, 'temp_c', 0):.1f}")
                row[1].metric("Humidity (%)", f"{getattr(t, 'humidity_pct', 0):.0f}")
                row[2].metric("Power", f"{getattr(t, 'power_load_kw', 0):.1f}")
                row[3].metric("Grid stress", grid_stress or "—")
                
                # Show AI reasoning if available
                if ai_reasoning and building_id in ai_reasoning:
                    st.info(f"**AI Decision:** {ai_reasoning[building_id]}")
    else:
        d = _sample_telemetry()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Temp.", f"{d['temp_c']:.1f}", delta=None)
        with c2:
            st.metric("Humidity (%)", f"{d['humidity_pct']:.0f}", delta=None)
        with c3:
            st.metric("Power", f"{d['power_load_kw']:.1f}", delta=None)
        with c4:
            st.metric("Grid stress", d["grid_stress"], delta=None)
