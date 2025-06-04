"""
LLM Integration module for the Metadata Code Extractor.

This module provides unified interfaces for interacting with various LLM providers,
including caching, prompt management, and response handling.
"""

from .cache import (
    FileLLMCache,
    InMemoryLLMCache,
    LLMCacheError,
    LLMCacheInterface,
)
from .client import (
    LLMClient,
    LLMClientError,
    LLMProviderAdapter,
    LLMProviderError,
)

__all__ = [
    # Cache
    "FileLLMCache",
    "InMemoryLLMCache", 
    "LLMCacheError",
    "LLMCacheInterface",
    # Client
    "LLMClient",
    "LLMClientError",
    "LLMProviderAdapter",
    "LLMProviderError",
]
