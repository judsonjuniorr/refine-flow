"""OpenAI client wrapper with LangChain integration."""

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from refineflow.llm.models import get_max_output_tokens, get_model_limits, is_reasoning_model
from refineflow.utils.config import get_config
from refineflow.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API client with LangChain."""

    def __init__(self) -> None:
        """Initialize OpenAI client."""
        self.config = get_config()
        self.llm: BaseChatModel | None = None
        self.model_name = self.config.openai_model

        if self.config.openai_api_key:
            # Detectar se é modelo de reasoning
            is_reasoning = is_reasoning_model(self.model_name)

            # Configurar parâmetros baseados no modelo
            llm_kwargs = {
                "model": self.model_name,
                "api_key": self.config.openai_api_key,
                "verbose": self.config.log_level == "DEBUG",
            }

            # Modelos de reasoning não aceitam temperature
            if not is_reasoning:
                llm_kwargs["temperature"] = 0.7

            self.llm = ChatOpenAI(**llm_kwargs)

            input_limit, output_limit = get_model_limits(self.model_name)
            logger.info(
                f"LangChain OpenAI client initialized - Model: {self.model_name}, "
                f"Limits: {input_limit} input / {output_limit} output tokens, "
                f"Reasoning: {is_reasoning}"
            )
        else:
            logger.warning("OpenAI API key not configured")

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.llm is not None

    def get_llm(self, task_type: str = "default", **kwargs) -> BaseChatModel | None:
        """
        Get LangChain LLM instance configured for specific task.

        Args:
            task_type: Tipo de tarefa (extraction, chat, jira, canvas)
            **kwargs: Parâmetros adicionais para override

        Returns:
            Configured LLM instance
        """
        if not self.llm:
            return None

        # Calcular max_tokens baseado no tipo de tarefa
        max_tokens = kwargs.pop("max_tokens", None)
        if max_tokens is None:
            max_tokens = get_max_output_tokens(self.model_name, task_type)

        # Configurar parâmetros - usar max_completion_tokens para compatibilidade
        llm_kwargs = {"max_completion_tokens": max_tokens, **kwargs}

        # Remover temperature se for modelo de reasoning
        if is_reasoning_model(self.model_name) and "temperature" in llm_kwargs:
            llm_kwargs.pop("temperature")

        logger.debug(
            f"Creating LLM for task '{task_type}' - max_completion_tokens: {max_tokens}, "
            f"kwargs: {llm_kwargs}"
        )

        return self.llm.bind(**llm_kwargs)

    def complete(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """
        Generate completion for a prompt (legacy method for backwards compatibility).

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if not self.llm:
            logger.error("OpenAI client not available")
            return ""

        try:
            # Configurar parâmetros - usar max_completion_tokens
            kwargs = {"max_completion_tokens": max_tokens}

            # Apenas adicionar temperature se não for modelo de reasoning
            if not is_reasoning_model(self.model_name):
                kwargs["temperature"] = temperature

            logger.debug(f"Calling OpenAI with model: {self.model_name}")

            # Usar LangChain para invocar
            llm = self.llm.bind(**kwargs)
            response = llm.invoke(prompt)

            content = response.content or ""

            # Log detalhado baseado no resultado
            if not content:
                logger.warning(
                    f"Empty response from OpenAI. Model: {self.model_name}, "
                    f"Response metadata: {response.response_metadata}"
                )
            else:
                usage = response.response_metadata.get("token_usage", {})
                logger.info(
                    f"Generated {len(content)} chars from OpenAI "
                    f"(tokens: {usage.get('completion_tokens', 'N/A')})"
                )

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return ""
