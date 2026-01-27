"""Tests for Jira prompt template structure and task breakdown instructions."""


from refineflow.llm.langchain_prompts import JIRA_TEMPLATE


class TestJiraPromptStructure:
    """Tests for Phase 1: Jira prompt template task breakdown."""

    def test_jira_prompt_structure(self) -> None:
        """Verify prompt includes instructions for task breakdown."""
        # Get the system message from the JIRA_TEMPLATE
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify instructions for breaking tasks into smaller deliverables
        assert "2-7" in system_message.lower() or "2 a 7" in system_message.lower(), (
            "Prompt should specify 2-7 tasks per area"
        )

        # Verify it mentions breaking down by complexity
        assert "complexidade" in system_message.lower() or "complexity" in system_message.lower(), (
            "Prompt should mention breaking down based on complexity"
        )

        # Verify it mentions both backend and frontend breakdown
        assert "backend" in system_message.lower(), "Prompt should mention backend task breakdown"
        assert "frontend" in system_message.lower(), "Prompt should mention frontend task breakdown"

    def test_jira_prompt_includes_e2e_test_tasks(self) -> None:
        """Verify prompt requests E2E test tasks (separate from implementation tasks)."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify it mentions E2E tests as separate tasks
        assert (
            "e2e" in system_message.lower()
            or "end-to-end" in system_message.lower()
            or "ponta a ponta" in system_message.lower()
        ), "Prompt should mention E2E tests"

        # Verify E2E tests are mentioned as separate/standalone tasks
        assert (
            (
                "separa" in system_message.lower()
                and ("teste" in system_message.lower() or "task" in system_message.lower())
            )
            or ("standalone" in system_message.lower())
            or ("independente" in system_message.lower())
        ), "Prompt should indicate E2E test tasks are separate/standalone"

    def test_jira_prompt_includes_unit_tests_in_tasks(self) -> None:
        """Verify prompt requests unit tests within each implementation task."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify it mentions unit tests within implementation tasks
        assert ("unit" in system_message.lower() and "test" in system_message.lower()) or (
            "teste" in system_message.lower() and "unitário" in system_message.lower()
        ), "Prompt should mention unit tests"

        # Verify TDD is mentioned (write test first, then code)
        assert "tdd" in system_message.lower() or (
            "test" in system_message.lower()
            and (
                "first" in system_message.lower()
                or "antes" in system_message.lower()
                or "primeiro" in system_message.lower()
            )
        ), "Prompt should mention TDD principles (test-first approach)"

        # Verify unit tests should be INCLUDED in implementation tasks
        assert (
            "incluir" in system_message.lower()
            or "include" in system_message.lower()
            or "deve conter" in system_message.lower()
            or "must include" in system_message.lower()
        ) and ("test" in system_message.lower() or "teste" in system_message.lower()), (
            "Prompt should indicate unit tests are included in implementation tasks"
        )

    def test_jira_prompt_allows_flexibility(self) -> None:
        """Verify prompt allows 2-7 tasks per area based on complexity."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify the range is specified (2-7 or 2 a 7)
        assert (
            "2-7" in system_message
            or "2 a 7" in system_message
            or ("2" in system_message and "7" in system_message)
        ), "Prompt should specify task range of 2-7"

        # Verify it allows flexibility based on complexity/size
        assert any(
            word in system_message.lower()
            for word in [
                "baseado",
                "based",
                "depende",
                "depend",
                "complexity",
                "complexidade",
                "tamanho",
                "size",
            ]
        ), "Prompt should allow flexibility based on complexity or size"
