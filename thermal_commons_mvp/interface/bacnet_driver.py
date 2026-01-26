"""BAC0-based BACnet/IP driver for BMS read/write."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Tuple

from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.models.telemetry import Telemetry
from thermal_commons_mvp.utils.logging_utils import get_logger

logger = get_logger(__name__)

try:
    import BAC0
    BAC0_AVAILABLE = True
except ImportError:
    BAC0 = None  # type: ignore[misc, assignment]
    BAC0_AVAILABLE = False


class BACnetDriver(ABC):
    """Abstract interface for BMS connectivity (BACnet or simulation)."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the BMS network."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection."""
        ...

    @abstractmethod
    def read_telemetry(self, building_id: str) -> Telemetry:
        """Read current temp, humidity, power_load for a building."""
        ...

    def write_setpoint(self, building_id: str, value: float) -> bool:
        """Optional: write cooling setpoint. Default no-op returns False."""
        return False


class BAC0Driver(BACnetDriver):
    """
    BAC0 (Python) implementation of BACnet/IP communication.

    Reads analogue values for temp, humidity, power from configured device/objects.
    """

    def __init__(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        local_obj_name: str = "COOL_Client",
    ) -> None:
        s = get_settings()
        self._ip = ip or s.bacnet_ip or "192.168.1.1"
        self._port = port or s.bacnet_port
        self._name = local_obj_name
        self._bacnet: Optional[object] = None

    def connect(self) -> None:
        if not BAC0_AVAILABLE:
            logger.warning("BAC0 not installed; driver is no-op.")
            return
        try:
            # BAC0 2025+ uses ip="x.x.x.x/mask" and has no objectName. Prefer /24 if only IP given.
            ip_spec = f"{self._ip}/24" if "/" not in str(self._ip) else str(self._ip)
            self._bacnet = BAC0.lite(ip=ip_spec, port=self._port)
            logger.info("BACnet driver connected to %s:%s", self._ip, self._port)
        except Exception as e:
            logger.error("BACnet connect failed: %s", e)
            self._bacnet = None

    def disconnect(self) -> None:
        if self._bacnet is not None and BAC0_AVAILABLE and hasattr(self._bacnet, "disconnect"):
            try:
                self._bacnet.disconnect()
            except Exception as e:
                logger.warning("BACnet disconnect error: %s", e)
        self._bacnet = None

    def read_telemetry(self, building_id: str) -> Telemetry:
        """Read from BACnet points. Override point addresses for your BMS."""
        if not BAC0_AVAILABLE or self._bacnet is None:
            return _mock_telemetry(building_id)
        temp, humidity, power = self._read_points(building_id)
        return Telemetry(
            building_id=building_id,
            temp_c=temp,
            humidity_pct=humidity,
            power_load_kw=power,
        )

    def _read_points(self, building_id: str) -> Tuple[float, float, float]:
        """Read temp, humidity, power from BACnet. Replace with real object lists."""
        # Placeholder: actual implementation would use self._bacnet.read("device,object")
        logger.debug("Reading points for %s (stub)", building_id)
        return (24.0, 60.0, 50.0)


def _mock_telemetry(building_id: str) -> Telemetry:
    """Return mock telemetry when BAC0 is unavailable or disconnected."""
    return Telemetry(
        building_id=building_id,
        temp_c=24.0,
        humidity_pct=60.0,
        power_load_kw=50.0,
        timestamp=datetime.now(timezone.utc),
    )
