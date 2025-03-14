"""
Initialization file for the fixtures package that exposes test fixtures and utility functions for JSON and Excel testing.
This file serves as a central point for importing test fixtures across the test suite, making them available to all test modules.
"""

from pathlib import Path

# Global constants for fixture paths
FIXTURES_DIR = Path(__file__).parent
SAMPLE_DATA_DIR = FIXTURES_DIR / 'sample_data'
EXPECTED_OUTPUT_DIR = FIXTURES_DIR / 'expected_output'

# Import and re-export JSON fixtures
from .json_fixtures import (
    flat_json, nested_json, array_json, complex_json, invalid_json,
    flat_json_data, nested_json_data, array_json_data, complex_json_data,
    load_json_file, get_json_data_object, get_invalid_json_string
)

# Import and re-export Excel fixtures
from .excel_fixtures import (
    default_excel_options, custom_excel_options,
    array_expand_options, array_join_options,
    expected_flat_excel, expected_nested_excel, expected_array_excel,
    test_flat_dataframe, test_nested_dataframe, test_array_dataframe,
    load_expected_excel, get_excel_file_path, create_test_dataframe
)