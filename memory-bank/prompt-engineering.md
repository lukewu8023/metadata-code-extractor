# Metadata Code Extractor - Prompt Engineering Guide

## Prompt Engineering Principles

### 1. Structured Output Format

All prompts should instruct the LLM to return responses in a consistent structured format:

- **JSON**: Most suitable for parsing and validation
- **Clear Schema**: Define expected fields and types
- **Nested Structure**: Support for hierarchical data
- **Error Handling**: Define how to indicate uncertainty

Example structure specification in a prompt:
```
Format your response as valid JSON with this structure:
{
  "entities": [
    {
      "name": "string",
      "type": "string",
      "description": "string",
      "line_start": number,
      "line_end": number
    }
  ],
  "confidence": number
}
```

### 2. Role and Context Setting

Begin prompts with clear role definition and context:

- **Expert Role**: Position the LLM as a code analysis expert
- **Task-Specific Expertise**: Mention specific skills relevant to extraction task
- **Context Awareness**: Specify programming language and extraction goal
- **Input/Output Clarity**: Clearly define what's being provided and what's expected

Example role setting:
```
You are a code analyzer specializing in Python data models. Your task is to identify 
all data entity classes and their attributes from the provided code segment.
```

### 3. Explicit Instructions

Instructions should be:

- **Sequenced**: Provide steps in logical order
- **Specific**: Avoid ambiguity about what to extract
- **Prioritized**: Indicate what information is most important
- **Bounded**: Set clear limits on what to include/exclude

Example instruction pattern:
```
For each class that appears to be a data model:
1. Extract the class name
2. Identify all fields/attributes
3. Determine field types (explicitly declared or inferred)
4. Extract any validation logic
5. Note any inheritance relationships
```

### 4. Example-Based Learning

Include examples to guide extraction format:

- **Input-Output Pairs**: Show code snippet and expected extraction
- **Edge Cases**: Demonstrate handling of complex patterns
- **Format Adherence**: Reinforce structured output requirements
- **Confidence Scoring**: Demonstrate proper use of confidence scores

### 5. Language-Specific Considerations

Tailor prompts for different programming languages:

- **Python**: Focus on class definitions, type hints, docstrings
- **Java/C#**: Emphasize strong typing, annotations/attributes, access modifiers
- **JavaScript/TypeScript**: Handle both class and prototype patterns, type definitions
- **SQL**: Extract table definitions, column constraints, relationships

## Prompt Templates

### Code Chunking Prompts

**Purpose**: Determine optimal chunk boundaries when splitting code files

**Key elements**:
- Instructions to identify logical boundaries (class/function definitions)
- Guidelines for preserving context (imports, parent classes)
- Rules for determining chunk overlap
- Priority list for code elements that shouldn't be split

```
As a code segmentation expert, analyze this code:

{code_sample}

Identify optimal splitting points that:
1. Keep related code together (classes, methods)
2. Preserve necessary context (imports, parent classes)
3. Create segments of approximately {target_size} lines
4. Don't split in the middle of logical blocks

Return JSON with proposed split points and required context for each segment.
```

### Entity Extraction Prompts

**Purpose**: Identify data entity classes, structures, or tables

**Key elements**:
- Focus on structural patterns that indicate data entities
- Guidelines for distinguishing data vs. behavioral classes
- Instructions for extracting metadata and relationships
- Rules for handling inheritance and composition

```
You are analyzing code to extract data entities (classes/structures that primarily 
store data rather than implement behavior).

CODE:
{code_chunk}

TASK:
Identify all data entities with these characteristics:
- Primarily contains fields/properties rather than methods
- Represents a business concept or data structure
- May be annotated with data-related decorators

For each entity, extract:
1. Name and type (class, enum, interface, etc.)
2. Description (from comments or semantics)
3. Line range (start and end line numbers)
4. Parent/implemented classes
5. Any annotations or decorators

Format as JSON with confidence scores for each identified entity.
```

### Field Extraction Prompts

**Purpose**: Extract field definitions with metadata from entities

**Key elements**:
- Detection of field declarations, properties, and attributes
- Type inference for weakly typed languages
- Default value extraction
- Access modifier identification
- Validation rule detection

```
You are analyzing fields/properties within data entities.

CODE:
{code_chunk}

TASK:
For each field or property in the given entity:
1. Extract the field name
2. Determine its type (explicit or implied)
3. Identify any default value
4. Note access modifiers (public, private, etc.)
5. Extract documentation from comments
6. Identify validation rules (from annotations, conditionals, or assertions)
7. Detect any specialized annotations/decorators

Entity context: {entity_name} (lines {start_line}-{end_line})

Format as JSON with confidence scores for each identified field.
```

### Validation Rule Extraction Prompts

**Purpose**: Identify validation constraints on fields

**Key elements**:
- Pattern recognition for common validation approaches
- Framework-specific validation detection
- Inference of implicit validations
- Extraction of validation messages

```
You are analyzing code to extract validation rules for data fields.

CODE:
{code_chunk}

TASK:
Identify all validation rules for fields in entity {entity_name}.
Look for:
1. Validator annotations/decorators (@NotNull, @Size, etc.)
2. Conditional checks that validate field values
3. Custom validation methods
4. Assertions or throwing exceptions for invalid values
5. Regex patterns used for validation

For each validation:
1. Link to the field being validated
2. Identify the validation type (required, range, pattern, etc.)
3. Extract the validation parameters (min/max, pattern, etc.)
4. Note any error messages associated with validation failures

Format as JSON with confidence scores for each validation rule.
```

### Relationship Extraction Prompts

**Purpose**: Detect relationships between entities

**Key elements**:
- Identification of reference fields, foreign keys
- Classification of relationship types
- Cardinality determination
- Direction assessment

```
You are analyzing code to extract relationships between data entities.

CODE:
{code_chunk}

ENTITY CONTEXT:
{entity_list}

TASK:
Identify all relationships between entities:
1. Inheritance relationships (extends, implements)
2. Composition relationships (contains instances of other entities)
3. Association relationships (references other entities)
4. Aggregation relationships (collections of other entities)

For each relationship:
1. Identify source and target entities
2. Determine the relationship type
3. Establish cardinality (one-to-one, one-to-many, etc.)
4. Identify the field/property establishing the relationship
5. Note any constraints or qualifiers on the relationship

Format as JSON with confidence scores for each identified relationship.
```

### Transformation Logic Extraction Prompts

**Purpose**: Detect data transformations between fields/entities

**Key elements**:
- Pattern recognition for data mapping/transformation
- Extraction of transformation formulas
- Identification of source and target fields
- Conditions for transformations

```
You are analyzing code to extract data transformation logic.

CODE:
{code_chunk}

ENTITY CONTEXT:
{entity_list}

TASK:
Identify all data transformations where values from one field/entity are:
1. Mapped to another field/entity
2. Transformed through calculations or functions
3. Aggregated from multiple sources
4. Converted between types

For each transformation:
1. Identify source field(s)/entity
2. Identify target field(s)/entity
3. Extract the transformation logic (formula, function, mapping)
4. Note any conditions controlling the transformation
5. Determine where the transformation occurs (method, constructor, etc.)

Format as JSON with confidence scores for each identified transformation.
```

## Prompt Optimization Techniques

### 1. Progressive Refinement

Use multi-step prompting for complex extractions:

1. **Initial Pass**: Extract high-level entities and structure
2. **Targeted Pass**: Focus on specific details of identified entities
3. **Relationship Pass**: Analyze connections between extracted elements
4. **Verification Pass**: Cross-check and validate extracted information

### 2. Context Management

Optimize the context provided to the LLM:

- **Relevant Imports**: Always include import statements
- **Class Hierarchy**: Include parent class definitions when analyzing subclasses
- **Symbol Resolution**: Provide type definitions for referenced symbols
- **Minimal Non-relevant Code**: Exclude unrelated code sections

### 3. Confidence Scoring Guidance

Train the LLM to properly use confidence scores:

- **Explicit Criteria**: Define what constitutes high vs. low confidence
- **Score Calibration**: Provide examples of different confidence levels
- **Uncertainty Handling**: Instructions for marking uncertain extractions
- **Confidence Thresholds**: Set minimum confidence levels for inclusion

Example confidence guidance:
```
For each extraction, assign a confidence score between 0.0 and 1.0:
- 0.9-1.0: Clear, explicit definition with no ambiguity
- 0.7-0.9: Strong evidence but some aspects may be inferred
- 0.5-0.7: Moderate evidence with significant inference
- 0.3-0.5: Weak evidence, highly speculative
- <0.3: Extremely uncertain, mention but mark as low confidence

If confidence is below 0.5, include a brief explanation of the uncertainty.
```

### 4. Error Recovery Strategies

Design prompts with error handling in mind:

- **Output Validation**: Instruct LLM to verify its output format
- **Fallback Options**: Provide alternatives when primary extraction fails
- **Uncertainty Indication**: Methods to flag uncertain extractions
- **Partial Results**: Accept incomplete extractions rather than none

### 5. Metadata Coverage Map

Ensure all dimensions of metadata are covered:

| Metadata Dimension | Primary Prompt | Secondary Prompt | Verification |
|-------------------|----------------|-------------------|-------------|
| Entity Identification | Entity Extraction | Class Pattern Analysis | Cross-reference with imports |
| Field Detection | Field Extraction | Property Access Analysis | Type consistency check |
| Type Information | Type Extraction | Usage-based Inference | Standard type validation |
| Validation Rules | Validation Extraction | Control Flow Analysis | Test case generation |
| Relationships | Relationship Extraction | Reference Analysis | Bidirectional verification |
| Transformations | Transformation Extraction | Data Flow Analysis | Transformation logic testing |

## Common Challenges and Solutions

### Handling Ambiguity

**Challenge**: Code might have multiple interpretations or unclear patterns.

**Solutions**:
- Use confidence scoring to indicate certainty level
- Extract multiple possible interpretations with probabilities
- Include reasoning behind each extraction decision
- Implement verification prompts to cross-check ambiguous cases

### Context Window Limitations

**Challenge**: LLM context windows may be insufficient for large files/classes.

**Solutions**:
- Develop optimal chunking strategy preserving context
- Create "header" context with critical imports and parent classes
- Implement reference resolution across chunks
- Use separate passes for global vs. local information

### Response Format Adherence

**Challenge**: LLMs may deviate from the requested output format.

**Solutions**:
- Include explicit format validation instructions
- Provide clear examples of expected format
- Use structured prompts with numbered steps
- Implement robust parsing with error correction

### Language/Framework Variation

**Challenge**: Different languages and frameworks use varying patterns.

**Solutions**:
- Create language-specific prompt templates
- Include framework detection in initial analysis
- Build library of framework-specific extraction patterns
- Implement adaptive prompting based on detected technology

## Template Evaluation Framework

When evaluating prompt effectiveness, assess these dimensions:

1. **Correctness**: Accuracy of extracted metadata
2. **Completeness**: Coverage of all relevant elements
3. **Consistency**: Uniform handling of similar patterns
4. **Confidence Accuracy**: Alignment of confidence with actual accuracy
5. **Error Rate**: Frequency of malformed or invalid extractions
6. **Degradation Pattern**: Performance on increasingly complex code
7. **Language Adaptability**: Performance across different programming languages
8. **Token Efficiency**: Minimizing token usage while maintaining quality

## Next Steps for Prompt Engineering

1. **Create Template Library**: Develop and version-control core prompt templates
2. **Language Adaptation**: Customize templates for top priority languages
3. **Test Suite**: Build comprehensive test cases covering edge cases
4. **Validation Framework**: Implement automatic validation of extraction results
5. **Metrics Collection**: Track performance metrics across prompt versions
6. **Continuous Improvement**: Establish refinement cycle based on findings 