"""
Initialization file for the CLI test fixtures package that makes fixture functions available for import in test modules.

This module re-exports all fixture functions from the cli_fixtures module to simplify imports in test files.
It allows test modules to directly import fixtures from the fixtures package rather than having to 
import from the specific modules that contain them.
"""

from .cli_fixtures import (
    get_basic_command_options,
    get_complex_command_options,
    get_invalid_command_options,
    get_success_response,
    get_error_response,
    get_validation_error,
    get_file_not_found_error,
    get_json_parsing_error,
    get_conversion_success_data,
    load_sample_args
)

# Export all fixtures from cli_fixtures module
__all__ = [
    'get_basic_command_options',
    'get_complex_command_options',
    'get_invalid_command_options',
    'get_success_response',
    'get_error_response',
    'get_validation_error',
    'get_file_not_found_error',
    'get_json_parsing_error',
    'get_conversion_success_data',
    'load_sample_args'
]