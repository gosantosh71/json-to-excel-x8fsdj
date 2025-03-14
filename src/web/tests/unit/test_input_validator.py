"""
Unit tests for the InputValidator class and related functions in the web interface component of the JSON to Excel Conversion Tool.
This test module verifies the functionality of input validation, sanitization, and error handling for user inputs from the web interface.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from ../../security/input_validator import (
    InputValidator,
    sanitize_string,
    sanitize_path,
    sanitize_form_data,
    validate_and_sanitize_json
)
from ../../../backend/models/error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ../../exceptions/api_exceptions import ValidationException, BadRequestException
from ../fixtures/file_fixtures import MockFileStorage


def test_sanitize_string_basic():
    """Tests that the sanitize_string function properly sanitizes basic string inputs."""
    # Test sanitization of a simple string without special characters
    input_str = "Hello, world!"
    assert sanitize_string(input_str) == input_str
    
    # Test sanitization of strings with HTML tags when allow_html=False
    html_str = "<p>This is a <b>test</b></p>"
    sanitized = sanitize_string(html_str, allow_html=False)
    assert "<p>" not in sanitized
    assert "<b>" not in sanitized
    
    # Test sanitization of strings with script tags
    script_str = "<p>Text</p><script>alert('xss')</script>"
    sanitized_html_allowed = sanitize_string(script_str, allow_html=True)
    sanitized_html_not_allowed = sanitize_string(script_str, allow_html=False)
    
    assert "<script>" not in sanitized_html_allowed
    assert "alert('xss')" not in sanitized_html_allowed
    assert "<p>" in sanitized_html_allowed  # HTML is preserved when allowed
    
    assert "<script>" not in sanitized_html_not_allowed
    assert "alert('xss')" not in sanitized_html_not_allowed
    assert "<p>" not in sanitized_html_not_allowed  # HTML is removed when not allowed


def test_sanitize_string_xss_prevention():
    """Tests that the sanitize_string function prevents XSS attacks."""
    # Test sanitization of strings containing potential XSS payloads
    xss_strings = [
        "<script>alert('XSS')</script>",
        "<img src='x' onerror='alert(\"XSS\")'>",
        "<a href='javascript:alert(\"XSS\")'>Click me</a>",
        "javascript:alert('XSS')",
        "<SCRIPT>alert('XSS')</SCRIPT>",  # Case-insensitive
        "<script>alert(String.fromCharCode(88,83,83))</script>",  # Encoded
        "<div onmouseover='alert(\"XSS\")'>Hover me</div>"
    ]
    
    for xss_str in xss_strings:
        sanitized = sanitize_string(xss_str)
        assert "<script>" not in sanitized.lower()
        assert "javascript:" not in sanitized.lower()
        assert "alert" not in sanitized.lower()
        assert "onerror" not in sanitized.lower()
        assert "onmouseover" not in sanitized.lower()


def test_sanitize_string_html_allowed():
    """Tests that the sanitize_string function properly handles HTML when allowed."""
    # Test sanitization of strings with benign HTML when allow_html=True
    html_strings = [
        "<p>This is a paragraph</p>",
        "<div>This is a div with <span>a span inside</span></div>",
        "<ul><li>List item 1</li><li>List item 2</li></ul>"
    ]
    
    for html_str in html_strings:
        sanitized = sanitize_string(html_str, allow_html=True)
        # Check that the HTML structure is preserved
        assert "<p>" in sanitized if "<p>" in html_str else True
        assert "<div>" in sanitized if "<div>" in html_str else True
        assert "<span>" in sanitized if "<span>" in html_str else True
        assert "<ul>" in sanitized if "<ul>" in html_str else True
        assert "<li>" in sanitized if "<li>" in html_str else True
    
    # Test sanitization of strings with mixed benign HTML and script tags
    mixed_html = "<p>Safe content</p><script>alert('XSS')</script><div>More safe content</div>"
    sanitized = sanitize_string(mixed_html, allow_html=True)
    
    # Script tags should be removed, but other HTML preserved
    assert "<p>" in sanitized
    assert "<div>" in sanitized
    assert "<script>" not in sanitized
    assert "alert('XSS')" not in sanitized


def test_sanitize_string_edge_cases():
    """Tests that the sanitize_string function properly handles edge cases."""
    # Test sanitization of None input
    assert sanitize_string(None) == ""
    
    # Test sanitization of non-string inputs (numbers, booleans)
    assert sanitize_string(123) == "123"
    assert sanitize_string(True) == "True"
    assert sanitize_string({"key": "value"}) == "{'key': 'value'}"
    
    # Test sanitization of empty string
    assert sanitize_string("") == ""


def test_sanitize_path():
    """Tests that the sanitize_path function properly sanitizes file paths."""
    # Test sanitization of normal file paths
    normal_paths = [
        "/tmp/file.txt",
        "C:\\Users\\user\\Documents\\file.txt",
        "relative/path/file.json",
        "./file.json"
    ]
    
    for path in normal_paths:
        sanitized = sanitize_path(path)
        # Normal paths should generally remain unchanged
        assert path in sanitized
    
    # Test sanitization of paths with directory traversal attempts (..\/)
    traversal_paths = [
        "../../../etc/passwd",
        "..\\..\\Windows\\System32\\config\\SAM",
        "file.txt/../../../etc/shadow",
        "uploads/../../config/secrets.ini"
    ]
    
    for path in traversal_paths:
        sanitized = sanitize_path(path)
        assert "../" not in sanitized
        assert "..\\" not in sanitized
    
    # Test sanitization of paths with encoded directory traversal
    encoded_path = "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"  # URL-encoded ../../../etc/passwd
    sanitized = sanitize_path(encoded_path)
    assert "../" not in sanitized
    
    # Test sanitization of None and empty paths
    assert sanitize_path(None) == ""
    assert sanitize_path("") == ""


def test_sanitize_form_data():
    """Tests that the sanitize_form_data function properly sanitizes form data dictionaries."""
    # Create a test form data dictionary with various types of values
    form_data = {
        "name": "John Doe",
        "email": "<script>alert('XSS')</script>john@example.com",
        "message": "<p>This is a test message</p>",
        "age": 30,
        "subscribe": True,
        "options": ["option1", "<script>alert('XSS')</script>option2"],
        "nested": {
            "key1": "value1",
            "key2": "<script>alert('XSS')</script>value2",
            "html": "<p>HTML content</p>"
        }
    }
    
    # Test sanitization of the form data with default settings
    sanitized = sanitize_form_data(form_data)
    
    assert sanitized["name"] == "John Doe"
    assert "<script>" not in sanitized["email"]
    assert "alert" not in sanitized["email"]
    assert "john@example.com" in sanitized["email"]
    assert "<p>" not in sanitized["message"]
    assert "This is a test message" in sanitized["message"]
    assert sanitized["age"] == 30  # Non-string values should be preserved
    assert sanitized["subscribe"] is True  # Non-string values should be preserved
    
    # Check list sanitization
    assert "<script>" not in sanitized["options"][1]
    assert "alert" not in sanitized["options"][1]
    assert "option2" in sanitized["options"][1]
    
    # Check nested dict sanitization
    assert "<script>" not in sanitized["nested"]["key2"]
    assert "alert" not in sanitized["nested"]["key2"]
    assert "value2" in sanitized["nested"]["key2"]
    assert "<p>" not in sanitized["nested"]["html"]
    
    # Test with html_allowed_fields specified
    html_allowed_fields = ["message", "nested.html"]
    sanitized = sanitize_form_data(form_data, html_allowed_fields)
    
    assert "<p>" in sanitized["message"]  # HTML preserved in allowed field
    assert "<p>" in sanitized["nested"]["html"]  # HTML preserved in allowed nested field
    assert "<script>" not in sanitized["email"]  # Scripts still removed from non-allowed fields


@patch('../../security/input_validator.validate_json_structure')
def test_validate_and_sanitize_json(mock_validate):
    """Tests that the validate_and_sanitize_json function properly validates and sanitizes JSON data."""
    # Create a test JSON object with various types of values
    test_json = {
        "name": "John Doe",
        "email": "<script>alert('XSS')</script>john@example.com",
        "nested": {
            "key": "<img src='x' onerror='alert(\"XSS\")'>value"
        },
        "numbers": [1, 2, 3]
    }
    
    # Mock the validate_json_structure function to return success
    mock_validate.return_value = (True, None)
    
    # Test validation and sanitization of valid JSON
    is_valid, error, sanitized = validate_and_sanitize_json(test_json)
    
    assert is_valid is True
    assert error is None
    assert "<script>" not in sanitized["email"]
    assert "alert" not in sanitized["email"]
    assert "john@example.com" in sanitized["email"]
    assert "<img" not in sanitized["nested"]["key"]
    assert "onerror" not in sanitized["nested"]["key"]
    assert "value" in sanitized["nested"]["key"]
    assert sanitized["numbers"] == [1, 2, 3]  # Non-string values preserved
    
    # Mock the validate_json_structure function to return failure
    mock_error = ErrorResponse(
        message="JSON validation error",
        error_code="E001",
        category=ErrorCategory.VALIDATION_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="test"
    )
    mock_validate.return_value = (False, mock_error)
    
    # Test validation and sanitization of invalid JSON
    is_valid, error, sanitized = validate_and_sanitize_json(test_json)
    
    assert is_valid is False
    assert error is mock_error
    assert sanitized is None


def test_input_validator_init():
    """Tests that the InputValidator class initializes correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Verify the instance has the expected attributes
    assert hasattr(validator, '_form_validator')
    assert validator._form_validator is not None


def test_sanitize_input_method():
    """Tests that the sanitize_input method of InputValidator works correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Test sanitization of string input
    input_str = "<script>alert('XSS')</script>Hello, world!"
    sanitized = validator.sanitize_input(input_str)
    assert "<script>" not in sanitized
    assert "alert" not in sanitized
    assert "Hello, world!" in sanitized
    
    # Test sanitization of dictionary input
    input_dict = {
        "name": "John Doe",
        "email": "<script>alert('XSS')</script>john@example.com",
        "nested": {
            "key": "<img src='x' onerror='alert(\"XSS\")'>value"
        }
    }
    
    sanitized = validator.sanitize_input(input_dict)
    assert "<script>" not in sanitized["email"]
    assert "alert" not in sanitized["email"]
    assert "john@example.com" in sanitized["email"]
    assert "<img" not in sanitized["nested"]["key"]
    assert "onerror" not in sanitized["nested"]["key"]
    
    # Test sanitization of list input
    input_list = [
        "Normal text",
        "<script>alert('XSS')</script>",
        {"key": "<img src='x' onerror='alert(\"XSS\")'>value"}
    ]
    
    sanitized = validator.sanitize_input(input_list)
    assert sanitized[0] == "Normal text"
    assert "<script>" not in sanitized[1]
    assert "alert" not in sanitized[1]
    assert "<img" not in sanitized[2]["key"]
    assert "onerror" not in sanitized[2]["key"]
    
    # Test sanitization of None input
    assert validator.sanitize_input(None) is None


@patch('../../validators/form_validators.FormValidator.validate_conversion_form')
def test_validate_form_data_method(mock_validate):
    """Tests that the validate_form_data method of InputValidator works correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Mock the FormValidator.validate_conversion_form method
    # Test validation of valid form data
    mock_validate.return_value = (True, {})
    form_data = {"name": "John Doe", "email": "john@example.com"}
    
    is_valid, result = validator.validate_form_data(form_data)
    
    assert is_valid is True
    assert isinstance(result, dict)
    assert "name" in result
    assert result["name"] == "John Doe"
    
    # Test validation of form data with missing required fields
    error_dict = {
        "name": ErrorResponse(
            message="Required field 'name' is missing",
            error_code="E001",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="test"
        )
    }
    mock_validate.return_value = (False, error_dict)
    
    is_valid, result = validator.validate_form_data({"email": "john@example.com"}, required_fields=["name"])
    
    assert is_valid is False
    assert isinstance(result, dict)
    assert "name" in result
    assert isinstance(result["name"], ErrorResponse)
    
    # Test validation of form data with invalid values
    mock_validate.return_value = (False, error_dict)
    
    is_valid, result = validator.validate_form_data({"name": "<script>alert('XSS')</script>"})
    
    assert is_valid is False
    assert isinstance(result, dict)


@patch('../../security/input_validator.validate_and_sanitize_json')
def test_validate_json_payload_method(mock_validate):
    """Tests that the validate_json_payload method of InputValidator works correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Mock the validate_and_sanitize_json function
    # Test validation of valid JSON payload
    mock_validate.return_value = (True, None, {"name": "John Doe"})
    
    result = validator.validate_json_payload({"name": "John Doe"})
    
    assert isinstance(result, dict)
    assert "name" in result
    assert result["name"] == "John Doe"
    
    # Test validation of JSON payload with missing required fields
    with pytest.raises(ValidationException) as exc:
        validator.validate_json_payload({"email": "john@example.com"}, required_fields=["name"])
    
    assert "Required field 'name' is missing" in str(exc.value)
    
    # Test validation of invalid JSON structure
    mock_validate.return_value = (False, ErrorResponse(
        message="JSON validation error",
        error_code="E001",
        category=ErrorCategory.VALIDATION_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="test"
    ), None)
    
    with pytest.raises(ValidationException) as exc:
        validator.validate_json_payload({"name": "John Doe"})
    
    assert "JSON validation failed" in str(exc.value)


def test_validate_with_response_method():
    """Tests that the validate_with_response method of InputValidator works correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Mock the validate_form_data and validate_json_payload methods
    validator.validate_form_data = MagicMock(return_value=(True, {"name": "John Doe"}))
    validator.validate_json_payload = MagicMock(return_value={"name": "John Doe"})
    
    # Mock the ResponseFormatter.validation_result method
    with patch('../../utils/response_formatter.ResponseFormatter.validation_result') as mock_formatter:
        mock_formatter.return_value = {"success": True, "data": {"name": "John Doe"}}
        
        # Test validation with 'form' validation_type
        result = validator.validate_with_response({"name": "John Doe"}, 'form')
        
        validator.validate_form_data.assert_called_once()
        mock_formatter.assert_called_once()
        
        # Reset mocks
        validator.validate_form_data.reset_mock()
        mock_formatter.reset_mock()
        
        # Test validation with 'json' validation_type
        result = validator.validate_with_response({"name": "John Doe"}, 'json')
        
        validator.validate_json_payload.assert_called_once()
        mock_formatter.assert_called_once()
        
        # Test validation with invalid validation_type
        with patch('../../utils/response_formatter.ResponseFormatter.error') as mock_error:
            mock_error.return_value = {"success": False, "error": "Unknown validation type"}
            
            result = validator.validate_with_response({"name": "John Doe"}, 'invalid')
            
            mock_error.assert_called_once()


def test_validate_with_exception_method():
    """Tests that the validate_with_exception method of InputValidator works correctly."""
    # Create an instance of InputValidator
    validator = InputValidator()
    
    # Mock the validate_form_data and validate_json_payload methods
    validator.validate_form_data = MagicMock(return_value=(True, {"name": "John Doe"}))
    validator.validate_json_payload = MagicMock(return_value={"name": "John Doe"})
    
    # Test validation with 'form' validation_type for valid data
    result = validator.validate_with_exception({"name": "John Doe"}, 'form')
    
    validator.validate_form_data.assert_called_once()
    assert result == {"name": "John Doe"}
    
    # Reset mock
    validator.validate_form_data.reset_mock()
    
    # Test validation with 'form' validation_type for invalid data
    validator.validate_form_data = MagicMock(return_value=(False, {
        "name": ErrorResponse(
            message="Invalid name",
            error_code="E001",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="test"
        )
    }))
    
    with pytest.raises(ValidationException) as exc:
        validator.validate_with_exception({"name": "Invalid<script>"}, 'form')
    
    assert "Form validation failed" in str(exc.value)
    
    # Test validation with 'json' validation_type
    validator.validate_form_data.reset_mock()
    result = validator.validate_with_exception({"name": "John Doe"}, 'json')
    
    validator.validate_json_payload.assert_called_once()
    assert result == {"name": "John Doe"}
    
    # Test validation with invalid validation_type
    with pytest.raises(ValueError) as exc:
        validator.validate_with_exception({"name": "John Doe"}, 'invalid')
    
    assert "Unknown validation type" in str(exc.value)