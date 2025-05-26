"""
Configuration models for the Metadata Code Extractor.

These Pydantic models define the structure and validation for all
application configuration parameters.
"""

from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""
    
    provider_name: Literal["openai", "anthropic", "azure_openai", "mock"] = "mock"
    api_key: Optional[str] = None
    base_url: Optional[HttpUrl] = None


class ModelParams(BaseModel):
    """Parameters for LLM model configuration."""
    
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, gt=0)
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is within valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        """Validate max_tokens is positive."""
        if v <= 0:
            raise ValueError('max_tokens must be positive')
        return v


class LLMSettings(BaseModel):
    """LLM configuration settings."""
    
    default_provider: str = "mock"
    default_model_name: str = "mock-model"
    default_embedding_model_name: str = "mock-embedding-model"
    providers: Dict[str, LLMProviderConfig] = Field(
        default_factory=lambda: {"mock": LLMProviderConfig()}
    )
    model_params: ModelParams = Field(default_factory=ModelParams)
    cache_enabled: bool = True


class GraphDBConnectionConfig(BaseModel):
    """Graph database connection configuration."""
    
    db_type: Literal["neo4j", "sqlite_graph_mock"] = "sqlite_graph_mock"
    uri: Optional[str] = "sqlite:///./temp_graph.db"
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None


class VectorDBConnectionConfig(BaseModel):
    """Vector database connection configuration."""
    
    db_type: Literal["chromadb", "faiss_local", "mock"] = "mock"
    path: Optional[Path] = Field(default=Path("./temp_vector_db"))
    collection_name: str = "metadata_embeddings"


class ScanPathsConfig(BaseModel):
    """Configuration for scan paths."""
    
    code_repositories: List[str] = Field(default_factory=list)
    documentation_sources: List[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    """Main application configuration."""
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    graph_db: GraphDBConnectionConfig = Field(default_factory=GraphDBConnectionConfig)
    vector_db: VectorDBConnectionConfig = Field(default_factory=VectorDBConnectionConfig)
    scan_paths: ScanPathsConfig = Field(default_factory=ScanPathsConfig)
    log_level: str = "INFO" 