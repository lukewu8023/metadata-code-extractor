# Configuration Management - Design Document

## 1. Overview
This document describes the design for the configuration management system of the Metadata Code Extractor. The system will handle loading, validating, and providing access to various configuration parameters needed by the application, such as API keys, database connection details, LLM model preferences, and scan paths.

## 2. Responsibilities
- Load configuration from multiple sources with a clear precedence order (e.g., default values, configuration files, environment variables).
- Validate the loaded configuration against predefined schemas (using Pydantic models from `core-data-models.md`).
- Provide a centralized and easily accessible way for different components to retrieve configuration values.
- Support different configuration environments (e.g., development, testing, production) if needed in the future.
- Securely manage sensitive information like API keys (e.g., by prioritizing environment variables or integrating with a secrets manager in more advanced setups).

## 3. Architecture and Internal Logic

### 3.1. Core Components:
- **`ConfigLoader`**: Responsible for reading configuration from various sources.
    - Supports loading from Python files (for defaults), YAML/JSON/TOML files, and environment variables.
    - Merges configurations from these sources, with a defined order of precedence (e.g., Env Vars > Config File > Defaults).
- **`ConfigValidator`**: Uses Pydantic models (specifically, a main `AppConfig` model defined in `core-data-models.md`) to validate the merged configuration. If validation fails, the application should report errors and potentially exit.
- **`ConfigProvider` (Singleton or Global Accessor):**
    - Holds the validated `AppConfig` object.
    - Provides methods for other components to access specific configuration sections or values (e.g., `ConfigProvider.get_llm_settings()`, `ConfigProvider.get_graph_db_config()`).

### 3.2. Configuration Sources and Precedence:
1.  **Default Values:** Hardcoded within the Pydantic models themselves (e.g., `field_name: str = "default_value"`). Lowest precedence.
2.  **Base Configuration File(s):** A default configuration file shipped with the application (e.g., `config.default.yaml`). This can be loaded first.
3.  **User Configuration File(s):** A user-provided configuration file (e.g., `config.yaml` in the project root or a user-specified path). This overrides defaults and the base config.
4.  **Environment Variables:** System environment variables override values from files. A clear mapping scheme will be used (e.g., `MCE_LLM_API_KEY` maps to `app_config.llm.api_key`). Highest precedence.

### 3.3. Loading Process:
1.  On application startup, the `ConfigLoader` is invoked.
2.  It first initializes an `AppConfig` Pydantic model with its internal defaults.
3.  It attempts to load values from a base configuration file (e.g., `config.default.yaml`), updating the `AppConfig` model.
4.  It then attempts to load values from a user-specified configuration file (e.g., `config.yaml`), further updating the `AppConfig` model.
5.  It then scans environment variables, mapping them to corresponding fields in the `AppConfig` model and updating values.
6.  The resulting `AppConfig` object is passed to the `ConfigValidator` (which is implicitly handled by Pydantic during model instantiation and updates if structured correctly).
7.  If validation is successful, the validated `AppConfig` object is made available via the `ConfigProvider`.
8.  If validation fails, Pydantic will raise a `ValidationError`, which should be caught, logged, and result in a graceful application shutdown.

### 3.4. Accessing Configuration:
- A global `config` object or a `get_config()` function can provide access to the validated `AppConfig` instance.
- Example: `from core.config import get_config; app_cfg = get_config(); llm_api_key = app_cfg.llm.providers["openai"].api_key`

### 3.5. Handling Sensitive Data:
- API keys and other secrets should primarily be managed via environment variables or a dedicated secrets management system (future enhancement).
- Configuration files committed to version control should not contain sensitive production secrets. A `.gitignore` entry for user-specific config files (e.g., `config.local.yaml`) should be standard.
- Example files (e.g., `config.example.yaml`) should demonstrate structure but use placeholder values for secrets.

## 4. Key Pydantic Models Involved
- The main model will be `AppConfig` as defined in `core-data-models.md`, which aggregates other specific configuration models like `LLMSettings`, `GraphDBConnectionConfig`, `VectorDBConnectionConfig`, etc.

## 5. File Structure Example for Configuration:
```
metadata_code_extractor/
├── core/
│   ├── config.py         # Manages loading and providing config
│   └── models.py         # Contains AppConfig and other Pydantic models
├── config.default.yaml   # Default application settings (version controlled)
├── config.example.yaml   # Example for user configuration (version controlled)
└── .env.example          # Example for environment variables
```
- Users might create their own `config.yaml` or `.env` file (which would be gitignored).

## 6. Design Considerations & Open Questions
- **Configuration File Format:** YAML is often preferred for its readability for complex structures. TOML or JSON are also options. Python files can also be used for configuration for maximum flexibility but might be less user-friendly for non-developers.
- **Dynamic Reloading:** Initially, configuration will be loaded at startup. Dynamic reloading of configuration without restarting the application is a future consideration if needed.
- **Environment-Specific Configurations:** For more complex deployments, support for environment-specific files (e.g., `config.dev.yaml`, `config.prod.yaml`) could be added, perhaps selected via an environment variable like `APP_ENV`.
- **Validation Strictness:** How strictly to enforce all fields versus allowing some flexibility, especially in nested models.
- **Error Reporting:** Clear error messages when configuration validation fails, indicating which field is problematic.

## 7. Future Enhancements
- Integration with secrets management services (e.g., HashiCorp Vault, AWS Secrets Manager).
- A CLI command to validate a configuration file.
- Schema generation for configuration files (e.g., JSON Schema from Pydantic models).
- Support for more sophisticated merging strategies if deeply nested configurations become common. 