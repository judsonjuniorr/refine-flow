"""LLM processing logic with LangChain."""

import json

from refineflow.core.models import Activity, Entry
from refineflow.core.state import ActivityState
from refineflow.llm.client_langchain import OpenAIClient
from refineflow.llm.langchain_prompts import (
    StateUpdate,
    get_canvas_chain,
    get_chat_chain,
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
