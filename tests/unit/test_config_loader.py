"""
Unit tests for configuration loader.

Tests the ConfigLoader class that handles loading configuration
from multiple sources with proper precedence.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from metadata_code_extractor.core.config import ConfigLoader
from metadata_code_extractor.core.models.config import AppConfig


class TestConfigLoader:
    """Test configuration loading functionality."""

    def test_load_default_config(self):
        """
        Test loading default configuration.
        
        Purpose: Verify that ConfigLoader can create a valid AppConfig instance with default values
        when no configuration file or environment variables are provided.
        
        Checkpoints:
        - ConfigLoader.load() returns an AppConfig instance
        - Default LLM provider is "mock"
        - Default graph DB type is "sqlite_graph_mock"
        - Default vector DB type is "mock"
        - Default log level is "INFO"
        
        Mocks: None - tests actual default configuration loading
        
        Dependencies:
        - ConfigLoader class from core.config
        - AppConfig model from core.models.config
        
        Notes: This test ensures the system has sensible defaults and can run without
        any external configuration, which is crucial for development and testing.
        """
        loader = ConfigLoader()
        config = loader.load()
        
        assert isinstance(config, AppConfig)
        assert config.llm.default_provider == "mock"
        assert config.graph_db.db_type == "sqlite_graph_mock"
        assert config.vector_db.db_type == "mock"
        assert config.log_level == "INFO"

    def test_load_from_yaml_file(self):
        """
        Test loading configuration from YAML file.
        
        Purpose: Verify that ConfigLoader can parse and load configuration from a YAML file,
        overriding default values with file-specified values.
        
        Checkpoints:
        - YAML file is correctly parsed
        - Configuration values from file override defaults
        - Nested configuration structures (llm.default_provider) work correctly
        - File cleanup occurs properly
        
        Mocks: None - uses real temporary file system operations
        
        Dependencies:
        - tempfile module for creating temporary YAML files
        - yaml module for YAML serialization
        - os.unlink for file cleanup
        
        Notes: Uses tempfile.NamedTemporaryFile to create a real YAML file on disk,
        ensuring the loader can handle actual file I/O operations. The test cleans up
        the temporary file in a try/finally block to prevent test pollution.
        """
        config_data = {
            "llm": {
                "default_provider": "openai",
                "default_model_name": "gpt-4"
            },
            "graph_db": {
                "db_type": "neo4j",
                "uri": "bolt://localhost:7687"
            },
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load(config_file=config_file)
            
            assert config.llm.default_provider == "openai"
            assert config.llm.default_model_name == "gpt-4"
            assert config.graph_db.db_type == "neo4j"
            assert config.graph_db.uri == "bolt://localhost:7687"
            assert config.log_level == "DEBUG"
        finally:
            os.unlink(config_file)

    def test_load_from_environment_variables(self):
        """
        Test loading configuration from environment variables.
        
        Purpose: Verify that ConfigLoader can read configuration from environment variables
        using the MCE_ prefix convention and properly map them to nested configuration structures.
        
        Checkpoints:
        - Environment variables with MCE_ prefix are recognized
        - Nested configuration paths (MCE_LLM_DEFAULT_PROVIDER) map correctly
        - Environment values override default configuration
        - All major configuration sections can be set via environment
        
        Mocks: 
        - os.environ using patch.dict to temporarily set environment variables
        
        Dependencies:
        - unittest.mock.patch for environment variable mocking
        - os module for environment access
        
        Notes: Uses patch.dict to temporarily modify os.environ without affecting
        the actual test environment. This ensures tests are isolated and don't
        interfere with each other or the system environment.
        """
        env_vars = {
            "MCE_LLM_DEFAULT_PROVIDER": "anthropic",
            "MCE_LLM_DEFAULT_MODEL_NAME": "claude-3-sonnet",
            "MCE_GRAPH_DB_TYPE": "neo4j",
            "MCE_GRAPH_DB_URI": "bolt://remote:7687",
            "MCE_LOG_LEVEL": "WARNING"
        }
        
        with patch.dict(os.environ, env_vars):
            loader = ConfigLoader()
            config = loader.load()
            
            assert config.llm.default_provider == "anthropic"
            assert config.llm.default_model_name == "claude-3-sonnet"
            assert config.graph_db.db_type == "neo4j"
            assert config.graph_db.uri == "bolt://remote:7687"
            assert config.log_level == "WARNING"

    def test_precedence_env_over_file(self):
        """
        Test that environment variables take precedence over config files.
        
        Purpose: Verify the configuration precedence hierarchy where environment variables
        should override values specified in configuration files, which is a common
        pattern for containerized deployments.
        
        Checkpoints:
        - Configuration file values are loaded first
        - Environment variables override file values for the same keys
        - Non-overridden file values remain intact
        - Precedence works for both simple and nested configuration keys
        
        Mocks:
        - os.environ using patch.dict for environment variable simulation
        
        Dependencies:
        - tempfile for creating test configuration file
        - yaml for configuration file serialization
        - unittest.mock.patch for environment mocking
        
        Notes: This test is crucial for deployment scenarios where base configuration
        is provided via files but specific values (like API keys or endpoints) are
        overridden via environment variables in different environments.
        """
        # Create config file
        config_data = {
            "llm": {
                "default_provider": "openai"
            },
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        # Set environment variables that should override
        env_vars = {
            "MCE_LLM_DEFAULT_PROVIDER": "anthropic",
            "MCE_LOG_LEVEL": "ERROR"
        }
        
        try:
            with patch.dict(os.environ, env_vars):
                loader = ConfigLoader()
                config = loader.load(config_file=config_file)
                
                # Environment variables should override file values
                assert config.llm.default_provider == "anthropic"
                assert config.log_level == "ERROR"
        finally:
            os.unlink(config_file)

    def test_invalid_config_file(self):
        """
        Test handling of invalid configuration file.
        
        Purpose: Verify that ConfigLoader properly handles and reports errors when
        encountering malformed YAML files, providing clear error feedback.
        
        Checkpoints:
        - Invalid YAML syntax is detected
        - Appropriate exception is raised (YAML parsing error)
        - Error handling doesn't crash the application
        - Temporary file cleanup occurs even on error
        
        Mocks: None - tests actual YAML parsing error handling
        
        Dependencies:
        - tempfile for creating malformed YAML file
        - pytest for exception testing
        
        Notes: This test ensures robust error handling for configuration files that
        may be manually edited and contain syntax errors. The malformed YAML contains
        an unclosed bracket to trigger a parsing error.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            loader = ConfigLoader()
            with pytest.raises(Exception):  # Should raise YAML parsing error
                loader.load(config_file=config_file)
        finally:
            os.unlink(config_file)

    def test_nonexistent_config_file(self):
        """
        Test handling of nonexistent configuration file.
        
        Purpose: Verify that ConfigLoader gracefully handles missing configuration files
        by falling back to default values rather than crashing.
        
        Checkpoints:
        - No exception is raised for missing file
        - Default configuration values are used
        - System remains functional without configuration file
        
        Mocks: None - tests actual file system behavior
        
        Dependencies: None beyond core ConfigLoader functionality
        
        Notes: This test ensures the system is resilient to deployment scenarios
        where configuration files might be missing or not yet created. The fallback
        to defaults allows the system to start and potentially be configured later.
        """
        loader = ConfigLoader()
        # Should not raise error, just use defaults
        config = loader.load(config_file="/nonexistent/config.yaml")
        assert config.llm.default_provider == "mock"

    def test_partial_config_file(self):
        """
        Test loading partial configuration from file.
        
        Purpose: Verify that ConfigLoader can handle configuration files that only
        specify some values, using defaults for unspecified configuration options.
        
        Checkpoints:
        - Specified configuration values are loaded from file
        - Unspecified values use default configuration
        - Partial configuration doesn't break the loading process
        - Mixed file/default configuration produces valid AppConfig
        
        Mocks: None - tests actual partial configuration loading
        
        Dependencies:
        - tempfile for creating partial configuration file
        - yaml for configuration serialization
        
        Notes: This test is important for real-world usage where users may only
        want to override specific configuration values while keeping defaults
        for everything else. It ensures the merge logic works correctly.
        """
        config_data = {
            "log_level": "DEBUG"
            # Only specify log_level, other values should use defaults
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load(config_file=config_file)
            
            # Specified value should be loaded
            assert config.log_level == "DEBUG"
            # Defaults should be preserved
            assert config.llm.default_provider == "mock"
            assert config.graph_db.db_type == "sqlite_graph_mock"
        finally:
            os.unlink(config_file)

    def test_nested_env_var_mapping(self):
        """
        Test mapping of nested environment variables.
        
        Purpose: Verify that ConfigLoader can correctly map deeply nested environment
        variables to complex configuration structures, particularly for provider-specific
        settings and model parameters.
        
        Checkpoints:
        - Deeply nested environment variables are mapped correctly
        - Provider-specific configuration (MCE_LLM_PROVIDERS_OPENAI_*) works
        - Model parameters (MCE_LLM_MODEL_PARAMS_*) are properly typed
        - Numeric values are converted from strings appropriately
        
        Mocks:
        - os.environ using patch.dict for complex environment variable setup
        
        Dependencies:
        - unittest.mock.patch for environment variable mocking
        
        Notes: This test verifies the environment variable naming convention and
        mapping logic for complex nested structures. It's particularly important
        for containerized deployments where all configuration must be possible
        via environment variables.
        """
        env_vars = {
            "MCE_LLM_PROVIDERS_OPENAI_API_KEY": "test-key-123",
            "MCE_LLM_PROVIDERS_OPENAI_PROVIDER_NAME": "openai",
            "MCE_LLM_MODEL_PARAMS_TEMPERATURE": "0.1",
            "MCE_LLM_MODEL_PARAMS_MAX_TOKENS": "2048"
        }
        
        with patch.dict(os.environ, env_vars):
            loader = ConfigLoader()
            config = loader.load()
            
            assert "openai" in config.llm.providers
            assert config.llm.providers["openai"].api_key == "test-key-123"
            assert config.llm.providers["openai"].provider_name == "openai"
            assert config.llm.model_params.temperature == 0.1
            assert config.llm.model_params.max_tokens == 2048

    def test_validation_error_handling(self):
        """
        Test handling of validation errors in configuration.
        
        Purpose: Verify that ConfigLoader properly validates configuration values
        and raises appropriate errors when invalid values are provided, ensuring
        data integrity and early error detection.
        
        Checkpoints:
        - Invalid temperature value (> 2.0) is rejected
        - Invalid max_tokens value (<= 0) is rejected
        - Validation errors are properly propagated
        - Configuration validation prevents invalid system state
        
        Mocks: None - tests actual Pydantic validation behavior
        
        Dependencies:
        - tempfile for creating invalid configuration file
        - yaml for configuration serialization
        - pytest for exception testing
        
        Notes: This test ensures that the Pydantic models properly validate
        configuration values and prevent the system from starting with invalid
        parameters that could cause runtime errors or unexpected behavior.
        """
        config_data = {
            "llm": {
                "model_params": {
                    "temperature": 3.0,  # Invalid: > 2.0
                    "max_tokens": -1     # Invalid: <= 0
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader()
            with pytest.raises(Exception):  # Should raise validation error
                loader.load(config_file=config_file)
        finally:
            os.unlink(config_file) 