"""Tests for core domain models."""

import pytest

from refineflow.core.models import Activity, ActivityStatus, Entry, EntryType
from refineflow.utils.time import get_timestamp


def test_entry_type_enum() -> None:
    """Test EntryType enumeration."""
    assert EntryType.NOTE.value == "note"
    assert EntryType.QUESTION.value == "question"
    assert EntryType.DECISION.value == "decision"


def test_activity_status_enum() -> None:
    """Test ActivityStatus enumeration."""
    assert ActivityStatus.IN_PROGRESS.value == "in_progress"
    assert ActivityStatus.FINALIZED.value == "finalized"


def test_entry_creation() -> None:
    """Test Entry model creation."""
    timestamp = get_timestamp()
    entry = Entry(
        entry_type=EntryType.NOTE,
        content="Test note content",
        timestamp=timestamp,
    )
    assert entry.entry_type == EntryType.NOTE
    assert entry.content == "Test note content"
    assert entry.timestamp == timestamp
    assert entry.metadata == {}


def test_entry_with_metadata() -> None:
    """Test Entry model with metadata."""
    entry = Entry(
        entry_type=EntryType.TRANSCRIPT,
        content="Meeting notes",
        timestamp=get_timestamp(),
        metadata={"meeting": "Sprint Planning", "duration": "30min"},
    )
    assert entry.metadata["meeting"] == "Sprint Planning"
    assert entry.metadata["duration"] == "30min"


def test_entry_validation_requires_fields() -> None:
    """Test that Entry requires mandatory fields."""
    with pytest.raises(ValueError):
        Entry()  # type: ignore


def test_activity_creation() -> None:
    """Test Activity model creation."""
    timestamp = get_timestamp()
    activity = Activity(
        slug="test-activity",
        title="Test Activity",
        description="Test description",
        created_at=timestamp,
        updated_at=timestamp,
    )
    assert activity.slug == "test-activity"
    assert activity.title == "Test Activity"
    assert activity.status == ActivityStatus.IN_PROGRESS
    assert activity.created_at == timestamp


def test_activity_with_initialization_data() -> None:
    """Test Activity with initialization data."""
    timestamp = get_timestamp()
    activity = Activity(
        slug="epic-123",
        title="User Authentication",
        description="Implement OAuth2",
        created_at=timestamp,
        updated_at=timestamp,
        problem="Users need secure authentication",
        stakeholders=["Product", "Security", "Engineering"],
        constraints="Must complete in 2 sprints",
        affected_system="API Gateway",
    )
    assert activity.problem == "Users need secure authentication"
    assert len(activity.stakeholders) == 3
    assert "Security" in activity.stakeholders
    assert activity.constraints == "Must complete in 2 sprints"


def test_activity_finalized_status() -> None:
    """Test Activity with finalized status."""
    timestamp = get_timestamp()
    activity = Activity(
        slug="done-task",
        title="Completed Task",
        description="Already done",
        status=ActivityStatus.FINALIZED,
        created_at=timestamp,
        updated_at=timestamp,
    )
    assert activity.status == ActivityStatus.FINALIZED


def test_activity_to_dict() -> None:
    """Test Activity serialization to dict."""
    timestamp = get_timestamp()
    activity = Activity(
        slug="test",
        title="Test",
        description="Test",
        created_at=timestamp,
        updated_at=timestamp,
    )
    data = activity.model_dump()
    assert data["slug"] == "test"
    assert data["status"] == "in_progress"
    assert isinstance(data, dict)


# Phase 1: Categorized Questions Tests (TDD - written FIRST)


def test_categorized_questions_model() -> None:
    """Test ActivityState with new categorized questions dict structure."""
    from refineflow.core.state import ActivityState

    timestamp = get_timestamp()
    state = ActivityState(
        summary="Test activity",
        open_questions={
            "Frontend": ["Como implementar o componente X?", "Qual biblioteca UI usar?"],
            "Backend": ["Como estruturar a API?"],
            "Arquitetura": ["Qual padrão usar?"],
            "Produto": [],
            "UX/UI": ["Qual o fluxo do usuário?"],
            "Geral": ["Quando começa o projeto?"],
        },
        last_updated=timestamp,
    )

    assert isinstance(state.open_questions, dict)
    assert len(state.open_questions["Frontend"]) == 2
    assert len(state.open_questions["Backend"]) == 1
    assert len(state.open_questions["Produto"]) == 0
    assert "Como implementar o componente X?" in state.open_questions["Frontend"]
    assert "Como estruturar a API?" in state.open_questions["Backend"]


def test_backward_compatibility_flat_list() -> None:
    """Test auto-migration from old flat list format to new dict format."""
    from refineflow.core.state import ActivityState

    # Simulate loading old state.json with flat list
    old_data = {
        "summary": "Old activity",
        "open_questions": ["Pergunta 1", "Pergunta 2", "Pergunta 3"],
        "action_items": [],
        "decisions": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "identified_risks": [],
        "dependencies": [],
        "metrics": [],
        "costs": [],
        "information_gaps": [],
        "canvas": {},
        "last_updated": get_timestamp(),
    }

    # Should auto-migrate to dict with "Geral" category
    state = ActivityState(**old_data)

    assert isinstance(state.open_questions, dict)
    assert "Geral" in state.open_questions
    assert len(state.open_questions["Geral"]) == 3
    assert "Pergunta 1" in state.open_questions["Geral"]
    assert "Pergunta 2" in state.open_questions["Geral"]
    assert "Pergunta 3" in state.open_questions["Geral"]


def test_multi_category_questions() -> None:
    """Test that same question can exist in multiple categories."""
    from refineflow.core.state import ActivityState

    timestamp = get_timestamp()
    same_question = "Qual a estimativa de prazo?"

    state = ActivityState(
        summary="Multi-category test",
        open_questions={
            "Frontend": [same_question, "Outra pergunta frontend"],
            "Backend": [same_question, "Outra pergunta backend"],
            "Produto": [same_question],
            "Geral": [],
        },
        last_updated=timestamp,
    )

    # Verify same question appears in multiple categories
    assert same_question in state.open_questions["Frontend"]
    assert same_question in state.open_questions["Backend"]
    assert same_question in state.open_questions["Produto"]

    # Count total occurrences
    total_occurrences = sum(
        1 for category_questions in state.open_questions.values()
        if same_question in category_questions
    )
    assert total_occurrences == 3


def test_empty_categories_allowed() -> None:
    """Test that categories can have empty lists."""
    from refineflow.core.state import ActivityState

    timestamp = get_timestamp()
    state = ActivityState(
        summary="Empty categories test",
        open_questions={
            "Frontend": [],
            "Backend": ["Uma pergunta"],
            "Arquitetura": [],
            "Produto": [],
            "UX/UI": [],
            "Geral": [],
        },
        last_updated=timestamp,
    )

    assert len(state.open_questions["Frontend"]) == 0
    assert len(state.open_questions["Backend"]) == 1
    assert len(state.open_questions["Arquitetura"]) == 0
    assert all(isinstance(questions, list) for questions in state.open_questions.values())
