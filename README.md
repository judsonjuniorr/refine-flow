# RefineFlow

Agente de refinamento de atividades com IA e CLI interativa para gerenciamento de tarefas técnicas.

> **Nota**: A interface do usuário está completamente em português brasileiro (pt-BR).

## ✨ Novidades na v0.2.0

🚀 **Integração LangChain Completa**
- ✅ Prompts otimizados com templates estruturados
- ✅ Gerenciamento automático de tokens por modelo (20+ modelos OpenAI)
- ✅ Suporte para reasoning models (O1 series) com detecção automática
- ✅ Output parsing com validação (JSON + String)
- ✅ Logging detalhado de tokens e metadata

📖 [Leia mais sobre a implementação LangChain](LANGCHAIN.md)

## Funcionalidades

- 🎯 **Gerenciamento de Contexto**: Crie e mantenha contextos detalhados para cada atividade técnica
- 🤖 **Análise com IA**: Extração automática de itens de ação, questões, decisões e lacunas
- 📊 **Business Case Canvas**: Gere documentação abrangente de business case
- 🎫 **Exportação Jira**: Exporte atividades como tarefas pai com subtarefas backend/frontend
- 💬 **Chat Interativo**: Perguntas e respostas com contexto e citações
- 📝 **Armazenamento Markdown**: Todos os dados armazenados em arquivos Markdown legíveis
- 🔍 **Busca Inteligente**: Índice SQLite para pesquisa rápida de atividades

## Instalação

### Requisitos

- Python 3.12 ou superior
- Chave de API OpenAI
- (Opcional) Ollama para embeddings

### Configuração

#### Opção 1: Setup Automático (Recomendado)

```bash
git clone <repository-url>
cd refinement-agent
./setup.sh
```

O script irá:
- Criar ambiente virtual
- Instalar todas as dependências
- Configurar .env
- Opcionalmente iniciar Ollama com Docker

#### Opção 2: Setup Manual

1. Clone o repositório:
```bash
git clone <repository-url>
cd refinement-agent
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale o pacote:
```bash
pip install -e ".[dev]"
```

**Ou use o Makefile:**
```bash
make install
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env e adicione sua chave de API OpenAI
```

> **Dica**: Use `make help` para ver todos os comandos disponíveis.

## Configuração

### Configuração Obrigatória

Defina sua chave de API OpenAI no `.env`:
```env
OPENAI_API_KEY=sua-chave-api-aqui
OPENAI_MODEL=gpt-5-mini
```

### Opcional: Ollama para Embeddings

Se você quiser usar embeddings para busca semântica, há duas opções:

#### Opção 1: Usando Docker Compose (Recomendado)

1. Inicie o Ollama com Docker Compose:
```bash
docker-compose up -d
```

O container irá:
- Subir o servidor Ollama na porta 11434
- Baixar automaticamente o modelo `snowflake-arctic-embed`
- Manter os dados persistentes no volume Docker

2. Configure no `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=snowflake-arctic-embed
ENABLE_EMBEDDINGS=true
```

3. Verificar status:
```bash
docker-compose logs -f ollama
```

4. Parar o serviço:
```bash
docker-compose down
```

#### Opção 2: Instalação Local

1. Instale o [Ollama](https://ollama.ai/)
2. Baixe o modelo de embedding:
```bash
ollama pull snowflake-arctic-embed
```
3. Configure no `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=snowflake-arctic-embed
ENABLE_EMBEDDINGS=true
```

## Uso

### Iniciar a Aplicação

```bash
refineflow
```

Ou usando o módulo Python:
```bash
python -m refineflow
```

### Fluxos Principais

#### 1. Criar uma Nova Atividade

1. Selecione "📝 Criar Nova Atividade" no menu principal
2. Responda as perguntas de inicialização:
   - Título da Atividade
   - Breve Descrição
   - Declaração do Problema
   - Stakeholders (separados por vírgula)
   - Restrições/Cronograma
   - Sistema/Produto Afetado

O sistema cria uma estrutura de pastas com templates Markdown.

#### 2. Trabalhar em uma Atividade

1. Selecione "🔄 Selecionar Atividade em Andamento"
2. Escolha dentre as atividades disponíveis
3. Visualize o painel de status com resumo e ações abertas
4. Opções:
   - Adicionar informação (notas, perguntas, decisões, transcrições, etc.)
   - Conversar com contexto
   - Gerar Business Case Canvas
   - Exportar para Jira
   - Finalizar atividade

#### 3. Adicionar Informação

Selecione o tipo de entrada:
- **Nota**: Observação ou informação geral
- **Pergunta**: Questão aberta ou incerteza
- **Resposta**: Resposta a uma pergunta anterior
- **Transcrição**: Transcrição de reunião ou conversa
- **Decisão**: Decisão documentada
- **Requisito**: Requisito funcional ou não-funcional
- **Risco**: Risco identificado e mitigação
- **Métrica**: Métrica de sucesso ou KPI
- **Custo**: Estimativa de custo ou item de orçamento
- **Dependência**: Dependência interna ou externa

Escolha o método de entrada:
- **Múltiplas linhas (terminal)**: Digite diretamente no terminal (ESC + Enter ou Ctrl+D para finalizar)
- **Editor do Sistema**: Abre o editor padrão do sistema ($EDITOR)

#### 4. Modo Conversação

Faça perguntas sobre o contexto da atividade. A IA irá:
- Usar todo o contexto disponível de logs e estado
- Citar fontes (nomes de arquivos e timestamps)
- Fornecer insights relevantes

Digite 'sair' para retornar ao menu.

#### 5. Gerar Business Case Canvas

Cria um documento abrangente de business case cobrindo:
- Problema e Solução
- Recursos e Dependências
- Benefícios e ROI
- Escopo e Cronograma
- Riscos e Mitigações
- Stakeholders
- Análise de Complexidade
- Plano de Comunicação
- Custos e Métricas

O canvas destaca informações faltantes e sugere perguntas para completá-lo.

#### 6. Exportar para Jira

Gera:
- Tarefa pai com contexto completo
- Subtarefa de backend
- Subtarefa de frontend

Formatos de exportação:
- **Markdown**: Formatado para copiar e colar
- **JSON**: Dados estruturados
- **CSV**: Compatível com planilhas

#### 7. Finalizar Atividade

- Marca a atividade como completa
- Previne modificações futuras
- Permite consulta e exportação

## Estrutura do Projeto

```
data/
└── activities/
    └── <slug-da-atividade>/
        ├── activity.md       # Visão geral e metadados
        ├── log.md           # Entradas cronológicas
        ├── canvas.md        # Business Case Canvas
        ├── jira_export.md   # Saída da exportação Jira
        ├── state.json       # Estado estruturado
        └── chat.md          # Histórico de conversas
```

## Desenvolvimento

### Comandos Rápidos com Makefile

```bash
make help          # Lista todos os comandos disponíveis
make install       # Instala o projeto
make test          # Executa testes
make test-cov      # Testes com cobertura
make lint          # Verifica código
make format        # Formata código
make run           # Inicia RefineFlow
make docker-up     # Inicia Ollama
make docker-logs   # Ver logs do Ollama
make docker-down   # Para Ollama
make setup         # Configura tudo (install + docker-up)
```

### Executar Testes

```bash
pytest
# ou
make test
```

### Verificação de Tipos

```bash
mypy src/refineflow
# ou
make type-check
```

### Linting

```bash
ruff check src/refineflow
ruff format src/refineflow
# ou
make format
```

## Arquitetura

- **Armazenamento**: Arquivos Markdown + índice SQLite
- **IA**: OpenAI API com **LangChain** para geração e análise de texto
- **Prompts**: Templates estruturados com system/human messages em pt-BR
- **Token Management**: Otimização automática baseada em modelo e tipo de tarefa
- **Output Parsing**: Validação automática com JsonOutputParser e StrOutputParser
- **Embeddings**: Integração opcional com Ollama para busca semântica (via Docker)
- **Interface**: Rich panels e Questionary para menus interativos
- **Configuração**: Pydantic settings com variáveis de ambiente

## Modelos Suportados

RefineFlow suporta automaticamente 20+ modelos OpenAI com otimização de tokens:

- **GPT-4 Series**: gpt-4, gpt-4-32k, gpt-4-turbo, gpt-4-turbo-preview
- **GPT-4o Series**: gpt-4o, gpt-4o-mini (128K input / 16K output)
- **GPT-3.5 Series**: gpt-3.5-turbo, gpt-3.5-turbo-16k
- **O1 Series** (Reasoning): o1, o1-preview, o1-mini
  - ⚠️ Detecção automática - remove parâmetro `temperature`

Configure no `.env`:
```env
OPENAI_MODEL=gpt-4-turbo  # ou gpt-4o, o1-mini, etc
```

📖 [Ver lista completa de modelos e limites](LANGCHAIN.md#modelos-suportados)

## Arquivos de Configuração

- `docker-compose.yml` - Configuração do Ollama com download automático do modelo
- `Makefile` - Comandos úteis para desenvolvimento
- `.env.example` - Template de variáveis de ambiente
- `pyproject.toml` - Configuração do projeto Python
- `DOCKER.md` - Documentação detalhada do Docker

## Licença

MIT
