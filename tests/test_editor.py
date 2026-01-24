"""Tests for editor utilities."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from refineflow.utils.editor import open_editor


@patch("subprocess.run")
@patch("tempfile.NamedTemporaryFile")
def test_open_editor_returns_edited_content(
    mock_tempfile: MagicMock, mock_run: MagicMock, tmp_path: Path
) -> None:
    """Test that open_editor returns edited content."""
    # Create a temporary file for testing
    temp_file = tmp_path / "test.md"
    temp_file.write_text("edited content")

    # Mock tempfile creation
    mock_file = MagicMock()
    mock_file.__enter__ = MagicMock(return_value=mock_file)
    mock_file.__exit__ = MagicMock(return_value=False)
    mock_file.name = str(temp_file)
    mock_file.write = MagicMock()
    mock_tempfile.return_value = mock_file

    # Mock subprocess
    mock_run.return_value = MagicMock(returncode=0)

    result = open_editor("initial")

    assert result == "edited content"
    mock_run.assert_called_once()


@patch("subprocess.run")
@patch("tempfile.NamedTemporaryFile")
def test_open_editor_returns_none_on_no_change(
    mock_tempfile: MagicMock, mock_run: MagicMock, tmp_path: Path
) -> None:
    """Test that open_editor returns None if content unchanged."""
    initial = "initial content"
    temp_file = tmp_path / "test.md"
    temp_file.write_text(initial)

    mock_file = MagicMock()
    mock_file.__enter__ = MagicMock(return_value=mock_file)
    mock_file.__exit__ = MagicMock(return_value=False)
    mock_file.name = str(temp_file)
    mock_file.write = MagicMock()
    mock_tempfile.return_value = mock_file

    mock_run.return_value = MagicMock(returncode=0)

    result = open_editor(initial)

    assert result is None


@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "editor"))
@patch("tempfile.NamedTemporaryFile")
def test_open_editor_returns_none_on_error(
    mock_tempfile: MagicMock, mock_run: MagicMock, tmp_path: Path
) -> None:
    """Test that open_editor returns None on subprocess error."""
    temp_file = tmp_path / "test.md"
    temp_file.write_text("content")

    mock_file = MagicMock()
    mock_file.__enter__ = MagicMock(return_value=mock_file)
    mock_file.__exit__ = MagicMock(return_value=False)
    mock_file.name = str(temp_file)
    mock_file.write = MagicMock()
    mock_tempfile.return_value = mock_file

    result = open_editor()

    assert result is None
