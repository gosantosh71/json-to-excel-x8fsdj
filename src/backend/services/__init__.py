"""
Initializes the services package and exposes the core service classes and utility functions for JSON to Excel conversion.

This module makes the ValidationService and ConversionService classes available to other modules
without requiring them to import from specific service modules.
"""

# Import service classes and utility functions
from .validation_service import ValidationService, create_validation_result, merge_validation_errors
from .conversion_service import ConversionService, create_conversion_summary

# Define what is exposed from this package
__all__ = [
    "ValidationService",
    "ConversionService",
    "create_validation_result",
    "merge_validation_errors",
    "create_conversion_summary"
]