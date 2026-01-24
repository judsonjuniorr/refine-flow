"""Logging configuration for RefineFlow."""

import logging
import sys


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with structured formatting.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger


_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name
        level: Optional log level override

    Returns:
        Logger instance
    """
    if name not in _loggers:
        from .config import get_config

        cfg = get_config()
        log_level = level or cfg.log_level
        _loggers[name] = setup_logger(name, log_level)
    return _loggers[name]
