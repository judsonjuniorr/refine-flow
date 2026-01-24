# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.2.0] - 2025-01-20

### Adicionado

- **Integração LangChain completa** para otimização de prompts e gerenciamento de tokens
  - `models.py`: Configuração de limites de tokens para 20+ modelos OpenAI
  - `langchain_prompts.py`: Templates estruturados com system/human messages em pt-BR
  - `client_langchain.py`: Cliente OpenAI usando LangChain ChatOpenAI
  - `processor_langchain.py`: Processamento com chains e output parsers
- **Otimização automática de tokens** baseada no tipo de tarefa (extraction: 30%, chat: 50%, jira: 60%, canvas: 70%)
- **Detecção automática de reasoning models** (O1 series) com remoção de parâmetro temperature
- **Suporte para 20+ modelos OpenAI** incluindo GPT-4, GPT-4o, GPT-3.5, O1 series
- **Output parsing automático** com JsonOutputParser e StrOutputParser
- **Logging detalhado** com informações de tokens, metadata e erros claros
- **Documentação LangChain** completa em `LANGCHAIN.md`

### Modificado

- **flows.py**: Atualizado para usar `processor_langchain` ao invés de `processor`
- **exporters.py**: 
  - Atualizado import para `processor_langchain`
  - Novo método `generate_canvas()` usando LangChain
  - Método fallback `_generate_canvas_fallback()` para compatibilidade
- **test_config.py**: Teste ajustado para aceitar múltiplos valores de modelo/log_level

### Dependências

- Adicionado `langchain>=0.1.0`
- Adicionado `langchain-openai>=0.0.5`
- Adicionado `langchain-core>=0.1.0`
- Adicionado `tiktoken>=0.5.0`

### Corrigido

- **Compatibilidade API OpenAI**: `max_tokens` → `max_completion_tokens`
- **Suporte reasoning models**: Remoção condicional do parâmetro `temperature`
- **Testes**: Todos os 56 testes passando com LangChain

## [0.1.0] - 2025-01-15

### Adicionado

- **Tradução completa pt-BR** de todos inputs/outputs
  - Menus CLI em português
  - Prompts em português  
  - Templates Markdown em português
  - Mensagens de erro e sucesso em português
- **Docker Compose** para Ollama local
  - Download automático do modelo `snowflake-arctic-embed`
  - Configuração de volumes persistentes
  - Healthcheck e restart automático
- **Makefile** com 15+ comandos de desenvolvimento
  - `make docker-up/down/logs/status`
  - `make install/test/lint/format/run`
  - `make setup` para configuração completa
- **Scripts de automação**
  - `setup.sh`: Setup automatizado do projeto
  - `ollama.sh`: CLI para gerenciar Ollama
- **Documentação Docker** completa em `DOCKER.md`
- **Template .env** com comentários em pt-BR

### Inicial

- Sistema de refinamento de atividades via LLM
- Armazenamento em Markdown + SQLite
- CLI interativo com Typer + Rich + Questionary
- Suporte para OpenAI API
- Exportadores Jira e Business Case Canvas
- Sistema de embeddings com Ollama (opcional)
- 56 testes com pytest
- Linting com ruff e mypy
