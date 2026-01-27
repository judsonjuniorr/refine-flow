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


def test_state_merge_basic() -> None:
    """Test basic state merging."""
    existing = ActivityState(
        summary="Original summary",
        functional_requirements=["Req 1"],
        open_questions={"Frontend": ["Question 1"]},
        last_updated="2026-01-20T10:00:00",
    )

    new = ActivityState(
        summary="Updated summary",
        functional_requirements=["Req 2"],
        open_questions={"Backend": ["Question 2"]},
        last_updated="2026-01-20T11:00:00",
    )

    merged = existing.merge_with(new)

    # New summary should be used
    assert merged.summary == "Updated summary"

    # Requirements should be merged
    assert len(merged.functional_requirements) == 2
    assert "Req 1" in merged.functional_requirements
    assert "Req 2" in merged.functional_requirements

    # Questions should be merged by category
    assert "Frontend" in merged.open_questions
    assert "Backend" in merged.open_questions
    assert len(merged.open_questions["Frontend"]) == 1
    assert len(merged.open_questions["Backend"]) == 1

    # Timestamp should be updated
    assert merged.last_updated == "2026-01-20T11:00:00"


def test_state_merge_same_category_questions() -> None:
    """Test merging questions in the same category."""
    existing = ActivityState(
        open_questions={
            "Frontend": ["Question A", "Question B"],
            "Backend": ["Question X"],
        }
    )

    new = ActivityState(
        open_questions={
            "Frontend": ["Question C"],
            "Backend": ["Question Y", "Question Z"],
        }
    )

    merged = existing.merge_with(new)

    # Frontend should have all 3 questions
    assert len(merged.open_questions["Frontend"]) == 3
    assert "Question A" in merged.open_questions["Frontend"]
    assert "Question B" in merged.open_questions["Frontend"]
    assert "Question C" in merged.open_questions["Frontend"]

    # Backend should have all 3 questions
    assert len(merged.open_questions["Backend"]) == 3
    assert "Question X" in merged.open_questions["Backend"]
    assert "Question Y" in merged.open_questions["Backend"]
    assert "Question Z" in merged.open_questions["Backend"]


def test_state_merge_deduplication() -> None:
    """Test that merge deduplicates identical items."""
    existing = ActivityState(
        functional_requirements=["Requirement A", "Requirement B"],
        open_questions={"Frontend": ["Question 1", "Question 2"]},
    )

    new = ActivityState(
        functional_requirements=["Requirement B", "Requirement C"],  # B is duplicate
        open_questions={"Frontend": ["Question 2", "Question 3"]},  # Q2 is duplicate
    )

    merged = existing.merge_with(new)

    # Requirements should be deduplicated
    assert len(merged.functional_requirements) == 3
    assert merged.functional_requirements.count("Requirement B") == 1

    # Questions should be deduplicated (case-insensitive)
    assert len(merged.open_questions["Frontend"]) == 3
    question_texts = [q.lower() for q in merged.open_questions["Frontend"]]
    assert question_texts.count("question 2") == 1


def test_state_merge_complex_types() -> None:
    """Test merging complex dict-based fields."""
    existing = ActivityState(
        action_items=[
            {"action": "Task 1", "owner": "Alice", "status": "open"}
        ],
        identified_risks=[
            {"risk": "Risk A", "impact": "High", "mitigation": "Plan A"}
        ],
    )

    new = ActivityState(
        action_items=[
            {"action": "Task 2", "owner": "Bob", "status": "open"}
        ],
        identified_risks=[
            {"risk": "Risk B", "impact": "Medium", "mitigation": "Plan B"}
        ],
    )

    merged = existing.merge_with(new)

    # Both action items should be present
    assert len(merged.action_items) == 2
    assert any(item["action"] == "Task 1" for item in merged.action_items)
    assert any(item["action"] == "Task 2" for item in merged.action_items)

    # Both risks should be present
    assert len(merged.identified_risks) == 2
    assert any(risk["risk"] == "Risk A" for risk in merged.identified_risks)
    assert any(risk["risk"] == "Risk B" for risk in merged.identified_risks)


def test_state_merge_preserves_empty_summary() -> None:
    """Test that empty new summary doesn't override existing one."""
    existing = ActivityState(
        summary="Important existing summary",
    )

    new = ActivityState(
        summary="",  # Empty summary
    )

    merged = existing.merge_with(new)

    # Should keep existing summary when new is empty
    assert merged.summary == "Important existing summary"
