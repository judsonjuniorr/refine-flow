"""Time utilities for RefineFlow."""

from datetime import UTC, datetime


def get_timestamp() -> str:
    """
    Get current UTC timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now(UTC).isoformat()


def format_timestamp(timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """
    Format an ISO timestamp string.

    Args:
        timestamp: ISO formatted timestamp
        format_str: Output format string

    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime(format_str)
    except (ValueError, AttributeError):
        return timestamp
