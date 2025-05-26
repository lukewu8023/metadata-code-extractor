"""
Unit tests for LLM Provider Adapters.

Tests the concrete implementations of LLMProviderAdapter including
OpenAI adapter (for OpenRouter) and Mock adapter for testing.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import List, Optional
import json

from metadata_code_extractor.core.models.llm_models import (
    ChatMessage, MessageRole, ModelConfig, EmbeddingConfig, 
    LLMResponse, EmbeddingResponse
)


class TestOpenAIAdapter:
    """Test cases for the OpenAI adapter (used with OpenRouter)."""
    
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
            model_name="openai/gpt-4",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """Sample embedding configuration."""
        return EmbeddingConfig(
            model_name="openai/text-embedding-ada-002"
        )
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        client = Mock()
        client.chat = Mock()
        client.chat.completions = Mock()
        client.chat.completions.create = Mock()  # OpenAI client methods are synchronous
        client.embeddings = Mock()
        client.embeddings.create = Mock()  # OpenAI client methods are synchronous
        return client
    
    @pytest.fixture
    def openai_chat_response(self):
        """Mock OpenAI chat response."""
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = "Python is a programming language."
        response.choices[0].finish_reason = "stop"
        response.model = "openai/gpt-4"
        response.usage = Mock()
        response.usage.prompt_tokens = 10
        response.usage.completion_tokens = 8
        response.usage.total_tokens = 18
        return response
    
    @pytest.fixture
    def openai_embedding_response(self):
        """Mock OpenAI embedding response."""
        response = Mock()
        response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        response.model = "openai/text-embedding-ada-002"
        response.usage = Mock()
        response.usage.prompt_tokens = 5
        response.usage.total_tokens = 5
        return response
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_success(self, mock_openai_client, openai_chat_response,
                                             sample_chat_messages, sample_model_config):
        """Test successful chat completion with OpenAI adapter."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        # Setup mock
        mock_openai_client.chat.completions.create.return_value = openai_chat_response
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test the method
        result = await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Assertions
        assert isinstance(result, LLMResponse)
        assert result.content == "Python is a programming language."
        assert result.model == "openai/gpt-4"
        assert result.usage == {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
        assert result.finish_reason == "stop"
        
        # Verify the call was made correctly
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "openai/gpt-4"
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["max_tokens"] == 1024
        assert len(call_args.kwargs["messages"]) == 2
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, mock_openai_client, openai_embedding_response,
                                             sample_embedding_config):
        """Test successful embedding generation with OpenAI adapter."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        # Setup mock
        mock_openai_client.embeddings.create.return_value = openai_embedding_response
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test the method
        texts = ["Hello world", "Python programming"]
        result = await adapter.generate_embeddings(texts, sample_embedding_config)
        
        # Assertions
        assert isinstance(result, EmbeddingResponse)
        assert result.embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert result.model == "openai/text-embedding-ada-002"
        assert result.usage == {"prompt_tokens": 5, "total_tokens": 5}
        
        # Verify the call was made correctly
        mock_openai_client.embeddings.create.assert_called_once()
        call_args = mock_openai_client.embeddings.create.call_args
        assert call_args.kwargs["model"] == "openai/text-embedding-ada-002"
        assert call_args.kwargs["input"] == texts
    
    @pytest.mark.asyncio
    async def test_is_available_success(self, mock_openai_client):
        """Test availability check when client is working."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        # Setup mock for a simple test call
        test_response = Mock()
        test_response.choices = [Mock()]
        test_response.choices[0].message = Mock()
        test_response.choices[0].message.content = "test"
        mock_openai_client.chat.completions.create.return_value = test_response
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test availability
        result = await adapter.is_available()
        
        # Assertions
        assert result is True
        mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_available_failure(self, mock_openai_client):
        """Test availability check when client fails."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        # Setup mock to raise an exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test availability
        result = await adapter.is_available()
        
        # Assertions
        assert result is False
    
    @pytest.mark.asyncio
    async def test_chat_completion_api_error(self, mock_openai_client, sample_chat_messages, sample_model_config):
        """Test handling of API errors during chat completion."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        from metadata_code_extractor.core.llm.client import LLMProviderError
        
        # Setup mock to raise an exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test that error is wrapped and raised
        with pytest.raises(LLMProviderError, match="API Error"):
            await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
    
    @pytest.mark.asyncio
    async def test_embeddings_api_error(self, mock_openai_client, sample_embedding_config):
        """Test handling of API errors during embedding generation."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        from metadata_code_extractor.core.llm.client import LLMProviderError
        
        # Setup mock to raise an exception
        mock_openai_client.embeddings.create.side_effect = Exception("API Error")
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test that error is wrapped and raised
        with pytest.raises(LLMProviderError, match="API Error"):
            await adapter.generate_embeddings(["test"], sample_embedding_config)
    
    def test_adapter_initialization_with_config(self):
        """Test adapter initialization with configuration."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        config = {
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1",
            "organization": "test-org"
        }
        
        with patch('metadata_code_extractor.core.llm.adapters.OpenAI') as mock_openai:
            adapter = OpenAIAdapter(config=config)
            
            # Verify OpenAI client was created with correct config
            mock_openai.assert_called_once_with(
                api_key="test-key",
                base_url="https://openrouter.ai/api/v1",
                organization="test-org"
            )
    
    def test_adapter_initialization_without_config(self):
        """Test adapter initialization without configuration (should use env vars)."""
        from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
        
        with patch('metadata_code_extractor.core.llm.adapters.OpenAI') as mock_openai:
            adapter = OpenAIAdapter()
            
            # Verify OpenAI client was created with default config
            mock_openai.assert_called_once_with()


class TestMockAdapter:
    """Test cases for the Mock adapter."""
    
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
            model_name="mock-model",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """Sample embedding configuration."""
        return EmbeddingConfig(
            model_name="mock-embedding-model"
        )
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_success(self, sample_chat_messages, sample_model_config):
        """Test successful chat completion with Mock adapter."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        
        # Create adapter
        adapter = MockAdapter()
        
        # Test the method
        result = await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
        
        # Assertions
        assert isinstance(result, LLMResponse)
        assert result.content.startswith("Mock response for:")
        assert "What is Python?" in result.content  # Should include user message
        assert result.model == "mock-model"
        assert result.usage == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        assert result.finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, sample_embedding_config):
        """Test successful embedding generation with Mock adapter."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        
        # Create adapter
        adapter = MockAdapter()
        
        # Test the method
        texts = ["Hello world", "Python programming"]
        result = await adapter.generate_embeddings(texts, sample_embedding_config)
        
        # Assertions
        assert isinstance(result, EmbeddingResponse)
        assert len(result.embeddings) == 2
        assert len(result.embeddings[0]) == 384  # Standard embedding dimension
        assert len(result.embeddings[1]) == 384
        assert result.model == "mock-embedding-model"
        assert result.usage == {"prompt_tokens": 5, "total_tokens": 5}
        
        # Embeddings should be deterministic for same input
        result2 = await adapter.generate_embeddings(texts, sample_embedding_config)
        assert result.embeddings == result2.embeddings
    
    @pytest.mark.asyncio
    async def test_is_available_always_true(self):
        """Test that mock adapter is always available."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        
        # Create adapter
        adapter = MockAdapter()
        
        # Test availability
        result = await adapter.is_available()
        
        # Assertions
        assert result is True
    
    @pytest.mark.asyncio
    async def test_mock_response_includes_context(self, sample_model_config):
        """Test that mock responses include context from messages."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        
        # Create adapter
        adapter = MockAdapter()
        
        # Test with different messages
        messages1 = [ChatMessage(role=MessageRole.USER, content="Hello")]
        messages2 = [ChatMessage(role=MessageRole.USER, content="Goodbye")]
        
        result1 = await adapter.get_chat_completion(messages1, sample_model_config)
        result2 = await adapter.get_chat_completion(messages2, sample_model_config)
        
        # Responses should be different based on input
        assert result1.content != result2.content
        assert "Hello" in result1.content
        assert "Goodbye" in result2.content
    
    def test_mock_adapter_initialization(self):
        """Test mock adapter initialization."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        
        # Test with default settings
        adapter1 = MockAdapter()
        assert adapter1.response_delay == 0.1
        assert adapter1.fail_rate == 0.0
        
        # Test with custom settings
        adapter2 = MockAdapter(response_delay=0.5, fail_rate=0.1)
        assert adapter2.response_delay == 0.5
        assert adapter2.fail_rate == 0.1
    
    @pytest.mark.asyncio
    async def test_mock_adapter_simulated_failure(self, sample_chat_messages, sample_model_config):
        """Test mock adapter simulated failures."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        from metadata_code_extractor.core.llm.client import LLMProviderError
        
        # Create adapter with 100% failure rate
        adapter = MockAdapter(fail_rate=1.0)
        
        # Test that it raises an error
        with pytest.raises(LLMProviderError, match="Simulated failure"):
            await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
    
    @pytest.mark.asyncio
    async def test_mock_adapter_response_delay(self, sample_chat_messages, sample_model_config):
        """Test mock adapter response delay."""
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        import time
        
        # Create adapter with delay
        adapter = MockAdapter(response_delay=0.1)
        
        # Measure time
        start_time = time.time()
        result = await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
        end_time = time.time()
        
        # Should have taken at least the delay time
        assert end_time - start_time >= 0.1
        assert isinstance(result, LLMResponse)


class TestAdapterFactory:
    """Test cases for adapter factory functionality."""
    
    def test_create_openai_adapter(self):
        """Test creating OpenAI adapter through factory."""
        from metadata_code_extractor.core.llm.adapters import create_adapter
        
        config = {
            "provider": "openai",
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1"
        }
        
        with patch('metadata_code_extractor.core.llm.adapters.OpenAI'):
            adapter = create_adapter(config)
            
            from metadata_code_extractor.core.llm.adapters import OpenAIAdapter
            assert isinstance(adapter, OpenAIAdapter)
    
    def test_create_mock_adapter(self):
        """Test creating Mock adapter through factory."""
        from metadata_code_extractor.core.llm.adapters import create_adapter
        
        config = {
            "provider": "mock",
            "response_delay": 0.2,
            "fail_rate": 0.1
        }
        
        adapter = create_adapter(config)
        
        from metadata_code_extractor.core.llm.adapters import MockAdapter
        assert isinstance(adapter, MockAdapter)
        assert adapter.response_delay == 0.2
        assert adapter.fail_rate == 0.1
    
    def test_create_adapter_invalid_provider(self):
        """Test creating adapter with invalid provider."""
        from metadata_code_extractor.core.llm.adapters import create_adapter
        
        config = {"provider": "invalid"}
        
        with pytest.raises(ValueError, match="Unknown provider"):
            create_adapter(config)
    
    def test_create_adapter_missing_provider(self):
        """Test creating adapter without provider specified."""
        from metadata_code_extractor.core.llm.adapters import create_adapter
        
        config = {}
        
        with pytest.raises(ValueError, match="Provider must be specified"):
            create_adapter(config) 