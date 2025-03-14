"""
Unit tests for the ValidationService class, which is responsible for validating
JSON files, content, and output paths in the JSON to Excel Conversion Tool.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from ...services.validation_service import ValidationService
from ...validators.json_validator import JSONValidator
from ...validators.file_validator import FileValidator
from ...models.json_data import JSONData
from ...models.error_response import ErrorResponse, ErrorCategory
from ...adapters.file_system_adapter import FileSystemAdapter
from ..fixtures.json_fixtures import (
    flat_json,
    nested_json,
    array_json,
    complex_json,
    invalid_json,
    flat_json_data,
    nested_json_data,
    get_invalid_json_string
)

def test_validation_service_initialization():
    """Tests that the ValidationService initializes correctly with default and custom parameters."""
    # Create a ValidationService instance with default parameters
    validator = ValidationService()
    
    # Verify that internal properties are set to default values
    assert validator._max_file_size_bytes is not None
    assert validator._max_nesting_level is not None
    assert validator._file_validator is not None
    assert validator._json_validator is not None
    assert validator._file_system_adapter is not None
    
    # Create a ValidationService instance with custom parameters
    custom_max_file_size_mb = 10
    custom_max_nesting_level = 15
    custom_validator = ValidationService(
        max_file_size_mb=custom_max_file_size_mb,
        max_nesting_level=custom_max_nesting_level
    )
    
    # Verify that internal properties are set to the custom values
    assert custom_validator._max_file_size_bytes == custom_max_file_size_mb * 1024 * 1024
    assert custom_validator._max_nesting_level == custom_max_nesting_level


def test_validate_json_file_success(mock_file_validator, mock_json_validator, mock_file_system_adapter):
    """Tests that validate_json_file correctly validates a valid JSON file."""
    # Set up mock objects
    file_path = "valid_file.json"
    file_size = 1024  # 1KB
    json_content = '{"name": "test", "value": 123}'
    json_data = {'name': 'test', 'value': 123}
    
    # Configure mock_file_validator to return successful validation
    mock_file_validator.validate_json_file.return_value = (True, [])
    
    # Configure mock_file_system_adapter to return file size and content
    mock_file_system_adapter.get_file_size.return_value = file_size
    mock_file_system_adapter.read_json.return_value = json_content
    
    # Configure mock_json_validator to return successful validation
    mock_json_validator.validate_file_size.return_value = (True, None)
    mock_json_validator.validate_json_string.return_value = (True, None, json_data)
    mock_json_validator.validate_json_data_object.return_value = (True, [])
    
    # Create a mock JSONData instance for the return value
    mock_json_data = MagicMock(spec=JSONData)
    
    # Patch the JSONData class to return our mock instance
    with patch('src.backend.services.validation_service.JSONData', return_value=mock_json_data) as mock_json_data_class:
        # Create a ValidationService with our mocks
        validator = ValidationService()
        validator._file_validator = mock_file_validator
        validator._json_validator = mock_json_validator
        validator._file_system_adapter = mock_file_system_adapter
        
        # Call the method being tested
        result, errors, json_data_result = validator.validate_json_file(file_path)
        
        # Verify the method returns successful validation
        assert result is True
        assert errors == []
        assert json_data_result == mock_json_data
        
        # Verify the mocks were called correctly
        mock_file_validator.validate_json_file.assert_called_once_with(file_path)
        mock_file_system_adapter.get_file_size.assert_called_once_with(file_path)
        mock_json_validator.validate_file_size.assert_called_once_with(file_size)
        mock_file_system_adapter.read_json.assert_called_once_with(file_path)
        mock_json_validator.validate_json_string.assert_called_once_with(json_content)
        mock_json_data_class.assert_called_once_with(
            content=json_data,
            source_path=file_path,
            size_bytes=file_size
        )
        mock_json_data.analyze_structure.assert_called_once()
        mock_json_validator.validate_json_data_object.assert_called_once_with(mock_json_data)


def test_validate_json_file_not_found(mock_file_validator):
    """Tests that validate_json_file correctly handles a file not found scenario."""
    # Set up mock file_validator to return a file not found error
    file_path = "nonexistent_file.json"
    file_not_found_error = ErrorResponse(
        message=f"File not found: {file_path}",
        error_code="E001",
        category=ErrorCategory.INPUT_ERROR,
        severity=MagicMock(),
        source_component="FileValidator"
    )
    mock_file_validator.validate_json_file.return_value = (False, [file_not_found_error])
    
    # Create a ValidationService with our mock
    validator = ValidationService()
    validator._file_validator = mock_file_validator
    
    # Call the method being tested
    result, errors, json_data = validator.validate_json_file(file_path)
    
    # Verify the method returns file not found error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == file_not_found_error
    assert json_data is None
    
    # Verify the mock was called correctly
    mock_file_validator.validate_json_file.assert_called_once_with(file_path)


def test_validate_json_file_invalid_json(mock_file_validator, mock_json_validator, mock_file_system_adapter):
    """Tests that validate_json_file correctly handles invalid JSON content."""
    # Set up mock objects
    file_path = "invalid_json.json"
    file_size = 1024  # 1KB
    json_content = '{invalid json'
    json_parse_error = ErrorResponse(
        message="Invalid JSON syntax: expecting property name",
        error_code="E005",
        category=ErrorCategory.PARSING_ERROR,
        severity=MagicMock(),
        source_component="JSONValidator"
    )
    
    # Configure mock_file_validator to return successful validation
    mock_file_validator.validate_json_file.return_value = (True, [])
    
    # Configure mock_file_system_adapter to return file size and content
    mock_file_system_adapter.get_file_size.return_value = file_size
    mock_file_system_adapter.read_json.return_value = json_content
    
    # Configure mock_json_validator to return file size success but JSON parse error
    mock_json_validator.validate_file_size.return_value = (True, None)
    mock_json_validator.validate_json_string.return_value = (False, json_parse_error, None)
    
    # Create a ValidationService with our mocks
    validator = ValidationService()
    validator._file_validator = mock_file_validator
    validator._json_validator = mock_json_validator
    validator._file_system_adapter = mock_file_system_adapter
    
    # Call the method being tested
    result, errors, json_data = validator.validate_json_file(file_path)
    
    # Verify the method returns JSON parse error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == json_parse_error
    assert json_data is None
    
    # Verify the mocks were called correctly
    mock_file_validator.validate_json_file.assert_called_once_with(file_path)
    mock_file_system_adapter.get_file_size.assert_called_once_with(file_path)
    mock_json_validator.validate_file_size.assert_called_once_with(file_size)
    mock_file_system_adapter.read_json.assert_called_once_with(file_path)
    mock_json_validator.validate_json_string.assert_called_once_with(json_content)


def test_validate_json_file_too_large(mock_file_validator, mock_json_validator, mock_file_system_adapter):
    """Tests that validate_json_file correctly handles files that exceed the size limit."""
    # Set up mock objects
    file_path = "too_large.json"
    file_size = 10 * 1024 * 1024  # 10MB
    file_size_error = ErrorResponse(
        message="File too large",
        error_code="E003",
        category=ErrorCategory.VALIDATION_ERROR,
        severity=MagicMock(),
        source_component="JSONValidator"
    )
    
    # Configure mock_file_validator to return successful validation
    mock_file_validator.validate_json_file.return_value = (True, [])
    
    # Configure mock_file_system_adapter to return file size
    mock_file_system_adapter.get_file_size.return_value = file_size
    
    # Configure mock_json_validator to return file size error
    mock_json_validator.validate_file_size.return_value = (False, file_size_error)
    
    # Create a ValidationService with our mocks
    validator = ValidationService()
    validator._file_validator = mock_file_validator
    validator._json_validator = mock_json_validator
    validator._file_system_adapter = mock_file_system_adapter
    
    # Call the method being tested
    result, errors, json_data = validator.validate_json_file(file_path)
    
    # Verify the method returns file size error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == file_size_error
    assert json_data is None
    
    # Verify the mocks were called correctly
    mock_file_validator.validate_json_file.assert_called_once_with(file_path)
    mock_file_system_adapter.get_file_size.assert_called_once_with(file_path)
    mock_json_validator.validate_file_size.assert_called_once_with(file_size)
    

def test_validate_json_string_success(mock_json_validator, flat_json):
    """Tests that validate_json_string correctly validates a valid JSON string."""
    # Set up mock objects
    json_string = str(flat_json).replace("'", '"')
    
    # Configure mock_json_validator to return successful validation
    mock_json_validator.validate_json_string.return_value = (True, None, flat_json)
    mock_json_validator.validate_json_data_object.return_value = (True, [])
    
    # Create a mock JSONData instance for the return value
    mock_json_data = MagicMock(spec=JSONData)
    
    # Patch the JSONData class to return our mock instance
    with patch('src.backend.services.validation_service.JSONData', return_value=mock_json_data) as mock_json_data_class:
        # Create a ValidationService with our mock
        validator = ValidationService()
        validator._json_validator = mock_json_validator
        
        # Call the method being tested
        result, errors, json_data_result = validator.validate_json_string(json_string)
        
        # Verify the method returns successful validation
        assert result is True
        assert errors == []
        assert json_data_result == mock_json_data
        
        # Verify the mocks were called correctly
        mock_json_validator.validate_json_string.assert_called_once_with(json_string)
        mock_json_data_class.assert_called_once()
        mock_json_data.analyze_structure.assert_called_once()
        mock_json_validator.validate_json_data_object.assert_called_once_with(mock_json_data)


def test_validate_json_string_invalid_syntax(mock_json_validator, invalid_json):
    """Tests that validate_json_string correctly handles invalid JSON syntax."""
    # Set up mock objects
    json_parse_error = ErrorResponse(
        message="Invalid JSON syntax: expecting property name",
        error_code="E005",
        category=ErrorCategory.PARSING_ERROR,
        severity=MagicMock(),
        source_component="JSONValidator"
    )
    
    # Configure mock_json_validator to return parsing error
    mock_json_validator.validate_json_string.return_value = (False, json_parse_error, None)
    
    # Create a ValidationService with our mock
    validator = ValidationService()
    validator._json_validator = mock_json_validator
    
    # Call the method being tested
    result, errors, json_data = validator.validate_json_string(invalid_json)
    
    # Verify the method returns JSON parse error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == json_parse_error
    assert json_data is None
    
    # Verify the mock was called correctly
    mock_json_validator.validate_json_string.assert_called_once_with(invalid_json)


def test_validate_output_path_success(mock_file_validator):
    """Tests that validate_output_path correctly validates a valid output path."""
    # Set up mock objects
    output_path = "valid/output/path.xlsx"
    
    # Configure mock_file_validator to return successful validation
    mock_file_validator.validate_output_path.return_value = (True, None)
    
    # Create a ValidationService with our mock
    validator = ValidationService()
    validator._file_validator = mock_file_validator
    
    # Call the method being tested
    result, error = validator.validate_output_path(output_path)
    
    # Verify the method returns successful validation
    assert result is True
    assert error is None
    
    # Verify the mock was called correctly
    mock_file_validator.validate_output_path.assert_called_once_with(output_path)


def test_validate_output_path_invalid(mock_file_validator):
    """Tests that validate_output_path correctly handles an invalid output path."""
    # Set up mock objects
    output_path = "invalid/path"
    path_error = ErrorResponse(
        message="Permission denied: Cannot write to directory",
        error_code="E004",
        category=ErrorCategory.INPUT_ERROR,
        severity=MagicMock(),
        source_component="FileValidator"
    )
    
    # Configure mock_file_validator to return validation error
    mock_file_validator.validate_output_path.return_value = (False, path_error)
    
    # Create a ValidationService with our mock
    validator = ValidationService()
    validator._file_validator = mock_file_validator
    
    # Call the method being tested
    result, error = validator.validate_output_path(output_path)
    
    # Verify the method returns path error
    assert result is False
    assert error == path_error
    
    # Verify the mock was called correctly
    mock_file_validator.validate_output_path.assert_called_once_with(output_path)


def test_get_json_validation_warnings(mock_json_validator, nested_json_data):
    """Tests that get_json_validation_warnings correctly returns warnings for JSON data."""
    # Set up mock objects
    warning1 = {
        "warning_type": "deep_nesting",
        "message": "Deep nesting detected (5 levels) approaching the limit of 10",
        "severity": "medium"
    }
    warning2 = {
        "warning_type": "large_arrays",
        "message": "Large arrays detected which might impact performance",
        "severity": "medium"
    }
    warnings = [warning1, warning2]
    
    # Configure mock_json_validator to return warnings
    mock_json_validator.get_validation_warnings.return_value = warnings
    
    # Create a ValidationService with our mock
    validator = ValidationService()
    validator._json_validator = mock_json_validator
    
    # Call the method being tested
    result = validator.get_json_validation_warnings(nested_json_data)
    
    # Verify the method returns the warnings
    assert result == warnings
    
    # Verify the mock was called correctly
    mock_json_validator.get_validation_warnings.assert_called_once_with(nested_json_data)


def test_validate_conversion_parameters_success():
    """Tests that validate_conversion_parameters correctly validates valid conversion parameters."""
    # Create a ValidationService with mocked methods
    validator = ValidationService()
    
    # Mock validate_json_file and validate_output_path methods
    validator.validate_json_file = MagicMock(return_value=(True, [], MagicMock()))
    validator.validate_output_path = MagicMock(return_value=(True, None))
    
    # Call the method being tested
    input_path = "valid.json"
    output_path = "valid.xlsx"
    result, errors = validator.validate_conversion_parameters(input_path, output_path)
    
    # Verify the method returns successful validation
    assert result is True
    assert errors == []
    
    # Verify the mocked methods were called correctly
    validator.validate_json_file.assert_called_once_with(input_path)
    validator.validate_output_path.assert_called_once_with(output_path)


def test_validate_conversion_parameters_invalid_input():
    """Tests that validate_conversion_parameters correctly handles an invalid input file."""
    # Create a ValidationService with mocked methods
    validator = ValidationService()
    
    # Create a file not found error
    input_error = ErrorResponse(
        message="File not found",
        error_code="E001",
        category=ErrorCategory.INPUT_ERROR,
        severity=MagicMock(),
        source_component="ValidationService"
    )
    
    # Mock validate_json_file to return an error
    validator.validate_json_file = MagicMock(return_value=(False, [input_error], None))
    
    # Call the method being tested
    input_path = "invalid.json"
    output_path = "valid.xlsx"
    result, errors = validator.validate_conversion_parameters(input_path, output_path)
    
    # Verify the method returns validation error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == input_error
    
    # Verify the mocked method was called correctly
    validator.validate_json_file.assert_called_once_with(input_path)


def test_validate_conversion_parameters_invalid_output():
    """Tests that validate_conversion_parameters correctly handles an invalid output path."""
    # Create a ValidationService with mocked methods
    validator = ValidationService()
    
    # Create an output path error
    output_error = ErrorResponse(
        message="Permission denied: Cannot write to directory",
        error_code="E004",
        category=ErrorCategory.INPUT_ERROR,
        severity=MagicMock(),
        source_component="ValidationService"
    )
    
    # Mock validate_json_file to return success but validate_output_path to return an error
    validator.validate_json_file = MagicMock(return_value=(True, [], MagicMock()))
    validator.validate_output_path = MagicMock(return_value=(False, output_error))
    
    # Call the method being tested
    input_path = "valid.json"
    output_path = "invalid.xlsx"
    result, errors = validator.validate_conversion_parameters(input_path, output_path)
    
    # Verify the method returns validation error
    assert result is False
    assert len(errors) == 1
    assert errors[0] == output_error
    
    # Verify the mocked methods were called correctly
    validator.validate_json_file.assert_called_once_with(input_path)
    validator.validate_output_path.assert_called_once_with(output_path)


def test_create_validation_summary(nested_json_data):
    """Tests that create_validation_summary correctly generates a summary with warnings and recommendations."""
    # Create a ValidationService with mocked get_json_validation_warnings
    validator = ValidationService()
    
    # Define mock warnings
    warnings = [
        {
            "warning_type": "deep_nesting",
            "message": "Deep nesting detected",
            "severity": "medium"
        },
        {
            "warning_type": "large_arrays",
            "message": "Large arrays detected",
            "severity": "medium"
        }
    ]
    
    # Mock get_json_validation_warnings to return our warnings
    validator.get_json_validation_warnings = MagicMock(return_value=warnings)
    
    # Call the method being tested
    summary = validator.create_validation_summary(nested_json_data)
    
    # Verify the summary contains the expected structure information
    assert "structure" in summary
    assert "is_nested" in summary["structure"]
    assert "max_nesting_level" in summary["structure"]
    assert "contains_arrays" in summary["structure"]
    assert "array_paths" in summary["structure"]
    assert "complexity_score" in summary["structure"]
    assert "complexity_level" in summary["structure"]
    assert "flattening_strategy" in summary["structure"]
    
    # Verify the summary contains the warnings
    assert "warnings" in summary
    assert summary["warnings"] == warnings
    
    # Verify the summary contains recommendations
    assert "recommendations" in summary
    assert isinstance(summary["recommendations"], list)
    
    # Verify the method called get_json_validation_warnings
    validator.get_json_validation_warnings.assert_called_once_with(nested_json_data)


def test_integration_with_real_json_data(flat_json, nested_json, temp_dir):
    """Integration test that validates real JSON data without mocking dependencies."""
    import json
    
    # Create a ValidationService with real dependencies
    validator = ValidationService()
    
    # Create temporary JSON files
    flat_json_path = os.path.join(temp_dir, "flat.json")
    nested_json_path = os.path.join(temp_dir, "nested.json")
    output_path = os.path.join(temp_dir, "output.xlsx")
    
    with open(flat_json_path, "w") as f:
        json.dump(flat_json, f)
    
    with open(nested_json_path, "w") as f:
        json.dump(nested_json, f)
    
    # Test flat JSON validation
    flat_result, flat_errors, flat_json_data = validator.validate_json_file(flat_json_path)
    assert flat_result is True
    assert flat_errors == []
    assert flat_json_data is not None
    assert flat_json_data.is_analyzed
    
    # Test nested JSON validation
    nested_result, nested_errors, nested_json_data = validator.validate_json_file(nested_json_path)
    assert nested_result is True
    assert nested_errors == []
    assert nested_json_data is not None
    assert nested_json_data.is_analyzed
    
    # Test output path validation
    output_result, output_error = validator.validate_output_path(output_path)
    assert output_result is True
    assert output_error is None
    
    # Test conversion parameters validation
    params_result, params_errors = validator.validate_conversion_parameters(flat_json_path, output_path)
    assert params_result is True
    assert params_errors == []


# Fixtures for mocks
@pytest.fixture
def mock_file_validator():
    return MagicMock(spec=FileValidator)

@pytest.fixture
def mock_json_validator():
    return MagicMock(spec=JSONValidator)

@pytest.fixture
def mock_file_system_adapter():
    return MagicMock(spec=FileSystemAdapter)

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir