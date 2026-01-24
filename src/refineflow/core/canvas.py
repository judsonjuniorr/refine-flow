"""Business Case Canvas model."""

from pydantic import BaseModel, Field


class BusinessCaseCanvas(BaseModel):
    """Business Case Canvas model."""

    # Problem
    problem_statement: str = Field(default="", description="What is the problem?")
    problem_owner: str = Field(default="", description="Who has the problem?")
    problem_importance: str = Field(default="", description="Why is it important?")

    # Solution
    proposed_solution: str = Field(default="", description="What is the proposed solution?")
    solution_relation: str = Field(default="", description="How does solution relate to problem?")

    # Resources
    tangible_resources: list[str] = Field(
        default_factory=list, description="Tangible resources needed"
    )
    intangible_resources: list[str] = Field(
        default_factory=list, description="Intangible resources needed"
    )
    internal_dependencies: list[str] = Field(
        default_factory=list, description="Internal dependencies"
    )
    external_dependencies: list[str] = Field(
        default_factory=list, description="External dependencies"
    )

    # Benefits
    purpose: str = Field(default="", description="Why are we doing this?")
    goals: list[str] = Field(default_factory=list, description="What do we aim to achieve?")
    financial_benefits: list[str] = Field(default_factory=list, description="Financial benefits")
    non_financial_benefits: list[str] = Field(
        default_factory=list, description="Non-financial benefits"
    )

    # Scope
    in_scope: list[str] = Field(default_factory=list, description="What is in scope")
    out_of_scope: list[str] = Field(default_factory=list, description="What is out of scope")
    timeline: str = Field(default="", description="Time available")
    resources_available: str = Field(default="", description="Resources and technology available")
    strategic_relevance: str = Field(default="", description="Strategic relevance")

    # Risks
    risks: list[dict[str, str]] = Field(
        default_factory=list,
        description="Risks with impact and mitigation (risk, impact, mitigation keys)",
    )

    # Stakeholders
    stakeholders: list[dict[str, str]] = Field(
        default_factory=list,
        description="Stakeholders with interests and engagement (name, interests, engagement keys)",
    )

    # Complexity
    specification_effort: str = Field(default="", description="Specification/documentation effort")
    development_effort: str = Field(default="", description="Development effort")
    testing_effort: str = Field(default="", description="Testing effort")

    # Communication Plan
    materials: list[str] = Field(default_factory=list, description="Communication materials")
    videos: list[str] = Field(default_factory=list, description="Video materials")
    training: list[str] = Field(default_factory=list, description="Training requirements")

    # Costs
    cost_sources: list[str] = Field(default_factory=list, description="Cost sources")
    budget: str = Field(default="", description="Approximate budget")
    total_cost_over_time: str = Field(default="", description="Total cost over time")

    # Metrics
    success_metrics: list[str] = Field(default_factory=list, description="How to measure success")
    benefit_metrics: list[str] = Field(default_factory=list, description="How to measure benefits")
