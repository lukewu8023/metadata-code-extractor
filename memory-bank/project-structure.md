# Metadata Code Extractor - Project Structure

## Directory Structure

```
metadata_code_extractor/
├── README.md                  # Project overview and documentation
├── pyproject.toml             # Project configuration and dependencies
├── setup.py                   # Installation script
├── .gitignore                 # Git ignore file
├── .env.example               # Example environment configuration
├── requirements.txt           # Project dependencies
├── requirements-dev.txt       # Development dependencies
├── metadata_code_extractor/        # Main package
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── constants.py           # Constants and defaults
│   ├── exceptions.py          # Custom exceptions
│   ├── logging_config.py      # Logging configuration
│   ├── version.py             # Version information
│   ├── parser/                # Parser component
│   │   ├── __init__.py
│   │   ├── base.py            # Base parser interface
│   │   ├── llm_parser.py      # LLM-based parser implementation
│   │   ├── python_parser.py   # Python-specific parser
│   │   ├── chunking.py        # Code chunking utilities
│   │   └── utils.py           # Parser utilities
│   ├── prompts/               # LLM prompt management
│   │   ├── __init__.py
│   │   ├── template.py        # Prompt template base class
│   │   ├── template_manager.py # Template management
│   │   ├── confidence.py      # Confidence scoring utilities
│   │   ├── response_parser.py # LLM response parsing
│   │   └── templates/         # Prompt template files
│   │       ├── entity/        # Entity extraction templates
│   │       ├── field/         # Field extraction templates
│   │       ├── relationship/  # Relationship extraction templates
│   │       ├── validation/    # Validation rule templates
│   │       └── transformation/ # Transformation templates
│   ├── llm/                   # LLM integration
│   │   ├── __init__.py
│   │   ├── client.py          # LLM API client
│   │   ├── provider.py        # Provider interface
│   │   ├── openai.py          # OpenAI provider
│   │   ├── anthropic.py       # Anthropic provider
│   │   ├── cache.py           # Response caching
│   │   └── error_handler.py   # Error handling and retry logic
│   ├── metadata/              # Metadata extraction
│   │   ├── __init__.py
│   │   ├── extractor.py       # Main extractor class
│   │   ├── entity.py          # Entity models
│   │   ├── field.py           # Field models
│   │   ├── relationship.py    # Relationship models
│   │   ├── validation.py      # Validation rule models
│   │   ├── transformation.py  # Transformation models
│   │   └── schema.py          # Schema definition
│   ├── symbols/               # Symbol management
│   │   ├── __init__.py
│   │   ├── indexer.py         # Symbol indexer
│   │   ├── symbol_map.py      # Symbol map implementation
│   │   └── location.py        # Code location utilities
│   ├── storage/               # Data storage
│   │   ├── __init__.py
│   │   ├── graph/             # Graph database integration
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py     # Graph DB adapter interface
│   │   │   ├── neo4j.py       # Neo4j implementation
│   │   │   └── queries.py     # Graph queries
│   │   ├── vector/            # Vector database integration
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py     # Vector DB adapter interface
│   │   │   ├── embeddings.py  # Embedding generation
│   │   │   └── providers/     # Vector DB providers
│   │   └── local/             # Local storage options
│   │       ├── __init__.py
│   │       ├── json_store.py  # JSON file storage
│   │       └── sqlite.py      # SQLite storage
│   ├── scan/                  # Scanning logic
│   │   ├── __init__.py
│   │   ├── broad_scan.py      # Broad scan implementation
│   │   ├── focused_scan.py    # Focused scan implementation
│   │   ├── target_selection.py # Target selection for focused scan
│   │   └── scheduler.py       # Scan task scheduling
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── file_utils.py      # File handling utilities
│       ├── language_utils.py  # Language detection
│       ├── type_utils.py      # Type handling utilities
│       └── performance.py     # Performance monitoring
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_data/             # Test data files
│   ├── unit/                  # Unit tests
│   │   ├── __init__.py
│   │   ├── parser/            # Parser tests
│   │   ├── prompts/           # Prompt tests
│   │   ├── llm/               # LLM integration tests
│   │   ├── metadata/          # Metadata tests
│   │   └── ...                # Other unit tests
│   └── integration/           # Integration tests
│       ├── __init__.py
│       ├── test_scan.py       # Scan integration tests
│       ├── test_extraction.py # Extraction integration tests
│       └── ...                # Other integration tests
├── docs/                      # Documentation
│   ├── index.md               # Documentation home
│   ├── installation.md        # Installation guide
│   ├── usage.md               # Usage guide
│   ├── configuration.md       # Configuration reference
│   ├── api/                   # API documentation
│   ├── examples/              # Usage examples
│   └── development/           # Development guide
└── examples/                  # Example scripts
    ├── basic_extraction.py    # Basic extraction example
    ├── focused_scan.py        # Focused scan example
    ├── graph_output.py        # Graph output example
    └── custom_templates.py    # Custom prompt template example
```

## Key Modules and Components

### Parser Component

The parser component handles the parsing of source code files and extraction of metadata using LLM.

**Key Files**:
- `base.py`: Abstract base class for all parsers
- `llm_parser.py`: Core LLM-based parser implementation
- `python_parser.py`: Python-specific parser implementation
- `chunking.py`: Code chunking utilities

**Interfaces**:
- `CodeParser`: Base interface for all parsers
- `ParseResult`: Container for parsed code results
- `CodeChunk`: Representation of a code chunk for LLM processing

### Prompt Management

The prompts component manages templates for LLM interactions and handles response parsing.

**Key Files**:
- `template.py`: Prompt template base class
- `template_manager.py`: Template management system
- `response_parser.py`: LLM response parsing utilities

**Interfaces**:
- `PromptTemplate`: Base interface for all prompt templates
- `PromptTemplateManager`: Management of prompt templates
- `ResponseParser`: Parsing of LLM responses

### LLM Integration

The LLM component handles interactions with LLM providers, including API calls, caching, and error handling.

**Key Files**:
- `client.py`: LLM client for API interactions
- `provider.py`: Provider interface for different LLM services
- `cache.py`: Caching mechanism for LLM responses

**Interfaces**:
- `LLMClient`: Client for LLM API interactions
- `LLMProvider`: Interface for specific LLM providers
- `LLMCache`: Caching interface for LLM responses

### Metadata Extraction

The metadata component defines the data models and extraction logic for metadata entities.

**Key Files**:
- `extractor.py`: Main extractor class
- `entity.py`: Data entity models
- `field.py`: Field models
- `relationship.py`: Relationship models

**Interfaces**:
- `MetadataExtractor`: Main extraction interface
- `Entity`, `Field`, `Relationship`, etc.: Data models

### Symbol Management

The symbols component handles the indexing and mapping of code symbols for lookup.

**Key Files**:
- `indexer.py`: Symbol indexer implementation
- `symbol_map.py`: Symbol map data structure
- `location.py`: Code location utilities

**Interfaces**:
- `SymbolIndexer`: Interface for building symbol indices
- `SymbolMap`: Interface for symbol lookups
- `Location`: Representation of code locations

### Storage Integration

The storage component handles integration with graph and vector databases for metadata storage.

**Key Files**:
- `graph/adapter.py`: Graph database adapter interface
- `vector/adapter.py`: Vector database adapter interface
- `local/json_store.py`: Local JSON storage

**Interfaces**:
- `GraphOutputAdapter`: Interface for graph database output
- `VectorOutputAdapter`: Interface for vector database output

### Scanning Logic

The scan component implements the broad and focused scanning modes for code repositories.

**Key Files**:
- `broad_scan.py`: Broad scan implementation
- `focused_scan.py`: Focused scan implementation
- `target_selection.py`: Target selection for focused scans

**Interfaces**:
- `Scanner`: Base scanner interface
- `BroadScanner`: Broad scan implementation
- `FocusedScanner`: Focused scan implementation

## Configuration

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "metadata-code-extractor"
version = "0.1.0"
description = "LLM-based code metadata extraction tool"
readme = "README.md"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
requires-python = ">=3.9"
dependencies = [
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "requests>=2.25.0",
    "python-dotenv>=1.0.0",
    "rich>=10.0.0",
    "openai>=1.0.0",
    "anthropic>=0.5.0",
    "tenacity>=8.0.0",
    "networkx>=3.0",
    "faiss-cpu>=1.7.0",
    "neo4j>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.0.0",
    "mypy>=1.0.0",
    "pylint>=2.0.0",
    "pre-commit>=3.0.0",
]

[project.urls]
"Homepage" = "https://github.com/yourusername/metadata-code-extractor"
"Bug Tracker" = "https://github.com/yourusername/metadata-code-extractor/issues"

[project.scripts]
metadata-code-extractor = "metadata_code_extractor.cli:main"

[tool.black]
line-length = 88
target-version = ["py39"]

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
strict = true
```

### .env.example

```
# LLM Provider Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here

# Model Configuration
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-opus

# Database Configuration
GRAPH_DB_PROVIDER=neo4j
VECTOR_DB_PROVIDER=faiss
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Scanning Configuration
DEFAULT_CHUNK_SIZE=40
DEFAULT_CHUNK_OVERLAP=10
MAX_TOKENS=16000
TEMPERATURE=0.1
PROMPT_TEMPLATE_DIR=./metadata_code_extractor/prompts/templates

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=metadata_code_extractor.log
```

## CLI Interface Structure

```python
@click.group()
def cli():
    """Metadata Code Extractor - LLM-based code analysis tool."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for results')
@click.option('--format', '-f', type=click.Choice(['json', 'graph', 'vector']), default='json', help='Output format')
@click.option('--language', '-l', help='Filter by programming language')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
def scan(path, output, format, language, config):
    """Perform a broad scan of code files."""
    # Implementation here

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('query', type=str)
@click.option('--output', '-o', type=click.Path(), help='Output directory for results')
@click.option('--format', '-f', type=click.Choice(['json', 'graph', 'vector']), default='json', help='Output format')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
def focused(path, query, output, format, config):
    """Perform a focused scan based on query."""
    # Implementation here

@cli.command()
@click.option('--llm-provider', type=str, help='Test LLM provider connection')
@click.option('--graph-db', is_flag=True, help='Test graph database connection')
@click.option('--vector-db', is_flag=True, help='Test vector database connection')
@click.option('--all', 'all_tests', is_flag=True, help='Run all tests')
def test_connections(llm_provider, graph_db, vector_db, all_tests):
    """Test connections to external services."""
    # Implementation here

if __name__ == '__main__':
    cli()
```

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use type hints consistently
- Follow consistent docstring format (Google style)

### Testing Strategy
- Write unit tests for all core components
- Create integration tests for key workflows
- Achieve at least 80% code coverage
- Use pytest as the test framework
- Set up CI/CD for automated testing

### Documentation
- Document all public APIs
- Create example scripts for common use cases
- Provide detailed configuration reference
- Include architectural diagrams

### Development Workflow
1. Set up development environment with virtual environment
2. Install development dependencies
3. Use pre-commit hooks for style checks
4. Write tests before implementing features
5. Run full test suite before submitting changes

## Implementation Plan

### Phase 1: Core Framework
- Project structure setup
- Configuration system
- CLI skeleton
- Logging setup
- Basic parser interface

### Phase 2: LLM Integration
- LLM client implementation
- Provider interface and implementations
- Prompt template management
- Response parsing

### Phase 3: Parser Implementation
- Code chunking system
- Python parser implementation
- Symbol map generation
- Initial metadata extraction

### Phase 4: Storage Integration
- Local JSON storage
- Graph database integration
- Vector database integration

### Phase 5: Advanced Features
- Focused scan implementation
- Relationship detection
- Transformation detection
- Confidence scoring

### Phase 6: Refinement
- Performance optimization
- Error handling improvements
- Documentation completion
- Packaging and distribution

## Next Steps

1. Set up basic project structure
2. Create core interfaces and data models
3. Implement prompt template system
4. Begin LLM integration
5. Develop initial parser implementation 