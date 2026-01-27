"""Tests for CLI flows."""

from unittest.mock import Mock, patch

from refineflow.core.models import Activity, ActivityStatus
from refineflow.core.state import ActivityState
from refineflow.utils.time import get_timestamp


class TestShowActivityStatus:
    """Tests for show_activity_status function."""

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_counts_categorized_questions_correctly(self, mock_storage_class, mock_console):
        """Test that show_activity_status counts total questions across all categories."""
        # Arrange
        slug = "test-activity"
        timestamp = get_timestamp()

        activity = Activity(
            slug=slug,
            title="Test Activity",
            description="Test description",
            status=ActivityStatus.IN_PROGRESS,
            created_at=timestamp,
            updated_at=timestamp,
        )

        # Create state with categorized questions
        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Frontend": ["Question 1", "Question 2"],
                "Backend": ["Question 3"],
                "Arquitetura": [],
                "Produto": ["Question 4", "Question 5", "Question 6"],
                "UX/UI": [],
                "Geral": ["Question 7"],
            },
            action_items=[
                {"action": "Task 1", "owner": "Dev1", "status": "pending"},
                {"action": "Task 2", "owner": "Dev2", "status": "done"},
            ],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_activity.return_value = activity
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Mock console to capture table output
        mock_table = Mock()
        mock_console.print = Mock()

        with patch("refineflow.cli.flows.Table", return_value=mock_table):
            # Act
            from refineflow.cli.flows import show_activity_status

            show_activity_status(slug)

        # Assert - Check that Table.add_row was called with correct question count
        # Expected: 2 + 1 + 0 + 3 + 0 + 1 = 7 total questions
        calls = mock_table.add_row.call_args_list

        # Find the call with "Questões Abertas"
        question_count_call = None
        for call in calls:
            if call[0][0] == "Questões Abertas":
                question_count_call = call
                break

        assert question_count_call is not None, "Should have row for 'Questões Abertas'"
        actual = question_count_call[0][1]
        assert actual == "7", f"Expected '7' questions, got {actual}"

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_handles_empty_questions(self, mock_storage_class, mock_console):
        """Test that show_activity_status correctly handles empty question categories."""
        # Arrange
        slug = "test-activity-2"
        timestamp = get_timestamp()

        activity = Activity(
            slug=slug,
            title="Test Activity 2",
            description="Test description",
            status=ActivityStatus.IN_PROGRESS,
            created_at=timestamp,
            updated_at=timestamp,
        )

        # Create state with all empty question categories
        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Frontend": [],
                "Backend": [],
                "Arquitetura": [],
                "Produto": [],
                "UX/UI": [],
                "Geral": [],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_activity.return_value = activity
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Mock console
        mock_table = Mock()
        mock_console.print = Mock()

        with patch("refineflow.cli.flows.Table", return_value=mock_table):
            # Act
            from refineflow.cli.flows import show_activity_status

            show_activity_status(slug)

        # Assert - Check that question count is 0
        calls = mock_table.add_row.call_args_list

        # Find the call with "Questões Abertas"
        question_count_call = None
        for call in calls:
            if call[0][0] == "Questões Abertas":
                question_count_call = call
                break

        assert question_count_call is not None
        actual = question_count_call[0][1]
        assert actual == "0", f"Expected '0' questions, got {actual}"

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_handles_missing_categories(self, mock_storage_class, mock_console):
        """Test that show_activity_status handles partially populated question dict."""
        # Arrange
        slug = "test-activity-3"
        timestamp = get_timestamp()

        activity = Activity(
            slug=slug,
            title="Test Activity 3",
            description="Test description",
            status=ActivityStatus.IN_PROGRESS,
            created_at=timestamp,
            updated_at=timestamp,
        )

        # Create state with only some question categories
        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Backend": ["Q1", "Q2", "Q3"],
                "Geral": ["Q4"],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_activity.return_value = activity
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Mock console
        mock_table = Mock()
        mock_console.print = Mock()

        with patch("refineflow.cli.flows.Table", return_value=mock_table):
            # Act
            from refineflow.cli.flows import show_activity_status

            show_activity_status(slug)

        # Assert - Check that question count is 4 (3 + 1)
        calls = mock_table.add_row.call_args_list

        # Find the call with "Questões Abertas"
        question_count_call = None
        for call in calls:
            if call[0][0] == "Questões Abertas":
                question_count_call = call
                break

        assert question_count_call is not None
        actual = question_count_call[0][1]
        assert actual == "4", f"Expected '4' questions, got {actual}"


class TestViewQuestionsFlow:
    """Tests for view_questions_flow function."""

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_view_questions_display_all_categories(self, mock_storage_class, mock_console):
        """Test view_questions_flow with multiple categories."""
        # Arrange
        slug = "test-activity"

        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Frontend": [
                    "Como validar CPF no formulário?",
                    "Qual biblioteca de componentes usar?",
                ],
                "Backend": [
                    "Como estruturar a API REST?",
                    "Qual banco de dados usar?",
                    "Como implementar autenticação JWT?",
                ],
                "Arquitetura": ["Como garantir escalabilidade?"],
                "Produto": ["Qual métrica define sucesso?"],
                "UX/UI": [],
                "Geral": [],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Act
        from refineflow.cli.flows import view_questions_flow

        view_questions_flow(slug)

        # Assert
        # Should have been called with a Panel containing the questions
        assert mock_console.print.called
        call_args = mock_console.print.call_args_list

        # Find the Panel object call
        panel_call = None
        for call in call_args:
            if len(call[0]) > 0:
                from rich.panel import Panel

                if isinstance(call[0][0], Panel):
                    panel_call = call[0][0]
                    break

        assert panel_call is not None, "Should have printed a Panel"

        # Verify panel content
        panel_content = str(panel_call.renderable)

        # Verify categories with questions are shown
        assert "Frontend" in panel_content
        assert "Backend" in panel_content
        assert "Arquitetura" in panel_content
        assert "Produto" in panel_content

        # Verify specific questions
        assert "Como validar CPF no formulário?" in panel_content
        assert "Como estruturar a API REST?" in panel_content

        # Verify panel title contains total count
        panel_title = str(panel_call.title)
        assert "7" in panel_title

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_view_questions_empty_categories_hidden(self, mock_storage_class, mock_console):
        """Test that view_questions_flow does not display empty categories."""
        # Arrange
        slug = "test-activity"

        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Frontend": ["Pergunta frontend"],
                "Backend": [],
                "Arquitetura": [],
                "Produto": [],
                "UX/UI": [],
                "Geral": [],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Act
        from refineflow.cli.flows import view_questions_flow

        view_questions_flow(slug)

        # Assert
        call_args = mock_console.print.call_args_list

        # Find the Panel object call
        panel_call = None
        for call in call_args:
            if len(call[0]) > 0:
                from rich.panel import Panel

                if isinstance(call[0][0], Panel):
                    panel_call = call[0][0]
                    break

        assert panel_call is not None, "Should have printed a Panel"
        panel_content = str(panel_call.renderable)

        # Should show Frontend since it has a question
        assert "Frontend" in panel_content
        assert "Pergunta frontend" in panel_content

        # Should NOT show empty categories
        assert "Backend" not in panel_content
        assert "Arquitetura" not in panel_content

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_view_questions_no_questions(self, mock_storage_class, mock_console):
        """Test that view_questions_flow shows friendly message when no questions exist."""
        # Arrange
        slug = "test-activity"

        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Frontend": [],
                "Backend": [],
                "Arquitetura": [],
                "Produto": [],
                "UX/UI": [],
                "Geral": [],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Act
        from refineflow.cli.flows import view_questions_flow

        view_questions_flow(slug)

        # Assert
        printed_output = str(mock_console.print.call_args_list)

        # Should show friendly message
        assert "Nenhuma questão em aberto no momento" in printed_output

    @patch("refineflow.cli.flows.console")
    @patch("refineflow.cli.flows.ActivityStorage")
    def test_view_questions_single_category(self, mock_storage_class, mock_console):
        """Test that view_questions_flow displays correctly with only one category populated."""
        # Arrange
        slug = "test-activity"

        state = ActivityState(
            summary="Test summary",
            open_questions={
                "Geral": ["Questão geral 1", "Questão geral 2", "Questão geral 3"],
            },
            action_items=[],
        )

        # Mock storage
        mock_storage = Mock()
        mock_storage.load_state.return_value = state
        mock_storage_class.return_value = mock_storage

        # Act
        from refineflow.cli.flows import view_questions_flow

        view_questions_flow(slug)

        # Assert
        call_args = mock_console.print.call_args_list

        # Find the Panel object call
        panel_call = None
        for call in call_args:
            if len(call[0]) > 0:
                from rich.panel import Panel

                if isinstance(call[0][0], Panel):
                    panel_call = call[0][0]
                    break

        assert panel_call is not None, "Should have printed a Panel"
        panel_content = str(panel_call.renderable)

        # Should show Geral category
        assert "Geral" in panel_content
        assert "💡" in panel_content  # Geral icon

        # Should show all 3 questions
        assert "Questão geral 1" in panel_content
        assert "Questão geral 2" in panel_content
        assert "Questão geral 3" in panel_content

        # Should show correct count in title
        panel_title = str(panel_call.title)
        assert "3" in panel_title
