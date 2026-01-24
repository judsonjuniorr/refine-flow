"""Tests for logger utilities."""

import logging

from refineflow.utils.logger import get_logger, setup_logger


def test_setup_logger_creates_logger() -> None:
    """Test that setup_logger creates a logger."""
    logger = setup_logger("test_logger", "DEBUG")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG


def test_setup_logger_default_level() -> None:
    """Test that setup_logger uses INFO as default level."""
    logger = setup_logger("test_logger_default")
    assert logger.level == logging.INFO


def test_get_logger_returns_logger() -> None:
    """Test that get_logger returns a logger instance."""
    logger = get_logger("test_get_logger")
    assert isinstance(logger, logging.Logger)


def test_get_logger_singleton() -> None:
    """Test that get_logger returns same instance for same name."""
    logger1 = get_logger("singleton_test")
    logger2 = get_logger("singleton_test")
    assert logger1 is logger2
