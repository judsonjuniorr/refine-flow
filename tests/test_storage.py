"""Tests for storage layer."""

from pathlib import Path

import pytest

from refineflow.core.models import Activity, ActivityStatus, Entry, EntryType
from refineflow.core.state import ActivityState
from refineflow.storage.filesystem import ActivityStorage, slugify
from refineflow.utils.config import reset_config
from refineflow.utils.time import get_timestamp


def test_slugify() -> None:
    """Test slug generation."""
    assert slugify("Test Activity") == "test-activity"
    assert slugify("User Authentication & Authorization") == "user-authentication-authorization"
    assert slugify("  Multiple   Spaces  ") == "multiple-spaces"


def test_create_activity_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that create_activity creates proper folder structure."""
    # Use tmp_path as data_dir
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="test-activity",
        title="Test Activity",
        description="Test description",
        created_at=timestamp,
        updated_at=timestamp,
    )

    activity_dir = storage.create_activity(activity)

    assert activity_dir.exists()
    assert (activity_dir / "activity.md").exists()
    assert (activity_dir / "log.md").exists()
    assert (activity_dir / "canvas.md").exists()
    assert (activity_dir / "jira_export.md").exists()
    assert (activity_dir / "state.json").exists()
    assert (activity_dir / "chat.md").exists()
    assert (activity_dir / "activity.json").exists()


def test_save_and_load_activity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving and loading activity."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="save-load-test",
        title="Save Load Test",
        description="Testing save and load",
        created_at=timestamp,
        updated_at=timestamp,
        stakeholders=["Alice", "Bob"],
    )

    storage.create_activity(activity)

    loaded = storage.load_activity("save-load-test")
    assert loaded is not None
    assert loaded.title == "Save Load Test"
    assert loaded.slug == "save-load-test"
    assert len(loaded.stakeholders) == 2


def test_append_to_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test appending entries to log."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="log-test",
        title="Log Test",
        description="Testing log",
        created_at=timestamp,
        updated_at=timestamp,
    )

    storage.create_activity(activity)

    entry = Entry(
        entry_type=EntryType.NOTE,
        content="Test note content",
        timestamp=timestamp,
    )

    storage.append_to_log("log-test", entry)

    log_content = storage.read_log("log-test")
    assert "Test note content" in log_content
    assert "Note" in log_content


def test_state_save_and_load(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving and loading activity state."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="state-test",
        title="State Test",
        description="Testing state",
        created_at=timestamp,
        updated_at=timestamp,
    )

    storage.create_activity(activity)

    state = ActivityState(
        summary="Updated summary",
        action_items=[{"action": "Test action", "owner": "Alice", "status": "open"}],
        last_updated=timestamp,
    )

    storage.save_state("state-test", state)

    loaded_state = storage.load_state("state-test")
    assert loaded_state is not None
    assert loaded_state.summary == "Updated summary"
    assert len(loaded_state.action_items) == 1


def test_list_activities(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test listing activities."""
    # Use unique temp dir for each test
    reset_config()  # Reset singleton before changing env
    test_data = tmp_path / "list_test"
    monkeypatch.setenv("DATA_DIR", str(test_data))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    # Create multiple activities
    for i in range(3):
        activity = Activity(
            slug=f"activity-{i}",
            title=f"Activity {i}",
            description=f"Description {i}",
            created_at=timestamp,
            updated_at=timestamp,
        )
        storage.create_activity(activity)

    activities = storage.list_activities()
    assert len(activities) == 3


def test_list_activities_by_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test listing activities filtered by status."""
    # Use unique temp dir
    reset_config()  # Reset singleton before changing env
    test_data = tmp_path / "status_test"
    monkeypatch.setenv("DATA_DIR", str(test_data))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    # Create in-progress activity
    activity1 = Activity(
        slug="in-progress",
        title="In Progress",
        description="Active",
        created_at=timestamp,
        updated_at=timestamp,
    )
    storage.create_activity(activity1)

    # Create finalized activity
    activity2 = Activity(
        slug="finalized",
        title="Finalized",
        description="Done",
        status=ActivityStatus.FINALIZED,
        created_at=timestamp,
        updated_at=timestamp,
    )
    storage.create_activity(activity2)

    in_progress = storage.list_activities(status=ActivityStatus.IN_PROGRESS)
    finalized = storage.list_activities(status=ActivityStatus.FINALIZED)

    assert len(in_progress) == 1
    assert len(finalized) == 1
    assert in_progress[0].slug == "in-progress"
    assert finalized[0].slug == "finalized"


def test_finalize_activity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test finalizing an activity."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="to-finalize",
        title="To Finalize",
        description="Will be finalized",
        created_at=timestamp,
        updated_at=timestamp,
    )

    storage.create_activity(activity)

    assert not storage.is_finalized("to-finalize")

    storage.finalize_activity("to-finalize")

    assert storage.is_finalized("to-finalize")

    loaded = storage.load_activity("to-finalize")
    assert loaded is not None
    assert loaded.status == ActivityStatus.FINALIZED


def test_write_and_read_canvas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing and reading canvas."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="canvas-test",
        title="Canvas Test",
        description="Testing canvas",
        created_at=timestamp,
        updated_at=timestamp,
    )

    storage.create_activity(activity)

    canvas_content = "# Business Case Canvas\n\nTest content"
    storage.write_canvas("canvas-test", canvas_content)

    loaded_canvas = storage.read_canvas("canvas-test")
    assert "Test content" in loaded_canvas


def test_write_jira_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing Jira export."""
    reset_config()  # Reset singleton before changing env
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    storage = ActivityStorage()
    timestamp = get_timestamp()

    activity = Activity(
        slug="jira-test",
        title="Jira Test",
        description="Testing Jira export",
        created_at=timestamp,
        updated_at=timestamp,
    )

    storage.create_activity(activity)

    jira_content = "# Jira Export\n\nTest Jira content"
    storage.write_jira_export("jira-test", jira_content)

    jira_path = storage.get_activity_dir("jira-test") / "jira_export.md"
    assert "Test Jira content" in jira_path.read_text()
