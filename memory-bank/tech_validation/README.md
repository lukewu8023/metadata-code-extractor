# Metadata Code Extractor - Technology Validation

This directory contains scripts and tools for validating the technology choices for the Metadata Code Extractor project.

## Overview

Before proceeding with full implementation, we need to validate that our selected technologies work as expected and integrate properly. This process helps identify potential issues early and confirms our technology choices.

## Validation Components

1. **LLM Provider PoC** (`llm_poc.py`) - Tests connectivity and basic functionality with the chosen LLM provider (OpenAI/Anthropic)
2. **Graph Database PoC** (`graph_db_poc.py`) - Tests connectivity and basic CRUD operations with the graph database (Neo4j)
3. **Vector Database PoC** (`vector_db_poc.py`) - Tests embeddings and similarity search with the vector database (ChromaDB)
4. **Configuration Loading PoC** (`config_poc.py`) - Tests Pydantic-based configuration management
5. **Validation Checklist** (`validation_checklist.md`) - Document to track validation results

## Prerequisites

Before running the validation scripts, you need:

1. Python 3.9+ installed
2. Basic API keys and access for:
   - OpenAI API or Anthropic API (for LLM validation)
   - Neo4j instance (for Graph DB validation)
3. `.env` file in the project root with appropriate configuration values (copied from `.env.example`)

## Running the Validation

### Option 1: Run Automated Validation

The simplest approach is to use the included validation script:

```bash
# Make script executable
chmod +x memory-bank/tech_validation/run_validation.sh

# Run validation
./memory-bank/tech_validation/run_validation.sh
```

This script will:
1. Check for dependencies and create a virtual environment if needed
2. Install required packages
3. Run all PoC scripts sequentially
4. Generate a validation report

### Option 2: Run Individual Tests

You can also run each PoC script individually:

```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install python-dotenv pydantic requests openai neo4j chromadb

# Run individual tests
python memory-bank/tech_validation/config_poc.py
python memory-bank/tech_validation/llm_poc.py
python memory-bank/tech_validation/graph_db_poc.py
python memory-bank/tech_validation/vector_db_poc.py
```

## Expected Results

Each script reports its validation status:
- ✅ Success: The technology works as expected
- ⚠️ Warning: The technology works with some limitations or issues
- ❌ Failure: The technology validation failed

## Documenting Validation Results

After running the validation tests:

1. Complete the `validation_checklist.md` document with your results
2. Note any issues or limitations encountered
3. Finalize your technology choices based on the results
4. Update `tasks.md` to reflect completion of Technology Validation Planning

## Next Steps

Once validation is complete and successful:
1. Update the project's main README with the validated technology choices
2. Proceed to Phase 1 implementation (Core Framework and Infrastructure)

## Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API keys are correctly set in the `.env` file
- **Connection Errors**: Check network connectivity and firewall settings
- **Package Installation Errors**: Try installing the packages one by one to identify problematic dependencies
- **Permission Issues**: Ensure you have the necessary permissions to create directories and files

For detailed error logs, review the generated validation results file. 