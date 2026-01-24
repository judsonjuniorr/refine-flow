"""Main CLI entry point for RefineFlow."""

import sys

from refineflow.cli.app import app
from refineflow.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Run the RefineFlow CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
