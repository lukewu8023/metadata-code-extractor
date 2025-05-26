"""
Metadata Code Extractor

An intelligent metadata extraction system for code repositories and documentation.
"""

__version__ = "0.1.0"
__author__ = "Metadata Code Extractor Team"
__email__ = "team@metadata-code-extractor.com"

# Package-level imports for convenience
from metadata_code_extractor.core.config import get_config
from metadata_code_extractor.core.logging import setup_logging

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "get_config",
    "setup_logging",
] 