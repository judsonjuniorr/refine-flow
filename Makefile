.PHONY: help install test lint format clean run docker-up docker-down docker-logs

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instala o projeto e dependências
	pip install -e ".[dev]"

test: ## Executa os testes
	pytest -v

test-cov: ## Executa os testes com cobertura
	pytest -v --cov=src/refineflow --cov-report=html --cov-report=term

lint: ## Verifica o código com ruff
	ruff check src/refineflow tests

format: ## Formata o código com ruff
	ruff format src/refineflow tests
	ruff check --fix src/refineflow tests

type-check: ## Verifica tipos com mypy
	mypy src/refineflow

clean: ## Remove arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

run: ## Inicia o RefineFlow
	refineflow

docker-up: ## Inicia o Ollama com Docker Compose
	docker-compose up -d
	@echo "Aguardando Ollama iniciar e baixar o modelo snowflake-arctic-embed..."
	@echo "Acompanhe o progresso com: make docker-logs"

docker-down: ## Para o Ollama
	docker-compose down

docker-logs: ## Mostra os logs do Ollama
	docker-compose logs -f ollama

docker-restart: ## Reinicia o Ollama
	docker-compose restart ollama

docker-status: ## Mostra o status do container Ollama
	docker-compose ps
	@echo "\nModelos instalados:"
	@docker exec refineflow-ollama ollama list 2>/dev/null || echo "Container não está rodando"

docker-clean: ## Remove o container e volumes do Ollama
	docker-compose down -v
	@echo "Container e volumes removidos. O modelo precisará ser baixado novamente."

setup: install docker-up ## Configura todo o ambiente (instala + inicia Ollama)
	@echo "\n✅ Ambiente configurado!"
	@echo "1. Configure seu .env com OPENAI_API_KEY"
	@echo "2. Execute 'make run' para iniciar o RefineFlow"

all: clean install test lint ## Executa limpeza, instalação, testes e linting
