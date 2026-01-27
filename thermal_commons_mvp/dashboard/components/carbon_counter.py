"""Carbon Counter: aggregate real-time savings from carbon_calculator."""

from typing import Optional

import streamlit as st

from thermal_commons_mvp.utils.carbon_calculator import CarbonCalculator


def render_carbon_counter(total_kwh_saved: Optional[float] = None) -> None:
    """Render aggregated real-time carbon savings with modern styling."""
    # Compact carbon counter in a single row
    calc = CarbonCalculator()
    
    if total_kwh_saved is not None and total_kwh_saved >= 0:
        total_kg = calc.kwh_to_kg_co2(total_kwh_saved)
        total_tonnes = total_kg / 1000.0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌍 CO₂ Saved", f"{total_kg:.1f} kg")
        with col2:
            st.metric("⚡ Energy Traded", f"{total_kwh_saved:.1f} kWh")
        with col3:
            st.metric("📊 Equivalent", f"{total_tonnes:.3f} tCO₂")
        with col4:
            st.metric("🔄 Status", "Live", delta="Active")
    else:
        kwh_savings = [10.0, 5.5, 12.0]
        total_kg = calc.aggregate_savings_kg(kwh_savings)
        total_tonnes = total_kg / 1000.0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌍 CO₂ Saved", f"{total_kg:.1f} kg")
        with col2:
            st.metric("⚡ Energy Traded", f"{sum(kwh_savings):.1f} kWh")
        with col3:
            st.metric("📊 Equivalent", f"{total_tonnes:.3f} tCO₂")
        with col4:
            st.metric("🔄 Status", "Demo", delta="Sample")
