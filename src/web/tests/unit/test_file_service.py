"""
Unit tests for the FileService class which manages file operations in the web interface of the JSON to Excel Conversion Tool.
Tests cover file upload, retrieval, validation, deletion, and other file management operations.
"""

import pytest  # v: 7.3.0+
import os  # v: built-in
import uuid  # v: built-in
import datetime  # v: built-in
from unittest.mock import Mock, patch  # v: built-in

from ...services.file_service import FileService
from ...models.upload_file import UploadFile, UploadStatus
from ...utils.file_utils import FileManager
from ....backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..fixtures.file_fixtures import (
    create_test_file_storage,
    create_test_json_file_storage,
    create_oversized_file_storage,
    create_invalid_json_file_storage,
    create_test_upload_file,
    create_test_file_error,
    setup_test_upload_folder,
    teardown_test_upload_folder
)


def test_file_service_init():
    """Tests that the FileService initializes correctly with required dependencies."""
    # Create a new FileService instance
    service = FileService()
    
    # Assert that the _file_manager attribute is initialized
    assert hasattr(service, '_file_manager')
    assert isinstance(service._file_manager, FileManager)
    
    # Assert that the _uploads dictionary is empty
    assert hasattr(service, '_uploads')
    assert isinstance(service._uploads, dict)
    assert len(service._uploads) == 0


def test_upload_file_success(create_test_json_file_storage):
    """Tests successful file upload functionality."""
    # Create a mock FileManager
    mock_file_manager = Mock()
    
    # Configure the mock to return successful validation and file saving
    file_path = "/path/to/test.json"
    mock_file_manager.validate_file.return_value = (True, None)
    mock_file_manager.save_file.return_value = (file_path, None)
    
    # Create a FileService instance with the mocked FileManager
    service = FileService()
    service._file_manager = mock_file_manager
    
    # Mock UploadFile creation and validation
    file_id = str(uuid.uuid4())
    with patch('...models.upload_file.UploadFile.from_werkzeug_file') as mock_from_werkzeug:
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.file_id = file_id
        mock_upload_file.status = UploadStatus.PENDING
        mock_upload_file.validate.return_value = (True, None)
        mock_from_werkzeug.return_value = mock_upload_file
        
        # Call upload_file with the test file storage
        test_file = create_test_json_file_storage
        uploaded_file, error = service.upload_file(test_file)
        
        # Assert that the upload was successful
        assert uploaded_file is not None
        assert error is None
        
        # Assert that the returned UploadFile has the expected attributes
        assert uploaded_file.file_id == file_id
        
        # Assert that the file was added to the _uploads dictionary
        assert file_id in service._uploads
        assert service._uploads[file_id] == mock_upload_file


def test_upload_file_validation_failure(create_test_json_file_storage, create_test_file_error):
    """Tests file upload with validation failure."""
    # Create a mock FileManager
    mock_file_manager = Mock()
    
    # Configure the mock to return validation failure with error
    error_response = create_test_file_error
    mock_file_manager.validate_file.return_value = (False, error_response)
    
    # Create a FileService instance with the mocked FileManager
    service = FileService()
    service._file_manager = mock_file_manager
    
    # Call upload_file with the test file storage
    test_file = create_test_json_file_storage
    uploaded_file, error = service.upload_file(test_file)
    
    # Assert that the upload failed (returned None for file)
    assert uploaded_file is None
    
    # Assert that the error response matches the expected error
    assert error is error_response
    
    # Assert that no file was added to the _uploads dictionary
    assert len(service._uploads) == 0


def test_upload_file_save_failure(create_test_json_file_storage, create_test_file_error):
    """Tests file upload with save operation failure."""
    # Create a mock FileManager
    mock_file_manager = Mock()
    
    # Configure the mock to return successful validation but failed save operation
    error_response = create_test_file_error
    mock_file_manager.validate_file.return_value = (True, None)
    mock_file_manager.save_file.return_value = ("", error_response)
    
    # Create a FileService instance with the mocked FileManager
    service = FileService()
    service._file_manager = mock_file_manager
    
    # Call upload_file with the test file storage
    test_file = create_test_json_file_storage
    uploaded_file, error = service.upload_file(test_file)
    
    # Assert that the upload failed (returned None for file)
    assert uploaded_file is None
    
    # Assert that the error response matches the expected error
    assert error is error_response
    
    # Assert that no file was added to the _uploads dictionary
    assert len(service._uploads) == 0


def test_upload_file_json_validation_failure(create_test_json_file_storage):
    """Tests file upload with JSON validation failure."""
    # Create a mock FileManager with successful validation and save
    mock_file_manager = Mock()
    mock_file_manager.validate_file.return_value = (True, None)
    mock_file_manager.save_file.return_value = ("/path/to/test.json", None)
    
    # Create a mock UploadFile with validate method that returns False
    with patch('...models.upload_file.UploadFile.from_werkzeug_file') as mock_from_werkzeug:
        file_id = str(uuid.uuid4())
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.file_id = file_id
        mock_upload_file.validate.return_value = (False, ErrorResponse(
            message="Invalid JSON",
            error_code="JSON_PARSE_ERROR",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="UploadFile"
        ))
        mock_from_werkzeug.return_value = mock_upload_file
        
        # Create a FileService instance with the mocked FileManager
        service = FileService()
        service._file_manager = mock_file_manager
        
        # Call upload_file with the test file storage
        test_file = create_test_json_file_storage
        uploaded_file, error = service.upload_file(test_file)
        
        # Assert that the upload was successful but validation failed
        assert uploaded_file is mock_upload_file
        assert error is None
        
        # Assert that the UploadFile was added to _uploads with INVALID status
        assert file_id in service._uploads
        assert service._uploads[file_id] == mock_upload_file


def test_get_upload_success(create_test_upload_file):
    """Tests successful retrieval of an uploaded file."""
    # Create a FileService instance
    service = FileService()
    
    # Add the test upload file to the service's _uploads dictionary
    test_file = create_test_upload_file
    service._uploads[test_file.file_id] = test_file
    
    # Call get_upload with the file_id
    upload_file, error = service.get_upload(test_file.file_id)
    
    # Assert that the returned file matches the test upload file
    assert upload_file is test_file
    assert error is None


def test_get_upload_not_found():
    """Tests retrieval of a non-existent uploaded file."""
    # Create a FileService instance
    service = FileService()
    
    # Call get_upload with a non-existent file_id
    non_existent_id = str(uuid.uuid4())
    upload_file, error = service.get_upload(non_existent_id)
    
    # Assert that None was returned for the file
    assert upload_file is None
    
    # Assert that an error response was returned
    assert error is not None
    assert isinstance(error, ErrorResponse)
    
    # Assert that the error has INPUT_ERROR category
    assert error.category == ErrorCategory.INPUT_ERROR


def test_get_upload_path_success(create_test_upload_file):
    """Tests successful retrieval of an uploaded file path."""
    # Create a FileService instance
    service = FileService()
    
    # Add the test upload file to the service's _uploads dictionary
    test_file = create_test_upload_file
    service._uploads[test_file.file_id] = test_file
    
    # Call get_upload_path with the file_id
    file_path, error = service.get_upload_path(test_file.file_id)
    
    # Assert that the returned path matches the test upload file's file_path
    assert file_path == test_file.file_path
    assert error is None


def test_get_upload_path_not_found():
    """Tests retrieval of a non-existent uploaded file path."""
    # Create a FileService instance
    service = FileService()
    
    # Call get_upload_path with a non-existent file_id
    non_existent_id = str(uuid.uuid4())
    file_path, error = service.get_upload_path(non_existent_id)
    
    # Assert that None was returned for the path
    assert file_path is None
    
    # Assert that an error response was returned
    assert error is not None
    assert isinstance(error, ErrorResponse)
    
    # Assert that the error has INPUT_ERROR category
    assert error.category == ErrorCategory.INPUT_ERROR


def test_delete_upload_success(create_test_upload_file):
    """Tests successful deletion of an uploaded file."""
    # Create a mock for the UploadFile.delete_file method that returns True
    with patch.object(UploadFile, 'delete_file', return_value=True):
        # Create a FileService instance
        service = FileService()
        
        # Add the test upload file to the service's _uploads dictionary
        test_file = create_test_upload_file
        service._uploads[test_file.file_id] = test_file
        
        # Call delete_upload with the file_id
        success, error = service.delete_upload(test_file.file_id)
        
        # Assert that True was returned for success
        assert success is True
        assert error is None
        
        # Assert that the file was removed from the _uploads dictionary
        assert test_file.file_id not in service._uploads


def test_delete_upload_not_found():
    """Tests deletion of a non-existent uploaded file."""
    # Create a FileService instance
    service = FileService()
    
    # Call delete_upload with a non-existent file_id
    non_existent_id = str(uuid.uuid4())
    success, error = service.delete_upload(non_existent_id)
    
    # Assert that False was returned for success
    assert success is False
    
    # Assert that an error response was returned
    assert error is not None
    assert isinstance(error, ErrorResponse)
    
    # Assert that the error has INPUT_ERROR category
    assert error.category == ErrorCategory.INPUT_ERROR


def test_delete_upload_file_deletion_failure(create_test_upload_file):
    """Tests deletion when the physical file deletion fails."""
    # Create a mock for the UploadFile.delete_file method that returns False
    with patch.object(UploadFile, 'delete_file', return_value=False):
        # Create a FileService instance
        service = FileService()
        
        # Add the test upload file to the service's _uploads dictionary
        test_file = create_test_upload_file
        service._uploads[test_file.file_id] = test_file
        
        # Call delete_upload with the file_id
        success, error = service.delete_upload(test_file.file_id)
        
        # Assert that False was returned for success
        assert success is False
        
        # Assert that an error response was returned
        assert error is not None
        assert isinstance(error, ErrorResponse)
        
        # Assert that the file was not removed from the _uploads dictionary
        assert test_file.file_id in service._uploads


def test_list_uploads_all(create_test_upload_file):
    """Tests listing all uploaded files."""
    # Create multiple test upload files with different statuses
    service = FileService()
    
    file1 = create_test_upload_file(file_id="file1", status=UploadStatus.PENDING)
    file2 = create_test_upload_file(file_id="file2", status=UploadStatus.VALID)
    file3 = create_test_upload_file(file_id="file3", status=UploadStatus.INVALID)
    
    # Mock the to_dict method for each file
    file1.to_dict = Mock(return_value={"file_id": "file1", "status": "pending"})
    file2.to_dict = Mock(return_value={"file_id": "file2", "status": "valid"})
    file3.to_dict = Mock(return_value={"file_id": "file3", "status": "invalid"})
    
    # Add the test upload files to the service's _uploads dictionary
    service._uploads = {
        file1.file_id: file1,
        file2.file_id: file2,
        file3.file_id: file3
    }
    
    # Call list_uploads with no status filter
    result = service.list_uploads()
    
    # Assert that all uploaded files are returned
    assert len(result) == 3
    
    # Assert that each returned item is a dictionary representation of the upload file
    assert all(isinstance(item, dict) for item in result)
    
    # Check file IDs to ensure all files are returned
    file_ids = [item.get('file_id') for item in result]
    assert "file1" in file_ids
    assert "file2" in file_ids
    assert "file3" in file_ids


def test_list_uploads_by_status(create_test_upload_file):
    """Tests listing uploaded files filtered by status."""
    # Create multiple test upload files with different statuses
    service = FileService()
    
    file1 = create_test_upload_file(file_id="file1", status=UploadStatus.PENDING)
    file2 = create_test_upload_file(file_id="file2", status=UploadStatus.VALID)
    file3 = create_test_upload_file(file_id="file3", status=UploadStatus.VALID)
    
    # Mock the to_dict method for each file
    file1.to_dict = Mock(return_value={"file_id": "file1", "status": "pending"})
    file2.to_dict = Mock(return_value={"file_id": "file2", "status": "valid"})
    file3.to_dict = Mock(return_value={"file_id": "file3", "status": "valid"})
    
    # Add the test upload files to the service's _uploads dictionary
    service._uploads = {
        file1.file_id: file1,
        file2.file_id: file2,
        file3.file_id: file3
    }
    
    # Call list_uploads with a specific status filter
    result = service.list_uploads(status=UploadStatus.VALID)
    
    # Assert that only files with the matching status are returned
    assert len(result) == 2
    
    # Assert that each returned item is a dictionary representation of the upload file
    assert all(isinstance(item, dict) for item in result)
    
    # Check file IDs to ensure only files with VALID status are returned
    file_ids = [item.get('file_id') for item in result]
    assert "file1" not in file_ids
    assert "file2" in file_ids
    assert "file3" in file_ids


def test_validate_upload_success(create_test_upload_file):
    """Tests successful validation of an uploaded file."""
    # Create a mock for the UploadFile.validate method that returns (True, None)
    with patch.object(UploadFile, 'validate', return_value=(True, None)):
        # Create a FileService instance
        service = FileService()
        
        # Add the test upload file to the service's _uploads dictionary
        test_file = create_test_upload_file
        service._uploads[test_file.file_id] = test_file
        
        # Call validate_upload with the file_id
        success, error = service.validate_upload(test_file.file_id)
        
        # Assert that True was returned for success
        assert success is True
        assert error is None


def test_validate_upload_not_found():
    """Tests validation of a non-existent uploaded file."""
    # Create a FileService instance
    service = FileService()
    
    # Call validate_upload with a non-existent file_id
    non_existent_id = str(uuid.uuid4())
    success, error = service.validate_upload(non_existent_id)
    
    # Assert that False was returned for success
    assert success is False
    
    # Assert that an error response was returned
    assert error is not None
    assert isinstance(error, ErrorResponse)
    
    # Assert that the error has INPUT_ERROR category
    assert error.category == ErrorCategory.INPUT_ERROR


def test_validate_upload_validation_failure(create_test_upload_file, create_test_file_error):
    """Tests validation when the file validation fails."""
    # Create a mock for the UploadFile.validate method that returns (False, error_response)
    error_response = create_test_file_error
    with patch.object(UploadFile, 'validate', return_value=(False, error_response)):
        # Create a FileService instance
        service = FileService()
        
        # Add the test upload file to the service's _uploads dictionary
        test_file = create_test_upload_file
        service._uploads[test_file.file_id] = test_file
        
        # Call validate_upload with the file_id
        success, error = service.validate_upload(test_file.file_id)
        
        # Assert that False was returned for success
        assert success is False
        
        # Assert that the error response matches the expected error
        assert error is error_response


def test_get_file_details_success(create_test_upload_file):
    """Tests successful retrieval of file details."""
    # Create a mock for the UploadFile.get_file_details method that returns a details dictionary
    details = {
        "id": "test-id",
        "original_filename": "test.json",
        "file_size": 1024,
        "status": "valid"
    }
    
    with patch.object(UploadFile, 'get_file_details', return_value=details):
        # Create a FileService instance
        service = FileService()
        
        # Add the test upload file to the service's _uploads dictionary
        test_file = create_test_upload_file
        service._uploads[test_file.file_id] = test_file
        
        # Call get_file_details with the file_id
        result, error = service.get_file_details(test_file.file_id)
        
        # Assert that the returned details match the expected details
        assert result == details
        assert error is None


def test_get_file_details_not_found():
    """Tests retrieval of details for a non-existent file."""
    # Create a FileService instance
    service = FileService()
    
    # Call get_file_details with a non-existent file_id
    non_existent_id = str(uuid.uuid4())
    result, error = service.get_file_details(non_existent_id)
    
    # Assert that None was returned for the details
    assert result is None
    
    # Assert that an error response was returned
    assert error is not None
    assert isinstance(error, ErrorResponse)
    
    # Assert that the error has INPUT_ERROR category
    assert error.category == ErrorCategory.INPUT_ERROR


def test_cleanup_uploads_all(create_test_upload_file):
    """Tests cleanup of all uploaded files."""
    # Create multiple test upload files
    service = FileService()
    
    file1 = create_test_upload_file(file_id="file1", status=UploadStatus.PENDING)
    file2 = create_test_upload_file(file_id="file2", status=UploadStatus.VALID)
    file3 = create_test_upload_file(file_id="file3", status=UploadStatus.INVALID)
    
    # Create a mock for the UploadFile.delete_file method that returns True
    with patch.object(UploadFile, 'delete_file', return_value=True):
        # Add the test upload files to the service's _uploads dictionary
        service._uploads = {
            file1.file_id: file1,
            file2.file_id: file2,
            file3.file_id: file3
        }
        
        # Call cleanup_uploads with no filters
        result = service.cleanup_uploads()
        
        # Assert that all files were deleted
        assert len(service._uploads) == 0
        
        # Assert that the returned summary has the correct counts
        assert result["deleted"] == 3
        assert result["failed"] == 0
        assert result["skipped"] == 0
        assert result["total_processed"] == 3


def test_cleanup_uploads_by_status(create_test_upload_file):
    """Tests cleanup of uploaded files filtered by status."""
    # Create multiple test upload files with different statuses
    service = FileService()
    
    file1 = create_test_upload_file(file_id="file1", status=UploadStatus.PENDING)
    file2 = create_test_upload_file(file_id="file2", status=UploadStatus.VALID)
    file3 = create_test_upload_file(file_id="file3", status=UploadStatus.INVALID)
    
    # Create a mock for the UploadFile.delete_file method that returns True
    with patch.object(UploadFile, 'delete_file', return_value=True):
        # Add the test upload files to the service's _uploads dictionary
        service._uploads = {
            file1.file_id: file1,
            file2.file_id: file2,
            file3.file_id: file3
        }
        
        # Call cleanup_uploads with a specific status filter
        result = service.cleanup_uploads(status=UploadStatus.INVALID)
        
        # Assert that only files with the matching status were deleted
        assert len(service._uploads) == 2
        assert "file1" in service._uploads
        assert "file2" in service._uploads
        assert "file3" not in service._uploads
        
        # Assert that the returned summary has the correct counts
        assert result["deleted"] == 1
        assert result["failed"] == 0
        assert result["skipped"] == 2
        assert result["total_processed"] == 3


def test_cleanup_uploads_by_age(create_test_upload_file):
    """Tests cleanup of uploaded files filtered by age."""
    # Create multiple test upload files with different timestamps
    service = FileService()
    
    # Current file (created now)
    file1 = create_test_upload_file(file_id="file1")
    file1.upload_timestamp = datetime.datetime.now()
    
    # Old file (created 2 hours ago)
    file2 = create_test_upload_file(file_id="file2")
    file2.upload_timestamp = datetime.datetime.now() - datetime.timedelta(hours=2)
    
    # Older file (created 3 hours ago)
    file3 = create_test_upload_file(file_id="file3")
    file3.upload_timestamp = datetime.datetime.now() - datetime.timedelta(hours=3)
    
    # Create a mock for the UploadFile.delete_file method that returns True
    with patch.object(UploadFile, 'delete_file', return_value=True):
        # Add the test upload files to the service's _uploads dictionary
        service._uploads = {
            file1.file_id: file1,
            file2.file_id: file2,
            file3.file_id: file3
        }
        
        # Call cleanup_uploads with an age filter (files older than 1.5 hours)
        result = service.cleanup_uploads(older_than_minutes=90)
        
        # Assert that only files older than the specified age were deleted
        assert len(service._uploads) == 1
        assert "file1" in service._uploads
        assert "file2" not in service._uploads
        assert "file3" not in service._uploads
        
        # Assert that the returned summary has the correct counts
        assert result["deleted"] == 2
        assert result["failed"] == 0
        assert result["skipped"] == 1
        assert result["total_processed"] == 3


def test_get_upload_count(create_test_upload_file):
    """Tests retrieval of upload counts by status."""
    # Create multiple test upload files with different statuses
    service = FileService()
    
    file1 = create_test_upload_file(file_id="file1", status=UploadStatus.PENDING)
    file2 = create_test_upload_file(file_id="file2", status=UploadStatus.VALID)
    file3 = create_test_upload_file(file_id="file3", status=UploadStatus.VALID)
    file4 = create_test_upload_file(file_id="file4", status=UploadStatus.INVALID)
    file5 = create_test_upload_file(file_id="file5", status=UploadStatus.PROCESSED)
    file6 = create_test_upload_file(file_id="file6", status=UploadStatus.ERROR)
    
    # Add the test upload files to the service's _uploads dictionary
    service._uploads = {
        file1.file_id: file1,
        file2.file_id: file2,
        file3.file_id: file3,
        file4.file_id: file4,
        file5.file_id: file5,
        file6.file_id: file6
    }
    
    # Call get_upload_count
    counts = service.get_upload_count()
    
    # Assert that the returned counts match the expected counts for each status
    assert counts["total"] == 6
    assert counts["valid"] == 2
    assert counts["invalid"] == 1
    assert counts["pending"] == 1
    assert counts["processed"] == 1
    assert counts["error"] == 1