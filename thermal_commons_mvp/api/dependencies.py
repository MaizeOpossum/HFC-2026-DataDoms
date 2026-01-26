"""Shared injectables for FastAPI (settings, driver, order book, trade execution)."""

from typing import Optional

from thermal_commons_mvp.config import get_settings
from thermal_commons_mvp.interface.bacnet_driver import BAC0Driver, BACnetDriver
from thermal_commons_mvp.market.order_book import OrderBook
from thermal_commons_mvp.market.trade_execution import TradeExecution

_settings = None
_driver: Optional[BACnetDriver] = None
_order_book: Optional[OrderBook] = None
_trade_execution: Optional[TradeExecution] = None


def get_settings_dep():
    return get_settings()


def get_driver() -> BACnetDriver:
    global _driver
    if _driver is None:
        _driver = BAC0Driver()
        _driver.connect()
    return _driver


def get_order_book() -> OrderBook:
    global _order_book
    if _order_book is None:
        _order_book = OrderBook()
    return _order_book


def get_trade_execution() -> TradeExecution:
    global _trade_execution
    if _trade_execution is None:
        _trade_execution = TradeExecution()
    return _trade_execution
