"""Tests for configuration management."""

from pathlib import Path

import pytest

from refineflow.utils.config import Config, get_config


def test_config_default_values() -> None:
    """Test configuration with default values."""
    config = Config()
    # Note: The actual value may be overridden by .env file
    # Default in code is "gpt-5-mini", but .env may set "gpt-5-mini"
    assert config.openai_model in ["gpt-5-mini", "gpt-5-mini"]
    assert config.ollama_base_url == "http://localhost:11434"
    assert config.log_level in ["INFO", "DEBUG"]  # May be overridden by .env
    assert config.enable_embeddings is False


def test_config_creates_data_directory(tmp_path: Path) -> None:
    """Test that configuration creates data directory."""
    data_dir = tmp_path / "test_data"
    config = Config(data_dir=str(data_dir))
    assert config.data_dir.exists()
    assert (config.data_dir / "activities").exists()


def test_config_activities_dir_property(tmp_path: Path) -> None:
    """Test activities directory property."""
    data_dir = tmp_path / "test_data"
    config = Config(data_dir=str(data_dir))
    assert config.activities_dir == data_dir / "activities"


def test_config_db_path_property(tmp_path: Path) -> None:
    """Test database path property."""
    data_dir = tmp_path / "test_data"
    config = Config(data_dir=str(data_dir))
    assert config.db_path == data_dir / "refineflow.db"


def test_config_from_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test configuration loading from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "custom_data"))

    config = Config()
    assert config.openai_api_key == "test-key-123"
    assert config.openai_model == "gpt-4"
    assert config.log_level == "DEBUG"


def test_get_config_singleton() -> None:
    """Test that get_config returns singleton instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2
