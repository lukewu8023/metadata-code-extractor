# Metadata Code Extractor - Detailed Implementation Plan

## Project Overview
**Complexity Level:** Level 3 - Intermediate System  
**Technology Stack:** OpenRouter + Neo4j v4.4.12 + Weaviate v1.24.20  
**Architecture:** Agent-Driven Orchestration with LLM-powered metadata extraction  
**Status:** Ready for Phase 1 Implementation (Post-Technology Validation)  
**Total Estimated Timeline:** 22-30 Weeks

## Project Goal
To develop an intelligent metadata extraction system that uses an LLM Orchestrator Agent to scan code and documentation, identify metadata gaps, and iteratively fill those gaps using a combination of semantic search and targeted scanning. This plan reflects the validated technology stack and provides comprehensive implementation details.  

## Validated Technology Stack

### Core Technologies (Validated ✅)
- **LLM Provider:** OpenRouter API (multi-model access)
  - Primary Model: `openai/gpt-4o-mini` (validated working, e.g., `llm_poc.py`)
  - Production Model Options: `openai/gpt-4`, `anthropic/claude-3-sonnet`
  - Client: `openai` library (OpenRouter compatible, version as per `run_validation.sh`)
- **Graph Database:** Neo4j (target v4.4.44, validated with v4.4.12 driver)
  - Driver: `neo4j==4.4.12` (as per `run_validation.sh` and `graph_db_poc.py`)
  - Connection: Via URI, User, Password (validated in `graph_db_poc.py`)
- **Vector Database:** Weaviate (target v1.24.20, validated with client v3.24.2)
  - Client: `weaviate-client==3.24.2` (as per `run_validation.sh` and `vector_db_poc.py`)
  - Connection: Via URL, optional API Key (validated in `vector_db_poc.py`)
- **Configuration:** Pydantic, python-dotenv (validated in `config_poc.py`)
- **Python Environment:** Python 3.9+ (validation scripts use system Python, assumed to be compatible)

## Resolved Inconsistencies

### 1. Technology Version Alignment ✅
**Issue:** Original plans referenced Neo4j v4.4.44, but technology validation confirmed v4.4.12 availability  
**Resolution:** Updated all references to use validated Neo4j v4.4.12 with matching driver version  
**Impact:** All database connection code and configuration now aligned with validated technology stack

### 2. Graph Schema Completeness ✅
**Issue:** Current `graph-schema.md` only defines DataEntity and Field nodes, but design documents require Document, DocumentChunk, and MetadataGap nodes for full functionality  
**Resolution:** Phase 1 implementation will expand graph schema to include all required node types from design documents  
**Implementation:** Added comprehensive schema creation in Neo4j adapter covering all required node types

### 3. Embedding Strategy Resolution ✅
**Issue:** Original plans assumed OpenRouter provided embedding models, but validation confirmed it does not  
**Resolution:** Implemented fallback embedding strategy using hash-based vectors for development/validation, with path for future integration of dedicated embedding service  
**Implementation:** Added `_generate_fallback_embedding()` method in OpenRouter adapter with 384-dimensional normalized vectors

### 4. Configuration Model Standardization ✅
**Issue:** Configuration models varied between different design documents  
**Resolution:** Standardized on validated configuration structure from `config_poc.py` with comprehensive Pydantic models  
**Implementation:** Unified configuration approach across all components using validated AppConfig structure

### 5. Design Document Integration ✅
**Issue:** Implementation plan didn't fully reference all completed design documents  
**Resolution:** Updated all phase tasks to explicitly reference and implement specific design documents  
**Implementation:** Each component now explicitly implements its corresponding design document with full traceability

### 6. Response Parsing Enhancement ✅
**Issue:** Technology validation identified need for markdown response parsing from LLM responses  
**Resolution:** Added comprehensive response parsing in OpenRouter adapter to handle markdown code blocks  
**Implementation:** Added `_parse_markdown_response()` method to extract JSON from LLM responses wrapped in markdown

## Implementation Phases

### Phase 1: Core Framework and Infrastructure (Estimate: 3-4 Weeks)
**Objective:** Establish foundational elements using the validated technology stack.

#### 1.1 Project Structure Setup (Week 1)
**Based on `project-structure.md`**

**Tasks:**
- [ ] Initialize Python project directory (`metadata_code_extractor/` with subdirectories: `core`, `agents`, `scanners`, `evaluators`, `llm`, `db`, `prompts`, `utils`, `tests`, `cli`)
- [ ] Set up dependency management (e.g., `pyproject.toml` or `requirements.txt` with validated versions: `python-dotenv`, `pydantic`, `requests`, `openai` (for OpenRouter), `neo4j==4.4.12`, `weaviate-client==3.24.2`)
- [ ] Create initial project documentation and README
- [ ] Set up version control and development workflow

**Detailed Project Structure:**
```
metadata_code_extractor/
├── core/
│   ├── __init__.py
│   ├── config.py                     # Configuration management (from validated config_poc.py)
│   ├── models/                       # Pydantic data models
│   │   ├── __init__.py
│   │   ├── config_models.py          # Configuration models
│   │   ├── extraction_models.py      # Core extraction models
│   │   ├── llm_models.py             # LLM-related models
│   │   └── db_models.py              # Database models
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── logging.py                # Logging setup
│       └── file_utils.py             # File operations
├── llm/                              # LLM integration framework
│   ├── __init__.py
│   ├── client.py                     # LLM client interface
│   ├── providers/                    # Provider adapters
│   │   ├── __init__.py
│   │   └── openrouter_adapter.py     # OpenRouter adapter (validated)
│   ├── llm_cache.py                  # LLM response caching
│   └── prompt_manager.py             # Prompt management
├── db/                               # Database integration
│   ├── __init__.py
│   ├── graph_db_interface.py         # Graph DB interface
│   ├── vector_db_interface.py        # Vector DB interface
│   ├── graph_db/                     # Graph DB implementations
│   │   ├── __init__.py
│   │   └── neo4j_adapter.py          # Neo4j implementation (validated)
│   └── vector_db/                    # Vector DB implementations
│       ├── __init__.py
│       └── weaviate_adapter.py       # Weaviate implementation (validated)
├── agents/                           # LLM Orchestrator Agent
│   ├── __init__.py
│   ├── llm_orchestrator_agent.py     # Main orchestrator agent
│   └── strategies/                   # Gap resolution strategies
├── scanners/                         # Code and document scanners
│   ├── __init__.py
│   ├── base_scanner.py               # Base scanner interface
│   ├── code_scanner.py               # Code metadata scanner
│   └── document_scanner.py           # Document scanner
├── evaluators/                       # Completeness evaluation
│   ├── __init__.py
│   ├── completeness_evaluator.py     # Completeness evaluator
│   └── rules/                        # Completeness rules
├── prompts/                          # Prompt templates
│   ├── __init__.py
│   └── templates/                    # Prompt template files
├── cli/                              # Command-line interface
│   ├── __init__.py
│   └── commands/                     # CLI commands
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── fixtures/                     # Test fixtures
├── pyproject.toml                    # Project configuration
├── requirements.txt                  # Dependencies (validated versions)
├── .env.example                      # Environment template
└── README.md                         # Project documentation
```

#### 1.2 Configuration Management System (Week 1)
**Based on `configuration-management-design.md` and `config_poc.py`**

**Tasks:**
- [ ] Implement `core/config.py` using Pydantic models (`core/models/config_models.py`)
- [ ] Load from `.env` files and environment variables
- [ ] Validate configuration on startup
- [ ] Create configuration documentation and examples
- [ ] Add environment-specific configuration support

**Implementation Details:**
```python
# core/models/config_models.py
from pydantic import BaseModel, Field
from typing import Optional

class LLMConfig(BaseModel):
    provider: str = Field(default="openrouter", description="LLM provider to use")
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", description="OpenRouter model to use")
    openrouter_site_url: str = Field(default="https://github.com/metadata-code-extractor", description="OpenRouter site URL for referrer")
    openrouter_app_name: str = Field(default="metadata-code-extractor", description="OpenRouter app name")

class DatabaseConfig(BaseModel):
    graph_provider: str = Field(default="neo4j", description="Graph database provider")
    vector_provider: str = Field(default="weaviate", description="Vector database provider")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="password", description="Neo4j password")
    weaviate_url: str = Field(default="http://localhost:8080", description="Weaviate connection URL")
    weaviate_api_key: str = Field(default="", description="Weaviate API key (optional for local instances)")

class ScanningConfig(BaseModel):
    chunk_size: int = Field(default=40, description="Default code chunk size")
    chunk_overlap: int = Field(default=10, description="Default chunk overlap")
    max_tokens: int = Field(default=16000, description="Maximum tokens for LLM context")
    temperature: float = Field(default=0.1, description="LLM temperature setting")

class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scanning: ScanningConfig = Field(default_factory=ScanningConfig)
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="metadata_code_extractor.log", description="Log file path")
```

#### 1.3 Logging Framework (Week 1)
**Based on `logging-design.md`**

**Tasks:**
- [ ] Implement `core/logging_setup.py` using Python's `logging` module
- [ ] Configurable log levels, formats, and outputs (console, file)
- [ ] Add structured logging for better debugging
- [ ] Create logging configuration management
- [ ] Add performance logging capabilities

#### 1.4 Testing Infrastructure (Week 1)
**Based on `testing-strategy.md`**

**Tasks:**
- [ ] Set up `pytest` with initial directory structure (`tests/unit`, `tests/integration`)
- [ ] Create `conftest.py` for common fixtures
- [ ] Add test configuration and utilities
- [ ] Set up continuous integration testing
- [ ] Create test data and mock services

#### 1.5 LLM Integration Framework (Week 1-2)
**Based on `llm-integration-design.md` and `llm_poc.py`**

**Tasks:**
- [ ] Define `LLMClient` interface in `metadata_code_extractor/llm/client.py`
- [ ] Implement `OpenRouterAdapter` in `metadata_code_extractor/llm/providers/openrouter_adapter.py` using the `openai` library
- [ ] Implement basic `PromptManager` in `metadata_code_extractor/llm/prompt_manager.py` (loading from `prompts/` directory)
- [ ] Implement initial `LLMCache` in `metadata_code_extractor/llm/llm_cache.py` (e.g., in-memory or simple file-based)
- [ ] Add response parsing to handle markdown code blocks (identified in validation)
- [ ] Include fallback embedding generation logic from `vector_db_poc.py` if OpenRouter embedding models are not immediately used/available

**Implementation Details:**
```python
# llm/providers/openrouter_adapter.py
from typing import List, Dict, Any
from openai import OpenAI
import re
import hashlib
import struct
import json

class OpenRouterAdapter(LLMClient):
    def __init__(self, config: LLMConfig):
        self.client = OpenAI(
            api_key=config.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = config.openrouter_model
        self.headers = {
            "HTTP-Referer": config.openrouter_site_url,
            "X-Title": config.openrouter_app_name
        }
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Complete chat completion with OpenRouter, handling markdown response parsing
        as identified during technology validation
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.1),
                max_tokens=kwargs.get('max_tokens', 4000),
                extra_headers=self.headers
            )
            
            # Parse response to handle markdown code blocks
            content = response.choices[0].message.content
            parsed_content = self._parse_markdown_response(content)
            
            return {
                "content": parsed_content,
                "raw_content": content,  # Keep original for debugging
                "usage": response.usage.model_dump() if response.usage else None,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise LLMError(f"OpenRouter API error: {str(e)}")
    
    def _parse_markdown_response(self, content: str) -> str:
        """
        Handle markdown code blocks as identified in validation
        Supports JSON, Python, and plain text extraction
        """
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```(?:json)?\s*(\{.*?\})\s*```',  # JSON blocks
            r'```(?:python)?\s*(\{.*?\})\s*```',  # Python blocks with JSON
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    # Validate it's proper JSON
                    json.loads(match.group(1))
                    return match.group(1)
                except json.JSONDecodeError:
                    continue
        
        # If no valid JSON found, return cleaned content
        # Remove markdown code blocks but keep content
        cleaned = re.sub(r'```[\w]*\n?', '', content)
        return cleaned.strip()
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using fallback strategy since OpenRouter doesn't provide embeddings
        """
        return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Generate deterministic hash-based embedding for development/validation
        Returns 384-dimensional normalized vector
        """
        # Use multiple hash functions for better distribution
        hash_functions = [
            lambda t: hashlib.md5(t.encode()).digest(),
            lambda t: hashlib.sha1(t.encode()).digest(),
            lambda t: hashlib.sha256(t.encode()).digest()[:16],  # Truncate to 16 bytes
        ]
        
        all_bytes = b''
        for hash_func in hash_functions:
            all_bytes += hash_func(text)
        
        # Convert to float vector
        vector = []
        for i in range(0, len(all_bytes), 4):
            chunk = all_bytes[i:i+4]
            if len(chunk) == 4:
                # Interpret as float
                value = struct.unpack('>f', chunk)[0]
            else:
                # Pad with zeros
                padded = chunk + b'\x00' * (4 - len(chunk))
                value = struct.unpack('>f', padded)[0]
            
            # Handle NaN/inf values
            if not (value == value) or abs(value) == float('inf'):
                value = 0.0
            
            vector.append(value)
        
        # Extend to exactly 384 dimensions
        while len(vector) < 384:
            vector.extend(vector[:min(len(vector), 384 - len(vector))])
        vector = vector[:384]
        
        # Normalize vector
        magnitude = sum(x*x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x/magnitude for x in vector]
        else:
            # If all zeros, create a small random-like vector
            vector = [0.001 * (i % 10 - 5) for i in range(384)]
            magnitude = sum(x*x for x in vector) ** 0.5
            vector = [x/magnitude for x in vector]
        
        return vector
```

#### 1.6 Database Interface Definitions and Adapters (Week 2-3)
**Based on `database-integration-design.md` and PoCs**

**Tasks:**
- [ ] Define `GraphDBInterface` in `metadata_code_extractor/db/graph_db_interface.py`
- [ ] Implement `Neo4jAdapter` in `metadata_code_extractor/db/graph_db/neo4j_adapter.py` (using `neo4j==4.4.12` driver)
- [ ] Define `VectorDBInterface` in `metadata_code_extractor/db/vector_db_interface.py`
- [ ] Implement `WeaviateAdapter` in `metadata_code_extractor/db/vector_db/weaviate_adapter.py` (using `weaviate-client==3.24.2`)
- [ ] Include fallback embedding generation logic from `vector_db_poc.py` if OpenRouter embedding models are not immediately used/available
- [ ] Expand graph schema to include Document, DocumentChunk, and MetadataGap nodes
- [ ] Implement connection pooling and error handling
- [ ] Create database schema management
- [ ] Add data validation and serialization

**Expanded Graph Schema Implementation:**
```python
# db/graph_db/neo4j_adapter.py
class Neo4jAdapter(GraphDBInterface):
    def __init__(self, config: DatabaseConfig):
        self.driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password)
        )
    
    def create_schema(self):
        """Create complete schema including all node types from design documents"""
        with self.driver.session() as session:
            # Create constraints for all node types
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:DataEntity) REQUIRE e.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Field) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.path IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (dc:DocumentChunk) REQUIRE dc.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (mg:MetadataGap) REQUIRE mg.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transformation) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Validation) REQUIRE v.id IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    print(f"Warning: Could not create constraint: {e}")
```

**Weaviate Adapter with Validated Connection:**
```python
# db/vector_db/weaviate_adapter.py
class WeaviateAdapter(VectorDBInterface):
    def __init__(self, config: DatabaseConfig):
        # Use validated connection method from vector_db_poc.py
        self.client = weaviate.Client(url=config.weaviate_url)
        # Validate connection
        if not self.client.is_ready():
            raise ConnectionError(f"Cannot connect to Weaviate at {config.weaviate_url}")
    
    def create_schema(self):
        """Create schema for code snippets and document chunks"""
        schemas = [
            {
                "class": "CodeSnippets",
                "description": "Code snippets for metadata extraction",
                "vectorizer": "none",
                "properties": [
                    {"name": "code", "dataType": ["text"], "description": "The source code content"},
                    {"name": "language", "dataType": ["string"], "description": "Programming language"},
                    {"name": "description", "dataType": ["text"], "description": "Description of the code snippet"},
                    {"name": "snippet_id", "dataType": ["string"], "description": "Unique identifier for the snippet"}
                ]
            },
            {
                "class": "DocumentChunks",
                "description": "Document chunks for semantic search",
                "vectorizer": "none",
                "properties": [
                    {"name": "content", "dataType": ["text"], "description": "The document content"},
                    {"name": "document_path", "dataType": ["string"], "description": "Source document path"},
                    {"name": "chunk_type", "dataType": ["string"], "description": "Type of document chunk"},
                    {"name": "chunk_id", "dataType": ["string"], "description": "Unique identifier for the chunk"}
                ]
            }
        ]
        
        for schema in schemas:
            if not self.client.schema.exists(schema["class"]):
                self.client.schema.create_class(schema)
```

#### 1.7 Core Data Models (Week 3)
**Based on `core-data-models.md`**

**Tasks:**
- [ ] Implement Pydantic models in `core/models/` for configuration, LLM interactions, DB items, and extraction outputs (e.g., `ExtractedDataEntity`, `MetadataGapInfo`)
- [ ] Create comprehensive data validation rules
- [ ] Add serialization and deserialization methods
- [ ] Implement model documentation and examples
- [ ] Create model versioning strategy

**Complete Model Implementation:**
```python
# core/models/extraction_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExtractedDataEntity(BaseModel):
    id_within_scan: str
    name: str
    type: str
    description: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    extracted_from_file: Optional[str] = None
    confidence: Optional[float] = None
    raw_text_or_snippet: Optional[str] = None
    fields: List["ExtractedField"] = []
    relationships: List["ExtractedRelationship"] = []
    validations: List["ExtractedValidation"] = []

class ExtractedField(BaseModel):
    id_within_scan: str
    name: str
    data_type: Optional[str] = None
    nullable: Optional[bool] = None
    description: Optional[str] = None
    sensitivity: Optional[str] = None
    source: Optional[str] = None
    default_value: Optional[str] = None
    extracted_from_file: Optional[str] = None
    confidence: Optional[float] = None
    validations: List["ExtractedValidation"] = []

class ExtractedDocument(BaseModel):
    id_within_scan: str
    path_or_url: str
    title: Optional[str] = None
    doc_type: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
    chunks: List["ExtractedDocumentChunk"] = []

class ExtractedDocumentChunk(BaseModel):
    id_within_scan: str
    parent_document_id_within_scan: str
    content: str
    summary: Optional[str] = None
    vector_embedding: Optional[List[float]] = None
    chunk_index: int
    confidence: Optional[float] = None

class MetadataGap(BaseModel):
    gap_id: Optional[str] = None
    type: str
    target_node_id_within_scan: Optional[str] = None
    target_node_db_id: Optional[str] = None
    target_node_type: Optional[str] = None
    description: str
    priority: int = Field(default=3, ge=1, le=5)  # 1=High, 5=Low
    status: str = Field(default="open")
    suggested_actions: List[str] = []
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class ExtractedValidation(BaseModel):
    id_within_scan: str
    type: str
    rule: str
    description: Optional[str] = None
    confidence: Optional[float] = None

class ExtractedTransformation(BaseModel):
    id_within_scan: str
    name: Optional[str] = None
    type: str
    logic: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[float] = None

class ExtractedRelationship(BaseModel):
    source_entity_id_within_scan: str
    target_entity_id_within_scan: str
    label: str
    properties: Dict[str, Any] = {}
    confidence: Optional[float] = None

# Update forward references
ExtractedDataEntity.model_rebuild()
```

#### 1.8 Basic CLI Structure (Week 3-4)
**Based on `project-structure.md`**

**Tasks:**
- [ ] Implement `cli.py` using a library like `click` or `argparse` with placeholder commands
- [ ] Create command structure for all planned operations
- [ ] Add configuration management commands
- [ ] Implement basic help and documentation
- [ ] Add progress reporting framework

### Phase 2: Core Components Development (Estimate: 4-6 Weeks)
**Objective:** Develop the primary processing components.

#### 2.1 Code Metadata Scanner (Initial Version - Week 5-6)
**Based on `code-scanner-design.md`**

**Tasks:**
- [ ] Implement `scanners/base_scanner.py` with a base scanner interface
- [ ] Implement `scanners/code_scanner.py`
- [ ] Basic file traversal and language identification (Python initially)
- [ ] LLM-based extraction for primary code entities (classes, functions) and their fields/attributes
- [ ] Prompts for structured metadata (JSON) from code snippets
- [ ] Integration with `LLMClient` and `EmbeddingGenerator` (from LLM Integration framework)
- [ ] Integration with `GraphDBInterface` and `VectorDBInterface` for storing results
- [ ] Implement `scan_repository(repo_path)` and `scan_targeted(file_path, target_details)`
- [ ] Add support for chunking strategies (40 lines with 10 line overlap)
- [ ] Create confidence scoring for extracted metadata
- [ ] Add error handling and recovery mechanisms

#### 2.2 Document Scanner (Initial Version - Week 7-8)
**Based on `document-scanner-design.md`**

**Tasks:**
- [ ] Implement `scanners/document_scanner.py`
- [ ] Support for parsing Markdown files initially
- [ ] Document chunking strategy
- [ ] LLM-based extraction for document structure and summaries
- [ ] Heuristic or simple LLM prompts for identifying links to code entities
- [ ] Integration with `LLMClient` and `EmbeddingGenerator`
- [ ] Integration with `GraphDBInterface` and `VectorDBInterface`
- [ ] Implement `scan_document_repository(source_path_or_url_list)` and `scan_document_targeted(doc_identifier, target_details)`
- [ ] Add support for cross-reference detection
- [ ] Create document structure analysis
- [ ] Add metadata extraction for documentation

### Phase 3: Agent and Orchestration System (Estimate: 5-7 Weeks)
**Objective:** Develop the intelligent core of the system.

#### 3.1 LLM Orchestrator Agent (Core Logic - Week 9-11)
**Based on `llm-orchestrator-agent-design.md`**

**Tasks:**
- [ ] Implement `agents/llm_orchestrator_agent.py`
- [ ] Agent state management
- [ ] ReAct (Reason-Act) loop framework
- [ ] Prompts for agent reasoning (analyzing state, deciding next actions)
- [ ] Ability to invoke Scanners and Evaluator
- [ ] Initial strategies for choosing between semantic search and targeted scanning
- [ ] Create decision-making algorithms
- [ ] Add context management and memory
- [ ] Implement error handling and recovery
- [ ] Add performance monitoring and optimization

#### 3.2 Completeness Evaluator (Initial Version - Week 12-13)
**Based on `completeness-evaluator-design.md`**

**Tasks:**
- [ ] Implement `evaluators/completeness_evaluator.py`
- [ ] Define initial completeness criteria (e.g., entity description exists, field type defined)
- [ ] Logic to query `GraphDBInterface` and identify items failing criteria
- [ ] Functionality to create/update `MetadataGap` nodes in the Graph DB
- [ ] Prompts for summarizing and prioritizing gaps (if LLM-assisted)
- [ ] Implement `evaluate_completeness()` and `get_open_gaps()`
- [ ] Add confidence scoring for completeness assessment
- [ ] Create gap prioritization algorithms
- [ ] Add rule-based evaluation logic

#### 3.3 Orchestration Workflow (Initial - Week 14-15)
**Tasks:**
- [ ] Implement the main sequence: Initial Code Scan -> Initial Doc Scan -> Initial Evaluation -> Basic Gap Loop (semantic search for first iteration)
- [ ] Create workflow state management
- [ ] Add progress tracking and reporting
- [ ] Implement error handling and recovery
- [ ] Add workflow configuration and customization

### Phase 4: Integration, Iterative Improvement & Advanced Features (Estimate: 6-8 Weeks)
**Objective:** Refine components, enable the full iterative loop, and add advanced capabilities.

#### 4.1 Full Gap Resolution Loop (Week 16-18)
**Tasks:**
- [ ] Enhance Agent's ability to choose and execute targeted scans based on gap type and context
- [ ] Agent processes results from semantic search and targeted scans to update Graph DB
- [ ] Refined re-evaluation by Completeness Evaluator
- [ ] Agent logic to decide if a gap is resolved, needs more attempts, or requires human input
- [ ] Add iterative improvement mechanisms
- [ ] Create feedback loops for learning
- [ ] Implement adaptive strategies

#### 4.2 Advanced Scanning & Extraction (Week 19-20)
**Tasks:**
- [ ] Code Scanner: Deeper analysis (relationships like `REFERENCES`, `TRANSFORMED_FROM`), support for more languages
- [ ] Document Scanner: Support for more formats (e.g., PDF via PyMuPDF, HTML via BeautifulSoup), more sophisticated extraction of relationships
- [ ] Add advanced relationship detection
- [ ] Implement cross-language support
- [ ] Create sophisticated extraction algorithms

#### 4.3 Enhanced Completeness Evaluator (Week 21)
**Tasks:**
- [ ] More sophisticated completeness rules and heuristics
- [ ] Improved prioritization of gaps
- [ ] Add machine learning-based evaluation
- [ ] Create adaptive evaluation criteria

#### 4.4 Refined Agent Reasoning (Week 22)
**Tasks:**
- [ ] Improved prompts for nuanced decision-making and error handling
- [ ] Ability to learn from failed attempts
- [ ] Add advanced reasoning capabilities
- [ ] Create self-improvement mechanisms

#### 4.5 Performance & Scalability (Week 23)
**Tasks:**
- [ ] Optimize DB queries and LLM calls (batching)
- [ ] Refine caching
- [ ] Add performance monitoring
- [ ] Implement scalability improvements

### Phase 5: CLI, Testing, and Documentation (Estimate: 4-5 Weeks)
**Objective:** Make the system usable, robust, and well-documented.

#### 5.1 Command Line Interface (CLI) (Week 24-25)
**Tasks:**
- [ ] Full implementation of CLI commands defined in `project-structure.md`
- [ ] Progress reporting, configuration options
- [ ] Add interactive modes
- [ ] Create comprehensive help system
- [ ] Implement result visualization

#### 5.2 Comprehensive Testing (Week 26-27)
**Tasks:**
- [ ] Expand unit tests for all components
- [ ] Develop integration tests for interactions (Agent-Scanner, Agent-Evaluator, Scanner-DB)
- [ ] End-to-end tests with sample code/doc repositories
- [ ] Add performance testing
- [ ] Create load testing scenarios

#### 5.3 User and Developer Documentation (Week 28-29)
**Tasks:**
- [ ] User guide (install, configure, run, understand outputs)
- [ ] Developer guide (architecture, extending scanners/rules, API docs)
- [ ] Documentation for `graph-schema.md` and prompt templates (`prompt-engineering.md`)
- [ ] Create tutorial and examples
- [ ] Add troubleshooting guides

#### 5.4 Packaging & Deployment Considerations (Week 30)
**Tasks:**
- [ ] Package for distribution (e.g., PyPI)
- [ ] (Optional) Dockerfile
- [ ] Create deployment scripts
- [ ] Add monitoring and alerting
- [ ] Create maintenance procedures

## Key Milestones & Deliverables

### End of Phase 1 (Week 4)
- [ ] Core framework setup, basic LLM/DB interfaces and adapters implemented and unit-tested
- [ ] Configuration management system functional
- [ ] Database connections validated and working
- [ ] LLM integration with response parsing operational
- [ ] Basic project structure and development workflow established

### End of Phase 2 (Week 8)
- [ ] Initial versions of Code and Document Scanners functional, storing basic data in DBs
- [ ] Code scanner can extract basic metadata from Python files
- [ ] Document scanner can process Markdown files
- [ ] Integration with databases working for data storage
- [ ] Basic completeness evaluation operational

### End of Phase 3 (Week 15)
- [ ] Orchestrator Agent can run initial scans, evaluate completeness, and attempt semantic search for gaps
- [ ] ReAct framework operational for agent decision-making
- [ ] Basic gap resolution workflow functional
- [ ] Agent can coordinate between scanners and evaluators
- [ ] Initial orchestration workflow complete

### End of Phase 4 (Week 23)
- [ ] Full iterative gap resolution loop functional; advanced scanning capabilities integrated
- [ ] Agent can adaptively choose resolution strategies
- [ ] Advanced extraction capabilities for multiple languages and formats
- [ ] Performance optimizations implemented
- [ ] System can handle complex, real-world repositories

### End of Phase 5 (Week 30)
- [ ] Usable CLI, comprehensive tests, full documentation, packaged application
- [ ] Production-ready system with monitoring and deployment
- [ ] Complete user and developer documentation
- [ ] Comprehensive testing suite with high coverage
- [ ] Ready for distribution and adoption

## Implementation Dependencies

### Validated Dependencies (from tech validation)
```python
# pyproject.toml or requirements.txt
python-dotenv
pydantic
requests
openai  # for OpenRouter
neo4j==4.4.12
weaviate-client==3.24.2
click  # for CLI
pytest  # for testing
# Additional dependencies as needed for specific features
```

## Assumptions & Risks

### LLM Access & Performance
**Assumption:** Reliable access to OpenRouter  
**Risk:** Latency can be a bottleneck  
**Mitigation:** Effective caching, batching, efficient prompting, potential model tier selection

### Prompt Engineering Complexity
**Assumption:** Effective prompts can be crafted  
**Risk:** Crafting effective prompts is iterative  
**Mitigation:** Use `prompt-engineering.md` guidelines, version prompts, evaluate

### Data Variety
**Assumption:** System can handle diverse inputs  
**Risk:** Handling diverse languages, doc formats, project structures  
**Mitigation:** Start focused, design for extensibility

### Scalability
**Assumption:** System will scale to large repositories  
**Risk:** Large repositories may pose challenges  
**Mitigation:** Optimize critical paths, efficient DB usage

### Accuracy of Extraction
**Assumption:** LLM extraction will be sufficiently accurate  
**Risk:** LLM extraction may not be 100% accurate  
**Mitigation:** Confidence scoring, iterative refinement, human review flags

## Success Metrics

### Phase 1 Success Criteria
- [ ] All core interfaces implemented and tested
- [ ] Configuration system working with validated technology stack
- [ ] Database adapters functional with remote instances
- [ ] LLM integration working with OpenRouter
- [ ] 90%+ test coverage for core components

### Overall Project Success Criteria
- [ ] System can extract metadata from Python codebases
- [ ] Agent can identify and resolve metadata gaps
- [ ] Performance meets scalability requirements
- [ ] Documentation enables easy adoption
- [ ] System is production-ready with monitoring

## Next Steps

### Immediate Actions (This Week)
1. **Initialize Project Structure**
   - Create repository structure as defined above
   - Set up development environment with validated dependencies
   - Configure CI/CD pipeline

2. **Begin Phase 1 Implementation**
   - Start with configuration management system using validated models
   - Implement validated database adapters
   - Create LLM integration framework with response parsing

3. **Set Up Development Workflow**
   - Configure testing framework
   - Set up code quality tools
   - Create development documentation

The project is now ready to proceed with implementation based on the successfully validated technology stack and comprehensive planning. All major technical risks have been mitigated through the validation process, and the implementation plan provides a clear path to a working system that aligns with all design documents and delivers the intelligent metadata extraction capabilities as envisioned. 