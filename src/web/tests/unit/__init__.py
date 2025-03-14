"""
Initialization module for the unit tests package in the web interface component
of the JSON to Excel Conversion Tool.

This module provides configuration and utility functions specifically for unit tests,
including pytest markers and environment setup.
"""

import os
import pytest  # pytest 7.3.0+

# Directory containing the unit tests
UNIT_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Marker for unit tests
UNIT_TEST_MARKER = pytest.mark.unit

def pytest_configure(config):
    """
    Pytest hook to configure the test environment for unit tests.
    Registers custom markers.
    
    Args:
        config: The pytest configuration object
    
    Returns:
        None
    """
    # Register the 'unit' marker to prevent warnings about unknown markers
    config.addinivalue_line(
        "markers", 
        "unit: mark test as a unit test that tests a single component in isolation"
    )

def setup_unit_test_environment():
    """
    Sets up the environment for unit tests including test data paths and common mocks.
    
    Returns:
        dict: Dictionary containing setup configuration for unit tests
    """
    # Define paths to test fixture data
    test_data_path = os.path.join(UNIT_TESTS_DIR, "data")
    json_fixtures_path = os.path.join(test_data_path, "json")
    excel_fixtures_path = os.path.join(test_data_path, "excel")
    
    # Set up common configuration for unit tests
    test_config = {
        "test_data_path": test_data_path,
        "json_fixtures_path": json_fixtures_path,
        "excel_fixtures_path": excel_fixtures_path,
        "mock_config": {
            "default_timeout": 5,
            "simulate_errors": False
        }
    }
    
    return test_config