# LangChain Integration

## Visão Geral

O RefineFlow agora usa LangChain para otimizar prompts, gerenciar tokens automaticamente e suportar múltiplos modelos OpenAI com suas configurações específicas.

## Arquitetura

### Componentes Principais

1. **models.py** - Configuração de limites de tokens por modelo
2. **langchain_prompts.py** - Templates de prompts estruturados com parsers
3. **client_langchain.py** - Cliente OpenAI usando LangChain ChatOpenAI
4. **processor_langchain.py** - Lógica de processamento usando chains

## Modelos Suportados

O sistema agora suporta automaticamente:

### GPT-4 Series
- `gpt-4` (8K input / 8K output)
- `gpt-4-32k` (32K input / 32K output)
- `gpt-4-turbo`, `gpt-4-turbo-2024-04-09`, `gpt-4-turbo-preview` (128K input / 4K output)
- `gpt-4-1106-preview`, `gpt-4-0125-preview` (128K input / 4K output)

### GPT-4o Series  
- `gpt-4o`, `gpt-4o-2024-05-13`, `gpt-4o-2024-08-06` (128K input / 16K output)
- `gpt-4o-mini`, `gpt-4o-mini-2024-07-18` (128K input / 16K output)

### GPT-3.5 Series
- `gpt-3.5-turbo`, `gpt-3.5-turbo-16k` (16K input / 4K output)
- `gpt-3.5-turbo-1106`, `gpt-3.5-turbo-0125` (16K input / 4K output)

### O1 Series (Reasoning Models)
- `o1` (200K input / 100K output)
- `o1-preview` (128K input / 32K output)
- `o1-mini` (128K input / 65K output)

### Outros
- `gpt-5-mini` (128K input / 4K output)

## Otimização Automática de Tokens

O sistema calcula automaticamente o `max_tokens` baseado no tipo de tarefa:

| Tipo de Tarefa | % do Max Output | Uso |
|----------------|-----------------|-----|
| **extraction** | 30% | Extração de entidades e atualização de estado |
| **chat** | 50% | Respostas a perguntas |
| **jira** | 60% | Geração de export Jira |
| **canvas** | 70% | Geração de Business Case Canvas |

### Exemplo

Para `gpt-4o` (max output: 16K tokens):
- extraction: 4,800 tokens
- chat: 8,000 tokens
- jira: 9,600 tokens
- canvas: 11,200 tokens

## Modelos de Raciocínio (Reasoning Models)

Os modelos O1 series (`o1`, `o1-preview`, `o1-mini`) têm restrições especiais:

- ✅ **Suportam:** `max_completion_tokens`
- ❌ **Não suportam:** parâmetro `temperature` (sempre usa valor padrão)

O sistema detecta automaticamente esses modelos e remove o parâmetro `temperature`.

## Prompts Estruturados

Todos os prompts agora usam `ChatPromptTemplate` com mensagens separadas:

```python
EXTRACTION_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """Você é um assistente especializado..."""),
    ("human", """Entrada do usuário:
{entry_text}

Contexto atual:
{current_state}""")
])
```

### Benefícios

1. **Separação clara** entre instruções do sistema e input do usuário
2. **Reutilização** de prompts em diferentes contextos
3. **Parsing automático** de respostas com validação

## Output Parsing

### JsonOutputParser

Usado para `process_entry()` - valida e converte JSON para `ActivityState`:

```python
chain = prompt | llm | JsonOutputParser()
result = chain.invoke(inputs)  # Retorna dict validado
```

### StrOutputParser

Usado para `answer_question()`, `generate_jira_export()`, `generate_canvas()`:

```python
chain = prompt | llm | StrOutputParser()
result = chain.invoke(inputs)  # Retorna string
```

## Logging Detalhado

O sistema agora registra:

- ✅ Modelo usado e seus limites de tokens
- ✅ Max tokens calculado para a tarefa
- ✅ Detecção de reasoning model
- ✅ Metadata da resposta (tokens usados, finish_reason)
- ✅ Erros de parsing com mensagens claras

## Migração do Código Antigo

### Antes (Direct OpenAI API)

```python
from refineflow.llm.processor import LLMProcessor

processor = LLMProcessor()
state = processor.process_entry(activity, entry, state)
```

### Agora (LangChain)

```python
from refineflow.llm.processor_langchain import LLMProcessor

processor = LLMProcessor()
state = processor.process_entry(activity, entry, state)
```

A interface pública permanece a mesma! Apenas mude o import.

## Arquivos Criados/Modificados

### Novos Arquivos

- `src/refineflow/llm/models.py` (106 linhas)
- `src/refineflow/llm/langchain_prompts.py` (166 linhas)
- `src/refineflow/llm/client_langchain.py` (135 linhas)
- `src/refineflow/llm/processor_langchain.py` (210 linhas)

### Arquivos Modificados

- `pyproject.toml` - Adicionadas dependências LangChain
- `src/refineflow/cli/flows.py` - Import atualizado para `processor_langchain`
- `src/refineflow/core/exporters.py` - Import atualizado, novo método `generate_canvas()`
- `tests/test_config.py` - Teste ajustado para aceitar múltiplos modelos

## Dependências Adicionadas

```toml
langchain = ">=0.1.0"
langchain-openai = ">=0.0.5"
langchain-core = ">=0.1.0"
tiktoken = ">=0.5.0"
```

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -e ".[dev]"
```

## Testes

Todos os 56 testes continuam passando:

```bash
pytest tests/ -v
```

## Próximos Passos

1. ✅ **Implementação base completa**
2. ✅ **Testes passando**
3. 🔄 **Testar com API real do OpenAI**
4. 🔄 **Validar JSON parsing com entradas reais**
5. 🔄 **Otimizar prompts baseado em feedback**
6. 📋 **Adicionar suporte para novos modelos conforme disponibilidade**

## Solução de Problemas

### Erro: "max_tokens not supported"

**Causa:** Modelo O1 series não suporta `max_tokens`  
**Solução:** Automática - o sistema usa `max_completion_tokens`

### Erro: "temperature does not support X with this model"

**Causa:** Modelo O1 series não suporta parâmetro `temperature`  
**Solução:** Automática - o sistema detecta e remove o parâmetro

### Erro: "Output parsing failed"

**Causa:** LLM retornou JSON inválido ou formato incorreto  
**Solução:** Verifique os logs detalhados, ajuste o prompt se necessário

### Respostas vazias

**Causa:** Possível problema com parâmetros do modelo ou prompt  
**Solução:** 
1. Verifique logs para ver JSON completo da resposta
2. Confirme que o modelo está configurado em `models.py`
3. Teste com modelo conhecido (ex: `gpt-4-turbo`)

## Referências

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Model Token Limits](https://platform.openai.com/docs/models)
