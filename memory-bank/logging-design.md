# Logging - Design Document

## 1. Overview
This document outlines the design for the logging system within the Metadata Code Extractor. A consistent and configurable logging approach is crucial for debugging, monitoring application behavior, and tracking the progress of metadata extraction tasks.

## 2. Responsibilities
- Provide a standardized way for all components to log messages.
- Support different log levels (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Allow configuration of log output formats (e.g., plain text, JSON).
- Enable routing of log messages to various destinations (e.g., console, file, remote logging service).
- Allow per-module log level configuration for fine-grained debugging.
- Ensure log messages are structured and contain relevant contextual information (e.g., timestamp, module name, component ID, current task).

## 3. Architecture and Internal Logic

### 3.1. Core Technology:
- The standard Python `logging` module will be used as the foundation.

### 3.2. Configuration:
- **Setup Function:** A dedicated function (e.g., `setup_logging(config: AppConfig)`) will be called at application startup to configure the root logger and any specific handlers or formatters based on the `AppConfig`.
- **Configuration Parameters (within `AppConfig`):
    - `log_level`: Global minimum log level (e.g., "INFO", "DEBUG").
    - `log_format`: Predefined format names ("simple", "detailed", "json") or a custom format string.
    - `log_to_console`: Boolean, whether to log to `stdout`/`stderr`.
    - `log_to_file`: Boolean, whether to log to a file.
    - `log_file_path`: Path to the log file if `log_to_file` is true.
    - `log_file_rotation`: Configuration for log file rotation (e.g., max size, backup count) using `RotatingFileHandler` or `TimedRotatingFileHandler`.
    - `module_log_levels`: A dictionary to set specific log levels for different modules (e.g., `{"scanners.code_scanner": "DEBUG", "llm.client": "INFO"}`).

### 3.3. Log Formatters:
- **Simple Formatter:** `%(asctime)s - %(levelname)s - %(name)s - %(message)s`
- **Detailed Formatter:** `%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(lineno)d - %(funcName)s - %(message)s`
- **JSON Formatter:** A custom formatter (or a library like `python-json-logger`) to output logs as structured JSON objects, including standard fields and any custom fields passed via `extra`.
    ```json
    {
        "timestamp": "2023-10-27T10:30:00.123Z",
        "level": "INFO",
        "logger_name": "agent.orchestrator",
        "module": "llm_orchestrator_agent",
        "function": "process_gap",
        "message": "Attempting to resolve gap GAP_ID_123",
        "gap_id": "GAP_ID_123",
        "current_phase": "GAP_RESOLUTION_SEMANTIC"
    }
    ```

### 3.4. Log Handlers:
- **Console Handler (`StreamHandler`):** For outputting logs to `stdout` or `stderr`.
- **File Handler (`RotatingFileHandler` or `TimedRotatingFileHandler`):** For writing logs to files with rotation capabilities.
- **Future:** Potentially handlers for remote logging services (e.g., `SysLogHandler`, custom handlers for services like Datadog, Sentry, ELK stack).

### 3.5. Usage in Components:
- Each Python module/class will obtain a logger instance using `logger = logging.getLogger(__name__)`.
- Messages will be logged using standard methods: `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`, `logger.critical()`.
- For structured logging (especially with JSON output), contextual information can be passed via the `extra` keyword argument: `logger.info("Processing entity", extra={"entity_name": "Order", "file_path": "models/order.py"})`.

## 4. Key Pydantic Models Involved
- `AppConfig.log_level`, and potentially a nested `LogConfig` model within `AppConfig` to group all logging-related settings (as described in section 3.2).

## 5. Example Logging Setup (Conceptual in `core/logging_setup.py`):

```python
import logging
import logging.config
# from core.config import AppConfig # Assuming AppConfig is defined

def setup_logging(log_level_str: str = "INFO", log_format_str: str = "simple", log_to_console: bool = True, log_file_path: Optional[str] = None):
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level_str}")

    # Define formatters
    formats = {
        "simple": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        "detailed": "%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(lineno)d - %(funcName)s - %(message)s",
        # JSON formatter would be more complex or use a library
    }
    formatter_config = formats.get(log_format_str, formats["simple"])

    handlers = {}
    if log_to_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "standard_formatter",
            "level": numeric_level,
        }
    
    if log_file_path:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard_formatter",
            "level": numeric_level,
            "filename": log_file_path,
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 3,
        }

    logging_config_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard_formatter": {"format": formatter_config}
        },
        "handlers": handlers,
        "root": {
            "handlers": list(handlers.keys()),
            "level": numeric_level,
        },
        # "loggers": { # For per-module levels if needed
        #     "scanners": {"level": "DEBUG"}
        # }
    }
    logging.config.dictConfig(logging_config_dict)

    # Example: Call this at app startup
    # config = get_app_config() 
    # setup_logging(config.logging.log_level, config.logging.log_format, ...)
```

## 6. Design Considerations & Open Questions
- **Performance Impact:** Excessive DEBUG logging or complex formatting can impact performance. JSON logging can be slightly more overhead than plain text.
- **Log Redaction:** For sensitive data that might appear in logs (even if by accident), a mechanism for redaction might be needed in high-security environments (future).
- **Correlation IDs:** For tracking a single operation or request across multiple components and log messages, a correlation ID (e.g., a unique ID for each gap resolution attempt) should be included in log messages.
- **Standard Log Fields:** Define a set of standard fields to include in structured logs (e.g., `trace_id`, `span_id` if distributed tracing is ever considered).
- **Third-Party Library Logging:** How to control and integrate logging from third-party libraries (e.g., LLM provider client libraries, database drivers)? Usually, their loggers can be configured via the standard `logging` module as well.

## 7. Future Enhancements
- Integration with remote logging aggregation platforms (ELK, Datadog, Sentry).
- Asynchronous logging handlers to minimize I/O blocking in performance-critical paths.
- A central logging context manager to automatically inject contextual information (like `gap_id` or `current_task_id`) into all logs within a specific block of code.
- More sophisticated log analysis and alerting capabilities if the application is deployed as a long-running service. 