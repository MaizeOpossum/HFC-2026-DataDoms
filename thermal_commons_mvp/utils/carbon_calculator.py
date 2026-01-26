"""Carbon savings and kWh-to-CO2 conversion."""

from dataclasses import dataclass
from typing import Optional

from thermal_commons_mvp.config import get_settings


@dataclass
class CarbonCalculator:
    """Converts kWh to tCO2 and aggregates real-time savings."""

    kg_co2_per_kwh: Optional[float] = None

    def __post_init__(self) -> None:
        if self.kg_co2_per_kwh is None:
            self.kg_co2_per_kwh = get_settings().carbon_factor_kg_per_kwh

    def kwh_to_kg_co2(self, kwh: float) -> float:
        """Convert energy (kWh) to kg CO2."""
        return kwh * self.kg_co2_per_kwh

    def kwh_to_tonnes_co2(self, kwh: float) -> float:
        """Convert energy (kWh) to tonnes CO2."""
        return self.kwh_to_kg_co2(kwh) / 1000.0

    def aggregate_savings_kg(self, kwh_savings_list: list[float]) -> float:
        """Sum of kg CO2 saved from a list of kWh savings."""
        return sum(self.kwh_to_kg_co2(k) for k in kwh_savings_list)
