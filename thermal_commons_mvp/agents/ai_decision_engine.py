"""AI Decision Engine: adaptive reasoning, learning from history, strategic bidding."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

from thermal_commons_mvp.models.grid_signal import GridStressSignal
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.models.trades import Trade
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class DecisionContext:
    """Context for AI decision-making: current state, history, market conditions."""

    building_id: str
    telemetry: Telemetry
    grid_signal: Optional[GridStressSignal]
    recent_trades: List[Trade] = field(default_factory=list)
    trade_history_count: int = 0
    successful_trades: int = 0
    avg_price_paid: float = 0.0
    avg_price_received: float = 0.0


@dataclass
class AIDecision:
    """AI decision output with reasoning."""

    bid_price: float
    ask_price: float
    bid_quantity: float
    ask_quantity: float
    reasoning: str
    strategy: str
    confidence: float  # 0-1


class AIDecisionEngine:
    """
    AI-powered decision engine that:
    - Learns from trade history
    - Adapts bidding strategy based on market conditions
    - Uses multi-factor analysis (temp, power, grid stress, historical performance)
    - Provides reasoning for decisions
    """

    def __init__(self, building_id: str):
        self.building_id = building_id
        self._trade_history: List[Trade] = []
        self._strategy_history: List[str] = []
        self._adaptation_factor = 0.1  # Learning rate

    def analyze_and_decide(self, context: DecisionContext) -> AIDecision:
        """
        Analyze current state and make an AI-driven decision with reasoning.
        
        Strategy selection:
        - Aggressive: High grid stress + high power → maximize load shedding
        - Conservative: Low grid stress + comfortable temp → minimize disruption
        - Opportunistic: Recent successful trades → replicate strategy
        - Adaptive: Learn from market feedback
        """
        t = context.telemetry
        grid = context.grid_signal
        grid_value = grid.value if grid else 0.5
        grid_level = (grid.level if grid else "medium").lower()

        # Multi-factor analysis
        temp_factor = max(0.0, min(1.0, (t.temp_c - 22.0) / 6.0))  # Normalize 22-28°C
        power_factor = min(1.0, t.power_load_kw / 80.0)  # Normalize to 80kW max
        stress_factor = grid_value

        # Learning from history
        recent_success_rate = (
            context.successful_trades / max(1, context.trade_history_count)
            if context.trade_history_count > 0
            else 0.5
        )

        # Strategy selection (AI decision-making)
        if grid_level in ("high", "critical") and power_factor > 0.7:
            strategy = "aggressive"
            reasoning = (
                f"AI Decision: High grid stress ({grid_level}) + high power load ({t.power_load_kw:.1f}kW) "
                f"→ Aggressive strategy to maximize load shedding and grid support."
            )
            bid_price = 8.0 + stress_factor * 12.0 + temp_factor * 5.0
            ask_price = 6.0 + stress_factor * 10.0
            bid_qty = t.power_load_kw * 0.15  # Willing to buy more capacity
            ask_qty = t.power_load_kw * 0.20  # Offer to shed more
            confidence = 0.85

        elif grid_level == "low" and temp_factor < 0.3:
            strategy = "conservative"
            reasoning = (
                f"AI Decision: Low grid stress + comfortable temp ({t.temp_c:.1f}°C) "
                f"→ Conservative strategy to maintain comfort, minimal market participation."
            )
            bid_price = 3.0 + stress_factor * 4.0
            ask_price = 8.0 + (1.0 - temp_factor) * 5.0  # Higher ask when comfortable
            bid_qty = t.power_load_kw * 0.05
            ask_qty = t.power_load_kw * 0.08
            confidence = 0.75

        elif recent_success_rate > 0.6 and context.avg_price_received > 0:
            strategy = "opportunistic"
            reasoning = (
                f"AI Decision: High success rate ({recent_success_rate:.0%}) + avg price ${context.avg_price_received:.2f}/kWh "
                f"→ Replicating successful strategy, adjusting prices by {self._adaptation_factor:.0%}."
            )
            base_price = context.avg_price_received * (1.0 + self._adaptation_factor)
            bid_price = base_price * 0.9
            ask_price = base_price * 1.1
            bid_qty = t.power_load_kw * 0.10
            ask_qty = t.power_load_kw * 0.12
            confidence = 0.80

        else:
            strategy = "adaptive"
            # Weighted decision based on multiple factors
            urgency = (stress_factor * 0.4) + (power_factor * 0.3) + (temp_factor * 0.3)
            reasoning = (
                f"AI Decision: Adaptive strategy. Urgency score: {urgency:.2f} "
                f"(stress: {stress_factor:.2f}, power: {power_factor:.2f}, temp: {temp_factor:.2f}). "
                f"Balancing grid needs with building comfort."
            )
            bid_price = 5.0 + urgency * 8.0
            ask_price = 7.0 + urgency * 6.0
            bid_qty = t.power_load_kw * (0.08 + urgency * 0.07)
            ask_qty = t.power_load_kw * (0.10 + urgency * 0.08)
            confidence = 0.70

        # Ensure minimums
        bid_price = max(0.5, bid_price)
        ask_price = max(0.5, ask_price)
        bid_qty = max(1.0, bid_qty)
        ask_qty = max(1.0, ask_qty)

        self._strategy_history.append(strategy)

        return AIDecision(
            bid_price=round(bid_price, 2),
            ask_price=round(ask_price, 2),
            bid_quantity=round(bid_qty, 1),
            ask_quantity=round(ask_qty, 1),
            reasoning=reasoning,
            strategy=strategy,
            confidence=confidence,
        )

    def update_from_trades(self, trades: List[Trade], building_id: str) -> None:
        """Learn from executed trades to improve future decisions."""
        # Track trades where this building participated (via bid_id or ask_id matching)
        # Note: In a real system, we'd need to look up which building submitted which bid/ask
        # For now, we track all trades as learning context
        if trades:
            self._trade_history.extend(trades)
            # Keep last 50 trades for learning
            self._trade_history = self._trade_history[-50:]
