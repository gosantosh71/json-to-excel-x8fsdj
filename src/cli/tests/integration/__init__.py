"""
Initialization file for the CLI integration tests package that provides common imports, constants, and 
utility functions specific to integration testing of the JSON to Excel Conversion Tool's command-line interface.
This file serves as a central point for integration test configuration and shared resources.
"""

import os  # v: built-in
import pytest  # v: 7.3.0+
import tempfile  # v: built-in

# Import fixtures and utilities from parent modules
from ..fixtures.cli_fixtures import (
    get_basic_command_options,
    get_complex_command_options,
    get_conversion_success_data,
    get_file_not_found_error,
    get_json_parsing_error
)
from ..__init__ import (
    TEST_ROOT_DIR,
    create_temp_json_file,
    cleanup_temp_file
)

# Define integration test specific constants
INTEGRATION_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DATA_DIR = os.path.join(INTEGRATION_TESTS_DIR, 'mock_data')

def setup_integration_test_environment():
    """
    Sets up the environment for CLI integration tests, ensuring necessary
    directories and resources are available.
    """
    # Ensure the mock data directory exists
    os.makedirs(MOCK_DATA_DIR, exist_ok=True)
    
    # Set up any environment variables needed for integration tests
    # (None required by default for the core functionality)
    
    # Initialize any shared resources for integration tests
    # No additional initialization required for basic tests

def create_mock_backend_response(response_data, success=True):
    """
    Creates a standardized mock response for backend service calls during
    integration testing.
    
    Args:
        response_data (dict): The data to include in the response
        success (bool): Whether the response represents a successful operation
        
    Returns:
        dict: A mock response dictionary that simulates backend service responses
    """
    # Create a base response structure with status field
    response = {
        "status": "success" if success else "error",
        "data": response_data,
        "metadata": {
            "timestamp": "2023-05-20T15:30:45",
            "version": "1.0.0"
        }
    }
    
    # Add appropriate success or error indicators
    if not success:
        response["error"] = {
            "code": "TEST_ERROR",
            "message": "Test error message",
            "details": response_data.get("error_details", "")
        }
    
    return response

def pytest_configure(config):
    """
    Pytest hook to configure the integration test environment when pytest loads this package.
    
    Args:
        config (object): The pytest configuration object
    """
    # Register custom markers for CLI integration tests
    config.addinivalue_line("markers", "cli_command: mark a test as a CLI command integration test")
    config.addinivalue_line("markers", "cli_parser: mark a test as a CLI parser integration test")
    config.addinivalue_line("markers", "cli_backend: mark a test as a CLI and backend integration test")
    
    # Set up any pytest configuration specific to integration tests
    # Initialize the integration test environment
    setup_integration_test_environment()