"""Trade log table / feed."""

from typing import List, Optional

import pandas as pd
import streamlit as st


def _sample_trades() -> pd.DataFrame:
    return pd.DataFrame([
        {"id": "t1", "bid_id": "b1", "ask_id": "a1", "price": 12.5, "qty_kwh": 5.0},
        {"id": "t2", "bid_id": "b2", "ask_id": "a2", "price": 11.0, "qty_kwh": 3.0},
    ])


def render_trade_log(trades: Optional[List[object]] = None) -> None:
    """Render trade log. If trades is provided, show those (newest last); else sample."""
    st.subheader("Trade Log")
    if trades and len(trades) > 0:
        rows = []
        for t in trades[-50:]:  # last 50
            rows.append({
                "id": getattr(t, "id", ""),
                "bid_id": getattr(t, "bid_id", ""),
                "ask_id": getattr(t, "ask_id", ""),
                "price": getattr(t, "price_per_kwh", 0),
                "qty_kwh": getattr(t, "quantity_kwh", 0),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Showing last {len(rows)} of {len(trades)} trades")
    else:
        df = _sample_trades()
        st.dataframe(df, use_container_width=True, hide_index=True)
