"""Tests for Activity State model."""

from refineflow.core.state import ActivityState
from refineflow.utils.time import get_timestamp


def test_state_creation_empty() -> None:
    """Test ActivityState creation with defaults."""
    state = ActivityState()
    assert state.summary == ""
    assert state.action_items == []
    assert state.open_questions == {}
    assert state.information_gaps == []


def test_state_with_summary() -> None:
    """Test ActivityState with summary."""
    state = ActivityState(
        summary="Working on OAuth2 implementation for user authentication",
        last_updated=get_timestamp(),
    )
    assert "OAuth2" in state.summary
    assert state.last_updated != ""


def test_state_with_action_items() -> None:
    """Test ActivityState with action items."""
    state = ActivityState(
        action_items=[
            {"action": "Review security requirements", "owner": "Alice", "status": "open"},
            {"action": "Setup OAuth provider", "owner": "Bob", "status": "in_progress"},
        ]
    )
    assert len(state.action_items) == 2
    assert state.action_items[0]["action"] == "Review security requirements"
    assert state.action_items[1]["status"] == "in_progress"


def test_state_with_questions_and_decisions() -> None:
    """Test ActivityState with questions and decisions."""
    # Test backward compatibility - old list format auto-migrates to dict
    state = ActivityState(
        open_questions=[
            "Which OAuth provider should we use?",
            "Do we need 2FA integration?",
        ],
        decisions=[
            {
                "decision": "Use OAuth 2.0 standard",
                "rationale": "Industry standard, well-supported",
                "date": "2026-01-20",
            }
        ],
    )
    # After migration, questions are in "Geral" category
    assert isinstance(state.open_questions, dict)
    assert "Geral" in state.open_questions
    assert len(state.open_questions["Geral"]) == 2
    assert len(state.decisions) == 1
    assert "OAuth 2.0" in state.decisions[0]["decision"]


def test_state_with_requirements() -> None:
    """Test ActivityState with requirements."""
    state = ActivityState(
        functional_requirements=[
            "Support Google and GitHub OAuth",
            "Store refresh tokens securely",
        ],
        non_functional_requirements=[
            "Authentication must complete in <2s",
            "99.9% availability",
        ],
    )
    assert len(state.functional_requirements) == 2
    assert len(state.non_functional_requirements) == 2
    assert "Google" in state.functional_requirements[0]


def test_state_with_risks() -> None:
    """Test ActivityState with risks."""
    state = ActivityState(
        identified_risks=[
            {
                "risk": "Token leakage",
                "impact": "Security breach",
                "mitigation": "Encrypted storage + rotation",
            }
        ]
    )
    assert len(state.identified_risks) == 1
    assert state.identified_risks[0]["risk"] == "Token leakage"


def test_state_with_dependencies() -> None:
    """Test ActivityState with dependencies."""
    state = ActivityState(
        dependencies=[
            {
                "dependency": "User service API",
                "type": "internal",
                "status": "available",
            },
            {
                "dependency": "OAuth provider",
                "type": "external",
                "status": "pending_approval",
            },
        ]
    )
    assert len(state.dependencies) == 2
    assert state.dependencies[0]["type"] == "internal"
    assert state.dependencies[1]["status"] == "pending_approval"


def test_state_with_metrics_and_costs() -> None:
    """Test ActivityState with metrics and costs."""
    state = ActivityState(
        metrics=[
            {
                "metric": "Login success rate",
                "target": ">95%",
                "measurement": "Analytics dashboard",
            }
        ],
        costs=[
            {
                "item": "OAuth provider subscription",
                "amount": "$500/month",
                "notes": "Based on user volume",
            }
        ],
    )
    assert len(state.metrics) == 1
    assert len(state.costs) == 1
    assert state.metrics[0]["target"] == ">95%"


def test_state_with_information_gaps() -> None:
    """Test ActivityState with information gaps."""
    state = ActivityState(
        information_gaps=[
            "Exact user volume projections",
            "Legal requirements for data retention",
            "Budget approval timeline",
        ]
    )
    assert len(state.information_gaps) == 3
    assert "Budget approval" in state.information_gaps[2]


def test_state_serialization() -> None:
    """Test ActivityState serialization."""
    state = ActivityState(
        summary="Test summary",
        action_items=[{"action": "Test", "owner": "Me", "status": "open"}],
    )
    data = state.model_dump()
    assert isinstance(data, dict)
    assert data["summary"] == "Test summary"
    assert len(data["action_items"]) == 1
