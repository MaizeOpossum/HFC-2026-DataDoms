"""Structured logging helpers."""

import logging
import sys
from typing import Optional

from thermal_commons_mvp.config import get_settings


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return a logger with consistent format and level from config."""
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        log.addHandler(handler)
    log.setLevel((level or get_settings().log_level).upper())
    return log
