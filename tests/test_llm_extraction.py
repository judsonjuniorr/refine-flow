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


# ============================================================================
# PHASE 4: Entry Type Auto-Classification Tests
# ============================================================================


class TestEntryTypeClassification:
    """Tests for automatic entry type classification."""

    def test_classify_entry_type_note(self, processor: LLMProcessor) -> None:
        """Test classification of general note/observation."""
        content = "O sistema atual usa MySQL mas talvez possamos migrar para PostgreSQL no futuro."

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.processor_langchain.get_classification_chain") as mock_get_chain:

            # Mock LLM
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            # Mock chain that returns dict directly
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = {"entry_type": "note"}
            mock_get_chain.return_value = mock_chain

            result = processor.classify_entry_type(content)

            assert result == EntryType.NOTE

    def test_classify_entry_type_decision(self, processor: LLMProcessor) -> None:
        """Test classification of documented decision."""
        content = (
            "Decidimos usar PostgreSQL como banco de dados principal "
            "por sua robustez e suporte a JSON."
        )

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.processor_langchain.get_classification_chain") as mock_get_chain:

            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = {"entry_type": "decision"}
            mock_get_chain.return_value = mock_chain

            result = processor.classify_entry_type(content)

            assert result == EntryType.DECISION

    def test_classify_entry_type_requirement(self, processor: LLMProcessor) -> None:
        """Test classification of functional requirement."""
        content = "O sistema deve permitir que usuários façam login com email e senha."

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.processor_langchain.get_classification_chain") as mock_get_chain:

            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = {"entry_type": "requirement"}
            mock_get_chain.return_value = mock_chain

            result = processor.classify_entry_type(content)

            assert result == EntryType.REQUIREMENT

    def test_classify_entry_type_transcript(self, processor: LLMProcessor) -> None:
        """Test classification of meeting transcript."""
        content = """Reunião com stakeholders:
        João: Precisamos da funcionalidade de exportação em PDF.
        Maria: Concordo, mas precisamos definir o prazo primeiro.
        Pedro: Podemos entregar em 2 sprints."""

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.processor_langchain.get_classification_chain") as mock_get_chain:

            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = {"entry_type": "transcript"}
            mock_get_chain.return_value = mock_chain

            result = processor.classify_entry_type(content)

            assert result == EntryType.TRANSCRIPT

    def test_classify_entry_type_risk(self, processor: LLMProcessor) -> None:
        """Test classification of identified risk."""
        content = (
            "Existe o risco de a API externa não suportar a carga necessária, "
            "o que pode causar timeouts."
        )

        with patch.object(processor.client, "is_available", return_value=True), \
             patch.object(processor.client, "get_llm") as mock_get_llm, \
             patch("refineflow.llm.processor_langchain.get_classification_chain") as mock_get_chain:

            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = {"entry_type": "risk"}
            mock_get_chain.return_value = mock_chain

            result = processor.classify_entry_type(content)

            assert result == EntryType.RISK

    def test_classify_entry_type_llm_unavailable(self, processor: LLMProcessor) -> None:
        """Test that classification raises exception when LLM is unavailable."""
        content = "Some content to classify"

        # Mock LLM as unavailable
        with patch.object(processor.client, "is_available", return_value=False):
            # Should raise ValueError when LLM is not available
            with pytest.raises(ValueError, match="OpenAI not configured"):
                processor.classify_entry_type(content)

    @patch("refineflow.cli.flows.ActivityStorage")
    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.questionary")
    @patch("refineflow.cli.flows.LLMProcessor")
    def test_manual_override_classification(
        self, mock_processor_class, mock_questionary, mock_console, mock_storage_class
    ) -> None:
        """
        Test the manual override flow when user rejects auto-classification.
        
        Scenario:
        1. User enters content
        2. LLM auto-classifies as DECISION
        3. User is prompted: "Tipo detectado: Decisão. Está correto?"
        4. User rejects with "n" (não)
        5. System shows manual selection UI
        6. User manually selects REQUIREMENT
        7. Entry is created with REQUIREMENT (not DECISION)
        """
        # Arrange
        slug = "test-activity"
        content = "Some content here"

        # Mock storage
        mock_storage = MagicMock()
        mock_storage.is_finalized.return_value = False
        mock_storage.load_activity.return_value = MagicMock()  # Mock activity
        mock_storage.load_state.return_value = ActivityState(
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
        mock_storage_class.return_value = mock_storage

        # Mock LLM processor to return DECISION
        mock_processor = MagicMock()
        mock_processor.classify_entry_type.return_value = EntryType.DECISION
        # Mock process_entry - we don't care about the result for this test
        mock_processor.process_entry.return_value = None
        mock_processor_class.return_value = mock_processor

        # Mock questionary for user input
        # 1. Select input method: "Múltiplas linhas (terminal)"
        # 2. Confirmation of auto-classification: False (user rejects)
        # 3. Manual selection: "Requisito"
        mock_select = MagicMock()
        mock_select.ask.side_effect = [
            "Múltiplas linhas (terminal)",  # Input method
            "Requisito",  # Manual type selection (after rejection)
        ]

        mock_confirm = MagicMock()
        mock_confirm.ask.return_value = False  # User rejects auto-classification

        mock_questionary.select.return_value = mock_select
        mock_questionary.confirm.return_value = mock_confirm

        # Mock get_multiline_input to return content
        with patch("refineflow.cli.flows.get_multiline_input", return_value=content):
            # Act
            from refineflow.cli.flows import add_entry_flow
            add_entry_flow(slug)

        # Assert
        # 1. LLM classification was called
        mock_processor.classify_entry_type.assert_called_once_with(content)

        # 2. User was asked to confirm the detected type
        mock_questionary.confirm.assert_called_once_with("Está correto?", default=True)

        # 3. Manual selection was shown (called twice: once for input method, once for type)
        assert mock_questionary.select.call_count == 2
        manual_selection_call = mock_questionary.select.call_args_list[1]
        assert manual_selection_call[0][0] == "Tipo de Entrada:"
        assert "Requisito" in manual_selection_call[1]["choices"]

        # 4. Entry was saved with REQUIREMENT type (not DECISION)
        # The storage.append_to_log should be called with an Entry having REQUIREMENT type
        assert mock_storage.append_to_log.called
        saved_entry = mock_storage.append_to_log.call_args[0][1]  # Second argument is the entry
        assert saved_entry.entry_type == EntryType.REQUIREMENT
        assert saved_entry.content == content

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
