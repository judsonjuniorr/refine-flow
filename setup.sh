#!/bin/bash
# Script de configuração rápida do RefineFlow

set -e

echo "🚀 RefineFlow - Setup Rápido"
echo "=============================="
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.12 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"

# Verifica Docker (opcional)
if command -v docker &> /dev/null; then
    echo "✅ Docker encontrado"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker não encontrado (opcional, necessário apenas para Ollama)"
    DOCKER_AVAILABLE=false
fi

echo ""

# Cria ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativa ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instala dependências
echo "📥 Instalando dependências..."
pip install -q --upgrade pip
pip install -q -e ".[dev]"
echo "✅ Dependências instaladas"

# Configura .env
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Configurando .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado"
    echo ""
    echo "⚠️  IMPORTANTE: Configure sua OPENAI_API_KEY no arquivo .env"
    echo "   1. Abra o arquivo .env em um editor"
    echo "   2. Adicione sua chave da OpenAI"
    echo "   3. Salve o arquivo"
    echo ""
else
    echo "✅ Arquivo .env já existe"
fi

# Pergunta sobre Ollama
echo ""
if [ "$DOCKER_AVAILABLE" = true ]; then
    read -p "❓ Deseja iniciar o Ollama com Docker para embeddings? (s/N): " start_ollama
    if [[ $start_ollama =~ ^[Ss]$ ]]; then
        echo "🐳 Iniciando Ollama com Docker..."
        docker-compose up -d
        echo "✅ Ollama iniciado!"
        echo "   Use 'docker-compose logs -f ollama' para ver o progresso do download"
        echo "   Configure ENABLE_EMBEDDINGS=true no .env para usar embeddings"
    fi
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Configure OPENAI_API_KEY no arquivo .env"
echo "   2. Execute: source venv/bin/activate"
echo "   3. Execute: refineflow"
echo ""
echo "💡 Comandos úteis:"
echo "   make help         - Ver todos os comandos"
echo "   make run          - Iniciar RefineFlow"
echo "   make test         - Executar testes"
echo "   make docker-up    - Iniciar Ollama"
echo "   make docker-logs  - Ver logs do Ollama"
echo ""
