"""Bar chart and time series charts for building metrics."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from thermal_commons_mvp.dashboard.components.district_map_locations import BUILDING_NAMES

logger = logging.getLogger(__name__)


def _get_metric_value(building_id: str, telemetry: Dict[str, Any], grid_stress: Optional[str], metric: str) -> float:
    """Extract metric value from telemetry or grid stress."""
    if not metric or not telemetry:
        logger.warning(f"Missing metric or telemetry data for building {building_id}")
        return 0.0
    
    if building_id not in telemetry:
        logger.warning(f"Building {building_id} not found in telemetry data")
        return 0.0
    
    telemetry_obj = telemetry[building_id]
    if not telemetry_obj:
        logger.warning(f"Telemetry object is None for building {building_id}")
        return 0.0
    
    metric_normalized = metric.strip().lower()
    
    try:
        # Temperature matching - handle "Temp." and variations
        # Remove trailing period and whitespace for matching
        metric_clean = metric_normalized.rstrip(".")
        if metric_clean == "temp" or metric_normalized.startswith("temp") or "temperature" in metric_normalized:
            # Try to get temp_c attribute
            if hasattr(telemetry_obj, "temp_c"):
                value = getattr(telemetry_obj, "temp_c", None)
            elif isinstance(telemetry_obj, dict):
                value = telemetry_obj.get("temp_c")
            else:
                value = None
                
            if value is None:
                logger.warning(f"temp_c attribute missing for building {building_id}, telemetry type: {type(telemetry_obj)}")
                return 0.0
            return float(value)
        
        # Humidity matching
        if metric_normalized.startswith("humidity") or "humidity" in metric_normalized:
            if hasattr(telemetry_obj, "humidity_pct"):
                value = getattr(telemetry_obj, "humidity_pct", None)
            elif isinstance(telemetry_obj, dict):
                value = telemetry_obj.get("humidity_pct")
            else:
                value = None
            if value is None:
                logger.warning(f"humidity_pct attribute missing for building {building_id}")
                return 0.0
            return float(value)
        
        # Power matching - explicit check for "Power" first, then substring
        if metric_normalized == "power" or metric_normalized.startswith("power") or "energy" in metric_normalized:
            if hasattr(telemetry_obj, "power_load_kw"):
                value = getattr(telemetry_obj, "power_load_kw", None)
            elif isinstance(telemetry_obj, dict):
                value = telemetry_obj.get("power_load_kw")
            else:
                value = None
            if value is None:
                logger.warning(f"power_load_kw attribute missing for building {building_id}")
                return 0.0
            return float(value)
        
        # Grid stress matching
        if "grid" in metric_normalized and "stress" in metric_normalized:
            stress_map = {"low": 0.25, "medium": 0.5, "high": 0.9, "critical": 1.0}
            return stress_map.get((grid_stress or "low").lower(), 0.25)
    except (AttributeError, TypeError, ValueError) as e:
        logger.warning(f"Error extracting metric value for building {building_id}, metric {metric}: {e}")
        return 0.0
    
    return 0.0


def render_building_bar_chart(
    telemetry_by_building: Optional[Dict[str, Any]] = None,
    grid_stress: Optional[str] = None,
) -> None:
    """Render bar chart: buildings (x-axis, alphabetical) vs selected metric (y-axis)."""
    if not telemetry_by_building:
        return
    
    st.markdown("### 📊 Building Comparison")
    
    # Metric selector and stats in one row
    metric_col, stats_col = st.columns([3, 10])
    with metric_col:
        metric = st.selectbox(
            "Metric",
            ["Temp.", "Humidity (%)", "Power", "Grid stress"],
            key="bar_chart_metric",
            label_visibility="collapsed",
            index=0,  # Default to Temp.
        )
    
    # Sort buildings alphabetically by their real names
    building_ids = sorted(telemetry_by_building.keys())
    
    # Map building IDs to real building names
    building_names = [
        BUILDING_NAMES.get(bid, bid) for bid in building_ids
    ]
    
    # Create a mapping for sorting by name while preserving ID lookup
    building_data = [
        (BUILDING_NAMES.get(bid, bid), bid) for bid in building_ids
    ]
    # Sort by building name
    building_data.sort(key=lambda x: x[0])
    
    # Extract values for selected metric in sorted order
    sorted_building_ids = [bid for _, bid in building_data]
    sorted_building_names = [name for name, _ in building_data]
    values = [
        _get_metric_value(bid, telemetry_by_building, grid_stress, metric)
        for bid in sorted_building_ids
    ]
    
    # Check if we have valid values (not all zeros)
    if not values or all(v == 0.0 for v in values):
        st.warning(f"No valid {metric} data available for buildings.")
        return
    
    # Summary stats inline with labels
    with stats_col:
        stats_inline = st.columns(4)
        with stats_inline[0]:
            st.metric("Min", f"{min(values):.1f}")
        with stats_inline[1]:
            st.metric("Max", f"{max(values):.1f}")
        with stats_inline[2]:
            st.metric("Avg", f"{sum(values) / len(values) if values else 0:.1f}")
        with stats_inline[3]:
            st.metric("Buildings", len(sorted_building_names))
    
    # Create DataFrame for chart using real building names
    # Use a clean column name without special characters for better chart compatibility
    chart_column_name = metric.replace(".", "").replace(" ", "_").replace("(%)", "")
    df = pd.DataFrame({
        "Building": sorted_building_names,
        chart_column_name: values,
    })
    
    # Create bar chart - compact height for side-by-side
    st.bar_chart(df.set_index("Building"), height=350, use_container_width=True)
    
def render_time_series_chart(
    history: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Render time series chart showing selected metric over time for all buildings."""
    if not history or len(history) == 0:
        return
    
    st.markdown("### 📈 Time Series Trend")
    
    # Metric selector and stats in one row
    metric_col, stats_col = st.columns([3, 10])
    with metric_col:
        metric_selector = st.selectbox(
            "Metric",
            ["Temp.", "Humidity (%)", "Power", "Grid stress"],
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
        
        # Convert timestamp to datetime if it's not already
        if isinstance(timestamp, datetime):
            dt = timestamp
        elif isinstance(timestamp, str):
            try:
                dt = pd.to_datetime(timestamp)
            except:
                # Fallback: use step as minutes offset from a base time
                base_time = datetime.now()
                dt = base_time - timedelta(minutes=(len(history) - step))
        else:
            # Fallback: use step as minutes offset from a base time
            base_time = datetime.now()
            dt = base_time - timedelta(minutes=(len(history) - step))
        
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
                "Timestamp": dt,
                f"Avg {metric_selector}": avg_value,
                f"Min {metric_selector}": min_value,
                f"Max {metric_selector}": max_value,
            })
    
    if not rows:
        st.info("No historical data yet. Data will appear as simulation runs.")
        return
    
    df = pd.DataFrame(rows)
    
    # Ensure Timestamp is datetime type
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df = df.sort_values("Timestamp")
    
    # Plot time series with avg, min, max using Timestamp as x-axis
    if "Timestamp" in df.columns and f"Avg {metric_selector}" in df.columns:
        chart_data = df.set_index("Timestamp")[[
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
                st.metric("Current", f"{df[f'Avg {metric_selector}'].iloc[-1]:.1f}" if len(df) > 0 else "—")
            with stats_inline[1]:
                st.metric("Min", f"{df[f'Min {metric_selector}'].min():.1f}" if len(df) > 0 else "—")
            with stats_inline[2]:
                st.metric("Max", f"{df[f'Max {metric_selector}'].max():.1f}" if len(df) > 0 else "—")
    else:
        st.warning("Data format issue. Expected 'Timestamp' and metric columns.")
    
