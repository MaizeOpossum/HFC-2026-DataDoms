"""Singapore district map: building locations colored by temperature, power, or grid stress."""

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# Singapore coordinates: CBD, Orchard, One North
SINGAPORE_BUILDING_LOCATIONS: Dict[str, Tuple[float, float]] = {
    "Building_A": (1.2947, 103.8585),   # Suntec City / Marina
    "Building_B": (1.3048, 103.8318),   # ION Orchard
    "Building_C": (1.2991, 103.7872),   # Mapletree Business City
}
SINGAPORE_CENTER = (1.3521, 103.8198)

# Value ranges for color scale (approx)
TEMP_RANGE = (20.0, 30.0)
POWER_RANGE = (0.0, 100.0)
GRID_STRESS_VALUES = {"low": 0.25, "medium": 0.5, "high": 0.9, "critical": 1.0}


def _norm_to_color(norm: float) -> List[int]:
    """Map normalized value in [0, 1] to [R, G, B, A]. Blue (low) → Red (high)."""
    norm = max(0.0, min(1.0, norm))
    if norm <= 0.5:
        r = 0
        g = int(255 * 2 * norm)
        b = 255
    else:
        r = int(255 * 2 * (norm - 0.5))
        g = 255
        b = int(255 * 2 * (1 - norm))
    return [r, g, b, 200]


def _get_value_and_label(
    building_id: str,
    telemetry: Optional[Dict[str, Any]],
    grid_stress: Optional[str],
    metric: str,
) -> Tuple[float, str]:
    """Return (normalized 0–1 value, label string) for the chosen metric."""
    if metric == "Temperature (°C)":
        if telemetry and building_id in telemetry:
            t = telemetry[building_id]
            v = getattr(t, "temp_c", 24.0)
            lo, hi = TEMP_RANGE
            norm = (v - lo) / (hi - lo) if hi > lo else 0.5
            return (norm, f"{v:.1f} °C")
        return (0.5, "—")
    if metric == "Power (kW)":
        if telemetry and building_id in telemetry:
            t = telemetry[building_id]
            v = getattr(t, "power_load_kw", 50.0)
            lo, hi = POWER_RANGE
            norm = (v - lo) / (hi - lo) if hi > lo else 0.5
            return (norm, f"{v:.1f} kW")
        return (0.5, "—")
    if metric == "Grid stress":
        v = GRID_STRESS_VALUES.get((grid_stress or "low").lower(), 0.25)
        return (v, grid_stress or "low")
    return (0.5, "—")


def render_district_map(
    telemetry_by_building: Optional[Dict[str, Any]] = None,
    grid_stress: Optional[str] = None,
) -> None:
    """Render Singapore map with buildings colored by selected metric."""
    st.subheader("District Map — Singapore")
    try:
        import pydeck as pdk
    except ImportError:
        st.warning("PyDeck not installed. Install with: pip install pydeck")
        return

    building_ids = list(SINGAPORE_BUILDING_LOCATIONS.keys())
    if not building_ids:
        st.info("No building locations configured.")
        return

    metric = st.selectbox(
        "Color buildings by",
        ["Temperature (°C)", "Power (kW)", "Grid stress"],
        key="district_map_metric",
    )
    tooltip = {"html": "<b>{name}</b><br/>{label}", "style": {"backgroundColor": "steelblue", "color": "white"}}

    rows: List[Dict[str, Any]] = []
    for bid in building_ids:
        lat, lon = SINGAPORE_BUILDING_LOCATIONS[bid]
        norm, label = _get_value_and_label(bid, telemetry_by_building, grid_stress, metric)
        color = _norm_to_color(norm)
        rows.append({
            "lat": lat,
            "lon": lon,
            "name": bid,
            "label": label,
            "color": color,
            "radius": 180,
        })

    view = pdk.ViewState(
        latitude=SINGAPORE_CENTER[0],
        longitude=SINGAPORE_CENTER[1],
        zoom=11,
        pitch=40,
        bearing=0,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=rows,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        radius_min_pixels=8,
        radius_max_pixels=120,
    )
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip=tooltip,
    )
    st.pydeck_chart(deck)

    # Legend
    st.caption("Color scale: blue = low, green = mid, red = high. Buildings: A — Marina, B — Orchard, C — One North.")
