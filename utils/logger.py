"""
Central logger configuration helpers.
"""

from __future__ import annotations

import sys
from loguru import Logger, logger as _logger


def configure_logging(verbose: bool) -> None:
    """Configure loguru with file + console handlers."""
    _logger.remove()
    _logger.add(
        "nexus_autodl.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG" if verbose else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    console_format = (
        "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        if verbose
        else "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    _logger.add(
        sys.stderr,
        level="DEBUG" if verbose else "INFO",
        format=console_format,
        colorize=True,
    )


def get_logger(name: str) -> Logger:
    """Return module-scoped logger."""
    return _logger


__all__ = ["configure_logging", "get_logger"]
