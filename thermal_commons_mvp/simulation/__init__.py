"""
Simulation layer: Grid stress generator and optional CityLearn integration.

CityLearn integration is optional (shelved) - the dashboard works with mock telemetry.
"""

from thermal_commons_mvp.simulation.city_gym import CityLearnGym
from thermal_commons_mvp.simulation.grid_stress import GridStressGenerator

__all__ = ["CityLearnGym", "GridStressGenerator"]
