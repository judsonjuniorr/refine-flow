#!/bin/bash
# Comandos úteis para gerenciar o Ollama com Docker

case "$1" in
    start)
        echo "🚀 Iniciando Ollama..."
        docker-compose up -d
        echo "✅ Ollama iniciado na porta 11434"
        echo "📊 Acompanhe os logs com: $0 logs"
        ;;
    
    stop)
        echo "⏸️  Parando Ollama..."
        docker-compose down
        echo "✅ Ollama parado"
        ;;
    
    restart)
        echo "🔄 Reiniciando Ollama..."
        docker-compose restart ollama
        echo "✅ Ollama reiniciado"
        ;;
    
    logs)
        echo "📋 Logs do Ollama (Ctrl+C para sair):"
        docker-compose logs -f ollama
        ;;
    
    status)
        echo "📊 Status do Ollama:"
        docker-compose ps
        echo ""
        echo "📦 Modelos instalados:"
        docker exec refineflow-ollama ollama list 2>/dev/null || echo "❌ Container não está rodando"
        ;;
    
    models)
        echo "📦 Modelos disponíveis:"
        docker exec refineflow-ollama ollama list
        ;;
    
    pull)
        if [ -z "$2" ]; then
            echo "❌ Uso: $0 pull <nome-do-modelo>"
            echo "Exemplo: $0 pull llama2"
            exit 1
        fi
        echo "📥 Baixando modelo: $2"
        docker exec refineflow-ollama ollama pull "$2"
        ;;
    
    test)
        echo "🧪 Testando embeddings com snowflake-arctic-embed..."
        docker exec refineflow-ollama ollama run snowflake-arctic-embed "teste de embedding"
        ;;
    
    clean)
        read -p "⚠️  Isso irá remover o container e TODOS os modelos. Continuar? (s/N): " confirm
        if [[ $confirm =~ ^[Ss]$ ]]; then
            echo "🗑️  Removendo container e volumes..."
            docker-compose down -v
            echo "✅ Container e volumes removidos"
        else
            echo "❌ Operação cancelada"
        fi
        ;;
    
    shell)
        echo "🐚 Abrindo shell no container Ollama..."
        docker exec -it refineflow-ollama /bin/bash
        ;;
    
    *)
        echo "🐳 Ollama Docker Manager - RefineFlow"
        echo ""
        echo "Uso: $0 <comando>"
        echo ""
        echo "Comandos disponíveis:"
        echo "  start      - Inicia o Ollama"
        echo "  stop       - Para o Ollama"
        echo "  restart    - Reinicia o Ollama"
        echo "  logs       - Mostra logs em tempo real"
        echo "  status     - Mostra status e modelos instalados"
        echo "  models     - Lista modelos instalados"
        echo "  pull       - Baixa um novo modelo (ex: $0 pull llama2)"
        echo "  test       - Testa embeddings"
        echo "  clean      - Remove container e todos os modelos"
        echo "  shell      - Abre shell no container"
        echo ""
        echo "Exemplos:"
        echo "  $0 start                    # Inicia Ollama"
        echo "  $0 logs                     # Ver logs"
        echo "  $0 pull llama2              # Baixar modelo llama2"
        echo "  $0 test                     # Testar embeddings"
        echo ""
        exit 1
        ;;
esac
