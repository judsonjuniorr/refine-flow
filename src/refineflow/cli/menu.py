"""Main menu and navigation for RefineFlow CLI."""

import questionary
from rich.console import Console
from rich.panel import Panel

from refineflow.cli.flows import (
    create_activity_flow,
    select_activity_flow,
    view_finalized_activities,
)
from refineflow.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


def main_menu() -> None:
    """Display main menu and handle navigation."""
    console.print(
        Panel.fit(
            "[bold cyan]RefineFlow[/bold cyan]\nAgente de Refinamento de Atividades com IA",
            border_style="cyan",
        )
    )

    while True:
        choice = questionary.select(
            "O que você gostaria de fazer?",
            choices=[
                "📝 Criar Nova Atividade",
                "🔄 Selecionar Atividade em Andamento",
                "✅ Ver Atividades Finalizadas",
                "⚙️  Configurações",
                "❌ Sair",
            ],
        ).ask()

        if not choice or choice == "❌ Sair":
            console.print("\n[cyan]Até logo![/cyan]")
            break

        elif choice == "📝 Criar Nova Atividade":
            create_activity_flow()

        elif choice == "🔄 Selecionar Atividade em Andamento":
            select_activity_flow()

        elif choice == "✅ Ver Atividades Finalizadas":
            view_finalized_activities()

        elif choice == "⚙️  Configurações":
            show_settings()


def show_settings() -> None:
    """Display current settings."""
    from refineflow.utils.config import get_config

    config = get_config()

    console.print(
        Panel(
            f"[bold]Configurações Atuais[/bold]\n\n"
            f"Diretório de Dados: {config.data_dir}\n"
            f"Modelo OpenAI: {config.openai_model}\n"
            f"OpenAI Configurada: {'✅' if config.openai_api_key else '❌'}\n"
            f"Embeddings Habilitados: {'✅' if config.enable_embeddings else '❌'}\n"
            f"URL Ollama: {config.ollama_base_url}",
            title="Configurações",
            border_style="green",
        )
    )
