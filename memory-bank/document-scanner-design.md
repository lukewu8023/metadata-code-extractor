# Document Scanner - Design Document

## 1. Overview
The Document Scanner is responsible for processing various types of documentation files (e.g., Markdown, PDF, HTML, Confluence pages if accessible via API) to extract metadata, identify relationships to code entities, and generate content for semantic search. It supports both broad and targeted scanning modes and interacts with an LLM for content understanding, summarization, and metadata extraction.

## 2. Responsibilities
- Scan documentation repositories or specific document files/URLs as directed by the LLM Orchestrator Agent.
- Identify and parse supported document formats (initially Markdown, extensible to PDF, HTML, etc.).
- Extract structured metadata from documents, such as:
    - Document title, authors, creation/modification dates.
    - Document structure (headings, sections, chapters).
    - Explicitly defined data entities, fields, or processes within the documentation.
    - Links or references to code entities, files, or other documents.
- Utilize LLM prompts for:
    - Summarizing document sections or entire documents.
    - Extracting semantic meaning and relationships from text.
    - Identifying potential links between documentation content and code entities (e.g., "This section describes class X").
    - Normalizing extracted information to align with the graph schema.
- Chunk documents into manageable segments for vector embedding and storage in the Vector DB.
- Generate vector embeddings for document chunks.
- Convert extracted structured metadata (e.g., `Document` nodes, `DocumentChunk` nodes, relationships to `DataEntity`) into the format required by the Graph DB.
- Report scan summaries and detailed findings back to the LLM Orchestrator Agent.

## 3. Architecture and Internal Logic

### 3.1. Core Components:
- **`DocumentFetcher`**: Handles retrieving document content from various sources (local file system, URLs, potentially APIs for systems like Confluence).
- **`FormatParser` (Interface/Abstract Class):**
    - Defines a common interface for parsing different document formats.
    - Concrete implementations (e.g., `MarkdownParser`, `PdfParser`, `HtmlParser`).
    - Each implementation will convert the raw document content into a structured or semi-structured representation (e.g., plain text with section markers, HTML DOM-like structure).
- **`ContentChunker`**: Divides the parsed document content into smaller, meaningful chunks suitable for LLM processing and vector embedding. Strategies can include:
    - Structural chunking (by section, paragraph).
    - Fixed-size chunking with overlap.
    - Recursive chunking for hierarchical documents.
- **`MetadataExtractor`**: Uses LLM prompts to extract metadata from document chunks or the whole document:
    - Basic metadata (title, author from text or file properties).
    - Summaries of chunks/sections.
    - Identification of discussed `DataEntity` or `Field` names.
    - Extraction of relationships described in text (e.g., "Data Entity A is derived from Data Entity B").
- **`EmbeddingGenerator`**: Creates vector embeddings for document chunks.
- **`OutputFormatter`**: Transforms extracted metadata and chunks into formats for Graph DB and Vector DB.

### 3.2. Scanning Modes:
- **Broad Scan (`scan_document_repository(source_path_or_url_list)`):**
    1.  Traverse the specified documentation sources (e.g., directory, list of URLs).
    2.  For each document, use `DocumentFetcher` then the appropriate `FormatParser`.
    3.  Apply `ContentChunker` to the parsed content.
    4.  Process chunks and/or full document with `MetadataExtractor` and `EmbeddingGenerator`.
    5.  Collect all results and return a comprehensive scan report.
- **Targeted Scan (`scan_document_targeted(doc_identifier, target_details)`):**
    1.  `doc_identifier` could be a file path, URL, or unique ID.
    2.  `target_details` might specify sections to focus on, keywords, or types of information to extract (e.g., "Find description of 'Order' entity in this document").
    3.  Fetch and parse the specific document.
    4.  Chunking might be focused around relevant sections if identifiable.
    5.  `MetadataExtractor` applies highly specific LLM prompts based on `target_details`.
    6.  Return specific metadata and relevant embeddings.

### 3.3. LLM Interaction:
- **Prompt Templates:** A library of prompt templates for:
    - Summarizing document chunks/sections.
    - Identifying mentions of known `DataEntity` or `Field` names (from Graph DB).
    - Extracting definitions or descriptions of entities/fields found in the text.
    - Determining relationships between documented entities and code entities.
    - Classifying document sections (e.g., "API documentation", "Data model description", "Tutorial").

### 3.4. Extensibility for New Formats/Sources:
- New document formats: Implement a new `FormatParser`.
- New document sources (e.g., Confluence API): Extend `DocumentFetcher`.

## 4. Key Interfaces and Interactions

### 4.1. Called by:
- `LLMOrchestratorAgent`

### 4.2. Calls (Interfaces it uses):
- `LLMIntegration` (for LLM calls, embeddings)
- `GraphDBInterface` (to format data or store)
- `VectorDBInterface` (to format data or store)

### 4.3. Key Public Methods:
- `scan_document_repository(source_details_list: List[DocSourceInfo], config: DocScanConfig) -> DocScanResult`
- `scan_document_targeted(doc_identifier: str, target_details: TargetScanDetails, config: DocScanConfig) -> TargetedDocScanResult`

## 5. Data Structures
- **`DocSourceInfo`**: Information about a document source (e.g., path, URL, type).
- **`DocScanConfig`**: Configuration for a document scan (e.g., formats to include, chunking parameters, LLM preferences).
- **`TargetScanDetails`**: (Can be similar to Code Scanner's) Specifies what to look for.
- **`DocScanResult` / `TargetedDocScanResult`**: Pydantic models for output:
    - List of `Document` nodes created/updated.
    - List of `DocumentChunk` nodes with their content and embeddings.
    - Extracted relationships (e.g., `DOCUMENTS`, `REFERENCES_CODE_ENTITY`).
    - Summary statistics.
- **`ParsedDocument`**: Internal representation of a document after initial parsing, before chunking and LLM extraction.

## 6. Design Considerations & Open Questions
- **Parsing Complex Formats (PDF, HTML):** Robustly extracting clean text and structure from these can be challenging. Consider using specialized libraries (PyMuPDF, BeautifulSoup) within the `FormatParser` implementations.
- **Identifying Links to Code:** How to reliably identify that a piece of text refers to a specific `DataEntity` or `Field` from the codebase? This might involve fuzzy matching, using aliases, or LLM-based disambiguation querying the existing Graph DB entities.
- **Chunking Strategy for Diverse Documents:** Optimal chunking may vary significantly between dense technical PDFs and loosely structured Markdown files.
- **Handling Outdated Documentation:** How to detect or flag documentation that seems to be out of sync with code (potential future feature for Completeness Evaluator).
- **Scalability for Large Document Sets:** Processing thousands of documents.
- **Image and Diagram Processing:** Initially out of scope, but how could diagrams or tables containing metadata be handled in the future (e.g., OCR + LLM vision models)?

## 7. Future Enhancements
- Support for more document formats and sources (e.g., Google Docs, Word documents, specific Wiki APIs).
- Advanced table extraction and interpretation from documents.
- Cross-document link analysis.
- Using LLM to generate questions about documents to verify understanding or identify gaps. 