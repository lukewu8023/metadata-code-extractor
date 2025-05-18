# Metadata Code Extractor - Graph Schema

## Graph Data Model

```mermaid
classDiagram
    class DataEntity {
        +String name
        +String type
        +String description
        +String filePath
        +Int lineStart
        +Int lineEnd
        +Float confidence
    }
    
    class Field {
        +String name
        +String type
        +String description
        +String defaultValue
        +String filePath
        +Int line
        +String accessModifier
        +Float confidence
    }
    
    class Validation {
        +String type
        +String rule
        +String description
    }
    
    class Transformation {
        +String type
        +String logic
        +String description
        +Float confidence
    }
    
    class Repository {
        +String name
        +String path
        +String version
    }
    
    class File {
        +String path
        +String language
        +Int lines
        +String hash
    }
    
    Repository "1" -- "*" File : CONTAINS
    File "1" -- "*" DataEntity : DEFINES
    DataEntity "1" -- "*" Field : HAS_FIELD
    DataEntity "1" -- "*" DataEntity : INHERITS_FROM
    DataEntity "1" -- "*" DataEntity : REFERENCES
    Field "1" -- "*" Validation : HAS_VALIDATION
    Field "1" -- "*" Field : TRANSFORMED_FROM
    Field "1" -- "*" Transformation : USES_TRANSFORMATION
```

## Node Types

### DataEntity

Represents a data structure definition such as a class, table, data model, enumeration, etc.

**Properties:**
- `name` (string): Name of the entity
- `type` (string): Type of entity (e.g., "class", "table", "enum", "interface")
- `description` (string): Description or purpose, extracted from comments or context
- `filePath` (string): Path to the file where the entity is defined
- `lineStart` (integer): Starting line number in the source file
- `lineEnd` (integer): Ending line number in the source file
- `language` (string): Programming language of the implementation
- `namespace` (string): Namespace or package containing the entity
- `confidence` (float): Confidence score for the extraction (0.0-1.0)
- `properties` (json): Additional properties as key-value pairs

### Field

Represents a field, attribute, property, or column within a DataEntity.

**Properties:**
- `name` (string): Name of the field
- `type` (string): Data type of the field
- `description` (string): Description or purpose, extracted from comments
- `defaultValue` (string): Default value as a string representation
- `filePath` (string): Path to the file where the field is defined
- `line` (integer): Line number in the source file
- `accessModifier` (string): Access level (e.g., "public", "private", "protected")
- `isNullable` (boolean): Whether the field can be null
- `isPrimaryKey` (boolean): Whether the field is a primary key
- `isUnique` (boolean): Whether the field has a uniqueness constraint
- `decorators` (json array): List of decorators or annotations
- `confidence` (float): Confidence score for the extraction (0.0-1.0)
- `properties` (json): Additional properties as key-value pairs

### Validation

Represents a validation rule or constraint applied to a Field.

**Properties:**
- `type` (string): Type of validation (e.g., "range", "pattern", "length", "required")
- `rule` (string): The validation rule expression
- `description` (string): Human-readable description of the validation
- `errorMessage` (string): Error message associated with validation failure
- `properties` (json): Additional properties as key-value pairs

### Transformation

Represents a data transformation operation applied to Fields.

**Properties:**
- `type` (string): Type of transformation (e.g., "mapping", "calculation", "aggregation")
- `logic` (string): Logic or formula defining the transformation
- `description` (string): Description of the transformation purpose
- `filePath` (string): Path to the file where the transformation is defined
- `lineStart` (integer): Starting line number in the source file
- `lineEnd` (integer): Ending line number in the source file
- `conditions` (json array): Conditions under which the transformation applies
- `confidence` (float): Confidence score for the extraction (0.0-1.0)
- `properties` (json): Additional properties as key-value pairs

### File

Represents a source code file.

**Properties:**
- `path` (string): Path to the file relative to repository root
- `language` (string): Programming language
- `lines` (integer): Number of lines in the file
- `hash` (string): Hash of file contents for change detection
- `lastModified` (timestamp): Last modification timestamp

### Repository

Represents a code repository.

**Properties:**
- `name` (string): Repository name
- `path` (string): Path to repository root
- `version` (string): Version identifier (e.g., commit hash, tag)
- `scanTime` (timestamp): When the repository was scanned

### Document

Represents a documentation file or resource.

**Properties:**
- `path` (string): Path to the document relative to repository root
- `type` (string): Document type (e.g., "markdown", "pdf", "html", "javadoc")
- `title` (string): Document title
- `description` (string): Brief description of document content
- `lastModified` (timestamp): Last modification timestamp
- `tags` (json array): Content tags for categorization
- `scanTime` (timestamp): When the document was scanned

### DocumentChunk

Represents a segment of a document for vector storage and retrieval.

**Properties:**
- `documentPath` (string): Path to the parent document
- `content` (string): The actual text content of the chunk
- `startPosition` (integer): Start position in the document (e.g., line number, character offset)
- `endPosition` (integer): End position in the document
- `summary` (string): AI-generated summary of the chunk
- `tags` (json array): Content tags for the chunk
- `confidence` (float): Confidence score for the extraction/relevance (0.0-1.0)

### MetadataGap

Represents a missing or incomplete piece of metadata identified by the system.

**Properties:**
- `gapId` (string): Unique identifier for the gap
- `type` (string): Type of gap (e.g., "missing_field_description", "incomplete_relationship", "unknown_entity_type", "missing_documentation_link")
- `entityName` (string): Name of the primary DataEntity associated with the gap (if applicable)
- `fieldName` (string): Name of the Field associated with the gap (if applicable)
- `description` (string): Detailed description of the missing information
- `priority` (integer): Priority level for resolution (e.g., 1-High, 2-Medium, 3-Low)
- `status` (string): Current status (e.g., "open", "in_progress_semantic", "in_progress_targeted_code", "in_progress_targeted_doc", "resolved", "requires_human_input", "failed")
- `attemptCount` (integer): Number of automated resolution attempts made
- `lastAttempt` (timestamp): Timestamp of the last resolution attempt
- `resolutionNotes` (string): Notes about resolution attempts or guidance for human intervention
- `suggestedActions` (json array): List of suggested actions (e.g., query VectorDB, scan specific file)

## Relationship Types

### CONTAINS
- **From:** Repository
- **To:** File
- **Properties:** None

### DEFINES
- **From:** File
- **To:** DataEntity
- **Properties:**
  - `definitionType` (string): Type of definition (e.g., "declaration", "implementation")

### HAS_FIELD
- **From:** DataEntity
- **To:** Field
- **Properties:** None

### HAS_VALIDATION
- **From:** Field
- **To:** Validation
- **Properties:**
  - `priority` (integer): Execution priority if applicable

### INHERITS_FROM
- **From:** DataEntity
- **To:** DataEntity
- **Properties:**
  - `inheritanceType` (string): Type of inheritance (e.g., "extends", "implements")

### REFERENCES
- **From:** DataEntity
- **To:** DataEntity
- **Properties:**
  - `referenceType` (string): Type of reference (e.g., "composition", "association", "dependency")
  - `cardinality` (string): Cardinality of the relationship (e.g., "one-to-one", "one-to-many")

### TRANSFORMED_FROM
- **From:** Field
- **To:** Field
- **Properties:**
  - `transformationType` (string): Type of transformation
  - `confidence` (float): Confidence score for the relationship (0.0-1.0)

### USES_TRANSFORMATION
- **From:** Field
- **To:** Transformation
- **Properties:**
  - `order` (integer): Order of application if multiple transformations

### DERIVED_FROM
- **From:** DataEntity
- **To:** DataEntity
- **Properties:**
  - `derivationType` (string): How the entity is derived (e.g., "copy", "subset", "transformation")
  - `confidence` (float): Confidence score for the relationship (0.0-1.0)

### DOCUMENTS
- **From:** Document
- **To:** DataEntity
- **Description:** Links a document to a data entity it describes or references.
- **Properties:**
  - `documentationType` (string): Type of documentation (e.g., "reference_material", "user_guide", "api_spec", "data_dictionary_entry")
  - `confidence` (float): Confidence score for the relationship (0.0-1.0)

### CONTAINS_CHUNK
- **From:** Document
- **To:** DocumentChunk
- **Description:** Links a document to its constituent chunks.
- **Properties:**
  - `position` (integer): Order or position of the chunk within the document sequence.

### REFERENCES_CODE_ENTITY
- **From:** DocumentChunk
- **To:** DataEntity
- **Description:** Links a document chunk to a specific code entity it discusses or exemplifies.
- **Properties:**
  - `referenceType` (string): Type of reference (e.g., "mentions", "explains_details", "provides_example_for")
  - `confidence` (float): Confidence score for the relationship (0.0-1.0)

### REFERENCES_FIELD
- **From:** DocumentChunk
- **To:** Field
- **Description:** Links a document chunk to a specific field it discusses.
- **Properties:**
  - `referenceType` (string): Type of reference (e.g., "defines", "explains_usage", "constraints")
  - `confidence` (float): Confidence score for the relationship (0.0-1.0)

### HAS_GAP
- **From:** DataEntity or Field or Document (or even Repository for global gaps)
- **To:** MetadataGap
- **Description:** Links an element to a metadata gap identified for it.
- **Properties:**
  - `identifiedAt` (timestamp): When the gap was first identified.
  - `gapSeverity` (string): Estimated severity of the gap (e.g., "critical", "major", "minor").

### RESOLVED_BY_CODE
- **From:** MetadataGap
- **To:** DataEntity or Field (or other relevant code-derived node)
- **Description:** Indicates a gap was resolved by information extracted from code.
- **Properties:**
  - `resolutionTimestamp` (timestamp): When the gap was resolved.
  - `resolutionMethod` (string): How it was resolved (e.g., "targeted_code_scan", "agent_inference_from_code").
  - `confidence` (float): Confidence in the resolution.

### RESOLVED_BY_DOCUMENT
- **From:** MetadataGap
- **To:** DocumentChunk (or Document)
- **Description:** Indicates a gap was resolved by information from a document.
- **Properties:**
  - `resolutionTimestamp` (timestamp): When the gap was resolved.
  - `resolutionMethod` (string): How it was resolved (e.g., "semantic_search_doc", "targeted_doc_scan").
  - `confidence` (float): Confidence in the resolution.

## Query Examples

### Find all fields of a specific entity
```cypher
MATCH (e:DataEntity {name: 'User'})-[:HAS_FIELD]->(f:Field)
RETURN f.name, f.type, f.description
```

### Find data lineage for a field
```cypher
MATCH (f:Field {name: 'totalPrice'})-[:TRANSFORMED_FROM*]->(source:Field)
RETURN f.name, source.name, source.entity
```

### Find all entities implementing an interface
```cypher
MATCH (e:DataEntity)-[:INHERITS_FROM]->(interface:DataEntity {name: 'Serializable'})
RETURN e.name, e.type, e.filePath
```

### Find validation rules for a field
```cypher
MATCH (e:DataEntity {name: 'Product'})-[:HAS_FIELD]->(f:Field {name: 'price'})-[:HAS_VALIDATION]->(v:Validation)
RETURN f.name, v.type, v.rule, v.description
```

## Implementation Notes

1. **Node Identifiers**
   - Use composite keys for entities: `{name}_{filePath}`
   - Use composite keys for fields: `{entityName}_{name}_{filePath}`
   - This allows handling of similarly named entities across different files

2. **Confidence Scoring**
   - All LLM-extracted nodes and relationships should include confidence scores
   - Consider confidence threshold filtering in queries
   - Lower confidence items may require manual verification

3. **Property Indexing**
   - Create indexes on frequently queried properties:
     - DataEntity.name
     - Field.name
     - File.path
     - All confidence scores

4. **Graph Database Selection**
   - Primary recommendation: Neo4j (mature, widely used)
   - Alternatives: Amazon Neptune, JanusGraph, ArangoDB
   - Consider cloud-hosted options for easier deployment

5. **Schema Evolution**
   - Design for extensibility to add new node and relationship types
   - Use property-level extensions rather than schema changes when possible
   - Version the schema to track changes over time 