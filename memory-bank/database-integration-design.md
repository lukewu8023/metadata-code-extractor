# Database Integration - Design Document

## 1. Overview
This document outlines the design for abstract interfaces to interact with the Graph Database and Vector Database. These interfaces will allow other components of the Metadata Code Extractor to store and retrieve data without being tightly coupled to specific database implementations. This promotes flexibility in choosing or switching database technologies.

## 2. Responsibilities
- Define clear, abstract interfaces for common database operations required by the system.
- For the Graph Database:
    - Support CRUD (Create, Read, Update, Delete) operations for nodes based on `graph-schema.md` (e.g., `DataEntity`, `Field`, `Document`, `MetadataGap`, etc.).
    - Support CRUD operations for relationships between these nodes.
    - Allow execution of complex queries (e.g., Cypher for Neo4j) for data retrieval and analysis.
    - Handle transactions where necessary to ensure data consistency.
- For the Vector Database:
    - Support adding text chunks with their vector embeddings.
    - Support semantic similarity searches based on query vectors.
    - Support updating or deleting vector entries if needed.
    - Handle metadata associated with vector entries (e.g., source document ID, chunk ID).
- Provide a mechanism for configuring and connecting to the chosen database instances.
- Ensure implementations of these interfaces handle database-specific connection management, query language, and error handling.

## 3. Architecture and Internal Logic

### 3.1. Graph Database Interface (`GraphDBInterface` - Abstract Base Class)

**Key Methods:**
- `connect(config: GraphDBConfig)`
- `disconnect()`
- `add_node(label: str, properties: Dict) -> NodeID`
- `get_node(node_id: NodeID) -> Optional[Node]` (or `get_node_by_properties(label: str, properties: Dict) -> Optional[Node]`)
- `update_node(node_id: NodeID, properties: Dict) -> bool`
- `delete_node(node_id: NodeID) -> bool`
- `add_relationship(from_node_id: NodeID, to_node_id: NodeID, label: str, properties: Dict) -> RelationshipID`
- `get_relationship(relationship_id: RelationshipID) -> Optional[Relationship]`
- `update_relationship(relationship_id: RelationshipID, properties: Dict) -> bool`
- `delete_relationship(relationship_id: RelationshipID) -> bool`
- `find_nodes(label: str, query_properties: Dict) -> List[Node]`
- `find_relationships(from_node_label: Optional[str] = None, from_node_properties: Optional[Dict] = None, to_node_label: Optional[str] = None, to_node_properties: Optional[Dict] = None, rel_label: Optional[str] = None, rel_properties: Optional[Dict] = None) -> List[Relationship]`
- `execute_query(query: str, parameters: Optional[Dict] = None) -> QueryResult` (for raw/complex queries)
- `ensure_node(label: str, match_properties: Dict, create_properties: Optional[Dict] = None, update_properties: Optional[Dict] = None) -> NodeID` (useful for create-or-update semantics)
- `ensure_relationship(from_node_id: NodeID, to_node_id: NodeID, label: str, match_properties: Dict, create_properties: Optional[Dict] = None, update_properties: Optional[Dict] = None) -> RelationshipID`

**Concrete Implementations:**
- `Neo4jGraphDBAdapter(GraphDBInterface)`
- Potentially others: `SQLGraphDBAdapter` (using SQLite/Postgres with JSON columns for simpler local dev/testing if full graph capabilities aren't immediately needed for all features).

### 3.2. Vector Database Interface (`VectorDBInterface` - Abstract Base Class)

**Key Methods:**
- `connect(config: VectorDBConfig)`
- `disconnect()`
- `add_embeddings(embeddings: List[VectorEmbeddingItem]) -> List[ItemID]`
    - `VectorEmbeddingItem` would contain the vector, its ID, and associated metadata (e.g., `chunk_id`, `document_path`).
- `semantic_search(query_vector: List[float], top_k: int, filter_metadata: Optional[Dict] = None) -> List[SearchResultItem]`
    - `SearchResultItem` would contain the ID of the found item, its metadata, and a similarity score.
- `get_item_by_id(item_id: ItemID) -> Optional[VectorEmbeddingItem]`
- `delete_items(item_ids: List[ItemID]) -> bool`
- `update_item_metadata(item_id: ItemID, metadata: Dict) -> bool` (if supported by the backend)
- `create_collection_if_not_exists(collection_name: str, vector_size: int, distance_metric: str)`

**Concrete Implementations:**
- `FAISSVectorDBAdapter(VectorDBInterface)` (for local, in-memory use)
- `ChromaDBAdapter(VectorDBInterface)`
- `PineconeVectorDBAdapter(VectorDBInterface)`
- `WeaviateVectorDBAdapter(VectorDBInterface)`

### 3.3. Configuration:
- `GraphDBConfig` and `VectorDBConfig` Pydantic models will store connection details (host, port, credentials, collection names, etc.) specific to each database type and provider.
- These configurations will be part of the main application configuration managed by the `ConfigurationManagement` system.

## 4. Key Interfaces and Interactions

### 4.1. Used by:
- `LLMOrchestratorAgent` (to update gaps, store agent-inferred metadata)
- `CodeMetadataScanner` (to store extracted code metadata and embeddings)
- `DocumentScanner` (to store extracted document metadata and embeddings)
- `CompletenessEvaluator` (to query metadata and store/update `MetadataGap` nodes)

### 4.2. Calls (External Dependencies):
- Chosen Graph Database (e.g., Neo4j instance).
- Chosen Vector Database (e.g., ChromaDB, FAISS library, Pinecone/Weaviate API).

## 5. Data Structures (for interface methods)
- **`NodeID`**, **`RelationshipID`**, **`ItemID`**: Type aliases for string or integer identifiers returned by the databases.
- **`Node`**, **`Relationship`**: Generic representations of graph elements, likely dictionaries or Pydantic models (e.g., `{'id': NodeID, 'labels': List[str], 'properties': Dict}`).
- **`VectorEmbeddingItem`**: `(id: ItemID, vector: List[float], metadata: Dict)`
- **`SearchResultItem`**: `(id: ItemID, score: float, metadata: Dict)`
- **`QueryResult`**: A structure to hold results from raw graph queries (e.g., list of records, where each record is a dictionary).

## 6. Design Considerations & Open Questions
- **Transaction Management (Graph DB):** How explicitly should transactions be managed by the interface vs. handled within adapter implementations for individual operations? For complex sequences of updates (e.g., adding multiple nodes and relationships that must succeed or fail together), an explicit transaction context might be needed.
- **Schema Enforcement/Validation:** Should the interfaces play a role in validating data against `graph-schema.md` before insertion, or is this the responsibility of the calling components?
- **Batch Operations:** Interfaces should support batch operations (e.g., `add_nodes_batch`, `add_relationships_batch`) for performance.
- **Error Handling:** Standardizing error types/exceptions raised by different database adapters (e.g., `ConnectionError`, `QueryError`, `ItemNotFoundError`).
- **Idempotency:** `ensure_node` and `ensure_relationship` methods aim for idempotency. How to best achieve this across different backends?
- **Abstracting Query Languages:** While `execute_query` allows raw queries, how much abstraction should be provided for common query patterns beyond basic CRUD and finders to avoid leaking too much Cypher/SQL into the rest of the application if a non-graph-native DB is used as an alternative for the graph interface?

## 7. Future Enhancements
- Support for more database backends.
- More sophisticated querying capabilities in the abstract interfaces (e.g., graph traversal patterns).
- Built-in support for schema migration management for the Graph DB.
- Connection pooling management within the adapters. 