"""Prompt builders for LLM tasks."""

from refineflow.core.models import Activity, Entry
from refineflow.core.state import ActivityState


def build_extraction_prompt(activity: Activity, entry: Entry, current_state: ActivityState) -> str:
    """
    Build prompt for extracting structured information from a new entry.

    Args:
        activity: Current activity
        entry: New entry to process
        current_state: Current state

    Returns:
        Extraction prompt
    """
    prompt = f"""Você é um assistente de IA ajudando a refinar atividades técnicas.

**Atividade**: {activity.title}
**Descrição**: {activity.description}

**Nova Entrada ({entry.entry_type})**:
{entry.content}

**Resumo Atual**:
{current_state.summary or "Ainda sem resumo"}

**Tarefa**: Extraia e atualize informações estruturadas desta entrada:
1. Atualize o resumo se necessário
2. Identifique itens de ação (com responsável e status)
3. Liste quaisquer perguntas abertas
4. Anote decisões tomadas
5. Extraia requisitos funcionais e não-funcionais
6. Identifique riscos com impacto e mitigação
7. Liste dependências (internas/externas)
8. Anote métricas ou custos mencionados
9. Identifique lacunas de informação

Retorne APENAS um JSON válido (sem markdown, sem explicações) seguindo o schema ActivityState.
Seja conciso e específico.

Exemplo de formato esperado:
{{
  "summary": "texto do resumo",
  "action_items": [],
  "open_questions": [],
  "decisions": [],
  "functional_requirements": [],
  "non_functional_requirements": [],
  "identified_risks": [],
  "dependencies": [],
  "metrics": [],
  "cost_estimates": [],
  "information_gaps": []
}}
"""
    return prompt


def build_chat_prompt(
    activity: Activity, state: ActivityState, log_content: str, question: str
) -> str:
    """
    Build prompt for answering questions about an activity.

    Args:
        activity: Current activity
        state: Current state
        log_content: Recent log entries
        question: User question

    Returns:
        Chat prompt
    """
    prompt = f"""Você é um assistente de IA ajudando com refinamento de atividades.

**Atividade**: {activity.title}
**Descrição**: {activity.description}

**Resumo Atual**:
{state.summary or "Resumo não disponível"}

**Entradas Recentes do Log**:
{log_content[:2000]}...

**Pergunta do Usuário**: {question}

Forneça uma resposta útil baseada no contexto da atividade. Cite entradas \
específicas do log ou informações do estado quando relevante. Se alguma informação \
estiver faltando, declare claramente o que é desconhecido e sugira como encontrá-la.
"""
    return prompt


def build_jira_export_prompt(activity: Activity, state: ActivityState) -> str:
    """
    Build prompt for generating Jira tasks export.

    Args:
        activity: Current activity
        state: Current state

    Returns:
        Jira export prompt
    """
    prompt = f"""Você é um assistente de IA gerando descrições de tarefas Jira.

**Atividade**: {activity.title}
**Descrição**: {activity.description}

**Resumo**: {state.summary}

**Requisitos**:
Funcionais: {
        ", ".join(state.functional_requirements)
        if state.functional_requirements
        else "Nenhum especificado"
    }
Não-funcionais: {
        ", ".join(state.non_functional_requirements)
        if state.non_functional_requirements
        else "Nenhum especificado"
    }

**Riscos**: {len(state.identified_risks)} identificados
**Dependências**: {len(state.dependencies)} listadas

**Tarefa**: Gere uma tarefa pai Jira e subtarefas separadas para backend + frontend.

Formato de saída:
## Tarefa Pai
- **Título**: [título conciso]
- **Descrição**: [descrição abrangente]
- **Critérios de Aceitação**: [lista de pontos]

## Subtarefa Backend
- **Título**: [título específico BE]
- **Descrição**: [trabalho de backend]
- **Critérios de Aceitação**: [critérios BE]

## Subtarefa Frontend
- **Título**: [título específico FE]
- **Descrição**: [trabalho de frontend]
- **Critérios de Aceitação**: [critérios FE]

Inclua testes, observabilidade e mitigação de riscos nas descrições.
"""
    return prompt
