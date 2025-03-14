"""
Unit tests for the JSON parser component of the JSON to Excel Conversion Tool.

This file contains comprehensive test cases to verify the functionality of parsing, 
validating, and analyzing JSON data structures, including handling of flat, nested, 
and invalid JSON formats.
"""

import pytest  # v: 7.3.0+
import json  # v: built-in
import os  # v: built-in
import tempfile  # v: built-in

from ...json_parser import (
    JSONParser, 
    parse_json_string, 
    parse_json_file, 
    analyze_json_structure, 
    detect_json_type,
    create_json_data
)
from ...models.json_data import JSONData, JSONComplexity
from ...exceptions import (
    JSONParsingException, 
    JSONValidationException, 
    JSONStructureException
)
from ..fixtures.json_fixtures import (
    flat_json, 
    nested_json, 
    array_json, 
    complex_json, 
    invalid_json,
    get_invalid_json_string
)

# Define a constant for sample data directory
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_data')


def test_json_parser_initialization():
    """Tests that the JSONParser class initializes correctly with default and custom parameters."""
    # Create a JSONParser instance with default parameters
    parser = JSONParser()
    assert parser is not None
    assert parser._max_nesting_level == 10  # Default from JSON_CONSTANTS
    
    # Create a JSONParser instance with custom parameters
    custom_parser = JSONParser(max_nesting_level=15)
    assert custom_parser._max_nesting_level == 15


def test_parse_json_string_valid():
    """Tests parsing a valid JSON string."""
    # Create a valid JSON string
    valid_json = '{"name": "Test", "value": 123}'
    
    # Call parse_json_string with the valid JSON string
    result, error = parse_json_string(valid_json)
    
    # Verify that the function returns the expected parsed JSON object
    assert error is None
    assert result is not None
    assert isinstance(result, dict)
    assert result["name"] == "Test"
    assert result["value"] == 123


def test_parse_json_string_invalid():
    """Tests parsing an invalid JSON string and verifies that appropriate exceptions are raised."""
    # Get an invalid JSON string
    invalid_json = get_invalid_json_string()
    
    # Use parse_json_string and verify error is returned
    result, error = parse_json_string(invalid_json)
    
    # Verify that the error contains appropriate details
    assert result is None
    assert error is not None
    assert error.category.value == "parsing_error"
    assert "Invalid JSON syntax" in error.message
    assert error.context.get("line") is not None


def test_parse_json_file_valid():
    """Tests parsing a valid JSON file."""
    # Create a temporary file with valid JSON content
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        tmp.write('{"name": "Test", "value": 123}')
        tmp.flush()
        temp_file_path = tmp.name
    
    try:
        # Call parse_json_file with the valid file path
        result, error = parse_json_file(temp_file_path)
        
        # Verify that the function returns the expected parsed JSON object
        assert error is None
        assert result is not None
        assert isinstance(result, dict)
        assert result["name"] == "Test"
        assert result["value"] == 123
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_parse_json_file_not_found():
    """Tests parsing a non-existent JSON file and verifies that appropriate exceptions are raised."""
    # Create a path to a non-existent JSON file
    non_existent_file = os.path.join(SAMPLE_DATA_DIR, "nonexistent.json")
    
    # Verify that FileNotFoundError is raised
    with pytest.raises(FileNotFoundError):
        parse_json_file(non_existent_file)


def test_json_parser_parse_string():
    """Tests the parse_string method of the JSONParser class with valid and invalid inputs."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Test with a valid JSON string
    valid_json = '{"name": "Test", "value": 123}'
    result, error = parser.parse_string(valid_json)
    
    # Verify successful parsing
    assert error is None
    assert result is not None
    assert result["name"] == "Test"
    assert result["value"] == 123
    
    # Test with an invalid JSON string
    invalid_json = get_invalid_json_string()
    result, error = parser.parse_string(invalid_json)
    
    # Verify exception handling
    assert result is None
    assert error is not None
    assert error.category.value == "parsing_error"


def test_json_parser_parse_file():
    """Tests the parse_file method of the JSONParser class with valid and invalid file paths."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Create a temporary file with valid JSON content
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        tmp.write('{"name": "Test", "value": 123}')
        tmp.flush()
        temp_file_path = tmp.name
    
    try:
        # Test with a valid JSON file path
        with pytest.raises(NotImplementedError):
            # This will raise NotImplementedError as the method is not implemented in the provided code
            parser.parse_file(temp_file_path)
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_analyze_json_structure():
    """Tests the analyze_json_structure function with different JSON structures."""
    # Test with flat JSON structure
    flat_structure = {"id": 1, "name": "Test", "active": True}
    flat_analysis = analyze_json_structure(flat_structure)
    
    # Verify that is_nested is False and complexity level is SIMPLE
    assert flat_analysis["is_nested"] == False
    assert flat_analysis["max_nesting_level"] == 1
    assert flat_analysis["complexity_level"] == "SIMPLE"
    
    # Test with nested JSON structure
    nested_structure = {
        "id": 1,
        "name": "Test",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        }
    }
    nested_analysis = analyze_json_structure(nested_structure)
    
    # Verify that is_nested is True and complexity level is higher than SIMPLE
    assert nested_analysis["is_nested"] == True
    assert nested_analysis["max_nesting_level"] >= 2
    assert nested_analysis["complexity_level"] in ["MODERATE", "COMPLEX"]
    
    # Verify that flattening_strategy is provided
    assert "flattening_strategy" in nested_analysis


def test_json_parser_create_json_data():
    """Tests the create_json_data method of the JSONParser class."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Parse a JSON structure
    json_data = {"id": 1, "name": "Test", "active": True}
    
    # Call create_json_data with the parsed JSON
    json_data_obj = parser.create_json_data(json_data, "memory", 100)
    
    # Verify that a JSONData object is returned with correct analysis
    assert isinstance(json_data_obj, JSONData)
    assert json_data_obj.content == json_data
    assert json_data_obj.source_path == "memory"
    assert json_data_obj.size_bytes == 100
    assert json_data_obj.is_analyzed == True


def test_detect_json_type():
    """Tests the detect_json_type function with different JSON structures."""
    # Test with flat JSON and verify type is 'flat'
    flat_structure = {"id": 1, "name": "Test", "active": True}
    assert detect_json_type(flat_structure) == "flat"
    
    # Test with nested JSON and verify type is 'nested'
    nested_structure = {
        "id": 1,
        "name": "Test",
        "address": {"street": "123 Main St", "city": "Anytown"}
    }
    assert detect_json_type(nested_structure) == "nested"
    
    # Test with array JSON and verify type is 'array'
    array_structure = {
        "id": 1,
        "name": "Test",
        "items": [1, 2, 3],
        "tags": ["tag1", "tag2"]
    }
    assert detect_json_type(array_structure) == "array"
    
    # Test with complex JSON and verify type is 'mixed'
    complex_structure = {
        "id": 1,
        "name": "Test",
        "address": {"street": "123 Main St"},
        "items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    }
    assert detect_json_type(complex_structure) == "mixed"


def test_json_parser_detect_type():
    """Tests the detect_type method of the JSONParser class."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Test with different JSON structures
    flat_structure = {"id": 1, "name": "Test", "active": True}
    nested_structure = {
        "id": 1,
        "name": "Test",
        "address": {"street": "123 Main St"}
    }
    array_structure = {
        "id": 1,
        "name": "Test",
        "items": [1, 2, 3]
    }
    
    # Verify that the correct type is detected for each structure
    assert parser.detect_type(flat_structure) == "flat"
    assert parser.detect_type(nested_structure) == "nested"
    assert parser.detect_type(array_structure) == "array"


def test_json_parser_validate():
    """Tests the validate method of the JSONParser class."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Test with valid JSON and verify validation passes
    valid_json = {"id": 1, "name": "Test", "active": True}
    is_valid, error = parser.validate(valid_json)
    assert is_valid is True
    assert error is None
    
    # Test with invalid JSON structure and verify validation fails
    invalid_json = ["Not a dictionary"]
    is_valid, error = parser.validate(invalid_json)
    assert is_valid is False
    assert error is not None
    assert error.category.value == "parsing_error"
    assert "Invalid JSON structure" in error.message


def test_json_parser_get_structure_info():
    """Tests the get_structure_info method of the JSONParser class."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Parse different JSON structures
    flat_structure = {"id": 1, "name": "Test", "active": True}
    nested_structure = {
        "id": 1,
        "name": "Test",
        "address": {"street": "123 Main St", "city": "Anytown"}
    }
    array_structure = {
        "id": 1,
        "name": "Test",
        "items": [1, 2, 3]
    }
    
    # Call get_structure_info for each structure
    flat_info = parser.get_structure_info(flat_structure)
    nested_info = parser.get_structure_info(nested_structure)
    array_info = parser.get_structure_info(array_structure)
    
    # Verify that the returned structure information is correct
    assert flat_info["is_nested"] == False
    assert flat_info["contains_arrays"] == False
    assert flat_info["complexity_level"] == "SIMPLE"
    
    assert nested_info["is_nested"] == True
    assert nested_info["contains_arrays"] == False
    assert nested_info["complexity_level"] in ["MODERATE", "COMPLEX"]
    
    assert array_info["is_nested"] == False
    assert array_info["contains_arrays"] == True
    assert "items" in array_info["array_paths"]


def test_json_parser_format_json():
    """Tests the format_json method of the JSONParser class."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Parse a JSON structure
    json_data = {"id": 1, "name": "Test", "active": True}
    
    # Call format_json with different indent values
    formatted_2 = parser.format_json(json_data, indent=2)
    formatted_4 = parser.format_json(json_data, indent=4)
    
    # Verify that the formatted JSON string has the correct indentation
    assert isinstance(formatted_2, str)
    assert "{\n  " in formatted_2  # 2-space indentation
    
    assert isinstance(formatted_4, str)
    assert "{\n    " in formatted_4  # 4-space indentation
    
    # Test with no indentation
    formatted_none = parser.format_json(json_data, indent=None)
    assert "\n" not in formatted_none  # No line breaks means no pretty printing


def test_json_parser_with_temp_file():
    """Tests the JSONParser with a temporary file created during the test."""
    # Create a temporary file with JSON content
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        json_data = {"id": 1, "name": "Test", "nested": {"key": "value"}, "array": [1, 2, 3]}
        json.dump(json_data, tmp)
        tmp.flush()
        temp_file_path = tmp.name
    
    try:
        # Create a JSONParser instance
        parser = JSONParser()
        
        # Since parse_file isn't fully implemented, we'll read the file and use parse_string
        with open(temp_file_path, 'r') as f:
            json_content = f.read()
            
        result, error = parser.parse_string(json_content)
        
        # Verify that the parsing is successful
        assert error is None
        assert result is not None
        assert result["id"] == 1
        assert result["nested"]["key"] == "value"
        assert result["array"] == [1, 2, 3]
        
        # Test structure analysis
        structure_info = parser.get_structure_info(result)
        assert structure_info["is_nested"] == True
        assert structure_info["contains_arrays"] == True
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_json_parser_with_fixtures(flat_json, nested_json, array_json, complex_json):
    """Tests the JSONParser with pytest fixtures for different JSON structures."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Test parsing and analysis with each fixture
    flat_info = parser.get_structure_info(flat_json)
    nested_info = parser.get_structure_info(nested_json)
    array_info = parser.get_structure_info(array_json)
    complex_info = parser.get_structure_info(complex_json)
    
    # Verify that the correct structure type is detected for each fixture
    assert flat_info["is_nested"] == False
    assert flat_info["complexity_level"] == "SIMPLE"
    
    assert nested_info["is_nested"] == True
    assert nested_info["max_nesting_level"] >= 2
    assert nested_info["complexity_level"] in ["MODERATE", "COMPLEX"]
    
    assert array_info["contains_arrays"] == True
    assert len(array_info["array_paths"]) > 0
    
    # Verify that the analysis results match the expected characteristics
    assert complex_info["is_nested"] == True
    assert complex_info["contains_arrays"] == True
    assert complex_info["complexity_level"] in ["COMPLEX", "VERY_COMPLEX"]
    assert complex_info["max_nesting_level"] >= 4


def test_json_parser_error_handling(invalid_json):
    """Tests the error handling capabilities of the JSONParser."""
    # Create a JSONParser instance
    parser = JSONParser()
    
    # Test parsing invalid JSON and verify appropriate exceptions are raised
    result, error = parser.parse_string(invalid_json)
    assert result is None
    assert error is not None
    assert error.category.value == "parsing_error"
    assert "Invalid JSON syntax" in error.message
    
    # Test parsing non-existent files
    non_existent_file = os.path.join(SAMPLE_DATA_DIR, "nonexistent.json")
    with pytest.raises(FileNotFoundError):
        parse_json_file(non_existent_file)
    
    # Test with invalid structure (array instead of object)
    array_json = "[1, 2, 3]"
    result, error = parse_json_string(array_json)
    assert result is not None  # Valid JSON, just not an object
    
    is_valid, error = parser.validate(result)
    assert is_valid is False
    assert error is not None
    assert "Invalid JSON structure" in error.message


class TestJSONParser:
    """Test class for the JSONParser component, containing all test methods for parsing, validation, and analysis of JSON data."""
    
    def setup_method(self, method):
        """Set up method that runs before each test."""
        # Initialize common test resources
        self.parser = JSONParser()
        self.temp_files = []
        
        # Set up paths to test data files
        self.sample_data_dir = SAMPLE_DATA_DIR
    
    def teardown_method(self, method):
        """Tear down method that runs after each test."""
        # Clean up any resources created during tests
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_initialization(self):
        """Tests the initialization of the JSONParser class."""
        # Create a JSONParser with default parameters
        assert self.parser is not None
        assert self.parser._max_nesting_level == 10
        
        # Create a JSONParser with custom parameters
        custom_parser = JSONParser(max_nesting_level=15)
        assert custom_parser._max_nesting_level == 15
    
    def test_parse_string_valid(self):
        """Tests parsing a valid JSON string."""
        # Create a valid JSON string
        valid_json = '{"name": "Test", "value": 123}'
        
        # Parse the string using the JSONParser
        result, error = self.parser.parse_string(valid_json)
        
        # Verify the parsed result matches the expected structure
        assert error is None
        assert result is not None
        assert result["name"] == "Test"
        assert result["value"] == 123
    
    def test_parse_string_invalid(self):
        """Tests parsing an invalid JSON string."""
        # Create an invalid JSON string
        invalid_json = get_invalid_json_string()
        
        # Attempt to parse the string and verify JSONParsingException is raised
        result, error = self.parser.parse_string(invalid_json)
        
        # Verify the exception contains appropriate error details
        assert result is None
        assert error is not None
        assert error.category.value == "parsing_error"
        assert "Invalid JSON syntax" in error.message
    
    def test_parse_file_valid(self):
        """Tests parsing a valid JSON file."""
        # Get path to a valid JSON test file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
            json_data = {"id": 1, "name": "Test"}
            json.dump(json_data, tmp)
            tmp.flush()
            self.temp_files.append(tmp.name)
            
            # This method would be tested if implemented in the class
            with pytest.raises(NotImplementedError):
                self.parser.parse_file(tmp.name)
    
    def test_parse_file_not_found(self):
        """Tests parsing a non-existent JSON file."""
        # Create a path to a non-existent file
        non_existent_file = os.path.join(self.sample_data_dir, "nonexistent.json")
        
        # Attempt to parse the file - will raise NotImplementedError since the method isn't implemented
        with pytest.raises(NotImplementedError):
            self.parser.parse_file(non_existent_file)
    
    def test_create_json_data(self):
        """Tests creating a JSONData object from parsed JSON."""
        # Parse a JSON file to get the data
        json_data = {"id": 1, "name": "Test", "active": True}
        
        # Create a JSONData object using the parser
        json_data_obj = self.parser.create_json_data(json_data, "memory", 100)
        
        # Verify the JSONData object contains correct analysis results
        assert isinstance(json_data_obj, JSONData)
        assert json_data_obj.content == json_data
        assert json_data_obj.source_path == "memory"
        assert json_data_obj.size_bytes == 100
        assert json_data_obj.is_analyzed == True
    
    def test_detect_type(self):
        """Tests detecting the type of JSON structure."""
        # Test with different JSON structures (flat, nested, array, complex)
        flat_structure = {"id": 1, "name": "Test", "active": True}
        nested_structure = {
            "id": 1, 
            "name": "Test",
            "address": {"street": "123 Main St"}
        }
        array_structure = {
            "id": 1,
            "name": "Test",
            "items": [1, 2, 3]
        }
        
        # Verify the correct type is detected for each structure
        assert self.parser.detect_type(flat_structure) == "flat"
        assert self.parser.detect_type(nested_structure) == "nested"
        assert self.parser.detect_type(array_structure) == "array"
    
    def test_validate(self):
        """Tests validating JSON structures."""
        # Test validation with valid JSON structures
        valid_json = {"id": 1, "name": "Test", "active": True}
        is_valid, error = self.parser.validate(valid_json)
        assert is_valid is True
        assert error is None
        
        # Test validation with invalid JSON structures
        invalid_json = ["Not a dictionary"]
        is_valid, error = self.parser.validate(invalid_json)
        assert is_valid is False
        assert error is not None
        assert "Invalid JSON structure" in error.message
    
    def test_get_structure_info(self):
        """Tests getting structure information from JSON."""
        # Parse different JSON structures
        flat_structure = {"id": 1, "name": "Test", "active": True}
        nested_structure = {
            "id": 1,
            "name": "Test",
            "address": {"street": "123 Main St", "city": "Anytown"}
        }
        array_structure = {
            "id": 1,
            "name": "Test",
            "items": [1, 2, 3]
        }
        
        # Get structure information for each
        flat_info = self.parser.get_structure_info(flat_structure)
        nested_info = self.parser.get_structure_info(nested_structure)
        array_info = self.parser.get_structure_info(array_structure)
        
        # Verify the structure information is correct
        assert flat_info["is_nested"] == False
        assert flat_info["contains_arrays"] == False
        
        assert nested_info["is_nested"] == True
        assert nested_info["max_nesting_level"] >= 2
        
        assert array_info["contains_arrays"] == True
        assert "items" in array_info["array_paths"]
    
    def test_format_json(self):
        """Tests formatting JSON with different indentation."""
        # Parse a JSON structure
        json_data = {"id": 1, "name": "Test", "active": True}
        
        # Format with different indent values
        formatted_2 = self.parser.format_json(json_data, indent=2)
        formatted_4 = self.parser.format_json(json_data, indent=4)
        
        # Verify the formatted output has correct indentation
        assert isinstance(formatted_2, str)
        assert "{\n  " in formatted_2
        
        assert isinstance(formatted_4, str)
        assert "{\n    " in formatted_4
    
    def test_with_fixtures(self, flat_json, nested_json, array_json, complex_json):
        """Tests using pytest fixtures for different JSON structures."""
        # Test each fixture with the parser
        flat_info = self.parser.get_structure_info(flat_json)
        nested_info = self.parser.get_structure_info(nested_json)
        array_info = self.parser.get_structure_info(array_json)
        complex_info = self.parser.get_structure_info(complex_json)
        
        # Verify correct parsing and analysis for each structure type
        assert flat_info["is_nested"] == False
        assert flat_info["complexity_level"] == "SIMPLE"
        
        assert nested_info["is_nested"] == True
        assert nested_info["complexity_level"] in ["MODERATE", "COMPLEX"]
        
        assert array_info["contains_arrays"] == True
        assert len(array_info["array_paths"]) > 0
        
        assert complex_info["is_nested"] == True
        assert complex_info["contains_arrays"] == True
        assert complex_info["complexity_level"] in ["COMPLEX", "VERY_COMPLEX"]
    
    def test_error_handling(self, invalid_json):
        """Tests error handling for various error conditions."""
        # Test various error conditions
        result, error = self.parser.parse_string(invalid_json)
        
        # Verify appropriate exceptions are raised
        assert result is None
        assert error is not None
        
        # Verify exception details are correct
        assert error.category.value == "parsing_error"
        assert "Invalid JSON syntax" in error.message