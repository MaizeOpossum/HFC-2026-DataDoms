"""Unit tests for RbcAgent."""

import pytest
from thermal_commons_mvp.agents.rbc_agent import RbcAgent


def test_act_returns_list() -> None:
    agent = RbcAgent()
    out = agent.act([25.0, 60.0, 50.0])
    assert isinstance(out, list)
    assert len(out) >= 1


def test_act_high_temp_lowers_setpoint() -> None:
    agent = RbcAgent(cooling_setpoint_c=24.0)
    out = agent.act([26.0, 60.0, 50.0])  # temp > setpoint+1
    assert out[0] < 0


def test_act_low_temp_raises_setpoint() -> None:
    agent = RbcAgent(cooling_setpoint_c=24.0)
    out = agent.act([22.0, 60.0, 50.0])
    assert out[0] > 0
