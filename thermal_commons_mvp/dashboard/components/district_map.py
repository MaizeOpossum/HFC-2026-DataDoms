"""Singapore district map: building locations colored by temperature, power, or grid stress."""

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from thermal_commons_mvp.dashboard.components.district_map_locations import (
    BUILDING_NAMES,
    SINGAPORE_BUILDING_LOCATIONS,
)

# Fallbacks when there is no variation in data
TEMP_RANGE_FALLBACK = (20.0, 30.0)
POWER_RANGE_FALLBACK = (0.0, 100.0)
GRID_STRESS_VALUES = {"low": 0.25, "medium": 0.5, "high": 0.9, "critical": 1.0}


def _norm_to_color(norm: float) -> List[int]:
    """Map normalized value in [0, 1] to [R, G, B, A]. Blue (low) → Red (high)."""
    norm = max(0.0, min(1.0, norm))
    r = int(255 * norm)
    g = 0
    b = int(255 * (1.0 - norm))
    return [r, g, b, 200]


def _get_raw_value_and_label(
    building_id: str,
    telemetry: Optional[Dict[str, Any]],
    grid_stress: Optional[str],
    metric: str,
) -> Tuple[Optional[float], str]:
    """Return (raw numeric value or None, label string) for the chosen metric."""
    metric_key = (metric or "").strip().lower()
    if metric_key in {"temperature (°c)", "temp.", "temp", "temp. (°c)", "temperature"}:
        if telemetry and building_id in telemetry:
            t = telemetry[building_id]
            v = getattr(t, "temp_c", 24.0)
            return (float(v), f"{v:.1f} °C")
        return (None, "—")
    if metric_key in {"power (kw)", "power", "energy use", "energy", "power (kwh)"}:
        if telemetry and building_id in telemetry:
            t = telemetry[building_id]
            v = getattr(t, "power_load_kw", 50.0)
            return (float(v), f"{v:.1f} kW")
        return (None, "—")
    if metric_key in {"grid stress", "grid_stress"}:
        v = GRID_STRESS_VALUES.get((grid_stress or "low").lower(), 0.25)
        return (v, grid_stress or "low")
    return (None, "—")


def _compute_data_range(
    building_ids: List[str],
    telemetry: Optional[Dict[str, Any]],
    grid_stress: Optional[str],
    metric: str,
) -> Tuple[float, float, str]:
    """Return (min_val, max_val, value_unit) for the chosen metric from actual data."""
    metric_key = (metric or "").strip().lower()
    if metric_key in {"grid stress", "grid_stress"}:
        vals = list(GRID_STRESS_VALUES.values())
        return (min(vals), max(vals), "")

    raw_values: List[float] = []
    for bid in building_ids:
        v, _ = _get_raw_value_and_label(bid, telemetry, grid_stress, metric)
        if v is not None:
            raw_values.append(v)

    if metric_key in {"temperature (°c)", "temp.", "temp", "temp. (°c)", "temperature"}:
        lo, hi = (min(raw_values), max(raw_values)) if raw_values else TEMP_RANGE_FALLBACK
        if lo >= hi:
            lo, hi = TEMP_RANGE_FALLBACK
        return (lo, hi, "°C")
    if metric_key in {"power (kw)", "power", "energy use", "energy", "power (kwh)"}:
        lo, hi = (min(raw_values), max(raw_values)) if raw_values else POWER_RANGE_FALLBACK
        if lo >= hi:
            lo, hi = POWER_RANGE_FALLBACK
        return (lo, hi, "kW")
    return (0.0, 1.0, "")


def render_district_map(
    telemetry_by_building: Optional[Dict[str, Any]] = None,
    grid_stress: Optional[str] = None,
    trades: Optional[List[Any]] = None,
    bid_to_building: Optional[Dict[str, str]] = None,
    ask_to_building: Optional[Dict[str, str]] = None,
) -> None:
    """Render Singapore map with buildings as points at their real locations."""
    st.markdown("### 🗺️ CBD District Map — Singapore")
    
    try:
        import pydeck as pdk
    except ImportError:
        st.error("❌ PyDeck not installed. Install with: pip install pydeck")
        return

    building_ids = list(SINGAPORE_BUILDING_LOCATIONS.keys())
    if not building_ids:
        return

    # Color selector for buildings
    metric = st.selectbox(
        "🎨 Color buildings by",
        ["Temp.", "Power", "Grid stress"],
        key="district_map_metric",
    )

    # Dynamic range from actual data: [min_val, max_val]
    data_min, data_max, value_unit = _compute_data_range(
        building_ids, telemetry_by_building, grid_stress, metric
    )
    data_range = data_max - data_min
    if data_range <= 0:
        data_range = 1.0  # avoid div by zero

    tooltip = {
        "html": "<b>{name}</b><br/>{label}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # Prepare building data: normalize value to [0,1] using data_min..data_max, then color
    rows: List[Dict[str, Any]] = []
    for bid in building_ids:
        lat, lon = SINGAPORE_BUILDING_LOCATIONS[bid]
        raw_val, label = _get_raw_value_and_label(
            bid, telemetry_by_building, grid_stress, metric
        )
        if raw_val is not None and data_range > 0:
            norm = (raw_val - data_min) / data_range
            norm = max(0.0, min(1.0, norm))
        else:
            norm = 0.5
        color = _norm_to_color(norm)
        building_name = BUILDING_NAMES.get(bid, bid)
        rows.append({
            "lat": lat,
            "lon": lon,
            "name": building_name,
            "label": f"{building_name}<br/>{label}",
            "color": color,
            "radius": 50,
        })

    # Center on CBD (Marina Bay / Raffles Place area) - using real Singapore coordinates
    view = pdk.ViewState(
        latitude=1.2815,  # Marina Bay area
        longitude=103.8515,  # Marina Bay area
        zoom=14,  # Good zoom level to see all buildings
        pitch=0,  # Top-down view for clarity
        bearing=0,
    )
    
    # Create scatterplot layer for buildings
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=rows,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        radius_min_pixels=4,
        radius_max_pixels=50,
        stroked=True,
        get_line_color=[255, 255, 255, 255],
        line_width_min_pixels=2,
    )
    
    layers = [scatterplot_layer]
    
    # Create deck with default Mapbox light style
    try:
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view,
            map_style="light",  # Default Mapbox light style
            tooltip=tooltip,
        )
        st.pydeck_chart(deck)
    except Exception as e:
        st.error(f"❌ Map rendering error: {e}")
        import logging
        logging.getLogger(__name__).exception("Map rendering failed")

    # Color scale legend: value → color (matches circle coloring)
    def _fmt(x: float) -> str:
        if value_unit == "°C":
            return f"{x:.1f} °C"
        if value_unit == "kW":
            return f"{x:.0f} kW"
        return str(x)

    min_label = _fmt(data_min)
    max_label = _fmt(data_max)
    if (metric or "").strip().lower() in {"grid stress", "grid_stress"}:
        # Use level names for grid stress
        rev_stress = {v: k for k, v in GRID_STRESS_VALUES.items()}
        min_label = rev_stress.get(data_min, str(data_min)).capitalize()
        max_label = rev_stress.get(data_max, str(data_max)).capitalize()

    legend_html = f"""
    <div style="
        margin-top: 12px;
        padding: 12px 16px;
        background: rgba(26, 31, 58, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        font-family: inherit;
    ">
        <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-bottom: 8px;">
            <strong>{metric}</strong> — value range
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 11px; color: #7dd3fc; min-width: 56px;">{min_label}</span>
            <div style="
                flex: 1;
                height: 14px;
                border-radius: 7px;
                background: linear-gradient(90deg,
                    #0000ff 0%,
                    #ff0000 100%
                );
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
            "></div>
            <span style="font-size: 11px; color: #f87171; min-width: 56px; text-align: right;">{max_label}</span>
        </div>
        <div style="font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 6px;">
            Blue = lowest · Red = highest
        </div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    st.caption(
        f"📍 {len(building_ids)} buildings in Singapore CBD. Circle color reflects {metric} over range [{min_label}, {max_label}]."
    )
