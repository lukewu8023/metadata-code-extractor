## NOTE: Potentially Conflicting / Partially Superseded Document

**This document (`metadata_schema.md`) outlines an early, broad conceptual schema. While some entity type names overlap with the primary graph schema, the detailed attributes, relationships, and particularly the "Supporting Entity Types" and "Example JSON Output" may differ from the more focused and current schema defined in `memory-bank/graph-schema.md`.**

**The primary reference for the graph database structure to be implemented should be `memory-bank/graph-schema.md`.**

This document (`metadata_schema.md`) can be used for:
*   Historical context on schema brainstorming.
*   Ideas for potential future extensions if the system incorporates more traditional static analysis outputs.

However, for the current agent-driven, LLM-centric implementation, direct reliance on all details herein might lead to inconsistencies with `graph-schema.md` and the Pydantic models in `core-data-models.md` which are designed to map to `graph-schema.md`.

---

# Metadata Schema - Code Extractor

## Primary Entity Types

### 1. DataEntity
Represents a logical collection of data (table, dataset, file, etc.)

**Attributes:**
- `name`: Name of the data entity (e.g., "Orders", "Invoice")
- `type`: Type of data entity (e.g., "table", "file", "topic", "view")
- `description`: Description of what data it contains
- `source_file`: Source code file where this entity is defined
- `line_position`: Line number in source file

### 2. Field
Represents an individual field/attribute within a data entity.

**Attributes:**
- `name`: Field name (e.g., "order_id", "amount", "status")
- `data_type`: Data type (e.g., "INT", "VARCHAR(100)", "Decimal")
- `nullable`: Whether the field can be null
- `description`: Description of the field's meaning
- `sensitivity`: Classification such as "PII", "Sensitive", "Confidential"
- `source`: Original system or source if applicable
- `default_value`: Default value if any
- `source_file`: Source code file where this field is defined
- `line_position`: Line number in source file

### 3. ValidationRule
Represents a validation rule applied to a Data Entity or Field.

**Attributes:**
- `rule_type`: Type of validation (e.g., "not null", "length", "range")
- `parameters`: Parameters of the validation rule
- `description`: Description of the validation rule

### 4. Transformation
Represents a transformation applied to Field(s).

**Attributes:**
- `transformation_type`: Type of transformation
- `logic`: Description or code snippet of the transformation logic
- `source_fields`: Fields used in the transformation
- `target_fields`: Fields produced by the transformation

### 5. Process
Represents a process or job that transforms data.

**Attributes:**
- `name`: Process name
- `description`: Description of the process
- `source_file`: Source code file where this process is defined
- `schedule`: Execution schedule if applicable

### 6. CodeChunk
Represents an unstructured chunk of code with context for vector storage.

**Attributes:**
- `content`: Code content
- `start_line`: Starting line number
- `end_line`: Ending line number
- `symbols`: Symbols contained in the chunk
- `summary`: Summary of the chunk's purpose

## Supporting Entity Types

### 7. FileEntity
Represents a source code file.

**Attributes:**
- `path`: Full path to the file
- `name`: File name
- `extension`: File extension
- `language`: Programming language
- `size`: File size in bytes
- `last_modified`: Last modification timestamp

### 8. ModuleEntity
Represents a module or package.

**Attributes:**
- `name`: Module name
- `description`: Description from module docstring
- `imports`: List of imported modules

### 9. ClassEntity
Represents a class or similar structure.

**Attributes:**
- `name`: Class name
- `superclasses`: List of parent classes
- `description`: Description from class docstring
- `decorators`: Applied decorators

### 10. FunctionEntity
Represents a function or method.

**Attributes:**
- `name`: Function name
- `parameters`: List of parameters with types
- `return_type`: Return type
- `description`: Description from function docstring
- `decorators`: Applied decorators
- `is_method`: Boolean indicating if it's a class method

## Relationships

### Primary Relationships (Graph Schema)

#### 1. HAS_FIELD
- DataEntity HAS_FIELD Field (outgoing from DataEntity)

#### 2. BELONGS_TO / IN_ENTITY
- Field BELONGS_TO DataEntity (outgoing from Field)

#### 3. DERIVED_FROM / FEEDS_INTO
- DataEntity DERIVED_FROM DataEntity (lineage between entities)
- DataEntity FEEDS_INTO DataEntity (reverse lineage)

#### 4. VALIDATED_BY
- DataEntity VALIDATED_BY ValidationRule
- Field VALIDATED_BY ValidationRule

#### 5. TRANSFORMED_FROM / TRANSFORMED_INTO
- Field TRANSFORMED_FROM Field (field-level lineage)
- Field TRANSFORMED_INTO Field (reverse field-level lineage)

#### 6. USED_BY / UPDATED_BY
- DataEntity USED_BY Process (read relationship)
- DataEntity UPDATED_BY Process (write relationship)

#### 7. USED_IN
- Field USED_IN Process (field is used in a process)

#### 8. INPUT_TO / OUTPUT_FROM
- Field INPUT_TO Transformation
- Field OUTPUT_FROM Transformation

### Supporting Relationships

#### 9. CONTAINS
- FileEntity CONTAINS ModuleEntity
- ModuleEntity CONTAINS ClassEntity
- ClassEntity CONTAINS FunctionEntity
- ClassEntity CONTAINS Field
- FunctionEntity CONTAINS Field (local variables)

#### 10. INHERITS_FROM
- ClassEntity INHERITS_FROM ClassEntity

#### 11. CALLS
- FunctionEntity CALLS FunctionEntity

#### 12. REFERENCES
- FunctionEntity REFERENCES Field

#### 13. IMPORTS
- ModuleEntity IMPORTS ModuleEntity

#### 14. DOCUMENTED_BY
- Any entity DOCUMENTED_BY CodeChunk

## Example JSON Output for Graph Database

```json
{
  "nodes": [
    {
      "id": "de1",
      "type": "DataEntity",
      "properties": {
        "name": "Customer",
        "type": "table",
        "description": "Stores customer information",
        "source_file": "models/customer.py",
        "line_position": 10
      }
    },
    {
      "id": "f1",
      "type": "Field",
      "properties": {
        "name": "customer_id",
        "data_type": "String",
        "nullable": false,
        "description": "Unique identifier for the customer",
        "sensitivity": "PII",
        "default_value": null,
        "source_file": "models/customer.py",
        "line_position": 15
      }
    },
    {
      "id": "vr1",
      "type": "ValidationRule",
      "properties": {
        "rule_type": "not_null",
        "parameters": {},
        "description": "Customer ID cannot be null"
      }
    }
  ],
  "relationships": [
    {
      "source": "de1",
      "target": "f1",
      "type": "HAS_FIELD"
    },
    {
      "source": "f1",
      "target": "vr1",
      "type": "VALIDATED_BY"
    }
  ]
}
```

## Vector Storage Schema

For unstructured knowledge chunks:

```json
{
  "content": "def calculate_total(order):\n    # Sum all line items and apply discount\n    subtotal = sum(item.price * item.quantity for item in order.items)\n    if order.has_discount:\n        return subtotal * (1 - order.discount_rate)\n    return subtotal",
  "metadata": {
    "file": "services/order_service.py",
    "line_start": 45,
    "line_end": 51,
    "symbols": ["calculate_total", "subtotal", "order.items", "order.has_discount", "order.discount_rate"],
    "summary": "Calculates order total by summing line items and applying any available discount"
  },
  "embedding": [0.1, 0.2, 0.3, ...] // Vector representation
}
```

## Notes on Schema Evolution

This schema provides a starting point but should be extended as needed:

1. Alignment with specified graph structure requirements is a priority
2. Supporting entity types help map from code elements to graph elements
3. Enhanced relationship tracking for lineage at both entity and field levels
4. Additional properties may be added based on code analysis capabilities