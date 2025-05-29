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
        """
        Test default values for LLM provider config.
        
        Purpose: Verify that LLMProviderConfig initializes with correct default values
        when no parameters are provided, ensuring safe fallback behavior.
        
        Checkpoints:
        - Default provider_name is "mock"
        - Default api_key is None (no API key required for mock)
        - Default base_url is None (uses provider's default endpoint)
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - LLMProviderConfig Pydantic model
        
        Notes: The "mock" provider is used as default to ensure tests can run
        without requiring actual API credentials or external service dependencies.
        """
        config = LLMProviderConfig()
        assert config.provider_name == "mock"
        assert config.api_key is None
        assert config.base_url is None

    def test_valid_provider_names(self):
        """
        Test valid provider names are accepted.
        
        Purpose: Verify that all supported LLM provider names are accepted by the
        validation system, ensuring the enum constraint works correctly.
        
        Checkpoints:
        - "openai" provider name is accepted
        - "anthropic" provider name is accepted  
        - "azure_openai" provider name is accepted
        - "mock" provider name is accepted
        - All providers create valid config instances
        
        Mocks: None - tests actual Pydantic validation
        
        Dependencies:
        - LLMProviderConfig Pydantic model with provider name validation
        
        Notes: This test ensures that the provider name validation is working
        and that all intended providers are supported. Adding new providers
        requires updating both the model and this test.
        """
        valid_providers = ["openai", "anthropic", "azure_openai", "mock"]
        for provider in valid_providers:
            config = LLMProviderConfig(provider_name=provider)
            assert config.provider_name == provider

    def test_invalid_provider_name(self):
        """
        Test invalid provider names are rejected.
        
        Purpose: Verify that the validation system properly rejects unsupported
        provider names, preventing configuration errors at runtime.
        
        Checkpoints:
        - Invalid provider name raises ValidationError
        - Error occurs during model instantiation
        - System prevents invalid configuration states
        
        Mocks: None - tests actual Pydantic validation behavior
        
        Dependencies:
        - LLMProviderConfig Pydantic model
        - pytest for exception testing
        - Pydantic ValidationError
        
        Notes: This test ensures that typos or unsupported providers are caught
        early during configuration loading rather than causing runtime failures.
        """
        with pytest.raises(ValidationError):
            LLMProviderConfig(provider_name="invalid_provider")

    def test_with_api_key(self):
        """
        Test configuration with API key.
        
        Purpose: Verify that LLMProviderConfig can store and retrieve API keys
        correctly for providers that require authentication.
        
        Checkpoints:
        - API key is stored correctly
        - Provider name is set correctly
        - Configuration remains valid with API key
        
        Mocks: None - tests actual model field assignment
        
        Dependencies:
        - LLMProviderConfig Pydantic model
        
        Notes: API keys are sensitive data, so this test ensures they can be
        properly configured while maintaining model validation.
        """
        config = LLMProviderConfig(
            provider_name="openai",
            api_key="test-key-123"
        )
        assert config.provider_name == "openai"
        assert config.api_key == "test-key-123"

    def test_with_base_url(self):
        """
        Test configuration with custom base URL.
        
        Purpose: Verify that LLMProviderConfig can handle custom base URLs for
        providers, enabling use of proxy services or alternative endpoints.
        
        Checkpoints:
        - Custom base_url is stored as HttpUrl type
        - URL validation occurs during assignment
        - Provider configuration supports endpoint customization
        
        Mocks: None - tests actual Pydantic URL validation
        
        Dependencies:
        - LLMProviderConfig Pydantic model
        - Pydantic HttpUrl validation
        
        Notes: This is important for using services like OpenRouter that provide
        OpenAI-compatible APIs at different endpoints.
        """
        config = LLMProviderConfig(
            provider_name="openai",
            base_url="https://api.openrouter.ai/api/v1"
        )
        assert str(config.base_url) == "https://api.openrouter.ai/api/v1"


class TestModelParams:
    """Test model parameters configuration."""

    def test_default_values(self):
        """
        Test default model parameters.
        
        Purpose: Verify that ModelParams initializes with sensible default values
        for temperature and max_tokens that work well for most use cases.
        
        Checkpoints:
        - Default temperature is 0.7 (balanced creativity/consistency)
        - Default max_tokens is 1024 (reasonable response length)
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - ModelParams Pydantic model
        
        Notes: These defaults are chosen to provide good general-purpose behavior
        for most LLM interactions while being conservative on token usage.
        """
        params = ModelParams()
        assert params.temperature == 0.7
        assert params.max_tokens == 1024

    def test_custom_values(self):
        """
        Test custom model parameters.
        
        Purpose: Verify that ModelParams accepts custom values for temperature
        and max_tokens, allowing fine-tuning of model behavior.
        
        Checkpoints:
        - Custom temperature value is stored correctly
        - Custom max_tokens value is stored correctly
        - Model accepts valid parameter ranges
        
        Mocks: None - tests actual model field assignment
        
        Dependencies:
        - ModelParams Pydantic model
        
        Notes: This test ensures users can customize model behavior for specific
        use cases, such as more deterministic output (lower temperature) or
        longer responses (higher max_tokens).
        """
        params = ModelParams(temperature=0.1, max_tokens=2048)
        assert params.temperature == 0.1
        assert params.max_tokens == 2048

    def test_temperature_validation(self):
        """
        Test temperature validation (should be between 0 and 2).
        
        Purpose: Verify that temperature parameter validation enforces the valid
        range (0.0 to 2.0) as required by most LLM providers.
        
        Checkpoints:
        - Temperature 0.0 is accepted (minimum valid value)
        - Temperature 1.0 is accepted (common middle value)
        - Temperature 2.0 is accepted (maximum valid value)
        - Temperature -0.1 is rejected (below minimum)
        - Temperature 2.1 is rejected (above maximum)
        
        Mocks: None - tests actual Pydantic validation constraints
        
        Dependencies:
        - ModelParams Pydantic model with temperature validation
        - pytest for exception testing
        - Pydantic ValidationError
        
        Notes: Temperature controls randomness in LLM outputs. Values outside
        0-2 range are typically not supported by LLM APIs and could cause errors.
        """
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
        """
        Test max_tokens validation (should be positive).
        
        Purpose: Verify that max_tokens parameter validation enforces positive
        values, preventing invalid token limits that would cause API errors.
        
        Checkpoints:
        - max_tokens 1 is accepted (minimum positive value)
        - max_tokens 100000 is accepted (large valid value)
        - max_tokens 0 is rejected (not positive)
        - max_tokens -1 is rejected (negative value)
        
        Mocks: None - tests actual Pydantic validation constraints
        
        Dependencies:
        - ModelParams Pydantic model with max_tokens validation
        - pytest for exception testing
        - Pydantic ValidationError
        
        Notes: max_tokens must be positive as it represents the maximum number
        of tokens the model can generate. Zero or negative values are meaningless
        and would cause API failures.
        """
        ModelParams(max_tokens=1)
        ModelParams(max_tokens=100000)
        
        with pytest.raises(ValidationError):
            ModelParams(max_tokens=0)
        with pytest.raises(ValidationError):
            ModelParams(max_tokens=-1)


class TestLLMSettings:
    """Test LLM settings configuration."""

    def test_default_values(self):
        """
        Test default LLM settings.
        
        Purpose: Verify that LLMSettings initializes with appropriate default values
        that enable the system to function without external dependencies.
        
        Checkpoints:
        - Default provider is "mock" (no external API required)
        - Default model names use mock variants
        - Mock provider is included in providers dict
        - Default model parameters are reasonable
        - Cache is enabled by default for performance
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - LLMSettings Pydantic model
        - ModelParams for nested validation
        
        Notes: Mock defaults ensure the system can run in development and testing
        environments without requiring API keys or external service access.
        """
        settings = LLMSettings()
        assert settings.default_provider == "mock"
        assert settings.default_model_name == "mock-model"
        assert settings.default_embedding_model_name == "mock-embedding-model"
        assert "mock" in settings.providers
        assert settings.model_params.temperature == 0.7
        assert settings.cache_enabled is True

    def test_custom_provider_config(self):
        """
        Test custom provider configuration.
        
        Purpose: Verify that LLMSettings can be configured with custom providers
        and that the provider configuration is properly stored and accessible.
        
        Checkpoints:
        - Custom default_provider is set correctly
        - Custom provider configuration is stored in providers dict
        - Provider-specific settings (API key) are preserved
        
        Mocks: None - tests actual model configuration
        
        Dependencies:
        - LLMSettings Pydantic model
        - LLMProviderConfig for provider-specific settings
        
        Notes: This test ensures that real LLM providers can be configured
        with their specific settings like API keys and custom endpoints.
        """
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
        """
        Test default Graph DB configuration.
        
        Purpose: Verify that GraphDBConnectionConfig initializes with default values
        that enable local development without external database dependencies.
        
        Checkpoints:
        - Default db_type is "sqlite_graph_mock" (local, no setup required)
        - Default URI points to local SQLite file
        - Optional fields (username, password, database_name) are None
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - GraphDBConnectionConfig Pydantic model
        
        Notes: SQLite mock default enables immediate development without requiring
        Neo4j installation or configuration. The temp file approach prevents
        test pollution between runs.
        """
        config = GraphDBConnectionConfig()
        assert config.db_type == "sqlite_graph_mock"
        assert config.uri == "sqlite:///./temp_graph.db"
        assert config.username is None
        assert config.password is None
        assert config.database_name is None

    def test_neo4j_config(self):
        """
        Test Neo4j configuration.
        
        Purpose: Verify that GraphDBConnectionConfig can be configured for Neo4j
        with all required connection parameters for production use.
        
        Checkpoints:
        - Neo4j db_type is accepted
        - Bolt URI format is stored correctly
        - Authentication credentials are preserved
        - Database name is configurable
        
        Mocks: None - tests actual model field assignment
        
        Dependencies:
        - GraphDBConnectionConfig Pydantic model
        
        Notes: This test ensures production Neo4j deployments can be properly
        configured with authentication and specific database targeting.
        """
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
        """
        Test invalid database type is rejected.
        
        Purpose: Verify that only supported database types are accepted,
        preventing configuration errors for unsupported databases.
        
        Checkpoints:
        - Invalid db_type raises ValidationError
        - Validation occurs during model instantiation
        - Supported database types are enforced
        
        Mocks: None - tests actual Pydantic validation
        
        Dependencies:
        - GraphDBConnectionConfig Pydantic model
        - pytest for exception testing
        - Pydantic ValidationError
        
        Notes: This prevents runtime errors that would occur when trying to
        connect to unsupported database types.
        """
        with pytest.raises(ValidationError):
            GraphDBConnectionConfig(db_type="invalid_db")


class TestVectorDBConnectionConfig:
    """Test Vector DB connection configuration."""

    def test_default_values(self):
        """
        Test default Vector DB configuration.
        
        Purpose: Verify that VectorDBConnectionConfig initializes with default values
        that enable local development without external vector database setup.
        
        Checkpoints:
        - Default db_type is "mock" (no external dependencies)
        - Default path is "temp_vector_db" (local temporary storage)
        - Default collection name is descriptive and consistent
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - VectorDBConnectionConfig Pydantic model
        
        Notes: Mock default enables immediate development and testing without
        requiring ChromaDB or other vector database installation.
        """
        config = VectorDBConnectionConfig()
        assert config.db_type == "mock"
        assert str(config.path) == "temp_vector_db"
        assert config.collection_name == "metadata_embeddings"

    def test_chromadb_config(self):
        """
        Test ChromaDB configuration.
        
        Purpose: Verify that VectorDBConnectionConfig can be configured for ChromaDB
        with custom path and collection settings for production use.
        
        Checkpoints:
        - ChromaDB db_type is accepted
        - Custom path is stored correctly as Path object
        - Custom collection name is preserved
        
        Mocks: None - tests actual model field assignment
        
        Dependencies:
        - VectorDBConnectionConfig Pydantic model
        - pathlib.Path for path handling
        
        Notes: This test ensures production ChromaDB deployments can be configured
        with appropriate storage locations and collection organization.
        """
        config = VectorDBConnectionConfig(
            db_type="chromadb",
            path="./chroma_db",
            collection_name="test_collection"
        )
        assert config.db_type == "chromadb"
        assert str(config.path) == "chroma_db"
        assert config.collection_name == "test_collection"

    def test_invalid_db_type(self):
        """
        Test invalid database type is rejected.
        
        Purpose: Verify that only supported vector database types are accepted,
        preventing configuration errors for unsupported databases.
        
        Checkpoints:
        - Invalid db_type raises ValidationError
        - Validation occurs during model instantiation
        - Supported vector database types are enforced
        
        Mocks: None - tests actual Pydantic validation
        
        Dependencies:
        - VectorDBConnectionConfig Pydantic model
        - pytest for exception testing
        - Pydantic ValidationError
        
        Notes: This prevents runtime errors when attempting to connect to
        unsupported vector database types.
        """
        with pytest.raises(ValidationError):
            VectorDBConnectionConfig(db_type="invalid_db")


class TestScanPathsConfig:
    """Test scan paths configuration."""

    def test_default_values(self):
        """
        Test default scan paths.
        
        Purpose: Verify that ScanPathsConfig initializes with empty lists,
        requiring explicit configuration of paths to scan.
        
        Checkpoints:
        - Default code_repositories is empty list
        - Default documentation_sources is empty list
        - No paths are scanned by default (explicit configuration required)
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - ScanPathsConfig Pydantic model
        
        Notes: Empty defaults prevent accidental scanning of unintended directories
        and require users to explicitly specify what should be analyzed.
        """
        config = ScanPathsConfig()
        assert config.code_repositories == []
        assert config.documentation_sources == []

    def test_with_paths(self):
        """
        Test configuration with paths.
        
        Purpose: Verify that ScanPathsConfig can store multiple paths for both
        code repositories and documentation sources.
        
        Checkpoints:
        - Multiple code repository paths are stored correctly
        - Multiple documentation source paths are stored correctly
        - Both local paths and URLs are supported for documentation
        - List lengths match expected values
        
        Mocks: None - tests actual model field assignment
        
        Dependencies:
        - ScanPathsConfig Pydantic model
        
        Notes: This test ensures the system can handle multiple source locations
        and different types of documentation sources (local and remote).
        """
        config = ScanPathsConfig(
            code_repositories=["./src", "./lib"],
            documentation_sources=["./docs", "https://example.com/docs"]
        )
        assert len(config.code_repositories) == 2
        assert len(config.documentation_sources) == 2


class TestAppConfig:
    """Test main application configuration."""

    def test_default_values(self):
        """
        Test default application configuration.
        
        Purpose: Verify that AppConfig initializes with all subsystem defaults
        that enable the application to run without external dependencies.
        
        Checkpoints:
        - LLM subsystem uses mock provider by default
        - Graph DB uses SQLite mock by default
        - Vector DB uses mock by default
        - Scan paths are empty (explicit configuration required)
        - Log level is INFO (appropriate for production)
        
        Mocks: None - tests actual Pydantic model defaults
        
        Dependencies:
        - AppConfig Pydantic model
        - All subsystem configuration models
        
        Notes: These defaults enable immediate development and testing while
        requiring explicit configuration for production deployments.
        """
        config = AppConfig()
        assert config.llm.default_provider == "mock"
        assert config.graph_db.db_type == "sqlite_graph_mock"
        assert config.vector_db.db_type == "mock"
        assert config.scan_paths.code_repositories == []
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """
        Test custom application configuration.
        
        Purpose: Verify that AppConfig can be configured with custom settings
        for all subsystems, enabling production deployments.
        
        Checkpoints:
        - Custom LLM provider configuration is preserved
        - Custom graph DB configuration is preserved
        - Custom vector DB configuration is preserved
        - Custom log level is preserved
        - All subsystems can be configured simultaneously
        
        Mocks: None - tests actual model composition
        
        Dependencies:
        - AppConfig Pydantic model
        - All subsystem configuration models
        
        Notes: This test ensures production configurations can override all
        default settings with appropriate values for each subsystem.
        """
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
        """
        Test configuration serialization to dict.
        
        Purpose: Verify that AppConfig can be serialized to a dictionary format,
        enabling configuration export, debugging, and API responses.
        
        Checkpoints:
        - model_dump() returns a dictionary
        - All major configuration sections are present in output
        - Serialization preserves configuration structure
        
        Mocks: None - tests actual Pydantic serialization
        
        Dependencies:
        - AppConfig Pydantic model
        - Pydantic model_dump() method
        
        Notes: Serialization is important for configuration debugging, API
        responses, and integration with external configuration management systems.
        """
        config = AppConfig()
        config_dict = config.model_dump()
        
        assert isinstance(config_dict, dict)
        assert "llm" in config_dict
        assert "graph_db" in config_dict
        assert "vector_db" in config_dict
        assert "scan_paths" in config_dict
        assert "log_level" in config_dict

    def test_deserialization(self):
        """
        Test configuration deserialization from dict.
        
        Purpose: Verify that AppConfig can be created from a dictionary,
        enabling configuration loading from JSON/YAML files and APIs.
        
        Checkpoints:
        - model_validate() creates valid AppConfig from dict
        - Complex nested configuration is properly deserialized
        - All configuration values are preserved during round-trip
        - Provider-specific settings are maintained
        
        Mocks: None - tests actual Pydantic deserialization
        
        Dependencies:
        - AppConfig Pydantic model
        - Pydantic model_validate() method
        
        Notes: Deserialization is crucial for loading configuration from external
        sources like YAML files, environment variables, and configuration APIs.
        This test uses a comprehensive configuration to verify all features work.
        """
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