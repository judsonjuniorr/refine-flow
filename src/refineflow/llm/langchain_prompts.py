"""LangChain-based prompts for RefineFlow."""

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# Pydantic models para output parsing
class StateUpdate(BaseModel):
    """Schema for activity state updates."""

    summary: str = Field(description="Resumo conciso da atividade")
    action_items: list[dict] = Field(
        default_factory=list,
        description="Itens de ação com chaves 'action', 'owner', 'status'",
    )
    open_questions: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Perguntas categorizadas por Frontend, Backend, Arquitetura, "
        "Produto, UX/UI, Geral",
    )
    decisions: list[dict] = Field(
        default_factory=list,
        description="Decisões com chaves 'decision', 'rationale', 'date'",
    )
    functional_requirements: list[str] = Field(
        default_factory=list, description="Requisitos funcionais"
    )
    non_functional_requirements: list[str] = Field(
        default_factory=list, description="Requisitos não-funcionais"
    )
    identified_risks: list[dict] = Field(
        default_factory=list,
        description="Riscos com chaves 'risk', 'impact', 'mitigation'",
    )
    dependencies: list[dict] = Field(
        default_factory=list,
        description="Dependências com chaves 'dependency', 'type', 'status'",
    )
    metrics: list[dict] = Field(
        default_factory=list,
        description="Métricas com chaves 'metric', 'target', 'measurement'",
    )
    cost_estimates: list[dict] = Field(
        default_factory=list, description="Estimativas com chaves 'item', 'amount', 'notes'"
    )
    information_gaps: list[str] = Field(
        default_factory=list, description="Lacunas de informação"
    )


# Template para extração de estado
EXTRACTION_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um assistente especializado em refinamento de atividades técnicas.
Sua tarefa é extrair informações estruturadas de entradas do usuário e atualizar \
o estado da atividade.

Analise cuidadosamente a entrada e identifique:
- Itens de ação (com responsável e status quando possível)
- Perguntas abertas ou incertezas
- Decisões tomadas
- Requisitos funcionais e não-funcionais
- Riscos com impacto e mitigação
- Dependências internas e externas
- Métricas e estimativas de custo (utilize modelo T-Shirt quando aplicável)
- Lacunas de informação

**Modelo de Estimativas T-Shirt Sizing:**
- PP: Muito simples (até 2 semanas) - Ajuste pontual, 1 endpoint simples
- P: Simples/Baixa complexidade (até 1 mês) - Pequena feature isolada
- M: Complexidade média (até 2 meses) - Feature com UI, API e fluxo
- G: Alta complexidade (até 3 meses) - Múltiplos serviços/integrações
- GG: Muito complexo (até 5 meses) - Refatorações grandes, projetos amplos
- XGG: Extremamente complexo (meses) - Iniciativas estratégicas

Seja específico, conciso e extraia apenas informações explícitas ou claramente implícitas.

{format_instructions}""",
        ),
        (
            "human",
            """**Atividade**: {activity_title}
**Descrição**: {activity_description}

**Nova Entrada ({entry_type})**:
{entry_content}

**Estado Atual**:
Resumo: {current_summary}

Extraia e retorne as informações estruturadas desta entrada.""",
        ),
    ]
)


# Template para chat
CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um assistente especializado em refinamento de atividades técnicas.
Sua tarefa é responder perguntas sobre a atividade usando o contexto disponível.

Diretrizes:
- Cite informações específicas do log quando relevante
- Se informação não estiver disponível, declare claramente o que falta
- Sugira próximos passos quando apropriado
- Seja conciso mas completo""",
        ),
        (
            "human",
            """**Atividade**: {activity_title}
**Descrição**: {activity_description}

**Resumo Atual**:
{summary}

**Entradas Recentes do Log**:
{log_content}

**Pergunta**: {question}

Forneça uma resposta útil baseada no contexto disponível.""",
        ),
    ]
)


# Template para exportação Jira
JIRA_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em criar histórias Jira bem estruturadas.
Sua tarefa é gerar uma tarefa pai e subtarefas (backend e frontend) baseadas na atividade.

Estrutura esperada:
1. **Tarefa Pai**: Visão geral completa com contexto e critérios de aceitação
2. **Subtarefa Backend**: Trabalho específico de backend, APIs, banco de dados, etc.
3. **Subtarefa Frontend**: Trabalho específico de frontend, UI/UX, componentes, etc.

Cada tarefa deve incluir:
- Título claro e conciso
- Descrição detalhada
- Critérios de aceitação específicos e testáveis
- Estimativa T-Shirt (PP, P, M, G, GG, XGG)
- Considerações sobre testes, observabilidade e riscos

**Modelo de Estimativas T-Shirt:**
- PP: até 2 semanas | P: até 1 mês | M: até 2 meses
- G: até 3 meses | GG: até 5 meses | XGG: meses de trabalho""",
        ),
        (
            "human",
            """**Atividade**: {activity_title}
**Descrição**: {activity_description}

**Resumo**: {summary}

**Requisitos Funcionais**:
{functional_requirements}

**Requisitos Não-Funcionais**:
{non_functional_requirements}

**Riscos Identificados**: {risks_count}
**Dependências**: {dependencies_count}

Gere as tarefas Jira no formato Markdown.""",
        ),
    ]
)


# Template para Business Case Canvas
CANVAS_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em análise de negócios e criação de Business Case Canvas.
Sua tarefa é gerar um Business Case Canvas completo baseado nas informações da atividade.

O canvas deve cobrir:
1. **Problema**: O que, quem tem, por que é importante
2. **Solução**: Proposta e relação com o problema
3. **Recursos**: Tangíveis, intangíveis, dependências
4. **Benefícios**: Propósito, objetivos, benefícios financeiros/não-financeiros
5. **Escopo**: In/out, cronograma, relevância estratégica
6. **Riscos**: Identificados com mitigações
7. **Stakeholders**: Listados com papéis
8. **Complexidade**: Esforços usando modelo T-Shirt (PP a XGG)
9. **Comunicação**: Materiais, vídeos, treinamento
10. **Custos**: Fontes, orçamento, total ao longo do tempo
11. **Métricas**: Sucesso e benefícios

**Modelo de Estimativas T-Shirt Sizing:**
| Tamanho | Significado | Exemplo | Duração |
|---------|-------------|---------|----------|
| PP | Muito simples | Ajuste pontual, 1 endpoint simples | até 2 semanas |
| P | Simples/Baixa complexidade | Pequena feature isolada | até 1 mês |
| M | Complexidade média | Feature com UI, API e fluxo | até 2 meses |
| G | Alta complexidade | Múltiplos serviços/integrações | até 3 meses |
| GG | Muito complexo | Refatorações grandes, projetos amplos | até 5 meses |
| XGG | Extremamente complexo | Iniciativas estratégicas | meses de trabalho |

Sempre inclua uma seção "Modelo de Estimativas T-Shirt Sizing" com a tabela completa \
e uma estimativa inicial para a atividade baseada nos dados disponíveis.

Identifique lacunas de informação e sugira perguntas para completar.""",
        ),
        (
            "human",
            """**Atividade**: {activity_title}
**Descrição**: {activity_description}

**Resumo**: {summary}

**Informações Disponíveis**:
- Requisitos: {requirements_count}
- Riscos: {risks_count}
- Dependências: {dependencies_count}
- Stakeholders: {stakeholders_count}
- Decisões: {decisions_count}

**Detalhes do Estado**:
{state_json}

Gere o Business Case Canvas completo em Markdown.""",
        ),
    ]
)


def get_extraction_chain(llm):
    """Create extraction chain with JSON output parser."""
    parser = JsonOutputParser(pydantic_object=StateUpdate)
    prompt = EXTRACTION_TEMPLATE.partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser


def get_chat_chain(llm):
    """Create chat chain with string output."""
    parser = StrOutputParser()
    return CHAT_TEMPLATE | llm | parser


def get_jira_chain(llm):
    """Create Jira export chain."""
    parser = StrOutputParser()
    return JIRA_TEMPLATE | llm | parser


def get_canvas_chain(llm):
    """Create canvas generation chain."""
    parser = StrOutputParser()
    return CANVAS_TEMPLATE | llm | parser
