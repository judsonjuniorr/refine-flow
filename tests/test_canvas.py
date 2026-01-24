"""Tests for Business Case Canvas model."""

from refineflow.core.canvas import BusinessCaseCanvas


def test_canvas_creation_empty() -> None:
    """Test BusinessCaseCanvas creation with defaults."""
    canvas = BusinessCaseCanvas()
    assert canvas.problem_statement == ""
    assert canvas.tangible_resources == []
    assert canvas.risks == []
    assert canvas.stakeholders == []


def test_canvas_with_problem() -> None:
    """Test BusinessCaseCanvas with problem data."""
    canvas = BusinessCaseCanvas(
        problem_statement="High cart abandonment rate",
        problem_owner="E-commerce team",
        problem_importance="Losing 30% potential revenue",
    )
    assert canvas.problem_statement == "High cart abandonment rate"
    assert canvas.problem_owner == "E-commerce team"
    assert "revenue" in canvas.problem_importance.lower()


def test_canvas_with_solution() -> None:
    """Test BusinessCaseCanvas with solution data."""
    canvas = BusinessCaseCanvas(
        proposed_solution="Implement one-click checkout",
        solution_relation="Reduces friction in purchase process",
    )
    assert canvas.proposed_solution == "Implement one-click checkout"
    assert canvas.solution_relation == "Reduces friction in purchase process"


def test_canvas_with_resources() -> None:
    """Test BusinessCaseCanvas with resources."""
    canvas = BusinessCaseCanvas(
        tangible_resources=["3 developers", "Payment gateway API"],
        intangible_resources=["Product design expertise", "User research"],
        internal_dependencies=["User service", "Payment service"],
        external_dependencies=["Stripe API", "Analytics platform"],
    )
    assert len(canvas.tangible_resources) == 2
    assert len(canvas.internal_dependencies) == 2
    assert "Stripe API" in canvas.external_dependencies


def test_canvas_with_risks() -> None:
    """Test BusinessCaseCanvas with risks."""
    canvas = BusinessCaseCanvas(
        risks=[
            {
                "risk": "Integration complexity",
                "impact": "High - could delay launch",
                "mitigation": "Proof of concept in sprint 1",
            },
            {
                "risk": "Security concerns",
                "impact": "Critical - compliance issues",
                "mitigation": "Security audit before release",
            },
        ]
    )
    assert len(canvas.risks) == 2
    assert canvas.risks[0]["risk"] == "Integration complexity"
    assert "Security audit" in canvas.risks[1]["mitigation"]


def test_canvas_with_stakeholders() -> None:
    """Test BusinessCaseCanvas with stakeholders."""
    canvas = BusinessCaseCanvas(
        stakeholders=[
            {
                "name": "Product Manager",
                "interests": "Feature completion",
                "engagement": "High",
            },
            {
                "name": "CTO",
                "interests": "Technical debt",
                "engagement": "Medium",
            },
        ]
    )
    assert len(canvas.stakeholders) == 2
    assert canvas.stakeholders[0]["name"] == "Product Manager"


def test_canvas_with_complexity() -> None:
    """Test BusinessCaseCanvas with complexity analysis."""
    canvas = BusinessCaseCanvas(
        specification_effort="2 days",
        development_effort="3 sprints",
        testing_effort="1 sprint",
    )
    assert canvas.specification_effort == "2 days"
    assert canvas.development_effort == "3 sprints"


def test_canvas_with_metrics() -> None:
    """Test BusinessCaseCanvas with metrics."""
    canvas = BusinessCaseCanvas(
        success_metrics=["Conversion rate increase", "Cart abandonment reduction"],
        benefit_metrics=["Revenue growth", "Customer satisfaction score"],
    )
    assert len(canvas.success_metrics) == 2
    assert "Revenue growth" in canvas.benefit_metrics


def test_canvas_serialization() -> None:
    """Test BusinessCaseCanvas serialization."""
    canvas = BusinessCaseCanvas(
        problem_statement="Test problem",
        goals=["Goal 1", "Goal 2"],
    )
    data = canvas.model_dump()
    assert isinstance(data, dict)
    assert data["problem_statement"] == "Test problem"
    assert len(data["goals"]) == 2
