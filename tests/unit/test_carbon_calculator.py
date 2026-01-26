"""Unit tests for CarbonCalculator."""

import pytest
from thermal_commons_mvp.utils.carbon_calculator import CarbonCalculator


def test_kwh_to_kg_co2() -> None:
    calc = CarbonCalculator(kg_co2_per_kwh=0.5)
    assert calc.kwh_to_kg_co2(100.0) == 50.0


def test_kwh_to_tonnes_co2() -> None:
    calc = CarbonCalculator(kg_co2_per_kwh=1.0)
    assert calc.kwh_to_tonnes_co2(1000.0) == 1.0


def test_aggregate_savings_kg() -> None:
    calc = CarbonCalculator(kg_co2_per_kwh=0.4)
    assert calc.aggregate_savings_kg([10.0, 20.0, 5.0]) == 14.0
