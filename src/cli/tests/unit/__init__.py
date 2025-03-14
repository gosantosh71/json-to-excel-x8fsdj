"""
Initialization file for the CLI unit tests package.

This file marks the directory as a Python package, allowing test modules to be imported.
It provides common test utilities, fixtures, and setup code shared across unit tests for
the CLI component of the JSON to Excel Conversion Tool.
"""

import os
import pytest  # v: 7.3.0+

# Import fixtures from the fixtures module
from ..fixtures.cli_fixtures import (
    get_basic_command_options,
    get_complex_command_options,
    get_invalid_command_options,
    get_validation_error
)

# Define package constants
TEST_PACKAGE_NAME = "cli_unit_tests"
UNIT_TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def pytest_configure(config):
    """
    Optional pytest configuration function that can be used to set up the test environment 
    for all unit tests.
    
    Args:
        config: The pytest configuration object
        
    Returns:
        None: No return value
    """
    # Configure pytest for unit tests if needed
    # Set up any global test configuration
    # Register custom markers for unit tests
    pass

# Re-exported fixtures and constants:
# TEST_PACKAGE_NAME - Constant defining the package name for CLI unit tests
# UNIT_TEST_DIR - Constant defining the directory path of CLI unit tests
# get_basic_command_options - Basic command options fixture for use in unit tests
# get_complex_command_options - Complex command options fixture for use in unit tests
# get_invalid_command_options - Invalid command options fixture for use in unit tests
# get_validation_error - Validation error fixture for use in unit tests