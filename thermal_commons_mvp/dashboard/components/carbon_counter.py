"""Carbon Counter: aggregate real-time savings from carbon_calculator."""

from typing import Optional

import streamlit as st

from thermal_commons_mvp.utils.carbon_calculator import CarbonCalculator


def render_carbon_counter(total_kwh_saved: Optional[float] = None) -> None:
    """Render aggregated real-time carbon savings. If total_kwh_saved provided, use it."""
    st.subheader("Carbon Counter")
    calc = CarbonCalculator()
    if total_kwh_saved is not None and total_kwh_saved >= 0:
        total_kg = calc.kwh_to_kg_co2(total_kwh_saved)
        total_tonnes = total_kg / 1000.0
        st.metric("Total CO₂ saved (kg)", f"{total_kg:.1f}", delta=None)
        st.caption(f"≈ {total_tonnes:.3f} tCO₂ from {total_kwh_saved:.1f} kWh traded/saved")
    else:
        kwh_savings = [10.0, 5.5, 12.0]
        total_kg = calc.aggregate_savings_kg(kwh_savings)
        total_tonnes = total_kg / 1000.0
        st.metric("Total CO₂ saved (kg)", f"{total_kg:.1f}", delta=None)
        st.caption(f"≈ {total_tonnes:.3f} tCO₂ from {sum(kwh_savings):.1f} kWh saved (demo)")
