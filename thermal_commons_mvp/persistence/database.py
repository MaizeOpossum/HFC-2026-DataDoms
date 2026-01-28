"""SQLite database for persisting trades and historical data."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from thermal_commons_mvp.models.trades import Trade


class StateDatabase:
    """SQLite database for persisting simulation state."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        if db_path is None:
            # Default to data directory in project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "cool_state.db"
        
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    bid_id TEXT NOT NULL,
                    ask_id TEXT NOT NULL,
                    price_per_kwh REAL NOT NULL,
                    quantity_kwh REAL NOT NULL,
                    executed_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS simulation_history (
                    step INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    telemetry_json TEXT NOT NULL,
                    grid_stress TEXT NOT NULL,
                    total_kwh_saved REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (step)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_executed_at ON trades(executed_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_step ON simulation_history(step)
            """)
            
            conn.commit()

    def save_trade(self, trade: Trade) -> None:
        """Save a trade to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO trades 
                (id, bid_id, ask_id, price_per_kwh, quantity_kwh, executed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trade.id,
                trade.bid_id,
                trade.ask_id,
                trade.price_per_kwh,
                trade.quantity_kwh,
                trade.executed_at.isoformat() if trade.executed_at else datetime.now(timezone.utc).isoformat(),
            ))
            conn.commit()

    def save_trades(self, trades: List[Trade]) -> None:
        """Save multiple trades in a transaction."""
        with sqlite3.connect(self.db_path) as conn:
            for trade in trades:
                conn.execute("""
                    INSERT OR REPLACE INTO trades 
                    (id, bid_id, ask_id, price_per_kwh, quantity_kwh, executed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trade.id,
                    trade.bid_id,
                    trade.ask_id,
                    trade.price_per_kwh,
                    trade.quantity_kwh,
                    trade.executed_at.isoformat() if trade.executed_at else datetime.now(timezone.utc).isoformat(),
                ))
            conn.commit()

    def get_trades(self, limit: Optional[int] = None) -> List[Trade]:
        """Retrieve trades from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM trades ORDER BY executed_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query).fetchall()
            trades = []
            for row in rows:
                trades.append(Trade(
                    id=row["id"],
                    bid_id=row["bid_id"],
                    ask_id=row["ask_id"],
                    price_per_kwh=row["price_per_kwh"],
                    quantity_kwh=row["quantity_kwh"],
                    executed_at=datetime.fromisoformat(row["executed_at"]) if row["executed_at"] else None,
                ))
            return trades

    def save_history_snapshot(
        self,
        step: int,
        timestamp: datetime,
        telemetry: Dict[str, Any],
        grid_stress: str,
        total_kwh_saved: float,
    ) -> None:
        """Save a simulation history snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            # Convert telemetry to JSON
            # Handle both Telemetry objects and dicts
            telemetry_dict = {}
            for bid, t in telemetry.items():
                if hasattr(t, 'building_id'):
                    # It's a Telemetry object
                    telemetry_dict[bid] = {
                        "building_id": t.building_id,
                        "temp_c": t.temp_c,
                        "humidity_pct": t.humidity_pct,
                        "power_load_kw": t.power_load_kw,
                        "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                    }
                else:
                    # It's already a dict
                    telemetry_dict[bid] = t
            
            telemetry_json = json.dumps(telemetry_dict, default=str)
            
            conn.execute("""
                INSERT OR REPLACE INTO simulation_history
                (step, timestamp, telemetry_json, grid_stress, total_kwh_saved)
                VALUES (?, ?, ?, ?, ?)
            """, (
                step,
                timestamp.isoformat(),
                telemetry_json,
                grid_stress,
                total_kwh_saved,
            ))
            conn.commit()

    def get_history_snapshot(self, step: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific history snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM simulation_history WHERE step = ?",
                (step,)
            ).fetchone()
            
            if not row:
                return None
            
            return {
                "step": row["step"],
                "timestamp": datetime.fromisoformat(row["timestamp"]),
                "telemetry": json.loads(row["telemetry_json"]),
                "grid_stress": row["grid_stress"],
                "total_kwh_saved": row["total_kwh_saved"],
            }

    def get_recent_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent history snapshots."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM simulation_history ORDER BY step DESC LIMIT ?",
                (limit,)
            ).fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "step": row["step"],
                    "timestamp": datetime.fromisoformat(row["timestamp"]),
                    "telemetry": json.loads(row["telemetry_json"]),
                    "grid_stress": row["grid_stress"],
                    "total_kwh_saved": row["total_kwh_saved"],
                })
            
            # Return in chronological order
            return list(reversed(history))

    def clear_old_data(self, keep_last_n_steps: int = 1000) -> None:
        """Clear old data, keeping only the most recent N steps."""
        with sqlite3.connect(self.db_path) as conn:
            # Delete old history
            conn.execute("""
                DELETE FROM simulation_history
                WHERE step NOT IN (
                    SELECT step FROM simulation_history
                    ORDER BY step DESC
                    LIMIT ?
                )
            """, (keep_last_n_steps,))
            
            # Keep trades from recent history steps
            max_step = conn.execute("SELECT MAX(step) FROM simulation_history").fetchone()[0]
            if max_step:
                # Keep trades from last N steps (rough estimate)
                conn.execute("""
                    DELETE FROM trades
                    WHERE executed_at < (
                        SELECT MIN(timestamp) FROM simulation_history
                        WHERE step > ? - ?
                    )
                """, (max_step, keep_last_n_steps))
            
            conn.commit()
