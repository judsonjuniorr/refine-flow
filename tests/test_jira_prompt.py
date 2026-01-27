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


class TestJiraPromptWeekEstimations:
    """Tests for Phase 2: Week estimations with T-shirt sizing backward compatibility."""

    def test_tshirt_to_weeks_conversion(self) -> None:
        """Verify conversion dictionary maps T-shirt sizes to weeks correctly."""
        from refineflow.llm.langchain_prompts import TSHIRT_TO_WEEKS

        # Verify the constant exists and has expected mappings
        assert TSHIRT_TO_WEEKS is not None, "TSHIRT_TO_WEEKS constant should exist"

        # Verify all expected T-shirt sizes are present
        expected_sizes = ["PP", "P", "M", "G", "GG", "XGG"]
        for size in expected_sizes:
            assert size in TSHIRT_TO_WEEKS, f"T-shirt size {size} should be in TSHIRT_TO_WEEKS"

        # Verify the conversion values match specification
        assert TSHIRT_TO_WEEKS["PP"] == 1, "PP should map to 1 week"
        assert TSHIRT_TO_WEEKS["P"] == 2, "P should map to 2 weeks"
        assert TSHIRT_TO_WEEKS["M"] == 4, "M should map to 4 weeks"
        assert TSHIRT_TO_WEEKS["G"] == 8, "G should map to 8 weeks"
        assert TSHIRT_TO_WEEKS["GG"] == 12, "GG should map to 12 weeks"
        assert TSHIRT_TO_WEEKS["XGG"] == 20, "XGG should map to 20 weeks"

    def test_estimation_guidelines_in_prompt(self) -> None:
        """Verify prompt includes week estimation rules."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify prompt mentions week-based estimations
        assert "week" in system_message.lower() or "semana" in system_message.lower(), (
            "Prompt should mention week-based estimations"
        )

        # Verify prompt requests both T-shirt AND week estimates
        assert ("t-shirt" in system_message.lower() or "tamanho" in system_message.lower()) and (
            "week" in system_message.lower() or "semana" in system_message.lower()
        ), "Prompt should request both T-shirt size and week estimates"

    def test_minimum_half_week_mentioned(self) -> None:
        """Verify 0.5 week minimum is specified in the prompt."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify minimum of 0.5 weeks is mentioned
        assert (
            "0.5" in system_message or "0,5" in system_message or "half" in system_message.lower()
        ), "Prompt should specify 0.5 week minimum"

        # Verify it's mentioned in the context of minimum estimate
        assert (
            "m" in system_message.lower()  # minimum, mínimo
            and ("week" in system_message.lower() or "semana" in system_message.lower())
        ), "Prompt should mention minimum week estimate"

    def test_exact_number_format_requested(self) -> None:
        """Verify prompt asks for exact numbers not ranges for week estimates."""
        messages = JIRA_TEMPLATE.messages
        system_message = messages[0].prompt.template

        # Verify prompt requests exact numbers
        assert any(
            word in system_message.lower()
            for word in ["exact", "exato", "specific", "específico", "número"]
        ), "Prompt should request exact numbers for estimates"

        # Verify examples show the expected format (e.g., "M / 3.5 weeks")
        # Look for examples with both T-shirt and week format
        assert (
            "/" in system_message  # separator between T-shirt and weeks
            and ("week" in system_message.lower() or "semana" in system_message.lower())
        ), "Prompt should include examples with T-shirt / week format"
