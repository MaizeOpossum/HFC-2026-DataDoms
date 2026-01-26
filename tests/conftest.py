"""Pytest fixtures and config."""

import pytest


@pytest.fixture
def sample_telemetry():
    """Sample Telemetry for tests."""
    from datetime import datetime, timezone
    from thermal_commons_mvp.models.telemetry import Telemetry
    return Telemetry(
        building_id="Building_5",
        temp_c=24.0,
        humidity_pct=60.0,
        power_load_kw=50.0,
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_grid_signal():
    """Sample GridStressSignal for tests."""
    from datetime import datetime, timezone
    from thermal_commons_mvp.models.grid_signal import GridStressSignal
    return GridStressSignal(level="high", value=0.8, starts_at=datetime.now(timezone.utc))
