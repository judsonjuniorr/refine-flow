"""Filesystem-based storage for activities."""

import json
import re
from pathlib import Path

from refineflow.core.models import Activity, ActivityStatus, Entry, EntryType
from refineflow.core.state import ActivityState
from refineflow.utils.config import get_config
from refineflow.utils.logger import get_logger
from refineflow.utils.time import format_timestamp, get_timestamp

from .index import ActivityIndex
from .templates import ACTIVITY_TEMPLATE, LOG_TEMPLATE

logger = get_logger(__name__)


def get_status_value(status: ActivityStatus | str) -> str:
    """Get string value from status (handles both enum and string)."""
    return status if isinstance(status, str) else status.value


def get_entry_type_value(entry_type: EntryType | str) -> str:
    """Get string value from entry type (handles both enum and string)."""
    return entry_type if isinstance(entry_type, str) else entry_type.value


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text[:50]  # Limit length


class ActivityStorage:
    """Manages activity storage on filesystem."""

    def __init__(self) -> None:
        """Initialize storage."""
        self.config = get_config()
        self.activities_dir = self.config.activities_dir
        self.index = ActivityIndex(self.config.db_path)

    def create_activity(self, activity: Activity) -> Path:
        """
        Create a new activity with folder structure and templates.

        Args:
            activity: Activity instance

        Returns:
            Path to activity directory
        """
        activity_dir = self.activities_dir / activity.slug
        activity_dir.mkdir(parents=True, exist_ok=True)

        # Create activity.md
        activity_md = activity_dir / "activity.md"
        stakeholders_str = "\n".join(f"- {s}" for s in activity.stakeholders) or "- None specified"
        metadata_str = "\n".join(f"- {k}: {v}" for k, v in activity.metadata.items()) or "- None"

        activity_content = ACTIVITY_TEMPLATE.format(
            title=activity.title,
            status=get_status_value(activity.status),
            created_at=format_timestamp(activity.created_at),
            updated_at=format_timestamp(activity.updated_at),
            description=activity.description,
            problem=activity.problem or "Not specified",
            stakeholders=stakeholders_str,
            constraints=activity.constraints or "Not specified",
            affected_system=activity.affected_system or "Not specified",
            metadata=metadata_str,
        )
        activity_md.write_text(activity_content, encoding="utf-8")

        # Create log.md
        log_md = activity_dir / "log.md"
        log_content = LOG_TEMPLATE.format(title=activity.title)
        log_md.write_text(log_content, encoding="utf-8")

        # Create canvas.md (placeholder)
        canvas_md = activity_dir / "canvas.md"
        canvas_md.write_text(
            f"# Business Case Canvas: {activity.title}\n\n_Not yet generated_\n",
            encoding="utf-8",
        )

        # Create jira_export.md (placeholder)
        jira_md = activity_dir / "jira_export.md"
        jira_md.write_text(
            f"# Jira Export: {activity.title}\n\n_Not yet generated_\n",
            encoding="utf-8",
        )

        # Create state.json
        state_json = activity_dir / "state.json"
        initial_state = ActivityState(
            summary=activity.description,
            last_updated=activity.created_at,
        )
        state_json.write_text(initial_state.model_dump_json(indent=2), encoding="utf-8")

        # Create chat.md (empty)
        chat_md = activity_dir / "chat.md"
        chat_md.write_text(f"# Chat History: {activity.title}\n\n", encoding="utf-8")

        # Save activity metadata to JSON for easy loading
        activity_json = activity_dir / "activity.json"
        activity_json.write_text(activity.model_dump_json(indent=2), encoding="utf-8")

        # Add to index
        self.index.add_activity(activity)

        logger.info(f"Created activity: {activity.slug} at {activity_dir}")
        return activity_dir

    def load_activity(self, slug: str) -> Activity | None:
        """
        Load an activity by slug.

        Args:
            slug: Activity slug

        Returns:
            Activity instance or None if not found
        """
        activity_dir = self.activities_dir / slug
        activity_json = activity_dir / "activity.json"

        if not activity_json.exists():
            logger.warning(f"Activity not found: {slug}")
            return None

        data = json.loads(activity_json.read_text(encoding="utf-8"))
        return Activity(**data)

    def save_activity(self, activity: Activity) -> None:
        """
        Save activity metadata (update activity.json and activity.md).

        Args:
            activity: Activity instance
        """
        activity_dir = self.activities_dir / activity.slug

        # Update activity.json
        activity_json = activity_dir / "activity.json"
        activity_json.write_text(activity.model_dump_json(indent=2), encoding="utf-8")

        # Update activity.md
        activity_md = activity_dir / "activity.md"
        stakeholders_str = "\n".join(f"- {s}" for s in activity.stakeholders) or "- None specified"
        metadata_str = "\n".join(f"- {k}: {v}" for k, v in activity.metadata.items()) or "- None"

        activity_content = ACTIVITY_TEMPLATE.format(
            title=activity.title,
            status=get_status_value(activity.status),
            created_at=format_timestamp(activity.created_at),
            updated_at=format_timestamp(activity.updated_at),
            description=activity.description,
            problem=activity.problem or "Not specified",
            stakeholders=stakeholders_str,
            constraints=activity.constraints or "Not specified",
            affected_system=activity.affected_system or "Not specified",
            metadata=metadata_str,
        )
        activity_md.write_text(activity_content, encoding="utf-8")

        # Update index
        self.index.update_activity(activity)

        logger.info(f"Saved activity: {activity.slug}")

    def append_to_log(self, slug: str, entry: Entry) -> None:
        """
        Append an entry to the activity log.

        Args:
            slug: Activity slug
            entry: Entry instance
        """
        activity_dir = self.activities_dir / slug
        log_md = activity_dir / "log.md"

        # Format entry
        entry_type_title = get_entry_type_value(entry.entry_type).title()
        timestamp_str = format_timestamp(entry.timestamp)
        entry_text = f"\n## {entry_type_title} - {timestamp_str}\n\n"
        entry_text += f"{entry.content}\n\n"

        if entry.metadata:
            entry_text += "**Metadata:**\n"
            for key, value in entry.metadata.items():
                entry_text += f"- {key}: {value}\n"
            entry_text += "\n"

        entry_text += "---\n"

        # Append to log
        with open(log_md, "a", encoding="utf-8") as f:
            f.write(entry_text)

        logger.info(f"Appended {get_entry_type_value(entry.entry_type)} to log: {slug}")

    def load_state(self, slug: str) -> ActivityState | None:
        """
        Load activity state.

        Args:
            slug: Activity slug

        Returns:
            ActivityState instance or None if not found
        """
        activity_dir = self.activities_dir / slug
        state_json = activity_dir / "state.json"

        if not state_json.exists():
            return None

        data = json.loads(state_json.read_text(encoding="utf-8"))
        return ActivityState(**data)

    def save_state(self, slug: str, state: ActivityState) -> None:
        """
        Save activity state.

        Args:
            slug: Activity slug
            state: ActivityState instance
        """
        activity_dir = self.activities_dir / slug
        state_json = activity_dir / "state.json"

        state_json.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        logger.info(f"Saved state for: {slug}")

    def list_activities(self, status: ActivityStatus | None = None) -> list[Activity]:
        """
        List all activities, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of Activity instances
        """
        activities: list[Activity] = []

        for activity_dir in self.activities_dir.iterdir():
            if not activity_dir.is_dir():
                continue

            activity = self.load_activity(activity_dir.name)
            if activity is None:
                continue

            if status is None or activity.status == status:
                activities.append(activity)

        # Sort by updated_at descending
        activities.sort(key=lambda a: a.updated_at, reverse=True)

        return activities

    def finalize_activity(self, slug: str) -> None:
        """
        Mark an activity as finalized.

        Args:
            slug: Activity slug
        """
        activity = self.load_activity(slug)
        if activity is None:
            raise ValueError(f"Activity not found: {slug}")

        activity.status = ActivityStatus.FINALIZED
        activity.updated_at = get_timestamp()
        self.save_activity(activity)

        logger.info(f"Finalized activity: {slug}")

    def is_finalized(self, slug: str) -> bool:
        """
        Check if an activity is finalized.

        Args:
            slug: Activity slug

        Returns:
            True if finalized, False otherwise
        """
        activity = self.load_activity(slug)
        return activity is not None and activity.status == ActivityStatus.FINALIZED

    def get_activity_dir(self, slug: str) -> Path:
        """
        Get the directory path for an activity.

        Args:
            slug: Activity slug

        Returns:
            Path to activity directory
        """
        return self.activities_dir / slug

    def read_log(self, slug: str) -> str:
        """
        Read the full log content for an activity.

        Args:
            slug: Activity slug

        Returns:
            Log content as string
        """
        log_path = self.get_activity_dir(slug) / "log.md"
        if not log_path.exists():
            return ""
        return log_path.read_text(encoding="utf-8")

    def read_canvas(self, slug: str) -> str:
        """
        Read the canvas content for an activity.

        Args:
            slug: Activity slug

        Returns:
            Canvas content as string
        """
        canvas_path = self.get_activity_dir(slug) / "canvas.md"
        if not canvas_path.exists():
            return ""
        return canvas_path.read_text(encoding="utf-8")

    def write_canvas(self, slug: str, content: str) -> None:
        """
        Write canvas content.

        Args:
            slug: Activity slug
            content: Canvas markdown content
        """
        canvas_path = self.get_activity_dir(slug) / "canvas.md"
        canvas_path.write_text(content, encoding="utf-8")
        logger.info(f"Wrote canvas for: {slug}")

    def write_jira_export(self, slug: str, content: str) -> None:
        """
        Write Jira export content.

        Args:
            slug: Activity slug
            content: Jira export content
        """
        jira_path = self.get_activity_dir(slug) / "jira_export.md"
        jira_path.write_text(content, encoding="utf-8")
        logger.info(f"Wrote Jira export for: {slug}")
