"""LLM processing logic."""

import json

from refineflow.core.models import Activity, Entry
from refineflow.core.state import ActivityState
from refineflow.llm.client import OpenAIClient
from refineflow.llm.prompts import (
    build_chat_prompt,
    build_extraction_prompt,
    build_jira_export_prompt,
)
from refineflow.utils.logger import get_logger
from refineflow.utils.time import get_timestamp

logger = get_logger(__name__)


class LLMProcessor:
    """Processes LLM tasks for activity refinement."""

    def __init__(self) -> None:
        """Initialize processor."""
        self.client = OpenAIClient()

    def process_entry(
        self, activity: Activity, entry: Entry, current_state: ActivityState
    ) -> ActivityState | None:
        """
        Process a new entry and update state.

        Args:
            activity: Current activity
            entry: New entry
            current_state: Current state

        Returns:
            Updated state or None if processing fails
        """
        if not self.client.is_available():
            logger.warning("OpenAI not available, skipping state extraction")
            return None

        prompt = build_extraction_prompt(activity, entry, current_state)
        logger.debug(f"Extraction prompt length: {len(prompt)} chars")
        response = self.client.complete(prompt, max_tokens=1500)

        if not response:
            logger.warning("Empty response from OpenAI for state extraction")
            return None

        try:
            # Remove markdown code blocks se presentes
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # Remove ```json ou ``` do início e fim
                lines = cleaned_response.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_response = "\n".join(lines)

            # Try to parse JSON response
            data = json.loads(cleaned_response)
            updated_state = ActivityState(**data)
            updated_state.last_updated = get_timestamp()
            logger.info("Successfully extracted and updated activity state")
            return updated_state
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse state update: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return None

    def answer_question(
        self, activity: Activity, state: ActivityState, log_content: str, question: str
    ) -> str:
        """
        Answer a question about the activity.

        Args:
            activity: Current activity
            state: Current state
            log_content: Recent log content
            question: User question

        Returns:
            Answer text
        """
        if not self.client.is_available():
            return "OpenAI is not configured. Cannot answer questions."

        prompt = build_chat_prompt(activity, state, log_content, question)
        return self.client.complete(prompt, max_tokens=800)

    def generate_jira_export(self, activity: Activity, state: ActivityState) -> str:
        """
        Generate Jira export content.

        Args:
            activity: Current activity
            state: Current state

        Returns:
            Jira export markdown
        """
        if not self.client.is_available():
            return self._generate_jira_fallback(activity, state)

        prompt = build_jira_export_prompt(activity, state)
        return self.client.complete(prompt, max_tokens=1500)

    def _generate_jira_fallback(self, activity: Activity, state: ActivityState) -> str:
        """Generate basic Jira export without AI."""
        return f"""## Parent Task: {activity.title}

**Description**: {activity.description}

{state.summary}

**Acceptance Criteria**:
- All functional requirements met
- All tests passing

## Backend Subtask

**Title**: [BE] {activity.title}

**Description**: Implement backend components

## Frontend Subtask

**Title**: [FE] {activity.title}

**Description**: Implement frontend components
"""
