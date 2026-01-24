"""Core domain models for activities and entries."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ActivityStatus(str, Enum):
    """Activity status enumeration."""

    IN_PROGRESS = "in_progress"
    FINALIZED = "finalized"


class EntryType(str, Enum):
    """Entry type enumeration."""

    NOTE = "note"
    QUESTION = "question"
    ANSWER = "answer"
    TRANSCRIPT = "transcript"
    JIRA_DESCRIPTION = "jira_description"
    DECISION = "decision"
    REQUIREMENT = "requirement"
    RISK = "risk"
    METRIC = "metric"
    COST = "cost"
    DEPENDENCY = "dependency"


class Entry(BaseModel):
    """Activity entry model."""

    model_config = ConfigDict(use_enum_values=True)

    entry_type: EntryType = Field(..., description="Type of entry")
    content: str = Field(..., description="Entry content")
    timestamp: str = Field(..., description="ISO timestamp")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class Activity(BaseModel):
    """Activity model."""

    model_config = ConfigDict(use_enum_values=True)

    slug: str = Field(..., description="URL-friendly identifier")
    title: str = Field(..., description="Activity title")
    description: str = Field(..., description="Activity description")
    status: ActivityStatus = Field(
        default=ActivityStatus.IN_PROGRESS, description="Activity status"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    # Initialization data
    problem: str = Field(default="", description="Problem statement")
    stakeholders: list[str] = Field(default_factory=list, description="List of stakeholders")
    constraints: str = Field(default="", description="Constraints and deadlines")
    affected_system: str = Field(default="", description="Affected product/system")
