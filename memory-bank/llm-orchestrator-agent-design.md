# LLM Orchestrator Agent - Design Document

## 1. Overview
The LLM Orchestrator Agent is the central coordinating component of the Metadata Code Extractor. It manages the end-to-end workflow, from initiating scans to evaluating completeness and orchestrating iterative gap-filling tasks. It uses an LLM for reasoning and decision-making, following a ReAct (Reason + Act) pattern.

## 2. Responsibilities
- Initiate and manage broad scans of code and documentation.
- Receive and interpret scan reports from the Code Metadata Scanner and Document Scanner.
- Interface with the Completeness Evaluator to identify and prioritize metadata gaps.
- Formulate and execute plans to resolve identified gaps, deciding between:
    - Semantic search via the Vector DB.
    - Targeted code scans.
    - Targeted document scans.
- Process information retrieved from various sources (Vector DB, targeted scans) to update the Graph DB.
- Maintain the overall state of the extraction process.
- Track progress, handle errors, and decide when to terminate the process (e.g., all gaps resolved, no further progress, human intervention required).
- Log its decisions, actions, and observations for transparency and debugging.

## 3. Architecture and Internal Logic

### 3.1. Core Agent Loop (ReAct Pattern)
The agent operates in a loop, cycling through phases of reasoning, acting, and observing.

```
Loop:
  1. Reason():
     - Analyze current state (e.g., current phase, available gaps, previous actions' results).
     - Use LLM to generate a 'Thought' about the situation and determine the 'Next Action'.
     - Examples of thoughts:
         - "Initial broad scans are complete. Need to evaluate completeness."
         - "Gap X (missing description for Entity Y) is high priority. Best approach is semantic search in Vector DB."
         - "Semantic search for Gap X yielded no useful results. Next, try targeted scan of File Z, where Entity Y is defined."
         - "Targeted scan of File Z provided a description for Entity Y."
  2. Act():
     - Execute the 'Next Action' determined in the Reason phase.
     - Actions involve calling methods on other components (Scanners, Evaluator, DB interfaces).
     - Examples of actions:
         - `code_scanner.scan_all_code()`
         - `document_scanner.scan_all_documents()`
         - `completeness_evaluator.evaluate_completeness()`
         - `vector_db.semantic_search(query)`
         - `code_scanner.scan_targeted(file_path, entity_name)`
         - `graph_db.update_node(node_id, new_properties)`
  3. Observe():
     - Collect the results/output of the executed 'Action'.
     - Update internal state based on the observation.
     - Examples of observations:
         - "Scan report received."
         - "List of metadata gaps received."
         - "Semantic search returned 3 relevant document chunks."
         - "Targeted scan successful, new metadata extracted."
  4. Update State & Loop/Terminate:
     - Update overall process state (e.g., current workflow phase, resolved gaps).
     - Decide if the process should continue or terminate.
```

### 3.2. State Management
The Agent needs to maintain state, including:
- **`current_phase`**: E.g., `INITIAL_SCANNING`, `GAP_ANALYSIS`, `GAP_RESOLUTION_SEMANTIC`, `GAP_RESOLUTION_TARGETED_CODE`, `GAP_RESOLUTION_TARGETED_DOC`, `FINALIZING`, `TERMINATED`.
- **`repository_context`**: Information about the target repository (path, type).
- **`active_gaps`**: A list of `MetadataGap` objects currently being addressed, possibly prioritized.
- **`current_gap_focus`**: The specific `MetadataGap` being worked on.
- **`attempt_history`**: For each gap, a history of resolution attempts and their outcomes to avoid loops and inform new strategies.
- **`confidence_thresholds`**: Configurable thresholds for deciding if a gap is sufficiently resolved.
- **`max_attempts_per_gap`**: Configurable limit for automated resolution attempts.

### 3.3. LLM Prompts for Reasoning
A suite of prompts will be designed for the Agent's reasoning step:
- **Overall Strategy Prompt:** Given the current phase and high-level status, what's the next major step?
- **Gap Prioritization Prompt:** Given a list of gaps, which one(s) should be addressed next based on type, severity, and potential impact?
- **Gap Resolution Strategy Prompt:** For a specific gap, what is the most promising first/next action (semantic search, targeted code scan, targeted doc scan, or mark for human review)? This prompt will consider the gap type, previous attempts, and available context.
- **Information Synthesis Prompt:** Given snippets from semantic search or targeted scan results, extract the relevant information to fill a specific gap and formulate the update for the Graph DB.

### 3.4. Error Handling and Recovery
- The Agent must handle errors reported by other components.
- Retry mechanisms for transient errors (e.g., LLM API issues, temporary DB unavailability).
- Fallback strategies if a primary action fails (e.g., if semantic search fails to yield results, try a targeted scan).
- If a gap cannot be resolved after multiple attempts, mark it as `requires_human_input` in the Graph DB.

## 4. Key Interfaces and Interactions

### 4.1. Inputs to the Agent:
- Initial configuration (repository path, API keys, DB connection details, thresholds).
- Scan reports from `CodeMetadataScanner` and `DocumentScanner`.
- List of `MetadataGap` objects from `CompletenessEvaluator`.
- Results from `VectorDB.semantic_search()`.
- Results from targeted scans.

### 4.2. Outputs/Actions from the Agent:
- Commands to `CodeMetadataScanner` (e.g., `scan_all_code()`, `scan_targeted(...)`).
- Commands to `DocumentScanner` (e.g., `scan_all_documents()`, `scan_targeted(...)`).
- Commands to `CompletenessEvaluator` (e.g., `evaluate_completeness()`).
- Queries to `VectorDB` (e.g., `semantic_search(query)`).
- Update operations to `GraphDB` (e.g., `add_node()`, `update_relationship()`, `update_gap_status()`).
- Log messages detailing its thought process, actions, and observations.
- Final process status and summary report.

## 5. Data Structures (Internal to Agent or for Interaction)
- **`AgentState`**: Pydantic model to hold the agent's current operational state.
- **`GapResolutionAttempt`**: Stores details of an attempt to resolve a gap (action taken, result, confidence).
- **`PlannedAction`**: Represents an action the agent has decided to take (e.g., target component, method to call, parameters).

## 6. Design Considerations & Open Questions
- **Prompt Chaining for Complex Reasoning:** How to structure prompts if a single reasoning step requires multiple LLM calls?
- **Balancing Exploration vs. Exploitation:** How does the agent decide when to stop trying to resolve a gap and move on?
- **Cost Management:** Strategies to minimize LLM calls (e.g., more deterministic logic for simple decisions, caching reasoning steps if inputs haven't changed significantly).
- **Extensibility:** How easily can new gap types or resolution strategies be added?
- **User Feedback Loop:** How can user feedback on incorrectly resolved gaps be incorporated (future consideration)?
- **State Persistence:** Should the agent's state be persistable to allow for resuming long-running extraction processes? (Initially, likely in-memory for a single run).

## 7. Future Enhancements
- Learning from past interactions to improve gap resolution strategies.
- More sophisticated cost/benefit analysis for choosing actions.
- Parallel execution of independent gap resolution tasks. 