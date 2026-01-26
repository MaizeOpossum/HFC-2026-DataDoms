"""Trade log table / feed."""

import streamlit as st
import pandas as pd

# Placeholder; in production, fetch from /market/trades
def _sample_trades() -> pd.DataFrame:
    return pd.DataFrame([
        {"id": "t1", "bid_id": "b1", "ask_id": "a1", "price": 12.5, "qty_kwh": 5.0},
        {"id": "t2", "bid_id": "b2", "ask_id": "a2", "price": 11.0, "qty_kwh": 3.0},
    ])


def render_trade_log() -> None:
    """Render trade log in the right column."""
    st.subheader("Trade Log")
    df = _sample_trades()
    st.dataframe(df, use_container_width=True, hide_index=True)
