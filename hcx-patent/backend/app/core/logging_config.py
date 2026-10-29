"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """Configure structured logging for the application.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
    """
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove existing handlers to avoid duplicate output
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # Suppress noisy libraries
    for noisy in ("urllib3", "matplotlib", "PIL", "asyncio", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
