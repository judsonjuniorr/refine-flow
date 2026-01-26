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


