# Detailed Implementation Plan - Metadata Code Extractor

## Project Overview
**Complexity Level:** Level 3 - Intermediate System  
**Technology Stack:** OpenRouter + Neo4j v4.4.12 + Weaviate v1.24.20  
**Architecture:** Agent-Driven Orchestration with LLM-powered metadata extraction  

## Validated Technology Stack

### Core Technologies (Validated ✅)
- **LLM Provider:** OpenRouter API (multi-model access)
  - Primary Model: `openai/gpt-4`
  - Fallback Model: `deepseek/deepseek-chat-v3-0324:free`
  - Client: `openai-1.82.0` (OpenRouter compatible)
- **Graph Database:** Neo4j v4.4.12 (LTS)
  - Driver: `neo4j-4.4.12`
  - Connection: `bolt://localhost:7687`
- **Vector Database:** Weaviate v1.24.20
  - Client: `weaviate-client-3.24.2`
  - Connection: `http://localhost:8080`
- **Configuration:** Pydantic v2.11.5 + python-dotenv v1.1.0
- **Python Environment:** Python 3.12.8

## Implementation Strategy

### Phase 1: Core Framework and Infrastructure (3-4 Weeks)
**Objective:** Establish foundational elements with validated technology stack

#### 1.1 Project Structure Setup
```
metadata_code_extractor/
├── core/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── config_models.py      # Configuration models
│   │   ├── extraction_models.py  # Core extraction models
│   │   ├── llm_models.py         # LLM-related models
│   │   └── db_models.py          # Database models
│   ├── llm/                      # LLM integration framework
│   │   ├── __init__.py
│   │   ├── client.py             # LLM client interface
│   │   ├── adapters/             # Provider adapters
│   │   │   ├── __init__.py
│   │   │   ├── openrouter.py     # OpenRouter adapter
│   │   │   └── mock.py           # Mock adapter for testing
│   │   ├── cache.py              # LLM response caching
│   │   └── prompts/              # Prompt management
│   │       ├── __init__.py
│   │       ├── manager.py        # Prompt manager
│   │       └── templates/        # Prompt templates
│   ├── db/                       # Database integration
│   │   ├── __init__.py
│   │   ├── graph_interface.py    # Graph DB interface
│   │   ├── vector_interface.py   # Vector DB interface
│   │   ├── adapters/             # Database adapters
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_adapter.py  # Neo4j implementation
│   │   │   └── weaviate_adapter.py # Weaviate implementation
│   │   └── models.py             # Database-specific models
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── logging.py            # Logging setup
│       └── helpers.py            # Common utilities
├── agents/                       # LLM Orchestrator Agent
│   ├── __init__.py
│   ├── orchestrator.py           # Main agent logic
│   ├── state.py                  # Agent state management
│   └── strategies/               # Gap resolution strategies
├── scanners/                     # Code and document scanners
│   ├── __init__.py
│   ├── code/                     # Code metadata scanner
│   │   ├── __init__.py
│   │   ├── scanner.py            # Main scanner logic
│   │   ├── parsers/              # Language parsers
│   │   └── extractors/           # Metadata extractors
│   └── document/                 # Document scanner
│       ├── __init__.py
│       ├── scanner.py            # Document scanner logic
│       └── parsers/              # Format parsers
├── evaluators/                   # Completeness evaluator
│   ├── __init__.py
│   ├── completeness.py           # Main evaluator
│   ├── rules/                    # Completeness rules
│   └── gap_factory.py            # Gap creation logic
├── cli/                          # Command line interface
│   ├── __init__.py
│   └── main.py                   # CLI implementation
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── pyproject.toml                # Project configuration
├── requirements.txt              # Dependencies
└── README.md                     # Project documentation
```

#### 1.2 Configuration Management System
**Files:** `core/config.py`, `core/models/config_models.py`

**Implementation Tasks:**
- [x] ✅ Validated Pydantic-based configuration loading
- [ ] Implement `ConfigLoader` class with YAML/env support
- [ ] Create comprehensive `AppConfig` model
- [ ] Add configuration validation and error handling
- [ ] Implement environment-specific configurations

**Configuration Model Structure:**
```python
class LLMConfig(BaseModel):
    provider: str = "openrouter"
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-4"
    openrouter_site_url: str
    openrouter_app_name: str
    temperature: float = 0.1
    max_tokens: int = 16000

class DatabaseConfig(BaseModel):
    graph_provider: str = "neo4j"
    vector_provider: str = "weaviate"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None

class AppConfig(BaseModel):
    llm: LLMConfig
    database: DatabaseConfig
    scanning: ScanningConfig
    logging: LoggingConfig
```

#### 1.3 LLM Integration Framework
**Files:** `core/llm/client.py`, `core/llm/adapters/openrouter.py`

**Implementation Tasks:**
- [ ] Create `LLMClient` interface
- [ ] Implement `OpenRouterAdapter` with validated configuration
- [ ] Add response caching mechanism
- [ ] Implement retry logic with exponential backoff
- [ ] Create prompt template management system

**OpenRouter Integration:**
```python
class OpenRouterAdapter(LLMProviderAdapter):
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
```

#### 1.4 Database Interface Definitions
**Files:** `core/db/graph_interface.py`, `core/db/vector_interface.py`

**Implementation Tasks:**
- [ ] Define `GraphDBInterface` abstract base class
- [ ] Define `VectorDBInterface` abstract base class
- [ ] Create database-agnostic model definitions
- [ ] Implement connection management and health checks

#### 1.5 Core Data Models
**Files:** `core/models/extraction_models.py`

**Implementation Tasks:**
- [ ] Implement `ExtractedDataEntity` model
- [ ] Implement `ExtractedField` model
- [ ] Implement `ExtractedDocument` model
- [ ] Implement `MetadataGapInfo` model
- [ ] Add validation and serialization methods

### Phase 2: Database Implementations (2-3 Weeks)
**Objective:** Implement concrete database adapters with validated technology stack

#### 2.1 Neo4j Graph Database Implementation
**Files:** `core/db/adapters/neo4j_adapter.py`

**Implementation Tasks:**
- [ ] Implement `Neo4jAdapter` class using validated driver v4.4.12
- [ ] Create schema management (constraints, indexes)
- [ ] Implement CRUD operations for core entities
- [ ] Add relationship management
- [ ] Implement query optimization

**Neo4j Schema (Based on validated graph-schema.md):**
```cypher
// Constraints
CREATE CONSTRAINT entity_name_unique FOR (e:DataEntity) REQUIRE e.name IS UNIQUE;
CREATE CONSTRAINT field_composite_key FOR (f:Field) REQUIRE (f.name, f.entity_name) IS NODE KEY;

// Indexes
CREATE INDEX entity_type_index FOR (e:DataEntity) ON (e.type);
CREATE INDEX gap_status_index FOR (g:MetadataGap) ON (g.status);
```

#### 2.2 Weaviate Vector Database Implementation
**Files:** `core/db/adapters/weaviate_adapter.py`

**Implementation Tasks:**
- [ ] Implement `WeaviateAdapter` using validated client v3.24.2
- [ ] Create schema for code snippets and documents
- [ ] Implement embedding storage and retrieval
- [ ] Add semantic search capabilities
- [ ] Implement metadata filtering

**Weaviate Schema:**
```python
code_snippets_schema = {
    "class": "CodeSnippets",
    "description": "Code snippets for metadata extraction",
    "vectorizer": "none",  # We provide our own vectors
    "properties": [
        {"name": "code", "dataType": ["text"]},
        {"name": "language", "dataType": ["string"]},
        {"name": "file_path", "dataType": ["string"]},
        {"name": "entity_name", "dataType": ["string"]},
    ]
}
```

### Phase 3: Core Components Development (4-5 Weeks)
**Objective:** Develop primary processing components

#### 3.1 Code Metadata Scanner
**Files:** `scanners/code/scanner.py`, `scanners/code/parsers/python_parser.py`

**Implementation Tasks:**
- [ ] Implement file processing and language detection
- [ ] Create Python parser using validated LLM integration
- [ ] Add metadata extraction for classes, functions, fields
- [ ] Implement embedding generation for code snippets
- [ ] Add support for relationship extraction

**Python Parser Prompt Template:**
```
You are a Python code analyzer. Extract metadata from this code:

{code_snippet}

Return a JSON object with:
1. Classes: name, description, fields, methods
2. Functions: name, description, parameters, return_type
3. Relationships: imports, inheritance, references

Format as valid JSON only.
```

#### 3.2 Document Scanner
**Files:** `scanners/document/scanner.py`, `scanners/document/parsers/markdown_parser.py`

**Implementation Tasks:**
- [ ] Implement document fetching and format detection
- [ ] Create Markdown parser
- [ ] Add content chunking by sections
- [ ] Implement metadata extraction for document structure
- [ ] Add entity reference detection

#### 3.3 Completeness Evaluator
**Files:** `evaluators/completeness.py`, `evaluators/rules/`

**Implementation Tasks:**
- [ ] Implement rule engine for gap detection
- [ ] Create initial completeness rules
- [ ] Add gap prioritization logic
- [ ] Implement gap storage in Neo4j
- [ ] Add gap resolution tracking

**Initial Completeness Rules:**
1. Missing entity descriptions
2. Missing field types
3. Undocumented relationships
4. Orphaned entities
5. Missing transformation logic

### Phase 4: Agent and Orchestration System (5-6 Weeks)
**Objective:** Develop the intelligent core using validated LLM integration

#### 4.1 LLM Orchestrator Agent
**Files:** `agents/orchestrator.py`, `agents/state.py`

**Implementation Tasks:**
- [ ] Implement ReAct (Reason-Act) loop framework
- [ ] Create agent state management
- [ ] Develop decision-making prompts using validated OpenRouter
- [ ] Implement tool invocation (scanners, evaluator)
- [ ] Add gap resolution strategies

**Agent Decision Prompt:**
```
You are an intelligent metadata extraction orchestrator. 

Current State:
- Entities: {entity_count}
- Open Gaps: {gap_count}
- Last Action: {last_action}

Available Actions:
1. scan_code(path) - Scan code repository
2. scan_documents(path) - Scan documentation
3. evaluate_completeness() - Check for gaps
4. semantic_search(query) - Search for related information
5. targeted_scan(entity, gap_type) - Focused scanning

Choose the next action and provide reasoning.
```

#### 4.2 Gap Resolution Strategies
**Files:** `agents/strategies/`

**Implementation Tasks:**
- [ ] Implement semantic search strategy
- [ ] Create targeted code scanning strategy
- [ ] Add targeted document scanning strategy
- [ ] Implement multi-step resolution workflows
- [ ] Add strategy selection logic

### Phase 5: Integration and Advanced Features (4-5 Weeks)
**Objective:** Complete system integration and add advanced capabilities

#### 5.1 Full Orchestration Workflow
**Implementation Tasks:**
- [ ] Integrate all components into complete workflow
- [ ] Implement error handling and recovery
- [ ] Add progress tracking and reporting
- [ ] Create comprehensive logging
- [ ] Add performance monitoring

#### 5.2 CLI Implementation
**Files:** `cli/main.py`

**Implementation Tasks:**
- [ ] Create Click-based CLI interface
- [ ] Add scan commands with configuration options
- [ ] Implement query and reporting commands
- [ ] Add interactive mode for gap resolution
- [ ] Create export functionality

**CLI Commands:**
```bash
# Main scanning operations
metadata-extractor scan --code-path ./src --doc-path ./docs
metadata-extractor query-gaps --status open
metadata-extractor get-entity User --format json

# Configuration and management
metadata-extractor config validate
metadata-extractor db status
metadata-extractor cache clear
```

#### 5.3 Testing and Quality Assurance
**Files:** `tests/`

**Implementation Tasks:**
- [ ] Create comprehensive unit test suite
- [ ] Implement integration tests for all components
- [ ] Add end-to-end workflow tests
- [ ] Create test data and fixtures
- [ ] Set up CI/CD pipeline

### Phase 6: Documentation and Deployment (2-3 Weeks)
**Objective:** Complete documentation and prepare for deployment

#### 6.1 Documentation
**Implementation Tasks:**
- [ ] Write comprehensive user guide
- [ ] Create developer documentation
- [ ] Document API references
- [ ] Create deployment guides
- [ ] Add troubleshooting documentation

#### 6.2 Packaging and Distribution
**Implementation Tasks:**
- [ ] Create PyPI package configuration
- [ ] Add Docker containerization
- [ ] Create installation scripts
- [ ] Add example configurations
- [ ] Prepare release documentation

## Development Environment Setup

### Prerequisites (Validated ✅)
- Python 3.12.8
- Virtual environment capability
- Git for version control

### Required Services
- **Neo4j v4.4.x:** Download from https://neo4j.com/download/
- **Weaviate v1.24.20:** Use Docker or cloud instance
- **OpenRouter API Key:** Register at https://openrouter.ai/

### Development Setup
```bash
# 1. Clone and setup environment
git clone <repository>
cd metadata-code-extractor
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies (validated)
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with actual API keys and database URLs

# 4. Start services
# Neo4j: Start Neo4j Desktop or Docker container
# Weaviate: docker run -p 8080:8080 semitechnologies/weaviate:1.24.20

# 5. Validate setup
python -m metadata_code_extractor.cli config validate
```

## Risk Mitigation Strategies

### Technical Risks
1. **LLM API Reliability**
   - Mitigation: Implement caching, retry logic, fallback models
   - Monitoring: Track API response times and error rates

2. **Database Performance**
   - Mitigation: Query optimization, connection pooling, indexing
   - Monitoring: Database query performance metrics

3. **Prompt Engineering Complexity**
   - Mitigation: Modular prompt design, version control, A/B testing
   - Monitoring: Extraction accuracy metrics

### Integration Risks
1. **Component Compatibility**
   - Mitigation: Comprehensive integration testing, interface contracts
   - Monitoring: End-to-end workflow success rates

2. **Scalability Concerns**
   - Mitigation: Asynchronous processing, batch operations, resource monitoring
   - Monitoring: Processing throughput and resource utilization

## Success Metrics

### Technical Metrics
- **Extraction Accuracy:** >90% for core entities and relationships
- **Gap Detection Rate:** >85% of missing metadata identified
- **Processing Speed:** <1 minute per 1000 lines of code
- **System Reliability:** >99% uptime for core components

### Quality Metrics
- **Test Coverage:** >90% code coverage
- **Documentation Coverage:** 100% of public APIs documented
- **Performance Benchmarks:** Established baselines for all operations

## Next Steps

1. **Immediate Actions:**
   - Set up development environment with validated technology stack
   - Obtain OpenRouter API key for LLM integration
   - Install and configure Neo4j and Weaviate instances

2. **Phase 1 Kickoff:**
   - Begin project structure setup
   - Implement configuration management system
   - Start LLM integration framework development

3. **Continuous Activities:**
   - Regular technology validation updates
   - Performance monitoring and optimization
   - Documentation maintenance and updates

---

**Implementation Plan Status:** Ready for Execution  
**Technology Validation:** ✅ Completed  
**Next Phase:** Phase 1 - Core Framework and Infrastructure 