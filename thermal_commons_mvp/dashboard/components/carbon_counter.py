"""Carbon Counter: aggregate real-time savings from carbon_calculator."""

import streamlit as st

from thermal_commons_mvp.utils.carbon_calculator import CarbonCalculator


def render_carbon_counter() -> None:
    """Render aggregated real-time carbon savings."""
    st.subheader("Carbon Counter")
    calc = CarbonCalculator()
    # Placeholder kWh savings; in production, sum from trade/telemetry
    kwh_savings = [10.0, 5.5, 12.0]
    total_kg = calc.aggregate_savings_kg(kwh_savings)
    total_tonnes = total_kg / 1000.0
    st.metric("Total CO₂ saved (kg)", f"{total_kg:.1f}", delta=None)
    st.caption(f"≈ {total_tonnes:.3f} tCO₂ from {sum(kwh_savings):.1f} kWh saved")
