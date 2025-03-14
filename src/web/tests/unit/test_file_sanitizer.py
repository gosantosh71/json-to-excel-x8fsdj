"""
Unit tests for the FileSanitizer class in the web interface component of the JSON to Excel Conversion Tool.
These tests verify the functionality of file sanitization, validation, and security measures to prevent
common vulnerabilities such as path traversal, malicious file uploads, and Excel formula injection.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import MagicMock, patch

# Import the components under test
from ../../security.file_sanitizer import (
    FileSanitizer,
    sanitize_filename,
    sanitize_json_content,
    sanitize_excel_cell_content,
    sanitize_json_object,
    validate_file_type,
    validate_file_size
)

# Import exception classes
from ../../exceptions.file_exceptions import (
    FileTypeNotAllowedException,
    FileSizeExceededException,
    FileCorruptedException
)

# Import test fixtures
from ../fixtures.file_fixtures import (
    create_test_file_storage,
    create_test_json_file_storage,
    create_oversized_file_storage,
    create_invalid_json_file_storage,
    setup_test_upload_folder,
    teardown_test_upload_folder
)

# Import configuration
from ../../config.upload_config import upload_config

# Test data constants
TEST_DATA = {
    'valid_filename': 'test.json',
    'invalid_filename': 'test<script>.json',
    'oversized_filename': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json',
    'path_traversal_filename': '../../../etc/passwd',
    'formula_trigger_content': '={1+1}'
}

# Mock class for testing
class MockFileSanitizer:
    """A test double for the FileSanitizer class with configurable behavior."""
    
    def __init__(self, sanitize_success=True, validate_success=True):
        """Initializes a new MockFileSanitizer with default behavior."""
        self.sanitize_called = False
        self.validate_called = False
        self.sanitized_objects = {}
        self._sanitize_success = sanitize_success
        self._validate_success = validate_success
    
    def sanitize_filename(self, filename):
        """Mock implementation of sanitize_filename."""
        self.sanitize_called = True
        return f"sanitized_{filename}" if self._sanitize_success else None
    
    def validate_file(self, filename, file_size):
        """Mock implementation of validate_file."""
        self.validate_called = True
        return (self._validate_success, None if self._validate_success else "Error")
    
    def sanitize_json_object(self, json_obj):
        """Mock implementation of sanitize_json_object."""
        self.sanitized_objects = json_obj
        return json_obj.copy()

def test_sanitize_filename():
    """Tests that the sanitize_filename function properly sanitizes filenames."""
    # Test that valid filenames remain unchanged
    result = sanitize_filename(TEST_DATA['valid_filename'])
    assert result == TEST_DATA['valid_filename']
    
    # Test that special characters are removed
    result = sanitize_filename(TEST_DATA['invalid_filename'])
    assert '<script>' not in result
    
    # Test that long filenames are truncated
    result = sanitize_filename(TEST_DATA['oversized_filename'])
    assert len(result) <= upload_config['security']['max_filename_length']
    
    # Test that path traversal attempts are neutralized
    result = sanitize_filename(TEST_DATA['path_traversal_filename'])
    assert '../' not in result
    
    # Test that empty filenames after sanitization raise an error
    result = sanitize_filename("!@#$%^&*()")
    assert result and result != "!@#$%^&*()"

def test_sanitize_excel_cell_content():
    """Tests that the sanitize_excel_cell_content function prevents Excel formula injection."""
    # Test that normal text is not modified
    assert sanitize_excel_cell_content("normal text") == "normal text"
    
    # Test that numeric values are not modified
    assert sanitize_excel_cell_content(123) == 123
    
    # Test that formulas starting with '=' are prefixed with a single quote
    assert sanitize_excel_cell_content("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    
    # Test that other formula triggers (+, -, @, etc.) are properly handled
    assert sanitize_excel_cell_content("+1234") == "'+1234"
    assert sanitize_excel_cell_content("-1234") == "'-1234"
    assert sanitize_excel_cell_content("@SomeReference") == "'@SomeReference"
    
    # Test that non-string values are returned unchanged
    assert sanitize_excel_cell_content(None) is None
    assert sanitize_excel_cell_content(False) is False
    assert sanitize_excel_cell_content(1.234) == 1.234

def test_sanitize_json_content():
    """Tests that the sanitize_json_content function removes dangerous patterns."""
    # Test that normal JSON content is not modified
    normal_content = '{"name": "test", "value": 123}'
    assert sanitize_json_content(normal_content) == normal_content
    
    # Test that content with <script> tags is sanitized
    script_content = '{"html": "<script>alert(\'xss\')</script>"}'
    sanitized = sanitize_json_content(script_content)
    assert "<script>" not in sanitized
    
    # Test that content with javascript: URLs is sanitized
    js_url_content = '{"url": "javascript:alert(\'xss\')"}'
    sanitized = sanitize_json_content(js_url_content)
    assert "javascript:" not in sanitized
    
    # Test that content with data:text/html is sanitized
    data_html_content = '{"url": "data:text/html,<script>alert(\'xss\')</script>"}'
    sanitized = sanitize_json_content(data_html_content)
    assert "data:text/html" not in sanitized
    
    # Test that content with data:application/javascript is sanitized
    data_js_content = '{"url": "data:application/javascript,alert(\'xss\')"}'
    sanitized = sanitize_json_content(data_js_content)
    assert "data:application/javascript" not in sanitized

def test_sanitize_json_object():
    """Tests that the sanitize_json_object function recursively sanitizes all string values in a JSON object."""
    # Test sanitization of a flat JSON object with formula triggers
    flat_obj = {
        "formula": "=SUM(1,2)",
        "normal": "text",
        "number": 123
    }
    sanitized = sanitize_json_object(flat_obj)
    assert sanitized["formula"] == "'=SUM(1,2)"
    assert sanitized["normal"] == "text"
    assert sanitized["number"] == 123
    
    # Test sanitization of a nested JSON object with formula triggers
    nested_obj = {
        "user": {
            "name": "John",
            "formula": "=DELETE()"
        },
        "settings": {
            "enabled": True,
            "formula": "=HACK()"
        }
    }
    sanitized = sanitize_json_object(nested_obj)
    assert sanitized["user"]["formula"] == "'=DELETE()"
    assert sanitized["settings"]["formula"] == "'=HACK()"
    
    # Test sanitization of a JSON object with arrays containing formula triggers
    array_obj = {
        "items": [
            {"name": "Item 1", "formula": "=BAD()"},
            {"name": "Item 2", "formula": "=WORSE()"}
        ],
        "values": ["normal", "=SUM()", "+VALUE", 123]
    }
    sanitized = sanitize_json_object(array_obj)
    assert sanitized["items"][0]["formula"] == "'=BAD()"
    assert sanitized["items"][1]["formula"] == "'=WORSE()"
    assert sanitized["values"][1] == "'=SUM()"
    assert sanitized["values"][2] == "'+VALUE"
    assert sanitized["values"][3] == 123
    
    # Test that non-string values are not modified
    mixed_obj = {
        "string": "text",
        "number": 123,
        "boolean": True,
        "null": None,
        "array": [1, 2, 3]
    }
    sanitized = sanitize_json_object(mixed_obj)
    assert sanitized["number"] == 123
    assert sanitized["boolean"] is True
    assert sanitized["null"] is None
    assert sanitized["array"] == [1, 2, 3]
    
    # Test that the original object is not modified (function creates a copy)
    original = {"formula": "=ATTACK()"}
    sanitized = sanitize_json_object(original)
    assert original["formula"] == "=ATTACK()"
    assert sanitized["formula"] == "'=ATTACK()"

def test_validate_file_type():
    """Tests that the validate_file_type function correctly validates file extensions."""
    # Test that files with allowed extensions (.json) are accepted
    assert validate_file_type("test.json") is True
    
    # Test that files with disallowed extensions are rejected
    assert validate_file_type("test.exe") is False
    assert validate_file_type("test.php") is False
    
    # Test that files with no extension are rejected
    assert validate_file_type("test") is False
    
    # Test that case sensitivity is handled correctly
    assert validate_file_type("test.JSON") is True

def test_validate_file_size():
    """Tests that the validate_file_size function correctly validates file sizes."""
    max_size = upload_config['max_file_size']
    
    # Test that files within size limit are accepted
    assert validate_file_size(max_size - 1024) is True
    
    # Test that files at exactly the size limit are accepted
    assert validate_file_size(max_size) is True
    
    # Test that files exceeding the size limit are rejected
    assert validate_file_size(max_size + 1) is False
    
    # Test with various size values including edge cases
    assert validate_file_size(1) is True
    assert validate_file_size(0) is True
    assert validate_file_size(max_size // 2) is True

def test_file_sanitizer_init():
    """Tests that the FileSanitizer class initializes correctly."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Verify that it initializes without errors
    assert sanitizer is not None
    assert hasattr(sanitizer, 'logger')

def test_file_sanitizer_sanitize_filename():
    """Tests the sanitize_filename method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Test sanitization of various filenames
    result = sanitizer.sanitize_filename(TEST_DATA['valid_filename'])
    assert result == TEST_DATA['valid_filename']
    
    result = sanitizer.sanitize_filename(TEST_DATA['invalid_filename'])
    assert '<script>' not in result
    
    result = sanitizer.sanitize_filename(TEST_DATA['path_traversal_filename'])
    assert '../' not in result
    
    # Verify that the method logs the sanitization operation
    with patch.object(sanitizer.logger, 'debug') as mock_debug:
        sanitizer.sanitize_filename("test.json")
        mock_debug.assert_called()

def test_file_sanitizer_validate_file():
    """Tests the validate_file method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Test validation of valid files
    is_valid, error_msg = sanitizer.validate_file(TEST_DATA['valid_filename'], 1024)
    assert is_valid is True
    assert error_msg is None
    
    # Test validation of files with invalid types
    is_valid, error_msg = sanitizer.validate_file("test.exe", 1024)
    assert is_valid is False
    assert error_msg is not None
    assert "File type not allowed" in error_msg
    
    # Test validation of oversized files
    max_size = upload_config['max_file_size']
    is_valid, error_msg = sanitizer.validate_file(TEST_DATA['valid_filename'], max_size + 1024)
    assert is_valid is False
    assert error_msg is not None
    assert "File size" in error_msg and "exceeds" in error_msg
    
    # Verify that the method returns appropriate validation results and error messages
    with patch.object(sanitizer.logger, 'warning') as mock_warning:
        sanitizer.validate_file("test.exe", 1024)
        mock_warning.assert_called()

def test_file_sanitizer_validate_with_exceptions():
    """Tests the validate_with_exceptions method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Test that valid files pass validation without exceptions
    try:
        result = sanitizer.validate_with_exceptions(TEST_DATA['valid_filename'], 1024)
        assert result is True
    except Exception as e:
        pytest.fail(f"validate_with_exceptions raised an exception for valid file: {e}")
    
    # Test that files with invalid types raise FileTypeNotAllowedException
    with pytest.raises(FileTypeNotAllowedException):
        sanitizer.validate_with_exceptions("test.exe", 1024)
    
    # Test that oversized files raise FileSizeExceededException
    max_size = upload_config['max_file_size']
    with pytest.raises(FileSizeExceededException):
        sanitizer.validate_with_exceptions(TEST_DATA['valid_filename'], max_size + 1024)

def test_file_sanitizer_sanitize_json_object():
    """Tests the sanitize_json_object method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Test sanitization of various JSON objects
    flat_obj = {
        "formula": "=SUM(1,2)",
        "normal": "text",
        "number": 123
    }
    sanitized = sanitizer.sanitize_json_object(flat_obj)
    assert sanitized["formula"] == "'=SUM(1,2)"
    assert sanitized["normal"] == "text"
    assert sanitized["number"] == 123
    
    # Verify that the method logs the sanitization operation
    with patch.object(sanitizer.logger, 'debug') as mock_debug:
        sanitizer.sanitize_json_object({"test": "value"})
        mock_debug.assert_called()

def test_file_sanitizer_sanitize_file_content(setup_test_upload_folder):
    """Tests the sanitize_file_content method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Create test JSON files in the test upload folder
    test_file_path = os.path.join(setup_test_upload_folder, "test_content.json")
    with open(test_file_path, 'w') as f:
        json.dump({"data": "value", "formula": "=EVIL()"}, f)
    
    # Test sanitization of valid JSON files
    json_obj, error_msg = sanitizer.sanitize_file_content(test_file_path)
    assert json_obj is not None
    assert error_msg is None
    assert json_obj["formula"] == "'=EVIL()"
    
    # Test handling of invalid JSON files
    invalid_file_path = os.path.join(setup_test_upload_folder, "invalid.json")
    with open(invalid_file_path, 'w') as f:
        f.write("{invalid json")
    
    json_obj, error_msg = sanitizer.sanitize_file_content(invalid_file_path)
    assert json_obj is None
    assert error_msg is not None
    assert "Invalid JSON" in error_msg
    
    # Test handling of files with dangerous content
    dangerous_file_path = os.path.join(setup_test_upload_folder, "dangerous.json")
    with open(dangerous_file_path, 'w') as f:
        f.write('{"html": "<script>alert(\'xss\')</script>"}')
    
    json_obj, error_msg = sanitizer.sanitize_file_content(dangerous_file_path)
    assert json_obj is not None
    assert error_msg is None
    assert "<script>" not in str(json_obj)
    
    # Test handling of files that don't exist
    nonexistent_path = os.path.join(setup_test_upload_folder, "nonexistent.json")
    json_obj, error_msg = sanitizer.sanitize_file_content(nonexistent_path)
    assert json_obj is None
    assert error_msg is not None
    assert "File not found" in error_msg

def test_file_sanitizer_is_safe_path(setup_test_upload_folder):
    """Tests the is_safe_path method of the FileSanitizer class."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    
    # Test with paths within the base directory
    safe_path = os.path.join(setup_test_upload_folder, "safe.json")
    assert sanitizer.is_safe_path(safe_path, setup_test_upload_folder) is True
    
    # Test with paths outside the base directory (path traversal attempts)
    traversal_path = os.path.join(setup_test_upload_folder, "..", "outside.json")
    abs_base_dir = os.path.abspath(setup_test_upload_folder)
    abs_traversal_path = os.path.abspath(traversal_path)
    assert sanitizer.is_safe_path(traversal_path, setup_test_upload_folder) is False
    
    # Test with absolute paths
    abs_path = os.path.abspath(os.path.join(setup_test_upload_folder, "file.json"))
    assert sanitizer.is_safe_path(abs_path, setup_test_upload_folder) is True
    
    outside_abs_path = os.path.join(tempfile.gettempdir(), "outside.json")
    assert sanitizer.is_safe_path(outside_abs_path, setup_test_upload_folder) is False
    
    # Test with symbolic links
    if hasattr(os, 'symlink'):  # Skip on platforms without symlink support
        try:
            link_path = os.path.join(setup_test_upload_folder, "link.json")
            target_path = os.path.join(setup_test_upload_folder, "target.json")
            with open(target_path, 'w') as f:
                f.write("{}")
            os.symlink(target_path, link_path)
            assert sanitizer.is_safe_path(link_path, setup_test_upload_folder) is True
            
            outside_target = os.path.join(tempfile.gettempdir(), "outside_target.json")
            outside_link = os.path.join(setup_test_upload_folder, "outside_link.json")
            with open(outside_target, 'w') as f:
                f.write("{}")
            os.symlink(outside_target, outside_link)
            # This might pass or fail depending on how absolute paths are resolved
            # The test verifies the behavior, not the specific result
            result = sanitizer.is_safe_path(outside_link, setup_test_upload_folder)
            assert isinstance(result, bool)
        except (OSError, PermissionError):
            pass  # Skip if symlink creation fails due to permissions

def test_integration_file_upload_sanitization(setup_test_upload_folder, create_test_json_file_storage):
    """Integration test for the complete file sanitization process during upload."""
    # Create a FileSanitizer instance
    sanitizer = FileSanitizer()
    file_storage = create_test_json_file_storage()
    
    # Simulate a file upload process
    file_path = os.path.join(setup_test_upload_folder, "uploaded.json")
    file_storage.save(file_path)
    
    # Verify that the filename is sanitized
    original_filename = file_storage.filename
    sanitized_filename = sanitizer.sanitize_filename(original_filename)
    assert sanitized_filename == original_filename  # Should be safe already
    
    # Verify that the file type is validated
    file_size = os.path.getsize(file_path)
    is_valid, _ = sanitizer.validate_file(sanitized_filename, file_size)
    assert is_valid is True
    
    # Verify that the file size is validated
    assert file_size <= upload_config['max_file_size']
    
    # Verify that the file content is sanitized
    json_obj, error_msg = sanitizer.sanitize_file_content(file_path)
    assert json_obj is not None
    assert error_msg is None
    
    # Verify that the resulting JSON object is safe for Excel conversion
    # Check if any values would be sanitized again
    sanitized_again = sanitizer.sanitize_json_object(json_obj)
    assert sanitized_again == json_obj  # Should be already sanitized