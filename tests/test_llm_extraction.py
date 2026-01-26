"""Tests for LLM extraction with question categorization."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from refineflow.core.models import Activity, Entry, EntryType
from refineflow.core.state import ActivityState
from refineflow.llm.processor_langchain import LLMProcessor
from refineflow.utils.time import get_timestamp


@pytest.fixture
def sample_activity() -> Activity:
    """Create a sample activity for testing."""
    return Activity(
        slug="test-activity",
        title="Implementação de Login",
        description="Implementar sistema de autenticação de usuários",
        created_at=get_timestamp(),
        updated_at=get_timestamp(),
    )


@pytest.fixture
def empty_state() -> ActivityState:
    """Create an empty state for testing."""
    return ActivityState(
        summary="",
        action_items=[],
        open_questions={},
        decisions=[],
        functional_requirements=[],
        non_functional_requirements=[],
        identified_risks=[],
        dependencies=[],
        metrics=[],
        costs=[],
        information_gaps=[],
        last_updated=get_timestamp(),
    )


@pytest.fixture
def processor() -> LLMProcessor:
    """Create an LLM processor for testing."""
    return LLMProcessor()


def create_mock_llm_response(processor, json_response: str):
    """Helper context manager to mock LLM responses for testing."""
    from contextlib import contextmanager

    @contextmanager
    def _mock():
        ai_message = AIMessage(content=json_response)
        ai_message.response_metadata = {}

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.langchain_prompts.EXTRACTION_TEMPLATE") as mock_template:

            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            mock_prompt = MagicMock()
            mock_template.partial.return_value = mock_prompt

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = ai_message

            mock_prompt.__or__.return_value = mock_chain

            yield

    return _mock()


def mock_llm_chain_invoke(json_response: str):
    """Helper to create a mock chain that returns proper AIMessage."""
    def side_effect(*args, **kwargs):
        msg = AIMessage(content=json_response)
        # Ensure content is accessible
        msg.content = json_response
        msg.response_metadata = {}
        return msg
    return side_effect


class TestQuestionCategorization:
    """Test suite for question categorization in LLM extraction."""

    def test_categorize_frontend_question(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a UI-related question is categorized under Frontend."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Precisamos validar o CPF no formulário de cadastro. Qual biblioteca usar?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with Frontend categorization
        json_response = """{
            "summary": "Discussão sobre validação de CPF no formulário",
            "action_items": [],
            "open_questions": {
                "Frontend": ["Qual biblioteca usar para validar CPF no formulário de cadastro?"]
            },
            "decisions": [],
            "functional_requirements": ["Validar CPF no formulário de cadastro"],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "Frontend" in result.open_questions
        assert any(
            "CPF" in q and "formulário" in q for q in result.open_questions.get("Frontend", [])
        )

    def test_categorize_backend_question(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that an API-related question is categorized under Backend."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Qual é o endpoint da API de autenticação? Usamos JWT ou sessões?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with Backend categorization
        json_response = """{
            "summary": "Discussão sobre API de autenticação",
            "action_items": [],
            "open_questions": {
                "Backend": [
                    "Qual é o endpoint da API de autenticação?",
                    "Usamos JWT ou sessões para autenticação?"
                ]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "Backend" in result.open_questions
        assert len(result.open_questions["Backend"]) >= 1
        assert any("autenticação" in q for q in result.open_questions["Backend"])

    def test_categorize_multi_category_question(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a question relevant to both Frontend and Backend appears in both categories."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Como validar o token JWT? Precisamos validar no frontend e backend?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with multi-category question
        json_response = """{
            "summary": "Discussão sobre validação de JWT",
            "action_items": [],
            "open_questions": {
                "Frontend": ["Como validar o token JWT no frontend?"],
                "Backend": ["Como validar o token JWT no backend?"]
            },
            "decisions": [],
            "functional_requirements": ["Validar token JWT no frontend e backend"],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "Frontend" in result.open_questions
        assert "Backend" in result.open_questions
        assert any("JWT" in q for q in result.open_questions["Frontend"])
        assert any("JWT" in q for q in result.open_questions["Backend"])

    def test_categorize_geral_fallback(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a general question is categorized under Geral."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Qual é o prazo final do projeto? Temos budget aprovado?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with Geral categorization
        json_response = """{
            "summary": "Discussão sobre prazo e orçamento",
            "action_items": [],
            "open_questions": {
                "Geral": [
                    "Qual é o prazo final do projeto?",
                    "Temos budget aprovado?"
                ]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "Geral" in result.open_questions
        assert len(result.open_questions["Geral"]) >= 1
        assert any("prazo" in q or "budget" in q for q in result.open_questions["Geral"])

    def test_categorize_produto_question(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a product-related question is categorized under Produto."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content=(
                "Qual métrica define sucesso desta feature? "
                "Quantos usuários esperamos atingir?"
            ),
            timestamp=get_timestamp(),
        )

        # Mock LLM response with Produto categorization
        json_response = """{
            "summary": "Discussão sobre métricas de produto",
            "action_items": [],
            "open_questions": {
                "Produto": [
                    "Qual métrica define sucesso desta feature?",
                    "Quantos usuários esperamos atingir?"
                ]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "Produto" in result.open_questions
        assert len(result.open_questions["Produto"]) >= 1
        assert any("métrica" in q or "usuários" in q for q in result.open_questions["Produto"])

    def test_categorize_uxui_question(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a UX/UI-related question is categorized under UX/UI."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content="O fluxo de checkout deve ter quantas etapas? Precisamos de protótipo?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with UX/UI categorization
        json_response = """{
            "summary": "Discussão sobre fluxo de checkout",
            "action_items": [],
            "open_questions": {
                "UX/UI": [
                    "O fluxo de checkout deve ter quantas etapas?",
                    "Precisamos de protótipo para o fluxo?"
                ]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        assert "UX/UI" in result.open_questions
        assert len(result.open_questions["UX/UI"]) >= 1
        assert any("checkout" in q or "protótipo" in q for q in result.open_questions["UX/UI"])

    def test_categorize_three_plus_categories(
        self, processor: LLMProcessor, sample_activity: Activity, empty_state: ActivityState
    ) -> None:
        """Test that a complex question appears in 3+ categories."""
        # Arrange
        entry = Entry(
            entry_type=EntryType.NOTE,
            content=(
                "Como implementar autenticação OAuth no frontend com validação no backend "
                "garantindo escalabilidade da infraestrutura?"
            ),
            timestamp=get_timestamp(),
        )

        # Mock LLM response with multi-category question (Frontend, Backend, Arquitetura)
        json_response = """{
            "summary": "Discussão sobre implementação de OAuth",
            "action_items": [],
            "open_questions": {
                "Frontend": ["Como implementar autenticação OAuth no frontend?"],
                "Backend": ["Como validar OAuth no backend?"],
                "Arquitetura": ["Como garantir escalabilidade da infraestrutura de autenticação?"]
            },
            "decisions": [],
            "functional_requirements": ["Implementar autenticação OAuth"],
            "non_functional_requirements": ["Infraestrutura escalável"],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, empty_state)

        # Assert
        assert result is not None
        # Should appear in at least 3 categories
        categories_with_questions = [cat for cat, qs in result.open_questions.items() if qs]
        assert len(categories_with_questions) >= 3
        assert "Frontend" in result.open_questions
        assert "Backend" in result.open_questions
        assert "Arquitetura" in result.open_questions
        assert any("OAuth" in q for q in result.open_questions["Frontend"])
        assert any("OAuth" in q for q in result.open_questions["Backend"])
        assert any(
            "escalabilidade" in q or "infraestrutura" in q
            for q in result.open_questions["Arquitetura"]
        )

    def test_preserve_existing_questions(
        self, processor: LLMProcessor, sample_activity: Activity
    ) -> None:
        """
        Test that new questions are correctly extracted.

        Note: Merging happens at CLI level, not in processor.
        """
        # Arrange
        existing_state = ActivityState(
            summary="Estado existente",
            action_items=[],
            open_questions={
                "Frontend": ["Questão frontend existente"],
                "Backend": ["Questão backend existente"],
            },
            decisions=[],
            functional_requirements=[],
            non_functional_requirements=[],
            identified_risks=[],
            dependencies=[],
            metrics=[],
            costs=[],
            information_gaps=[],
            last_updated=get_timestamp(),
        )

        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Precisamos definir a arquitetura do sistema. Microserviços ou monolito?",
            timestamp=get_timestamp(),
        )

        # Mock LLM response with Arquitetura categorization
        json_response = """{
            "summary": "Discussão sobre arquitetura do sistema",
            "action_items": [],
            "open_questions": {
                "Arquitetura": ["Microserviços ou monolito?"]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, existing_state)

        # Assert
        assert result is not None
        # The processor returns new state from LLM extraction
        # State merging happens at a higher level (CLI/flows)
        assert "Arquitetura" in result.open_questions
        assert any(
            "Microserviços" in q or "monolito" in q
            for q in result.open_questions["Arquitetura"]
        )


class TestStateMerging:
    """Test suite for state merging functionality."""

    def test_merge_preserves_existing_categorized_questions(
        self, processor: LLMProcessor, sample_activity: Activity
    ) -> None:
        """Integration test: Verify that processor merges new questions with existing ones."""
        # Arrange - existing state with questions in Frontend and Backend
        existing_state = ActivityState(
            summary="Estado inicial",
            action_items=[],
            open_questions={
                "Frontend": ["Questão frontend existente 1"],
                "Backend": ["Questão backend existente 1", "Questão backend existente 2"],
            },
            decisions=[],
            functional_requirements=["Requisito existente"],
            non_functional_requirements=[],
            identified_risks=[],
            dependencies=[],
            metrics=[],
            costs=[],
            information_gaps=[],
            last_updated=get_timestamp(),
        )

        # New entry that adds more questions to Frontend and a new Arquitetura category
        entry = Entry(
            entry_type=EntryType.NOTE,
            content=(
                "Precisamos validar inputs no frontend e definir a arquitetura "
                "de microserviços."
            ),
            timestamp=get_timestamp(),
        )

        # Mock LLM response with new questions
        json_response = """{
            "summary": "Discussão sobre validação e arquitetura",
            "action_items": [],
            "open_questions": {
                "Frontend": ["Como validar inputs complexos?"],
                "Arquitetura": ["Quantos microserviços teremos?"]
            },
            "decisions": [],
            "functional_requirements": ["Validação de inputs"],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, existing_state)

        # Assert - merged state should contain all questions
        assert result is not None

        # Frontend should have both old and new questions
        assert "Frontend" in result.open_questions
        assert len(result.open_questions["Frontend"]) == 2
        assert "Questão frontend existente 1" in result.open_questions["Frontend"]
        assert any("validar inputs" in q for q in result.open_questions["Frontend"])

        # Backend should still have old questions (unchanged)
        assert "Backend" in result.open_questions
        assert len(result.open_questions["Backend"]) == 2
        assert "Questão backend existente 1" in result.open_questions["Backend"]
        assert "Questão backend existente 2" in result.open_questions["Backend"]

        # Arquitetura is new category
        assert "Arquitetura" in result.open_questions
        assert len(result.open_questions["Arquitetura"]) == 1
        assert any("microserviços" in q for q in result.open_questions["Arquitetura"])

        # Functional requirements should be merged
        assert len(result.functional_requirements) == 2
        assert "Requisito existente" in result.functional_requirements
        assert "Validação de inputs" in result.functional_requirements

    def test_merge_deduplicates_questions(
        self, processor: LLMProcessor, sample_activity: Activity
    ) -> None:
        """Test that merging deduplicates identical questions."""
        # Arrange - state with existing question
        existing_state = ActivityState(
            summary="Estado com questão duplicada",
            action_items=[],
            open_questions={
                "Frontend": ["Qual biblioteca de validação usar?"],
            },
            decisions=[],
            functional_requirements=[],
            non_functional_requirements=[],
            identified_risks=[],
            dependencies=[],
            metrics=[],
            costs=[],
            information_gaps=[],
            last_updated=get_timestamp(),
        )

        entry = Entry(
            entry_type=EntryType.NOTE,
            content="Qual biblioteca de validação usar no frontend?",
            timestamp=get_timestamp(),
        )

        # LLM extracts the same question again
        json_response = """{
            "summary": "Discussão sobre validação",
            "action_items": [],
            "open_questions": {
                "Frontend": ["Qual biblioteca de validação usar?"]
            },
            "decisions": [],
            "functional_requirements": [],
            "non_functional_requirements": [],
            "identified_risks": [],
            "dependencies": [],
            "metrics": [],
            "cost_estimates": [],
            "information_gaps": []
        }"""

        # Act
        with create_mock_llm_response(processor, json_response):
            result = processor.process_entry(sample_activity, entry, existing_state)

        # Assert - should not duplicate the question
        assert result is not None
        assert "Frontend" in result.open_questions
        assert len(result.open_questions["Frontend"]) == 1
        assert result.open_questions["Frontend"][0] == "Qual biblioteca de validação usar?"
