"""Energy-flow visualization: seller → animated energy bolt → buyer. Built for at-a-glance readability."""

import json
from typing import Any, Dict, List, Optional

import streamlit as st

from thermal_commons_mvp.dashboard.components.district_map_locations import (
    BUILDING_NAMES,
    SINGAPORE_BUILDING_LOCATIONS,
)

# How many flow strips to show (most recent trades)
MAX_STRIPS = 8


def render_agent_network(
    trades: Optional[List[Any]] = None,
    bid_to_building: Optional[Dict[str, str]] = None,
    ask_to_building: Optional[Dict[str, str]] = None,
    key: Optional[str] = None,
) -> None:
    """Render energy-flow strips: seller (left) → moving energy bolt → buyer (right)."""
    st.markdown("### ⚡ Energy in transit")

    network_viz_container = st.empty()

    trades = trades or []
    bid_to_building = bid_to_building or {}
    ask_to_building = ask_to_building or {}
    building_list = sorted(SINGAPORE_BUILDING_LOCATIONS.keys())
    building_to_index = {b: i for i, b in enumerate(building_list)}

    # Build recent strip data (last N trades) and mark which are new
    if "displayed_trades" not in st.session_state:
        st.session_state["displayed_trades"] = set()

    strip_trades: List[Dict[str, Any]] = []
    new_trade_keys: List[str] = []
    seen_keys = set()

    def _t(t, key, default=None):
        return t.get(key, default) if isinstance(t, dict) else getattr(t, key, default)

    for trade in reversed(trades[-MAX_STRIPS * 3:]):
        bid_id = _t(trade, "bid_id")
        ask_id = _t(trade, "ask_id")
        if not bid_id or not ask_id:
            continue
        buyer_id = bid_to_building.get(bid_id)
        seller_id = ask_to_building.get(ask_id)
        if not buyer_id or not seller_id or buyer_id == seller_id:
            continue
        if buyer_id not in building_to_index or seller_id not in building_to_index:
            continue

        exec_at = _t(trade, "executed_at")
        trade_key = f"{bid_id}_{ask_id}_{exec_at if exec_at is not None else id(trade)}"
        if trade_key in seen_keys:
            continue
        seen_keys.add(trade_key)

        qty = _t(trade, "quantity_kwh", 0.0) or 0.0
        price = _t(trade, "price_per_kwh", 0.0) or 0.0
        strip_trades.append({
            "tradeKey": trade_key,
            "sellerId": seller_id,
            "buyerId": buyer_id,
            "sellerName": BUILDING_NAMES.get(seller_id, seller_id),
            "buyerName": BUILDING_NAMES.get(buyer_id, buyer_id),
            "quantity": round(qty, 2),
            "pricePerKwh": round(price, 2),
        })
        if trade_key not in st.session_state["displayed_trades"]:
            st.session_state["displayed_trades"].add(trade_key)
            new_trade_keys.append(trade_key)

    strip_trades = strip_trades[:MAX_STRIPS]

    strips_json = json.dumps(strip_trades)
    new_keys_json = json.dumps(new_trade_keys)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; padding: 0; background: transparent; font-family: 'Inter', system-ui, sans-serif; }}
            #flow-root {{
                width: 100%;
                min-height: 420px;
                padding: 16px 0;
                background: linear-gradient(180deg, rgba(10,14,28,0.6) 0%, rgba(18,22,40,0.5) 100%);
                border-radius: 12px;
                border: 1px solid rgba(0, 212, 255, 0.15);
            }}
            .flow-strip {{
                display: flex;
                align-items: center;
                gap: 0;
                height: 52px;
                padding: 0 20px;
                margin: 6px 16px;
                border-radius: 10px;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                position: relative;
            }}
            .pill {{
                flex-shrink: 0;
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 160px;
            }}
            .pill-seller {{
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 180, 220, 0.15));
                color: #7dd3fc;
                border: 1px solid rgba(0, 212, 255, 0.35);
            }}
            .pill-buyer {{
                background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.15));
                color: #fcd34d;
                border: 1px solid rgba(251, 191, 36, 0.35);
            }}
            .track-wrap {{
                flex: 1;
                height: 24px;
                margin: 0 12px;
                position: relative;
                border-radius: 12px;
                background: rgba(255,255,255,0.04);
                overflow: hidden;
            }}
            .track-line {{
                position: absolute;
                left: 0;
                top: 50%;
                width: 100%;
                height: 2px;
                transform: translateY(-50%);
                background: linear-gradient(90deg, rgba(0,212,255,0.3), rgba(251,191,36,0.3));
                border-radius: 1px;
            }}
            .bolt {{
                position: absolute;
                left: 0;
                top: 50%;
                transform: translate(-50%, -50%);
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, #fff, #a5f3fc 40%, #0ea5e9 70%);
                box-shadow: 0 0 20px rgba(0,212,255,0.7), 0 0 40px rgba(0,212,255,0.4), inset 0 0 12px rgba(255,255,255,0.6);
                opacity: 0;
                transition: left 0.05s linear;
                pointer-events: none;
            }}
            .bolt.animating {{
                opacity: 1;
                animation: bolt-pulse 0.6s ease-in-out infinite alternate;
            }}
            .bolt.delivered {{
                opacity: 0.35;
                left: 100% !important;
            }}
            @keyframes bolt-pulse {{
                from {{ box-shadow: 0 0 16px rgba(0,212,255,0.6), 0 0 32px rgba(0,212,255,0.3); }}
                to {{ box-shadow: 0 0 24px rgba(0,212,255,0.9), 0 0 48px rgba(0,212,255,0.5); }}
            }}
            .qty {{
                flex-shrink: 0;
                font-size: 12px;
                font-weight: 700;
                color: rgba(255,255,255,0.9);
                background: rgba(0,0,0,0.35);
                padding: 6px 10px;
                border-radius: 6px;
                margin-left: 8px;
                min-width: 64px;
                text-align: center;
            }}
            .price {{
                flex-shrink: 0;
                font-size: 11px;
                font-weight: 600;
                color: rgba(34, 197, 94, 0.95);
                background: rgba(34, 197, 94, 0.12);
                padding: 6px 10px;
                border-radius: 6px;
                margin-left: 6px;
                min-width: 72px;
                text-align: center;
                border: 1px solid rgba(34, 197, 94, 0.25);
            }}
            .empty-state {{
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: rgba(255,255,255,0.5);
                font-size: 15px;
            }}
            .arrow-symbol {{
                flex-shrink: 0;
                width: 24px;
                text-align: center;
                color: rgba(255,255,255,0.4);
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div id="flow-root"></div>
        <script>
            (function() {{
                const strips = {strips_json};
                const newKeys = new Set({new_keys_json});

                const root = document.getElementById('flow-root');
                if (!strips.length) {{
                    root.innerHTML = '<div class="empty-state">No energy transfers yet. Trades will show here as buildings exchange energy.</div>';
                    return;
                }}

                const DURATION_MS = 2200;
                const HOLD_MS = 400;

                strips.forEach((s, idx) => {{
                    const strip = document.createElement('div');
                    strip.className = 'flow-strip';
                    strip.dataset.tradeKey = s.tradeKey;

                    const sellerPill = document.createElement('div');
                    sellerPill.className = 'pill pill-seller';
                    sellerPill.title = s.sellerName;
                    sellerPill.textContent = s.sellerName;

                    const arrow = document.createElement('div');
                    arrow.className = 'arrow-symbol';
                    arrow.textContent = '→';

                    const trackWrap = document.createElement('div');
                    trackWrap.className = 'track-wrap';
                    const trackLine = document.createElement('div');
                    trackLine.className = 'track-line';
                    const bolt = document.createElement('div');
                    bolt.className = 'bolt';
                    bolt.setAttribute('aria-hidden', 'true');
                    trackWrap.appendChild(trackLine);
                    trackWrap.appendChild(bolt);

                    const qtyEl = document.createElement('div');
                    qtyEl.className = 'qty';
                    qtyEl.textContent = s.quantity + ' kWh';

                    const priceEl = document.createElement('div');
                    priceEl.className = 'price';
                    priceEl.textContent = '$' + (s.pricePerKwh != null ? s.pricePerKwh.toFixed(2) : '0.00') + '/kWh';

                    const buyerPill = document.createElement('div');
                    buyerPill.className = 'pill pill-buyer';
                    buyerPill.title = s.buyerName;
                    buyerPill.textContent = s.buyerName;

                    strip.appendChild(sellerPill);
                    strip.appendChild(arrow);
                    strip.appendChild(trackWrap);
                    strip.appendChild(qtyEl);
                    strip.appendChild(priceEl);
                    strip.appendChild(buyerPill);
                    root.appendChild(strip);

                    const isNew = newKeys.has(s.tradeKey);
                    const trackWidth = trackWrap.offsetWidth || 200;

                    if (isNew) {{
                        bolt.classList.add('animating');
                        bolt.style.left = '0%';
                        let started = null;
                        function run(t) {{
                            if (started == null) started = t;
                            const elapsed = t - started;
                            if (elapsed >= DURATION_MS + HOLD_MS) {{
                                bolt.classList.remove('animating');
                                bolt.classList.add('delivered');
                                bolt.style.left = '100%';
                                return;
                            }}
                            let p = Math.min(1, elapsed / DURATION_MS);
                            bolt.style.left = (p * 100) + '%';
                            requestAnimationFrame(run);
                        }}
                        requestAnimationFrame(run);
                    }} else {{
                        bolt.classList.add('delivered');
                        bolt.style.left = '100%';
                    }}
                }});
            }})();
        </script>
    </body>
    </html>
    """

    h = max(260, min(520, 72 + len(strip_trades) * 64)) if strip_trades else 220
    with network_viz_container.container():
        st.components.v1.html(html_content, height=h)

    new_count = len(new_trade_keys)
    total = len(st.session_state.get("displayed_trades", set()))
    st.caption(
        f"⚡ Energy flows: seller → buyer. "
        f"{new_count} new this cycle • {total} total shown."
    )
