# Code Metadata Scanner - Design Document

## 1. Overview
The Code Metadata Scanner is responsible for parsing source code files, extracting structured metadata, and identifying elements for semantic understanding. It supports both broad (full repository) and targeted (specific file/entity) scanning modes, interacting with an LLM for complex parsing and metadata extraction tasks. Its findings are used to populate the Graph DB and Vector DB.

## 2. Responsibilities
- Scan entire code repositories or specific files/code sections as directed by the LLM Orchestrator Agent.
- Identify and parse source code files of various supported languages (initially Python, extensible to others).
- Extract structured metadata, including:
    - Data Entities (classes, structs, tables definitions, etc.)
    - Fields (attributes, properties, columns within entities)
    - Relationships between entities (inheritance, composition, references)
    - Transformations (how data is manipulated or derived)
    - Validation rules associated with entities or fields.
- Utilize LLM prompts for:
    - Parsing code constructs where static analysis is insufficient or too complex.
    - Extracting semantic information (e.g., descriptions from comments, inferring intent).
    - Normalizing extracted information to align with the graph schema.
- Generate vector embeddings for code snippets, comments, and docstrings for storage in the Vector DB.
- Convert extracted structured metadata into the format required by the Graph DB (`graph-schema.md`).
- Report scan summaries and detailed findings back to the LLM Orchestrator Agent.
- Handle language-specific parsing nuances through configurable strategies or plugins.

## 3. Architecture and Internal Logic

### 3.1. Core Components:
- **`FileProcessor`**: Handles reading files, identifying language, and potentially basic pre-processing (e.g., stripping comments for certain types of static analysis if used as a preliminary step).
- **`LanguageParser` (Interface/Abstract Class):**
    - Defines a common interface for parsing different languages.
    - Concrete implementations (e.g., `PythonParser`, `SQLParser`) will handle language-specifics.
    - Each implementation will use a combination of: 
        - (Optional) Static analysis tools/libraries (e.g., AST for Python) for initial structural understanding.
        - LLM-based parsing for complex constructs, semantic extraction, and robust handling of unfamiliar patterns.
- **`MetadataExtractor`**: Orchestrates the extraction process using the appropriate `LanguageParser`. It takes parsed code (or chunks of it) and applies a series of LLM prompts to extract specific metadata types (entities, fields, relationships, etc.) according to `graph-schema.md`.
- **`EmbeddingGenerator`**: Uses an embedding model (via LLM Integration) to create vector representations of code chunks, comments, or other relevant text.
- **`OutputFormatter`**: Transforms the extracted metadata into formats suitable for the Graph DB and Vector DB.

### 3.2. Scanning Modes:
- **Broad Scan (`scan_repository(repo_path)`):**
    1.  Traverse the repository, identifying all relevant source code files based on extensions or configuration.
    2.  For each file, invoke the `FileProcessor` and then the appropriate `LanguageParser`.
    3.  The `LanguageParser` and `MetadataExtractor` work together to extract all relevant metadata.
    4.  Collect all extracted metadata and embeddings.
    5.  Return a comprehensive scan report and structured data.
- **Targeted Scan (`scan_targeted(file_path, target_details)`):**
    1.  `target_details` can specify entities, functions, line ranges, or metadata aspects to focus on.
    2.  Load the specific file using `FileProcessor`.
    3.  The `LanguageParser` focuses its efforts on the specified targets, possibly by sending only relevant code chunks to the LLM or by tailoring prompts for specific information.
    4.  `MetadataExtractor` applies prompts specifically designed to extract the requested `target_details`.
    5.  Return the specific metadata found and any relevant embeddings.

### 3.3. LLM Interaction:
- **Chunking Strategy:** For large files or for LLM-based parsing, code will be intelligently chunked (e.g., by class, function, or fixed-size blocks with overlap) to fit within LLM context windows while preserving necessary context (imports, class definitions).
- **Prompt Templates:** A library of prompt templates will be maintained for:
    - Identifying Data Entities.
    - Extracting Fields and their properties (type, nullability, description from comments).
    - Detecting Relationships (e.g., "Does Class A use Class B? How?").
    - Parsing transformation logic described in code.
    - Extracting validation rules from annotations or code constructs.
- **Contextual Information:** Prompts will include relevant contextual information (e.g., file path, language, surrounding code, already identified entities) to improve LLM accuracy.

### 3.4. Extensibility for New Languages:
- New languages can be supported by:
    1.  Implementing a new `LanguageParser` for that language.
    2.  Developing language-specific LLM prompt templates.
    3.  (If applicable) Integrating any language-specific static analysis tools.

## 4. Key Interfaces and Interactions

### 4.1. Called by:
- `LLMOrchestratorAgent`

### 4.2. Calls (Interfaces it uses):
- `LLMIntegration` (for LLM calls, embeddings)
- `GraphDBInterface` (to format data for, or directly store in, Graph DB – TBD if direct storage happens here or if it just returns formatted data to Agent)
- `VectorDBInterface` (similarly, for Vector DB)

### 4.3. Key Public Methods:
- `scan_repository(repo_path: str, config: ScanConfig) -> ScanResult`
- `scan_targeted(file_path: str, target_details: TargetScanDetails, config: ScanConfig) -> TargetedScanResult`

## 5. Data Structures
- **`ScanConfig`**: Configuration for a scan (e.g., languages to include/exclude, LLM model preferences, chunking parameters).
- **`TargetScanDetails`**: Specifies what to look for in a targeted scan (e.g., entity name, type of metadata, line numbers).
- **`ScanResult` / `TargetedScanResult`**: Pydantic models to structure the output, containing:
    - List of extracted `DataEntity` objects (with nested `Field`, `Validation`, `Transformation` info).
    - List of `Relationship` objects (between entities/fields).
    - List of code snippets/comments and their `VectorEmbedding` data.
    - Summary statistics (files scanned, entities found, errors encountered).
- **Internal representations** for parsed code elements before they are converted to the final graph schema.

## 6. Design Considerations & Open Questions
- **Balance between Static Analysis and LLM:** For which languages and constructs is static analysis a reliable first pass? How to seamlessly combine it with LLM for deeper understanding?
- **Chunking Effectiveness:** Optimizing chunking to provide sufficient context without excessive overlap or too many LLM calls.
- **Prompt Robustness:** Ensuring prompts are robust against various coding styles and complexities.
- **Error Handling for Parsing:** How to handle files that are partially unparseable or contain syntax errors?
- **State Management during Scans:** For very large repositories, how to manage intermediate state if the scan is long-running (initially, assume scans complete in a single, albeit potentially long, operation).
- **Mapping to Graph Schema:** Ensuring consistent and accurate mapping of diverse code constructs to the canonical `graph-schema.md`.
- **Confidence Scoring:** How to assign confidence scores to LLM-extracted metadata from code?

## 7. Future Enhancements
- Support for incremental scanning (only process changed files).
- More sophisticated pre-processing using tree-sitter or other advanced parsers before LLM interaction.
- Automated discovery and suggestion of new prompt templates for unhandled patterns. 