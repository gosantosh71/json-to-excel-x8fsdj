"""
Unit tests for the InputHandler class and related functions in the JSON to Excel Conversion Tool.

This test module verifies the functionality of file reading, validation, and JSON data preparation components
to ensure proper handling of various input scenarios including valid, invalid, and edge cases.
"""

import os
import json
import pytest
from unittest import mock

# Import the InputHandler class and related functions
from ...input_handler import (
    InputHandler, 
    read_json_file, 
    get_json_data, 
    validate_json_file, 
    get_file_info
)

# Import exceptions for testing error handling
from ...exceptions import (
    FileNotFoundError, 
    InvalidFileTypeError, 
    FileTooLargeError, 
    PermissionError as FilePermissionError,
    JSONParseError
)

# Import related models
from ...models.json_data import JSONData
from ...models.error_response import ErrorResponse

# Import test fixtures
from ..fixtures.json_fixtures import (
    flat_json, 
    nested_json, 
    array_json,
    complex_json,
    invalid_json
)

# Import utility functions
from .. import (
    create_temp_json_file,
    cleanup_temp_file,
    get_test_file_path
)

# Import constants for validation
from ...constants import FILE_CONSTANTS

# Define test data
TEST_JSON_CONTENT = '{"name": "test", "value": 123}'
INVALID_JSON_CONTENT = '{"name": "test", value: 123}'  # Missing quotes around value

def setup_function():
    """Setup function that runs before each test to prepare the test environment."""
    # Create any necessary test directories
    os.makedirs("test_temp", exist_ok=True)

def teardown_function():
    """Teardown function that runs after each test to clean up the test environment."""
    # Remove test directories if they exist
    if os.path.exists("test_temp"):
        for file in os.listdir("test_temp"):
            os.remove(os.path.join("test_temp", file))
        os.rmdir("test_temp")

class TestInputHandlerFunctions:
    """Test class for the standalone functions in the input_handler module."""
    
    def test_read_json_file_success(self):
        """Tests that read_json_file successfully reads a valid JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call the function
            data = read_json_file(temp_file)
            
            # Assert that the data matches what we expect
            assert data is not None
            assert data['name'] == 'test'
            assert data['value'] == 123
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_read_json_file_not_found(self):
        """Tests that read_json_file handles file not found errors correctly."""
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Expect a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            read_json_file(non_existent_file)
    
    def test_read_json_file_invalid_json(self):
        """Tests that read_json_file handles invalid JSON content correctly."""
        # Create a temporary file with invalid JSON content
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(INVALID_JSON_CONTENT)
            
            # Expect a JSONParseError
            with pytest.raises(JSONParseError):
                read_json_file(temp_path)
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_path)
    
    def test_validate_json_input_success(self):
        """Tests that validate_json_input successfully validates a valid JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call the function
            result = validate_json_file(temp_file)
            
            # Assert that the validation was successful
            assert result is True
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_validate_json_input_file_not_found(self):
        """Tests that validate_json_input handles file not found errors correctly."""
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Call the function
        result = validate_json_file(non_existent_file)
        
        # Assert that the validation failed
        assert result is False
    
    def test_validate_json_input_invalid_json(self):
        """Tests that validate_json_input handles invalid JSON content correctly."""
        # Create a temporary file with invalid JSON content
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(INVALID_JSON_CONTENT)
            
            # Call the function
            result = validate_json_file(temp_path)
            
            # Assert that the validation failed
            assert result is False
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_path)
    
    def test_validate_json_input_file_too_large(self):
        """Tests that validate_json_input handles files exceeding size limits correctly."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Mock get_file_size to return a size larger than MAX_FILE_SIZE_BYTES
            with mock.patch('os.path.getsize', return_value=FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'] + 1):
                # Call the function
                result = validate_json_file(temp_file)
                
                # Assert that the validation failed
                assert result is False
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_get_json_file_info_success(self):
        """Tests that get_json_file_info successfully retrieves information about a JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call the function
            file_info = get_file_info(temp_file)
            
            # Assert that file information is returned
            assert file_info is not None
            assert 'path' in file_info
            assert 'size' in file_info
            assert 'extension' in file_info
            assert file_info['extension'] == 'json'
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_get_json_file_info_file_not_found(self):
        """Tests that get_json_file_info handles file not found errors correctly."""
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Expect a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            get_file_info(non_existent_file)
    
    def test_prepare_json_data_success(self):
        """Tests that prepare_json_data successfully prepares JSON data for processing."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call the function
            json_data = get_json_data(temp_file)
            
            # Assert that a JSONData object is returned
            assert json_data is not None
            assert isinstance(json_data, JSONData)
            assert json_data.content['name'] == 'test'
            assert json_data.content['value'] == 123
            assert json_data.is_analyzed  # Structure should be analyzed
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_prepare_json_data_validation_failure(self):
        """Tests that prepare_json_data handles validation failures correctly."""
        # Create a temporary file with invalid JSON content
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(INVALID_JSON_CONTENT)
            
            # Expect a JSONParseError
            with pytest.raises(JSONParseError):
                get_json_data(temp_path)
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_path)

class TestInputHandlerClass:
    """Test class for the InputHandler class methods."""
    
    def setup_method(self):
        """Setup method that runs before each test to initialize an InputHandler instance."""
        self.input_handler = InputHandler()
    
    def test_constructor(self):
        """Tests that the InputHandler constructor initializes properties correctly."""
        # Create an InputHandler with custom max_file_size_bytes
        custom_size = 1024 * 1024  # 1MB
        handler = InputHandler(max_file_size=custom_size)
        
        # Verify that the _max_file_size_bytes property is set correctly
        assert handler._max_file_size == custom_size
        # Verify that the adapters and validators are initialized
        assert handler._file_adapter is not None
        assert handler._file_validator is not None
    
    def test_read_file_success(self):
        """Tests that the read_file method successfully reads a valid JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call self.input_handler.read_file with the temporary file path
            data = self.input_handler.read_json_file(temp_file)
            
            # Assert that the returned data matches the expected content
            assert data is not None
            assert data['name'] == 'test'
            assert data['value'] == 123
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_read_file_not_found(self):
        """Tests that the read_file method handles file not found errors correctly."""
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Expect a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            self.input_handler.read_json_file(non_existent_file)
    
    def test_validate_file_success(self):
        """Tests that the validate_file method successfully validates a valid JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call self.input_handler.validate_file with the temporary file path
            result = self.input_handler.validate_json_file(temp_file)
            
            # Assert that True is returned for the validation result
            assert result is True
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_validate_file_not_found(self):
        """Tests that the validate_file method handles file not found errors correctly."""
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Call self.input_handler.validate_file with a non-existent file path
        result = self.input_handler.validate_json_file(non_existent_file)
        
        # Assert that False is returned for the validation result
        assert result is False
    
    def test_validate_file_too_large(self):
        """Tests that the validate_file method handles files exceeding size limits correctly."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Mock the file_system_adapter.get_file_info to return a size larger than _max_file_size_bytes
            with mock.patch('os.path.getsize', return_value=self.input_handler._max_file_size + 1):
                # Call self.input_handler.validate_file with the temporary file path
                result = self.input_handler.validate_json_file(temp_file)
                
                # Assert that False is returned for the validation result
                assert result is False
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_get_file_info_success(self):
        """Tests that the get_file_info method successfully retrieves information about a JSON file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call self.input_handler.get_file_info with the temporary file path
            file_info = self.input_handler.get_file_info(temp_file)
            
            # Assert that file information is returned
            assert file_info is not None
            # Verify that the file information contains expected fields
            assert 'path' in file_info
            assert 'size' in file_info
            assert 'extension' in file_info
            assert file_info['extension'] == 'json'
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_prepare_data_success(self):
        """Tests that the prepare_data method successfully prepares JSON data for processing."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call self.input_handler.prepare_data with the temporary file path
            json_data = self.input_handler.get_json_data(temp_file)
            
            # Assert that a JSONData object is returned
            assert json_data is not None
            assert isinstance(json_data, JSONData)
            # Verify that the JSONData object contains the expected content
            assert json_data.content['name'] == 'test'
            assert json_data.content['value'] == 123
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_input_success(self):
        """Tests that the process_input method successfully processes a JSON input file."""
        # Create a temporary JSON file with valid content
        temp_file = create_temp_json_file(json.loads(TEST_JSON_CONTENT))
        
        try:
            # Call self.input_handler.process_input with the temporary file path
            content, structure_info = self.input_handler.process_json_file(temp_file)
            
            # Assert that the JSONData object contains the expected content
            assert content is not None
            assert structure_info is not None
            assert content['name'] == 'test'
            assert content['value'] == 123
            assert 'is_nested' in structure_info
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_input_failure(self):
        """Tests that the process_input method handles processing failures correctly."""
        # Create a temporary file with invalid JSON content
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(INVALID_JSON_CONTENT)
            
            # Expect a JSONParseError
            with pytest.raises(JSONParseError):
                self.input_handler.process_json_file(temp_path)
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_path)

class TestInputHandlerWithFixtures:
    """Test class for the InputHandler class using predefined JSON fixtures."""
    
    def setup_method(self):
        """Setup method that runs before each test to initialize an InputHandler instance."""
        self.input_handler = InputHandler()
    
    def test_process_flat_json(self, flat_json):
        """Tests processing a flat JSON structure using fixtures."""
        # Create a temporary JSON file with the flat_json fixture content
        temp_file = create_temp_json_file(flat_json)
        
        try:
            # Call self.input_handler.process_input with the temporary file path
            json_data = self.input_handler.get_json_data(temp_file)
            
            # Verify that is_nested is False in the JSONData object
            assert json_data is not None
            assert json_data.is_nested is False
            # Verify that contains_arrays is False in the JSONData object
            assert json_data.contains_arrays is False
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_nested_json(self, nested_json):
        """Tests processing a nested JSON structure using fixtures."""
        # Create a temporary JSON file with the nested_json fixture content
        temp_file = create_temp_json_file(nested_json)
        
        try:
            # Call self.input_handler.process_input with the temporary file path
            json_data = self.input_handler.get_json_data(temp_file)
            
            # Verify that is_nested is True in the JSONData object
            assert json_data is not None
            assert json_data.is_nested is True
            # Verify that max_nesting_level is greater than 1
            assert json_data.max_nesting_level > 1
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_array_json(self, array_json):
        """Tests processing a JSON structure with arrays using fixtures."""
        # Create a temporary JSON file with the array_json fixture content
        temp_file = create_temp_json_file(array_json)
        
        try:
            # Call self.input_handler.process_input with the temporary file path
            json_data = self.input_handler.get_json_data(temp_file)
            
            # Verify that contains_arrays is True in the JSONData object
            assert json_data is not None
            assert json_data.contains_arrays is True
            # Verify that array_paths is not empty
            assert len(json_data.array_paths) > 0
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_complex_json(self, complex_json):
        """Tests processing a complex JSON structure using fixtures."""
        # Create a temporary JSON file with the complex_json fixture content
        temp_file = create_temp_json_file(complex_json)
        
        try:
            # Call self.input_handler.process_input with the temporary file path
            json_data = self.input_handler.get_json_data(temp_file)
            
            # Verify that is_nested is True in the JSONData object
            assert json_data is not None
            assert json_data.is_nested is True
            # Verify that contains_arrays is True in the JSONData object
            assert json_data.contains_arrays is True
            # Verify that complexity_score is high
            assert json_data.complexity_score > 5
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_file)
    
    def test_process_invalid_json(self, invalid_json):
        """Tests processing an invalid JSON structure using fixtures."""
        # Need to manually create a file with invalid JSON as it can't be parsed by Python
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(invalid_json)
            
            # Expect a JSONParseError
            with pytest.raises(JSONParseError):
                self.input_handler.get_json_data(temp_path)
        finally:
            # Clean up the temporary file
            cleanup_temp_file(temp_path)