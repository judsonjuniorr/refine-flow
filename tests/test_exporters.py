"""Tests for exporters module with validation integration."""

from unittest.mock import Mock, patch

import pytest

from refineflow.core.exporters import JiraExporter
from refineflow.core.models import Activity
from refineflow.core.state import ActivityState
from refineflow.storage.filesystem import ActivityStorage


@pytest.fixture
def mock_storage():
    """Create a mock storage."""
    storage = Mock(spec=ActivityStorage)

    # Mock activity
    activity = Activity(
        slug="test-activity",
        title="Test Activity",
        description="Test description",
        problem="Test problem",
        stakeholders=["User1"],
        constraints="None",
        status="in_progress",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )

    # Mock state
    state = ActivityState(
        summary="Test summary",
        functional_requirements=["Req1", "Req2"],
        non_functional_requirements=["NFR1"],
        identified_risks=[],
        dependencies=[],
        costs=[],
        metrics=[],
        information_gaps=[],
    )

    storage.load_activity.return_value = activity
    storage.load_state.return_value = state

    return storage


@pytest.fixture
def valid_jira_content():
    """Valid Jira export content."""
    return """## Parent Task

**Title:** Test Activity

**Description:**
Test description

## Backend Subtask

**Title:** [BE] Test Activity

**Description:**
Backend implementation

## Frontend Subtask

**Title:** [FE] Test Activity

**Description:**
Frontend implementation
"""


@pytest.fixture
def jira_content_with_warnings():
    """Jira content that will trigger warnings."""
    return """## Parent Task

**Title:** Test Activity

**Description:**
Test description

## Backend Subtask

**Title:** [BE] Backend Work

**Description:**
Backend implementation

## Frontend Subtask

**Title:** [FE] Frontend Work

**Description:**
Frontend implementation
"""


def test_export_with_validation_success(mock_storage, valid_jira_content):
    """Verify export succeeds with valid structure."""
    exporter = JiraExporter(mock_storage)

    with patch.object(exporter.processor, "generate_jira_export", return_value=valid_jira_content):
        with patch("refineflow.core.exporters.validate_jira_structure", return_value=(True, [])):
            result = exporter.export_markdown("test-activity")

    assert result is not None
    assert "Test Activity" in result
    assert "**Generated**:" in result
    assert valid_jira_content in result


def test_export_with_validation_warnings(mock_storage, jira_content_with_warnings):
    """Verify warnings logged for minor issues."""
    exporter = JiraExporter(mock_storage)

    warnings = [
        "Backend subtask title doesn't include parent title",
        "Frontend subtask title doesn't include parent title",
    ]

    with patch.object(
        exporter.processor, "generate_jira_export", return_value=jira_content_with_warnings
    ):
        with patch(
            "refineflow.core.exporters.validate_jira_structure", return_value=(False, warnings)
        ):
            with patch("refineflow.core.exporters.logger") as mock_logger:
                result = exporter.export_markdown("test-activity")

                # Verify warnings were logged
                assert mock_logger.warning.call_count == len(warnings)
                for warning in warnings:
                    mock_logger.warning.assert_any_call(f"Jira validation warning: {warning}")

    # Export should still succeed
    assert result is not None
    assert jira_content_with_warnings in result


def test_export_proceeds_despite_warnings(mock_storage, jira_content_with_warnings):
    """Verify export ALWAYS continues even with warnings."""
    exporter = JiraExporter(mock_storage)

    warnings = [
        "Multiple validation errors",
        "Structure issues detected",
        "Missing required sections",
    ]

    with patch.object(
        exporter.processor, "generate_jira_export", return_value=jira_content_with_warnings
    ):
        with patch(
            "refineflow.core.exporters.validate_jira_structure", return_value=(False, warnings)
        ):
            result = exporter.export_markdown("test-activity")

    # Export must proceed despite warnings
    assert result is not None
    assert "**Generated**:" in result
    assert jira_content_with_warnings in result


def test_export_validation_logged_to_logger(mock_storage, jira_content_with_warnings):
    """Verify validation results use logger.warning()."""
    exporter = JiraExporter(mock_storage)

    warnings = ["Warning 1", "Warning 2", "Warning 3"]

    with patch.object(
        exporter.processor, "generate_jira_export", return_value=jira_content_with_warnings
    ):
        with patch(
            "refineflow.core.exporters.validate_jira_structure", return_value=(False, warnings)
        ):
            with patch("refineflow.core.exporters.logger") as mock_logger:
                exporter.export_markdown("test-activity")

                # Verify logger.warning was called, not logger.error
                assert mock_logger.warning.call_count == len(warnings)
                assert mock_logger.error.call_count == 0

                # Verify each warning was logged with correct format
                for warning in warnings:
                    mock_logger.warning.assert_any_call(f"Jira validation warning: {warning}")


def test_export_no_exception_on_validation_fail(mock_storage, jira_content_with_warnings):
    """Verify export never throws due to validation."""
    exporter = JiraExporter(mock_storage)

    # Simulate validation returning many warnings
    warnings = [f"Warning {i}" for i in range(10)]

    with patch.object(
        exporter.processor, "generate_jira_export", return_value=jira_content_with_warnings
    ):
        with patch(
            "refineflow.core.exporters.validate_jira_structure", return_value=(False, warnings)
        ):
            # This should not raise any exception
            result = exporter.export_markdown("test-activity")

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_export_validation_exception_handled(mock_storage, valid_jira_content):
    """Verify export continues even if validation itself throws an exception."""
    exporter = JiraExporter(mock_storage)

    with patch.object(exporter.processor, "generate_jira_export", return_value=valid_jira_content):
        with patch(
            "refineflow.core.exporters.validate_jira_structure",
            side_effect=Exception("Validation error"),
        ):
            with patch("refineflow.core.exporters.logger") as mock_logger:
                # Export should still succeed
                result = exporter.export_markdown("test-activity")

                # Verify error was logged but export continued
                assert mock_logger.error.call_count == 1
                assert "Validation failed with error" in str(mock_logger.error.call_args)

    assert result is not None
    assert valid_jira_content in result
