"""
LLM Client interface for the Metadata Code Extractor.

This module provides a unified interface for interacting with various LLM providers,
including support for chat completions, text generation, embeddings, and caching.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from metadata_code_extractor.core.models.llm_models import (
    ChatMessage,
    EmbeddingConfig,
    EmbeddingResponse,
    LLMResponse,
    MessageRole,
    ModelConfig,
)


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMProviderError(LLMClientError):
    """Exception raised when there's an error with the LLM provider."""
    pass


class LLMCacheError(LLMClientError):
    """Exception raised when there's an error with the LLM cache."""
    pass


class LLMProviderAdapter(ABC):
    """Abstract base class for LLM provider adapters."""
    
    @abstractmethod
    async def get_chat_completion(
        self, 
        messages: List[ChatMessage], 
        config: ModelConfig
    ) -> LLMResponse:
        """Get a chat completion from the LLM provider."""
        pass
    
    @abstractmethod
    async def generate_embeddings(
        self, 
        texts: List[str], 
        config: EmbeddingConfig
    ) -> EmbeddingResponse:
        """Generate embeddings for the given texts."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class LLMClient:
    """
    Main LLM client interface for interacting with various LLM providers.
    
    Provides a unified interface for chat completions, text generation, and embeddings
    with support for caching and multiple provider adapters.
    """
    
    def __init__(
        self, 
        provider_adapter: Optional[LLMProviderAdapter] = None,
        cache: Optional[Any] = None
    ):
        """
        Initialize the LLM client.
        
        Args:
            provider_adapter: The provider adapter to use for LLM operations
            cache: Optional cache implementation for storing responses
        """
        self.provider_adapter = provider_adapter
        self.cache = cache
    
    async def get_chat_completion(
        self, 
        messages: List[ChatMessage], 
        config: ModelConfig
    ) -> LLMResponse:
        """
        Get a chat completion from the LLM provider.
        
        Args:
            messages: List of chat messages
            config: Model configuration
            
        Returns:
            LLM response
            
        Raises:
            LLMProviderError: If the provider is unavailable or returns an error
            LLMClientError: If messages list is empty
        """
        if not messages:
            raise LLMClientError("Messages cannot be empty")
        
        if not self.provider_adapter:
            raise LLMProviderError("No provider adapter configured")
        
        # Check if provider is available
        if not await self.provider_adapter.is_available():
            raise LLMProviderError("Provider is not available")
        
        # Check cache if available
        if self.cache:
            cache_key = self._generate_cache_key(messages, config)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                return cached_response
        
        # Get response from provider
        response = await self.provider_adapter.get_chat_completion(messages, config)
        
        # Cache the response if cache is available
        if self.cache:
            cache_key = self._generate_cache_key(messages, config)
            self.cache.set(cache_key, response)
        
        return response
    
    async def generate_text(
        self, 
        prompt: str, 
        config: ModelConfig
    ) -> LLMResponse:
        """
        Generate text from a prompt using the LLM provider.
        
        This is a convenience method that converts a text prompt to chat messages
        and calls get_chat_completion.
        
        Args:
            prompt: Text prompt
            config: Model configuration
            
        Returns:
            LLM response
            
        Raises:
            LLMProviderError: If the provider is unavailable or returns an error
            LLMClientError: If prompt is empty
        """
        if not prompt.strip():
            raise LLMClientError("Prompt cannot be empty")
        
        # Convert text prompt to chat messages
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        
        return await self.get_chat_completion(messages, config)
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        config: EmbeddingConfig
    ) -> EmbeddingResponse:
        """
        Generate embeddings for the given texts.
        
        Args:
            texts: List of texts to generate embeddings for
            config: Embedding configuration
            
        Returns:
            Embedding response
            
        Raises:
            LLMProviderError: If the provider is unavailable or returns an error
            LLMClientError: If texts list is empty
        """
        if not texts:
            raise LLMClientError("Texts cannot be empty")
        
        if not self.provider_adapter:
            raise LLMProviderError("No provider adapter configured")
        
        # Check if provider is available
        if not await self.provider_adapter.is_available():
            raise LLMProviderError("Provider is not available")
        
        # Check cache if available
        if self.cache:
            cache_key = self._generate_cache_key(texts, config)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                return cached_response
        
        # Get response from provider
        response = await self.provider_adapter.generate_embeddings(texts, config)
        
        # Cache the response if cache is available
        if self.cache:
            cache_key = self._generate_cache_key(texts, config)
            self.cache.set(cache_key, response)
        
        return response
    
    def _generate_cache_key(
        self, 
        data: Union[List[ChatMessage], List[str]], 
        config: Union[ModelConfig, EmbeddingConfig]
    ) -> str:
        """
        Generate a cache key for the given data and configuration.
        
        Args:
            data: Input data (messages or texts)
            config: Model or embedding configuration
            
        Returns:
            Cache key string
        """
        # Convert data to a serializable format
        if isinstance(data, list) and data and isinstance(data[0], ChatMessage):
            # Handle chat messages
            data_dict = [msg.model_dump() for msg in data]
        else:
            # Handle list of strings
            data_dict = data
        
        # Create a dictionary with all relevant data
        cache_data = {
            "data": data_dict,
            "config": config.model_dump(),
            "timestamp": int(time.time() / 3600)  # Hour-based cache key
        }
        
        # Generate hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest() 