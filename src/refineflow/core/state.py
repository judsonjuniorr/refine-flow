"""Activity state model for tracking structured information."""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class ActivityState(BaseModel):
    """
    Structured state for an activity.

    This is continuously updated by AI based on new entries.
    """

    # Summary
    summary: str = Field(default="", description="Current summary of the activity")

    # Actions and Questions
    action_items: list[dict[str, str]] = Field(
        default_factory=list, description="Open action items (action, owner, status keys)"
    )
    open_questions: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Categorized questions (Frontend, Backend, Arquitetura, Produto, UX/UI, Geral)",
    )
    decisions: list[dict[str, str]] = Field(
        default_factory=list, description="Documented decisions (decision, rationale, date keys)"
    )

    # Requirements
    functional_requirements: list[str] = Field(
        default_factory=list, description="Functional requirements"
    )
    non_functional_requirements: list[str] = Field(
        default_factory=list, description="Non-functional requirements"
    )

    # Risks and Dependencies
    identified_risks: list[dict[str, str]] = Field(
        default_factory=list, description="Identified risks (risk, impact, mitigation keys)"
    )
    dependencies: list[dict[str, str]] = Field(
        default_factory=list,
        description="Dependencies (dependency, type, status keys - type: internal/external)",
    )

    # Metrics and Costs
    metrics: list[dict[str, str]] = Field(
        default_factory=list, description="Success metrics (metric, target, measurement keys)"
    )
    costs: list[dict[str, str]] = Field(
        default_factory=list, description="Cost estimates (item, amount, notes keys)"
    )

    # Gaps - Information we still need
    information_gaps: list[str] = Field(
        default_factory=list, description="Missing information or uncertainties"
    )

    # Business Case Canvas (embedded or referenced)
    canvas: dict[str, Any] = Field(default_factory=dict, description="Business Case Canvas data")

    # Last updated
    last_updated: str = Field(default="", description="Last update timestamp")

    @model_validator(mode="before")
    @classmethod
    def migrate_open_questions(cls, data: Any) -> Any:
        """
        Migrate open_questions from old list format to new dict format.

        If open_questions is a list (old format), convert it to a dict
        with all questions in the "Geral" category.
        """
        if isinstance(data, dict):
            open_questions = data.get("open_questions")

            # If it's a list (old format), migrate to dict with "Geral" category
            if isinstance(open_questions, list):
                data["open_questions"] = {"Geral": open_questions}

        return data

    def merge_with(self, new_state: "ActivityState") -> "ActivityState":
        """
        Merge this state with a new state from LLM extraction.

        Strategy:
        - Use new summary (latest is most complete)
        - Merge lists by appending new items (deduplicated where possible)
        - For open_questions dict, merge by category (deduplicate questions)
        - Update last_updated to new timestamp

        Args:
            new_state: New state from LLM extraction

        Returns:
            Merged ActivityState
        """
        # Helper to deduplicate lists while preserving order
        def dedupe_list(items: list) -> list:
            seen = set()
            result = []
            for item in items:
                # For dict items, use a tuple of sorted items as key
                if isinstance(item, dict):
                    key = tuple(sorted(item.items()))
                else:
                    key = item
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        # Helper to deduplicate string lists (case-insensitive)
        def dedupe_strings(items: list[str]) -> list[str]:
            seen = set()
            result = []
            for item in items:
                key = item.lower().strip()
                if key not in seen and key:
                    seen.add(key)
                    result.append(item)
            return result

        # Merge open_questions by category
        merged_questions = dict(self.open_questions)
        for category, questions in new_state.open_questions.items():
            if category in merged_questions:
                # Merge questions for existing category
                combined = merged_questions[category] + questions
                merged_questions[category] = dedupe_strings(combined)
            else:
                # New category
                merged_questions[category] = dedupe_strings(questions)

        return ActivityState(
            summary=new_state.summary if new_state.summary else self.summary,
            action_items=dedupe_list(self.action_items + new_state.action_items),
            open_questions=merged_questions,
            decisions=dedupe_list(self.decisions + new_state.decisions),
            functional_requirements=dedupe_strings(
                self.functional_requirements + new_state.functional_requirements
            ),
            non_functional_requirements=dedupe_strings(
                self.non_functional_requirements + new_state.non_functional_requirements
            ),
            identified_risks=dedupe_list(self.identified_risks + new_state.identified_risks),
            dependencies=dedupe_list(self.dependencies + new_state.dependencies),
            metrics=dedupe_list(self.metrics + new_state.metrics),
            costs=dedupe_list(self.costs + new_state.costs),
            information_gaps=dedupe_strings(self.information_gaps + new_state.information_gaps),
            canvas=new_state.canvas if new_state.canvas else self.canvas,
            last_updated=new_state.last_updated,
        )

