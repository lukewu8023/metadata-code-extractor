# Metadata Code Extractor - Implementation Plan (Agent-Driven Orchestration)

## Project Goal
To develop an intelligent metadata extraction system that uses an LLM Orchestrator Agent to scan code and documentation, identify metadata gaps, and iteratively fill those gaps using a combination of semantic search and targeted scanning. This plan reflects the validated technology stack.

## Validated Technology Stack

### Core Technologies (Validated ✅)
-   **LLM Provider:** OpenRouter API (multi-model access)
    *   Primary Model: `openai/gpt-4o-mini` (validated working, e.g., `llm_poc.py`)
    *   Production Model Options: `openai/gpt-4`, `anthropic/claude-3-sonnet`
    *   Client: `openai` library (OpenRouter compatible, version as per `run_validation.sh`)
-   **Graph Database:** Neo4j (target v4.4.44, validated with v4.4.12 driver)
    *   Driver: `neo4j==4.4.12` (as per `run_validation.sh` and `graph_db_poc.py`)
    *   Connection: Via URI, User, Password (validated in `graph_db_poc.py`)
-   **Vector Database:** Weaviate (target v1.24.20, validated with client v3.24.2)
    *   Client: `weaviate-client==3.24.2` (as per `run_validation.sh` and `vector_db_poc.py`)
    *   Connection: Via URL, optional API Key (validated in `vector_db_poc.py`)
-   **Configuration:** Pydantic, python-dotenv (validated in `config_poc.py`)
-   **Python Environment:** Python 3.9+ (validation scripts use system Python, assumed to be compatible)

## Implementation Phases

### Phase 1: Core Framework and Infrastructure (Estimate: 3-4 Weeks)
**Objective:** Establish foundational elements using the validated technology stack.

1.  **Project Structure Setup (as per `project-structure.md`):**
    *   Initialize Python project directory (`metadata_code_extractor/` with subdirectories: `core`, `agents`, `scanners`, `evaluators`, `llm_integrations`, `db_integrations`, `prompts`, `utils`, `tests`, `cli`).
    *   Set up dependency management (e.g., `pyproject.toml` or `requirements.txt` with validated versions: `python-dotenv`, `pydantic`, `requests`, `openai` (for OpenRouter), `neo4j==4.4.12`, `weaviate-client==3.24.2`).
2.  **Configuration Management System (based on `configuration-management-design.md` and `config_poc.py`):**
    *   Implement `core/config.py` using Pydantic models (`core/models/config_models.py`).
    *   Load from `.env` files and environment variables.
    *   Validate configuration on startup.
3.  **Logging Framework (based on `logging-design.md`):**
    *   Implement `core/logging_setup.py` using Python's `logging` module.
    *   Configurable log levels, formats, and outputs (console, file).
4.  **Testing Infrastructure (based on `testing-strategy.md`):**
    *   Set up `pytest` with initial directory structure (`tests/unit`, `tests/integration`).
    *   Create `conftest.py` for common fixtures.
5.  **LLM Integration Framework (based on `llm-integration-design.md` and `llm_poc.py`):**
    *   Define `LLMClient` interface in `metadata_code_extractor/llm_integrations/llm_client.py`.
    *   Implement `OpenRouterAdapter` in `metadata_code_extractor/llm_integrations/providers/openrouter_adapter.py` using the `openai` library.
    *   Implement basic `PromptManager` in `metadata_code_extractor/llm_integrations/prompt_manager.py` (loading from `prompts/` directory).
    *   Implement initial `LLMCache` in `metadata_code_extractor/llm_integrations/llm_cache.py` (e.g., in-memory or simple file-based).
6.  **Database Interface Definitions and Adapters (based on `database-integration-design.md` and PoCs):**
    *   Define `GraphDBInterface` in `metadata_code_extractor/db_integrations/graph_db_interface.py`.
    *   Implement `Neo4jAdapter` in `metadata_code_extractor/db_integrations/graph_db/neo4j_adapter.py` (using `neo4j==4.4.12` driver).
    *   Define `VectorDBInterface` in `metadata_code_extractor/db_integrations/vector_db_interface.py`.
    *   Implement `WeaviateAdapter` in `metadata_code_extractor/db_integrations/vector_db/weaviate_adapter.py` (using `weaviate-client==3.24.2`).
    *   Include fallback embedding generation logic from `vector_db_poc.py` if OpenRouter embedding models are not immediately used/available.
7.  **Core Data Models (based on `core-data-models.md`):**
    *   Implement Pydantic models in `core/models/` for configuration, LLM interactions, DB items, and extraction outputs (e.g., `ExtractedDataEntity`, `MetadataGapInfo`).
8.  **Basic CLI Structure (based on `project-structure.md`):**
    *   Implement `cli.py` using a library like `click` or `argparse` with placeholder commands.

### Phase 2: Core Components Development (Estimate: 4-6 Weeks)
**Objective:** Develop the primary processing components.

1.  **Code Metadata Scanner (Initial Version - based on `code-scanner-design.md`):**
    *   Implement `scanners/base_scanner.py` with a base scanner interface.
    *   Implement `scanners/code_scanner.py`.
    *   Basic file traversal and language identification (Python initially).
    *   LLM-based extraction for primary code entities (classes, functions) and their fields/attributes.
    *   Prompts for structured metadata (JSON) from code snippets.
    *   Integration with `LLMClient` and `EmbeddingGenerator` (from LLM Integration framework).
    *   Integration with `GraphDBInterface` and `VectorDBInterface` for storing results.
    *   Implement `scan_repository(repo_path)` and `scan_targeted(file_path, target_details)`.
2.  **Document Scanner (Initial Version - based on `document-scanner-design.md`):**
    *   Implement `scanners/document_scanner.py`.
    *   Support for parsing Markdown files initially.
    *   Document chunking strategy.
    *   LLM-based extraction for document structure and summaries.
    *   Heuristic or simple LLM prompts for identifying links to code entities.
    *   Integration with `LLMClient` and `EmbeddingGenerator`.
    *   Integration with `GraphDBInterface` and `VectorDBInterface`.
    *   Implement `scan_document_repository(source_path_or_url_list)` and `scan_document_targeted(doc_identifier, target_details)`.

### Phase 3: Agent and Orchestration System (Estimate: 5-7 Weeks)
**Objective:** Develop the intelligent core of the system.

1.  **LLM Orchestrator Agent (Core Logic - based on `llm-orchestrator-agent-design.md`):**
    *   Implement `agents/llm_orchestrator_agent.py`.
    *   Agent state management.
    *   ReAct (Reason-Act) loop framework.
    *   Prompts for agent reasoning (analyzing state, deciding next actions).
    *   Ability to invoke Scanners and Evaluator.
    *   Initial strategies for choosing between semantic search and targeted scanning.
2.  **Completeness Evaluator (Initial Version - based on `completeness-evaluator-design.md`):**
    *   Implement `evaluators/completeness_evaluator.py`.
    *   Define initial completeness criteria (e.g., entity description exists, field type defined).
    *   Logic to query `GraphDBInterface` and identify items failing criteria.
    *   Functionality to create/update `MetadataGap` nodes in the Graph DB.
    *   Prompts for summarizing and prioritizing gaps (if LLM-assisted).
    *   Implement `evaluate_completeness()` and `get_open_gaps()`.
3.  **Orchestration Workflow (Initial):**
    *   Implement the main sequence: Initial Code Scan -> Initial Doc Scan -> Initial Evaluation -> Basic Gap Loop (semantic search for first iteration).

### Phase 4: Integration, Iterative Improvement & Advanced Features (Estimate: 6-8 Weeks)
**Objective:** Refine components, enable the full iterative loop, and add advanced capabilities.

1.  **Full Gap Resolution Loop:**
    *   Enhance Agent's ability to choose and execute targeted scans based on gap type and context.
    *   Agent processes results from semantic search and targeted scans to update Graph DB.
    *   Refined re-evaluation by Completeness Evaluator.
    *   Agent logic to decide if a gap is resolved, needs more attempts, or requires human input.
2.  **Advanced Scanning & Extraction:**
    *   Code Scanner: Deeper analysis (relationships like `REFERENCES`, `TRANSFORMED_FROM`), support for more languages.
    *   Document Scanner: Support for more formats (e.g., PDF via PyMuPDF, HTML via BeautifulSoup), more sophisticated extraction of relationships.
3.  **Enhanced Completeness Evaluator:**
    *   More sophisticated completeness rules and heuristics.
    *   Improved prioritization of gaps.
4.  **Refined Agent Reasoning:**
    *   Improved prompts for nuanced decision-making and error handling.
    *   Ability to learn from failed attempts.
5.  **Performance & Scalability:**
    *   Optimize DB queries and LLM calls (batching).
    *   Refine caching.

### Phase 5: CLI, Testing, and Documentation (Estimate: 4-5 Weeks)
**Objective:** Make the system usable, robust, and well-documented.

1.  **Command Line Interface (CLI):**
    *   Full implementation of CLI commands defined in `project-structure.md`.
    *   Progress reporting, configuration options.
2.  **Comprehensive Testing:**
    *   Expand unit tests for all components.
    *   Develop integration tests for interactions (Agent-Scanner, Agent-Evaluator, Scanner-DB).
    *   End-to-end tests with sample code/doc repositories.
3.  **User and Developer Documentation:**
    *   User guide (install, configure, run, understand outputs).
    *   Developer guide (architecture, extending scanners/rules, API docs).
    *   Documentation for `graph-schema.md` and prompt templates (`prompt-engineering.md`).
4.  **Packaging & Deployment Considerations:**
    *   Package for distribution (e.g., PyPI).
    *   (Optional) Dockerfile.

## Total Estimated Timeline: 22-30 Weeks

## Key Milestones & Deliverables:
-   **End of Phase 1:** Core framework setup, basic LLM/DB interfaces and adapters implemented and unit-tested.
-   **End of Phase 2:** Initial versions of Code and Document Scanners functional, storing basic data in DBs.
-   **End of Phase 3:** Orchestrator Agent can run initial scans, evaluate completeness, and attempt semantic search for gaps.
-   **End of Phase 4:** Full iterative gap resolution loop functional; advanced scanning capabilities integrated.
-   **End of Phase 5:** Usable CLI, comprehensive tests, full documentation, packaged application.

## Assumptions & Risks:
-   **LLM Access & Performance:** Assumes reliable access to OpenRouter. Latency can be a bottleneck. (Mitigation: effective caching, batching, efficient prompting, potential model tier selection).
-   **Prompt Engineering Complexity:** Crafting effective prompts is iterative. (Mitigation: use `prompt-engineering.md` guidelines, version prompts, evaluate).
-   **Data Variety:** Handling diverse languages, doc formats, project structures. (Mitigation: start focused, design for extensibility).
-   **Scalability:** Large repositories may pose challenges. (Mitigation: optimize critical paths, efficient DB usage).
-   **Accuracy of Extraction:** LLM extraction may not be 100% accurate. (Mitigation: confidence scoring, iterative refinement, human review flags). 