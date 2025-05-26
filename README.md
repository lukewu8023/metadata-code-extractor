# Metadata Code Extractor

An intelligent metadata extraction system for code repositories and documentation using LLM-powered analysis and graph-based storage.

## Overview

The Metadata Code Extractor is an agent-driven system that automatically scans code repositories and documentation to extract, analyze, and organize metadata about data entities, relationships, and transformations. It uses Large Language Models (LLMs) for semantic understanding and stores results in both graph and vector databases for comprehensive querying.

## Key Features

- **LLM-Powered Extraction**: Uses OpenRouter API for access to multiple LLM models (GPT-4, Claude-3, etc.)
- **Agent-Driven Orchestration**: Intelligent agent manages the entire workflow using ReAct (Reason-Act) patterns
- **Dual Database Storage**: 
  - Neo4j for structured metadata and relationships
  - Weaviate for vector embeddings and semantic search
- **Gap Detection & Resolution**: Automatically identifies missing metadata and iteratively fills gaps
- **Multi-Language Support**: Extensible parser architecture (starting with Python)
- **Document Integration**: Processes documentation alongside code for comprehensive understanding

## Architecture

```
┌─────────────────────────────────────────┐
│         LLM Orchestrator Agent          │
├─────────────┬───────────────────────────┤
│             │                           │
▼             ▼                           ▼
┌─────────────┐ ┌─────────────────────┐ ┌─────────────────┐
│Code Scanner │ │  Document Scanner   │ │   Completeness  │
│             │ │                     │ │   Evaluator     │
└─────┬───────┘ └─────────┬───────────┘ └─────────┬───────┘
      │                   │                       │
      ▼                   ▼                       ▼
┌─────────────────────────────────────────────────────────┐
│              Database Integration Layer                 │
├─────────────────────────┬───────────────────────────────┤
│      Graph Database     │        Vector Database        │
│        (Neo4j)          │         (Weaviate)            │
└─────────────────────────┴───────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.9+
- Neo4j v4.4.44 (LTS)
- Weaviate v1.24.20
- OpenRouter API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/metadata-code-extractor/metadata-code-extractor.git
cd metadata-code-extractor
```

2. Install dependencies:
```bash
pip install -e .
```

3. Install development dependencies (optional):
```bash
pip install -e ".[dev]"
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database connections
```

## Configuration

Create a `.env` file with the following variables:

```bash
# LLM Provider - OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4
OPENROUTER_SITE_URL=https://github.com/metadata-code-extractor
OPENROUTER_APP_NAME=metadata-code-extractor

# Graph Database - Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Vector Database - Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=  # Optional for local instances

# Application Settings
LOG_LEVEL=INFO
LOG_FILE=metadata_code_extractor.log
```

## Usage

### Command Line Interface

```bash
# Scan a code repository
mce scan --code-path /path/to/repo --doc-path /path/to/docs

# Query metadata gaps
mce query-gaps

# Get entity information
mce get-entity-info "User"

# Run completeness evaluation
mce evaluate-completeness
```

### Python API

```python
from metadata_code_extractor import get_config, setup_logging
from metadata_code_extractor.agents.orchestrator import LLMOrchestratorAgent

# Setup
config = get_config()
setup_logging(config.log_level)

# Initialize agent
agent = LLMOrchestratorAgent(config)

# Run extraction
result = agent.run_extraction(
    code_paths=["/path/to/repo"],
    doc_paths=["/path/to/docs"]
)
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=metadata_code_extractor
```

### Code Quality

```bash
# Format code
black metadata_code_extractor tests

# Sort imports
isort metadata_code_extractor tests

# Type checking
mypy metadata_code_extractor

# Linting
flake8 metadata_code_extractor tests
```

## Technology Stack

- **Language**: Python 3.9+
- **LLM Provider**: OpenRouter (multi-model access)
- **Graph Database**: Neo4j v4.4.44 (LTS)
- **Vector Database**: Weaviate v1.24.20
- **Configuration**: Pydantic + python-dotenv
- **CLI**: Click/Typer
- **Testing**: pytest
- **Code Quality**: black, isort, flake8, mypy

## Project Status

**Current Phase**: Phase 1 - Core Framework and Infrastructure Development

### Completed
- ✅ Requirements analysis and architecture design
- ✅ Technology selection and validation
- ✅ Project structure setup

### In Progress
- 🔄 Core configuration management system
- 🔄 LLM integration framework
- 🔄 Database interface definitions

### Upcoming
- ⏳ Code and document scanners
- ⏳ LLM orchestrator agent
- ⏳ Completeness evaluator

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenRouter for LLM API access
- Neo4j for graph database capabilities
- Weaviate for vector search functionality
- The open-source community for foundational tools and libraries 