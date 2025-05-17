# Tasks - Metadata Code Extractor

## Project Complexity
**Level 3 - Intermediate System**: This project involves multiple interconnected components, complex data processing workflows, integration with external systems (graph and vector databases), and LLM-based semantic extraction.

## Implementation Plan

### Phase 1: Project Setup and Core Structure
1. [ ] Set up Python project structure with appropriate directories
2. [ ] Define package dependencies and create requirements.txt
3. [ ] Set up configuration management system
4. [ ] Create basic CLI interface structure
5. [ ] Implement logging system
6. [ ] Establish test framework and basic tests
7. [ ] Set up LLM API integration framework

### Phase 2: Code Parsing and Symbol Indexing
1. [ ] Implement generic code parser interface
2. [ ] Create Python parser implementation using AST/libCST
3. [ ] Build symbol indexer to map fields/methods/constants to locations
4. [ ] Implement file and line position tracking
5. [ ] Create storage mechanism for symbol index
6. [ ] Add basic parsing tests with test code files

### Phase 3: LLM Prompt Engineering System
1. [ ] Design prompt templates for different extraction tasks
2. [ ] Create context window management system for code chunks
3. [ ] Implement response parsing and validation
4. [ ] Build error handling and retry logic
5. [ ] Design prompt evaluation framework
6. [ ] Create prompt template storage and versioning system
7. [ ] Add tests for LLM prompt system

### Phase 4: Metadata Extraction System
1. [ ] Implement graph schema for DataEntity and Field nodes with relationships
2. [ ] Create code-to-graph element mapper
3. [ ] Implement broad scan extraction logic for Python files
   - [ ] DataEntity identification (classes, tables, data models)
   - [ ] Field extraction with data types and attributes
   - [ ] Validation rule detection
   - [ ] Transformation logic identification
4. [ ] Build LLM-augmented semantic extraction capabilities
5. [ ] Design structured output format for graph database
6. [ ] Create unstructured knowledge chunk formatter
7. [ ] Implement scan report generator
8. [ ] Add tests for metadata extraction

### Phase 5: Semantic Chunking and Vector System
1. [ ] Implement code chunking strategy with ~40 line overlap
2. [ ] Set up vector embedding generation
3. [ ] Create storage interface for vector database
4. [ ] Implement similarity search for semantic lookup
5. [ ] Build integration between symbol index and vector search
6. [ ] Add tests for chunking and vector operations

### Phase 6: Focused Scan Implementation
1. [ ] Create focused extraction interface
2. [ ] Implement target selection heuristic logic
   - [ ] Symbol map exact lookup
   - [ ] Vector similarity search
3. [ ] Build context window determination for focused extraction
4. [ ] Develop targeted extraction strategies for specific metadata types
5. [ ] Create gap detection system
6. [ ] Design specialized LLM prompts for targeted extraction
7. [ ] Implement focused scan mode tests

### Phase 7: Database Integration and Output
1. [ ] Implement graph database output adapter for DataEntity and Field nodes
2. [ ] Create relationships mapping to graph database
3. [ ] Build vector database integration for unstructured chunks
4. [ ] Implement JSON/dict output formatter
5. [ ] Create scan report generator
6. [ ] Add export functionality for standalone operation
7. [ ] Test database integrations

### Phase 8: Data Lineage Tracking
1. [ ] Implement entity-level lineage detection (DERIVED_FROM/FEEDS_INTO)
2. [ ] Build field-level lineage tracking (TRANSFORMED_FROM/TRANSFORMED_INTO)
3. [ ] Create visualization components for lineage graphs
4. [ ] Add lineage queries and reports
5. [ ] Implement LLM-based lineage extraction for complex transformations
6. [ ] Test lineage tracking capabilities

### Phase 9: Integration and System Testing
1. [ ] Integrate all components into complete pipeline
2. [ ] Create comprehensive end-to-end tests
3. [ ] Implement performance optimizations
4. [ ] Add multi-language support (if requirements expand)
5. [ ] Test with large codebases for scalability
6. [ ] Refine based on test results

### Phase 10: Documentation and Packaging
1. [ ] Create comprehensive API documentation
2. [ ] Write user guide with examples
3. [ ] Add inline code documentation
4. [ ] Create example configurations
5. [ ] Document LLM prompt templates and their purposes
6. [ ] Package for distribution
7. [ ] Create deployment guide

## Current Tasks
- [x] Update project brief with detailed requirements
- [x] Develop comprehensive implementation plan
- [x] Define graph schema for metadata storage
- [ ] Set up project structure and environment
- [ ] Begin implementing core parsing system

## Notes
- LLM prompts are required for extracting semantic information from code
- The graph structure requires DataEntity and Field nodes with specific relationships
- Need to balance between static analysis and LLM-based extraction
- Should support both field-level and entity-level lineage tracking
- Chunking strategy (~40 lines with overlap) is specified for vector storage 