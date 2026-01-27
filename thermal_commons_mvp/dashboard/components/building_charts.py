"""Bar chart and time series charts for building metrics."""

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def _get_metric_value(building_id: str, telemetry: Dict[str, Any], grid_stress: Optional[str], metric: str) -> float:
    """Extract metric value from telemetry or grid stress."""
    if metric == "Temperature (°C)":
        if building_id in telemetry:
            return getattr(telemetry[building_id], "temp_c", 0.0)
        return 0.0
    elif metric == "Humidity (%)":
        if building_id in telemetry:
            return getattr(telemetry[building_id], "humidity_pct", 0.0)
        return 0.0
    elif metric == "Energy Use (kW)":
        if building_id in telemetry:
            return getattr(telemetry[building_id], "power_load_kw", 0.0)
        return 0.0
    elif metric == "Grid Stress":
        # Map grid stress level to numeric value
        stress_map = {"low": 0.25, "medium": 0.5, "high": 0.9, "critical": 1.0}
        return stress_map.get((grid_stress or "low").lower(), 0.25)
    return 0.0


def render_building_bar_chart(
    telemetry_by_building: Optional[Dict[str, Any]] = None,
    grid_stress: Optional[str] = None,
) -> None:
    """Render bar chart: buildings (x-axis, alphabetical) vs selected metric (y-axis)."""
    if not telemetry_by_building:
        return
    
    # Group everything in a styled container
    st.markdown(
        """
        <div style="
            background: rgba(26, 31, 58, 0.6);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 212, 255, 0.2);
            margin-bottom: 1rem;
        ">
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### 📊 Building Comparison")
    
    # Metric selector and stats in one row
    metric_col, stats_col = st.columns([2, 3])
    with metric_col:
        metric = st.selectbox(
            "Metric",
            ["Temperature (°C)", "Humidity (%)", "Energy Use (kW)", "Grid Stress"],
            key="bar_chart_metric",
            label_visibility="collapsed",
        )
    
    # Sort buildings alphabetically
    building_ids = sorted(telemetry_by_building.keys())
    
    # Extract values for selected metric
    values = [
        _get_metric_value(bid, telemetry_by_building, grid_stress, metric)
        for bid in building_ids
    ]
    
    # Summary stats inline with labels
    with stats_col:
        stats_inline = st.columns(4)
        with stats_inline[0]:
            st.metric("Min", f"{min(values):.1f}", delta=f"{metric}")
        with stats_inline[1]:
            st.metric("Max", f"{max(values):.1f}", delta=f"{metric}")
        with stats_inline[2]:
            st.metric("Avg", f"{sum(values) / len(values) if values else 0:.1f}", delta=f"{metric}")
        with stats_inline[3]:
            st.metric("Buildings", len(building_ids))
    
    # Create DataFrame for chart
    df = pd.DataFrame({
        "Building": building_ids,
        metric: values,
    })
    
    # Create bar chart - compact height for side-by-side
    st.bar_chart(df.set_index("Building"), height=350, use_container_width=True)
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)


def render_time_series_chart(
    history: Optional[List[Dict[str, Any]]] = None,
    metric: Optional[str] = None,
) -> None:
    """Render time series chart showing selected metric over time for all buildings."""
    if not history or len(history) == 0:
        return
    
    # Group everything in a styled container
    st.markdown(
        """
        <div style="
            background: rgba(26, 31, 58, 0.6);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 212, 255, 0.2);
            margin-bottom: 1rem;
        ">
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### 📈 Time Series Trend")
    
    # Metric selector and stats in one row
    metric_col, stats_col = st.columns([2, 3])
    with metric_col:
        metric_selector = st.selectbox(
            "Metric",
            ["Temperature (°C)", "Humidity (%)", "Energy Use (kW)", "Grid Stress"],
            key="time_series_metric",
            label_visibility="collapsed",
        )
    
    # Build DataFrame from history
    # history is list of {step, timestamp, telemetry: {bid: Telemetry}, grid_stress}
    rows = []
    for entry in history:
        step = entry.get("step", 0)
        timestamp = entry.get("timestamp", step)
        telemetry = entry.get("telemetry", {})
        grid_stress = entry.get("grid_stress", "low")
        
        # Calculate aggregate stats
        values = []
        for bid in sorted(telemetry.keys()):
            val = _get_metric_value(bid, telemetry, grid_stress, metric_selector)
            values.append(val)
        
        if values:
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            rows.append({
                "Step": step,
                "Time": timestamp,
                f"Avg {metric_selector}": avg_value,
                f"Min {metric_selector}": min_value,
                f"Max {metric_selector}": max_value,
            })
    
    if not rows:
        st.info("No historical data yet. Data will appear as simulation runs.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(rows)
    
    # Plot time series with avg, min, max
    if "Step" in df.columns and f"Avg {metric_selector}" in df.columns:
        chart_data = df.set_index("Step")[[
            f"Avg {metric_selector}",
            f"Min {metric_selector}",
            f"Max {metric_selector}",
        ]]
        st.line_chart(
            chart_data,
            height=350,
            use_container_width=True,
        )
        
        # Summary stats inline with labels
        with stats_col:
            stats_inline = st.columns(3)
            with stats_inline[0]:
                st.metric("Current", f"{df[f'Avg {metric_selector}'].iloc[-1]:.1f}" if len(df) > 0 else "—", delta=f"{metric_selector}")
            with stats_inline[1]:
                st.metric("Min", f"{df[f'Min {metric_selector}'].min():.1f}" if len(df) > 0 else "—", delta=f"{metric_selector}")
            with stats_inline[2]:
                st.metric("Max", f"{df[f'Max {metric_selector}'].max():.1f}" if len(df) > 0 else "—", delta=f"{metric_selector}")
    else:
        st.warning("Data format issue. Expected 'Step' and metric columns.")
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)
