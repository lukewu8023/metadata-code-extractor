"""
Configuration management for the Metadata Code Extractor.

Handles loading configuration from multiple sources with proper precedence:
1. Default values (lowest precedence)
2. Configuration files
3. Environment variables (highest precedence)
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from metadata_code_extractor.core.models.config_models import AppConfig

logger = logging.getLogger(__name__)

# Global configuration instance
_config: Optional[AppConfig] = None


class ConfigLoader:
    """Loads configuration from multiple sources with proper precedence."""
    
    ENV_PREFIX = "MCE_"
    
    def __init__(self):
        """Initialize the configuration loader."""
        pass
    
    def load(self, config_file: Optional[str] = None) -> AppConfig:
        """
        Load configuration from multiple sources.
        
        Args:
            config_file: Optional path to configuration file
            
        Returns:
            Validated AppConfig instance
            
        Raises:
            ValidationError: If configuration validation fails
        """
        # Start with default configuration
        config_dict = {}
        
        # Load from file if provided and exists
        if config_file and Path(config_file).exists():
            try:
                file_config = self._load_from_file(config_file)
                config_dict = self._merge_dicts(config_dict, file_config)
                logger.info(f"Loaded configuration from file: {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file {config_file}: {e}")
                raise
        elif config_file:
            logger.warning(f"Config file not found: {config_file}, using defaults")
        
        # Load from environment variables (highest precedence)
        env_config = self._load_from_env()
        if env_config:
            config_dict = self._merge_dicts(config_dict, env_config)
            logger.info("Loaded configuration from environment variables")
        
        # Create and validate configuration
        try:
            if config_dict:
                config = AppConfig.model_validate(config_dict)
            else:
                config = AppConfig()  # Use all defaults
            
            logger.info("Configuration loaded and validated successfully")
            return config
            
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _load_from_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                return config_data or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to read config file: {e}")
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Get all environment variables with our prefix
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(self.ENV_PREFIX)}
        
        for env_key, env_value in env_vars.items():
            # Remove prefix and convert to lowercase
            key_path = env_key[len(self.ENV_PREFIX):].lower()
            
            # Convert environment variable to nested dict structure
            self._set_nested_value(config, key_path, env_value)
        
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: str):
        """Set a nested value in config dict from underscore-separated key path."""
        # Map known configuration paths to their correct structure
        path_mappings = {
            'llm_default_provider': ['llm', 'default_provider'],
            'llm_default_model_name': ['llm', 'default_model_name'],
            'llm_default_embedding_model_name': ['llm', 'default_embedding_model_name'],
            'llm_cache_enabled': ['llm', 'cache_enabled'],
            'llm_model_params_temperature': ['llm', 'model_params', 'temperature'],
            'llm_model_params_max_tokens': ['llm', 'model_params', 'max_tokens'],
            'llm_providers': ['llm', 'providers'],
            'graph_db_type': ['graph_db', 'db_type'],
            'graph_db_uri': ['graph_db', 'uri'],
            'graph_db_username': ['graph_db', 'username'],
            'graph_db_password': ['graph_db', 'password'],
            'graph_db_database_name': ['graph_db', 'database_name'],
            'vector_db_type': ['vector_db', 'db_type'],
            'vector_db_path': ['vector_db', 'path'],
            'vector_db_collection_name': ['vector_db', 'collection_name'],
            'scan_paths_code_repositories': ['scan_paths', 'code_repositories'],
            'scan_paths_documentation_sources': ['scan_paths', 'documentation_sources'],
            'log_level': ['log_level'],
        }
        
        # Check if we have a specific mapping for this path
        if key_path in path_mappings:
            keys = path_mappings[key_path]
        else:
            # Handle nested provider configurations like llm_providers_openai_api_key
            if key_path.startswith('llm_providers_'):
                parts = key_path.split('_')
                if len(parts) >= 4:  # llm_providers_<provider>_<field>
                    provider_name = parts[2]
                    field_name = '_'.join(parts[3:])  # Join remaining parts for compound field names
                    keys = ['llm', 'providers', provider_name, field_name]
                else:
                    # Fallback to simple split
                    keys = key_path.split('_')
            else:
                # Fallback to simple split for unknown paths
                keys = key_path.split('_')
        
        # Navigate/create nested structure
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # If we encounter a non-dict value, convert it to dict
                current[key] = {}
            current = current[key]
        
        # Set the final value with type conversion
        final_key = keys[-1]
        current[final_key] = self._convert_env_value(value)
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Try to convert to appropriate type
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result


def get_config() -> AppConfig:
    """
    Get the global configuration instance.
    
    Returns:
        The global AppConfig instance
        
    Raises:
        RuntimeError: If configuration has not been initialized
    """
    global _config
    if _config is None:
        raise RuntimeError(
            "Configuration not initialized. Call setup_config() first."
        )
    return _config


def setup_config(config_file: Optional[str] = None) -> AppConfig:
    """
    Initialize the global configuration.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        The initialized AppConfig instance
    """
    global _config
    loader = ConfigLoader()
    _config = loader.load(config_file=config_file)
    return _config


def reset_config():
    """Reset the global configuration (mainly for testing)."""
    global _config
    _config = None 