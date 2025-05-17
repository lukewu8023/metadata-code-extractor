# Metadata Code Extractor - Project Brief

## Project Overview
A Python program designed to scan code repositories and extract detailed metadata information, with a focus on data attribute lineage, relationships, and contextual information. The system will process source code to identify key entities, their attributes, relationships, and capture both structured metadata and unstructured insights. The extracted metadata will be stored in a specific graph structure focusing on Data Entities and Fields with their relationships.

## Key Objectives
- Extract comprehensive metadata from code repositories through broad scanning
- Provide targeted extraction for specific elements with a focused scan mode
- Build and maintain a symbol/semantic index for efficient lookup
- Generate structured metadata for graph database storage following the defined graph schema
- Capture unstructured knowledge chunks for vector database storage
- Track data attribute lineage and relationships
- Leverage LLM prompts to extract semantic information from code

## Core Components
1. **Code Scanner** - Processes source files to extract metadata
   - Broad scan mode for comprehensive extraction
   - Focused scan mode for targeted extraction
2. **Symbol Indexer** - Builds lookup maps for fields, methods, and constants
3. **Vector DB Integration** - Stores chunked code and semantic information
4. **Graph DB Integration** - Stores structured metadata relationships
5. **LLM Prompt System** - Uses language models to extract semantic information from code

## Processing Workflow
1. Initial broad scan to build comprehensive metadata and symbol indices
2. Gap identification for targeted follow-up
3. Focused extraction for specific elements using symbol maps and vector similarity
4. LLM-driven extraction for semantic understanding of code
5. Storage of extracted information in appropriate databases

## Output Types
- Structured metadata findings in graph format (Data Entities and Fields)
- Unstructured knowledge chunks (for vector database)
- Symbol maps for exact lookups
- Scan reports summarizing findings

## Graph Structure
The metadata is stored in a graph with two primary node types:

### Data Entity
Represents logical collections of data (tables, datasets, files, etc.)
- **Properties**: name, type, description
- **Relationships**: HAS_FIELD, DERIVED_FROM, FEEDS_INTO, VALIDATED_BY, USED_BY, UPDATED_BY, HAS_SLA, OWNED_BY

### Field
Represents individual data fields/attributes within entities
- **Properties**: name, data_type, nullable, description, sensitivity, source, default_value
- **Relationships**: BELONGS_TO, VALIDATED_BY, TRANSFORMED_FROM, TRANSFORMED_INTO, USED_IN, HAS_SLA

The graph structure supports detailed lineage tracking at both entity and field levels. 