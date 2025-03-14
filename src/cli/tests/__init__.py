"""
Initialization file for the CLI tests package that provides common utilities, fixtures, and 
configuration for all test types.

This file marks the directory as a Python package and centralizes shared test functionality,
making it available to unit, integration, and end-to-end tests.
"""

import os  # v: built-in
import sys  # v: built-in
import tempfile  # v: built-in
import pytest  # v: 7.3.0+
import json  # v: built-in

# Import fixtures from the fixtures module
from .fixtures.cli_fixtures import (
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

# Define constants for test directories
TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CLI_ROOT_DIR = os.path.abspath(os.path.join(TEST_ROOT_DIR, '..', '..'))
TEST_DATA_DIR = os.path.join(TEST_ROOT_DIR, 'fixtures', 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(TEST_ROOT_DIR, 'fixtures', 'expected_output')


def create_temp_json_file(json_data: dict, prefix: str = "test_") -> str:
    """
    Creates a temporary JSON file with the given content for testing.
    
    Args:
        json_data: The dictionary to write as JSON content
        prefix: Prefix for the temporary file name
        
    Returns:
        Path to the created temporary JSON file
    """
    # Create a temporary file with the given prefix
    with tempfile.NamedTemporaryFile(prefix=prefix, suffix=".json", delete=False) as temp_file:
        # Write the JSON data to the file with proper formatting
        temp_file.write(json.dumps(json_data, indent=2).encode('utf-8'))
        return temp_file.name


def cleanup_temp_file(file_path: str) -> bool:
    """
    Removes a temporary file created for testing.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        True if file was successfully removed, False otherwise
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Remove the file if it exists
        os.remove(file_path)
        return True
    return False


def get_test_json_path(filename: str) -> str:
    """
    Returns the path to a sample JSON file in the test data directory.
    
    Args:
        filename: Name of the JSON file
        
    Returns:
        Full path to the requested sample JSON file
    """
    # Construct the full path to the sample JSON file
    file_path = os.path.join(TEST_DATA_DIR, filename)
    
    # Verify the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test JSON file not found: {file_path}")
    
    return file_path


def get_expected_excel_path(filename: str) -> str:
    """
    Returns the path to an expected Excel output file for comparison.
    
    Args:
        filename: Name of the Excel file
        
    Returns:
        Full path to the expected Excel output file
    """
    # Construct the full path to the expected Excel file
    file_path = os.path.join(EXPECTED_OUTPUT_DIR, filename)
    
    # Verify the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Expected Excel file not found: {file_path}")
    
    return file_path


def pytest_configure(config):
    """
    Pytest hook to configure the test environment when pytest loads this package.
    
    Args:
        config: The pytest configuration object
    """
    # Register custom markers for CLI tests
    config.addinivalue_line("markers", "cli_unit: mark a test as a CLI unit test")
    config.addinivalue_line("markers", "cli_integration: mark a test as a CLI integration test")
    config.addinivalue_line("markers", "cli_e2e: mark a test as a CLI end-to-end test")
    
    # Set up any pytest configuration specific to CLI tests
    # Initialize the test environment if needed