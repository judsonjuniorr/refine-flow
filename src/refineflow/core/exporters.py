"""Exporters for Business Case Canvas and Jira tasks."""

import csv
import json
from io import StringIO

from refineflow.core.state import ActivityState
from refineflow.llm.processor_langchain import LLMProcessor
from refineflow.storage.filesystem import ActivityStorage
from refineflow.storage.templates import CANVAS_TEMPLATE
from refineflow.utils.logger import get_logger
from refineflow.utils.time import get_timestamp

logger = get_logger(__name__)


class CanvasExporter:
    """Business Case Canvas exporter."""

    def __init__(self, storage: ActivityStorage) -> None:
        """Initialize exporter."""
        self.storage = storage

    def generate_canvas(self, slug: str) -> str:
        """
        Generate Business Case Canvas markdown using LangChain.

        Args:
            slug: Activity slug

        Returns:
            Canvas markdown content
        """
        activity = self.storage.load_activity(slug)
        state = self.storage.load_state(slug)

        if not activity or not state:
            return "# Error: Activity or state not found"

        # Use LangChain processor to generate canvas
        processor = LLMProcessor()
        try:
            canvas_md = processor.generate_canvas(activity, state)
            return canvas_md
        except Exception as e:
            logger.error(f"Failed to generate canvas with LangChain: {e}")
            # Fallback to template-based generation
            return self._generate_canvas_fallback(activity, state)

    def _generate_canvas_fallback(self, activity, state) -> str:
        """Fallback canvas generation using templates."""
        canvas_data = state.canvas if state.canvas else {}

        # Extract data
        problem_stmt = canvas_data.get("problem_statement", activity.problem)
        stakeholders_list = activity.stakeholders if activity.stakeholders else []

        # Format lists
        def format_list(items: list[str]) -> str:
            return "\n".join(f"- {item}" for item in items) if items else "- None specified"

        canvas_md = CANVAS_TEMPLATE.format(
            title=activity.title,
            problem_statement=problem_stmt or "_Not specified_",
            problem_owner=", ".join(stakeholders_list) or "_Not specified_",
            problem_importance=canvas_data.get("problem_importance", "_Not specified_"),
            proposed_solution=canvas_data.get(
                "proposed_solution", state.summary or "_Not specified_"
            ),
            solution_relation=canvas_data.get("solution_relation", "_Not specified_"),
            tangible_resources=format_list(canvas_data.get("tangible_resources", [])),
            intangible_resources=format_list(canvas_data.get("intangible_resources", [])),
            internal_dependencies=format_list(
                [d["dependency"] for d in state.dependencies if d.get("type") == "internal"]
            ),
            external_dependencies=format_list(
                [d["dependency"] for d in state.dependencies if d.get("type") == "external"]
            ),
            purpose=canvas_data.get("purpose", "_Not specified_"),
            goals=format_list(canvas_data.get("goals", [])),
            financial_benefits=format_list(canvas_data.get("financial_benefits", [])),
            non_financial_benefits=format_list(canvas_data.get("non_financial_benefits", [])),
            in_scope=format_list(state.functional_requirements + state.non_functional_requirements),
            out_of_scope=format_list(canvas_data.get("out_of_scope", [])),
            timeline=activity.constraints or "_Not specified_",
            resources_available=canvas_data.get("resources_available", "_Not specified_"),
            strategic_relevance=canvas_data.get("strategic_relevance", "_Not specified_"),
            risks=self._format_risks(state.identified_risks),
            stakeholders=self._format_stakeholders(stakeholders_list),
            specification_effort=canvas_data.get("specification_effort", "_Not estimated_"),
            development_effort=canvas_data.get("development_effort", "_Not estimated_"),
            testing_effort=canvas_data.get("testing_effort", "_Not estimated_"),
            materials=format_list(canvas_data.get("materials", [])),
            videos=format_list(canvas_data.get("videos", [])),
            training=format_list(canvas_data.get("training", [])),
            cost_sources=format_list([c["item"] for c in state.costs]),
            budget=canvas_data.get("budget", "_Not estimated_"),
            total_cost_over_time=canvas_data.get("total_cost_over_time", "_Not estimated_"),
            success_metrics=format_list([m["metric"] for m in state.metrics]),
            benefit_metrics=format_list(canvas_data.get("benefit_metrics", [])),
            missing_info=format_list(state.information_gaps),
            suggested_questions=self._generate_questions(state),
        )

        return canvas_md

    def _format_risks(self, risks: list[dict[str, str]]) -> str:
        """Format risks for canvas."""
        if not risks:
            return "- None identified"

        result = []
        for risk in risks:
            result.append(f"**{risk.get('risk', 'Unknown')}**")
            result.append(f"  - Impact: {risk.get('impact', 'Not specified')}")
            result.append(f"  - Mitigation: {risk.get('mitigation', 'Not specified')}")
            result.append("")
        return "\n".join(result)

    def _format_stakeholders(self, stakeholders: list[str]) -> str:
        """Format stakeholders for canvas."""
        if not stakeholders:
            return "- None specified"

        return "\n".join(f"- {s}" for s in stakeholders)

    def _generate_questions(self, state: ActivityState) -> str:
        """Generate suggested questions based on gaps."""
        questions = []

        if not state.functional_requirements:
            questions.append("- What are the key functional requirements?")

        if len(state.identified_risks) < 2:
            questions.append("- What are the main risks and how can they be mitigated?")

        if not state.metrics:
            questions.append("- How will we measure success?")

        if state.information_gaps:
            for gap in state.information_gaps[:3]:
                questions.append(f"- {gap}?")

        return "\n".join(questions) if questions else "- Canvas appears complete!"


class JiraExporter:
    """Jira task exporter."""

    def __init__(self, storage: ActivityStorage) -> None:
        """Initialize exporter."""
        self.storage = storage
        self.processor = LLMProcessor()

    def export_markdown(self, slug: str) -> str:
        """
        Export as Markdown format.

        Args:
            slug: Activity slug

        Returns:
            Markdown content
        """
        activity = self.storage.load_activity(slug)
        state = self.storage.load_state(slug)

        if not activity or not state:
            return "# Error: Activity or state not found"

        # Use LLM to generate if available
        jira_content = self.processor.generate_jira_export(activity, state)

        header = f"""# Jira Export: {activity.title}

**Generated**: {get_timestamp()}
**Status**: {activity.status}

---

"""
        return header + jira_content

    def export_json(self, slug: str) -> str:
        """Export as JSON."""
        activity = self.storage.load_activity(slug)
        state = self.storage.load_state(slug)

        if not activity or not state:
            return json.dumps({"error": "Activity not found"})

        data = {
            "parent": {
                "title": activity.title,
                "description": activity.description,
                "summary": state.summary,
                "requirements": state.functional_requirements + state.non_functional_requirements,
                "risks": state.identified_risks,
            },
            "subtasks": [
                {
                    "title": f"[BE] {activity.title}",
                    "description": "Backend implementation",
                    "type": "backend",
                },
                {
                    "title": f"[FE] {activity.title}",
                    "description": "Frontend implementation",
                    "type": "frontend",
                },
            ],
        }

        return json.dumps(data, indent=2)

    def export_csv(self, slug: str) -> str:
        """Export as CSV."""
        activity = self.storage.load_activity(slug)
        state = self.storage.load_state(slug)

        if not activity or not state:
            return "error,Activity not found"

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Type", "Title", "Description", "Requirements"])
        writer.writerow(
            [
                "Parent",
                activity.title,
                activity.description,
                "; ".join(state.functional_requirements[:3]),
            ]
        )
        writer.writerow(
            [
                "Backend Subtask",
                f"[BE] {activity.title}",
                "Backend implementation",
                "",
            ]
        )
        writer.writerow(
            [
                "Frontend Subtask",
                f"[FE] {activity.title}",
                "Frontend implementation",
                "",
            ]
        )

        return output.getvalue()
