## NOTE: Partially Superseded Document

**This document (`interface-designs.md`) outlines some earlier, more generic interface ideas. While some conceptual aspects might still be relevant, many of these interfaces have been refined and detailed within the specific component design documents:**

*   `llm-integration-design.md` (for `LLMClient`, prompt management)
*   `database-integration-design.md` (for `GraphDBInterface`, `VectorDBInterface`)
*   `code-scanner-design.md` (for internal scanner interfaces like `LanguageParser`)
*   `document-scanner-design.md` (for internal scanner interfaces like `FormatParser`)

Please refer to those documents for the most current interface designs relevant to each component. This document can be used for historical context or general interface concepts.

---

# Metadata Code Extractor - Interface Designs

## Core Interface Designs

### Parser Interface

```python
class CodeParser:
    """Abstract base class for all language-specific parsers."""
    
    def __init__(self, config: ParserConfig):
        """Initialize parser with configuration."""
        pass
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a file and extract metadata using LLM."""
        raise NotImplementedError
    
    def parse_code(self, code: str, file_name: str = None) -> ParseResult:
        """Parse code string and extract metadata using LLM."""
        raise NotImplementedError
    
    def chunk_code(self, code: str) -> List[CodeChunk]:
        """Split code into manageable chunks for LLM processing."""
        raise NotImplementedError
    
    def extract_metadata(self, parsed_result: ParseResult) -> MetadataResult:
        """Extract structured metadata from parsed result."""
        raise NotImplementedError
    
    def build_symbol_map(self, parse_result: ParseResult) -> SymbolMap:
        """Build symbol map from parse result."""
        raise NotImplementedError


class ParseResult:
    """Container for parsed code results."""
    
    entities: List[Entity]
    fields: List[Field]
    relationships: List[Relationship]
    transformations: List[Transformation]
    symbols: Dict[str, SymbolInfo]
    source_info: SourceInfo
    confidence_score: float
    raw_responses: List[LLMResponse]


class SymbolMap:
    """Symbol map for code navigation and lookup."""
    
    def lookup(self, symbol_name: str) -> List[SymbolInfo]:
        """Look up a symbol by name."""
        pass
    
    def get_symbols_in_range(self, start_line: int, end_line: int) -> List[SymbolInfo]:
        """Get symbols defined in a line range."""
        pass
    
    def get_related_symbols(self, symbol_name: str) -> List[SymbolRelationship]:
        """Get symbols related to the given symbol."""
        pass


class ParserConfig:
    """Configuration for code parser."""
    
    llm_provider: str
    model_name: str
    chunk_size: int
    chunk_overlap: int
    max_tokens: int
    temperature: float
    template_dir: str
    cache_dir: str
    timeout: int
    retries: int
```

### LLM Prompt Template Interface

```python
class PromptTemplate:
    """Template for LLM prompts."""
    
    def __init__(self, template_path: str, template_type: str):
        """Initialize template from file."""
        pass
    
    def render(self, **kwargs) -> str:
        """Render template with parameters."""
        pass
    
    @property
    def template_type(self) -> str:
        """Get template type (entity, field, relationship, etc.)."""
        pass
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        pass
    
    @property
    def required_parameters(self) -> List[str]:
        """Get list of required parameters for rendering."""
        pass


class PromptTemplateManager:
    """Manager for prompt templates."""
    
    def __init__(self, template_dir: str):
        """Initialize manager with template directory."""
        pass
    
    def get_template(self, template_type: str, language: str) -> PromptTemplate:
        """Get template for a specific type and language."""
        pass
    
    def list_templates(self) -> List[TemplateInfo]:
        """List all available templates."""
        pass
    
    def register_template(self, template: PromptTemplate) -> None:
        """Register a new template."""
        pass


class LLMClient:
    """Client for LLM API."""
    
    def __init__(self, provider: str, model: str, config: LLMConfig):
        """Initialize LLM client."""
        pass
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from LLM."""
        pass
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[LLMResponse]:
        """Generate multiple responses in batch."""
        pass


class ResponseParser:
    """Parser for LLM responses."""
    
    def parse_entity_response(self, response: LLMResponse) -> List[Entity]:
        """Parse entity extraction response."""
        pass
    
    def parse_field_response(self, response: LLMResponse) -> List[Field]:
        """Parse field extraction response."""
        pass
    
    def parse_relationship_response(self, response: LLMResponse) -> List[Relationship]:
        """Parse relationship extraction response."""
        pass
    
    def parse_transformation_response(self, response: LLMResponse) -> List[Transformation]:
        """Parse transformation extraction response."""
        pass
```

### Metadata Extraction Interface

```python
class MetadataExtractor:
    """Extracts metadata from code."""
    
    def __init__(self, parser: CodeParser, config: ExtractorConfig):
        """Initialize extractor with parser and configuration."""
        pass
    
    def extract_from_file(self, file_path: str) -> MetadataResult:
        """Extract metadata from a file."""
        pass
    
    def extract_from_directory(self, dir_path: str, file_pattern: str = None) -> MetadataResult:
        """Extract metadata from all matching files in a directory."""
        pass
    
    def extract_focused(self, query: str, context: ExtractionContext = None) -> MetadataResult:
        """Perform focused extraction based on query."""
        pass


class Entity:
    """Represents a data entity (class, table, etc.)."""
    
    name: str
    type: str
    description: str
    file_path: str
    line_start: int
    line_end: int
    parent_entities: List[str]
    properties: Dict[str, Any]
    confidence: float


class Field:
    """Represents a field/attribute of an entity."""
    
    name: str
    entity_name: str
    type: str
    description: str
    default_value: Any
    file_path: str
    line: int
    validations: List[Validation]
    access_modifier: str
    decorators: List[str]
    properties: Dict[str, Any]
    confidence: float


class Relationship:
    """Represents a relationship between entities."""
    
    source_entity: str
    target_entity: str
    type: str
    cardinality: str
    through_field: str
    constraints: List[str]
    properties: Dict[str, Any]
    confidence: float


class Transformation:
    """Represents a data transformation."""
    
    source: str
    target: str
    type: str
    logic: str
    conditions: List[str]
    file_path: str
    line_start: int
    line_end: int
    properties: Dict[str, Any]
    confidence: float


class MetadataResult:
    """Container for extracted metadata."""
    
    entities: List[Entity]
    fields: List[Field]
    relationships: List[Relationship]
    transformations: List[Transformation]
    symbol_map: SymbolMap
    source_files: List[str]
    extraction_stats: ExtractionStats
```

### Graph Output Interface

```python
class GraphOutputAdapter:
    """Adapter for outputting metadata to graph database."""
    
    def __init__(self, connection_config: ConnectionConfig):
        """Initialize adapter with connection configuration."""
        pass
    
    def output_metadata(self, metadata: MetadataResult) -> OutputResult:
        """Output metadata to graph database."""
        pass
    
    def clear_metadata(self, scope: OutputScope = None) -> None:
        """Clear existing metadata from graph database."""
        pass
    
    def query_metadata(self, query: str) -> QueryResult:
        """Query metadata from graph database."""
        pass


class VectorOutputAdapter:
    """Adapter for outputting code chunks to vector database."""
    
    def __init__(self, connection_config: ConnectionConfig):
        """Initialize adapter with connection configuration."""
        pass
    
    def store_chunks(self, chunks: List[CodeChunk]) -> OutputResult:
        """Store code chunks in vector database."""
        pass
    
    def search_similar(self, text: str, limit: int = 10) -> List[SimilarityResult]:
        """Search for similar code chunks."""
        pass
    
    def clear_chunks(self, scope: OutputScope = None) -> None:
        """Clear existing chunks from vector database."""
        pass
```

## Implementation Considerations

### Interface Evolution
- Interfaces should remain stable while implementations evolve
- Use abstract base classes with clear method signatures
- Consider versioning interfaces for backward compatibility

### Error Handling
- All methods should have consistent error handling
- Use custom exception types for different error categories
- Include context information in exceptions

### Asynchronous Support
- Key operations should support async/await pattern
- Batch operations should be optimized for parallel processing
- Consider backpressure mechanisms for large-scale processing

### Configuration Management
- Use dataclasses or Pydantic models for typed configurations
- Support environment variable overrides
- Include validation rules in configuration classes

### Extension Points
- Each interface should define clear extension points
- Use dependency injection for component composition
- Consider plugin architecture for language-specific implementations

## Next Steps

1. Review and refine these interface designs
2. Create detailed class diagrams showing relationships
3. Implement proof-of-concept for critical interfaces
4. Define test interfaces for component validation
5. Document extension mechanisms for future enhancement 