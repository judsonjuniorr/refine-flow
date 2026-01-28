"""End-to-end tests for complete Jira export flow with all optimization features.

This test suite validates the complete flow:
Activity -> LLM -> Validation -> File Output

All tests use mock LLM responses to ensure consistent, predictable output.
"""

from unittest.mock import Mock, patch

import pytest

from refineflow.core.exporters import JiraExporter
from refineflow.core.models import Activity
from refineflow.core.state import ActivityState
from refineflow.storage.filesystem import ActivityStorage

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_activity():
    """Create a realistic test activity."""
    return Activity(
        slug="test-feature",
        title="Test Feature Implementation",
        description="Implement a new feature with backend and frontend components",
        problem="Users need better data visualization capabilities",
        stakeholders=["Product Manager", "Tech Lead", "UX Designer"],
        constraints="Must be completed in 2 months",
        status="in_progress",
        created_at="2026-01-27T00:00:00",
        updated_at="2026-01-27T12:00:00",
    )


@pytest.fixture
def mock_state():
    """Create a realistic test activity state."""
    return ActivityState(
        summary="Feature to enhance data visualization with interactive charts and filters",
        functional_requirements=[
            "Display data in multiple chart types (bar, line, pie)",
            "Allow users to filter data by date range",
            "Export charts as PNG or PDF",
            "Real-time data updates via WebSocket",
        ],
        non_functional_requirements=[
            "Response time < 2 seconds for chart rendering",
            "Support up to 10,000 data points",
            "Mobile-responsive design",
        ],
        identified_risks=[
            {
                "risk": "Large datasets may cause performance issues",
                "impact": "High - affects user experience",
                "mitigation": "Implement pagination and lazy loading",
            },
            {
                "risk": "Browser compatibility issues with chart library",
                "impact": "Medium - some users may have issues",
                "mitigation": "Use well-tested library with broad support",
            },
        ],
        dependencies=[
            {"dependency": "Data API v2", "type": "internal"},
            {"dependency": "Chart.js library", "type": "external"},
        ],
        costs=[
            {"item": "Chart.js Pro license", "amount": "500"},
            {"item": "Additional infrastructure", "amount": "200/month"},
        ],
        metrics=[
            {"metric": "Chart load time < 2s"},
            {"metric": "User satisfaction score > 4.0"},
        ],
        information_gaps=[],
    )


@pytest.fixture
def optimized_jira_response():
    """
    Mock LLM response with ALL optimized features from Phases 1-5:
    - 2-7 granular backend tasks (each mentions unit tests)
    - 2-7 granular frontend tasks (each mentions unit tests)
    - Separate E2E test tasks section
    - Both T-shirt sizes and exact week estimates
    - Dependency and workflow information
    """
    return """# Tarefa Pai
**Título:** Test Feature Implementation

**Descrição (visão geral / contexto):**
Implement a new feature with backend API, frontend UI, and comprehensive testing.
This feature enhances data visualization capabilities for users.

**Critérios de aceitação:**
1. Backend API provides data endpoints
2. Frontend renders interactive charts
3. All components are tested (unit + E2E)
4. Performance meets SLA requirements

**Estimativa T-Shirt:** G (até 3 meses)
**Estimativa:** 10 weeks

---

# Subtarefa Backend 1
**Título:** [BE] API Data Models and Schema Design

**Descrição:**
Design and implement database models and schemas for chart data storage.
**IMPORTANTE:** Esta tarefa inclui testes unitários seguindo TDD.

**Critérios de aceitação:**
- Models defined with SQLAlchemy/ORM
- Migration scripts created
- Unit tests for model validation (TDD approach)
- Schema documented

**Estimativa:** P / 1.5 weeks

**Dependências:** Nenhuma (tarefa inicial)
**Pode executar em paralelo com:** Subtarefa Frontend 1

---

# Subtarefa Backend 2
**Título:** [BE] REST API Endpoints for Chart Data

**Descrição:**
Implement REST endpoints for retrieving and filtering chart data.
Includes comprehensive unit tests for all endpoints following TDD principles.

**Critérios de aceitação:**
- GET /api/charts endpoint implemented
- Query parameters for filtering (date range, type)
- Unit tests for endpoints (request/response validation)
- API documentation (OpenAPI/Swagger)

**Estimativa:** M / 2 weeks

**Dependências:** Subtarefa Backend 1
**Workflow:** Backend 1 → Backend 2

---

# Subtarefa Backend 3
**Título:** [BE] WebSocket Real-time Data Updates

**Descrição:**
Implement WebSocket connection for real-time chart data updates.
Unit tests cover connection handling, message formats, and error scenarios.

**Critérios de aceitação:**
- WebSocket server configured
- Real-time event broadcasting
- Unit tests for WebSocket handlers (TDD)
- Connection error handling

**Estimativa:** M / 2.5 weeks

**Dependências:** Subtarefa Backend 2
**Workflow:** Backend 2 → Backend 3

---

# Subtarefa Backend 4
**Título:** [BE] Data Export Service (PDF/PNG)

**Descrição:**
Service to export charts as PDF or PNG files.
Includes unit tests for export logic, file generation, and format validation.

**Critérios de aceitação:**
- PDF generation using library (e.g., ReportLab)
- PNG generation from chart data
- Unit tests for export functions (TDD approach)
- File size optimization

**Estimativa:** P / 1.5 weeks

**Dependências:** Subtarefa Backend 2
**Pode executar em paralelo com:** Backend 3
**Workflow:** Backend 2 → (Backend 3 || Backend 4)

---

# Subtarefa Frontend 1
**Título:** [FE] Chart Component Library Setup

**Descrição:**
Setup Chart.js library and create reusable chart components.
Component unit tests using Jest/React Testing Library following TDD.

**Critérios de aceitação:**
- Chart.js integrated
- Base chart components created (Bar, Line, Pie)
- Unit tests for components (TDD)
- Storybook documentation

**Estimativa:** P / 1 week

**Dependências:** Nenhuma (tarefa inicial)
**Pode executar em paralelo com:** Subtarefa Backend 1

---

# Subtarefa Frontend 2
**Título:** [FE] Data Filtering UI Controls

**Descrição:**
Implement UI controls for date range and data type filtering.
Unit tests cover component behavior, state management, and user interactions.

**Critérios de aceitação:**
- Date range picker component
- Filter dropdowns for chart types
- Unit tests for filter logic (TDD approach)
- Responsive design

**Estimativa:** M / 2 weeks

**Dependências:** Subtarefa Frontend 1
**Workflow:** Frontend 1 → Frontend 2

---

# Subtarefa Frontend 3
**Título:** [FE] Real-time Data Integration (WebSocket Client)

**Descrição:**
Connect frontend to WebSocket for live chart updates.
Includes unit tests for WebSocket client, reconnection logic, and data synchronization.

**Critérios de aceitação:**
- WebSocket client implemented
- Auto-reconnection on disconnect
- Unit tests for WebSocket integration (TDD)
- Loading states and error handling

**Estimativa:** M / 2.5 weeks

**Dependências:** Subtarefa Frontend 2, Subtarefa Backend 3
**Workflow:** (Frontend 2 + Backend 3) → Frontend 3

---

# Subtarefa Frontend 4
**Título:** [FE] Export Chart Functionality

**Descrição:**
UI for exporting charts as PDF/PNG with download functionality.
Unit tests validate export button, download triggers, and error handling.

**Critérios de aceitação:**
- Export buttons (PDF, PNG)
- Download functionality
- Unit tests for export UI (TDD approach)
- Progress indicators

**Estimativa:** P / 1 week

**Dependências:** Subtarefa Frontend 2, Subtarefa Backend 4
**Pode executar em paralelo com:** Frontend 3
**Workflow:** (Frontend 2 + Backend 4) → Frontend 4

---

# Tarefas de Teste E2E

## Tarefa E2E 1
**Título:** [E2E] Complete User Flow - Chart Visualization

**Descrição:**
End-to-end test covering the complete user journey from login to chart viewing.

**Critérios de aceitação:**
- User can login and access charts page
- Charts load with data
- Filters work correctly
- Performance meets SLA (< 2s load time)

**Estimativa:** P / 1 week

**Dependências:** Todas as subtarefas Backend e Frontend
**Workflow:** (Backend 1-4 + Frontend 1-4) → E2E 1

---

## Tarefa E2E 2
**Título:** [E2E] Real-time Updates and Export

**Descrição:**
End-to-end test for WebSocket real-time updates and export functionality.

**Critérios de aceitação:**
- Real-time data updates work across browser tabs
- Export to PDF generates correct file
- Export to PNG generates correct file
- Downloaded files are valid

**Estimativa:** P / 1 week

**Dependências:** Todas as subtarefas Backend e Frontend
**Workflow:** (Backend 1-4 + Frontend 1-4) → E2E 2

---

## Observabilidade e Métricas
- Logs estruturados para todas as operações
- Traces distribuídos com correlation IDs
- Métricas: response time, error rate, chart renders/min
- Dashboards e alertas configurados

## Riscos e Mitigações
- Performance com grandes datasets: lazy loading e paginação
- Browser compatibility: usar biblioteca testada (Chart.js)
- WebSocket disconnections: auto-reconnect e fallback para polling
"""


@pytest.fixture
def mock_storage(mock_activity, mock_state):
    """Create a mock storage that returns test data."""
    storage = Mock(spec=ActivityStorage)
    storage.load_activity.return_value = mock_activity
    storage.load_state.return_value = mock_state
    return storage


# ============================================================================
# E2E TESTS
# ============================================================================


class TestJiraExportE2E:
    """End-to-end tests for complete Jira export flow."""

    def test_e2e_jira_export_granular_tasks(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Test full flow from activity data to optimized Jira export with granular tasks."""
        # Setup exporter with mock storage
        exporter = JiraExporter(mock_storage)

        # Mock LLM to return optimized response
        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Verify header is present
        assert "# Jira Export: Test Feature Implementation" in result
        assert "**Generated**:" in result
        assert "**Status**: in_progress" in result

        # Verify the optimized content is included
        assert optimized_jira_response in result

        # Verify structure
        assert "# Tarefa Pai" in result
        assert "# Subtarefa Backend" in result
        assert "# Subtarefa Frontend" in result
        assert "# Tarefas de Teste E2E" in result

    def test_e2e_backend_tasks_breakdown(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Verify 2-7 backend tasks are generated in the export."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Count backend tasks (should be 4 in our mock)
        import re

        backend_pattern = r"# Subtarefa Backend \d+"
        backend_matches = re.findall(backend_pattern, result)

        assert len(backend_matches) >= 2, "Should have at least 2 backend tasks"
        assert len(backend_matches) <= 7, "Should have at most 7 backend tasks"
        assert len(backend_matches) == 4, "Mock response should have exactly 4 backend tasks"

    def test_e2e_frontend_tasks_breakdown(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Verify 2-7 frontend tasks are generated in the export."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Count frontend tasks (should be 4 in our mock)
        import re

        frontend_pattern = r"# Subtarefa Frontend \d+"
        frontend_matches = re.findall(frontend_pattern, result)

        assert len(frontend_matches) >= 2, "Should have at least 2 frontend tasks"
        assert len(frontend_matches) <= 7, "Should have at most 7 frontend tasks"
        assert len(frontend_matches) == 4, "Mock response should have exactly 4 frontend tasks"

    def test_e2e_unit_tests_in_implementation_tasks(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Verify unit tests are mentioned within each implementation task."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Check for unit test keywords
        result_lower = result.lower()
        assert "unit test" in result_lower or "tdd" in result_lower
        assert (
            "jest" in result_lower or "pytest" in result_lower or "testing library" in result_lower
        )

        # Verify unit tests are in task descriptions (not just E2E section)
        # Split content to check backend/frontend sections specifically
        backend_section = result.split("# Subtarefa Frontend")[0]
        assert "unit test" in backend_section.lower() or "tdd" in backend_section.lower()

    def test_e2e_e2e_test_tasks_separate(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Verify E2E test tasks are in a separate dedicated section."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Verify dedicated E2E section exists
        assert "# Tarefas de Teste E2E" in result or "E2E" in result

        # Verify E2E tasks are present
        result_lower = result.lower()
        assert "e2e" in result_lower or "end-to-end" in result_lower

        # Count E2E tasks
        import re

        e2e_pattern = r"## Tarefa E2E \d+"
        e2e_matches = re.findall(e2e_pattern, result)
        assert len(e2e_matches) >= 1, "Should have at least 1 E2E test task"

    def test_e2e_week_estimates_valid(self, mock_storage, mock_activity, optimized_jira_response):
        """Verify all tasks have exact week estimates >= 0.5."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        # Extract week estimates
        import re

        week_pattern = r"(\d+(?:\.\d+)?)\s*(?:week|semana)"
        week_matches = re.findall(week_pattern, result.lower())

        assert len(week_matches) > 0, "Should have week estimates"

        # Convert to floats and check minimum
        week_values = [float(w) for w in week_matches]
        assert all(w >= 0.5 for w in week_values), "All estimates should be >= 0.5 weeks"

        # Verify no ranges (e.g., "2-3 weeks")
        assert not re.search(r"\d+-\d+\s*(?:week|semana)", result.lower()), (
            "Should not have range estimates"
        )

    def test_e2e_tshirt_and_weeks_both_present(
        self, mock_storage, mock_activity, optimized_jira_response
    ):
        """Verify both T-shirt sizes and week estimates are present."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        result_lower = result.lower()

        # Check for T-shirt sizes
        tshirt_sizes = ["pp", "p /", "m /", "g /", "gg", "xgg"]
        has_tshirt = any(size in result_lower for size in tshirt_sizes)
        assert has_tshirt, "Should have T-shirt size estimates"

        # Check for week estimates
        import re

        week_pattern = r"\d+(?:\.\d+)?\s*(?:week|semana)"
        has_weeks = re.search(week_pattern, result_lower) is not None
        assert has_weeks, "Should have week estimates"

        # Verify format "P / 1.5 weeks" or similar
        combined_pattern = r"(pp|p|m|g|gg|xgg)\s*/\s*\d+(?:\.\d+)?\s*(?:week|semana)"
        has_combined = re.search(combined_pattern, result_lower) is not None
        assert has_combined, "Should have combined format like 'P / 1.5 weeks'"

    def test_e2e_dependencies_included(self, mock_storage, mock_activity, optimized_jira_response):
        """Verify workflow and dependency information is present."""
        exporter = JiraExporter(mock_storage)

        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            result = exporter.export_markdown(mock_activity.slug)

        result_lower = result.lower()

        # Check for dependency keywords
        dependency_keywords = [
            "dependência",
            "dependências",
            "dependency",
            "dependencies",
            "depends on",
            "workflow",
            "→",
            "||",
        ]

        has_dependencies = any(
            keyword in result_lower or keyword in result for keyword in dependency_keywords
        )
        assert has_dependencies, "Should include dependency/workflow information"

        # Verify specific dependency mentions
        assert "workflow:" in result_lower or "dependências:" in result_lower

    def test_e2e_output_file_created(
        self, mock_storage, mock_activity, mock_state, optimized_jira_response
    ):
        """Verify jira export content is generated correctly.

        File writing is CLI responsibility.
        """
        # Setup exporter
        exporter = JiraExporter(mock_storage)

        # Mock LLM
        with patch.object(
            exporter.processor, "generate_jira_export", return_value=optimized_jira_response
        ):
            # Generate export content
            result = exporter.export_markdown(mock_activity.slug)

        # Verify generated content structure
        assert "# Jira Export: Test Feature Implementation" in result
        assert "# Tarefa Pai" in result
        assert "# Subtarefa Backend" in result
        assert "# Subtarefa Frontend" in result
        assert "# Tarefas de Teste E2E" in result

        # Verify it's valid markdown
        assert result.startswith("#"), "Should be valid markdown starting with header"
        assert len(result) > 500, "Should have substantial content"

        # Verify all key sections present
        assert "**Generated**:" in result
        assert "**Status**:" in result
        assert "**Estimativa" in result or "**Estimative" in result
