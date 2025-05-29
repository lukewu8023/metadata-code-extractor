"""
Unit tests for LLM Provider Adapters.

Tests the concrete implementations of LLMProviderAdapter including
OpenAI adapter (for OpenRouter) and Mock adapter for testing.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import List, Optional
import json

from metadata_code_extractor.core.models.llm import (
    ChatMessage, MessageRole, ModelConfig, EmbeddingConfig, 
    LLMResponse, EmbeddingResponse
)


class TestOpenAIAdapter:
    """Test cases for the OpenAI adapter (used with OpenRouter)."""
    
    @pytest.fixture
    def sample_chat_messages(self):
        """
        Sample chat messages for testing.
        
        Purpose: Provide consistent test data for chat completion tests.
        
        Notes: Creates a typical conversation with system and user messages
        that represents real-world usage patterns.
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
        
        Notes: Uses OpenAI model naming convention with reasonable parameters
        for testing chat completions.
        """
        return ModelConfig(
            model_name="openai/gpt-4",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """
        Sample embedding configuration.
        
        Purpose: Provide consistent embedding model configuration for testing.
        
        Notes: Uses OpenAI embedding model for testing embedding generation.
        """
        return EmbeddingConfig(
            model_name="openai/text-embedding-ada-002"
        )
    
    @pytest.fixture
    def mock_openai_client(self):
        """
        Mock OpenAI client.
        
        Purpose: Create a mock OpenAI client for testing without actual API calls.
        
        Notes: Mocks the synchronous OpenAI client structure with chat.completions
        and embeddings endpoints. OpenAI client methods are synchronous, not async.
        """
        client = Mock()
        client.chat = Mock()
        client.chat.completions = Mock()
        client.chat.completions.create = Mock()  # OpenAI client methods are synchronous
        client.embeddings = Mock()
        client.embeddings.create = Mock()  # OpenAI client methods are synchronous
        return client
    
    @pytest.fixture
    def openai_chat_response(self):
        """
        Mock OpenAI chat response.
        
        Purpose: Create a realistic mock response that matches OpenAI API structure.
        
        Notes: Includes all fields typically returned by OpenAI chat completions API
        including usage statistics and finish reason.
        """
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
        """
        Mock OpenAI embedding response.
        
        Purpose: Create a realistic mock response for embedding generation.
        
        Notes: Includes multiple embeddings (for batch processing) and usage statistics
        matching the OpenAI embeddings API structure.
        """
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
        """
        Test successful chat completion with OpenAI adapter.
        
        Purpose: Verify that the OpenAI adapter correctly handles successful chat completion
        requests and properly transforms the response into the expected format.
        
        Checkpoints:
        - Adapter returns LLMResponse instance
        - Response content matches mock API response
        - Model name is preserved from API response
        - Usage statistics are correctly extracted and formatted
        - Finish reason is properly captured
        - OpenAI client is called with correct parameters
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client to avoid actual API calls
        - openai_chat_response: Mocked API response structure
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - LLMResponse model for response validation
        - ChatMessage and ModelConfig for input validation
        
        Notes: This test verifies the core functionality of the OpenAI adapter
        including parameter passing, response parsing, and error-free execution.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
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
        """
        Test successful embedding generation with OpenAI adapter.
        
        Purpose: Verify that the OpenAI adapter correctly handles embedding generation
        requests and properly transforms the response into the expected format.
        
        Checkpoints:
        - Adapter returns EmbeddingResponse instance
        - Embeddings list matches mock API response structure
        - Model name is preserved from API response
        - Usage statistics are correctly extracted
        - Multiple embeddings are handled correctly (batch processing)
        - OpenAI client is called with correct parameters
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client to avoid actual API calls
        - openai_embedding_response: Mocked embedding API response
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - EmbeddingResponse model for response validation
        - EmbeddingConfig for input validation
        
        Notes: This test verifies embedding generation functionality including
        batch processing of multiple texts and proper response transformation.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
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
        """
        Test availability check when client is working.
        
        Purpose: Verify that the adapter can correctly determine when the OpenAI
        client is available and functioning properly.
        
        Checkpoints:
        - is_available() returns True when client works
        - Test call to OpenAI API succeeds
        - Adapter performs actual connectivity check
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client with successful test response
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        
        Notes: The availability check performs a minimal test call to verify
        the client can communicate with the API successfully.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
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
        """
        Test availability check when client fails.
        
        Purpose: Verify that the adapter correctly detects when the OpenAI client
        is not available or experiencing connectivity issues.
        
        Checkpoints:
        - is_available() returns False when client fails
        - Exception during test call is handled gracefully
        - No unhandled exceptions are raised
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client configured to raise exceptions
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        
        Notes: This test ensures robust error handling when the API is unavailable,
        preventing crashes and enabling graceful degradation.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
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
        """
        Test handling of API errors during chat completion.
        
        Purpose: Verify that the adapter properly handles and wraps API errors
        during chat completion requests, providing consistent error handling.
        
        Checkpoints:
        - API exceptions are caught and wrapped in LLMProviderError
        - Original error message is preserved
        - Error handling doesn't crash the adapter
        - Consistent error interface is maintained
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client configured to raise exceptions
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - LLMProviderError for error wrapping
        - pytest for exception testing
        
        Notes: This test ensures that API errors are properly handled and wrapped
        in a consistent error type, enabling proper error handling upstream.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        from metadata_code_extractor.integrations.llm.client import LLMProviderError
        
        # Setup mock to raise an exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test that error is wrapped and raised
        with pytest.raises(LLMProviderError, match="API Error"):
            await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
    
    @pytest.mark.asyncio
    async def test_embeddings_api_error(self, mock_openai_client, sample_embedding_config):
        """
        Test handling of API errors during embedding generation.
        
        Purpose: Verify that the adapter properly handles and wraps API errors
        during embedding generation requests, maintaining consistent error handling.
        
        Checkpoints:
        - API exceptions are caught and wrapped in LLMProviderError
        - Original error message is preserved
        - Error handling doesn't crash the adapter
        - Consistent error interface is maintained
        
        Mocks:
        - mock_openai_client: Mocked OpenAI client configured to raise exceptions
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - LLMProviderError for error wrapping
        - pytest for exception testing
        
        Notes: This test ensures that embedding API errors are properly handled
        and wrapped consistently with chat completion errors.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        from metadata_code_extractor.integrations.llm.client import LLMProviderError
        
        # Setup mock to raise an exception
        mock_openai_client.embeddings.create.side_effect = Exception("API Error")
        
        # Create adapter
        adapter = OpenAIAdapter(client=mock_openai_client)
        
        # Test that error is wrapped and raised
        with pytest.raises(LLMProviderError, match="API Error"):
            await adapter.generate_embeddings(["test"], sample_embedding_config)
    
    def test_adapter_initialization_with_config(self):
        """
        Test adapter initialization with configuration.
        
        Purpose: Verify that the OpenAI adapter can be initialized with custom
        configuration parameters and properly passes them to the OpenAI client.
        
        Checkpoints:
        - Configuration parameters are passed to OpenAI client constructor
        - API key, base URL, and organization are handled correctly
        - Client initialization occurs with expected parameters
        
        Mocks:
        - OpenAI client constructor using patch to verify initialization parameters
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - unittest.mock.patch for constructor mocking
        
        Notes: This test ensures that custom configuration (like API keys and
        custom endpoints) are properly passed through to the underlying client.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
        config = {
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1",
            "organization": "test-org"
        }
        
        with patch('metadata_code_extractor.integrations.llm.providers.adapters.OpenAI') as mock_openai:
            adapter = OpenAIAdapter(config=config)
            
            # Verify OpenAI client was created with correct config
            mock_openai.assert_called_once_with(
                api_key="test-key",
                base_url="https://openrouter.ai/api/v1",
                organization="test-org"
            )
    
    def test_adapter_initialization_without_config(self):
        """
        Test adapter initialization without configuration (should use env vars).
        
        Purpose: Verify that the OpenAI adapter can be initialized without explicit
        configuration and relies on environment variables for client setup.
        
        Checkpoints:
        - OpenAI client is created with default constructor (no parameters)
        - Environment variables are used for configuration
        - Adapter initializes successfully without explicit config
        
        Mocks:
        - OpenAI client constructor using patch to verify default initialization
        
        Dependencies:
        - OpenAIAdapter class from adapters module
        - unittest.mock.patch for constructor mocking
        
        Notes: This test ensures that the adapter works with standard OpenAI
        environment variable configuration (OPENAI_API_KEY, etc.).
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
        
        with patch('metadata_code_extractor.integrations.llm.providers.adapters.OpenAI') as mock_openai:
            adapter = OpenAIAdapter()
            
            # Verify OpenAI client was created with default config
            mock_openai.assert_called_once_with()


class TestMockAdapter:
    """Test cases for the Mock adapter."""
    
    @pytest.fixture
    def sample_chat_messages(self):
        """
        Sample chat messages for testing.
        
        Purpose: Provide consistent test data for mock adapter testing.
        
        Notes: Same structure as OpenAI adapter tests for consistency.
        """
        return [
            ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            ChatMessage(role=MessageRole.USER, content="What is Python?")
        ]
    
    @pytest.fixture
    def sample_model_config(self):
        """
        Sample model configuration.
        
        Purpose: Provide consistent model configuration for mock testing.
        
        Notes: Uses mock model names appropriate for testing scenarios.
        """
        return ModelConfig(
            model_name="mock-model",
            temperature=0.7,
            max_tokens=1024
        )
    
    @pytest.fixture
    def sample_embedding_config(self):
        """
        Sample embedding configuration.
        
        Purpose: Provide consistent embedding configuration for mock testing.
        
        Notes: Uses mock embedding model for testing scenarios.
        """
        return EmbeddingConfig(
            model_name="mock-embedding-model"
        )
    
    @pytest.mark.asyncio
    async def test_get_chat_completion_success(self, sample_chat_messages, sample_model_config):
        """
        Test successful chat completion with Mock adapter.
        
        Purpose: Verify that the Mock adapter generates appropriate mock responses
        for chat completion requests without requiring external dependencies.
        
        Checkpoints:
        - Adapter returns LLMResponse instance
        - Response content includes "Mock response for:" prefix
        - User message content is included in response (context awareness)
        - Model name matches configuration
        - Usage statistics are provided (mock values)
        - Finish reason is set appropriately
        
        Mocks: None - tests actual mock adapter implementation
        
        Dependencies:
        - MockAdapter class from adapters module
        - LLMResponse model for response validation
        
        Notes: The mock adapter should generate deterministic responses that
        include context from the input messages for testing purposes.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        
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
        """
        Test successful embedding generation with Mock adapter.
        
        Purpose: Verify that the Mock adapter generates appropriate mock embeddings
        for testing without requiring external embedding services.
        
        Checkpoints:
        - Adapter returns EmbeddingResponse instance
        - Number of embeddings matches number of input texts
        - Embedding dimensions are standard (384)
        - Model name matches configuration
        - Usage statistics are provided (mock values)
        - Embeddings are deterministic for same input
        
        Mocks: None - tests actual mock adapter implementation
        
        Dependencies:
        - MockAdapter class from adapters module
        - EmbeddingResponse model for response validation
        
        Notes: Mock embeddings should be deterministic to enable consistent
        testing while providing realistic vector dimensions.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        
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
        """
        Test that mock adapter is always available.
        
        Purpose: Verify that the Mock adapter always reports as available,
        ensuring tests can run without external dependencies.
        
        Checkpoints:
        - is_available() always returns True
        - No external dependencies are required
        - Adapter is always ready for testing
        
        Mocks: None - tests actual mock adapter behavior
        
        Dependencies:
        - MockAdapter class from adapters module
        
        Notes: Mock adapter should always be available to ensure tests can
        run in any environment without external service dependencies.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        
        # Create adapter
        adapter = MockAdapter()
        
        # Test availability
        result = await adapter.is_available()
        
        # Assertions
        assert result is True
    
    @pytest.mark.asyncio
    async def test_mock_response_includes_context(self, sample_model_config):
        """
        Test that mock responses include context from messages.
        
        Purpose: Verify that the Mock adapter generates different responses based
        on input context, making tests more realistic and debuggable.
        
        Checkpoints:
        - Different input messages produce different responses
        - Input message content is reflected in response
        - Context awareness improves test realism
        
        Mocks: None - tests actual mock adapter context handling
        
        Dependencies:
        - MockAdapter class from adapters module
        - ChatMessage for input variation
        
        Notes: Context-aware mock responses help identify issues in message
        handling and make test failures more informative.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        
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
        """
        Test mock adapter initialization.
        
        Purpose: Verify that the Mock adapter can be initialized with custom
        parameters for response delay and failure simulation.
        
        Checkpoints:
        - Default initialization sets reasonable default values
        - Custom initialization preserves provided parameters
        - Response delay and failure rate are configurable
        
        Mocks: None - tests actual mock adapter initialization
        
        Dependencies:
        - MockAdapter class from adapters module
        
        Notes: Configurable mock behavior enables testing of error conditions
        and performance scenarios without external dependencies.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        
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
        """
        Test mock adapter simulated failures.
        
        Purpose: Verify that the Mock adapter can simulate API failures for
        testing error handling and resilience scenarios.
        
        Checkpoints:
        - High failure rate (100%) consistently produces errors
        - Simulated failures raise LLMProviderError
        - Error message indicates simulated failure
        - Failure simulation enables error path testing
        
        Mocks: None - tests actual mock adapter failure simulation
        
        Dependencies:
        - MockAdapter class from adapters module
        - LLMProviderError for error validation
        - pytest for exception testing
        
        Notes: Simulated failures enable testing of error handling, retry logic,
        and graceful degradation without relying on actual API failures.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        from metadata_code_extractor.integrations.llm.client import LLMProviderError
        
        # Create adapter with 100% failure rate
        adapter = MockAdapter(fail_rate=1.0)
        
        # Test that it raises an error
        with pytest.raises(LLMProviderError, match="Simulated failure"):
            await adapter.get_chat_completion(sample_chat_messages, sample_model_config)
    
    @pytest.mark.asyncio
    async def test_mock_adapter_response_delay(self, sample_chat_messages, sample_model_config):
        """
        Test mock adapter response delay.
        
        Purpose: Verify that the Mock adapter can simulate response delays for
        testing timeout handling and performance scenarios.
        
        Checkpoints:
        - Configured delay is actually applied
        - Response time meets minimum delay requirement
        - Delayed responses still return valid results
        - Delay simulation enables performance testing
        
        Mocks: None - tests actual mock adapter delay implementation
        
        Dependencies:
        - MockAdapter class from adapters module
        - time module for delay measurement
        
        Notes: Response delay simulation enables testing of timeout handling,
        user experience with slow APIs, and performance optimization scenarios.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
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
        """
        Test creating OpenAI adapter through factory.
        
        Purpose: Verify that the adapter factory can create OpenAI adapters
        with proper configuration and initialization.
        
        Checkpoints:
        - Factory creates OpenAIAdapter instance
        - Configuration is passed through correctly
        - Adapter type is correct
        
        Mocks:
        - OpenAI client constructor to avoid actual client creation
        
        Dependencies:
        - create_adapter factory function
        - OpenAIAdapter class
        - unittest.mock.patch for client mocking
        
        Notes: Factory pattern enables dynamic adapter creation based on
        configuration, supporting multiple LLM providers.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import create_adapter
        
        config = {
            "provider": "openai",
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1"
        }
        
        with patch('metadata_code_extractor.integrations.llm.providers.adapters.OpenAI'):
            adapter = create_adapter(config)
            
            from metadata_code_extractor.integrations.llm.providers.adapters import OpenAIAdapter
            assert isinstance(adapter, OpenAIAdapter)
    
    def test_create_mock_adapter(self):
        """
        Test creating Mock adapter through factory.
        
        Purpose: Verify that the adapter factory can create Mock adapters
        with custom configuration parameters.
        
        Checkpoints:
        - Factory creates MockAdapter instance
        - Custom configuration parameters are preserved
        - Adapter type is correct
        
        Mocks: None - tests actual mock adapter creation
        
        Dependencies:
        - create_adapter factory function
        - MockAdapter class
        
        Notes: Mock adapter creation through factory enables consistent
        adapter instantiation patterns across different provider types.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import create_adapter
        
        config = {
            "provider": "mock",
            "response_delay": 0.2,
            "fail_rate": 0.1
        }
        
        adapter = create_adapter(config)
        
        from metadata_code_extractor.integrations.llm.providers.adapters import MockAdapter
        assert isinstance(adapter, MockAdapter)
        assert adapter.response_delay == 0.2
        assert adapter.fail_rate == 0.1
    
    def test_create_adapter_invalid_provider(self):
        """
        Test creating adapter with invalid provider.
        
        Purpose: Verify that the adapter factory properly handles invalid
        provider names and raises appropriate errors.
        
        Checkpoints:
        - Invalid provider name raises ValueError
        - Error message indicates unknown provider
        - Factory validates provider names
        
        Mocks: None - tests actual factory validation
        
        Dependencies:
        - create_adapter factory function
        - pytest for exception testing
        
        Notes: Proper error handling prevents runtime failures when
        unsupported providers are specified in configuration.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import create_adapter
        
        config = {"provider": "invalid"}
        
        with pytest.raises(ValueError, match="Unknown provider"):
            create_adapter(config)
    
    def test_create_adapter_missing_provider(self):
        """
        Test creating adapter without provider specified.
        
        Purpose: Verify that the adapter factory requires a provider to be
        specified and raises appropriate errors when missing.
        
        Checkpoints:
        - Missing provider raises ValueError
        - Error message indicates provider requirement
        - Factory validates required configuration
        
        Mocks: None - tests actual factory validation
        
        Dependencies:
        - create_adapter factory function
        - pytest for exception testing
        
        Notes: Requiring explicit provider specification prevents ambiguous
        configuration and ensures intentional adapter selection.
        """
        from metadata_code_extractor.integrations.llm.providers.adapters import create_adapter
        
        config = {}
        
        with pytest.raises(ValueError, match="Provider must be specified"):
            create_adapter(config) 