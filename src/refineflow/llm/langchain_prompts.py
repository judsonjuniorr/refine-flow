"""LangChain-based prompts for RefineFlow."""

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# T-Shirt size to weeks conversion mapping
TSHIRT_TO_WEEKS = {
    "PP": 1,  # Até 2 semanas → 1 semana como referência
    "P": 2,  # Até 1 mês → 2 semanas
    "M": 4,  # Até 2 meses → 4 semanas
    "G": 8,  # Até 3 meses → 8 semanas
    "GG": 12,  # Até 5 meses → 12 semanas
    "XGG": 20,  # Meses de trabalho → 20 semanas
}


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
    information_gaps: list[str] = Field(default_factory=list, description="Lacunas de informação")


class EntryTypeClassification(BaseModel):
    """Schema for entry type classification."""

    entry_type: str = Field(
        description="Tipo da entrada: note, answer, transcript, jira_description, "
        "decision, requirement, risk, metric, cost, ou dependency"
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

**Categorização de Questões Abertas:**

Categorize cada questão identificada nas seguintes categorias. Uma questão pode aparecer em \
múltiplas categorias se for relevante para múltiplos domínios:

- **Frontend**: Questões sobre componentes UI, lógica client-side, implementação de interface de usuário, \
bibliotecas frontend, frameworks (React, Vue, Angular), validação de formulários, etc.

- **Backend**: Questões sobre APIs, serviços, banco de dados, lógica server-side, processamento de dados, \
autenticação, autorização, endpoints, integrações backend, etc.

- **Arquitetura**: Questões sobre design de sistema, infraestrutura, escalabilidade, padrões arquiteturais, \
microserviços vs monolito, cloud, DevOps, observabilidade, etc.

- **Produto**: Questões sobre requisitos de negócio, features, histórias de usuário, priorização, \
roadmap, decisões de produto, métricas de negócio, etc.

- **UX/UI**: Questões sobre design de experiência do usuário, usabilidade, fluxos de usuário, \
design visual, acessibilidade, interações, wireframes, protótipos, etc.

- **Geral**: Questões sobre gestão de projeto (prazos, orçamento, equipe, processo) OU questões \
que não se encaixam claramente nas categorias técnicas acima.

**Exemplos de Categorização:**
- "Como validar o CPF no formulário?" → Frontend, Backend
- "Qual é a capacidade máxima do servidor?" → Backend, Arquitetura  
- "O usuário espera notificação por email ou SMS?" → Produto, UX/UI
- "Qual biblioteca de validação usar?" → Frontend (se contexto é UI) ou Backend (se contexto é API)
- "Qual prazo do projeto?" → Geral

**IMPORTANTE**: Categorize cada questão na(s) categoria(s) mais apropriada(s). Se uma questão é \
relevante para múltiplos domínios, coloque-a em todas as categorias aplicáveis.

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
2. **Subtarefas Backend (2-7 tarefas)**: Divida o trabalho de backend em 2 a 7 tarefas menores
   e entregáveis baseado na complexidade. Cada tarefa de implementação DEVE incluir seus testes
   unitários seguindo TDD (escrever o teste primeiro, depois o código).
3. **Subtarefas Frontend (2-7 tarefas)**: Divida o trabalho de frontend em 2 a 7 tarefas menores
   e entregáveis baseado na complexidade. Cada tarefa de implementação DEVE incluir seus testes
   unitários seguindo TDD (escrever o teste primeiro, depois o código).
4. **Tarefas de Teste E2E (separadas)**: Crie tarefas independentes para testes end-to-end (E2E)
   cobrindo os principais fluxos de usuário.

**Instruções para Divisão de Tarefas:**
- Divida backend e frontend em 2-7 subtarefas cada, baseado na complexidade e tamanho
- Tarefas menores/simples: 2-3 subtarefas
- Tarefas médias: 4-5 subtarefas
- Tarefas grandes/complexas: 6-7 subtarefas
- Cada subtarefa de implementação deve ser pequena, focada e entregável
- **IMPORTANTE**: Cada subtarefa de implementação DEVE incluir testes unitários como parte da tarefa
- Os testes unitários devem seguir TDD: escrever o teste primeiro, depois implementar o código
- Testes E2E devem ser tarefas separadas e independentes das implementações

Cada tarefa deve incluir:
- Título claro e conciso
- Descrição detalhada
- Critérios de aceitação específicos e testáveis (incluindo critérios para testes unitários)
- Estimativa T-Shirt (PP, P, M, G, GG, XGG)
- Estimativa em semanas (número exato, mínimo 0.5 semanas)
- Considerações sobre testes, observabilidade e riscos

**Modelo de Estimativas T-Shirt:**
- PP: até 2 semanas | P: até 1 mês | M: até 2 meses
- G: até 3 meses | GG: até 5 meses | XGG: meses de trabalho

**Diretrizes para Estimativas em Semanas:**
- Forneça números exatos (ex: 1.5, 2.5, 3.5 semanas), não intervalos
- Estimativa mínima é de 0.5 semanas por tarefa
- Use as estimativas T-Shirt como referência: PP≈1, P≈2, M≈4, G≈8, GG≈12, XGG≈20 semanas
- Ajuste o número exato baseado na complexidade específica da tarefa
- Formato recomendado: "Estimativa: M / 3.5 semanas" (T-shirt / semanas)

**Exemplos de Estimativas:**
- Tarefa pequena: "PP / 0.5 semanas"
- Tarefa média-simples: "P / 1.5 semanas"
- Tarefa média-complexa: "M / 3.5 semanas"
- Tarefa grande: "G / 7 semanas"
- Tarefa muito grande: "GG / 10 semanas"
- Tarefa extremamente complexa: "XGG / 18 semanas""",
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


# ============================================================================
# PHASE 4: Entry Type Classification
# ============================================================================

# Template para classificação de tipo de entrada
CLASSIFICATION_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um assistente especializado em classificar tipos de entrada em um sistema de refinamento de atividades.

Sua tarefa é analisar o conteúdo fornecido e determinar qual tipo de entrada ele representa.

**Tipos de Entrada Disponíveis:**

1. **note** (Nota): Observação geral, comentário, informação adicional sem compromisso formal.
   - Exemplo: "O sistema atual usa MySQL mas talvez possamos migrar para PostgreSQL no futuro."

2. **answer** (Resposta): Resposta direta a uma questão previamente identificada.
   - Exemplo: "Resposta à questão sobre autenticação: usaremos OAuth 2.0 com JWT."

3. **transcript** (Transcrição): Transcrição de reunião, conversa ou discussão entre múltiplas pessoas.
   - Exemplo: "João: Precisamos definir o prazo. Maria: Sugiro 2 sprints."

4. **jira_description** (Descrição Jira): Descrição formal de tarefa ou história de usuário importada do Jira.
   - Exemplo: "Como usuário, quero poder recuperar minha senha por email para poder acessar o sistema."

5. **decision** (Decisão): Decisão tomada pela equipe ou stakeholders, geralmente com justificativa.
   - Exemplo: "Decidimos usar PostgreSQL como banco de dados principal por sua robustez."

6. **requirement** (Requisito): Requisito funcional ou não-funcional do sistema.
   - Exemplo: "O sistema deve permitir que usuários façam login com email e senha."

7. **risk** (Risco): Risco identificado com possível impacto e/ou mitigação.
   - Exemplo: "Existe o risco de a API externa não suportar a carga, causando timeouts."

8. **metric** (Métrica): Métrica de sucesso, KPI ou indicador de desempenho.
   - Exemplo: "A taxa de conversão deve ser de pelo menos 15%."

9. **cost** (Custo): Estimativa de custo, orçamento ou recursos financeiros.
   - Exemplo: "O custo estimado da infraestrutura cloud é de R$ 5.000/mês."

10. **dependency** (Dependência): Dependência técnica ou de processo com outros sistemas/equipes.
    - Exemplo: "Dependemos da API do time de Pagamentos para processar transações."

**Regras de Classificação:**
- Analise o conteúdo cuidadosamente
- Escolha o tipo MAIS ESPECÍFICO que se aplica
- Se houver dúvida, prefira 'note' (é o tipo mais genérico)
- Decisões geralmente contêm palavras como "decidimos", "optamos", "escolhemos"
- Requisitos geralmente contêm "deve", "precisa", "é necessário"
- Riscos geralmente contêm "risco", "pode causar", "potencial problema"
- Transcrições têm formato de diálogo com múltiplos interlocutores

{format_instructions}""",
        ),
        ("human", "Classifique o seguinte conteúdo:\n\n{content}"),
    ]
)


def get_classification_chain(llm):
    """Create entry type classification chain."""
    parser = JsonOutputParser(pydantic_object=EntryTypeClassification)
    prompt = CLASSIFICATION_TEMPLATE.partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser
