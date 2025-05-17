# System Patterns - Metadata Code Extractor

## Architectural Patterns
- **Pipeline Architecture**: Multi-stage processing (parsing → symbol indexing → metadata extraction → output generation)
- **Plugin Architecture**: Support for multiple language parsers and database integrations
- **Command Pattern**: Different scan modes (broad vs. focused) with common interface
- **Strategy Pattern**: Different extraction strategies based on code type and context
- **Repository Pattern**: For storing and retrieving metadata

## Data Processing Patterns
- **Two-Tier Storage**:
  - Structured metadata → Graph Database
  - Unstructured knowledge → Vector Database
- **Symbol Map**: Fast, exact lookup table for code symbols
- **Semantic Index**: Vector embeddings for similarity search
- **Chunking Strategy**: Overlapping code segments with context preservation
- **Entity-Relationship Model**: For metadata schema design

## Workflow Patterns
- **Broad-then-Focused**: Initial comprehensive scan followed by targeted extraction
- **Gap Detection**: Identifying missing metadata for focused follow-up
- **Target Selection Heuristic**: Using both exact and semantic search to pinpoint relevant code
- **Incremental Processing**: Process only changed files in subsequent runs
- **Dependency-Aware Processing**: Handle files in order of dependencies

## Output Patterns
- **Structured Schema**: Consistent format for graph database nodes and edges
- **Context-Enriched Chunks**: Code segments with relevant metadata for vector storage
- **Summary Reports**: Condensed findings and potential gaps
- **Logging System**: Track processing status and errors 