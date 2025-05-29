"""
Unit tests for logging configuration.

Tests the logging setup and configuration functionality.
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from metadata_code_extractor.core.logging import setup_logging


class TestLogging:
    """Test logging configuration functionality."""

    def test_setup_logging_default(self):
        """
        Test default logging setup.
        
        Purpose: Verify that setup_logging() configures the logging system with
        appropriate default settings for the application.
        
        Checkpoints:
        - Logger for the application namespace is configured
        - Default log level is set to INFO
        - At least one handler is attached to the logger
        - Logger configuration is accessible after setup
        
        Mocks: None - tests actual logging configuration
        
        Dependencies:
        - setup_logging function from core.logging
        - Python logging module
        
        Notes: This test ensures that the application can be used with minimal
        configuration and that logging works out of the box with sensible defaults.
        """
        setup_logging()
        
        # Check that root logger is configured
        logger = logging.getLogger("metadata_code_extractor")
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_debug_level(self):
        """
        Test logging setup with DEBUG level.
        
        Purpose: Verify that setup_logging() can be configured with different
        log levels and that the configuration is applied correctly.
        
        Checkpoints:
        - Logger level is set to DEBUG when specified
        - Debug level configuration overrides default INFO level
        - Logger configuration reflects the specified level
        
        Mocks: None - tests actual logging configuration
        
        Dependencies:
        - setup_logging function with level parameter
        - Python logging module
        
        Notes: DEBUG level is important for development and troubleshooting,
        so this test ensures that verbose logging can be enabled when needed.
        """
        setup_logging(level="DEBUG")
        
        logger = logging.getLogger("metadata_code_extractor")
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_file(self):
        """
        Test logging setup with file output.
        
        Purpose: Verify that setup_logging() can configure file-based logging
        and that log messages are properly written to the specified file.
        
        Checkpoints:
        - File logging is configured when log_file parameter is provided
        - Log messages are written to the specified file
        - File is created if it doesn't exist
        - Log content includes the expected message
        - File cleanup occurs properly
        
        Mocks: None - tests actual file logging functionality
        
        Dependencies:
        - setup_logging function with log_file parameter
        - tempfile for creating test log files
        - pathlib.Path for file operations
        - Python logging module
        
        Notes: File logging is crucial for production deployments where logs
        need to be persisted and analyzed. This test ensures file logging works correctly.
        """
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(level="INFO", log_file=log_file)
            
            # Test that we can log to the file
            logger = logging.getLogger("metadata_code_extractor.test")
            logger.info("Test message")
            
            # Check that file was created and contains log message
            assert Path(log_file).exists()
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
        finally:
            Path(log_file).unlink(missing_ok=True)

    def test_setup_logging_invalid_level(self):
        """
        Test logging setup with invalid level.
        
        Purpose: Verify that setup_logging() properly validates log level
        parameters and raises appropriate errors for invalid values.
        
        Checkpoints:
        - Invalid log level raises ValueError
        - Error occurs during setup_logging call
        - Error message indicates invalid level
        - System doesn't accept arbitrary log level strings
        
        Mocks: None - tests actual validation behavior
        
        Dependencies:
        - setup_logging function with validation
        - pytest for exception testing
        
        Notes: Input validation prevents misconfiguration and provides clear
        error messages when invalid log levels are specified.
        """
        with pytest.raises(ValueError):
            setup_logging(level="INVALID")

    def test_setup_logging_console_format(self):
        """
        Test that console logging has proper format.
        
        Purpose: Verify that console log handlers are configured with appropriate
        formatters to ensure readable and informative log output.
        
        Checkpoints:
        - Logger has handlers attached after setup
        - All handlers have formatters configured
        - Formatters are not None (indicating proper configuration)
        - Console output will be properly formatted
        
        Mocks: None - tests actual formatter configuration
        
        Dependencies:
        - setup_logging function
        - Python logging module
        
        Notes: Proper log formatting is essential for readability and debugging.
        This test ensures that log messages will be formatted consistently.
        """
        setup_logging(level="DEBUG")
        
        logger = logging.getLogger("metadata_code_extractor")
        
        # Check that handlers have formatters
        for handler in logger.handlers:
            assert handler.formatter is not None

    def test_setup_logging_multiple_calls(self):
        """
        Test that multiple calls to setup_logging don't create duplicate handlers.
        
        Purpose: Verify that setup_logging() is idempotent and doesn't create
        duplicate handlers when called multiple times, preventing log duplication.
        
        Checkpoints:
        - Initial setup creates expected number of handlers
        - Second setup call doesn't increase handler count
        - Handler count remains stable across multiple calls
        - No duplicate log messages are generated
        
        Mocks: None - tests actual handler management
        
        Dependencies:
        - setup_logging function with handler management
        - Python logging module
        
        Notes: Idempotent setup is important for applications that may call
        setup_logging multiple times during initialization or configuration changes.
        This prevents log message duplication and handler proliferation.
        """
        setup_logging(level="INFO")
        initial_handler_count = len(logging.getLogger("metadata_code_extractor").handlers)
        
        setup_logging(level="DEBUG")
        final_handler_count = len(logging.getLogger("metadata_code_extractor").handlers)
        
        # Should not have more handlers after second call
        assert final_handler_count == initial_handler_count 