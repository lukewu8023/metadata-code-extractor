"""
LLM Cache implementation for the Metadata Code Extractor.

This module provides caching functionality for LLM responses to reduce
redundant API calls and improve performance. Supports both in-memory
and file-based caching with configurable TTL and cleanup.
"""

import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

from metadata_code_extractor.core.models.llm import (
    EmbeddingResponse,
    LLMResponse,
)


class LLMCacheError(Exception):
    """Exception raised when there's an error with the LLM cache."""
    pass


class LLMCacheInterface(ABC):
    """Abstract interface for LLM cache implementations."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Union[LLMResponse, EmbeddingResponse]]:
        """
        Get a cached response by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        pass
    
    @abstractmethod
    def set(
        self, 
        key: str, 
        response: Union[LLMResponse, EmbeddingResponse],
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a cached response.
        
        Args:
            key: Cache key
            response: Response to cache
            ttl: Time to live in seconds (optional)
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached entries."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get the number of cached entries."""
        pass


class InMemoryLLMCache(LLMCacheInterface):
    """
    In-memory LLM cache implementation.
    
    Stores cached responses in memory with TTL support and automatic cleanup.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the in-memory cache.
        
        Args:
            default_ttl: Default time to live in seconds (default: 1 hour)
            
        Raises:
            ValueError: If TTL is not positive
        """
        if default_ttl <= 0:
            raise ValueError("TTL must be positive")
        
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Union[LLMResponse, EmbeddingResponse]]:
        """
        Get a cached response by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if datetime.now() > entry["expires_at"]:
            del self._cache[key]
            return None
        
        return entry["response"]
    
    def set(
        self, 
        key: str, 
        response: Union[LLMResponse, EmbeddingResponse],
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a cached response.
        
        Args:
            key: Cache key
            response: Response to cache
            ttl: Time to live in seconds (optional)
            
        Raises:
            LLMCacheError: If key is empty or response is invalid
        """
        if not key or not key.strip():
            raise LLMCacheError("Cache key cannot be empty")
        
        if response is None:
            raise LLMCacheError("Response cannot be None")
        
        if not isinstance(response, (LLMResponse, EmbeddingResponse)):
            raise LLMCacheError(f"Unsupported response type: {type(response)}")
        
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "response": response,
            "expires_at": expires_at
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
    
    def size(self) -> int:
        """
        Get the number of cached entries.
        
        Automatically cleans up expired entries.
        
        Returns:
            Number of valid (non-expired) cached entries
        """
        # Clean up expired entries
        self._cleanup_expired()
        return len(self._cache)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from the cache."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]


class FileLLMCache(LLMCacheInterface):
    """
    File-based LLM cache implementation.
    
    Stores cached responses as JSON files on disk with TTL support and cleanup.
    """
    
    def __init__(
        self, 
        cache_dir: Union[str, Path],
        default_ttl: int = 3600,
        max_file_size: int = 10 * 1024 * 1024  # 10MB
    ):
        """
        Initialize the file-based cache.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time to live in seconds (default: 1 hour)
            max_file_size: Maximum file size in bytes (default: 10MB)
            
        Raises:
            ValueError: If TTL or max_file_size is not positive
        """
        if default_ttl <= 0:
            raise ValueError("TTL must be positive")
        
        if max_file_size <= 0:
            raise ValueError("Max file size must be positive")
        
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.max_file_size = max_file_size
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Union[LLMResponse, EmbeddingResponse]]:
        """
        Get a cached response by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if expired
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                cache_file.unlink(missing_ok=True)
                return None
            
            # Reconstruct response object
            response_data = data["response"]
            response_type = response_data.get("response_type")
            
            if response_type == "LLMResponse":
                return LLMResponse(**{k: v for k, v in response_data.items() if k != "response_type"})
            elif response_type == "EmbeddingResponse":
                return EmbeddingResponse(**{k: v for k, v in response_data.items() if k != "response_type"})
            else:
                # Unknown response type, remove file
                cache_file.unlink(missing_ok=True)
                return None
                
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            # Corrupted or invalid file, remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(
        self, 
        key: str, 
        response: Union[LLMResponse, EmbeddingResponse],
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a cached response.
        
        Args:
            key: Cache key
            response: Response to cache
            ttl: Time to live in seconds (optional)
            
        Raises:
            LLMCacheError: If key is empty, response is invalid, or file operations fail
        """
        if not key or not key.strip():
            raise LLMCacheError("Cache key cannot be empty")
        
        if response is None:
            raise LLMCacheError("Response cannot be None")
        
        if not isinstance(response, (LLMResponse, EmbeddingResponse)):
            raise LLMCacheError(f"Unsupported response type: {type(response)}")
        
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # Prepare data for serialization
        response_data = response.model_dump()
        response_data["response_type"] = response.__class__.__name__
        
        cache_data = {
            "response": response_data,
            "expires_at": expires_at.isoformat()
        }
        
        # Check file size before writing
        cache_json = json.dumps(cache_data, indent=2)
        if len(cache_json.encode('utf-8')) > self.max_file_size:
            raise LLMCacheError(f"Response too large for cache (max: {self.max_file_size} bytes)")
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            # Ensure parent directory exists
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(cache_json)
                
        except (OSError, PermissionError) as e:
            raise LLMCacheError(f"Failed to write cache file: {e}")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                # Ignore errors during cleanup
                pass
    
    def size(self) -> int:
        """
        Get the number of cached entries.
        
        Returns:
            Number of cache files in the directory
        """
        return len(list(self.cache_dir.glob("*.json")))
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache files."""
        now = datetime.now()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                expires_at = datetime.fromisoformat(data["expires_at"])
                if now > expires_at:
                    cache_file.unlink(missing_ok=True)
                    
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # Corrupted file, remove it
                cache_file.unlink(missing_ok=True)
    
    def _get_cache_file_path(self, key: str) -> Path:
        """
        Get the file path for a cache key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to the cache file
        """
        # Sanitize the key to be filesystem-safe
        safe_key = re.sub(r'[<>:"/\\|?*]', '_', key)
        return self.cache_dir / f"{safe_key}.json" 