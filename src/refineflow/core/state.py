"""Activity state model for tracking structured information."""

from typing import Any

from pydantic import BaseModel, Field


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
    open_questions: list[str] = Field(default_factory=list, description="Open questions")
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
