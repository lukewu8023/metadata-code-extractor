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
        """Test loading default configuration."""
        loader = ConfigLoader()
        config = loader.load()
        
        assert isinstance(config, AppConfig)
        assert config.llm.default_provider == "mock"
        assert config.graph_db.db_type == "sqlite_graph_mock"
        assert config.vector_db.db_type == "mock"
        assert config.log_level == "INFO"

    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
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
        """Test loading configuration from environment variables."""
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
        """Test that environment variables take precedence over config files."""
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
        """Test handling of invalid configuration file."""
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
        """Test handling of nonexistent configuration file."""
        loader = ConfigLoader()
        # Should not raise error, just use defaults
        config = loader.load(config_file="/nonexistent/config.yaml")
        assert config.llm.default_provider == "mock"

    def test_partial_config_file(self):
        """Test loading partial configuration from file."""
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
        """Test mapping of nested environment variables."""
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
        """Test handling of validation errors in configuration."""
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