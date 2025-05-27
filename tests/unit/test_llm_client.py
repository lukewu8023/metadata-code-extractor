"""
Unit tests for the LLM Client interface.

Tests the main LLMClient interface and its core functionality including
chat completions, text generation, embeddings, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import List, Optional

from metadata_code_extractor.core.models.llm import (
    ChatMessage, MessageRole, ModelConfig, EmbeddingConfig, 
    LLMResponse, EmbeddingResponse
)


class TestLLMClient:
    """Test cases for the LLMClient interface."""
    
    @pytest.fixture
    def mock_provider_adapter(self):
        """Create a mock provider adapter."""
        adapter = AsyncMock()
        adapter.get_chat_completion = AsyncMock()
        adapter.generate_embeddings = AsyncMock()
        adapter.is_available = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def sample_chat_messages(self):
        """Sample chat messages for testing."""
        return [
            ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            ChatMessage(role=MessageRole.USER, content="What is Python?")
        ]
    
    @pytest.fixture
    def sample_model_config(self):
        """Sample model configuration."""
        return ModelConfig(
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """Sample embedding configuration."""
        return EmbeddingConfig(
            model_name="text-embedding-ada-002"
        )
    
    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response."""
        return LLMResponse(
            content="Python is a programming language.",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            finish_reason="stop"
        )
    
    @pytest.fixture
    def sample_embedding_response(self):
        """Sample embedding response."""
        return EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            model="text-embedding-ada-002",
            usage={"prompt_tokens": 5, "total_tokens": 5}
        )
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_success(self, mock_provider_adapter, sample_chat_messages, 
                                             sample_model_config, sample_llm_response):
        """Test successful chat completion."""
        # Import here to avoid circular imports during test discovery
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Setup mock
        mock_provider_adapter.get_chat_completion.return_value = sample_llm_response
        
        # Create client with mock adapter
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test the method
        result = await client.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Assertions
        assert result == sample_llm_response
        mock_provider_adapter.get_chat_completion.assert_called_once_with(
            sample_chat_messages, sample_model_config
        )
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_with_caching(self, mock_provider_adapter, sample_chat_messages,
                                                   sample_model_config, sample_llm_response):
        """Test chat completion with caching enabled."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Setup mock
        mock_provider_adapter.get_chat_completion.return_value = sample_llm_response
        mock_cache = Mock()
        mock_cache.get = Mock(return_value=None)  # Cache miss first time
        mock_cache.set = Mock()
        
        # Create client with cache
        client = LLMClient(provider_adapter=mock_provider_adapter, cache=mock_cache)
        
        # First call - should hit provider and cache result
        result1 = await client.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Setup cache hit for second call
        mock_cache.get.return_value = sample_llm_response
        
        # Second call - should hit cache
        result2 = await client.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Assertions
        assert result1 == sample_llm_response
        assert result2 == sample_llm_response
        # Provider should only be called once
        assert mock_provider_adapter.get_chat_completion.call_count == 1
        # Cache should be checked twice and set once
        assert mock_cache.get.call_count == 2
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self, mock_provider_adapter, sample_model_config, sample_llm_response):
        """Test successful text generation."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Setup mock
        mock_provider_adapter.get_chat_completion.return_value = sample_llm_response
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test the method
        prompt = "What is Python?"
        result = await client.generate_text(prompt, sample_model_config)
        
        # Assertions
        assert result == sample_llm_response
        # Should convert text prompt to chat messages
        expected_messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        mock_provider_adapter.get_chat_completion.assert_called_once_with(
            expected_messages, sample_model_config
        )
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, mock_provider_adapter, sample_embedding_config, 
                                             sample_embedding_response):
        """Test successful embedding generation."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Setup mock
        mock_provider_adapter.generate_embeddings.return_value = sample_embedding_response
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test the method
        texts = ["Hello world", "Python programming"]
        result = await client.generate_embeddings(texts, sample_embedding_config)
        
        # Assertions
        assert result == sample_embedding_response
        mock_provider_adapter.generate_embeddings.assert_called_once_with(
            texts, sample_embedding_config
        )
    
    @pytest.mark.asyncio
    async def test_provider_error_handling(self, mock_provider_adapter, sample_chat_messages, sample_model_config):
        """Test handling of provider errors."""
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMProviderError
        
        # Setup mock to raise an error
        mock_provider_adapter.get_chat_completion.side_effect = LLMProviderError("API Error")
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test that error is propagated
        with pytest.raises(LLMProviderError, match="API Error"):
            await client.get_chat_completion(sample_chat_messages, sample_model_config)
    
    @pytest.mark.asyncio
    async def test_provider_unavailable(self, mock_provider_adapter, sample_chat_messages, sample_model_config):
        """Test handling when provider is unavailable."""
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMProviderError
        
        # Setup mock to be unavailable
        mock_provider_adapter.is_available.return_value = False
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test that error is raised
        with pytest.raises(LLMProviderError, match="Provider is not available"):
            await client.get_chat_completion(sample_chat_messages, sample_model_config)
    
    def test_client_initialization_with_defaults(self):
        """Test client initialization with default parameters."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Should be able to create client without parameters (will use defaults)
        client = LLMClient()
        
        # Should have None values by default (user must provide adapter explicitly)
        assert client.provider_adapter is None
        assert client.cache is None
    
    def test_client_initialization_with_custom_adapter(self, mock_provider_adapter):
        """Test client initialization with custom adapter."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Create client with custom adapter
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Should use the provided adapter
        assert client.provider_adapter == mock_provider_adapter
    
    @pytest.mark.asyncio
    async def test_empty_messages_handling(self, mock_provider_adapter, sample_model_config):
        """Test handling of empty message list."""
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMClientError
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test with empty messages
        with pytest.raises(LLMClientError, match="Messages cannot be empty"):
            await client.get_chat_completion([], sample_model_config)
    
    @pytest.mark.asyncio
    async def test_empty_texts_for_embeddings(self, mock_provider_adapter, sample_embedding_config):
        """Test handling of empty text list for embeddings."""
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMClientError
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test with empty texts
        with pytest.raises(LLMClientError, match="Texts cannot be empty"):
            await client.generate_embeddings([], sample_embedding_config)
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, mock_provider_adapter, sample_chat_messages, sample_model_config):
        """Test that cache keys are generated consistently."""
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        mock_cache = Mock()
        mock_cache.get = Mock(return_value=None)
        mock_cache.set = Mock()
        
        client = LLMClient(provider_adapter=mock_provider_adapter, cache=mock_cache)
        
        # Make the same call twice
        await client.get_chat_completion(sample_chat_messages, sample_model_config)
        await client.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Cache should be called with the same key both times
        cache_calls = mock_cache.get.call_args_list
        assert len(cache_calls) == 2
        assert cache_calls[0][0][0] == cache_calls[1][0][0]  # Same cache key


class TestLLMProviderAdapter:
    """Test cases for the LLMProviderAdapter interface."""
    
    def test_provider_adapter_interface(self):
        """Test that provider adapter interface is properly defined."""
        from metadata_code_extractor.integrations.llm.client import LLMProviderAdapter
        
        # Should be an abstract base class
        assert hasattr(LLMProviderAdapter, '__abstractmethods__')
        
        # Should have required abstract methods
        required_methods = {'get_chat_completion', 'generate_embeddings', 'is_available'}
        assert required_methods.issubset(LLMProviderAdapter.__abstractmethods__)


class TestLLMExceptions:
    """Test cases for LLM-related exceptions."""
    
    def test_llm_client_error(self):
        """Test LLMClientError exception."""
        from metadata_code_extractor.integrations.llm.client import LLMClientError
        
        error = LLMClientError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_llm_provider_error(self):
        """Test LLMProviderError exception."""
        from metadata_code_extractor.integrations.llm.client import LLMProviderError
        
        error = LLMProviderError("Provider error")
        assert str(error) == "Provider error"
        assert isinstance(error, Exception)
    
    def test_llm_cache_error(self):
        """Test LLMCacheError exception."""
        from metadata_code_extractor.integrations.llm.client import LLMCacheError
        
        error = LLMCacheError("Cache error")
        assert str(error) == "Cache error"
        assert isinstance(error, Exception) 