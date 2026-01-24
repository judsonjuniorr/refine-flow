"""OpenAI client wrapper with LangChain integration."""

from openai import OpenAI
from openai.types.chat import ChatCompletion

from refineflow.utils.config import get_config
from refineflow.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API client."""

    def __init__(self) -> None:
        """Initialize OpenAI client."""
        self.config = get_config()
        self.client: OpenAI | None = None

        if self.config.openai_api_key:
            self.client = OpenAI(api_key=self.config.openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not configured")

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.client is not None

    def complete(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """
        Generate completion for a prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if not self.client:
            logger.error("OpenAI client not available")
            return ""

        try:
            # Detectar modelos de reasoning (o1, o1-mini, o1-preview)
            # que não suportam temperature customizado
            is_reasoning_model = any(
                model_name in self.config.openai_model.lower()
                for model_name in ["o1", "o-1", "gpt-5-mini"]
            )

            # Preparar parâmetros base
            params = {
                "model": self.config.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": max_tokens,
            }

            # Apenas adicionar temperature se não for modelo de reasoning
            if not is_reasoning_model:
                params["temperature"] = temperature

            logger.debug(f"Calling OpenAI with model: {self.config.openai_model}")
            response: ChatCompletion = self.client.chat.completions.create(**params)

            # Debug: log da resposta completa em JSON
            logger.debug(f"Full OpenAI response: {response.model_dump_json(indent=2)}")
            logger.debug(f"Response finish_reason: {response.choices[0].finish_reason}")
            logger.debug(f"Response role: {response.choices[0].message.role}")
            logger.debug(f"Response content type: {type(response.choices[0].message.content)}")

            content = response.choices[0].message.content or ""

            if not content:
                logger.warning(
                    f"Empty response from OpenAI. Model: {self.config.openai_model}, "
                    f"Finish reason: {response.choices[0].finish_reason}, "
                    f"Usage: {response.usage}, "
                    f"Full message object: {response.choices[0].message}"
                )
            else:
                logger.info(
                    f"Generated {len(content)} chars from OpenAI "
                    f"(tokens: {response.usage.completion_tokens if response.usage else 'N/A'})"
                )

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""
