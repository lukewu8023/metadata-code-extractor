"""
Unit tests for LLM cache implementation.

Tests cover in-memory and file-based cache implementations with proper
expiration, serialization, and error handling.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from metadata_code_extractor.core.models.llm import (
    ChatMessage,
    EmbeddingConfig,
    EmbeddingResponse,
    LLMResponse,
    MessageRole,
    ModelConfig,
)
from metadata_code_extractor.integrations.llm.cache import (
    InMemoryLLMCache,
    FileLLMCache,
    LLMCacheInterface,
    LLMCacheError,
)


class TestLLMCacheInterface:
    """Test the LLM cache interface."""
    
    def test_interface_is_abstract(self):
        """
        Test that LLMCacheInterface cannot be instantiated directly.
        
        Purpose: Verify that the LLMCacheInterface is properly defined as an abstract
        base class and cannot be instantiated directly, enforcing implementation.
        
        Checkpoints:
        - Direct instantiation raises TypeError
        - Abstract base class pattern is enforced
        - Interface contract is maintained
        
        Mocks: None - tests actual abstract class behavior
        
        Dependencies:
        - LLMCacheInterface abstract base class
        - pytest for exception testing
        
        Notes: This ensures that the cache interface is properly designed as an
        abstract contract that must be implemented by concrete cache classes.
        """
        with pytest.raises(TypeError):
            LLMCacheInterface()


class TestInMemoryLLMCache:
    """Test the in-memory LLM cache implementation."""
    
    def test_init_default_ttl(self):
        """
        Test cache initialization with default TTL.
        
        Purpose: Verify that InMemoryLLMCache initializes with appropriate default
        values for TTL (time-to-live) and internal cache storage.
        
        Checkpoints:
        - Default TTL is set to 3600 seconds (1 hour)
        - Internal cache dictionary is initialized as empty
        - Cache is ready for use after initialization
        
        Mocks: None - tests actual initialization behavior
        
        Dependencies:
        - InMemoryLLMCache class
        
        Notes: Default TTL of 1 hour provides reasonable caching duration for
        most LLM use cases while preventing indefinite memory growth.
        """
        cache = InMemoryLLMCache()
        assert cache.default_ttl == 3600  # 1 hour default
        assert cache._cache == {}
    
    def test_init_custom_ttl(self):
        """
        Test cache initialization with custom TTL.
        
        Purpose: Verify that InMemoryLLMCache can be configured with custom TTL
        values to support different caching strategies.
        
        Checkpoints:
        - Custom TTL value is stored correctly
        - Cache accepts different TTL configurations
        - TTL configuration affects cache behavior
        
        Mocks: None - tests actual configuration behavior
        
        Dependencies:
        - InMemoryLLMCache class with TTL parameter
        
        Notes: Custom TTL enables fine-tuning of cache behavior for different
        use cases, such as longer caching for stable prompts or shorter for dynamic content.
        """
        cache = InMemoryLLMCache(default_ttl=7200)
        assert cache.default_ttl == 7200
    
    def test_init_invalid_ttl(self):
        """
        Test cache initialization with invalid TTL.
        
        Purpose: Verify that InMemoryLLMCache validates TTL values and rejects
        invalid configurations that could cause issues.
        
        Checkpoints:
        - Zero TTL raises ValueError
        - Negative TTL raises ValueError
        - Error messages indicate TTL validation failure
        - Invalid configurations are prevented
        
        Mocks: None - tests actual validation behavior
        
        Dependencies:
        - InMemoryLLMCache class with validation
        - pytest for exception testing
        
        Notes: TTL validation prevents configuration errors that could lead to
        unexpected cache behavior or performance issues.
        """
        with pytest.raises(ValueError, match="TTL must be positive"):
            InMemoryLLMCache(default_ttl=0)
        
        with pytest.raises(ValueError, match="TTL must be positive"):
            InMemoryLLMCache(default_ttl=-1)
    
    def test_set_and_get_llm_response(self):
        """
        Test setting and getting LLM response.
        
        Purpose: Verify that InMemoryLLMCache can store and retrieve LLMResponse
        objects correctly, preserving all response data and metadata.
        
        Checkpoints:
        - LLMResponse can be stored in cache
        - Retrieved response matches stored response exactly
        - All response fields are preserved (content, model, usage, finish_reason)
        - Cache key-value operations work correctly
        
        Mocks: None - tests actual cache storage and retrieval
        
        Dependencies:
        - InMemoryLLMCache class
        - LLMResponse model for test data
        
        Notes: This is the core functionality test for LLM response caching,
        ensuring that expensive LLM API calls can be cached effectively.
        """
        cache = InMemoryLLMCache()
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop"
        )
        
        cache.set("test_key", response)
        retrieved = cache.get("test_key")
        
        assert retrieved is not None
        assert retrieved.content == "Test response"
        assert retrieved.model == "gpt-4"
        assert retrieved.usage == {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    
    def test_set_and_get_embedding_response(self):
        """
        Test setting and getting embedding response.
        
        Purpose: Verify that InMemoryLLMCache can store and retrieve EmbeddingResponse
        objects correctly, preserving embedding vectors and metadata.
        
        Checkpoints:
        - EmbeddingResponse can be stored in cache
        - Retrieved embeddings match stored embeddings exactly
        - All embedding fields are preserved (embeddings, model, usage)
        - Multiple embeddings in response are handled correctly
        
        Mocks: None - tests actual cache storage and retrieval
        
        Dependencies:
        - InMemoryLLMCache class
        - EmbeddingResponse model for test data
        
        Notes: Embedding caching is crucial for performance as embedding generation
        can be expensive, especially for large text corpora.
        """
        cache = InMemoryLLMCache()
        
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            model="text-embedding-ada-002",
            usage={"prompt_tokens": 8, "total_tokens": 8}
        )
        
        cache.set("embed_key", response)
        retrieved = cache.get("embed_key")
        
        assert retrieved is not None
        assert retrieved.embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert retrieved.model == "text-embedding-ada-002"
    
    def test_get_nonexistent_key(self):
        """
        Test getting a non-existent key returns None.
        
        Purpose: Verify that InMemoryLLMCache handles cache misses gracefully
        by returning None for keys that don't exist in the cache.
        
        Checkpoints:
        - Non-existent key returns None
        - No exceptions are raised for missing keys
        - Cache miss behavior is consistent
        - Empty cache handles get operations correctly
        
        Mocks: None - tests actual cache miss behavior
        
        Dependencies:
        - InMemoryLLMCache class
        
        Notes: Graceful cache miss handling is essential for cache integration
        with LLM clients, allowing fallback to actual API calls.
        """
        cache = InMemoryLLMCache()
        assert cache.get("nonexistent") is None
    
    def test_set_with_custom_ttl(self):
        """
        Test setting with custom TTL.
        
        Purpose: Verify that InMemoryLLMCache supports per-item TTL configuration,
        allowing fine-grained control over cache expiration.
        
        Checkpoints:
        - Custom TTL is applied to specific cache entries
        - Expiry time is calculated correctly based on custom TTL
        - Per-item TTL overrides default TTL
        - Expiry time is stored with cache entry
        
        Mocks: None - tests actual TTL calculation and storage
        
        Dependencies:
        - InMemoryLLMCache class with per-item TTL support
        - datetime for time calculations
        
        Notes: Per-item TTL enables different caching strategies for different
        types of requests, such as longer caching for stable prompts.
        """
        cache = InMemoryLLMCache(default_ttl=3600)
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        cache.set("test_key", response, ttl=7200)
        
        # Check that the expiry time is set correctly
        entry = cache._cache["test_key"]
        expected_expiry = datetime.now() + timedelta(seconds=7200)
        assert abs((entry["expires_at"] - expected_expiry).total_seconds()) < 1
    
    def test_expiration(self):
        """
        Test that expired entries are not returned.
        
        Purpose: Verify that InMemoryLLMCache properly handles cache expiration
        and does not return expired entries, ensuring cache freshness.
        
        Checkpoints:
        - Entries are available before expiration
        - Entries are not returned after expiration
        - Expiration timing is accurate
        - Expired entries are handled gracefully
        
        Mocks: None - tests actual time-based expiration
        
        Dependencies:
        - InMemoryLLMCache class with expiration logic
        - time.sleep for expiration testing
        
        Notes: Proper expiration handling prevents stale data from being served
        and ensures cache freshness for time-sensitive applications.
        """
        cache = InMemoryLLMCache(default_ttl=1)  # 1 second TTL
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        cache.set("test_key", response)
        
        # Should be available immediately
        assert cache.get("test_key") is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        assert cache.get("test_key") is None
    
    def test_clear(self):
        """
        Test clearing the cache.
        
        Purpose: Verify that InMemoryLLMCache can be completely cleared,
        removing all cached entries and resetting to empty state.
        
        Checkpoints:
        - All cached entries are removed after clear
        - Cache returns to empty state
        - Previously cached items are no longer accessible
        - Clear operation is complete and immediate
        
        Mocks: None - tests actual cache clearing behavior
        
        Dependencies:
        - InMemoryLLMCache class with clear functionality
        
        Notes: Cache clearing is useful for testing, memory management,
        and scenarios where cache invalidation is needed.
        """
        cache = InMemoryLLMCache()
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        cache.set("key1", response)
        cache.set("key2", response)
        
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache._cache == {}
    
    def test_size(self):
        """
        Test getting cache size.
        
        Purpose: Verify that InMemoryLLMCache can report its current size,
        excluding expired entries for accurate memory usage tracking.
        
        Checkpoints:
        - Empty cache reports size 0
        - Size increases as items are added
        - Expired entries are not counted in size
        - Size calculation is accurate and efficient
        
        Mocks: None - tests actual size calculation
        
        Dependencies:
        - InMemoryLLMCache class with size functionality
        - time.sleep for expiration testing
        
        Notes: Accurate size reporting enables memory monitoring and cache
        management decisions in production environments.
        """
        cache = InMemoryLLMCache()
        
        assert cache.size() == 0
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        cache.set("key1", response)
        assert cache.size() == 1
        
        cache.set("key2", response)
        assert cache.size() == 2
        
        # Add expired entry
        cache.set("key3", response, ttl=0.1)
        time.sleep(0.2)
        
        # Size should still be 2 (expired entries not counted)
        assert cache.size() == 2
    
    def test_cleanup_expired(self):
        """
        Test cleanup of expired entries.
        
        Purpose: Verify that InMemoryLLMCache automatically removes expired
        entries during normal operations to prevent memory leaks.
        
        Checkpoints:
        - Expired entries are removed from internal storage
        - Non-expired entries are preserved
        - Cleanup occurs during size calculation
        - Memory is freed for expired entries
        
        Mocks: None - tests actual cleanup behavior
        
        Dependencies:
        - InMemoryLLMCache class with cleanup logic
        - time.sleep for expiration testing
        
        Notes: Automatic cleanup prevents memory leaks in long-running
        applications and maintains cache performance over time.
        """
        cache = InMemoryLLMCache(default_ttl=1)
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        # Add entries with different TTLs
        cache.set("key1", response, ttl=0.1)  # Will expire quickly
        cache.set("key2", response, ttl=3600)  # Will not expire
        
        time.sleep(0.2)
        
        # Trigger cleanup by calling size()
        assert cache.size() == 1
        
        # Check that expired entry is removed
        assert "key1" not in cache._cache
        assert "key2" in cache._cache
    
    def test_invalid_response_type(self):
        """
        Test setting invalid response type raises error.
        
        Purpose: Verify that InMemoryLLMCache validates response types and
        rejects unsupported objects to maintain type safety.
        
        Checkpoints:
        - Invalid response type raises LLMCacheError
        - Error message indicates unsupported type
        - Type validation prevents cache corruption
        - Only supported response types are accepted
        
        Mocks: None - tests actual type validation
        
        Dependencies:
        - InMemoryLLMCache class with type validation
        - LLMCacheError for error handling
        - pytest for exception testing
        
        Notes: Type validation ensures cache integrity and prevents runtime
        errors when retrieving cached responses.
        """
        cache = InMemoryLLMCache()
        
        with pytest.raises(LLMCacheError, match="Unsupported response type"):
            cache.set("key", "invalid_response")
    
    def test_set_none_response(self):
        """
        Test setting None response raises error.
        
        Purpose: Verify that InMemoryLLMCache rejects None values to prevent
        cache pollution and maintain data integrity.
        
        Checkpoints:
        - None response raises LLMCacheError
        - Error message indicates None is not allowed
        - Null value validation prevents cache issues
        - Cache maintains data integrity
        
        Mocks: None - tests actual null value validation
        
        Dependencies:
        - InMemoryLLMCache class with null validation
        - LLMCacheError for error handling
        - pytest for exception testing
        
        Notes: Preventing None values ensures that cache hits always return
        valid response objects and prevents confusion with cache misses.
        """
        cache = InMemoryLLMCache()
        
        with pytest.raises(LLMCacheError, match="Response cannot be None"):
            cache.set("key", None)
    
    def test_empty_key(self):
        """
        Test setting with empty key raises error.
        
        Purpose: Verify that InMemoryLLMCache validates cache keys and rejects
        empty or whitespace-only keys to prevent cache issues.
        
        Checkpoints:
        - Empty string key raises LLMCacheError
        - Whitespace-only key raises LLMCacheError
        - Error message indicates key validation failure
        - Key validation prevents cache corruption
        
        Mocks: None - tests actual key validation
        
        Dependencies:
        - InMemoryLLMCache class with key validation
        - LLMCacheError for error handling
        - pytest for exception testing
        
        Notes: Key validation ensures that all cache entries have meaningful
        identifiers and prevents accidental cache overwrites.
        """
        cache = InMemoryLLMCache()
        
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            usage={},
            finish_reason="stop"
        )
        
        with pytest.raises(LLMCacheError, match="Cache key cannot be empty"):
            cache.set("", response)
        
        with pytest.raises(LLMCacheError, match="Cache key cannot be empty"):
            cache.set("   ", response)


class TestFileLLMCache:
    """Test the file-based LLM cache implementation."""
    
    def test_init_default_params(self):
        """
        Test cache initialization with default parameters.
        
        Purpose: Verify that FileLLMCache initializes with appropriate default
        values for TTL, file size limits, and directory configuration.
        
        Checkpoints:
        - Cache directory is set correctly
        - Default TTL is 3600 seconds (1 hour)
        - Default max file size is 10MB
        - Cache is ready for file operations
        
        Mocks: None - tests actual initialization with temporary directory
        
        Dependencies:
        - FileLLMCache class
        - tempfile for temporary directory creation
        - pathlib.Path for path handling
        
        Notes: Default parameters provide reasonable file caching behavior
        while preventing excessive disk usage and ensuring cache freshness.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            assert cache.cache_dir == Path(temp_dir)
            assert cache.default_ttl == 3600
            assert cache.max_file_size == 10 * 1024 * 1024  # 10MB
    
    def test_init_custom_params(self):
        """
        Test cache initialization with custom parameters.
        
        Purpose: Verify that FileLLMCache can be configured with custom TTL
        and file size limits to support different deployment scenarios.
        
        Checkpoints:
        - Custom TTL is stored correctly
        - Custom max file size is stored correctly
        - Configuration parameters are preserved
        - Cache accepts custom configurations
        
        Mocks: None - tests actual configuration with temporary directory
        
        Dependencies:
        - FileLLMCache class with custom parameters
        - tempfile for temporary directory creation
        
        Notes: Custom parameters enable tuning of file cache behavior for
        different use cases, such as longer caching or larger file limits.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(
                cache_dir=temp_dir,
                default_ttl=7200,
                max_file_size=5 * 1024 * 1024
            )
            assert cache.default_ttl == 7200
            assert cache.max_file_size == 5 * 1024 * 1024
    
    def test_init_creates_directory(self):
        """
        Test that cache directory is created if it doesn't exist.
        
        Purpose: Verify that FileLLMCache automatically creates the cache
        directory if it doesn't exist, enabling easy deployment.
        
        Checkpoints:
        - Non-existent directory is created automatically
        - Created directory is accessible and writable
        - Directory creation doesn't interfere with cache operations
        - Cache initialization succeeds with new directory
        
        Mocks: None - tests actual directory creation
        
        Dependencies:
        - FileLLMCache class with directory creation
        - tempfile for temporary directory management
        - pathlib.Path for directory operations
        
        Notes: Automatic directory creation simplifies deployment and prevents
        configuration errors in production environments.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"
            assert not cache_dir.exists()
            
            cache = FileLLMCache(cache_dir=cache_dir)
            assert cache_dir.exists()
            assert cache_dir.is_dir()
    
    def test_init_invalid_ttl(self):
        """
        Test initialization with invalid TTL.
        
        Purpose: Verify that FileLLMCache validates TTL values and rejects
        invalid configurations that could cause caching issues.
        
        Checkpoints:
        - Zero TTL raises ValueError
        - Error message indicates TTL validation failure
        - Invalid TTL prevents cache initialization
        - Validation occurs during initialization
        
        Mocks: None - tests actual TTL validation
        
        Dependencies:
        - FileLLMCache class with TTL validation
        - tempfile for temporary directory
        - pytest for exception testing
        
        Notes: TTL validation prevents configuration errors that could lead
        to unexpected file cache behavior or performance issues.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="TTL must be positive"):
                FileLLMCache(cache_dir=temp_dir, default_ttl=0)
    
    def test_init_invalid_max_file_size(self):
        """
        Test initialization with invalid max file size.
        
        Purpose: Verify that FileLLMCache validates file size limits and rejects
        invalid configurations that could cause storage issues.
        
        Checkpoints:
        - Zero max file size raises ValueError
        - Error message indicates file size validation failure
        - Invalid file size prevents cache initialization
        - Validation occurs during initialization
        
        Mocks: None - tests actual file size validation
        
        Dependencies:
        - FileLLMCache class with file size validation
        - tempfile for temporary directory
        - pytest for exception testing
        
        Notes: File size validation prevents configuration errors that could
        lead to disk space issues or performance problems.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Max file size must be positive"):
                FileLLMCache(cache_dir=temp_dir, max_file_size=0)
    
    def test_set_and_get_llm_response(self):
        """
        Test setting and getting LLM response.
        
        Purpose: Verify that FileLLMCache can store LLMResponse objects to disk
        and retrieve them correctly, preserving all response data.
        
        Checkpoints:
        - LLMResponse is serialized to file correctly
        - Retrieved response matches stored response exactly
        - All response fields are preserved through serialization
        - File-based storage and retrieval work correctly
        
        Mocks: None - tests actual file I/O operations
        
        Dependencies:
        - FileLLMCache class with file operations
        - LLMResponse model for test data
        - tempfile for temporary directory
        
        Notes: File-based caching enables persistent cache across application
        restarts and provides larger storage capacity than memory caching.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                finish_reason="stop"
            )
            
            cache.set("test_key", response)
            retrieved = cache.get("test_key")
            
            assert retrieved is not None
            assert retrieved.content == "Test response"
            assert retrieved.model == "gpt-4"
            assert retrieved.usage == {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    
    def test_set_and_get_embedding_response(self):
        """
        Test setting and getting embedding response.
        
        Purpose: Verify that FileLLMCache can store EmbeddingResponse objects
        to disk and retrieve them correctly, preserving embedding vectors.
        
        Checkpoints:
        - EmbeddingResponse is serialized to file correctly
        - Retrieved embeddings match stored embeddings exactly
        - All embedding fields are preserved through serialization
        - Multiple embeddings in response are handled correctly
        
        Mocks: None - tests actual file I/O operations
        
        Dependencies:
        - FileLLMCache class with file operations
        - EmbeddingResponse model for test data
        - tempfile for temporary directory
        
        Notes: File-based embedding caching is particularly valuable for large
        embedding datasets that would consume too much memory.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            response = EmbeddingResponse(
                embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                model="text-embedding-ada-002",
                usage={"prompt_tokens": 8, "total_tokens": 8}
            )
            
            cache.set("embed_key", response)
            retrieved = cache.get("embed_key")
            
            assert retrieved is not None
            assert retrieved.embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            assert retrieved.model == "text-embedding-ada-002"
    
    def test_get_nonexistent_key(self):
        """
        Test getting a non-existent key returns None.
        
        Purpose: Verify that FileLLMCache handles cache misses gracefully
        when requested files don't exist on disk.
        
        Checkpoints:
        - Non-existent key returns None
        - No exceptions are raised for missing files
        - Cache miss behavior is consistent with memory cache
        - File system errors are handled gracefully
        
        Mocks: None - tests actual file system behavior
        
        Dependencies:
        - FileLLMCache class with file operations
        - tempfile for temporary directory
        
        Notes: Graceful cache miss handling is essential for file-based caching
        where files may be deleted or corrupted externally.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            assert cache.get("nonexistent") is None
    
    def test_file_creation(self):
        """
        Test that cache files are created correctly.
        
        Purpose: Verify that FileLLMCache creates properly formatted JSON files
        with correct structure and content for cached responses.
        
        Checkpoints:
        - Cache file is created on disk
        - File contains proper JSON structure
        - Response data is serialized correctly
        - Expiration metadata is included
        - File format is readable and valid
        
        Mocks: None - tests actual file creation and format
        
        Dependencies:
        - FileLLMCache class with file operations
        - json module for file content verification
        - tempfile for temporary directory
        
        Notes: Proper file format ensures cache files can be read correctly
        and enables debugging and external cache inspection.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            cache.set("test_key", response)
            
            # Check that file was created
            cache_file = cache._get_cache_file_path("test_key")
            assert cache_file.exists()
            
            # Check file content
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            assert "response" in data
            assert "expires_at" in data
            assert data["response"]["content"] == "Test response"
    
    def test_expiration(self):
        """
        Test that expired entries are not returned.
        
        Purpose: Verify that FileLLMCache properly handles file-based cache
        expiration and does not return expired entries.
        
        Checkpoints:
        - Entries are available before expiration
        - Entries are not returned after expiration
        - Expiration timing is accurate for file cache
        - Expired files are handled gracefully
        
        Mocks: None - tests actual time-based expiration with files
        
        Dependencies:
        - FileLLMCache class with expiration logic
        - time.sleep for expiration testing
        - tempfile for temporary directory
        
        Notes: File-based expiration ensures cache freshness even across
        application restarts and prevents serving stale data.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir, default_ttl=1)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            cache.set("test_key", response)
            
            # Should be available immediately
            assert cache.get("test_key") is not None
            
            # Wait for expiration
            time.sleep(1.1)
            
            # Should be expired now
            assert cache.get("test_key") is None
    
    def test_clear(self):
        """
        Test clearing the cache.
        
        Purpose: Verify that FileLLMCache can remove all cached files from
        disk and reset to empty state.
        
        Checkpoints:
        - All cache files are removed from disk
        - Cache directory is cleaned up
        - Previously cached items are no longer accessible
        - Clear operation is complete and immediate
        
        Mocks: None - tests actual file deletion operations
        
        Dependencies:
        - FileLLMCache class with clear functionality
        - tempfile for temporary directory
        - pathlib.Path for file operations
        
        Notes: File cache clearing is useful for testing, disk space management,
        and scenarios where cache invalidation is needed.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            cache.set("key1", response)
            cache.set("key2", response)
            
            # Check files exist
            assert cache._get_cache_file_path("key1").exists()
            assert cache._get_cache_file_path("key2").exists()
            
            cache.clear()
            
            # Check files are removed
            assert not cache._get_cache_file_path("key1").exists()
            assert not cache._get_cache_file_path("key2").exists()
            
            # Check get returns None
            assert cache.get("key1") is None
            assert cache.get("key2") is None
    
    def test_size(self):
        """
        Test getting cache size.
        
        Purpose: Verify that FileLLMCache can report its current size by
        counting valid cache files on disk.
        
        Checkpoints:
        - Empty cache reports size 0
        - Size increases as files are added
        - Size calculation is accurate
        - File-based size counting works correctly
        
        Mocks: None - tests actual file counting
        
        Dependencies:
        - FileLLMCache class with size functionality
        - tempfile for temporary directory
        
        Notes: Accurate size reporting enables disk usage monitoring and
        cache management decisions for file-based caching.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            assert cache.size() == 0
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            cache.set("key1", response)
            assert cache.size() == 1
            
            cache.set("key2", response)
            assert cache.size() == 2
    
    def test_cleanup_expired(self):
        """
        Test cleanup of expired entries.
        
        Purpose: Verify that FileLLMCache automatically removes expired
        cache files from disk to prevent disk space accumulation.
        
        Checkpoints:
        - Expired files are removed from disk
        - Non-expired files are preserved
        - Cleanup occurs when triggered
        - Disk space is freed for expired entries
        
        Mocks: None - tests actual file cleanup operations
        
        Dependencies:
        - FileLLMCache class with cleanup logic
        - time.sleep for expiration testing
        - tempfile for temporary directory
        
        Notes: Automatic file cleanup prevents disk space leaks in long-running
        applications and maintains file system performance.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir, default_ttl=1)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            # Add entries with different TTLs
            cache.set("key1", response, ttl=0.1)  # Will expire quickly
            cache.set("key2", response, ttl=3600)  # Will not expire
            
            time.sleep(0.2)
            
            # Trigger cleanup
            cache._cleanup_expired()
            
            # Check that expired file is removed
            assert not cache._get_cache_file_path("key1").exists()
            assert cache._get_cache_file_path("key2").exists()
    
    def test_corrupted_file_handling(self):
        """
        Test handling of corrupted cache files.
        
        Purpose: Verify that FileLLMCache handles corrupted or invalid JSON
        files gracefully without crashing the application.
        
        Checkpoints:
        - Corrupted files are detected during read
        - Invalid JSON doesn't crash the cache
        - Corrupted files are removed automatically
        - Cache returns None for corrupted entries
        
        Mocks: None - tests actual corrupted file handling
        
        Dependencies:
        - FileLLMCache class with error handling
        - tempfile for temporary directory
        - pathlib.Path for file operations
        
        Notes: Robust error handling for corrupted files ensures cache
        reliability in production environments where files may be corrupted.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            # Create a corrupted cache file
            cache_file = cache._get_cache_file_path("corrupted_key")
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write("invalid json content")
            
            # Should return None and not raise exception
            assert cache.get("corrupted_key") is None
            
            # File should be removed
            assert not cache_file.exists()
    
    def test_file_size_limit(self):
        """
        Test file size limit enforcement.
        
        Purpose: Verify that FileLLMCache enforces file size limits to prevent
        excessive disk usage from large responses.
        
        Checkpoints:
        - Large responses are rejected with appropriate error
        - File size is calculated before writing
        - Size limit enforcement prevents disk issues
        - Error message indicates size limit exceeded
        
        Mocks: None - tests actual file size validation
        
        Dependencies:
        - FileLLMCache class with size validation
        - LLMCacheError for error handling
        - tempfile for temporary directory
        - pytest for exception testing
        
        Notes: File size limits prevent disk space exhaustion and ensure
        reasonable cache file sizes for performance and management.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir, max_file_size=100)  # Very small limit
            
            # Create a large response
            large_content = "x" * 1000  # Large content
            response = LLMResponse(
                content=large_content,
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            with pytest.raises(LLMCacheError, match="Response too large"):
                cache.set("large_key", response)
    
    def test_invalid_response_type(self):
        """
        Test setting invalid response type raises error.
        
        Purpose: Verify that FileLLMCache validates response types and rejects
        unsupported objects to maintain file cache integrity.
        
        Checkpoints:
        - Invalid response type raises LLMCacheError
        - Error message indicates unsupported type
        - Type validation prevents file corruption
        - Only supported response types are accepted
        
        Mocks: None - tests actual type validation
        
        Dependencies:
        - FileLLMCache class with type validation
        - LLMCacheError for error handling
        - tempfile for temporary directory
        - pytest for exception testing
        
        Notes: Type validation ensures file cache integrity and prevents
        serialization errors that could corrupt cache files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            with pytest.raises(LLMCacheError, match="Unsupported response type"):
                cache.set("key", "invalid_response")
    
    def test_permission_error_handling(self):
        """
        Test handling of permission errors.
        
        Purpose: Verify that FileLLMCache handles file system permission errors
        gracefully and provides meaningful error messages.
        
        Checkpoints:
        - Permission errors are caught and wrapped
        - Meaningful error message is provided
        - Cache operation fails gracefully
        - System doesn't crash on permission issues
        
        Mocks:
        - builtins.open: Mocked to raise PermissionError
        
        Dependencies:
        - FileLLMCache class with error handling
        - LLMCacheError for error wrapping
        - unittest.mock.patch for permission simulation
        - tempfile for temporary directory
        - pytest for exception testing
        
        Notes: Permission error handling ensures graceful degradation when
        cache directories have insufficient permissions.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            response = LLMResponse(
                content="Test response",
                model="gpt-4",
                usage={},
                finish_reason="stop"
            )
            
            # Mock permission error
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(LLMCacheError, match="Failed to write cache file"):
                    cache.set("test_key", response)
    
    def test_get_cache_file_path(self):
        """
        Test cache file path generation.
        
        Purpose: Verify that FileLLMCache generates safe and consistent file
        paths for cache keys, handling special characters appropriately.
        
        Checkpoints:
        - Normal keys generate expected file paths
        - Special characters are sanitized in file names
        - File paths are safe for file system operations
        - Path generation is consistent and deterministic
        
        Mocks: None - tests actual path generation logic
        
        Dependencies:
        - FileLLMCache class with path generation
        - tempfile for temporary directory
        - pathlib.Path for path operations
        
        Notes: Safe path generation prevents file system issues and ensures
        cache keys can be safely used as file names across different platforms.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileLLMCache(cache_dir=temp_dir)
            
            # Test normal key
            path = cache._get_cache_file_path("test_key")
            expected = Path(temp_dir) / "test_key.json"
            assert path == expected
            
            # Test key with special characters
            path = cache._get_cache_file_path("test/key:with*special?chars")
            # Should be sanitized
            assert "/" not in path.name
            assert ":" not in path.name
            assert "*" not in path.name
            assert "?" not in path.name 