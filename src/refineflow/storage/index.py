"""SQLite index for fast activity lookup."""

import sqlite3
from pathlib import Path

from refineflow.core.models import Activity, ActivityStatus
from refineflow.utils.logger import get_logger

logger = get_logger(__name__)


def get_status_value(status: ActivityStatus | str) -> str:
    """Get string value from status (handles both enum and string)."""
    return status if isinstance(status, str) else status.value


class ActivityIndex:
    """SQLite-based index for activities."""

    def __init__(self, db_path: Path) -> None:
        """
        Initialize the activity index.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                problem TEXT,
                stakeholders TEXT,
                constraints TEXT,
                affected_system TEXT
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON activities(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_updated_at ON activities(updated_at DESC)
        """)

        conn.commit()
        conn.close()

        logger.debug(f"Initialized activity index at {self.db_path}")

    def add_activity(self, activity: Activity) -> None:
        """
        Add an activity to the index.

        Args:
            activity: Activity instance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stakeholders_str = ",".join(activity.stakeholders)

        cursor.execute(
            """
            INSERT OR REPLACE INTO activities
            (slug, title, description, status, created_at, updated_at,
             problem, stakeholders, constraints, affected_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                activity.slug,
                activity.title,
                activity.description,
                get_status_value(activity.status),
                activity.created_at,
                activity.updated_at,
                activity.problem,
                stakeholders_str,
                activity.constraints,
                activity.affected_system,
            ),
        )

        conn.commit()
        conn.close()

        logger.debug(f"Added activity to index: {activity.slug}")

    def update_activity(self, activity: Activity) -> None:
        """
        Update an activity in the index.

        Args:
            activity: Activity instance
        """
        self.add_activity(activity)  # INSERT OR REPLACE handles updates

    def get_activity(self, slug: str) -> dict[str, str] | None:
        """
        Get activity metadata from index.

        Args:
            slug: Activity slug

        Returns:
            Activity metadata dict or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activities WHERE slug = ?", (slug,))
        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return dict(row)

    def search_activities(
        self,
        query: str | None = None,
        status: ActivityStatus | None = None,
    ) -> list[dict[str, str]]:
        """
        Search activities.

        Args:
            query: Text search query (searches title, description, problem)
            status: Optional status filter

        Returns:
            List of activity metadata dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM activities WHERE 1=1"
        params: list[str] = []

        if status is not None:
            sql += " AND status = ?"
            params.append(get_status_value(status))

        if query:
            sql += " AND (title LIKE ? OR description LIKE ? OR problem LIKE ?)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])

        sql += " ORDER BY updated_at DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    def delete_activity(self, slug: str) -> None:
        """
        Remove an activity from the index.

        Args:
            slug: Activity slug
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM activities WHERE slug = ?", (slug,))

        conn.commit()
        conn.close()

        logger.debug(f"Deleted activity from index: {slug}")
