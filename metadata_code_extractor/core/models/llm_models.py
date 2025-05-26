"""
LLM-related Pydantic models for the Metadata Code Extractor.

These models define the structure for LLM interactions, configurations,
and responses used throughout the system.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enumeration of message roles in a conversation."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation."""
    
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ModelConfig(BaseModel):
    """Configuration for LLM model parameters."""
    
    model_name: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, gt=0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    stop: Optional[Union[str, List[str]]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class EmbeddingConfig(BaseModel):
    """Configuration for embedding model parameters."""
    
    model_name: str
    dimensions: Optional[int] = Field(default=None, gt=0)
    encoding_format: Literal["float", "base64"] = "float"
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class LLMResponse(BaseModel):
    """Response from an LLM completion request."""
    
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class EmbeddingResponse(BaseModel):
    """Response from an embedding request."""
    
    embeddings: List[List[float]]
    model: str
    usage: Optional[Dict[str, int]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class LLMCacheEntry(BaseModel):
    """Cache entry for LLM responses."""
    
    request_hash: str
    response: Union[LLMResponse, EmbeddingResponse]
    timestamp: float
    model_config: Union[ModelConfig, EmbeddingConfig]
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid" 