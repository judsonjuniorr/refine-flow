# RefineFlow Project Structure

## Overview

Complete Python application for AI-powered technical activity refinement with interactive CLI.

## Directory Structure

```
refinement-agent/
├── README.md                      # Installation and usage guide
├── pyproject.toml                 # Project metadata and dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
│
├── src/refineflow/                # Main application package
│   ├── __init__.py               # Package initialization
│   ├── __main__.py               # CLI entry point
│   │
│   ├── cli/                       # Command-line interface
│   │   ├── __init__.py
│   │   ├── app.py                # Typer app setup
│   │   ├── menu.py               # Main menu and navigation
│   │   ├── flows.py              # Activity management flows
│   │   └── inputs.py             # Multi-line input helpers
│   │
│   ├── core/                      # Core domain models
│   │   ├── __init__.py
│   │   ├── models.py             # Activity, Entry, Status, EntryType
│   │   ├── canvas.py             # BusinessCaseCanvas model
│   │   ├── state.py              # ActivityState model
│   │   └── exporters.py          # Canvas and Jira exporters
│   │
│   ├── storage/                   # Data persistence layer
│   │   ├── __init__.py
│   │   ├── filesystem.py         # ActivityStorage (Markdown files)
│   │   ├── index.py              # SQLite metadata index
│   │   └── templates.py          # Markdown templates
│   │
│   ├── llm/                       # AI integration
│   │   ├── __init__.py
│   │   ├── client.py             # OpenAI client wrapper
│   │   ├── prompts.py            # Prompt builders
│   │   └── processor.py          # LLM processing logic
│   │
│   ├── rag/                       # RAG (embeddings) - placeholder
│   │   └── __init__.py           # Future Ollama integration
│   │
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       ├── config.py             # Configuration management
│       ├── logger.py             # Structured logging
│       ├── time.py               # Timestamp utilities
│       └── editor.py             # System editor integration
│
├── tests/                         # Test suite
│   ├── test_config.py            # Config tests
│   ├── test_models.py            # Domain model tests
│   ├── test_canvas.py            # Canvas model tests
│   ├── test_state.py             # State model tests
│   ├── test_storage.py           # Storage layer tests
│   ├── test_time.py              # Time utility tests
│   ├── test_editor.py            # Editor utility tests
│   └── test_logger.py            # Logger utility tests
│
└── data/                          # Application data (git ignored)
    ├── refineflow.db             # SQLite activity index
    └── activities/                # Activity folders
        └── <activity-slug>/       # Per-activity directory
            ├── activity.md        # Activity overview
            ├── activity.json      # Activity metadata
            ├── log.md             # Chronological entries
            ├── state.json         # Structured state (AI-maintained)
            ├── canvas.md          # Business Case Canvas
            ├── jira_export.md     # Jira export
            └── chat.md            # Chat history
```

## Key Components

### Core Models (src/refineflow/core/)

- **Activity**: Main activity entity with status, metadata, stakeholders
- **Entry**: Log entries (notes, questions, decisions, risks, etc.)
- **ActivityState**: AI-maintained structured state
  - Summary
  - Action items
  - Open questions
  - Decisions
  - Requirements (functional/non-functional)
  - Risks and mitigations
  - Dependencies
  - Metrics and costs
  - Information gaps
- **BusinessCaseCanvas**: Comprehensive business case structure
  - Problem/Solution
  - Resources/Dependencies
  - Benefits/ROI
  - Scope/Timeline
  - Risks/Mitigations
  - Stakeholders
  - Complexity analysis
  - Communication plan
  - Costs and metrics

### Storage (src/refineflow/storage/)

- **ActivityStorage**: Filesystem-based storage
  - Creates Markdown-based activity folders
  - Manages activity lifecycle
  - Handles log appending
  - State persistence
- **ActivityIndex**: SQLite index for fast search
  - Metadata caching
  - Status filtering
  - Full-text search ready

### LLM Integration (src/refineflow/llm/)

- **OpenAIClient**: API wrapper with error handling
- **Prompts**: Structured prompt builders for:
  - Information extraction from entries
  - Context-aware chat responses
  - Jira task generation
- **LLMProcessor**: Orchestrates AI operations
  - Processes entries to update state
  - Answers questions with context citations
  - Generates exports

### CLI Interface (src/refineflow/cli/)

- **Interactive menus** using Questionary
- **Rich UI** with tables, panels, markdown rendering
- **Multi-line input** with prompt_toolkit
- **System editor integration** ($EDITOR support)
- **Flows**: create, select, add entries, chat, export, finalize

### Utilities (src/refineflow/utils/)

- **Config**: Pydantic settings with env vars
- **Logger**: Structured logging
- **Time**: ISO timestamp handling
- **Editor**: System $EDITOR integration

## Data Flow

1. **User creates activity** → Creates folder with templates
2. **User adds entries** → Appends to log.md
3. **LLM processes entry** → Updates state.json
4. **User generates canvas** → Creates canvas.md from state
5. **User exports to Jira** → Generates jira_export.md (Markdown/JSON/CSV)
6. **User finalizes** → Marks activity read-only

## Testing

- **56 tests** covering:
  - Configuration loading
  - Model validation and serialization
  - Storage CRUD operations
  - Time and editor utilities
  - Canvas and state models
- **Coverage**: 89% (54/56 tests passing - 2 isolation issues)

## Configuration

Environment variables (.env):
```
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5-mini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=snowflake-arctic-embed
DATA_DIR=./data
LOG_LEVEL=INFO
```

## Entry Points

- **Command line**: `refineflow` or `python -m refineflow`
- **Programmatic**: `from refineflow.cli import app; app()`

## Extension Points

- **RAG module** (src/refineflow/rag/): Ready for Ollama embeddings integration
- **Custom exporters**: Extend CanvasExporter, JiraExporter classes
- **Additional entry types**: Extend EntryType enum
- **Custom prompts**: Modify prompt builders in llm/prompts.py

## Dependencies

**Core:**
- typer (CLI framework)
- rich (Terminal UI)
- questionary (Interactive prompts)
- pydantic (Data validation)
- openai (LLM integration)
- prompt-toolkit (Multi-line input)

**Dev:**
- pytest (Testing)
- mypy (Type checking)
- ruff (Linting/formatting)
- pytest-cov (Coverage)

## File Formats

- **.md**: Human-readable Markdown for all content
- **.json**: Structured metadata and state
- **.db**: SQLite index for fast queries

All data is local-first and human-readable!
