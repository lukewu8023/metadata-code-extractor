# LLM Integration - Design Document

## 1. Overview
The LLM Integration component provides a standardized way for other parts of the system (Agent, Scanners, Evaluator) to interact with Large Language Models. It abstracts the specifics of different LLM providers, manages prompt templates, handles API calls, and facilitates response parsing and caching.

## 2. Responsibilities
- Provide a unified client interface for making calls to various LLM functionalities (e.g., chat completions, text generation, embeddings).
- Support multiple LLM providers (e.g., OpenAI, Anthropic, Azure OpenAI) through an adapter pattern.
- Manage a library of prompt templates, allowing for versioning, loading, and parameter substitution.
- Execute LLM API calls, including handling authentication, rate limiting, and retries for transient errors.
- Parse and validate LLM responses, converting them into structured data objects where applicable.
- Implement a caching mechanism for LLM responses to reduce redundant calls and costs.
- Provide utility functions for common LLM-related tasks, such as token counting or input truncation.
- Centralize configuration for LLM providers, models, and API keys.

## 3. Architecture and Internal Logic

### 3.1. Core Components:
- **`LLMClient` (Interface/Main Class):**
    - The primary entry point for other components to interact with LLMs.
    - Delegates calls to a specific `LLMProviderAdapter` based on configuration.
    - Methods like `get_chat_completion(prompt_messages, model_config)`, `generate_text(prompt, model_config)`, `generate_embeddings(texts, embedding_config)`.
- **`LLMProviderAdapter` (Interface/Abstract Class):**
    - Defines the contract for provider-specific implementations.
    - Concrete classes: `OpenAIAdapter`, `AnthropicAdapter`, `AzureOpenAIAdapter`, etc.
    - Each adapter handles provider-specific API formats, authentication, and error mapping.
- **`PromptManager`**: 
    - Loads prompt templates from a designated location (e.g., files, a database).
    - Allows retrieval of templates by name/ID and version.
    - Provides functionality to substitute parameters into templates.
    - Potentially supports prompt chaining or composition logic.
- **`ResponseParser`**: 
    - Contains methods to parse LLM responses, often expected in JSON or specific textual formats.
    - Validates the structure and content of responses.
    - Converts parsed data into Pydantic models or other well-defined Python objects.
- **`LLMCache` (Interface/Implementation):**
    - Stores LLM requests (or a hash of them) and their corresponding responses.
    - Before making an API call, the `LLMClient` checks the cache.
    - Configurable cache storage (e.g., in-memory, Redis, disk-based).
    - Configurable cache expiration policies.
- **`TokenCounterUtil`**: Utility to estimate token counts for prompts to help manage context window limits.

### 3.2. Workflow for an LLM Call (e.g., Chat Completion):
1.  A system component (e.g., `LLMOrchestratorAgent`) needs an LLM completion.
2.  It calls `LLMClient.get_chat_completion()` with a list of prompt messages (system, user, assistant) and model configuration.
3.  `LLMClient` generates a cache key based on the request.
4.  `LLMClient` checks `LLMCache`:
    a.  If a valid cached response exists, it's returned.
5.  If not cached or cache is stale:
    a.  `LLMClient` selects the configured `LLMProviderAdapter`.
    b.  The adapter formats the request for the specific LLM provider's API.
    c.  The adapter makes the API call, handling authentication, rate limits (with potential delays/retries).
    d.  The adapter receives the raw API response.
    e.  The adapter normalizes provider-specific errors to a common error type.
    f.  The raw response is returned to `LLMClient`.
6.  `LLMClient` stores the raw response in `LLMCache`.
7.  `LLMClient` (or the calling component, TBD) might use `ResponseParser` to convert the raw response (e.g., JSON content within the completion) into a structured object.
8.  The final response (raw or parsed) is returned to the calling component.

### 3.3. Prompt Template Management:
- Templates stored in a structured format (e.g., YAML or JSON files, or a simple directory structure with `.txt` files using a clear naming convention).
- Each template can have placeholders for dynamic values.
- `PromptManager.get_template(name, version).fill(param1=value1, ...)`.

## 4. Key Interfaces and Interactions

### 4.1. Used by:
- `LLMOrchestratorAgent`
- `CodeMetadataScanner`
- `DocumentScanner`
- `CompletenessEvaluator` (potentially)

### 4.2. Calls (External Dependencies):
- External LLM Provider APIs (OpenAI, Anthropic, etc.).
- Cache storage system (if not in-memory).

### 4.3. Key Public Methods (for `LLMClient`):
- `async get_chat_completion(messages: List[ChatMessage], config: ModelConfig) -> LLMResponse`
- `async generate_text(prompt: str, config: ModelConfig) -> LLMResponse` (could be a wrapper around chat completion)
- `async generate_embeddings(texts: List[str], config: EmbeddingConfig) -> List[List[float]]`
- `get_prompt(template_name: str, version: Optional[str] = None) -> PromptTemplate` (via `PromptManager`)

## 5. Data Structures
- **`ChatMessage`**: Pydantic model (role: "system"|"user"|"assistant", content: str).
- **`ModelConfig`**: LLM model parameters (e.g., model_name, temperature, max_tokens, stop_sequences, stream: bool).
- **`EmbeddingConfig`**: Embedding model parameters (e.g., model_name, dimensions).
- **`LLMResponse`**: Raw response from the LLM provider, typically including content, usage statistics, finish reason.
- **`ParsedLLMOutput` (Generic or Specific Pydantic models):** Structured data extracted from LLM responses by `ResponseParser`.
- **`PromptTemplate`**: Represents a loaded prompt template, with methods to fill parameters.
- **`LLMProviderConfig`**: Stores API keys, endpoint URLs for different providers.

## 6. Design Considerations & Open Questions
- **Asynchronous Operations:** All LLM API calls should be asynchronous (`async/await`) to prevent blocking the main application thread.
- **Streaming Support:** For long text generation, streaming responses might be necessary. The interface should accommodate this.
- **Error Handling Granularity:** How to handle different types of LLM errors (API errors, rate limits, content moderation flags, malformed responses from LLM)?
- **Configuration of Providers/Models:** How will users specify which provider and model to use for different tasks? (e.g., a powerful model for reasoning, a cheaper/faster one for summarization, a specific embedding model).
- **Security of API Keys:** Secure storage and access to LLM API keys.
- **Standardization of Parsed Output:** Defining clear Pydantic models for expected outputs from different types of LLM tasks (e.g., `EntityExtractionOutput`, `SummarizationOutput`).
- **Prompt Versioning Strategy:** How to manage changes to prompts and ensure reproducibility?

## 7. Future Enhancements
- Support for fine-tuned models.
- A/B testing framework for prompts.
- More sophisticated rate limiting and backoff strategies (e.g., exponential backoff with jitter).
- Automatic selection of best model based on task complexity and cost constraints.
- Integration with LLM observability/monitoring tools. 