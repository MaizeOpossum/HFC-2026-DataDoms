"""Stream or poll sensor telemetry (temp, humidity, power_load)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from thermal_commons_mvp.api.dependencies import get_driver

router = APIRouter()


class TelemetryResponse(BaseModel):
    building_id: str
    temp_c: float
    humidity_pct: float
    power_load_kw: float
    timestamp: Optional[datetime] = None


@router.get("/{building_id}", response_model=TelemetryResponse)
def get_telemetry(building_id: str, driver=Depends(get_driver)) -> TelemetryResponse:
    """Return current telemetry for a building."""
    t = driver.read_telemetry(building_id)
    return TelemetryResponse(
        building_id=t.building_id,
        temp_c=t.temp_c,
        humidity_pct=t.humidity_pct,
        power_load_kw=t.power_load_kw,
        timestamp=t.timestamp,
    )
