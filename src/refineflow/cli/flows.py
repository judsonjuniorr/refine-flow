"""Activity management flows for RefineFlow CLI."""

import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from refineflow.cli.inputs import get_multiline_input
from refineflow.core.exporters import CanvasExporter, JiraExporter
from refineflow.core.models import Activity, ActivityStatus, Entry, EntryType
from refineflow.llm.processor_langchain import LLMProcessor
from refineflow.storage.filesystem import ActivityStorage, slugify
from refineflow.utils.editor import open_editor
from refineflow.utils.logger import get_logger
from refineflow.utils.time import format_timestamp, get_timestamp

console = Console()
logger = get_logger(__name__)


def create_activity_flow() -> None:
    """Flow for creating a new activity."""
    console.print("\n[bold cyan]Criar Nova Atividade[/bold cyan]\n")

    # Collect activity information
    title = questionary.text("Título da Atividade:").ask()
    if not title:
        return

    description = questionary.text("Breve Descrição:").ask() or ""
    problem = questionary.text("Declaração do Problema:").ask() or ""

    # Stakeholders
    stakeholders_input = questionary.text("Stakeholders (separados por vírgula):").ask() or ""
    stakeholders = [s.strip() for s in stakeholders_input.split(",") if s.strip()]

    constraints = questionary.text("Restrições/Cronograma:").ask() or ""
    affected_system = questionary.text("Sistema/Produto Afetado:").ask() or ""

    # Create activity
    timestamp = get_timestamp()
    slug = slugify(title)

    activity = Activity(
        slug=slug,
        title=title,
        description=description,
        created_at=timestamp,
        updated_at=timestamp,
        problem=problem,
        stakeholders=stakeholders,
        constraints=constraints,
        affected_system=affected_system,
    )

    storage = ActivityStorage()
    storage.create_activity(activity)

    console.print(f"\n[green]✅ Atividade '{title}' criada com sucesso![/green]")
    console.print(f"[dim]Slug: {slug}[/dim]\n")


def select_activity_flow() -> None:
    """Flow for selecting and working with an activity."""
    storage = ActivityStorage()
    activities = storage.list_activities(status=ActivityStatus.IN_PROGRESS)

    if not activities:
        console.print("[yellow]Nenhuma atividade em andamento.[/yellow]")
        return

    # Create choices
    choices = [f"{a.title} ({a.slug})" for a in activities]
    choices.append("← Voltar")

    selected = questionary.select(
        "Selecione uma atividade:",
        choices=choices,
    ).ask()

    if not selected or selected == "← Voltar":
        return

    # Extract slug
    slug = selected.split("(")[1].rstrip(")")
    activity_menu(slug)


def activity_menu(slug: str) -> None:
    """Menu for working with a specific activity."""
    storage = ActivityStorage()
    activity = storage.load_activity(slug)

    if not activity:
        console.print(f"[red]Atividade não encontrada: {slug}[/red]")
        return

    while True:
        # Show status panel
        show_activity_status(slug)

        choice = questionary.select(
            f"Trabalhando em: {activity.title}",
            choices=[
                "➕ Adicionar Informação",
                "💬 Conversar com Contexto",
                "❓ Ver Questões Abertas",
                "📊 Gerar Business Case Canvas",
                "📤 Exportar para Jira",
                "✅ Finalizar Atividade",
                "← Voltar ao Menu Principal",
            ],
        ).ask()

        if not choice or choice == "← Voltar ao Menu Principal":
            break

        elif choice == "➕ Adicionar Informação":
            add_entry_flow(slug)

        elif choice == "💬 Conversar com Contexto":
            chat_flow(slug)

        elif choice == "❓ Ver Questões Abertas":
            view_questions_flow(slug)

        elif choice == "📊 Gerar Business Case Canvas":
            generate_canvas_flow(slug)

        elif choice == "📤 Exportar para Jira":
            export_jira_flow(slug)

        elif choice == "✅ Finalizar Atividade":
            if finalize_activity_flow(slug):
                break


def show_activity_status(slug: str) -> None:
    """Display activity status panel."""
    storage = ActivityStorage()
    activity = storage.load_activity(slug)
    state = storage.load_state(slug)

    if not activity or not state:
        return

    # Create status table
    table = Table(title=f"Atividade: {activity.title}", show_header=False)
    table.add_column("Campo", style="cyan")
    table.add_column("Valor")

    table.add_row("Status", activity.status.upper())
    table.add_row("Última Atualização", format_timestamp(activity.updated_at))
    summary_display = state.summary[:100] + "..." if len(state.summary) > 100 else state.summary
    table.add_row("Resumo", summary_display)
    table.add_row("Itens de Ação", str(len(state.action_items)))
    # Calculate total questions across all categories
    total_questions = sum(len(questions) for questions in state.open_questions.values())
    table.add_row("Questões Abertas", str(total_questions))

    console.print(table)
    console.print()


def add_entry_flow(slug: str) -> None:
    """Flow for adding an entry to an activity."""
    storage = ActivityStorage()

    if storage.is_finalized(slug):
        console.print("[red]Não é possível adicionar entradas a atividade finalizada.[/red]")
        return

    # PHASE 4: Get content FIRST, then auto-classify
    # Get content
    input_method = questionary.select(
        "Método de entrada:",
        choices=["Múltiplas linhas (terminal)", "Editor do Sistema", "Cancelar"],
    ).ask()

    if input_method == "Cancelar":
        return

    content = ""
    if input_method == "Múltiplas linhas (terminal)":
        content = get_multiline_input()
    elif input_method == "Editor do Sistema":
        content = open_editor() or ""

    if not content:
        console.print("[yellow]Nenhum conteúdo inserido.[/yellow]")
        return

    # Map EntryType to Portuguese labels
    entry_type_labels = {
        EntryType.NOTE: "Nota",
        EntryType.ANSWER: "Resposta",
        EntryType.TRANSCRIPT: "Transcrição",
        EntryType.JIRA_DESCRIPTION: "Descrição Jira",
        EntryType.DECISION: "Decisão",
        EntryType.REQUIREMENT: "Requisito",
        EntryType.RISK: "Risco",
        EntryType.METRIC: "Métrica",
        EntryType.COST: "Custo",
        EntryType.DEPENDENCY: "Dependência",
    }

    # Try to auto-classify with LLM
    processor = LLMProcessor()
    entry_type = None

    try:
        detected_type = processor.classify_entry_type(content)
        detected_label = entry_type_labels.get(detected_type, "Nota")

        # Ask user to confirm
        console.print(f"\n[cyan]Tipo detectado: {detected_label}[/cyan]")
        confirmation = questionary.confirm("Está correto?", default=True).ask()

        if confirmation:
            entry_type = detected_type
            console.print(f"[green]✓ Usando tipo detectado: {detected_label}[/green]\n")
        else:
            # User rejected, show manual selection
            console.print("[yellow]Por favor, selecione o tipo manualmente:[/yellow]")
            entry_type = None  # Will trigger manual selection below

    except (ValueError, Exception) as e:
        # LLM not available or classification failed
        logger.debug(f"Auto-classification failed: {e}")
        console.print("[yellow]Classificação automática não disponível.[/yellow]")
        entry_type = None

    # Manual selection fallback (if auto-classification failed or user rejected)
    if entry_type is None:
        # Note: "Pergunta" is not included - questions are extracted automatically by LLM
        entry_type_choice = questionary.select(
            "Tipo de Entrada:",
            choices=[
                "Nota",
                "Resposta",
                "Transcrição",
                "Descrição Jira",
                "Decisão",
                "Requisito",
                "Risco",
                "Métrica",
                "Custo",
                "Dependência",
            ],
        ).ask()

        if not entry_type_choice:
            return

        # Map Portuguese choices to EntryType enum
        # Note: QUESTION is not in the map - questions are extracted automatically by LLM
        entry_type_map = {
            "Nota": EntryType.NOTE,
            "Resposta": EntryType.ANSWER,
            "Transcrição": EntryType.TRANSCRIPT,
            "Descrição Jira": EntryType.JIRA_DESCRIPTION,
            "Decisão": EntryType.DECISION,
            "Requisito": EntryType.REQUIREMENT,
            "Risco": EntryType.RISK,
            "Métrica": EntryType.METRIC,
            "Custo": EntryType.COST,
            "Dependência": EntryType.DEPENDENCY,
        }
        entry_type = entry_type_map[entry_type_choice]

    # Create entry
    entry = Entry(
        entry_type=entry_type,
        content=content,
        timestamp=get_timestamp(),
    )

    storage.append_to_log(slug, entry)

    # Process with LLM if available
    activity = storage.load_activity(slug)
    state = storage.load_state(slug)

    if activity and state:
        updated_state = processor.process_entry(activity, entry, state)

        if updated_state:
            storage.save_state(slug, updated_state)
            console.print("[green]✅ Entrada adicionada e estado atualizado![/green]")
        else:
            console.print("[green]✅ Entrada adicionada (atualização de estado ignorada).[/green]")
    else:
        console.print("[green]✅ Entrada adicionada![/green]")


def chat_flow(slug: str) -> None:
    """Flow for chatting with activity context."""
    storage = ActivityStorage()
    activity = storage.load_activity(slug)
    state = storage.load_state(slug)
    log_content = storage.read_log(slug)

    if not activity or not state:
        console.print("[red]Falha ao carregar dados da atividade.[/red]")
        return

    console.print("\n[bold cyan]Modo Conversação[/bold cyan]")
    console.print("[dim]Digite 'sair' para retornar ao menu[/dim]\n")

    processor = LLMProcessor()

    while True:
        question = questionary.text("Você:").ask()

        if not question or question.lower() in ["sair", "exit", "quit", "voltar"]:
            break

        answer = processor.answer_question(activity, state, log_content, question)

        console.print(f"\n[bold green]Assistente:[/bold green]\n{answer}\n")


def generate_canvas_flow(slug: str) -> None:
    """Flow for generating Business Case Canvas."""
    storage = ActivityStorage()
    activity = storage.load_activity(slug)
    state = storage.load_state(slug)

    if not activity or not state:
        console.print("[red]Falha ao carregar dados da atividade.[/red]")
        return

    console.print("\n[cyan]Gerando Business Case Canvas...[/cyan]")

    exporter = CanvasExporter(storage)
    canvas_md = exporter.generate_canvas(slug)

    storage.write_canvas(slug, canvas_md)

    console.print("[green]✅ Canvas gerado![/green]")

    # Show preview
    if questionary.confirm("Visualizar canvas?").ask():
        console.print(Markdown(canvas_md[:1500] + "\n\n_[truncado]_"))


def export_jira_flow(slug: str) -> None:
    """Flow for exporting to Jira format."""
    storage = ActivityStorage()
    activity = storage.load_activity(slug)
    state = storage.load_state(slug)

    if not activity or not state:
        console.print("[red]Falha ao carregar dados da atividade.[/red]")
        return

    console.print("\n[cyan]Gerando Exportação Jira...[/cyan]")

    exporter = JiraExporter(storage)

    # Select format
    format_choice = questionary.select(
        "Formato de exportação:",
        choices=["Markdown", "JSON", "CSV"],
    ).ask()

    if format_choice == "Markdown":
        content = exporter.export_markdown(slug)
        storage.write_jira_export(slug, content)
        console.print(Markdown(content[:1000] + "\n\n_[truncado]_"))

    elif format_choice == "JSON":
        content = exporter.export_json(slug)
        console.print(content)

    elif format_choice == "CSV":
        content = exporter.export_csv(slug)
        console.print(content)

    console.print("\n[green]✅ Exportação Jira salva![/green]")


def finalize_activity_flow(slug: str) -> bool:
    """Flow for finalizing an activity."""
    storage = ActivityStorage()

    confirm = questionary.confirm(
        "Tem certeza que deseja finalizar esta atividade? Ela não poderá ser modificada após isto."
    ).ask()

    if confirm:
        storage.finalize_activity(slug)
        console.print("[green]✅ Atividade finalizada![/green]")
        return True

    return False


def view_finalized_activities() -> None:
    """View finalized activities."""
    storage = ActivityStorage()
    activities = storage.list_activities(status=ActivityStatus.FINALIZED)

    if not activities:
        console.print("[yellow]Nenhuma atividade finalizada.[/yellow]")
        return

    table = Table(title="Atividades Finalizadas")
    table.add_column("Título", style="cyan")
    table.add_column("Slug", style="dim")
    table.add_column("Finalizada em", style="green")

    for activity in activities:
        table.add_row(
            activity.title,
            activity.slug,
            format_timestamp(activity.updated_at),
        )

    console.print(table)


def view_questions_flow(slug: str) -> None:
    """Flow for viewing categorized open questions."""
    storage = ActivityStorage()
    state = storage.load_state(slug)

    if not state:
        console.print("[red]Falha ao carregar dados da atividade.[/red]")
        return

    # Category icons mapping
    category_icons = {
        "Frontend": "🎨",
        "Backend": "⚙️",
        "Arquitetura": "📐",
        "Produto": "📦",
        "UX/UI": "🎭",
        "Geral": "💡",
    }

    # Filter out empty categories and count total questions
    questions_by_category = {
        category: questions
        for category, questions in state.open_questions.items()
        if questions
    }

    total_questions = sum(len(questions) for questions in questions_by_category.values())

    # Handle no questions case
    if total_questions == 0:
        console.print("\n[yellow]Nenhuma questão em aberto no momento.[/yellow]\n")
        return

    # Build the display content
    content_parts = []

    for category, questions in questions_by_category.items():
        icon = category_icons.get(category, "❓")
        category_header = f"{icon} {category} ({len(questions)})"
        content_parts.append(f"[bold cyan]{category_header}[/bold cyan]")

        for question in questions:
            content_parts.append(f"  • {question}")

        content_parts.append("")  # Empty line between categories

    # Remove trailing empty line
    if content_parts and content_parts[-1] == "":
        content_parts.pop()

    content = "\n".join(content_parts)

    # Display in a panel
    panel = Panel(
        content,
        title=f"[bold]📋 Questões Abertas ({total_questions} questões)[/bold]",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print("\n")
    console.print(panel)
    console.print("\n")
