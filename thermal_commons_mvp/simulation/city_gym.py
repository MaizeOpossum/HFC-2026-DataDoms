"""CityLearn environment wrapper: Building_5 tropical preset, step() -> [temp, humidity, power_load]."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.config.constants import DEFAULT_BUILDING_ID
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)

# CityLearn is optional at import time for environments that only run BACnet/dashboard
try:
    from citylearn.citylearn import CityLearnEnv
    from citylearn.schema import Schema

    CITYLEARN_AVAILABLE = True
except ImportError:
    CityLearnEnv = object  # type: ignore[misc, assignment]
    Schema = object  # type: ignore[misc, assignment]
    CITYLEARN_AVAILABLE = False


class CityLearnGym:
    """
    Wrapper around CityLearn with Building_5 (tropical) preset.

    Exposes step() returning (temp_c, humidity_pct, power_load_kw) and optional
    Telemetry for a single building.
    """

    def __init__(
        self,
        schema_path: Optional[Path] = None,
        building_id: Optional[str] = None,
    ) -> None:
        self._schema_path = schema_path or get_settings().citylearn_schema_path
        self._building_id = building_id or get_settings().citylearn_building_id or DEFAULT_BUILDING_ID
        self._env: Any = None
        self._current_step = 0

    def reset(self) -> Tuple[float, float, float]:
        """Reset environment and return initial (temp, humidity, power_load)."""
        if not CITYLEARN_AVAILABLE:
            logger.warning("CityLearn not installed; returning mock values.")
            return (24.0, 60.0, 50.0)
        if self._env is None:
            self._init_env()
        obs, _ = self._env.reset()
        self._current_step = 0
        return self._obs_to_telemetry_tuple(obs)

    def step(self, action: Optional[List[float]] = None) -> Tuple[float, float, float]:
        """
        Advance one step. Returns (temp_c, humidity_pct, power_load_kw).

        If action is None, a no-op or default action is used.
        """
        if not CITYLEARN_AVAILABLE:
            self._current_step += 1
            return (24.0, 60.0, 50.0)
        if self._env is None:
            self._init_env()
        if action is None:
            action = [0.0] * self._env.action_space.shape[0] if hasattr(self._env, "action_space") else []
        obs, _reward, terminated, truncated, _info = self._env.step(action)
        self._current_step += 1
        return self._obs_to_telemetry_tuple(obs)

    def to_telemetry(self, temp_c: float, humidity_pct: float, power_load_kw: float) -> Telemetry:
        """Build a Telemetry instance from step() outputs."""
        from datetime import datetime, timezone

        return Telemetry(
            building_id=self._building_id,
            temp_c=temp_c,
            humidity_pct=humidity_pct,
            power_load_kw=power_load_kw,
            timestamp=datetime.now(timezone.utc),
        )

    def _init_env(self) -> None:
        if self._schema_path and self._schema_path.exists():
            self._env = CityLearnEnv(schema=Schema(str(self._schema_path)))
        else:
            # Fallback: use CityLearn's built-in demo if available
            logger.warning("No CityLearn schema path; using placeholder. Set CITYLEARN_SCHEMA_PATH.")
            self._env = _make_placeholder_env()
        self._env.reset()

    def _obs_to_telemetry_tuple(self, obs: Any) -> Tuple[float, float, float]:
        """Map raw observation vector to (temp, humidity, power_load)."""
        if obs is None or (hasattr(obs, "__len__") and len(obs) < 3):
            return (24.0, 60.0, 50.0)
        arr = obs if hasattr(obs, "__getitem__") else list(obs)
        return (float(arr[0]), float(arr[1]), float(arr[2]))


def _make_placeholder_env() -> Any:
    """Return a minimal placeholder when CityLearn schema is missing."""
    if not CITYLEARN_AVAILABLE:
        return None
    try:
        from citylearn.data import DataSet

        ds = DataSet.get_tropical_data_set("citylearn_tropical_1building")
        if ds and hasattr(ds, "get_schema"):
            return CityLearnEnv(schema=ds.get_schema())
    except Exception as e:
        logger.warning("Placeholder CityLearn env failed: %s", e)
    return None


def main() -> None:
    """CLI entrypoint: run a few simulation steps and print telemetry."""
    gym = CityLearnGym()
    t, h, p = gym.reset()
    print(f"reset -> temp={t}, humidity={h}, power_load={p}")
    for _ in range(3):
        t, h, p = gym.step()
        print(f"step  -> temp={t}, humidity={h}, power_load={p}")


if __name__ == "__main__":
    main()
