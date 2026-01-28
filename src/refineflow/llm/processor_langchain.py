"""LLM processing logic with LangChain."""

import json
import re

from refineflow.core.models import Activity, Entry, EntryType
from refineflow.core.state import ActivityState
from refineflow.llm.client_langchain import OpenAIClient
from refineflow.llm.langchain_prompts import (
    StateUpdate,
    get_canvas_chain,
    get_chat_chain,
    get_classification_chain,
    get_extraction_chain,
    get_jira_chain,
)
from refineflow.utils.logger import get_logger
from refineflow.utils.time import get_timestamp

logger = get_logger(__name__)


class LLMProcessor:
    """Processes LLM tasks for activity refinement using LangChain."""

    def __init__(self) -> None:
        """Initialize processor."""
        self.client = OpenAIClient()

    def process_entry(
        self, activity: Activity, entry: Entry, current_state: ActivityState
    ) -> ActivityState | None:
        """
        Process a new entry and update state using LangChain.

        Args:
            activity: Current activity
            entry: New entry
            current_state: Current state

        Returns:
            Updated state or None if processing fails
        """
        if not self.client.is_available():
            logger.warning("OpenAI not available, skipping state extraction")
            return None

        try:
            # Obter LLM configurado para extração
            llm = self.client.get_llm(task_type="extraction")
            if not llm:
                return None

            # Criar chain com parser
            chain = get_extraction_chain(llm)

            # Preparar inputs
            inputs = {
                "activity_title": activity.title,
                "activity_description": activity.description,
                "entry_type": entry.entry_type,
                "entry_content": entry.content,
                "current_summary": current_state.summary or "Ainda sem resumo",
            }

            logger.debug(f"Extraction inputs prepared: {len(str(inputs))} chars")
            logger.debug(f"Entry content preview: {entry.content[:200]}...")

            # Invocar chain - primeiro pegar a resposta do LLM antes do parser
            # Para debug, vamos separar LLM e parser
            from langchain_core.output_parsers.json import JsonOutputParser

            parser = JsonOutputParser(pydantic_object=StateUpdate)
            from refineflow.llm.langchain_prompts import EXTRACTION_TEMPLATE

            prompt = EXTRACTION_TEMPLATE.partial(
                format_instructions=parser.get_format_instructions()
            )

            # Invocar apenas LLM primeiro para ver a resposta raw
            llm_chain = prompt | llm
            raw_response = llm_chain.invoke(inputs)

            logger.debug(f"Raw LLM response type: {type(raw_response)}")
            logger.debug(f"Raw LLM response content: {raw_response.content[:500]}...")

            # Verificar se a resposta está vazia
            if not raw_response.content or len(raw_response.content.strip()) == 0:
                logger.error("Empty response from LLM for extraction")
                logger.error(f"Response metadata: {raw_response.response_metadata}")
                return None

            # Agora tentar parsear
            try:
                result = parser.parse(raw_response.content)
            except Exception as parse_error:
                logger.error(f"Failed to parse LLM response: {parse_error}")
                logger.error(f"Response content was: {raw_response.content[:1000]}")
                return None

            # Mapear cost_estimates para costs (nome diferente entre modelos)
            if "cost_estimates" in result:
                result["costs"] = result.pop("cost_estimates")

            # Atualizar estado
            try:
                updated_state = ActivityState(**result)
                updated_state.last_updated = get_timestamp()

                # Merge with existing state to preserve previous entries
                merged_state = current_state.merge_with(updated_state)
            except Exception as validation_error:
                logger.error(f"Failed to create ActivityState: {validation_error}")
                logger.error(f"Result data: {result}")
                return None

            logger.info("Successfully extracted and updated activity state via LangChain")
            return merged_state

        except Exception as e:
            logger.error(f"Failed to process entry with LangChain: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return None

    def answer_question(
        self, activity: Activity, state: ActivityState, log_content: str, question: str
    ) -> str:
        """
        Answer a question about the activity using LangChain.

        Args:
            activity: Current activity
            state: Current state
            log_content: Recent log content
            question: User question

        Returns:
            Answer text
        """
        if not self.client.is_available():
            return "OpenAI não está configurado. Não é possível responder perguntas."

        try:
            # Obter LLM configurado para chat
            llm = self.client.get_llm(task_type="chat")
            if not llm:
                return "Erro ao configurar LLM para chat."

            # Criar chain
            chain = get_chat_chain(llm)

            # Preparar inputs
            inputs = {
                "activity_title": activity.title,
                "activity_description": activity.description,
                "summary": state.summary or "Resumo não disponível",
                "log_content": log_content[:2000],  # Limitar tamanho
                "question": question,
            }

            logger.debug(f"Chat inputs prepared: {list(inputs.keys())}")
            logger.debug(f"Question: {question}")

            # Invocar chain
            answer = chain.invoke(inputs)

            logger.debug(f"Raw answer type: {type(answer)}")
            logger.debug(f"Raw answer: {repr(answer)[:200]}")
            logger.info(f"Generated answer via LangChain: {len(answer)} chars")

            if not answer or len(answer.strip()) == 0:
                logger.warning("Empty answer received from LangChain chat chain")
                return "Não foi possível gerar uma resposta. Por favor, tente novamente."

            return answer

        except Exception as e:
            logger.error(f"Failed to answer question with LangChain: {e}", exc_info=True)
            return f"Erro ao processar pergunta: {e}"

        except Exception as e:
            logger.error(f"Failed to answer question with LangChain: {e}")
            return f"Erro ao processar pergunta: {str(e)}"

    def generate_jira_export(self, activity: Activity, state: ActivityState) -> str:
        """
        Generate Jira export content using LangChain.

        Args:
            activity: Current activity
            state: Current state

        Returns:
            Jira export markdown
        """
        if not self.client.is_available():
            return self._generate_jira_fallback(activity, state)

        try:
            # Obter LLM configurado para Jira
            llm = self.client.get_llm(task_type="jira")
            if not llm:
                return self._generate_jira_fallback(activity, state)

            # Criar chain
            chain = get_jira_chain(llm)

            # Preparar inputs
            func_reqs = (
                ", ".join(state.functional_requirements)
                if state.functional_requirements
                else "Nenhum especificado"
            )
            non_func_reqs = (
                ", ".join(state.non_functional_requirements)
                if state.non_functional_requirements
                else "Nenhum especificado"
            )
            inputs = {
                "activity_title": activity.title,
                "activity_description": activity.description,
                "summary": state.summary,
                "functional_requirements": func_reqs,
                "non_functional_requirements": non_func_reqs,
                "risks_count": len(state.identified_risks),
                "dependencies_count": len(state.dependencies),
            }

            # Invocar chain
            jira_content = chain.invoke(inputs)

            logger.info(f"Generated Jira export via LangChain: {len(jira_content)} chars")
            return jira_content

        except Exception as e:
            logger.error(f"Failed to generate Jira export with LangChain: {e}")
            return self._generate_jira_fallback(activity, state)

    def generate_canvas(self, activity: Activity, state: ActivityState) -> str:
        """
        Generate Business Case Canvas using LangChain.

        Args:
            activity: Current activity
            state: Current state

        Returns:
            Canvas markdown
        """
        if not self.client.is_available():
            return "OpenAI não está configurado. Não é possível gerar canvas."

        try:
            # Obter LLM configurado para canvas
            llm = self.client.get_llm(task_type="canvas")
            if not llm:
                return "Erro ao configurar LLM para canvas."

            # Criar chain
            chain = get_canvas_chain(llm)

            # Preparar inputs
            inputs = {
                "activity_title": activity.title,
                "activity_description": activity.description,
                "summary": state.summary,
                "requirements_count": len(state.functional_requirements)
                + len(state.non_functional_requirements),
                "risks_count": len(state.identified_risks),
                "dependencies_count": len(state.dependencies),
                "stakeholders_count": len(activity.stakeholders),
                "decisions_count": len(state.decisions),
                "state_json": json.dumps(state.model_dump(), indent=2, ensure_ascii=False),
            }

            # Invocar chain
            canvas_content = chain.invoke(inputs)

            logger.info(f"Generated canvas via LangChain: {len(canvas_content)} chars")
            return canvas_content

        except Exception as e:
            logger.error(f"Failed to generate canvas with LangChain: {e}")
            return f"Erro ao gerar canvas: {str(e)}"

    def _generate_jira_fallback(self, activity: Activity, state: ActivityState) -> str:
        """Generate basic Jira export without AI."""
        return f"""## Tarefa Pai: {activity.title}

**Descrição**: {activity.description}

{state.summary}

**Critérios de Aceitação**:
- Todos os requisitos funcionais atendidos
- Todos os testes passando

## Subtarefa Backend

**Título**: [BE] {activity.title}

**Descrição**: Implementar componentes de backend

## Subtarefa Frontend

**Título**: [FE] {activity.title}

**Descrição**: Implementar componentes de frontend
"""

    def classify_entry_type(self, content: str) -> EntryType:
        """
        Classify the entry type based on content using AI.

        Args:
            content: Entry content to classify

        Returns:
            Detected EntryType

        Raises:
            ValueError: If classification fails or LLM is unavailable
        """
        if not self.client.is_available():
            logger.warning("OpenAI not available, cannot classify entry type")
            raise ValueError("OpenAI not configured")

        try:
            # Get LLM configured for extraction/classification
            llm = self.client.get_llm(task_type="extraction")
            if not llm:
                raise ValueError("Failed to get LLM instance")

            # Create classification chain
            chain = get_classification_chain(llm)

            # Invoke chain
            inputs = {"content": content}
            result = chain.invoke(inputs)

            logger.debug(f"Classification result: {result}")

            # Extract entry_type from result
            entry_type_str = result.get("entry_type", "note")

            # Convert to EntryType enum
            try:
                entry_type = EntryType(entry_type_str)
                logger.info(f"Classified entry as: {entry_type.value}")
                return entry_type
            except ValueError:
                logger.warning(f"Invalid entry type '{entry_type_str}', defaulting to NOTE")
                return EntryType.NOTE

        except Exception as e:
            logger.error(f"Failed to classify entry type: {e}", exc_info=True)
            raise ValueError(f"Classification failed: {e}")


def validate_jira_structure(jira_content: str) -> tuple[bool, list[str]]:
    """
    Validate Jira export structure meets quality requirements.

    Checks for:
    - 2-7 backend implementation tasks
    - 2-7 frontend implementation tasks
    - Unit tests mentioned within implementation tasks
    - Separate E2E test tasks section
    - Week estimates in exact number format
    - Minimum 0.5 weeks per task
    - Dependency/workflow information present

    Args:
        jira_content: Generated Jira export markdown content

    Returns:
        Tuple of (is_valid, warnings) where:
        - is_valid: True if all critical checks pass, False otherwise
        - warnings: List of warning messages (can be empty)
    """
    warnings = []

    # Defensive: handle None or empty content
    if jira_content is None:
        return False, ["Jira content is None"]

    if not jira_content or len(jira_content.strip()) == 0:
        return False, ["Jira content is empty"]

    try:
        # Convert to lowercase for case-insensitive matching
        content_lower = jira_content.lower()

        # 1. Check for 2-7 backend tasks
        # Pattern matches: "# Subtarefa Backend", "## Backend Task", etc.
        backend_pattern = r'#{1,3}\s*(?:subtarefa\s+)?backend(?:\s+\d+)?'
        backend_tasks = re.findall(backend_pattern, content_lower, re.IGNORECASE)
        backend_count = len(backend_tasks)

        if backend_count < 2 or backend_count > 7:
            warnings.append(
                f"Backend tasks count ({backend_count}) outside recommended range of 2-7. "
                "Consider breaking down into multiple granular tasks."
            )

        # 2. Check for 2-7 frontend tasks
        frontend_pattern = r'#{1,3}\s*(?:subtarefa\s+)?frontend(?:\s+\d+)?'
        frontend_tasks = re.findall(frontend_pattern, content_lower, re.IGNORECASE)
        frontend_count = len(frontend_tasks)

        if frontend_count < 2 or frontend_count > 7:
            warnings.append(
                f"Frontend tasks count ({frontend_count}) outside recommended range of 2-7. "
                "Consider breaking down into multiple granular tasks."
            )

        # 3. Check for unit test mentions within implementation tasks
        # Look for common unit test keywords in Portuguese and English
        unit_test_keywords = [
            'unit test', 'teste unitário', 'testes unitários',
            'unittest', 'jest', 'pytest', 'tdd', 'test-driven'
        ]
        has_unit_test_mentions = any(keyword in content_lower for keyword in unit_test_keywords)

        if not has_unit_test_mentions and (backend_count > 0 or frontend_count > 0):
            warnings.append(
                "Unit tests not explicitly mentioned in implementation tasks. "
                "Each task should include its unit tests following TDD principles."
            )

        # 4. Check for separate E2E test section
        e2e_keywords = ['e2e', 'end-to-end', 'teste e2e', 'testes e2e', 'test e2e']
        has_e2e_section = any(keyword in content_lower for keyword in e2e_keywords)

        if not has_e2e_section:
            warnings.append(
                "No dedicated E2E test section found. "
                "Consider adding separate E2E test tasks covering main user flows."
            )

        # 5. Check for week estimates format (exact numbers)
        # Pattern matches: "2 weeks", "1.5 weeks", "3.5 semanas", etc.
        week_pattern = r'(\d+(?:\.\d+)?)\s*(?:week|semana|wk)'
        week_estimates = re.findall(week_pattern, content_lower)

        # Check for vague estimates (ranges, "around", etc.)
        vague_patterns = [
            r'\d+-\d+\s*(?:week|semana)',  # "2-3 weeks"
            r'around\s+\d+',  # "around 2"
            r'approximately\s+\d+',  # "approximately 2"
            r'cerca de\s+\d+',  # "cerca de 2" (Portuguese)
        ]
        has_vague_estimates = any(
            re.search(pattern, content_lower) for pattern in vague_patterns
        )

        if has_vague_estimates:
            warnings.append(
                "Week estimates should be exact numbers (e.g., '2.5 weeks'), "
                "not ranges or approximations."
            )

        # 6. Check minimum 0.5 weeks
        if week_estimates:
            numeric_estimates = [float(est) for est in week_estimates]
            min_estimate = min(numeric_estimates)

            if min_estimate < 0.5:
                warnings.append(
                    f"Found task with estimate below minimum 0.5 weeks ({min_estimate} weeks). "
                    "All tasks should be at least 0.5 weeks."
                )

        # 7. Check for dependency/workflow information
        dependency_keywords = [
            'dependência', 'dependências', 'dependency', 'dependencies',
            'depends on', 'depende de', 'workflow', 'fluxo',
            '→', '-->', 'after', 'após', 'before', 'antes'
        ]
        has_dependencies = any(keyword in content_lower for keyword in dependency_keywords)

        if not has_dependencies and (backend_count > 1 or frontend_count > 1):
            warnings.append(
                "No dependency or workflow information found. "
                "Consider specifying task dependencies and execution order."
            )

        # Determine overall validity
        # Critical issues that make content invalid:
        is_valid = True

        # If backend or frontend count is 0 for BOTH, it's invalid
        if backend_count == 0 and frontend_count == 0:
            is_valid = False
            warnings.append("No backend or frontend tasks found. Content appears incomplete.")

        # Having only 1 task (old style) is now considered invalid per new requirements
        if backend_count == 1:
            is_valid = False

        if frontend_count == 1:
            is_valid = False

        # If either area has too many tasks (> 7), it's invalid
        if backend_count > 7:
            is_valid = False

        if frontend_count > 7:
            is_valid = False

        # If there are tasks but no week estimates at all, it's invalid
        if (backend_count > 0 or frontend_count > 0) and len(week_estimates) == 0:
            is_valid = False
            warnings.append("No week estimates found. All tasks must have time estimates.")

        return is_valid, warnings

    except Exception as e:
        # Never raise exceptions - always return a result
        logger.error(f"Error during Jira validation: {e}", exc_info=True)
        return False, [f"Validation error: {str(e)}"]
