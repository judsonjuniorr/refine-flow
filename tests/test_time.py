"""Tests for time utilities."""

from datetime import datetime

from refineflow.utils.time import format_timestamp, get_timestamp


def test_get_timestamp_returns_iso_format() -> None:
    """Test that get_timestamp returns ISO formatted string."""
    timestamp = get_timestamp()
    # Should be parseable as ISO format
    dt = datetime.fromisoformat(timestamp)
    assert isinstance(dt, datetime)


def test_get_timestamp_is_utc() -> None:
    """Test that timestamp is in UTC."""
    timestamp = get_timestamp()
    dt = datetime.fromisoformat(timestamp)
    # Check it has timezone info
    assert dt.tzinfo is not None


def test_format_timestamp() -> None:
    """Test timestamp formatting."""
    timestamp = "2026-01-23T10:30:00+00:00"
    formatted = format_timestamp(timestamp)
    assert "2026-01-23" in formatted
    assert "10:30:00" in formatted


def test_format_timestamp_custom_format() -> None:
    """Test timestamp formatting with custom format."""
    timestamp = "2026-01-23T10:30:00+00:00"
    formatted = format_timestamp(timestamp, "%Y-%m-%d")
    assert formatted == "2026-01-23"


def test_format_timestamp_invalid_input() -> None:
    """Test that invalid timestamp returns original string."""
    invalid = "not-a-timestamp"
    formatted = format_timestamp(invalid)
    assert formatted == invalid
