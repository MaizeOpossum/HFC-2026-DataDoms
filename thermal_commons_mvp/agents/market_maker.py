"""Market-making agent: submits bids/asks based on local state and grid stress."""

from typing import Any, List, Optional

from thermal_commons_mvp.agents.base_agent import BaseAgent
from thermal_commons_mvp.agents.bid_generator import BidGenerator
from thermal_commons_mvp.models.bids import Ask, Bid
from thermal_commons_mvp.models.grid_signal import GridStressSignal
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)


class MarketMakerAgent(BaseAgent):
    """
    Market-making logic: uses BidGenerator to produce Bid/Ask from local state
    and grid stress, and can submit them to a TradeExecution/order book.
    """

    def __init__(
        self,
        building_id: str,
        bid_generator: Optional[BidGenerator] = None,
    ) -> None:
        self.building_id = building_id
        self._bid_gen = bid_generator or BidGenerator(building_id=building_id)

    def act(self, obs: Any) -> Any:
        """Return a no-op action for CityLearn; use submit_orders for market side."""
        return [0.0]

    def submit_orders(
        self,
        telemetry: Telemetry,
        grid_signal: Optional[GridStressSignal] = None,
    ) -> tuple[Bid | None, Ask | None]:
        """
        Generate and return a bid and ask for the current state.
        Caller (or TradeExecution) is responsible for submitting to the book.
        """
        bid = self._bid_gen.generate_bid(telemetry, grid_signal)
        ask = self._bid_gen.generate_ask(telemetry, grid_signal)
        return (bid, ask)
