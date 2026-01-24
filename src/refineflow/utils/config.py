"""Configuration management for RefineFlow."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-5-mini", description="OpenAI model name")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    ollama_embedding_model: str = Field(
        default="snowflake-arctic-embed", description="Ollama embedding model"
    )
    enable_embeddings: bool = Field(default=False, description="Enable embeddings/RAG features")

    # Application Configuration
    data_dir: Path = Field(default=Path("./data"), description="Data directory path")
    log_level: str = Field(default="INFO", description="Logging level")

    def __init__(self, **kwargs: object) -> None:
        """Initialize configuration and create data directory."""
        super().__init__(**kwargs)
        self.data_dir = Path(self.data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "activities").mkdir(exist_ok=True)

    @property
    def activities_dir(self) -> Path:
        """Get activities directory path."""
        return self.data_dir / "activities"

    @property
    def db_path(self) -> Path:
        """Get SQLite database path."""
        return self.data_dir / "refineflow.db"


_config: Config | None = None


def get_config() -> Config:
    """Get or create configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset configuration instance (useful for testing)."""
    global _config
    _config = None
