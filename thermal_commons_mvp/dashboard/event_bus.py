"""In-process event bus for trade_executed and telemetry_updated. Subscribers are sync callbacks."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

EventCallback = Callable[[str, Any], None]

_TRADE_EXECUTED = "trade_executed"
_TELEMETRY_UPDATED = "telemetry_updated"
_GRID_STRESS_CHANGED = "grid_stress_changed"


class EventBus:
    """Sync publish/subscribe. One instance per process."""

    def __init__(self) -> None:
        self._subs: Dict[str, List[EventCallback]] = {
            _TRADE_EXECUTED: [],
            _TELEMETRY_UPDATED: [],
            _GRID_STRESS_CHANGED: [],
        }

    def subscribe(self, topic: str, callback: EventCallback) -> None:
        if topic not in self._subs:
            self._subs[topic] = []
        self._subs[topic].append(callback)

    def unsubscribe(self, topic: str, callback: EventCallback) -> None:
        if topic in self._subs:
            try:
                self._subs[topic].remove(callback)
            except ValueError:
                pass

    def publish(self, topic: str, payload: Any) -> None:
        for cb in self._subs.get(topic, []):
            try:
                cb(topic, payload)
            except Exception as e:
                logger.warning("EventBus subscriber error topic=%s: %s", topic, e)


_inst: EventBus | None = None


def get_event_bus() -> EventBus:
    global _inst
    if _inst is None:
        _inst = EventBus()
    return _inst


# Topic names for consumers
TRADE_EXECUTED = _TRADE_EXECUTED
TELEMETRY_UPDATED = _TELEMETRY_UPDATED
GRID_STRESS_CHANGED = _GRID_STRESS_CHANGED
