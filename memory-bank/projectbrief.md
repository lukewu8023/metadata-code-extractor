# Metadata Code Extractor - Project Brief

## Project Overview
A Python program designed to scan code repositories and associated documentation to extract detailed metadata information. It focuses on data attribute lineage, relationships, and contextual information, employing an LLM-driven, agent-based orchestration for comprehensive and iterative metadata gathering. The system processes source code and documents to identify key entities, their attributes, relationships, and captures both structured metadata and unstructured insights. The extracted metadata is stored in a graph database, and a vector database supports semantic search for an iterative gap-filling process.

## Key Objectives
- Extract comprehensive metadata from both code repositories and documentation through broad initial scanning.
- Provide targeted extraction for specific code or document elements via an agent-driven process.
- Leverage an LLM Orchestrator Agent to manage the extraction workflow, identify metadata gaps, and coordinate completion tasks.
- Utilize a Completeness Evaluator to assess metadata coverage and guide the agent's gap-filling strategies.
- Build and maintain a symbol/semantic index for efficient lookup and context retrieval from code and documents.
- Generate structured metadata for graph database storage, adhering to a defined schema that supports code, documents, and metadata gaps.
- Capture unstructured knowledge chunks (from code and documents) for vector database storage to aid semantic search and gap resolution.
- Track data attribute lineage and relationships, correlating information from both code and documentation.
- Employ LLM prompts for semantic information extraction, reasoning, and decision-making throughout the process.

## Core Components
1.  **LLM Orchestrator Agent:** The central coordinating component that manages the overall workflow, reasons about next steps, and directs other components.
2.  **Code Metadata Scanner:** Processes source files (broad and targeted scans) to extract metadata using LLM-based parsing.
3.  **Document Scanner:** Processes documentation files (e.g., Markdown, PDF) to extract metadata and identify links to code entities.
4.  **Completeness Evaluator:** Assesses the current state of extracted metadata, identifies gaps, and reports them to the agent.
5.  **Graph DB Integration:** Stores structured metadata including entities, fields, relationships, document structures, and identified metadata gaps.
6.  **Vector DB Integration:** Stores embeddings of code snippets, comments, and document chunks for semantic search by the agent.
7.  **Symbol Indexer:** (Potentially integrated within scanners or as a separate utility) Builds lookup maps for code symbols.
8.  **LLM Prompt System:** Manages and utilizes LLM prompts for extraction, reasoning, and evaluation tasks across components.

## Processing Workflow (Agent-Driven)
1.  **Initialization:** Agent starts the process.
2.  **Initial Broad Scans:**
    *   Agent directs Code Metadata Scanner to scan all code; results are stored in Graph DB (structured metadata) and Vector DB (code snippets/comments).
    *   Agent directs Document Scanner to scan all documents; results are stored in Graph DB (document structure, links) and Vector DB (document chunks).
3.  **Completeness Evaluation:** Agent requests Completeness Evaluator to assess the initial metadata and identify gaps.
4.  **Iterative Gap Completion Loop:** For each identified gap:
    *   Agent reasons about the next best action (ReAct: Thought, Action, Observation).
    *   **Action Option 1 (Semantic Search):** If relevant information might exist in already processed content, Agent queries Vector DB for similar code/document snippets. Agent processes results to fill the gap.
    *   **Action Option 2 (Targeted Scan):** If direct inspection is needed, Agent directs Code Scanner (for code) or Document Scanner (for documents) to perform a focused scan on specific files/aspects. Results update databases.
    *   Agent updates Graph DB with any newly inferred or extracted metadata.
    *   Agent requests Completeness Evaluator to re-evaluate.
    *   Agent decides to continue with the current gap, move to the next, or break the loop based on progress.
5.  **Termination:** The process ends when all gaps are filled to a satisfactory level, no further progress can be made, or a predefined limit is reached. Remaining significant gaps are marked for human review.

## Output Types
- Rich graph database containing structured metadata of code entities, fields, documents, their relationships, and tracked metadata gaps.
- Vector database with embeddings of code and document chunks for semantic querying.
- Symbol maps for direct code lookups.
- Scan and completeness reports summarizing findings and unresolved gaps.

## Graph Structure
The metadata is stored in a graph with primary node types including DataEntity, Field, Document, DocumentChunk, and MetadataGap, along with their interrelationships as defined in `graph-schema.md`.

### Data Entity
Represents logical collections of data (tables, datasets, files, etc.)
- **Properties**: name, type, description
- **Relationships**: HAS_FIELD, DERIVED_FROM, FEEDS_INTO, VALIDATED_BY, USED_BY, UPDATED_BY, HAS_SLA, OWNED_BY

### Field
Represents individual data fields/attributes within entities
- **Properties**: name, data_type, nullable, description, sensitivity, source, default_value
- **Relationships**: BELONGS_TO, VALIDATED_BY, TRANSFORMED_FROM, TRANSFORMED_INTO, USED_IN, HAS_SLA

The graph structure supports detailed lineage tracking at both entity and field levels. 