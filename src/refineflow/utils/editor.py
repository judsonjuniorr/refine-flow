"""System editor integration for RefineFlow."""

import os
import subprocess
import tempfile
from pathlib import Path


def open_editor(initial_content: str = "", suffix: str = ".md") -> str | None:
    """
    Open the system's default editor for text input.

    Args:
        initial_content: Initial text to populate the editor
        suffix: File suffix for the temporary file

    Returns:
        User's edited text, or None if cancelled/error
    """
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tf:
        tf.write(initial_content)
        temp_path = Path(tf.name)

    try:
        # Open editor
        subprocess.run([editor, str(temp_path)], check=True)

        # Read edited content
        content = temp_path.read_text(encoding="utf-8")

        # Remove temp file
        temp_path.unlink()

        return content.strip() if content.strip() != initial_content.strip() else None

    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Clean up on error
        if temp_path.exists():
            temp_path.unlink()
        return None
