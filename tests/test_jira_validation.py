"""Tests for Jira export validation logic."""

from refineflow.llm.processor_langchain import validate_jira_structure


class TestValidateJiraStructure:
    """Test suite for Jira structure validation."""

    def test_validate_multiple_backend_tasks(self):
        """Test detection of 2-7 backend tasks."""
        # Valid: 3 backend tasks
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** P / 1 week

# Subtarefa Backend 3
**Título:** Backend — Task 3
**Estimativa:** M / 2.5 weeks
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about backend task count
        backend_warnings = [w for w in warnings if "backend" in w.lower() and "task" in w.lower()]
        assert len(backend_warnings) == 0

        # Invalid: only 1 backend task
        invalid_content = """
# Subtarefa Backend
**Título:** Backend — Single Task
**Estimativa:** G / 8 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        assert is_valid is False
        assert any("backend" in w.lower() and ("2-7" in w or "múltip" in w) for w in warnings)

        # Invalid: 8 backend tasks (too many)
        many_tasks = "\n".join(
            [
                f"# Subtarefa Backend {i}\n"
                f"**Título:** Backend — Task {i}\n**Estimativa:** P / 1 week"
                for i in range(1, 9)
            ]
        )
        is_valid, warnings = validate_jira_structure(many_tasks)
        assert is_valid is False
        assert any(
            "backend" in w.lower() and ("2-7" in w or "múltip" in w) for w in warnings
        )

    def test_validate_multiple_frontend_tasks(self):
        """Test detection of 2-7 frontend tasks."""
        # Valid: 4 frontend tasks
        valid_content = """
# Subtarefa Frontend 1
**Título:** Frontend — Component A
**Estimativa:** P / 1.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Component B
**Estimativa:** M / 3 weeks

# Subtarefa Frontend 3
**Título:** Frontend — Component C
**Estimativa:** P / 1 week

# Subtarefa Frontend 4
**Título:** Frontend — Component D
**Estimativa:** M / 2 weeks
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about frontend task count
        frontend_warnings = [w for w in warnings if "frontend" in w.lower() and "task" in w.lower()]
        assert len(frontend_warnings) == 0

        # Invalid: only 1 frontend task
        invalid_content = """
# Subtarefa Frontend
**Título:** Frontend — Single Task
**Estimativa:** G / 8 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        assert is_valid is False
        assert any("frontend" in w.lower() and ("2-7" in w or "múltip" in w) for w in warnings)

    def test_validate_unit_tests_in_tasks(self):
        """Test verification that unit tests are mentioned within implementation tasks."""
        # Valid: tasks mention unit tests
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — API Endpoint
**Descrição:** Implement endpoint with unit tests for validation logic.
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Service Layer
**Descrição:** Create service layer. Unit tests should cover all edge cases.
**Estimativa:** P / 1.5 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Form Component
**Descrição:** Build form component with unit tests using Jest.
**Estimativa:** M / 2.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — State Management
**Descrição:** Implement state with unit tests for reducers.
**Estimativa:** P / 1 week
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have minimal or no warnings about unit tests
        unit_test_warnings = [w for w in warnings if "unit" in w.lower() and "test" in w.lower()]
        assert len(unit_test_warnings) == 0

        # Invalid: no mention of unit tests
        invalid_content = """
# Subtarefa Backend 1
**Título:** Backend — API Endpoint
**Descrição:** Implement endpoint.
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Service Layer
**Descrição:** Create service layer.
**Estimativa:** P / 1.5 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Form Component
**Descrição:** Build form component.
**Estimativa:** M / 2.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — State Management
**Descrição:** Implement state management.
**Estimativa:** P / 1 week
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        # This should generate a warning but might still be valid
        unit_test_warnings = [w for w in warnings if "unit" in w.lower() and "test" in w.lower()]
        assert len(unit_test_warnings) > 0

    def test_validate_e2e_test_tasks_separate(self):
        """Test verification that E2E test tasks are in separate section."""
        # Valid: has dedicated E2E test section
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** M / 1.5 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** M / 1.5 weeks

---

# Testes E2E

## Tarefa E2E 1
**Título:** E2E — Test user flow
**Estimativa:** P / 1 week

## Tarefa E2E 2
**Título:** E2E — Test error scenarios
**Estimativa:** P / 1 week
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about E2E tests
        e2e_warnings = [w for w in warnings if "e2e" in w.lower() or "end-to-end" in w.lower()]
        assert len(e2e_warnings) == 0

        # Invalid: no E2E test section
        invalid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** M / 1.5 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** M / 1.5 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        # This should generate a warning
        e2e_warnings = [w for w in warnings if "e2e" in w.lower() or "end-to-end" in w.lower()]
        assert len(e2e_warnings) > 0

    def test_validate_week_estimates_format(self):
        """Test verification that week estimates are parseable and exact."""
        # Valid: exact week numbers
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** P / 1.5 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 3.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1 week
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about week format
        week_warnings = [
            w
            for w in warnings
            if "week" in w.lower() and ("format" in w.lower() or "exat" in w.lower())
        ]
        assert len(week_warnings) == 0

        # Invalid: vague week estimates
        invalid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2-3 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** P / around 1 week

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1.5 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        # Should generate warnings about format
        week_warnings = [
            w
            for w in warnings
            if "week" in w.lower()
            and ("exact" in w.lower() or "exat" in w.lower() or "format" in w.lower())
        ]
        assert len(week_warnings) > 0

    def test_validate_minimum_half_week(self):
        """Test verification that no task is under 0.5 weeks."""
        # Valid: all tasks >= 0.5 weeks
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** PP / 0.5 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** P / 1 week

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1.5 weeks
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about minimum
        min_warnings = [
            w for w in warnings if "0.5" in w or "mínimo" in w.lower() or "minimum" in w.lower()
        ]
        assert len(min_warnings) == 0

        # Invalid: task under 0.5 weeks
        invalid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** PP / 0.25 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** P / 1 week

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1.5 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        # Should generate warnings
        min_warnings = [
            w for w in warnings if "0.5" in w or "mínimo" in w.lower() or "minimum" in w.lower()
        ]
        assert len(min_warnings) > 0

    def test_validate_dependencies_present(self):
        """Test verification that dependency information is included."""
        # Valid: has dependency information
        valid_content = """
# Subtarefa Backend 1
**Título:** Backend — Database Schema
**Estimativa:** M / 2 weeks
**Dependências:** None

# Subtarefa Backend 2
**Título:** Backend — API Layer
**Estimativa:** M / 2 weeks
**Dependências:** Task 1 (Database Schema)

# Subtarefa Frontend 1
**Título:** Frontend — UI Components
**Estimativa:** M / 2 weeks
**Dependências:** Task 2 (API Layer)

# Subtarefa Frontend 2
**Título:** Frontend — State Management
**Estimativa:** P / 1 week
**Dependências:** None
"""
        is_valid, warnings = validate_jira_structure(valid_content)
        assert is_valid is True
        # Should have no warnings about dependencies
        dep_warnings = [w for w in warnings if "depend" in w.lower()]
        assert len(dep_warnings) == 0

        # Also valid with workflow notation
        valid_workflow = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 1.5 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1 week

**Workflow:** Task 1 → Task 2
"""
        is_valid, warnings = validate_jira_structure(valid_workflow)
        assert is_valid is True

        # Invalid: no dependency information
        invalid_content = """
# Subtarefa Backend 1
**Título:** Backend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Backend 2
**Título:** Backend — Task 2
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 1
**Título:** Frontend — Task 1
**Estimativa:** M / 2 weeks

# Subtarefa Frontend 2
**Título:** Frontend — Task 2
**Estimativa:** P / 1.5 weeks
"""
        is_valid, warnings = validate_jira_structure(invalid_content)
        # Should generate warning about missing dependencies
        dep_warnings = [w for w in warnings if "depend" in w.lower() or "workflow" in w.lower()]
        assert len(dep_warnings) > 0

    def test_validation_returns_warnings_not_errors(self):
        """Test that validation returns warnings and never raises exceptions."""
        # Empty content should not raise exception
        is_valid, warnings = validate_jira_structure("")
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
        assert is_valid is False  # Empty content is invalid
        assert len(warnings) > 0  # Should have warnings

        # Malformed content should not raise exception
        malformed = "Random text with no structure"
        is_valid, warnings = validate_jira_structure(malformed)
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)

        # None should not raise exception (defensive programming)
        is_valid, warnings = validate_jira_structure(None)
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
        assert is_valid is False

        # Very long content should not raise exception
        huge_content = "# Task\n" * 10000
        is_valid, warnings = validate_jira_structure(huge_content)
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
