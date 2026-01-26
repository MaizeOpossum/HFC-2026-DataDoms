"""Abstract base agent for RLlib/CityLearn and custom control."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from thermal_commons_mvp.models.telemetry import Telemetry


class BaseAgent(ABC):
    """
    Abstract agent interface: act(obs) -> action.

    Compatible with Gymnasium/RLlib and custom step loops.
    """

    @abstractmethod
    def act(self, obs: Any) -> Any:
        """
        Map observation to action.

        Args:
            obs: Observation (e.g. list/array of state variables, or Telemetry).

        Returns:
            Action (e.g. setpoints, or list of floats for CityLearn).
        """
        ...

    def act_from_telemetry(self, telemetry: Telemetry) -> Any:
        """Convenience: build obs from Telemetry and call act."""
        obs = (telemetry.temp_c, telemetry.humidity_pct, telemetry.power_load_kw)
        return self.act(obs)
