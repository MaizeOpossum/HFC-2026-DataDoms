"""Grid stress signal generator for demand-response style events."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from thermal_commons_mvp.config.constants import GridStressLevel
from thermal_commons_mvp.models.grid_signal import GridStressSignal


class GridStressGenerator:
    """
    Produces GridStressSignal on a schedule or from a simple model.

    Used to mock demand-response events that drive agent bidding.
    """

    def __init__(
        self,
        cycle_minutes: int = 60,
        peak_level: str = GridStressLevel.HIGH,
    ) -> None:
        self.cycle_minutes = cycle_minutes
        self.peak_level = peak_level
        self._t0: Optional[datetime] = None

    def get_signal(self, at: Optional[datetime] = None) -> GridStressSignal:
        """
        Return current grid stress level based on a simple time cycle.

        Levels cycle: low -> medium -> high -> medium -> low over cycle_minutes.
        """
        now = at or datetime.now(timezone.utc)
        if self._t0 is None:
            self._t0 = now
        elapsed = (now - self._t0).total_seconds() / 60.0
        period = self.cycle_minutes
        phase = (elapsed % period) / max(period, 1e-6)
        if phase < 0.25:
            level = GridStressLevel.LOW
            value = 0.25
        elif phase < 0.5:
            level = GridStressLevel.MEDIUM
            value = 0.5
        elif phase < 0.75:
            level = self.peak_level
            value = 0.9
        else:
            level = GridStressLevel.MEDIUM
            value = 0.5
        return GridStressSignal(
            level=level,
            value=value,
            starts_at=now,
            ends_at=now + timedelta(minutes=period / 4),
        )
