"""Trade log table / feed."""

from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from thermal_commons_mvp.dashboard.components.district_map_locations import BUILDING_NAMES


def render_trade_log(
    trades: Optional[List[object]] = None,
    bid_to_building: Optional[Dict[str, str]] = None,
    ask_to_building: Optional[Dict[str, str]] = None,
) -> None:
    """Render trade log with building names and prices in a labeled table with overflow."""
    # Compact container
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
    
    st.markdown("### 💱 Recent Trades")
    
    bid_to_building = bid_to_building or {}
    ask_to_building = ask_to_building or {}
    
    if trades and len(trades) > 0:
        # Build table data
        table_rows = []
        for t in reversed(trades[-50:]):  # last 50, reversed to show newest first
            bid_id = getattr(t, "bid_id", "")
            ask_id = getattr(t, "ask_id", "")
            price = getattr(t, "price_per_kwh", 0.0)
            quantity = getattr(t, "quantity_kwh", 0.0)
            
            # Get building IDs from mappings
            bid_building_id = bid_to_building.get(bid_id, "Unknown")
            ask_building_id = ask_to_building.get(ask_id, "Unknown")
            
            # Get building names
            bid_building_name = BUILDING_NAMES.get(bid_building_id, bid_building_id)
            ask_building_name = BUILDING_NAMES.get(ask_building_id, ask_building_id)
            
            # Format as requested: [building name] - [price]
            table_rows.append({
                "Seller (Ask)": f"{ask_building_name} - ${price:.2f}/kWh",
                "Buyer (Bid)": f"{bid_building_name} - ${price:.2f}/kWh",
                "Quantity": f"{quantity:.2f} kWh",
                "Price": f"${price:.2f}",
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_rows)
        
        # Display table with fixed height and overflow
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400,  # Fixed height to prevent page stretching
        )
        
        st.caption(f"Showing last {len(table_rows)} of {len(trades)} trades (newest first)")
    else:
        # Empty state with placeholder table
        empty_df = pd.DataFrame({
            "Seller (Ask)": ["No trades yet"],
            "Buyer (Bid)": ["Trades will appear here"],
            "Quantity": ["—"],
            "Price": ["—"],
        })
        st.dataframe(empty_df, use_container_width=True, hide_index=True, height=100)
        st.caption("Waiting for trades...")
    
    st.markdown("</div>", unsafe_allow_html=True)
