"""
Unit tests for configuration models.

Tests the Pydantic models used for application configuration,
including validation, defaults, and environment variable loading.
"""

import os
import pytest
from pydantic import ValidationError
from metadata_code_extractor.core.models.config import (
    LLMProviderConfig,
    ModelParams,
    LLMSettings,
    GraphDBConnectionConfig,
    VectorDBConnectionConfig,
    ScanPathsConfig,
    AppConfig,
)


class TestLLMProviderConfig:
    """Test LLM provider configuration model."""

    def test_default_values(self):
        """Test default values for LLM provider config."""
        config = LLMProviderConfig()
        assert config.provider_name == "mock"
        assert config.api_key is None
        assert config.base_url is None

    def test_valid_provider_names(self):
        """Test valid provider names are accepted."""
        valid_providers = ["openai", "anthropic", "azure_openai", "mock"]
        for provider in valid_providers:
            config = LLMProviderConfig(provider_name=provider)
            assert config.provider_name == provider

    def test_invalid_provider_name(self):
        """Test invalid provider names are rejected."""
        with pytest.raises(ValidationError):
            LLMProviderConfig(provider_name="invalid_provider")

    def test_with_api_key(self):
        """Test configuration with API key."""
        config = LLMProviderConfig(
            provider_name="openai",
            api_key="test-key-123"
        )
        assert config.provider_name == "openai"
        assert config.api_key == "test-key-123"

    def test_with_base_url(self):
        """Test configuration with custom base URL."""
        config = LLMProviderConfig(
            provider_name="openai",
            base_url="https://api.openrouter.ai/api/v1"
        )
        assert str(config.base_url) == "https://api.openrouter.ai/api/v1"


class TestModelParams:
    """Test model parameters configuration."""

    def test_default_values(self):
        """Test default model parameters."""
        params = ModelParams()
        assert params.temperature == 0.7
        assert params.max_tokens == 1024

    def test_custom_values(self):
        """Test custom model parameters."""
        params = ModelParams(temperature=0.1, max_tokens=2048)
        assert params.temperature == 0.1
        assert params.max_tokens == 2048

    def test_temperature_validation(self):
        """Test temperature validation (should be between 0 and 2)."""
        # Valid temperatures
        ModelParams(temperature=0.0)
        ModelParams(temperature=1.0)
        ModelParams(temperature=2.0)
        
        # Invalid temperatures should raise validation error
        with pytest.raises(ValidationError):
            ModelParams(temperature=-0.1)
        with pytest.raises(ValidationError):
            ModelParams(temperature=2.1)

    def test_max_tokens_validation(self):
        """Test max_tokens validation (should be positive)."""
        ModelParams(max_tokens=1)
        ModelParams(max_tokens=100000)
        
        with pytest.raises(ValidationError):
            ModelParams(max_tokens=0)
        with pytest.raises(ValidationError):
            ModelParams(max_tokens=-1)


class TestLLMSettings:
    """Test LLM settings configuration."""

    def test_default_values(self):
        """Test default LLM settings."""
        settings = LLMSettings()
        assert settings.default_provider == "mock"
        assert settings.default_model_name == "mock-model"
        assert settings.default_embedding_model_name == "mock-embedding-model"
        assert "mock" in settings.providers
        assert settings.model_params.temperature == 0.7
        assert settings.cache_enabled is True

    def test_custom_provider_config(self):
        """Test custom provider configuration."""
        providers = {
            "openai": LLMProviderConfig(
                provider_name="openai",
                api_key="test-key"
            )
        }
        settings = LLMSettings(
            default_provider="openai",
            providers=providers
        )
        assert settings.default_provider == "openai"
        assert settings.providers["openai"].api_key == "test-key"


class TestGraphDBConnectionConfig:
    """Test Graph DB connection configuration."""

    def test_default_values(self):
        """Test default Graph DB configuration."""
        config = GraphDBConnectionConfig()
        assert config.db_type == "sqlite_graph_mock"
        assert config.uri == "sqlite:///./temp_graph.db"
        assert config.username is None
        assert config.password is None
        assert config.database_name is None

    def test_neo4j_config(self):
        """Test Neo4j configuration."""
        config = GraphDBConnectionConfig(
            db_type="neo4j",
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database_name="metadata"
        )
        assert config.db_type == "neo4j"
        assert config.uri == "bolt://localhost:7687"
        assert config.username == "neo4j"
        assert config.password == "password"
        assert config.database_name == "metadata"

    def test_invalid_db_type(self):
        """Test invalid database type is rejected."""
        with pytest.raises(ValidationError):
            GraphDBConnectionConfig(db_type="invalid_db")


class TestVectorDBConnectionConfig:
    """Test Vector DB connection configuration."""

    def test_default_values(self):
        """Test default Vector DB configuration."""
        config = VectorDBConnectionConfig()
        assert config.db_type == "mock"
        assert str(config.path) == "temp_vector_db"
        assert config.collection_name == "metadata_embeddings"

    def test_chromadb_config(self):
        """Test ChromaDB configuration."""
        config = VectorDBConnectionConfig(
            db_type="chromadb",
            path="./chroma_db",
            collection_name="test_collection"
        )
        assert config.db_type == "chromadb"
        assert str(config.path) == "chroma_db"
        assert config.collection_name == "test_collection"

    def test_invalid_db_type(self):
        """Test invalid database type is rejected."""
        with pytest.raises(ValidationError):
            VectorDBConnectionConfig(db_type="invalid_db")


class TestScanPathsConfig:
    """Test scan paths configuration."""

    def test_default_values(self):
        """Test default scan paths."""
        config = ScanPathsConfig()
        assert config.code_repositories == []
        assert config.documentation_sources == []

    def test_with_paths(self):
        """Test configuration with paths."""
        config = ScanPathsConfig(
            code_repositories=["./src", "./lib"],
            documentation_sources=["./docs", "https://example.com/docs"]
        )
        assert len(config.code_repositories) == 2
        assert len(config.documentation_sources) == 2


class TestAppConfig:
    """Test main application configuration."""

    def test_default_values(self):
        """Test default application configuration."""
        config = AppConfig()
        assert config.llm.default_provider == "mock"
        assert config.graph_db.db_type == "sqlite_graph_mock"
        assert config.vector_db.db_type == "mock"
        assert config.scan_paths.code_repositories == []
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """Test custom application configuration."""
        config = AppConfig(
            llm=LLMSettings(default_provider="openai"),
            graph_db=GraphDBConnectionConfig(db_type="neo4j"),
            vector_db=VectorDBConnectionConfig(db_type="chromadb"),
            log_level="DEBUG"
        )
        assert config.llm.default_provider == "openai"
        assert config.graph_db.db_type == "neo4j"
        assert config.vector_db.db_type == "chromadb"
        assert config.log_level == "DEBUG"

    def test_serialization(self):
        """Test configuration serialization to dict."""
        config = AppConfig()
        config_dict = config.model_dump()
        
        assert isinstance(config_dict, dict)
        assert "llm" in config_dict
        assert "graph_db" in config_dict
        assert "vector_db" in config_dict
        assert "scan_paths" in config_dict
        assert "log_level" in config_dict

    def test_deserialization(self):
        """Test configuration deserialization from dict."""
        config_dict = {
            "llm": {
                "default_provider": "openai",
                "default_model_name": "gpt-4",
                "default_embedding_model_name": "text-embedding-ada-002",
                "providers": {
                    "openai": {
                        "provider_name": "openai",
                        "api_key": "test-key"
                    }
                },
                "model_params": {
                    "temperature": 0.1,
                    "max_tokens": 2048
                },
                "cache_enabled": True
            },
            "graph_db": {
                "db_type": "neo4j",
                "uri": "bolt://localhost:7687"
            },
            "vector_db": {
                "db_type": "chromadb",
                "path": "./chroma_db"
            },
            "scan_paths": {
                "code_repositories": ["./src"],
                "documentation_sources": ["./docs"]
            },
            "log_level": "DEBUG"
        }
        
        config = AppConfig.model_validate(config_dict)
        assert config.llm.default_provider == "openai"
        assert config.graph_db.db_type == "neo4j"
        assert config.vector_db.db_type == "chromadb"
        assert config.log_level == "DEBUG" 