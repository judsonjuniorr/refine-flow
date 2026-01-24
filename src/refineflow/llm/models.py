"""Model configuration and token limits."""

# Token limits para diferentes modelos OpenAI
# Format: "model_name": (input_tokens, output_tokens)
MODEL_LIMITS: dict[str, tuple[int, int]] = {
    # GPT-4 Turbo
    "gpt-4-turbo": (128000, 4096),
    # GPT-5 (reasoning model)
    "gpt-5-mini": (128000, 65536),
    "gpt-4-1106-preview": (128000, 4096),
    "gpt-4-0125-preview": (128000, 4096),
    # GPT-4
    "gpt-4": (8192, 4096),
    "gpt-4-0613": (8192, 4096),
    "gpt-4-32k": (32768, 4096),
    "gpt-4-32k-0613": (32768, 4096),
    # GPT-3.5 Turbo
    "gpt-3.5-turbo": (16385, 4096),
    "gpt-3.5-turbo-16k": (16385, 4096),
    "gpt-3.5-turbo-1106": (16385, 4096),
    "gpt-3.5-turbo-0125": (16385, 4096),
    # O1 Models (reasoning)
    "o1-preview": (128000, 32768),
    "o1-mini": (128000, 65536),
    "o1": (200000, 100000),
    # GPT-4o
    "gpt-4o": (128000, 16384),
    "gpt-4o-mini": (128000, 16384),
    # ChatGPT-4o-latest
    "chatgpt-4o-latest": (128000, 16384),
    # Default fallback
    "default": (8192, 4096),
}


def get_model_limits(model_name: str) -> tuple[int, int]:
    """
    Get token limits for a model.

    Args:
        model_name: Nome do modelo

    Returns:
        Tuple of (input_limit, output_limit)
    """
    # Normaliza o nome do modelo
    model_lower = model_name.lower()

    # Busca exata
    if model_lower in MODEL_LIMITS:
        return MODEL_LIMITS[model_lower]

    # Busca parcial (para versões com datas)
    for key, limits in MODEL_LIMITS.items():
        if key in model_lower:
            return limits

    # Fallback
    return MODEL_LIMITS["default"]


def is_reasoning_model(model_name: str) -> bool:
    """
    Check if model is a reasoning model (o1 series, gpt-5).

    Args:
        model_name: Nome do modelo

    Returns:
        True se for modelo de reasoning
    """
    model_lower = model_name.lower()
    return any(name in model_lower for name in ["o1", "o-1", "gpt-5"])


def get_max_output_tokens(model_name: str, task_type: str = "default") -> int:
    """
    Get recommended max output tokens based on model and task type.

    Args:
        model_name: Nome do modelo
        task_type: Tipo de tarefa (extraction, chat, jira, canvas)

    Returns:
        Número recomendado de tokens de saída
    """
    _, max_output = get_model_limits(model_name)

    # Ajusta baseado no tipo de tarefa
    # Reasoning models precisam de mais tokens para raciocínio
    if is_reasoning_model(model_name):
        task_ratios = {
            "extraction": 0.5,  # Extração precisa de mais tokens para raciocínio
            "chat": 0.6,  # Chat - resposta média
            "jira": 0.7,  # Jira export - resposta maior
            "canvas": 0.8,  # Canvas - resposta muito grande
            "default": 0.6,
        }
    else:
        task_ratios = {
            "extraction": 0.3,  # Extração de estado - resposta menor
            "chat": 0.5,  # Chat - resposta média
            "jira": 0.6,  # Jira export - resposta maior
            "canvas": 0.7,  # Canvas - resposta muito grande
            "default": 0.5,
        }

    ratio = task_ratios.get(task_type, task_ratios["default"])
    return int(max_output * ratio)
