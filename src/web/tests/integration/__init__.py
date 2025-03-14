"""
Initialization module for the integration tests package of the JSON to Excel Conversion Tool's web interface.

This module provides common configuration, fixtures, and utilities for integration testing
of the web interface component, including API endpoint testing and component interactions.
"""

import os
import pytest  # pytest 7.3.0+

# Define constants for test directories and resources
INTEGRATION_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
INTEGRATION_TEST_MARKER = pytest.mark.integration
FIXTURES_DIR = os.path.join(os.path.dirname(INTEGRATION_TEST_DIR), 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')


def pytest_mark_integration():
    """
    Decorator function that applies the integration test marker to test functions.
    
    Returns:
        function: Decorated test function with integration marker
    """
    return INTEGRATION_TEST_MARKER


@pytest.fixture
def setup_integration_test():
    """
    Fixture that sets up the environment for integration tests.
    
    Returns:
        dict: Dictionary with test environment configuration
    """
    # Create configuration dictionary with paths and settings for integration tests
    config = {
        'integration_test_dir': INTEGRATION_TEST_DIR,
        'fixtures_dir': FIXTURES_DIR,
        'sample_data_dir': SAMPLE_DATA_DIR,
        'expected_output_dir': EXPECTED_OUTPUT_DIR,
        # Add other configuration settings as needed for integration tests
    }
    
    return config


def get_sample_json_path(filename):
    """
    Utility function to get the path to a sample JSON file.
    
    Args:
        filename (str): Name of the sample JSON file
        
    Returns:
        str: Path to the sample JSON file
    """
    return os.path.join(SAMPLE_DATA_DIR, filename)


def get_expected_excel_path(filename):
    """
    Utility function to get the path to an expected Excel file.
    
    Args:
        filename (str): Name of the expected Excel file
        
    Returns:
        str: Path to the expected Excel file
    """
    return os.path.join(EXPECTED_OUTPUT_DIR, filename)