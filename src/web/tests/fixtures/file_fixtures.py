"""
Provides test fixtures for file-related tests in the web interface component of the JSON to Excel Conversion Tool.
These fixtures include mock file storage objects, sample file paths, and utility functions for setting up
and tearing down test environments for file operations.
"""

import os  # v: built-in
import shutil  # v: built-in
import tempfile  # v: built-in
import io  # v: built-in
import uuid  # v: built-in
import datetime  # v: built-in
from typing import Any, Dict, List, Optional  # v: built-in
import unittest.mock  # v: built-in
import pytest  # v: 7.3.0+

from ../../models.upload_file import UploadFile, UploadStatus
from ../../../backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ../../config.upload_config import upload_config

# Global constants for test paths
TEST_UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'json_to_excel_test_uploads')
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'sample_data')
FLAT_JSON_PATH = os.path.join(SAMPLE_DATA_DIR, 'flat.json')
NESTED_JSON_PATH = os.path.join(SAMPLE_DATA_DIR, 'nested.json')


class MockFileStorage:
    """
    A mock implementation of Werkzeug's FileStorage class for testing file uploads without web dependencies.
    """

    def __init__(self, filename: str, content: bytes, content_type: str = "application/json"):
        """
        Initializes a new MockFileStorage instance with the specified parameters.
        
        Args:
            filename: Name of the file
            content: Binary content of the file
            content_type: MIME type of the file
        """
        self.filename = filename
        self.stream = io.BytesIO(content)
        self.content_type = content_type
        self.content_length = len(content)

    def save(self, destination: str) -> None:
        """
        Simulates saving the file to the specified destination.
        
        Args:
            destination: Path where the file should be saved
        """
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as f:
            f.write(self.read())
            
    def read(self) -> bytes:
        """
        Reads and returns the content of the file.
        
        Returns:
            The content of the file
        """
        self.stream.seek(0)
        return self.stream.read()


@pytest.fixture
def setup_test_upload_folder() -> str:
    """
    Creates a temporary upload folder for testing file operations.
    
    Returns:
        Path to the created test upload folder
    """
    os.makedirs(TEST_UPLOAD_FOLDER, exist_ok=True)
    return TEST_UPLOAD_FOLDER


@pytest.fixture
def teardown_test_upload_folder(setup_test_upload_folder: str) -> None:
    """
    Removes the temporary upload folder after tests are complete.
    
    Args:
        setup_test_upload_folder: Path to the test upload folder
    """
    yield
    try:
        shutil.rmtree(TEST_UPLOAD_FOLDER)
    except (OSError, FileNotFoundError):
        pass


@pytest.fixture
def get_sample_json_path(file_type: str = "flat") -> str:
    """
    Returns the path to a sample JSON file for testing.
    
    Args:
        file_type: Type of JSON file ('flat' or 'nested')
        
    Returns:
        Path to the requested sample JSON file
    """
    if file_type == "flat":
        return FLAT_JSON_PATH
    elif file_type == "nested":
        return NESTED_JSON_PATH
    return FLAT_JSON_PATH  # Default to flat


@pytest.fixture
def create_test_file_error(
    message: str = "File error", 
    category: ErrorCategory = ErrorCategory.INPUT_ERROR, 
    code: int = 400
) -> ErrorResponse:
    """
    Creates an ErrorResponse object for file-related errors in tests.
    
    Args:
        message: Error message
        category: Error category
        code: Error code
        
    Returns:
        An ErrorResponse instance with the specified parameters
    """
    return ErrorResponse(
        message=message,
        error_code=str(code),
        category=category,
        severity=ErrorSeverity.ERROR,
        source_component="test_component",
        context={"test": True}
    )


@pytest.fixture
def create_test_upload_file(
    file_id: Optional[str] = None, 
    original_filename: str = "test.json", 
    file_path: Optional[str] = None, 
    file_size: int = 1024, 
    status: UploadStatus = UploadStatus.PENDING
) -> UploadFile:
    """
    Creates an UploadFile instance for testing file operations.
    
    Args:
        file_id: Unique identifier for the file
        original_filename: Original filename
        file_path: Path to the file
        file_size: Size of the file in bytes
        status: Upload status
        
    Returns:
        An UploadFile instance with the specified parameters
    """
    if file_id is None:
        file_id = str(uuid.uuid4())
    
    if file_path is None:
        file_path = os.path.join(TEST_UPLOAD_FOLDER, f"{file_id}_{original_filename}")
    
    return UploadFile(
        file_id=file_id,
        original_filename=original_filename,
        secure_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        content_type="application/json",
        status=status
    )


@pytest.fixture
def create_test_file_storage(
    filename: str = "test.json", 
    content: bytes = b'{"test": "data"}', 
    content_type: str = "application/json"
) -> MockFileStorage:
    """
    Creates a MockFileStorage instance for testing file uploads.
    
    Args:
        filename: Name of the file
        content: Content of the file
        content_type: MIME type of the file
        
    Returns:
        A MockFileStorage instance with the specified parameters
    """
    return MockFileStorage(filename, content, content_type)


@pytest.fixture
def create_test_json_file_storage(file_type: str = "flat") -> MockFileStorage:
    """
    Creates a MockFileStorage instance with valid JSON content for testing.
    
    Args:
        file_type: Type of JSON file ('flat' or 'nested')
        
    Returns:
        A MockFileStorage instance with JSON content
    """
    if file_type == "flat":
        file_path = FLAT_JSON_PATH
    else:
        file_path = NESTED_JSON_PATH
        
    with open(file_path, 'rb') as f:
        content = f.read()
    
    filename = os.path.basename(file_path)
    return MockFileStorage(filename, content, "application/json")


@pytest.fixture
def create_oversized_file_storage() -> MockFileStorage:
    """
    Creates a MockFileStorage instance that exceeds the maximum file size limit.
    
    Returns:
        A MockFileStorage instance with oversized content
    """
    # Generate content that's larger than the maximum file size
    max_size = upload_config["max_file_size"]
    content = b'{"data": "' + b'x' * (max_size + 1024) + b'"}'
    
    return MockFileStorage("oversized.json", content, "application/json")


@pytest.fixture
def create_invalid_json_file_storage() -> MockFileStorage:
    """
    Creates a MockFileStorage instance with invalid JSON content for testing error handling.
    
    Returns:
        A MockFileStorage instance with invalid JSON content
    """
    # Invalid JSON syntax
    content = b'{"test": "data", invalid_json}'
    
    return MockFileStorage("invalid.json", content, "application/json")


@pytest.fixture
def create_empty_file_storage() -> MockFileStorage:
    """
    Creates a MockFileStorage instance with empty content for testing error handling.
    
    Returns:
        A MockFileStorage instance with empty content
    """
    return MockFileStorage("empty.json", b'', "application/json")


@pytest.fixture
def mock_file_validator(is_valid: bool = True, error_response: Optional[ErrorResponse] = None) -> unittest.mock.Mock:
    """
    Creates a mock file validator function for testing.
    
    Args:
        is_valid: Whether the validation should pass
        error_response: Error response to return if validation fails
        
    Returns:
        A mock validator function with predetermined responses
    """
    mock_validator = unittest.mock.Mock()
    mock_validator.return_value = (is_valid, error_response)
    return mock_validator