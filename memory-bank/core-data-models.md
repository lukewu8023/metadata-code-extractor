# Core Data Models - Design Document

## 1. Overview
This document defines the core Pydantic data models used for structuring information within the Metadata Code Extractor application. These models facilitate data exchange between components, configuration management, and serialization/deserialization. They are distinct from, but often precursors to, the storage format in the Graph DB (defined in `graph-schema.md`). Many of these models will align closely with the properties defined for nodes in the graph schema but serve as in-memory representations.

## 2. Purpose
- Provide type safety and validation for data passed between components.
- Standardize the structure of configuration objects.
- Define clear schemas for data returned by scanners and used by the agent and evaluator.
- Facilitate easy serialization to/from JSON or other formats if needed for intermediate storage or logging.

## 3. General Principles
- All models will inherit from `pydantic.BaseModel`.
- Use specific types (e.g., `str`, `int`, `bool`, `List`, `Dict`, `Optional`, `datetime`) for clarity and validation.
- Employ `Field` from Pydantic for default values, descriptions, and validation constraints where necessary.
- Strive for immutability where appropriate (though Pydantic V2 has different handling for this).
- Group related models logically.

## 4. Core Data Model Definitions

### 4.1. Configuration Models (Likely in a `config.py` module)

```python
from pydantic import BaseModel, FilePath, DirectoryPath, HttpUrl
from typing import List, Dict, Optional, Literal

class LLMProviderConfig(BaseModel):
    provider_name: Literal["openai", "anthropic", "azure_openai", "mock"] = "mock"
    api_key: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    # Provider-specific settings can be added here

class ModelParams(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 1024
    # Other common params like top_p, presence_penalty, etc.

class LLMSettings(BaseModel):
    default_provider: str = "mock"
    default_model_name: str = "mock-model"
    default_embedding_model_name: str = "mock-embedding-model"
    providers: Dict[str, LLMProviderConfig] = { "mock": LLMProviderConfig() }
    model_params: ModelParams = ModelParams()
    cache_enabled: bool = True
    # Cache TTL, etc.

class GraphDBConnectionConfig(BaseModel):
    db_type: Literal["neo4j", "sqlite_graph_mock"] = "sqlite_graph_mock"
    uri: Optional[str] = "sqlite:///./temp_graph.db"
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None # For Neo4j

class VectorDBConnectionConfig(BaseModel):
    db_type: Literal["chromadb", "faiss_local", "mock"] = "mock"
    path: Optional[DirectoryPath] = "./temp_vector_db"
    collection_name: str = "metadata_embeddings"
    # Other specific params like host/port for remote ChromaDB

class ScanPathsConfig(BaseModel):
    code_repositories: List[DirectoryPath] = []
    documentation_sources: List[str] = [] # Can be DirectoryPath or HttpUrl

class AppConfig(BaseModel):
    llm: LLMSettings = LLMSettings()
    graph_db: GraphDBConnectionConfig = GraphDBConnectionConfig()
    vector_db: VectorDBConnectionConfig = VectorDBConnectionConfig()
    scan_paths: ScanPathsConfig = ScanPathsConfig()
    log_level: str = "INFO"
```

### 4.2. Scanner Output Models (Representing extracted but not-yet-stored items)

These models will closely mirror the Graph DB schema nodes but are used as intermediate, in-memory objects before graph storage.

```python
# (Continuing in the same BaseModel style)
# These are simplified for brevity; actual fields will match graph-schema.md closely

class ExtractedProperty(BaseModel):
    name: str
    value: str # Or Any, with careful handling
    source_confidence: Optional[float] = None

class BaseMetadataElement(BaseModel):
    # Common fields for elements that might become nodes
    id_within_scan: str # Temporary ID during a scan, before DB ID is assigned
    extracted_from_file: Optional[FilePath] = None
    confidence: Optional[float] = None
    raw_text_or_snippet: Optional[str] = None # The source text that led to this extraction

class ExtractedDataEntity(BaseMetadataElement):
    name: str
    type: str
    description: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    # ... other properties from graph-schema.md DataEntity
    fields: List["ExtractedField"] = []
    relationships: List["ExtractedRelationship"] = []
    validations: List["ExtractedValidation"] = []

class ExtractedField(BaseMetadataElement):
    name: str
    data_type: Optional[str] = None
    description: Optional[str] = None
    # ... other properties from graph-schema.md Field
    validations: List["ExtractedValidation"] = []

class ExtractedValidation(BaseMetadataElement):
    type: str
    rule: str
    description: Optional[str] = None
    # ... other properties from graph-schema.md Validation

class ExtractedTransformation(BaseMetadataElement):
    name: Optional[str] = None
    type: str
    logic: Optional[str] = None
    description: Optional[str] = None
    # ... other properties from graph-schema.md Transformation

class ExtractedRelationship(BaseMetadataElement):
    source_entity_id_within_scan: str
    target_entity_id_within_scan: str
    label: str # e.g., INHERITS_FROM, REFERENCES_ENTITY
    properties: Dict[str, str] = {}

class ExtractedDocument(BaseMetadataElement):
    path_or_url: str
    title: Optional[str] = None
    doc_type: Optional[str] = None # markdown, pdf etc.
    # ... other properties from graph-schema.md Document
    chunks: List["ExtractedDocumentChunk"] = []

class ExtractedDocumentChunk(BaseMetadataElement):
    parent_document_id_within_scan: str
    content: str
    summary: Optional[str] = None
    vector_embedding: Optional[List[float]] = None # Populated by EmbeddingGenerator
    # ... other properties from graph-schema.md DocumentChunk

# Forward references for Pydantic
ExtractedDataEntity.update_forward_refs()
```

### 4.3. Agent and Evaluator Interaction Models

```python
class MetadataGapInfo(BaseModel):
    gap_id: Optional[str] = None # Populated once stored in DB
    type: str # e.g., missing_description, incomplete_relationship
    target_node_id_within_scan: Optional[str] = None # Refers to ExtractedDataEntity.id_within_scan etc.
    target_node_db_id: Optional[str] = None # Actual DB ID once known
    target_node_type: Optional[str] = None
    description: str
    priority: int = 3 # 1-High, 2-Medium, 3-Low
    status: str = "open"
    suggested_actions: List[str] = []
    resolution_notes: Optional[str] = None

class ScanReport(BaseModel):
    repository_path: Optional[str] = None
    document_source: Optional[str] = None
    files_scanned: int = 0
    entities_found: int = 0
    fields_found: int = 0
    documents_processed: int = 0
    chunks_created: int = 0
    gaps_identified_count: int = 0
    errors: List[str] = []
    summary_message: str

class AgentAction(BaseModel):
    action_type: Literal["run_code_scan", "run_doc_scan", "run_evaluation", "query_vector_db", "update_graph_db", "terminate"]
    parameters: Dict = {}
    reasoning_trace: Optional[str] = None # LLM thought process for this action

class AgentObservation(BaseModel):
    action_taken: AgentAction
    outcome_status: Literal["success", "failure", "partial_success"]
    result_summary: Optional[str] = None
    detailed_result: Optional[BaseModel] = None # e.g., ScanReport, List[MetadataGapInfo]
```

### 4.4. LLM Interaction Models (subset already in llm-integration-design.md)
```python
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class LLMFullResponse(BaseModel):
    # This might wrap the raw response from a provider
    provider: str
    model_used: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    finish_reason: Optional[str] = None
    content: Optional[str] = None # For simple text completion
    chat_messages: Optional[List[ChatMessage]] = None # For chat models
    error_message: Optional[str] = None
```

## 5. Location and Usage
- These models will primarily reside in a `core/models.py` or a `core/schemas.py` file (or a `models` sub-package if it grows large).
- Configuration models might be in `core/config.py`.
- Components will import these models for type hinting, data validation, and structuring their inputs/outputs.

## 6. Design Considerations
- **Granularity:** Balance between highly detailed models and overly complex ones. Start with essential fields and add more as needed.
- **Alignment with Graph Schema:** While these are in-memory, they should map cleanly to the Graph DB nodes and properties for easier storage.
- **Extensibility:** Design with future extensions in mind (e.g., using `Dict[str, Any]` for a generic `properties` field in some models).
- **Data Validation:** Leverage Pydantic's validation capabilities (e.g., for URL formats, email formats, constrained numbers).
- **Clarity:** Names should be clear and reflect the purpose of the model and its fields.

## 7. Future Enhancements
- More sophisticated validation rules within Pydantic models.
- Models for representing specific types of `Transformation` logic or `Validation` rules in a structured way, if LLMs can reliably extract them into such formats.
- Versioning of models if breaking changes are introduced over time. 