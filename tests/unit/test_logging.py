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
        """Test default logging setup."""
        setup_logging()
        
        # Check that root logger is configured
        logger = logging.getLogger("metadata_code_extractor")
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        setup_logging(level="DEBUG")
        
        logger = logging.getLogger("metadata_code_extractor")
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
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
        """Test logging setup with invalid level."""
        with pytest.raises(ValueError):
            setup_logging(level="INVALID")

    def test_setup_logging_console_format(self):
        """Test that console logging has proper format."""
        setup_logging(level="DEBUG")
        
        logger = logging.getLogger("metadata_code_extractor")
        
        # Check that handlers have formatters
        for handler in logger.handlers:
            assert handler.formatter is not None

    def test_setup_logging_multiple_calls(self):
        """Test that multiple calls to setup_logging don't create duplicate handlers."""
        setup_logging(level="INFO")
        initial_handler_count = len(logging.getLogger("metadata_code_extractor").handlers)
        
        setup_logging(level="DEBUG")
        final_handler_count = len(logging.getLogger("metadata_code_extractor").handlers)
        
        # Should not have more handlers after second call
        assert final_handler_count == initial_handler_count 