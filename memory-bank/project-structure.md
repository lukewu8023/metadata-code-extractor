# Metadata Code Extractor - Project Structure

## Directory Structure

```
metadata_code_extractor_project/  # Root project folder
├── README.md
├── pyproject.toml
├── setup.py                   # Optional, if not using pyproject.toml exclusively
├── .gitignore
├── .env.example
├── requirements.txt           # Generated if needed, primary is pyproject.toml
├── requirements-dev.txt
├── metadata_code_extractor/        # Main package (source root)
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface entry point
│   ├── main.py                # Main application orchestrator (if needed beyond CLI)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration loading (AppConfig)
│   │   ├── exceptions.py      # Custom project-wide exceptions
│   │   ├── logging_setup.py   # Logging configuration function
│   │   └── models/            # Core Pydantic models
│   │       ├── __init__.py
│   │       ├── config_models.py # Pydantic models for configuration
│   │       ├── llm_models.py    # Models for LLM interactions (ChatMessage, etc.)
│   │       ├── db_models.py     # Models for DB items (NodeID, VectorItem, etc.)
│   │       └── extraction_models.py # Models for extracted data (DataEntity, Field, etc.)
│   ├── agents/
│   │   ├── __init__.py
│   │   └── llm_orchestrator_agent.py
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── base_scanner.py
│   │   ├── code_scanner.py
│   │   └── document_scanner.py
│   ├── evaluators/
│   │   ├── __init__.py
│   │   └── completeness_evaluator.py
│   ├── llm_integrations/       # LLM client, providers, prompt management
│   │   ├── __init__.py
│   │   ├── llm_client.py      # LLMClient interface
│   │   ├── providers/         # Adapters for different LLM providers (OpenAI, Anthropic, Mock)
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py
│   │   │   └── openai_adapter.py
│   │   ├── prompt_manager.py
│   │   └── llm_cache.py
│   ├── db_integrations/          # Database interaction layer
│   │   ├── __init__.py
│   │   ├── graph_db_interface.py
│   │   ├── vector_db_interface.py
│   │   ├── graph_db/          # Concrete Graph DB implementations
│   │   │   ├── __init__.py
│   │   │   └── neo4j_impl.py  # Example
│   │   └── vector_db/         # Concrete Vector DB implementations
│   │       ├── __init__.py
│   │       └── chromadb_impl.py # Example
│   ├── prompts/               # Directory for storing prompt templates (e.g., .txt, .md files)
│   │   └── agent/
│   │   └── scanner/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   └── general_utils.py
│   └── version.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── core/
│   │   ├── agents/
│   │   └── ...
│   └── integration/
│       ├── __init__.py
│       └── ...
├── docs/
│   └── ...
├── examples/
│   └── ...
├── .cursor/                # Cursor-specific files (rules, etc.)
│   └── rules/
│       └── ...
└── memory-bank/            # Project planning and context documents
    ├── activeContext.md
    ├── architecture.md
    ├── graph-schema.md
    ├── implementation-plan.md
    ├── orchestration-architecture.md
    ├── progress.md
    ├── project-structure.md
    ├── projectbrief.md
    └── tasks.md
    # Add other design docs here e.g.:
    # llm-orchestrator-agent-design.md
    # code-scanner-design.md
    # ... etc.
```

## Key Modules and Components (Updated Alignment)

### Core (`metadata_code_extractor/core/`)
Centralizes foundational elements:
-   **Configuration (`core/config.py`, `core/models/config_models.py`):** Manages application settings using Pydantic models as defined in `configuration-management-design.md`.
-   **Logging (`core/logging_setup.py`):** Sets up the logging framework as per `logging-design.md`.
-   **Core Data Models (`core/models/*.py`):** Contains all primary Pydantic models for configuration, LLM interactions, database items, and especially the extraction outputs (`ExtractedDataEntity`, `MetadataGapInfo`, etc.) as per `core-data-models.md`.
-   **Custom Exceptions (`core/exceptions.py`):** Project-specific error classes.

### Agents (`metadata_code_extractor/agents/`)
Contains the intelligent agent(s):
-   **LLM Orchestrator Agent (`agents/llm_orchestrator_agent.py`):** Implements the logic described in `llm-orchestrator-agent-design.md`.

### Scanners (`metadata_code_extractor/scanners/`)
Responsible for parsing code and documents:
-   **Code Scanner (`scanners/code_scanner.py`):** Implements `code-scanner-design.md`.
-   **Document Scanner (`scanners/document_scanner.py`):** Implements `document-scanner-design.md`.

### Evaluators (`metadata_code_extractor/evaluators/`)
For assessing metadata completeness:
-   **Completeness Evaluator (`evaluators/completeness_evaluator.py`):** Implements `completeness-evaluator-design.md`.

### LLM Integrations (`metadata_code_extractor/llm_integrations/`)
Handles all interactions with Large Language Models:
-   **LLM Client (`llm_integrations/llm_client.py`):** Abstract interface and core client logic as per `llm-integration-design.md`.
-   **Providers (`llm_integrations/providers/`):** Adapters for specific LLM services (OpenAI, Anthropic, Mock).
-   **Prompt Manager (`llm_integrations/prompt_manager.py`):** Manages loading and formatting of prompt templates stored in the `metadata_code_extractor/prompts/` directory.
-   **LLM Cache (`llm_integrations/llm_cache.py`):** Caching mechanism for LLM responses.

### DB Integrations (`metadata_code_extractor/db_integrations/`)
Abstracts database interactions:
-   **Interfaces (`db_integrations/graph_db_interface.py`, `db_integrations/vector_db_interface.py`):** Abstract base classes as per `database-integration-design.md`.
-   **Concrete Implementations (`db_integrations/graph_db/`, `db_integrations/vector_db/`):** Specific adapters for chosen database technologies.

### Prompts (`metadata_code_extractor/prompts/`)
This directory will store the actual prompt template files (e.g., `.txt`, `.md`), organized by component (agent, scanner type). The `PromptManager` will load templates from here.

### CLI (`metadata_code_extractor/cli.py`)
Command-line interface for the application.

### Utils (`metadata_code_extractor/utils/`)
Shared utility functions.

*(The rest of the file, including pyproject.toml example, .env.example, CLI structure example, and Development Guidelines, can remain largely the same but should be reviewed to ensure consistency with the updated main package structure. The main focus of this update is the directory layout and component mapping within the `metadata_code_extractor` source package.)*

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