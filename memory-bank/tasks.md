# Project Plan Summary - Metadata Code Extractor (Agent-Driven Orchestration)

## Project Complexity
**Level 3 - Intermediate System**: This project involves multiple interconnected components, complex data processing workflows, integration with external systems (graph and vector databases), and LLM-based semantic extraction.

## Requirements Analysis Summary
The primary requirement is to develop an intelligent metadata extraction system. This system will utilize an LLM Orchestrator Agent to:
1.  Scan code repositories and associated documentation.
2.  Extract detailed metadata, focusing on data attribute lineage, relationships, and contextual information.
3.  Identify "MetadataGaps" where information is missing or incomplete.
4.  Iteratively fill these gaps using a combination of semantic search (via Vector DB) and targeted re-scanning of code/documents.
5.  Store structured metadata in a Graph DB and document/code embeddings in a Vector DB.

## Key Components Affected
The system comprises several newly developed, interconnected components:
*   **LLM Orchestrator Agent:** Core decision-making and workflow management.
*   **Code Metadata Scanner:** For processing source code.
*   **Document Scanner:** For processing documentation.
*   **Completeness Evaluator:** For identifying metadata gaps.
*   **LLM Integration Framework:** Generic client, prompt management, caching.
*   **Database Integration Layer:** Interfaces for Graph DB and Vector DB.
*   **Core Data Models:** Pydantic models for all data interchange.
*   **Configuration Management System.**
*   **Logging System.**
*   **CLI.**

## Architecture Considerations
*   **Agent-Driven Orchestration:** An LLM-based agent (LLM Orchestrator Agent) will manage the entire workflow, employing a ReAct (Reason-Act) pattern.
*   **Modular Design:** Components (Scanners, Evaluator, DB Integrations) are designed to be modular with clear interfaces.
*   **Dual Database System:**
    *   Graph Database: For storing structured metadata, relationships, and gaps (schema defined in `graph-schema.md`).
    *   Vector Database: For storing embeddings of code and document chunks to support semantic search.
*   **LLM-Powered Extraction and Reasoning:** LLMs will be used for parsing code/documents, extracting metadata, and powering the agent's decision-making.
*   **Iterative Gap Filling:** The system will iteratively identify and attempt to resolve metadata gaps.
*   **Extensibility:** Design should allow for adding support for new languages, document formats, and completeness rules.

## Dependencies
*   **Python 3.9+ Environment.**
*   **LLM Provider:** Access to a capable LLM API (e.g., OpenAI, Anthropic). Selection pending.
*   **Graph Database:** A graph database system (e.g., Neo4j, Memgraph). Selection pending.
*   **Vector Database:** A vector database system/library (e.g., ChromaDB, FAISS, Weaviate). Selection pending.
*   **Python Libraries:** As defined in `pyproject.toml`/`requirements.txt` (e.g., Pydantic, Click, HTTP clients).

## Potential Challenges & Mitigations
*   **LLM Access & Performance:**
    *   Challenge: Reliable access to LLM API, potential latency/rate limits.
    *   Mitigation: Caching, batching, efficient prompting, configurable retry mechanisms.
*   **Prompt Engineering Complexity:**
    *   Challenge: Crafting effective and robust prompts for diverse extraction and reasoning tasks.
    *   Mitigation: Iterative development, versioning of prompts, dedicated evaluation, modular prompt design.
*   **Data Variety & Complexity:**
    *   Challenge: Handling diverse coding languages, documentation formats, and project structures.
    *   Mitigation: Start with a focused set (e.g., Python, Markdown), design for extensibility, use LLM flexibility.
*   **Accuracy and Non-Determinism of LLMs:**
    *   Challenge: LLM-based extraction may not be 100% accurate and can be non-deterministic.
    *   Mitigation: Confidence scoring, validation rules, targeted re-scans, allowing human review flags, designing prompts for structured output.
*   **Scalability for Large Repositories:**
    *   Challenge: Processing very large codebases and document sets efficiently.
    *   Mitigation: Optimize critical paths, efficient chunking, consider asynchronous processing where applicable, batch DB operations.
*   **Integration Complexity:**
    *   Challenge: Ensuring smooth interaction between multiple components (Agent, Scanners, DBs).
    *   Mitigation: Clear API contracts (defined in design docs), thorough integration testing.

## Creative Phase Components
Based on the design, the following areas involve significant design decisions and will benefit from or require creative approaches during implementation:
*   **LLM Orchestrator Agent Reasoning Logic:** Designing the ReAct prompts and decision-making framework for the agent.
*   **Prompt Engineering:** Crafting and refining LLM prompts for all scanners, the evaluator, and the agent itself. This is an ongoing creative process.
*   **Completeness Rules Definition:** Designing the initial and subsequent sets of rules for the `CompletenessEvaluator`.
*   **Gap Resolution Strategies:** Developing diverse and effective strategies for the agent to fill different types of metadata gaps.

## Technology Validation Plan
Before full-scale implementation of Phase 1, key technologies must be selected and validated.

### 1. Finalize Technology Stack Selection
*   **Task:** Complete the pending decisions for specific technology choices.
    *   [ ] Finalize selection of specific LLM provider (e.g., OpenAI, Anthropic) and specific model versions for initial implementation.
    *   [ ] Finalize selection of specific Graph DB (e.g., Neo4j, Memgraph) for initial implementation.
    *   [ ] Finalize selection of specific Vector DB (e.g., Chroma, FAISS, Weaviate) for initial implementation.
*   **Output:** Documented choices for LLM, Graph DB, and Vector DB.

### 2. Document Chosen Technologies
*   **Task:** Update relevant project documentation (e.g., `README.md`, `architecture.md` notes, internal design notes) with the selected technologies.
*   **Output:** Consistent documentation of the tech stack.

### 3. Create Minimal Proofs of Concept (PoCs)
*   **Task:** For each selected core technology, create a small "hello world" style PoC to ensure basic connectivity, interaction, and understanding of the API.
    *   [ ] LLM PoC: Basic API call to chosen LLM provider (e.g., simple completion or embedding generation).
    *   [ ] Graph DB PoC: Connect to chosen Graph DB, create a sample node and relationship, query it.
    *   [ ] Vector DB PoC: Connect to chosen Vector DB, add a sample embedding, perform a similarity search.
*   **Output:** Simple, runnable scripts for each PoC.

### 4. Verify Build Process and Required Dependencies
*   **Task:** Ensure the project can be built with the chosen technologies and their client libraries.
    *   [ ] Add necessary client libraries for the selected LLM, Graph DB, and Vector DB to `pyproject.toml` / `requirements.txt`.
    *   [ ] Successfully install all dependencies in a clean environment.
*   **Output:** Updated dependency files; successful local build.

### 5. Validate Base Configurations
*   **Task:** Set up and validate basic configuration needed for the PoCs and initial development.
    *   [ ] Add example configurations for LLM API keys, DB connection strings to `.env.example` and local `.env` for testing.
    *   [ ] Ensure PoC scripts can load and use these configurations.
*   **Output:** Updated configuration examples; PoCs run successfully with externalized config.

### 6. Technology Validation Checkpoints
*   [ ] LLM Provider: API connectivity established, basic request/response working.
*   [ ] Graph DB: Connection established, basic CRUD (Create, Read, Update, Delete) operations functional.
*   [ ] Vector DB: Connection established, basic embedding/search operations functional.
*   [ ] Dependencies: All necessary client libraries for chosen technologies are identified and installable.
*   [ ] Configuration: Basic configuration for accessing these services is understood and can be managed.
*   [ ] Proofs of Concept: Minimal "Hello World" PoCs for each technology are created and working.

## Implementation Strategy & Detailed Steps
The project will be implemented in five phases, as detailed in `implementation-plan.md`. The tasks below represent the detailed breakdown.

## Implementation Phases (Aligned with implementation-plan.md)

### Phase 1: Core Framework and Infrastructure (3-4 Weeks)
Focus: Establish the foundational elements of the project.

1.  **Project Setup & Environment:**
    *   [ ] Initialize Python project structure (`metadata_code_extractor/` with subdirs: `core`, `agents`, `scanners`, `evaluators`, `db`, `prompts`, `utils`, `tests`, `cli`).
    *   [ ] Set up dependency management (e.g., `pyproject.toml` with Poetry or PDM, and `requirements.txt` for broader compatibility if needed).
    *   [ ] Design and implement configuration management system (as per `configuration-management-design.md`).
        *   [ ] Implement `ConfigLoader` for YAML/env vars.
        *   [ ] Define `AppConfig` and related Pydantic models (`core/config.py`, `core/models/config_models.py`).
    *   [ ] Design and implement logging framework (as per `logging-design.md`).
        *   [ ] Implement `setup_logging` function.
        *   [ ] Define standard log formatters.
    *   [ ] Set up testing infrastructure (`pytest` with basic structure, as per `testing-strategy.md`).
        *   [ ] Create `tests/` directory structure.
        *   [ ] Configure `pytest.ini` or `pyproject.toml` for pytest.
2.  **LLM Integration Framework (as per `llm-integration-design.md`):**
    *   [ ] Develop `LLMClient` interface (`core/llm/client.py`).
    *   [ ] Implement `LLMProviderAdapter` interface and at least one concrete adapter (e.g., `OpenAIAdapter`, `MockAdapter`).
    *   [ ] Basic `PromptManager` for loading and filling templates from files (`core/prompts/manager.py`).
    *   [ ] Initial `LLMCache` (e.g., in-memory or simple file-based).
    *   [ ] Define `ChatMessage`, `ModelConfig`, `EmbeddingConfig` Pydantic models (`core/models/llm_models.py`).
3.  **Database Interface Definitions (as per `database-integration-design.md`):**
    *   [ ] Define `GraphDBInterface` abstract base class (`core/db/graph_interface.py`).
    *   [ ] Define `VectorDBInterface` abstract base class (`core/db/vector_interface.py`).
    *   [ ] Define common DB-related Pydantic models (e.g., `NodeID`, `VectorEmbeddingItem`) (`core/models/db_models.py`).
4.  **Core Data Models (as per `core-data-models.md`):**
    *   [ ] Implement core Pydantic models for `ExtractedDataEntity`, `ExtractedField`, `ExtractedDocument`, `ExtractedDocumentChunk`, `MetadataGapInfo`, `ScanReport`, etc. (`core/models/extraction_models.py`).
5.  **Basic CLI Structure:**
    *   [ ] Implement initial CLI structure using `click` (`cli.py`) with a basic command (e.g., `scan` placeholder).

### Phase 2: Core Components Development (4-6 Weeks)
Focus: Develop the primary processing components.

1.  **Code Metadata Scanner (Initial Version - as per `code-scanner-design.md`):**
    *   [ ] Implement `FileProcessor` for file reading and language identification.
    *   [ ] Implement `LanguageParser` interface and an initial `PythonParser` (LLM-based).
    *   [ ] Implement `MetadataExtractor` for basic entities/fields from Python.
    *   [ ] Implement `EmbeddingGenerator` for code snippets.
    *   [ ] Implement `OutputFormatter` for Graph/Vector DB data.
    *   [ ] Define `ScanConfig`, `TargetScanDetails`, `ScanResult` Pydantic models.
    *   [ ] Develop `scan_repository()` and `scan_targeted()` methods.
    *   [ ] Unit tests for Code Scanner components.
2.  **Document Scanner (Initial Version - as per `document-scanner-design.md`):**
    *   [ ] Implement `DocumentFetcher` for local files.
    *   [ ] Implement `FormatParser` interface and an initial `MarkdownParser`.
    *   [ ] Implement `ContentChunker` (e.g., by section).
    *   [ ] Implement `MetadataExtractor` for document structure and basic entity mentions.
    *   [ ] Implement `EmbeddingGenerator` for document chunks.
    *   [ ] Define `DocSourceInfo`, `DocScanConfig`, `DocScanResult` Pydantic models.
    *   [ ] Develop `scan_document_repository()` and `scan_document_targeted()` methods.
    *   [ ] Unit tests for Document Scanner components.
3.  **Graph DB Implementation (Initial - as per `database-integration-design.md`):**
    *   [ ] Implement a concrete adapter for `GraphDBInterface` (e.g., `Neo4jAdapter` or `SQLiteGraphMockAdapter`).
    *   [ ] Implement CRUD methods for `DataEntity`, `Field`, `Document`, `DocumentChunk` nodes and their primary relationships.
    *   [ ] Integration tests for Graph DB adapter.
4.  **Vector DB Implementation (Initial - as per `database-integration-design.md`):**
    *   [ ] Implement a concrete adapter for `VectorDBInterface` (e.g., `ChromaDBAdapter` or `FAISSAdapter`).
    *   [ ] Implement methods for adding embeddings and semantic search.
    *   [ ] Integration tests for Vector DB adapter.

### Phase 3: Agent and Orchestration System (5-7 Weeks)
Focus: Develop the intelligent core of the system.

1.  **LLM Orchestrator Agent (Core Logic - as per `llm-orchestrator-agent-design.md`):**
    *   [ ] Implement Agent state management (`AgentState` Pydantic model).
    *   [ ] Develop ReAct (Reason-Act) loop framework.
    *   [ ] Design and implement initial set of LLM prompts for Agent reasoning.
    *   [ ] Implement agent's ability to invoke Code Scanner, Document Scanner (initial broad scans).
    *   [ ] Implement agent's ability to invoke Completeness Evaluator.
    *   [ ] Implement initial strategy for semantic search via VectorDB to resolve gaps.
    *   [ ] Unit tests for Agent logic.
2.  **Completeness Evaluator (Initial Version - as per `completeness-evaluator-design.md`):**
    *   [ ] Implement `RuleEngine` and `GapFactory`.
    *   [ ] Define and implement initial set of completeness rules (e.g., missing descriptions, missing types).
    *   [ ] Implement `evaluate_completeness()` method that queries GraphDB and creates `MetadataGapInfo` objects.
    *   [ ] Functionality to store/update `MetadataGap` nodes in GraphDB.
    *   [ ] Unit tests for Evaluator rules and logic.
3.  **Orchestration Workflow (Initial):**
    *   [ ] Implement the main sequence: Initial Code Scan -> Initial Doc Scan -> Initial Completeness Evaluation.
    *   [ ] Agent loop for processing one type of gap using semantic search.
    *   [ ] Integration tests for the initial orchestration flow.

### Phase 4: Integration, Iterative Improvement & Advanced Features (6-8 Weeks)
Focus: Refine components, enable the full iterative loop, and add advanced capabilities.

1.  **Full Gap Resolution Loop:**
    *   [ ] Enhance Agent's reasoning for choosing between semantic search, targeted code scan, targeted document scan based on gap type and context.
    *   [ ] Implement Agent's ability to invoke targeted scans (Code & Document) with appropriate parameters.
    *   [ ] Implement Agent's logic to process results from targeted scans and update GraphDB.
    *   [ ] Refine re-evaluation by Completeness Evaluator after each resolution attempt.
    *   [ ] Implement Agent's logic for deciding if a gap is resolved, needs more attempts, or requires human input (updating `MetadataGap.status`).
2.  **Advanced Scanning & Extraction:**
    *   [ ] Code Scanner: Add extraction for more relationships (e.g., `REFERENCES_ENTITY`, `TRANSFORMED_FROM`), support for an additional language (optional).
    *   [ ] Document Scanner: Add support for another document format (e.g., basic PDF text extraction), improve extraction of `REFERENCES_CODE_ENTITY` relationships.
3.  **Enhanced Completeness Evaluator:**
    *   [ ] Implement more sophisticated completeness rules (e.g., undocumented entities, orphaned transformations).
    *   [ ] Improve gap prioritization logic.
4.  **Refined Agent Reasoning:**
    *   [ ] Develop more nuanced LLM prompts for agent decision-making and error handling.
    *   [ ] Implement basic history tracking for gap resolution attempts to avoid simple loops.
5.  **Performance & Scalability (Initial Optimizations):**
    *   [ ] Review and optimize critical DB queries.
    *   [ ] Ensure LLM caching is effectively used.
    *   [ ] Consider batching for DB/LLM operations where appropriate.
6.  **Integration tests for the full gap resolution loop.**

### Phase 5: CLI, Testing, and Documentation (4-5 Weeks)
Focus: Make the system usable, robust, and well-documented.

1.  **Command Line Interface (CLI):**
    *   [ ] Develop a functional CLI using `click` for main operations:
        *   `scan --code-path <path> --doc-path <path>` (initiate full extraction).
        *   `query-gaps` (list open gaps).
        *   `get-entity-info <name>` (retrieve info from graph).
    *   [ ] CLI options for configuration (paths, API keys, DB settings, log level).
2.  **Comprehensive Testing (as per `testing-strategy.md`):**
    *   [ ] Expand unit tests to achieve good coverage for all modules.
    *   [ ] Develop more integration tests for component interactions.
    *   [ ] Create and run end-to-end tests with sample code/doc repositories.
    *   [ ] Prepare a small, representative test dataset.
    *   [ ] Set up CI for automated testing (e.g., GitHub Actions).
3.  **User and Developer Documentation:**
    *   [ ] Write User Guide (installation, configuration, running scans, understanding output).
    *   [ ] Write Developer Guide (architecture, module explanations, extending scanners/rules).
    *   [ ] Document `graph-schema.md` in detail.
    *   [ ] Document key prompt template strategies.
    *   [ ] Generate API documentation for core modules (e.g., using Sphinx).
4.  **Packaging & Deployment Considerations:**
    *   [ ] Package the application for distribution (e.g., create `setup.py`/`pyproject.toml` for PyPI).
    *   [ ] (Optional) Create a Dockerfile for containerized deployment.

## Current Tasks (Pre-Implementation Start)
- [x] Update project brief with detailed requirements for agent-driven architecture
- [x] Created system orchestration architecture document (`orchestration-architecture.md`)
- [x] Updated graph schema (`graph-schema.md`) for documents, chunks, and gaps
- [x] Developed comprehensive 5-phase implementation plan (`implementation-plan.md`)
- [x] Completed detailed design for LLM Orchestrator Agent (`llm-orchestrator-agent-design.md`)
- [x] Completed detailed design for Code Metadata Scanner (`code-scanner-design.md`)
- [x] Completed detailed design for Document Scanner (`document-scanner-design.md`)
- [x] Completed detailed design for Completeness Evaluator (`completeness-evaluator-design.md`)
- [x] Completed detailed design for LLM Integration (`llm-integration-design.md`)
- [x] Completed detailed design for Database Integration (`database-integration-design.md`)
- [x] Completed detailed design for Core Data Models (`core-data-models.md`)
- [x] Completed detailed design for Configuration Management (`configuration-management-design.md`)
- [x] Completed detailed design for Logging (`logging-design.md`)
- [x] Completed detailed design for Testing Strategy (`testing-strategy.md`)
The tasks below are now part of the "Technology Validation Plan" above:
- [ ] Finalize selection of specific LLM provider (e.g., OpenAI, Anthropic) and specific model versions for initial implementation.
- [ ] Finalize selection of specific Graph DB (e.g., Neo4j, Memgraph) and Vector DB (e.g., Chroma, FAISS, Weaviate) technologies for initial implementation.

## Notes
- LLM prompts are critical; continuous refinement will be needed.
- The graph structure (nodes, relationships) is central; ensure consistency.
- Balance between LLM-based extraction and deterministic logic.
- Iterative development: each phase should yield a more capable (if not fully featured) system. 