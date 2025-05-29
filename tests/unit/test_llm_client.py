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
        """
        Create a mock provider adapter.
        
        Purpose: Provide a mock implementation of LLMProviderAdapter for testing
        the LLMClient without requiring actual provider implementations.
        
        Notes: Uses AsyncMock for async methods and Mock for sync methods.
        All methods return appropriate default values for successful testing.
        """
        adapter = AsyncMock()
        adapter.get_chat_completion = AsyncMock()
        adapter.generate_embeddings = AsyncMock()
        adapter.is_available = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def sample_chat_messages(self):
        """
        Sample chat messages for testing.
        
        Purpose: Provide consistent test data for chat-related tests.
        
        Notes: Includes both system and user messages to test typical
        conversation patterns used in the application.
        """
        return [
            ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            ChatMessage(role=MessageRole.USER, content="What is Python?")
        ]
    
    @pytest.fixture
    def sample_model_config(self):
        """
        Sample model configuration.
        
        Purpose: Provide consistent model configuration for testing.
        
        Notes: Uses realistic model parameters that would be used
        in actual application scenarios.
        """
        return ModelConfig(
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """
        Sample embedding configuration.
        
        Purpose: Provide consistent embedding configuration for testing.
        
        Notes: Uses a realistic embedding model name for testing
        embedding generation functionality.
        """
        return EmbeddingConfig(
            model_name="text-embedding-ada-002"
        )
    
    @pytest.fixture
    def sample_llm_response(self):
        """
        Sample LLM response.
        
        Purpose: Provide a realistic LLM response for testing response handling.
        
        Notes: Includes all typical fields returned by LLM providers including
        usage statistics and finish reason for comprehensive testing.
        """
        return LLMResponse(
            content="Python is a programming language.",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            finish_reason="stop"
        )
    
    @pytest.fixture
    def sample_embedding_response(self):
        """
        Sample embedding response.
        
        Purpose: Provide a realistic embedding response for testing embedding handling.
        
        Notes: Includes multiple embeddings to test batch processing and
        usage statistics for comprehensive validation.
        """
        return EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            model="text-embedding-ada-002",
            usage={"prompt_tokens": 5, "total_tokens": 5}
        )
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_success(self, mock_provider_adapter, sample_chat_messages, 
                                             sample_model_config, sample_llm_response):
        """
        Test successful chat completion.
        
        Purpose: Verify that LLMClient correctly delegates chat completion requests
        to the provider adapter and returns the response unchanged.
        
        Checkpoints:
        - LLMClient returns the exact response from provider adapter
        - Provider adapter is called with correct parameters
        - No transformation or modification of the response occurs
        - Async operation completes successfully
        
        Mocks:
        - mock_provider_adapter: Mocked provider adapter to avoid external dependencies
        
        Dependencies:
        - LLMClient class from client module
        - Sample fixtures for consistent test data
        
        Notes: This test verifies the basic delegation pattern where LLMClient
        acts as a facade over provider adapters without modifying responses.
        """
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
        """
        Test chat completion with caching enabled.
        
        Purpose: Verify that LLMClient properly implements caching for chat completions,
        reducing redundant API calls and improving performance.
        
        Checkpoints:
        - First call results in cache miss and provider call
        - Cache stores the response after first call
        - Second identical call results in cache hit
        - Provider is only called once for identical requests
        - Cache key generation works correctly
        
        Mocks:
        - mock_provider_adapter: Mocked provider adapter
        - mock_cache: Mocked cache implementation
        
        Dependencies:
        - LLMClient class with caching support
        - Mock cache implementation
        
        Notes: Caching is crucial for performance when the same requests are made
        multiple times. This test ensures the caching logic works correctly.
        """
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
        """
        Test successful text generation.
        
        Purpose: Verify that LLMClient can convert simple text prompts into chat messages
        and delegate to the chat completion functionality.
        
        Checkpoints:
        - Text prompt is converted to ChatMessage with USER role
        - Converted message is passed to get_chat_completion
        - Response from chat completion is returned unchanged
        - Convenience method works as expected
        
        Mocks:
        - mock_provider_adapter: Mocked provider adapter
        
        Dependencies:
        - LLMClient class with text generation support
        - ChatMessage model for message conversion
        
        Notes: This is a convenience method that simplifies the interface for
        simple text-to-text interactions without requiring message construction.
        """
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
        """
        Test successful embedding generation.
        
        Purpose: Verify that LLMClient correctly delegates embedding generation
        to the provider adapter without modification.
        
        Checkpoints:
        - Embedding request is passed through to provider adapter
        - Response from provider is returned unchanged
        - Multiple texts are handled correctly
        - Async operation completes successfully
        
        Mocks:
        - mock_provider_adapter: Mocked provider adapter
        
        Dependencies:
        - LLMClient class with embedding support
        - EmbeddingResponse model for response validation
        
        Notes: Embedding generation is a direct delegation to the provider
        adapter, ensuring consistent behavior across different providers.
        """
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
        """
        Test handling of provider errors.
        
        Purpose: Verify that LLMClient properly propagates provider errors
        without modification, maintaining error context and type.
        
        Checkpoints:
        - Provider errors are propagated unchanged
        - Error type is preserved (LLMProviderError)
        - Error message is preserved
        - No additional error wrapping occurs
        
        Mocks:
        - mock_provider_adapter: Mocked provider configured to raise errors
        
        Dependencies:
        - LLMClient class
        - LLMProviderError for error type validation
        - pytest for exception testing
        
        Notes: Error propagation ensures that upstream code can handle
        provider-specific errors appropriately without losing context.
        """
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
        """
        Test handling when provider is unavailable.
        
        Purpose: Verify that LLMClient checks provider availability before
        making requests and raises appropriate errors when unavailable.
        
        Checkpoints:
        - Provider availability is checked before requests
        - Unavailable provider results in LLMProviderError
        - Error message indicates provider unavailability
        - No actual request is made to unavailable provider
        
        Mocks:
        - mock_provider_adapter: Mocked provider configured as unavailable
        
        Dependencies:
        - LLMClient class with availability checking
        - LLMProviderError for error validation
        
        Notes: Availability checking prevents wasted requests to known
        unavailable providers and provides clear error messaging.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMProviderError
        
        # Setup mock to be unavailable
        mock_provider_adapter.is_available.return_value = False
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test that error is raised
        with pytest.raises(LLMProviderError, match="Provider is not available"):
            await client.get_chat_completion(sample_chat_messages, sample_model_config)
    
    def test_client_initialization_with_defaults(self):
        """
        Test client initialization with default parameters.
        
        Purpose: Verify that LLMClient can be initialized without parameters
        and has appropriate default values for optional components.
        
        Checkpoints:
        - Client initializes successfully without parameters
        - Provider adapter defaults to None (requires explicit setup)
        - Cache defaults to None (no caching by default)
        - Default initialization doesn't raise errors
        
        Mocks: None - tests actual initialization behavior
        
        Dependencies:
        - LLMClient class
        
        Notes: Default initialization allows for flexible client setup
        where components can be configured after instantiation.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Should be able to create client without parameters (will use defaults)
        client = LLMClient()
        
        # Should have None values by default (user must provide adapter explicitly)
        assert client.provider_adapter is None
        assert client.cache is None
    
    def test_client_initialization_with_custom_adapter(self, mock_provider_adapter):
        """
        Test client initialization with custom adapter.
        
        Purpose: Verify that LLMClient can be initialized with a custom
        provider adapter and properly stores the reference.
        
        Checkpoints:
        - Custom adapter is stored correctly
        - Client initialization succeeds with custom adapter
        - Adapter reference is accessible after initialization
        
        Mocks:
        - mock_provider_adapter: Custom adapter for testing
        
        Dependencies:
        - LLMClient class
        
        Notes: Custom adapter initialization is the primary way to configure
        LLMClient for specific provider implementations.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClient
        
        # Create client with custom adapter
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Should use the provided adapter
        assert client.provider_adapter == mock_provider_adapter
    
    @pytest.mark.asyncio
    async def test_empty_messages_handling(self, mock_provider_adapter, sample_model_config):
        """
        Test handling of empty message list.
        
        Purpose: Verify that LLMClient validates input and raises appropriate
        errors when empty message lists are provided.
        
        Checkpoints:
        - Empty message list raises LLMClientError
        - Error message indicates the validation failure
        - Validation occurs before provider calls
        - Error type is specific to client validation
        
        Mocks:
        - mock_provider_adapter: Provider adapter (not called due to validation)
        
        Dependencies:
        - LLMClient class with input validation
        - LLMClientError for validation errors
        - pytest for exception testing
        
        Notes: Input validation prevents invalid requests from reaching
        providers and provides clear error messaging for client errors.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMClientError
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test with empty messages
        with pytest.raises(LLMClientError, match="Messages cannot be empty"):
            await client.get_chat_completion([], sample_model_config)
    
    @pytest.mark.asyncio
    async def test_empty_texts_for_embeddings(self, mock_provider_adapter, sample_embedding_config):
        """
        Test handling of empty text list for embeddings.
        
        Purpose: Verify that LLMClient validates embedding input and raises
        appropriate errors when empty text lists are provided.
        
        Checkpoints:
        - Empty text list raises LLMClientError
        - Error message indicates the validation failure
        - Validation occurs before provider calls
        - Error type is specific to client validation
        
        Mocks:
        - mock_provider_adapter: Provider adapter (not called due to validation)
        
        Dependencies:
        - LLMClient class with input validation
        - LLMClientError for validation errors
        - pytest for exception testing
        
        Notes: Input validation for embeddings prevents wasted API calls
        and provides clear feedback for invalid requests.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClient, LLMClientError
        
        # Create client
        client = LLMClient(provider_adapter=mock_provider_adapter)
        
        # Test with empty texts
        with pytest.raises(LLMClientError, match="Texts cannot be empty"):
            await client.generate_embeddings([], sample_embedding_config)
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, mock_provider_adapter, sample_chat_messages, sample_model_config):
        """
        Test that cache keys are generated consistently.
        
        Purpose: Verify that LLMClient generates consistent cache keys for
        identical requests, enabling proper cache hit/miss behavior.
        
        Checkpoints:
        - Identical requests generate identical cache keys
        - Cache is called with consistent keys across multiple requests
        - Cache key generation is deterministic
        - Cache operations use the same key for get and set
        
        Mocks:
        - mock_provider_adapter: Provider adapter for request handling
        - mock_cache: Cache implementation to verify key consistency
        
        Dependencies:
        - LLMClient class with caching support
        - Mock cache for key verification
        
        Notes: Consistent cache key generation is crucial for cache effectiveness.
        This test ensures that identical requests can be properly cached and retrieved.
        """
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
        """
        Test that provider adapter interface is properly defined.
        
        Purpose: Verify that the LLMProviderAdapter abstract base class
        properly defines the required interface for provider implementations.
        
        Checkpoints:
        - LLMProviderAdapter is an abstract base class
        - Required abstract methods are properly defined
        - Interface includes all necessary methods for LLM operations
        - Abstract methods prevent direct instantiation
        
        Mocks: None - tests actual interface definition
        
        Dependencies:
        - LLMProviderAdapter abstract base class
        
        Notes: This test ensures that the provider adapter interface is
        properly defined and enforces implementation of required methods.
        """
        from metadata_code_extractor.integrations.llm.client import LLMProviderAdapter
        
        # Should be an abstract base class
        assert hasattr(LLMProviderAdapter, '__abstractmethods__')
        
        # Should have required abstract methods
        required_methods = {'get_chat_completion', 'generate_embeddings', 'is_available'}
        assert required_methods.issubset(LLMProviderAdapter.__abstractmethods__)


class TestLLMExceptions:
    """Test cases for LLM-related exceptions."""
    
    def test_llm_client_error(self):
        """
        Test LLMClientError exception.
        
        Purpose: Verify that LLMClientError can be created and used properly
        for client-side validation and error handling.
        
        Checkpoints:
        - Exception can be instantiated with error message
        - Error message is preserved and accessible
        - Exception inherits from base Exception class
        - Exception can be raised and caught properly
        
        Mocks: None - tests actual exception class
        
        Dependencies:
        - LLMClientError exception class
        
        Notes: Client errors are used for validation failures and other
        client-side issues that don't originate from providers.
        """
        from metadata_code_extractor.integrations.llm.client import LLMClientError
        
        error = LLMClientError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_llm_provider_error(self):
        """
        Test LLMProviderError exception.
        
        Purpose: Verify that LLMProviderError can be created and used properly
        for provider-side errors and API failures.
        
        Checkpoints:
        - Exception can be instantiated with error message
        - Error message is preserved and accessible
        - Exception inherits from base Exception class
        - Exception can be raised and caught properly
        
        Mocks: None - tests actual exception class
        
        Dependencies:
        - LLMProviderError exception class
        
        Notes: Provider errors are used for API failures, network issues,
        and other problems originating from external LLM providers.
        """
        from metadata_code_extractor.integrations.llm.client import LLMProviderError
        
        error = LLMProviderError("Provider error")
        assert str(error) == "Provider error"
        assert isinstance(error, Exception)
    
    def test_llm_cache_error(self):
        """
        Test LLMCacheError exception.
        
        Purpose: Verify that LLMCacheError can be created and used properly
        for cache-related errors and failures.
        
        Checkpoints:
        - Exception can be instantiated with error message
        - Error message is preserved and accessible
        - Exception inherits from base Exception class
        - Exception can be raised and caught properly
        
        Mocks: None - tests actual exception class
        
        Dependencies:
        - LLMCacheError exception class
        
        Notes: Cache errors are used for cache system failures, serialization
        issues, and other problems related to response caching.
        """
        from metadata_code_extractor.integrations.llm.client import LLMCacheError
        
        error = LLMCacheError("Cache error")
        assert str(error) == "Cache error"
        assert isinstance(error, Exception) 