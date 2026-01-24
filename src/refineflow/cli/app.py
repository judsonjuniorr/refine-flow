"""CLI application setup."""

import typer
from rich.console import Console

app = typer.Typer(help="RefineFlow - AI-powered activity refinement agent")
console = Console()


@app.command()
def run() -> None:
    """Start the interactive RefineFlow application."""
    from refineflow.cli.menu import main_menu

    main_menu()


if __name__ == "__main__":
    app()
