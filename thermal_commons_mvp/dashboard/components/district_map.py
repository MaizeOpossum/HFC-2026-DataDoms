"""Singapore district map: building locations colored by temperature, power, or grid stress."""

import os
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.dashboard.components.district_map_locations import (
    BUILDING_NAMES,
    SINGAPORE_BUILDING_LOCATIONS,
)

# Load Mapbox token at module level so it's available before PyDeck is used
def _load_mapbox_token() -> Optional[str]:
    """Load Mapbox token from environment or settings."""
    token = os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        try:
            settings = get_settings()
            token = settings.mapbox_access_token
        except Exception:
            pass
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("MAPBOX_ACCESS_TOKEN")
        except (ImportError, Exception):
            pass
    if token:
        # Clean and validate token format
        token = str(token).strip()
        # Mapbox tokens typically start with "pk."
        if token and (token.startswith("pk.") or len(token) > 20):
            os.environ["MAPBOX_ACCESS_TOKEN"] = token
            return token
    return None

_MAPBOX_TOKEN = _load_mapbox_token()

# Building locations imported from district_map_locations.py (50 buildings)
SINGAPORE_CENTER = (1.30, 103.82)

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
    # Group map in a styled container
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
    
    st.markdown("### 🗺️ CBD District Map — Singapore")
    
    try:
        import pydeck as pdk
    except ImportError:
        st.warning("PyDeck not installed. Install with: pip install pydeck")
        return

    # Check if token is available (Streamlit reads from .streamlit/config.toml)
    # Also check environment as fallback
    mapbox_token = _MAPBOX_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Streamlit automatically reads from .streamlit/config.toml [mapbox] token
    # So even if env var isn't set, Streamlit should have it
    token_status = "✅ Mapbox token configured (check .streamlit/config.toml if map doesn't show)"
    
    if not mapbox_token:
        token_status = "⚠️ Token not in env - ensure it's in .streamlit/config.toml"

    building_ids = list(SINGAPORE_BUILDING_LOCATIONS.keys())
    if not building_ids:
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Put color selector and map style side by side
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox(
            "🎨 Color buildings by",
            ["Temperature (°C)", "Power (kW)", "Grid stress"],
            key="district_map_metric",
        )
    tooltip = {"html": "<b>{name}</b><br/>{label}", "style": {"backgroundColor": "steelblue", "color": "white"}}

    rows: List[Dict[str, Any]] = []
    for bid in building_ids:
        lat, lon = SINGAPORE_BUILDING_LOCATIONS[bid]
        norm, label = _get_value_and_label(bid, telemetry_by_building, grid_stress, metric)
        color = _norm_to_color(norm)
        # Use real building name if available, otherwise use building ID
        building_name = BUILDING_NAMES.get(bid, bid)
        rows.append({
            "lat": lat,
            "lon": lon,
            "name": building_name,
            "label": f"{building_name}<br/>{label}",
            "color": color,
            "radius": 100,  # meters (smaller radius for CBD buildings)
        })

    # Center on CBD (Marina Bay / Raffles Place area)
    view = pdk.ViewState(
        latitude=1.2815,  # CBD center (Marina Bay / Raffles Place)
        longitude=103.8515,  # CBD center
        zoom=15,  # Zoomed in to show CBD buildings clearly
        pitch=45,  # 3D tilt for better visibility
        bearing=0,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=rows,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        radius_min_pixels=5,
        radius_max_pixels=80,  # Smaller markers for 50 buildings
        stroked=True,
        get_line_color=[255, 255, 255, 200],
        line_width_min_pixels=2,
    )
    
    with col2:
        map_style = st.selectbox(
            "🗺️ Map style",
            ["Satellite", "Satellite with labels", "Terrain", "Street", "Light (no token)"],
            key="map_style_selector",
            index=0,
        )
    style_map = {
        "Satellite": "mapbox://styles/mapbox/satellite-v9",  # Google Earth-like satellite view
        "Satellite with labels": "mapbox://styles/mapbox/satellite-streets-v12",  # Satellite with street labels
        "Terrain": "mapbox://styles/mapbox/outdoors-v12",  # Topographic/terrain view
        "Street": "mapbox://styles/mapbox/streets-v12",  # Standard street map
        "Light (no token)": "light",  # Fallback that doesn't require token
    }
    
    selected_style = style_map.get(map_style, "light")
    
    # Streamlit reads Mapbox token from .streamlit/config.toml [mapbox] token
    # So we can use Mapbox styles even if env var isn't set
    # Only fallback if user explicitly selects "Light (no token)"
    
    # Create deck with the selected style
    try:
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_style=selected_style,
            tooltip=tooltip,
        )
        st.caption(token_status)
        st.pydeck_chart(deck)
    except Exception as e:
        st.error(f"❌ Map rendering error: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Ensure `.streamlit/config.toml` exists with `[mapbox] token = "your_token"`
        2. **Restart Streamlit** after creating/editing config.toml
        3. Check browser console (F12) for JavaScript errors
        4. Try selecting "Light (no token)" style as a fallback
        """)
        # Try fallback
        try:
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                map_style="light",
                tooltip=tooltip,
            )
            st.pydeck_chart(deck)
            st.caption("Using fallback 'light' style")
        except Exception as e2:
            st.error(f"Fallback also failed: {e2}")
    
    # Note about Mapbox API key if map doesn't show
    with st.expander("ℹ️ Map not showing or only black/white?"):
        st.markdown("""
        **Streamlit requires the Mapbox token in `.streamlit/config.toml`, not just `.env`!**
        
        The token has been added to `.streamlit/config.toml`. If the map still doesn't show:
        
        1. **Restart Streamlit** (the config file is read at startup)
        2. Check that `.streamlit/config.toml` exists with:
           ```toml
           [mapbox]
           token = "pk.your_token_here"
           ```
        3. Verify your token is valid at: https://account.mapbox.com/access-tokens/
        4. If using satellite styles, ensure your token has the right permissions
        
        **Note:** Streamlit's `st.pydeck_chart()` reads the token from `.streamlit/config.toml`, 
        not from environment variables or `.env` files.
        """)

    # Close container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Legend (outside container)
    st.caption(
        f"Color scale: blue = low, green = mid, red = high. "
        f"50 real buildings in Singapore CBD: Marina Bay Financial Centre, Raffles Place, Shenton Way, and surrounding areas."
    )
