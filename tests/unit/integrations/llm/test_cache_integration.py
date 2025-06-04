"""
Integration tests for LLM cache with LLM client.

Tests the integration between the cache implementations and the LLM client.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from metadata_code_extractor.core.models.llm import (
    ChatMessage,
    EmbeddingConfig,
    EmbeddingResponse,
    LLMResponse,
    MessageRole,
    ModelConfig,
)
from metadata_code_extractor.integrations.llm import (
    InMemoryLLMCache,
    LLMClient,
    LLMProviderAdapter,
)


class MockLLMProvider(LLMProviderAdapter):
    """
    Mock LLM provider for testing.
    
    Purpose: Provides a controllable mock implementation of LLMProviderAdapter
    for testing cache integration without making actual API calls.
    
    Features:
    - Tracks call count to verify caching behavior
    - Returns predictable responses for testing
    - Implements both chat completion and embedding methods
    - Always reports as available for testing
    
    Dependencies:
    - LLMProviderAdapter base class
    - LLMResponse and EmbeddingResponse models
    
    Notes: This mock enables testing of cache behavior without external
    dependencies or API costs, while maintaining realistic response patterns.
    """
    
    def __init__(self):
        self.call_count = 0
    
    async def get_chat_completion(self, messages, config):
        self.call_count += 1
        return LLMResponse(
            content=f"Response {self.call_count}",
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop"
        )
    
    async def generate_embeddings(self, texts, config):
        self.call_count += 1
        return EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3] for _ in texts],
            model="mock-embedding-model",
            usage={"prompt_tokens": len(texts) * 5, "total_tokens": len(texts) * 5}
        )
    
    async def is_available(self):
        return True


class TestLLMClientCacheIntegration:
    """Test LLM client integration with cache."""
    
    @pytest.mark.asyncio
    async def test_chat_completion_caching(self):
        """
        Test that chat completions are cached properly.
        
        Purpose: Verify that the LLM client correctly integrates with the cache
        to store and retrieve chat completion responses, avoiding duplicate API calls.
        
        Checkpoints:
        - First call hits the provider and increments call count
        - Second identical call uses cache and doesn't increment call count
        - Cached response matches original response exactly
        - Cache key is generated correctly for the request
        - Cache contains the expected response data
        
        Mocks:
        - MockLLMProvider: Tracks API calls and provides predictable responses
        
        Dependencies:
        - InMemoryLLMCache for caching functionality
        - MockLLMProvider for controlled API simulation
        - LLMClient for integration testing
        - ChatMessage and ModelConfig for request data
        - pytest.mark.asyncio for async test execution
        
        Notes: This test verifies the core caching functionality that prevents
        expensive duplicate API calls for identical chat completion requests.
        """
        cache = InMemoryLLMCache(default_ttl=3600)
        provider = MockLLMProvider()
        client = LLMClient(provider_adapter=provider, cache=cache)
        
        messages = [ChatMessage(role=MessageRole.USER, content="Test message")]
        config = ModelConfig(model_name="test-model", temperature=0.1)
        
        # First call should hit the provider
        response1 = await client.get_chat_completion(messages, config)
        assert provider.call_count == 1
        assert response1.content == "Response 1"
        
        # Second call should use cache
        response2 = await client.get_chat_completion(messages, config)
        assert provider.call_count == 1  # No additional call
        assert response2.content == "Response 1"  # Same response
        
        # Verify cache contains the response
        cache_key = client._generate_cache_key(messages, config)
        cached_response = cache.get(cache_key)
        assert cached_response is not None
        assert cached_response.content == "Response 1"
    
    @pytest.mark.asyncio
    async def test_embedding_caching(self):
        """
        Test that embeddings are cached properly.
        
        Purpose: Verify that the LLM client correctly integrates with the cache
        to store and retrieve embedding responses, avoiding duplicate API calls.
        
        Checkpoints:
        - First call hits the provider and increments call count
        - Second identical call uses cache and doesn't increment call count
        - Cached embeddings match original embeddings exactly
        - Cache key is generated correctly for embedding requests
        - Cache contains the expected embedding data
        
        Mocks:
        - MockLLMProvider: Tracks API calls and provides predictable embeddings
        
        Dependencies:
        - InMemoryLLMCache for caching functionality
        - MockLLMProvider for controlled API simulation
        - LLMClient for integration testing
        - EmbeddingConfig for request configuration
        - pytest.mark.asyncio for async test execution
        
        Notes: Embedding caching is particularly valuable as embedding generation
        can be expensive and embeddings for the same text are deterministic.
        """
        cache = InMemoryLLMCache(default_ttl=3600)
        provider = MockLLMProvider()
        client = LLMClient(provider_adapter=provider, cache=cache)
        
        texts = ["text1", "text2"]
        config = EmbeddingConfig(model_name="test-embedding-model")
        
        # First call should hit the provider
        response1 = await client.generate_embeddings(texts, config)
        assert provider.call_count == 1
        assert len(response1.embeddings) == 2
        
        # Second call should use cache
        response2 = await client.generate_embeddings(texts, config)
        assert provider.call_count == 1  # No additional call
        assert response2.embeddings == response1.embeddings
        
        # Verify cache contains the response
        cache_key = client._generate_cache_key(texts, config)
        cached_response = cache.get(cache_key)
        assert cached_response is not None
        assert cached_response.embeddings == response1.embeddings
    
    @pytest.mark.asyncio
    async def test_different_requests_not_cached(self):
        """
        Test that different requests are not cached together.
        
        Purpose: Verify that the LLM client generates different cache keys for
        different requests, ensuring cache isolation and correctness.
        
        Checkpoints:
        - Different messages generate different cache keys
        - Each unique request hits the provider
        - Call count increases for each different request
        - Responses are different for different requests
        - Cache doesn't incorrectly serve responses for different requests
        
        Mocks:
        - MockLLMProvider: Tracks API calls and provides unique responses
        
        Dependencies:
        - InMemoryLLMCache for caching functionality
        - MockLLMProvider for controlled API simulation
        - LLMClient for integration testing
        - ChatMessage and ModelConfig for request data
        - pytest.mark.asyncio for async test execution
        
        Notes: This test ensures cache key generation is sufficiently specific
        to prevent cache collisions between different requests.
        """
        cache = InMemoryLLMCache(default_ttl=3600)
        provider = MockLLMProvider()
        client = LLMClient(provider_adapter=provider, cache=cache)
        
        # Different messages
        messages1 = [ChatMessage(role=MessageRole.USER, content="Message 1")]
        messages2 = [ChatMessage(role=MessageRole.USER, content="Message 2")]
        config = ModelConfig(model_name="test-model", temperature=0.1)
        
        # Both calls should hit the provider
        response1 = await client.get_chat_completion(messages1, config)
        response2 = await client.get_chat_completion(messages2, config)
        
        assert provider.call_count == 2
        assert response1.content == "Response 1"
        assert response2.content == "Response 2"
    
    @pytest.mark.asyncio
    async def test_client_without_cache(self):
        """
        Test that client works without cache.
        
        Purpose: Verify that the LLM client functions correctly when no cache
        is provided, ensuring cache is optional and doesn't break functionality.
        
        Checkpoints:
        - Client accepts None as cache parameter
        - All requests hit the provider when cache is disabled
        - Call count increases for each request
        - Responses are generated normally without caching
        - No cache-related errors occur
        
        Mocks:
        - MockLLMProvider: Tracks API calls to verify no caching occurs
        
        Dependencies:
        - MockLLMProvider for controlled API simulation
        - LLMClient for integration testing
        - ChatMessage and ModelConfig for request data
        - pytest.mark.asyncio for async test execution
        
        Notes: This test ensures that caching is truly optional and the client
        can operate in environments where caching is not desired or available.
        """
        provider = MockLLMProvider()
        client = LLMClient(provider_adapter=provider, cache=None)
        
        messages = [ChatMessage(role=MessageRole.USER, content="Test message")]
        config = ModelConfig(model_name="test-model", temperature=0.1)
        
        # Both calls should hit the provider
        response1 = await client.get_chat_completion(messages, config)
        response2 = await client.get_chat_completion(messages, config)
        
        assert provider.call_count == 2
        assert response1.content == "Response 1"
        assert response2.content == "Response 2" 