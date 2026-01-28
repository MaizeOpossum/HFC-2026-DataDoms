"""Carbon Counter: aggregate real-time savings from carbon_calculator."""

from typing import Optional

import streamlit as st

from thermal_commons_mvp.utils.carbon_calculator import CarbonCalculator

# kg CO2 absorbed per tree per year (typical mature tree, ~21.77 used by EPA/others)
KG_CO2_PER_TREE_PER_YEAR = 21.77


def _trees_equivalent(kg_co2: float) -> int:
    """Convert kg CO2 saved to equivalent trees planted (absorbed over one year)."""
    if kg_co2 <= 0:
        return 0
    return max(0, int(round(kg_co2 / KG_CO2_PER_TREE_PER_YEAR)))


def render_carbon_counter(total_kwh_saved: Optional[float] = None) -> None:
    """Render aggregated real-time carbon savings with modern styling."""
    # Compact carbon counter in a single row
    calc = CarbonCalculator()
    
    if total_kwh_saved is not None and total_kwh_saved >= 0:
        total_kg = calc.kwh_to_kg_co2(total_kwh_saved)
        trees = _trees_equivalent(total_kg)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌍 CO₂ Saved", f"{total_kg:.1f} kg")
        with col2:
            st.metric("⚡ Energy Traded", f"{total_kwh_saved:.1f} kWh")
        with col3:
            st.metric("🌳 Equivalent trees planted", f"{trees}")
        with col4:
            st.metric("🔄 Status", "Live")
    else:
        kwh_savings = [10.0, 5.5, 12.0]
        total_kg = calc.aggregate_savings_kg(kwh_savings)
        trees = _trees_equivalent(total_kg)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌍 CO₂ Saved", f"{total_kg:.1f} kg")
        with col2:
            st.metric("⚡ Energy Traded", f"{sum(kwh_savings):.1f} kWh")
        with col3:
            st.metric("🌳 Equivalent trees planted", f"{trees}")
        with col4:
            st.metric("🔄 Status", "Demo")
