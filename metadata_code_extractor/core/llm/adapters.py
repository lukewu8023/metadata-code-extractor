"""
LLM Provider Adapters for the Metadata Code Extractor.

This module provides concrete implementations of the LLMProviderAdapter interface
for different LLM providers including OpenAI (for OpenRouter) and Mock adapters.
"""

import asyncio
import hashlib
import random
import time
from typing import Any, Dict, List, Optional, Union

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from metadata_code_extractor.core.llm.client import LLMProviderAdapter, LLMProviderError
from metadata_code_extractor.core.models.llm_models import (
    ChatMessage,
    EmbeddingConfig,
    EmbeddingResponse,
    LLMResponse,
    MessageRole,
    ModelConfig,
)


class OpenAIAdapter(LLMProviderAdapter):
    """
    OpenAI adapter for LLM operations.
    
    This adapter works with OpenAI API and OpenAI-compatible APIs like OpenRouter.
    """
    
    def __init__(self, client: Optional[Any] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenAI adapter.
        
        Args:
            client: Optional pre-configured OpenAI client
            config: Optional configuration dictionary with API settings
        """
        if client:
            self.client = client
        else:
            if OpenAI is None:
                raise ImportError("OpenAI package is required for OpenAIAdapter. Install with: pip install openai")
            
            if config:
                # Create client with provided configuration
                client_kwargs = {}
                if "api_key" in config:
                    client_kwargs["api_key"] = config["api_key"]
                if "base_url" in config:
                    client_kwargs["base_url"] = config["base_url"]
                if "organization" in config:
                    client_kwargs["organization"] = config["organization"]
                
                self.client = OpenAI(**client_kwargs)
            else:
                # Create client with default configuration (uses environment variables)
                self.client = OpenAI()
    
    async def get_chat_completion(
        self, 
        messages: List[ChatMessage], 
        config: ModelConfig
    ) -> LLMResponse:
        """Get a chat completion from the OpenAI API."""
        try:
            # Convert ChatMessage objects to OpenAI format
            openai_messages = []
            for msg in messages:
                openai_msg = {
                    "role": msg.role,  # MessageRole enum with use_enum_values=True gives us the string directly
                    "content": msg.content
                }
                if msg.name:
                    openai_msg["name"] = msg.name
                if msg.function_call:
                    openai_msg["function_call"] = msg.function_call
                openai_messages.append(openai_msg)
            
            # Prepare API call parameters
            api_params = {
                "model": config.model_name,
                "messages": openai_messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
            
            # Add optional parameters if specified
            if config.top_p is not None:
                api_params["top_p"] = config.top_p
            if config.frequency_penalty is not None:
                api_params["frequency_penalty"] = config.frequency_penalty
            if config.presence_penalty is not None:
                api_params["presence_penalty"] = config.presence_penalty
            if config.stop is not None:
                api_params["stop"] = config.stop
            
            # Make the API call
            response = self.client.chat.completions.create(**api_params)
            
            # Convert response to our format
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}") from e
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        config: EmbeddingConfig
    ) -> EmbeddingResponse:
        """Generate embeddings using the OpenAI API."""
        try:
            # Prepare API call parameters
            api_params = {
                "model": config.model_name,
                "input": texts,
                "encoding_format": config.encoding_format
            }
            
            # Add dimensions if specified
            if config.dimensions is not None:
                api_params["dimensions"] = config.dimensions
            
            # Make the API call
            response = self.client.embeddings.create(**api_params)
            
            # Convert response to our format
            embeddings = [item.embedding for item in response.data]
            
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=response.model,
                usage=usage
            )
            
        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}") from e
    
    async def is_available(self) -> bool:
        """Check if the OpenAI API is available."""
        try:
            # Make a simple test call to check availability
            test_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a basic model for testing
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return test_response is not None
        except Exception:
            return False


class MockAdapter(LLMProviderAdapter):
    """
    Mock adapter for testing and development.
    
    This adapter simulates LLM responses without making actual API calls.
    """
    
    def __init__(self, response_delay: float = 0.1, fail_rate: float = 0.0):
        """
        Initialize the mock adapter.
        
        Args:
            response_delay: Simulated response delay in seconds
            fail_rate: Probability of simulated failures (0.0 to 1.0)
        """
        self.response_delay = response_delay
        self.fail_rate = fail_rate
    
    async def get_chat_completion(
        self, 
        messages: List[ChatMessage], 
        config: ModelConfig
    ) -> LLMResponse:
        """Generate a mock chat completion response."""
        # Simulate response delay
        if self.response_delay > 0:
            await asyncio.sleep(self.response_delay)
        
        # Simulate failures
        if random.random() < self.fail_rate:
            raise LLMProviderError("Simulated failure")
        
        # Generate mock response based on input
        user_messages = [msg.content for msg in messages if msg.role == MessageRole.USER]
        last_user_message = user_messages[-1] if user_messages else "No user message"
        
        mock_content = f"Mock response for: {last_user_message}"
        
        return LLMResponse(
            content=mock_content,
            model=config.model_name,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop"
        )
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        config: EmbeddingConfig
    ) -> EmbeddingResponse:
        """Generate mock embeddings."""
        # Simulate response delay
        if self.response_delay > 0:
            await asyncio.sleep(self.response_delay)
        
        # Simulate failures
        if random.random() < self.fail_rate:
            raise LLMProviderError("Simulated failure")
        
        # Generate deterministic mock embeddings based on text content
        embeddings = []
        for text in texts:
            # Create a deterministic embedding based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convert hash to numbers and normalize to create a 384-dimensional vector
            embedding = []
            for i in range(0, len(text_hash), 2):
                # Take pairs of hex characters and convert to float
                hex_pair = text_hash[i:i+2]
                value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                embedding.append(value)
            
            # Extend to 384 dimensions by repeating the pattern
            while len(embedding) < 384:
                embedding.extend(embedding[:min(len(embedding), 384 - len(embedding))])
            
            embedding = embedding[:384]  # Ensure exactly 384 dimensions
            embeddings.append(embedding)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=config.model_name,
            usage={"prompt_tokens": 5, "total_tokens": 5}
        )
    
    async def is_available(self) -> bool:
        """Mock adapter is always available."""
        return True


def create_adapter(config: Dict[str, Any]) -> LLMProviderAdapter:
    """
    Factory function to create LLM provider adapters.
    
    Args:
        config: Configuration dictionary with provider settings
        
    Returns:
        Configured LLM provider adapter
        
    Raises:
        ValueError: If provider is not specified or unknown
    """
    if "provider" not in config:
        raise ValueError("Provider must be specified in config")
    
    provider = config["provider"].lower()
    
    if provider == "openai":
        # Extract OpenAI-specific config
        openai_config = {}
        if "api_key" in config:
            openai_config["api_key"] = config["api_key"]
        if "base_url" in config:
            openai_config["base_url"] = config["base_url"]
        if "organization" in config:
            openai_config["organization"] = config["organization"]
        
        return OpenAIAdapter(config=openai_config)
    
    elif provider == "mock":
        # Extract Mock-specific config
        mock_config = {}
        if "response_delay" in config:
            mock_config["response_delay"] = config["response_delay"]
        if "fail_rate" in config:
            mock_config["fail_rate"] = config["fail_rate"]
        
        return MockAdapter(**mock_config)
    
    else:
        raise ValueError(f"Unknown provider: {provider}") 