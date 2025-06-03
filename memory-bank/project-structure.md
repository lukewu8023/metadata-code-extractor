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
│   ├── __init__.py                       # Package initialization
│   ├── cli/                              # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                       # CLI entry point
│   │   └── commands/                     # CLI command modules
│   │       ├── __init__.py
│   │       ├── scan.py                   # Scanning commands
│   │       ├── evaluate.py               # Evaluation commands
│   │       └── config.py                 # Configuration commands
│   ├── core/                             # Core framework components
│   │   ├── __init__.py
│   │   ├── config.py                     # Configuration management
│   │   ├── logging.py                    # Logging setup
│   │   ├── exceptions.py                 # Custom exceptions
│   │   ├── models/                       # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # Configuration models
│   │   │   ├── extraction.py             # Extraction result models
│   │   │   ├── llm.py                    # LLM interaction models
│   │   │   └── database.py               # Database models
│   │   └── utils/                        # Core utilities
│   │       ├── __init__.py
│   │       ├── file_utils.py             # File operations
│   │       └── text_utils.py             # Text processing utilities
│   ├── integrations/                     # External service integrations
│   │   ├── __init__.py
│   │   ├── llm/                          # LLM service integrations
│   │   │   ├── __init__.py
│   │   │   ├── client.py                 # LLM client interface
│   │   │   ├── cache.py                  # Response caching
│   │   │   └── providers/                # LLM provider adapters
│   │   │       ├── __init__.py
│   │   │       ├── base.py               # Base provider interface
│   │   │       ├── openrouter.py         # OpenRouter adapter (validated)
│   │   │       └── mock.py               # Mock provider for testing
│   │   └── database/                     # Database integrations
│   │       ├── __init__.py
│   │       ├── graph/                    # Graph database integrations
│   │       │   ├── __init__.py
│   │       │   ├── interface.py          # Graph DB interface
│   │       │   └── neo4j.py              # Neo4j implementation (validated)
│   │       └── vector/                   # Vector database integrations
│   │           ├── __init__.py
│   │           ├── interface.py          # Vector DB interface
│   │           └── weaviate.py           # Weaviate implementation (validated)
│   ├── agents/                           # Intelligent agents
│   │   ├── __init__.py
│   │   ├── orchestrator.py               # Main orchestrator agent
│   │   ├── strategies/                   # Resolution strategies
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Base strategy interface
│   │   │   ├── semantic_search.py        # Semantic search strategy
│   │   │   └── targeted_scan.py          # Targeted scanning strategy
│   │   └── memory/                       # Agent memory and context
│   │       ├── __init__.py
│   │       └── context.py                # Context management
│   ├── processors/                       # Data processing components
│   │   ├── __init__.py
│   │   ├── scanners/                     # Content scanners
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Base scanner interface
│   │   │   ├── code.py                   # Code metadata scanner
│   │   │   └── document.py               # Document scanner
│   │   ├── evaluators/                   # Quality evaluators
│   │   │   ├── __init__.py
│   │   │   ├── completeness.py           # Completeness evaluator
│   │   │   └── rules/                    # Evaluation rules
│   │   │       ├── __init__.py
│   │   │       ├── base.py               # Base rule interface
│   │   │       └── metadata_rules.py     # Metadata completeness rules
│   │   └── extractors/                   # Data extractors
│   │       ├── __init__.py
│   │       ├── base.py                   # Base extractor interface
│   │       ├── code_entities.py          # Code entity extraction
│   │       └── relationships.py          # Relationship extraction
│   ├── prompts/                          # Prompt templates and management
│   │   ├── __init__.py
│   │   ├── manager.py                    # Prompt management
│   │   └── templates/                    # Template files
│   │       ├── agents/                   # Agent prompts
│   │       │   ├── orchestrator.md       # Orchestrator prompts
│   │       │   └── reasoning.md          # Reasoning prompts
│   │       ├── scanners/                 # Scanner prompts
│   │       │   ├── code_analysis.md      # Code analysis prompts
│   │       │   └── document_analysis.md  # Document analysis prompts
│   │       └── evaluators/               # Evaluator prompts
│   │           └── completeness.md       # Completeness evaluation prompts
│   └── utils/                            # Shared utilities
│       ├── __init__.py
│       ├── validation.py                 # Data validation utilities
│       ├── serialization.py              # Serialization helpers
│       └── performance.py                # Performance monitoring
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── core/
│   │   ├── agents/
│   │   ├── processors/
│   │   ├── integrations/
│   │   └── utils/
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
    ├── detailed-implementation-plan.md
    ├── orchestration-architecture.md
    ├── progress.md
    ├── project-structure.md
    ├── projectbrief.md
    └── tasks.md
```

## Key Modules and Components

### Core (`metadata_code_extractor/core/`)
Centralizes foundational elements:
- **Configuration (`core/config.py`, `core/models/config.py`):** Application settings using Pydantic models
- **Logging (`core/logging.py`):** Logging framework setup
- **Core Data Models (`core/models/*.py`):** Primary Pydantic models for configuration, LLM interactions, database items, and extraction outputs
- **Custom Exceptions (`core/exceptions.py`):** Project-specific error classes
- **Core Utilities (`core/utils/`):** File operations and text processing utilities

### Integrations (`metadata_code_extractor/integrations/`)
Handles external service integrations:
- **LLM Integrations (`integrations/llm/`):** 
  - Client interface and response caching
  - Provider adapters (OpenRouter, Mock) with base interface
- **Database Integrations (`integrations/database/`):**
  - Graph database integrations (Neo4j implementation)
  - Vector database integrations (Weaviate implementation)
  - Abstract interfaces for both database types

### Agents (`metadata_code_extractor/agents/`)
Contains intelligent agent components:
- **Orchestrator Agent (`agents/orchestrator.py`):** Main orchestration logic
- **Resolution Strategies (`agents/strategies/`):** Different approaches for gap resolution
- **Agent Memory (`agents/memory/`):** Context management for agents

### Processors (`metadata_code_extractor/processors/`)
Data processing components:
- **Scanners (`processors/scanners/`):** Content scanning for code and documents
- **Evaluators (`processors/evaluators/`):** Quality assessment with configurable rules
- **Extractors (`processors/extractors/`):** Data extraction for entities and relationships

### Prompts (`metadata_code_extractor/prompts/`)
Prompt template management:
- **Prompt Manager (`prompts/manager.py`):** Loading and formatting of templates
- **Template Files (`prompts/templates/`):** Organized by component type (agents, scanners, evaluators)

### CLI (`metadata_code_extractor/cli/`)
Command-line interface:
- **Main CLI (`cli/main.py`):** Entry point for command-line operations
- **Command Modules (`cli/commands/`):** Specific command implementations

### Utils (`metadata_code_extractor/utils/`)
Shared utility functions:
- **Validation (`utils/validation.py`):** Data validation utilities
- **Serialization (`utils/serialization.py`):** Serialization helpers
- **Performance (`utils/performance.py`):** Performance monitoring

## Project Structure Rationale

### Clear Separation of Concerns
- `core/` for framework essentials
- `integrations/` for external services
- `processors/` for data processing
- `agents/` for intelligent components

### Logical Grouping
- Related functionality grouped together (e.g., all LLM providers under `integrations/llm/providers/`)
- Template files organized by component type in `prompts/templates/`

### Scalability
- Easy to add new providers, processors, or agents without restructuring
- Modular design allows for independent development and testing

### Consistency
- Uniform naming conventions throughout
- Clear module boundaries for better testability

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