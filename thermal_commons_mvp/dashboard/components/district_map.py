"""3D district map using PyDeck."""

import streamlit as st

try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    PYDECK_AVAILABLE = False


def render_district_map() -> None:
    """Render 3D map for district visualization."""
    st.subheader("District Map")
    if not PYDECK_AVAILABLE:
        st.warning("PyDeck not installed. Install with: pip install pydeck")
        return
    # Singapore central area placeholder
    view_state = pdk.ViewState(
        latitude=1.3521,
        longitude=103.8198,
        zoom=11,
        pitch=45,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"lat": 1.3521, "lon": 103.8198, "radius": 500, "color": [200, 30, 0, 160]}],
        get_position="[lon, lat]",
        get_radius="radius",
        get_color="color",
        pickable=True,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9"))
