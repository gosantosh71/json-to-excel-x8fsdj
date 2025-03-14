"""
Initialization module for the backend tests package.

This module provides common test utilities, helper functions, and fixtures
for use across all test modules in the JSON to Excel Conversion Tool.
"""

import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import pytest  # pytest 7.3.0+

# Define global constants for test directories
TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TEST_ROOT_DIR, 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')


def create_temp_json_file(content: Dict[str, Any], prefix: str = "test_json_") -> str:
    """
    Creates a temporary JSON file with the provided content for testing purposes.
    
    Args:
        content: Dictionary content to write as JSON
        prefix: Prefix for the temporary file name. Defaults to "test_json_".
    
    Returns:
        Path to the created temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=".json", prefix=prefix)
    try:
        with os.fdopen(fd, 'w') as temp_file:
            json.dump(content, temp_file)
    except Exception as e:
        os.close(fd)
        os.unlink(temp_path)
        raise e
    
    return temp_path


def cleanup_temp_file(file_path: str) -> bool:
    """
    Removes a temporary file created for testing.
    
    Args:
        file_path: Path to the temporary file to remove
    
    Returns:
        True if file was successfully removed, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            return True
        return False
    except Exception:
        return False


def get_test_file_path(filename: str) -> str:
    """
    Returns the absolute path to a test file in the sample data directory.
    
    Args:
        filename: Name of the test file
    
    Returns:
        Absolute path to the test file
    """
    return os.path.join(SAMPLE_DATA_DIR, filename)


def get_expected_output_path(filename: str) -> str:
    """
    Returns the absolute path to an expected output file in the expected output directory.
    
    Args:
        filename: Name of the expected output file
    
    Returns:
        Absolute path to the expected output file
    """
    return os.path.join(EXPECTED_OUTPUT_DIR, filename)


def create_test_json_string(data: Dict[str, Any], pretty: bool = False) -> str:
    """
    Creates a JSON string for testing purposes.
    
    Args:
        data: Dictionary to convert to a JSON string
        pretty: Whether to format the JSON with indentation. Defaults to False.
    
    Returns:
        JSON string representation of the data
    """
    indent = 4 if pretty else None
    return json.dumps(data, indent=indent)


def create_invalid_json_string() -> str:
    """
    Creates an invalid JSON string for testing error handling.
    
    Returns:
        Invalid JSON string with syntax errors
    """
    return '{"name": "test", value: 123}'  # Missing quotes around 'value'


class TestFileHelper:
    """
    Helper class for file operations in tests.
    """
    
    def __init__(self):
        """
        Initializes the TestFileHelper with an empty list of temporary files.
        """
        self._temp_files: List[str] = []
    
    def create_temp_file(self, content: str, suffix: str = ".txt") -> str:
        """
        Creates a temporary file with the given content.
        
        Args:
            content: Content to write to the file
            suffix: File suffix. Defaults to ".txt".
        
        Returns:
            Path to the created temporary file
        """
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'w') as temp_file:
                temp_file.write(content)
        except Exception as e:
            os.close(fd)
            os.unlink(temp_path)
            raise e
        
        self._temp_files.append(temp_path)
        return temp_path
    
    def create_temp_json_file(self, data: Dict[str, Any], prefix: str = "test_json_") -> str:
        """
        Creates a temporary JSON file with the given data.
        
        Args:
            data: Dictionary to convert to JSON and write to file
            prefix: Prefix for the file name. Defaults to "test_json_".
        
        Returns:
            Path to the created temporary JSON file
        """
        json_string = create_test_json_string(data)
        return self.create_temp_file(json_string, suffix=".json")
    
    def cleanup(self) -> None:
        """
        Cleans up all temporary files created by this helper.
        """
        for file_path in self._temp_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception:
                    pass  # Ignore errors during cleanup
        
        self._temp_files = []


@pytest.fixture
def file_helper():
    """
    Provides a TestFileHelper instance that automatically cleans up temporary files.
    
    Yields:
        TestFileHelper: An instance of the TestFileHelper class
    """
    helper = TestFileHelper()
    yield helper
    helper.cleanup()