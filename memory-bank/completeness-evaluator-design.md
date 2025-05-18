# Completeness Evaluator - Design Document

## 1. Overview
The Completeness Evaluator is responsible for assessing the current state of the extracted metadata in the Graph DB and identifying areas where information is missing, incomplete, or potentially inconsistent. It generates a list of `MetadataGap` nodes, which are then used by the LLM Orchestrator Agent to prioritize and plan resolution tasks.

## 2. Responsibilities
- Define and manage a configurable set of completeness rules and heuristics.
- Query the Graph DB to retrieve metadata for evaluation based on these rules.
- For each `DataEntity`, `Field`, `Document`, `Process`, `APIEndpoint`, etc., check for:
    - Missing essential properties (e.g., description, type, owner).
    - Incomplete or missing relationships (e.g., a `DataEntity` with no `Field`s, a `Field` involved in a transformation but missing `TRANSFORMED_FROM` or `HAS_INPUT_FIELD`/`HAS_OUTPUT_FIELD` links to a `Transformation` node).
    - Lack of corresponding documentation (e.g., a `DataEntity` not `DOCUMENTS` by any `Document` or referenced by any `DocumentChunk`).
    - Potential inconsistencies (e.g., data type mismatch between a field and its documented type, though this might be more advanced).
- Create or update `MetadataGap` nodes in the Graph DB for each identified deficiency.
- Populate `MetadataGap` nodes with details such as type of gap, severity, priority, description, and links to the affected node(s).
- Provide a summary report or a list of identified gaps to the LLM Orchestrator Agent.
- Potentially use LLM prompts for more nuanced gap identification (e.g., "Does this description adequately explain the purpose of this DataEntity?").

## 3. Architecture and Internal Logic

### 3.1. Core Components:
- **`RuleEngine`**: Manages and executes a set of predefined completeness rules.
    - Rules can be data-driven (e.g., stored in a configuration file or in the Graph DB itself).
    - Each rule defines: what to check (e.g., node type, properties), conditions for a gap, gap type, severity, and default priority.
- **`GraphQueryExecutor`**: Executes Cypher queries (or queries for the chosen Graph DB) to fetch data needed by the rules.
- **`GapFactory`**: Responsible for creating and populating `MetadataGap` node instances with consistent information before they are stored in the Graph DB.
- **`LLMHelper` (Optional/Advanced):** Interacts with the LLM for more subjective evaluations (e.g., quality of descriptions, inferring if a relationship *should* exist but doesn't).

### 3.2. Evaluation Process (`evaluate_completeness()`):
1.  **Load Rules:** The `RuleEngine` loads all active completeness rules.
2.  **Iterate Through Rules:** For each rule:
    a.  **Fetch Data:** `RuleEngine` instructs `GraphQueryExecutor` to fetch the relevant nodes/relationships from the Graph DB that the rule applies to (e.g., "all `DataEntity` nodes", "all `Field` nodes of `DataEntity` X").
    b.  **Apply Rule Logic:** For each fetched item, the `RuleEngine` applies the rule's conditions. This might involve checking for the presence of properties, specific values, or existence of certain relationships.
    c.  **(Optional LLM Check):** For certain rules, if initial checks are inconclusive or require semantic understanding, the `LLMHelper` might be invoked (e.g., pass a description to an LLM and ask if it's adequate).
    d.  **Identify Gaps:** If a deficiency is found, the `RuleEngine` uses `GapFactory` to create a `MetadataGap` object.
3.  **Store Gaps:** All newly identified or updated `MetadataGap` objects are persisted to the Graph DB (e.g., via `GraphDBInterface.ensure_gap()`). Ensure existing open gaps for the same issue are updated rather than duplicated.
4.  **Report Gaps:** Return a list of active (open or newly created) `MetadataGap` identifiers or objects to the LLM Orchestrator Agent.

### 3.3. Completeness Rules Examples:
- **Entity Rules:**
    - `DataEntityMissingDescription`: Checks if `DataEntity.description` is null or too short.
    - `DataEntityMissingType`: Checks if `DataEntity.type` is undefined.
    - `DataEntityNoFields`: Checks if a `DataEntity` of type "table" or "class" has no outgoing `HAS_FIELD` relationships.
    - `DataEntityMissingOwnership`: Checks if `DataEntity` has no `OWNED_BY` relationship.
    - `DataEntityNotDocumented`: Checks if a `DataEntity` has no incoming `DOCUMENTS` relationship from a `Document` node or `REFERENCES_CODE_ENTITY` from a `DocumentChunk`.
- **Field Rules:**
    - `FieldMissingDescription`: Checks `Field.description`.
    - `FieldMissingDataType`: Checks `Field.data_type`.
    - `FieldMissingSensitivityForPIIName`: If `Field.name` suggests PII (e.g., "email", "ssn"), check if `Field.sensitivity` is set.
- **Relationship Rules:**
    - `TransformationMissingInputsOrOutputs`: A `Transformation` node must have at least one `HAS_INPUT_FIELD` and one `HAS_OUTPUT_FIELD`.
    - `ProcessActivityCheck`: A `Process` node should ideally have `READS_FROM` and/or `WRITES_TO` relationships.
- **Documentation Rules:**
    - `DocumentChunkLowConfidenceSummary`: If `DocumentChunk.summary` was AI-generated and has low confidence.
    - `DocumentNotLinked`: If a `Document` node doesn't link to any `DataEntity` via `DOCUMENTS` or its chunks via `REFERENCES_CODE_ENTITY`.

### 3.4. Gap Prioritization:
- Initial priority can be set by the rule definition.
- The LLM Orchestrator Agent might further refine priority based on broader context, dependencies, or user-defined goals.

## 4. Key Interfaces and Interactions

### 4.1. Called by:
- `LLMOrchestratorAgent`

### 4.2. Calls (Interfaces it uses):
- `GraphDBInterface` (to query metadata and store/update `MetadataGap` nodes).
- `LLMIntegration` (if LLM-based rule evaluation is implemented).

### 4.3. Key Public Methods:
- `evaluate_completeness(config: EvaluationConfig) -> List[MetadataGap]`
- `get_open_gaps(filter_criteria: GapFilterCriteria = None) -> List[MetadataGap]`

## 5. Data Structures
- **`EvaluationConfig`**: Parameters for the evaluation process (e.g., which rule sets to run, thresholds for certain checks).
- **`CompletenessRule`**: Defines a single rule (ID, name, description, target node type, conditions, gap_type_on_fail, default_severity, default_priority, Cypher query template if needed).
- **`MetadataGap`**: As defined in `graph-schema.md`. The `GapFactory` will ensure these are created correctly.
- **`GapFilterCriteria`**: Used to query specific types or statuses of gaps.

## 6. Design Considerations & Open Questions
- **Rule Definition Language/Format:** How will rules be defined and stored? (e.g., YAML, JSON, or even as special nodes in the Graph DB itself for dynamic rule management).
- **Performance of Evaluation:** Running many rules against a large graph could be slow. Queries need to be optimized. Consider batching or incremental evaluation.
- **Complexity of Rules:** How to balance simple, fast checks with more complex, potentially LLM-driven semantic checks?
- **Avoiding Duplicate Gaps:** Logic to ensure that running the evaluator multiple times doesn't create duplicate `MetadataGap` nodes for the same underlying issue. (e.g., use a composite key for gaps based on the rule and the target node).
- **User-Defined Rules:** How to allow users to easily add custom completeness rules?
- **Contextual Awareness in Rules:** Can rules consider the broader context (e.g., project type, specific tags on nodes) when evaluating?

## 7. Future Enhancements
- More sophisticated inconsistency detection (e.g., conflicting information between code and documentation).
- Trend analysis of metadata completeness over time.
- User interface for managing and defining completeness rules.
- Suggesting new completeness rules based on observed patterns in the metadata. 