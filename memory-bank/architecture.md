# Metadata Code Extractor - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────┐
│              Code Scanner               │
├─────────────┬───────────────────────────┤
│ Broad Scan  │       Focused Scan        │
└─────┬───────┴─────────────┬─────────────┘
      │                     │
      ▼                     ▼
┌─────────────┐     ┌───────────────────┐
│ Symbol Map  │◄────┤ Target Selection  │
└─────┬───────┘     └─────────┬─────────┘
      │                       │
      │       ┌───────────────┘
      │       │
      ▼       ▼
┌─────────────────────────┐    ┌────────────────────┐
│   Metadata Extraction   │    │ Vector DB Storage  │
└────────────┬────────────┘    └─────────┬──────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐     ┌─────────────────────┐
│  Structured Metadata   │     │ Unstructured Chunks │
└────────────┬───────────┘     └─────────┬───────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐     ┌─────────────────────┐
│    Graph Database      │     │   Vector Database   │
└────────────────────────┘     └─────────────────────┘
```

## Component Breakdown

### 1. Code Scanner
- **Purpose**: Entry point for processing source code files
- **Subcomponents**:
  - **Parser Interface**: Abstract interface for code parsing
  - **Language-specific Parsers**: Implementations for different languages
  - **Comment Extractor**: Pulls out comments and docstrings
  - **Scan Manager**: Coordinates the scanning process

### 2. Symbol Indexer
- **Purpose**: Creates mappings between symbols and their locations
- **Subcomponents**:
  - **Symbol Detector**: Identifies fields, methods, constants
  - **Location Tracker**: Records file and line positions
  - **Index Storage**: Persistent storage for the symbol map
  - **Lookup Service**: Fast retrieval of symbol locations

### 3. Metadata Extractor
- **Purpose**: Analyzes code to identify entities and relationships
- **Subcomponents**:
  - **Entity Recognizer**: Identifies classes, functions, etc.
  - **Attribute Analyzer**: Extracts types, defaults, etc.
  - **Relationship Detector**: Finds connections between entities
  - **Transformation Analyzer**: Identifies data transformations

### 4. Chunking System
- **Purpose**: Breaks code into manageable, overlapping segments
- **Subcomponents**:
  - **Chunker**: Splits code with appropriate overlap
  - **Embedding Generator**: Creates vector representations
  - **Chunk Storage**: Manages persistent storage of chunks

### 5. Target Selection
- **Purpose**: Identifies relevant code sections for focused scanning
- **Subcomponents**:
  - **Heuristic Engine**: Applies selection criteria
  - **Symbol Matcher**: Uses exact matching
  - **Semantic Matcher**: Uses similarity search

### 6. Database Adapters
- **Purpose**: Interfaces with external storage systems
- **Subcomponents**:
  - **Graph DB Client**: Stores structured metadata
  - **Vector DB Client**: Stores unstructured chunks
  - **Local Storage**: For standalone operation

## Data Flow

### Broad Scan Flow
1. Input source code file loaded by Code Scanner
2. Parser creates AST and extracts symbols
3. Symbol Indexer creates symbol map
4. Chunking System creates overlapping segments
5. Metadata Extractor processes each chunk
6. Structured metadata sent to Graph DB
7. Unstructured chunks sent to Vector DB
8. Summary report generated

### Focused Scan Flow
1. Input contains target symbol or query
2. Target Selection identifies relevant code sections
   - Uses Symbol Map for exact matches
   - Uses Vector DB for semantic matches
3. Context windows determined for each match
4. Code Scanner processes each context window
5. Extracted metadata integrated with existing data
6. Gaps and conflicts resolved
7. Updated data stored in databases

## Key Interfaces

### Code Scanner Interface
```python
def scan_broad(file_path: str) -> ScanResult:
    """Process entire file to extract all metadata."""
    pass

def scan_targeted(file_path: str, focus: FocusConfig) -> ScanResult:
    """Process specific parts of a file based on focus criteria."""
    pass
```

### Symbol Index Interface
```python
def build(repo_root: str) -> SymbolMap:
    """Build symbol index for entire repository."""
    pass

def lookup(symbol: str) -> List[Location]:
    """Find all locations where symbol is defined or used."""
    pass
```

### Metadata Output Interface
```python
def output_structured_metadata(metadata: Dict) -> None:
    """Send structured metadata to graph database."""
    pass

def output_unstructured_chunks(chunks: List[TextChunk]) -> None:
    """Send unstructured text chunks to vector database."""
    pass
```

## Design Decisions

1. **Hybrid Static/LLM Approach**: Use static analysis for structure, LLM for semantic understanding
2. **Pluggable Parser Architecture**: Support multiple languages through consistent interface
3. **Two-Tier Storage**: Separate structured (graph) and unstructured (vector) data
4. **Chunking Strategy**: ~40 lines with overlap for optimal context preservation
5. **Metadata Schema**: Consistent entity-relationship model across languages
6. **Standalone Operation**: Support local operation without external databases 