"""BidGenerator: willingness to shed load vs. comfort cost -> Bid/Ask."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from thermal_commons_mvp.agents.ai_decision_engine import AIDecisionEngine, DecisionContext
from thermal_commons_mvp.config.constants import DEFAULT_BID_TTL_SEC
from thermal_commons_mvp.models.bids import Ask, Bid, BidStatus, BidType
from thermal_commons_mvp.models.grid_signal import GridStressSignal
from thermal_commons_mvp.models.telemetry import Telemetry


class BidGenerator:
    """
    Computes willingness to shed load vs. comfort cost and produces Bid/Ask.

    Used by MarketMakerAgent to submit orders.
    """

    def __init__(
        self,
        building_id: str,
        comfort_weight: float = 0.5,
        load_shed_price_base: float = 10.0,
        bid_ttl_sec: int = DEFAULT_BID_TTL_SEC,
        use_ai: bool = True,
    ) -> None:
        self.building_id = building_id
        self.comfort_weight = comfort_weight
        self.load_shed_price_base = load_shed_price_base
        self.bid_ttl_sec = bid_ttl_sec
        self.use_ai = use_ai
        self._ai_engine = AIDecisionEngine(building_id) if use_ai else None
        self._last_decision: Optional[str] = None

    def generate_ask(
        self,
        telemetry: Telemetry,
        grid_signal: Optional[GridStressSignal] = None,
        quantity_kwh: Optional[float] = None,
        trade_history: Optional[list] = None,
    ) -> Ask:
        """
        Create an Ask (offer to shed load) using AI decision-making if enabled.

        Higher grid stress raises willingness to shed and adjusts price.
        """
        if self.use_ai and self._ai_engine:
            # Use AI decision engine
            context = DecisionContext(
                building_id=self.building_id,
                telemetry=telemetry,
                grid_signal=grid_signal,
                recent_trades=trade_history or [],
                trade_history_count=len(trade_history) if trade_history else 0,
            )
            decision = self._ai_engine.analyze_and_decide(context)
            self._last_decision = decision.reasoning
            price = decision.ask_price
            q = decision.ask_quantity
        else:
            # Fallback to rule-based
            q = quantity_kwh or max(0.0, telemetry.power_load_kw * 0.1)
            stress_factor = (grid_signal.value if grid_signal else 0.0) or 0.5
            price = self.load_shed_price_base * (1.0 + stress_factor) * (1.0 - self.comfort_weight * 0.3)
        
        now = datetime.now(timezone.utc)
        return Ask(
            id=f"ask-{uuid.uuid4().hex[:8]}",
            building_id=self.building_id,
            price_per_kwh=max(0.01, price),
            quantity_kwh=q,
            bid_type=BidType.SELL,
            status=BidStatus.OPEN,
            created_at=now,
            expires_at=now + timedelta(seconds=self.bid_ttl_sec),
        )

    def generate_bid(
        self,
        telemetry: Telemetry,
        grid_signal: Optional[GridStressSignal] = None,
        quantity_kwh: Optional[float] = None,
        trade_history: Optional[list] = None,
    ) -> Bid:
        """Create a Bid (willingness to pay for capacity/reduction) using AI if enabled."""
        if self.use_ai and self._ai_engine:
            # Use AI decision engine
            context = DecisionContext(
                building_id=self.building_id,
                telemetry=telemetry,
                grid_signal=grid_signal,
                recent_trades=trade_history or [],
                trade_history_count=len(trade_history) if trade_history else 0,
            )
            decision = self._ai_engine.analyze_and_decide(context)
            self._last_decision = decision.reasoning
            price = decision.bid_price
            q = decision.bid_quantity
        else:
            # Fallback to rule-based
            q = quantity_kwh or max(0.0, telemetry.power_load_kw * 0.05)
            stress_factor = (grid_signal.value if grid_signal else 0.0) or 0.5
            price = self.load_shed_price_base * stress_factor * self.comfort_weight
        
        now = datetime.now(timezone.utc)
        return Bid(
            id=f"bid-{uuid.uuid4().hex[:8]}",
            building_id=self.building_id,
            price_per_kwh=max(0.01, price),
            quantity_kwh=q,
            bid_type=BidType.BUY,
            status=BidStatus.OPEN,
            created_at=now,
            expires_at=now + timedelta(seconds=self.bid_ttl_sec),
        )
    
    def get_last_reasoning(self) -> Optional[str]:
        """Return the AI's reasoning for the last decision."""
        return self._last_decision
