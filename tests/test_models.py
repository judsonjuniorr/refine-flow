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
