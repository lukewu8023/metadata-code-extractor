# Metadata Code Extractor - Implementation Plan (Agent-Driven Orchestration)

## Project Goal
To develop an intelligent metadata extraction system that uses an LLM Orchestrator Agent to scan code and documentation, identify metadata gaps, and iteratively fill those gaps using a combination of semantic search and targeted scanning.

## Implementation Phases

### Phase 1: Core Framework and Infrastructure (3-4 Weeks)
Focus: Establish the foundational elements of the project.

1.  **Project Setup & Environment:**
    *   Initialize Python project structure (`metadata_code_extractor/` with subdirs: `core`, `agents`, `scanners`, `evaluators`, `db_integrations`, `prompts`, `utils`, `tests`, `cli`).
    *   Set up dependency management (e.g., `requirements.txt` or `pyproject.toml` with Poetry/PDM).
    *   Implement configuration management (e.g., Pydantic settings, `.env` files).
    *   Establish logging framework (e.g., `logging` module configured for console/file output).
    *   Set up testing infrastructure (e.g., `pytest` with basic test structure).
2.  **LLM Integration Framework:**
    *   Develop a generic LLM client interface (supporting chat, completions, embeddings).
    *   Implement adapter for at least one LLM provider (e.g., OpenAI, Anthropic).
    *   Basic prompt templating/management system.
    *   Initial caching mechanism for LLM responses.
3.  **Database Interface Definitions:**
    *   Define abstract interfaces for Graph DB interaction (CRUD operations for nodes/relationships based on `graph-schema.md`).
    *   Define abstract interfaces for Vector DB interaction (add embeddings, semantic search).
4.  **Basic Data Models:**
    *   Implement Pydantic models for core concepts (e.g., `CodeFile`, `DocumentFile`, `MetadataElement`, `Gap`).

### Phase 2: Core Components Development (4-6 Weeks)
Focus: Develop the primary processing components.

1.  **Code Metadata Scanner (Initial Version):**
    *   Implement basic file traversal for code repositories.
    *   Develop LLM-based extraction for primary code entities and fields (e.g., classes, functions, attributes in Python).
    *   Prompts for extracting basic structured metadata from code snippets.
    *   Functionality to generate embeddings for code snippets/comments.
    *   Integration with Graph DB and Vector DB interfaces for storing results.
    *   Develop `scan_code_repository(path)` and `scan_code_file_targeted(file_path, targets)` functions.
2.  **Document Scanner (Initial Version):**
    *   Implement basic file traversal for document directories.
    *   Support for parsing at least one document type (e.g., Markdown).
    *   LLM-based extraction for identifying document structure (headings, sections) and potential links to code entities (heuristic-based or simple LLM prompts).
    *   Document chunking strategy (e.g., by section or fixed size with overlap).
    *   Functionality to generate embeddings for document chunks.
    *   Integration with Graph DB and Vector DB interfaces.
    *   Develop `scan_document_repository(path)` and `scan_document_file_targeted(file_path, targets)` functions.
3.  **Graph DB Implementation (Initial):**
    *   Implement the Graph DB interface for a chosen provider (e.g., Neo4j connector, or a simpler local alternative like SQLite with JSON for early dev).
    *   Functions to add/update nodes and relationships as per `graph-schema.md` (DataEntity, Field, Document, DocumentChunk initially).
4.  **Vector DB Implementation (Initial):**
    *   Implement the Vector DB interface for a chosen provider (e.g., FAISS, ChromaDB, Pinecone client).
    *   Functions to add embeddings and perform similarity searches.

### Phase 3: Agent and Orchestration System (5-7 Weeks)
Focus: Develop the intelligent core of the system.

1.  **LLM Orchestrator Agent (Core Logic):**
    *   Implement agent state management.
    *   Develop ReAct (Reason-Act) loop framework.
    *   Prompts for agent reasoning: analyzing current state, deciding next actions (e.g., "Should I do a broad scan?", "Which gap to prioritize?", "How to resolve this gap?").
    *   Ability to invoke Code Scanner, Document Scanner, and Completeness Evaluator.
    *   Initial strategies for choosing between semantic search and targeted scanning.
2.  **Completeness Evaluator (Initial Version):**
    *   Define initial completeness criteria (e.g., "DataEntity has description?", "Field has type?").
    *   Logic to query Graph DB and identify items failing criteria, creating `MetadataGap` nodes.
    *   Prompts for summarizing and prioritizing gaps.
    *   Develop `evaluate_completeness()` and `get_gaps()` functions.
3.  **Orchestration Workflow (Initial):**
    *   Implement the main sequence: Initial Code Scan -> Initial Doc Scan -> Initial Evaluation -> Basic Gap Loop (semantic search only for first iteration).
    *   Store `MetadataGap` nodes in Graph DB.

### Phase 4: Integration, Iterative Improvement & Advanced Features (6-8 Weeks)
Focus: Refine components, enable the full iterative loop, and add advanced capabilities.

1.  **Full Gap Resolution Loop:**
    *   Enhance Agent's ability to choose and execute targeted scans (Code and Document) based on gap type and context.
    *   Agent's ability to process results from semantic search and targeted scans to update Graph DB (potentially creating/updating entities/fields or linking documents).
    *   Refined re-evaluation by Completeness Evaluator after each attempt.
    *   Logic for the Agent to decide if a gap is resolved, needs more attempts, or requires human input.
2.  **Advanced Scanning & Extraction:**
    *   Code Scanner: Deeper analysis (e.g., relationships like `REFERENCES`, `TRANSFORMED_FROM`), more languages.
    *   Document Scanner: Support for more formats (PDF), more sophisticated extraction of relationships between document parts and code entities (`REFERENCES_CODE_ENTITY`, `DESCRIBES`).
3.  **Enhanced Completeness Evaluator:**
    *   More sophisticated completeness rules and heuristics.
    *   Better prioritization of gaps.
4.  **Refined Agent Reasoning:**
    *   Improved prompts for more nuanced decision-making and error handling.
    *   Ability to learn from failed attempts (e.g., not retrying the same strategy on a persistent gap).
5.  **Performance & Scalability:**
    *   Implement caching strategies effectively.
    *   Optimize DB queries and LLM calls (batching where possible).

### Phase 5: CLI, Testing, and Documentation (4-5 Weeks)
Focus: Make the system usable, robust, and well-documented.

1.  **Command Line Interface (CLI):**
    *   Develop CLI using a library like `click` or `argparse`.
    *   Commands to initiate full scan, report on progress, query specific metadata.
    *   Configuration options (paths, API keys, DB settings).
2.  **Comprehensive Testing:**
    *   Unit tests for all core components and utilities.
    *   Integration tests for interactions between Agent, Scanners, Evaluator, and DBs.
    *   End-to-end tests with sample code/doc repositories.
    *   Develop a small, representative test dataset.
3.  **User and Developer Documentation:**
    *   User guide: How to install, configure, and run the extractor; understanding outputs.
    *   Developer guide: Architecture overview, how to extend with new scanners/rules, API documentation for core modules.
    *   Documentation for `graph-schema.md` and prompt templates.
4.  **Packaging & Deployment Considerations:**
    *   Package the application for distribution (e.g., PyPI).
    *   (Optional) Dockerfile for containerized deployment.

## Total Estimated Timeline: 22-30 Weeks

## Key Milestones & Deliverables:
- **End of Phase 1:** Core framework setup, basic LLM/DB interfaces.
- **End of Phase 2:** Initial versions of Code and Document Scanners, basic DB implementations working.
- **End of Phase 3:** Orchestrator Agent can run initial scans, evaluate completeness, and attempt semantic search for gaps.
- **End of Phase 4:** Full iterative gap resolution loop functional; advanced scanning capabilities integrated.
- **End of Phase 5:** Usable CLI, comprehensive tests, full documentation, packaged application.

## Assumptions & Risks:
- **LLM Access & Performance:** Assumes reliable access to a capable LLM API. Performance/latency of LLM calls can be a bottleneck (Mitigation: caching, batching, efficient prompting).
- **Prompt Engineering Complexity:** Crafting effective prompts for diverse tasks will require iteration (Mitigation: dedicated prompt engineering effort, versioning, evaluation framework).
- **Data Variety:** Handling diverse coding languages, documentation formats, and project structures (Mitigation: start focused, design for extensibility).
- **Scalability:** Processing large repositories may pose challenges (Mitigation: optimize critical paths, consider distributed processing for some tasks if necessary later).
- **Accuracy of Extraction:** LLM-based extraction may not be 100% accurate (Mitigation: confidence scoring, iterative refinement, human review flags for low-confidence items). 