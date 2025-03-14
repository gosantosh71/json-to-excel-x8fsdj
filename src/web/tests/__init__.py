"""
Initialization module for the web interface tests package of the JSON to Excel Conversion Tool.

This module defines common test utilities, constants, and imports that are shared across
all test modules in the web interface component. It provides path manipulation utilities
for handling test fixtures and standardized pytest markers for test categorization.
"""

import os
from pathlib import Path
import pytest  # pytest 7.3.0+

# Define directory constants for test file organization
TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TEST_ROOT_DIR, 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')

# Define pytest markers for different test categories
UNIT_TEST_MARKER = pytest.mark.unit
INTEGRATION_TEST_MARKER = pytest.mark.integration
FUNCTIONAL_TEST_MARKER = pytest.mark.functional
E2E_TEST_MARKER = pytest.mark.e2e


def get_sample_json_path(filename: str) -> str:
    """
    Returns the absolute path to a sample JSON file in the test fixtures.

    Args:
        filename (str): The name of the sample JSON file

    Returns:
        str: Absolute path to the sample JSON file
    """
    return os.path.join(SAMPLE_DATA_DIR, filename)


def get_expected_excel_path(filename: str) -> str:
    """
    Returns the absolute path to an expected Excel output file in the test fixtures.

    Args:
        filename (str): The name of the expected Excel file

    Returns:
        str: Absolute path to the expected Excel file
    """
    return os.path.join(EXPECTED_OUTPUT_DIR, filename)


def create_test_file_path(relative_path: str) -> str:
    """
    Creates a path for a test file within the test directory structure.

    Args:
        relative_path (str): The relative path from the test root directory

    Returns:
        str: Absolute path to the test file location
    """
    return os.path.join(TEST_ROOT_DIR, relative_path)