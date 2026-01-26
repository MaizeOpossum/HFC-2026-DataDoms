"""Rule-based control agent for baseline stability."""

from typing import Any, List

from thermal_commons_mvp.agents.base_agent import BaseAgent
from thermal_commons_mvp.config.constants import DEFAULT_COOLING_SETPOINT_C
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)


class RbcAgent(BaseAgent):
    """
    Rule-based controller: keeps comfort vs. load in a stable baseline.

    Actions are cooling setpoint deltas or multipliers applied to default setpoint.
    """

    def __init__(self, cooling_setpoint_c: float = DEFAULT_COOLING_SETPOINT_C) -> None:
        self.cooling_setpoint_c = cooling_setpoint_c

    def act(self, obs: Any) -> Any:
        """
        Simple rules: if temp high, lower setpoint; if load high, relax setpoint.

        Returns a single action or list of floats for CityLearn.
        """
        if obs is None:
            return [0.0]
        arr = list(obs) if hasattr(obs, "__iter__") and not isinstance(obs, (str, bytes)) else [obs]
        temp = float(arr[0]) if len(arr) > 0 else 24.0
        _humidity = float(arr[1]) if len(arr) > 1 else 60.0
        power = float(arr[2]) if len(arr) > 2 else 50.0
        delta = 0.0
        if temp > self.cooling_setpoint_c + 1.0:
            delta = -0.5
        elif temp < self.cooling_setpoint_c - 1.0:
            delta = 0.5
        if power > 80.0:
            delta += 0.25
        return [delta]
