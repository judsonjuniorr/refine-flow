# Docker Compose - Ollama para RefineFlow

Este arquivo configura o Ollama localmente usando Docker para fornecer embeddings ao RefineFlow.

## O que faz

- Sobe um container Ollama na porta `11434`
- Baixa automaticamente o modelo `snowflake-arctic-embed:latest`
- Persiste os modelos no volume Docker `refineflow-ollama-data`
- Reinicia automaticamente o container em caso de falha
- Healthcheck para garantir que o serviço está saudável

## Comandos Úteis

### Iniciar o Ollama
```bash
docker-compose up -d
```

### Ver logs (primeira execução para ver o download do modelo)
```bash
docker-compose logs -f ollama
```

### Verificar status
```bash
docker-compose ps
```

### Parar o serviço
```bash
docker-compose down
```

### Remover volumes (apaga os modelos baixados)
```bash
docker-compose down -v
```

### Listar modelos disponíveis
```bash
docker exec refineflow-ollama ollama list
```

### Executar comandos no Ollama
```bash
# Testar embeddings
docker exec refineflow-ollama ollama run snowflake-arctic-embed "teste"

# Baixar outro modelo
docker exec refineflow-ollama ollama pull llama2
```

## Configuração do RefineFlow

Após iniciar o container, configure no `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=snowflake-arctic-embed
ENABLE_EMBEDDINGS=true
```

## Requisitos

- Docker
- Docker Compose
- ~4GB de espaço em disco para o modelo snowflake-arctic-embed

## Troubleshooting

### Container não inicia
```bash
docker-compose logs ollama
```

### Porta 11434 já está em uso
Edite `docker-compose.yml` e altere a porta:
```yaml
ports:
  - "11435:11434"  # Mude também no .env para OLLAMA_BASE_URL=http://localhost:11435
```

### Modelo não foi baixado
Execute manualmente:
```bash
docker exec refineflow-ollama ollama pull snowflake-arctic-embed
```
