import pytest  # v: 7.3.0+ - Testing framework for writing and running tests
import json  # v: built-in - For parsing and validating JSON responses
import os  # v: built-in - For file path operations in tests
from unittest.mock import MagicMock  # v: built-in - For mocking dependencies in tests

from ..conftest import client, app, setup_test_upload_folder, mock_file_service, FileService  # src/web/tests/conftest.py - Flask test client fixture for making HTTP requests
from ..fixtures.file_fixtures import create_test_json_file_storage, create_invalid_json_file_storage, create_oversized_file_storage, create_empty_file_storage  # src/web/tests/fixtures/file_fixtures.py - Fixtures to create mock file storage objects for testing
from '../../models/upload_file' import UploadStatus  # src/web/models/upload_file.py - Enum for tracking upload status in tests

API_UPLOAD_ENDPOINT = '/api/uploads'


def test_upload_valid_json_file(client, setup_test_upload_folder, create_test_json_file_storage):
    """
    Tests successful upload of a valid JSON file through the API endpoint.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage
    # Make a POST request to the upload endpoint with the file
    response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the response contains the expected file details
    assert 'file' in data
    # Assert that the file_id is present in the response
    assert 'fileId' in data['file']
    # Assert that the status is set to PENDING initially
    assert data['file']['status'] == UploadStatus.PENDING.value


def test_upload_invalid_json_file(client, setup_test_upload_folder, create_invalid_json_file_storage):
    """
    Tests error handling when uploading an invalid JSON file.
    """
    # Create a test invalid JSON file storage object
    test_file = create_invalid_json_file_storage
    # Make a POST request to the upload endpoint with the invalid file
    response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    # Assert that the response status code is 400
    assert response.status_code == 400
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions JSON validation
    assert 'error' in data and 'Invalid JSON format' in data['error']['message']


def test_upload_oversized_file(client, setup_test_upload_folder, create_oversized_file_storage):
    """
    Tests error handling when uploading a file that exceeds the size limit.
    """
    # Create a test oversized file storage object
    test_file = create_oversized_file_storage
    # Make a POST request to the upload endpoint with the oversized file
    response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    # Assert that the response status code is 413
    assert response.status_code == 413
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions file size limits
    assert 'error' in data and 'exceeds maximum allowed size' in data['error']['message']


def test_upload_empty_file(client, setup_test_upload_folder, create_empty_file_storage):
    """
    Tests error handling when uploading an empty file.
    """
    # Create a test empty file storage object
    test_file = create_empty_file_storage
    # Make a POST request to the upload endpoint with the empty file
    response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    # Assert that the response status code is 400
    assert response.status_code == 400
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions empty file
    assert 'error' in data and 'No file was uploaded or filename is empty' in data['error']['message']


def test_upload_no_file(client, setup_test_upload_folder):
    """
    Tests error handling when making an upload request without a file.
    """
    # Make a POST request to the upload endpoint without including a file
    response = client.post(API_UPLOAD_ENDPOINT)
    # Assert that the response status code is 400
    assert response.status_code == 400
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions missing file
    assert 'error' in data and 'No file part in the request' in data['error']['message']


def test_get_upload_success(client, setup_test_upload_folder, create_test_json_file_storage, mock_file_service):
    """
    Tests retrieving information about a previously uploaded file.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage
    # Upload the file to get a file_id
    upload_response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    upload_data = json.loads(upload_response.data.decode('utf-8'))
    file_id = upload_data['file']['fileId']
    # Make a GET request to retrieve the uploaded file information
    response = client.get(f'{API_UPLOAD_ENDPOINT}/{file_id}')
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the response contains the expected file details
    assert 'file' in data
    # Assert that the file_id matches the uploaded file
    assert data['file']['fileId'] == file_id


def test_get_upload_not_found(client, setup_test_upload_folder, mock_file_service):
    """
    Tests error handling when requesting a non-existent file.
    """
    # Configure mock_file_service.get_upload to return a not found error
    mock_file_service.get_upload.return_value = (None, ErrorResponse(message="File not found", error_code="FILE_NOT_FOUND", category="INPUT_ERROR", severity="ERROR", source_component="test"))
    # Make a GET request to retrieve a non-existent file
    response = client.get(f'{API_UPLOAD_ENDPOINT}/nonexistent_id')
    # Assert that the response status code is 404
    assert response.status_code == 404
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions file not found
    assert 'error' in data and 'File not found' in data['error']['message']


def test_validate_upload_success(client, setup_test_upload_folder, create_test_json_file_storage, mock_file_service):
    """
    Tests successful validation of a previously uploaded JSON file.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage
    # Upload the file to get a file_id
    upload_response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    upload_data = json.loads(upload_response.data.decode('utf-8'))
    file_id = upload_data['file']['fileId']
    # Configure mock_file_service.validate_upload to return success
    mock_file_service.validate_upload.return_value = (True, None)
    # Make a POST request to validate the uploaded file
    response = client.post(f'{API_UPLOAD_ENDPOINT}/{file_id}/validate')
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the validation status is VALID
    assert data['is_valid'] is True
    # Assert that the response contains validation details
    assert 'validation_details' in data


def test_validate_upload_invalid_json(client, setup_test_upload_folder, create_invalid_json_file_storage, mock_file_service):
    """
    Tests validation failure for an invalid JSON file.
    """
    # Create a test invalid JSON file storage object
    test_file = create_invalid_json_file_storage
    # Upload the file to get a file_id
    upload_response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    upload_data = json.loads(upload_response.data.decode('utf-8'))
    file_id = upload_data['file']['fileId']
    # Configure mock_file_service.validate_upload to return validation failure
    mock_file_service.validate_upload.return_value = (False, ErrorResponse(message="Invalid JSON", error_code="INVALID_JSON", category="VALIDATION_ERROR", severity="ERROR", source_component="test"))
    # Make a POST request to validate the uploaded file
    response = client.post(f'{API_UPLOAD_ENDPOINT}/{file_id}/validate')
    # Assert that the response status code is 400
    assert response.status_code == 400
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the validation status is INVALID
    assert data['is_valid'] is False
    # Assert that the error message mentions JSON validation issues
    assert 'error' in data and 'Invalid JSON' in data['error']['message']


def test_validate_upload_not_found(client, setup_test_upload_folder, mock_file_service):
    """
    Tests error handling when validating a non-existent file.
    """
    # Configure mock_file_service.validate_upload to return a not found error
    mock_file_service.validate_upload.return_value = (False, ErrorResponse(message="File not found", error_code="FILE_NOT_FOUND", category="INPUT_ERROR", severity="ERROR", source_component="test"))
    # Make a POST request to validate a non-existent file
    response = client.post(f'{API_UPLOAD_ENDPOINT}/nonexistent_id/validate')
    # Assert that the response status code is 404
    assert response.status_code == 404
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions file not found
    assert 'error' in data and 'File not found' in data['error']['message']


def test_delete_upload_success(client, setup_test_upload_folder, create_test_json_file_storage, mock_file_service):
    """
    Tests successful deletion of a previously uploaded file.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage
    # Upload the file to get a file_id
    upload_response = client.post(API_UPLOAD_ENDPOINT, data={'file': (test_file.stream, test_file.filename)})
    upload_data = json.loads(upload_response.data.decode('utf-8'))
    file_id = upload_data['file']['fileId']
    # Configure mock_file_service.delete_upload to return success
    mock_file_service.delete_upload.return_value = (True, None)
    # Make a DELETE request to delete the uploaded file
    response = client.delete(f'{API_UPLOAD_ENDPOINT}/{file_id}')
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the success message confirms deletion
    assert 'message' in data and 'File deleted successfully' in data['message']


def test_delete_upload_not_found(client, setup_test_upload_folder, mock_file_service):
    """
    Tests error handling when deleting a non-existent file.
    """
    # Configure mock_file_service.delete_upload to return a not found error
    mock_file_service.delete_upload.return_value = (False, ErrorResponse(message="File not found", error_code="FILE_NOT_FOUND", category="INPUT_ERROR", severity="ERROR", source_component="test"))
    # Make a DELETE request to delete a non-existent file
    response = client.delete(f'{API_UPLOAD_ENDPOINT}/nonexistent_id')
    # Assert that the response status code is 404
    assert response.status_code == 404
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates an error
    assert data['success'] is False
    # Assert that the error message mentions file not found
    assert 'error' in data and 'File not found' in data['error']['message']


def test_list_uploads_empty(client, setup_test_upload_folder, mock_file_service):
    """
    Tests listing uploads when no files have been uploaded.
    """
    # Configure mock_file_service.list_uploads to return an empty list
    mock_file_service.list_uploads.return_value = []
    # Make a GET request to list all uploads
    response = client.get(API_UPLOAD_ENDPOINT)
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the response contains an empty list of uploads
    assert 'uploads' in data and len(data['uploads']) == 0


def test_list_uploads_with_files(client, setup_test_upload_folder, mock_file_service):
    """
    Tests listing uploads when files have been uploaded.
    """
    # Create mock upload file data
    mock_data = [{'fileId': '1', 'originalFilename': 'test1.json'}, {'fileId': '2', 'originalFilename': 'test2.json'}]
    # Configure mock_file_service.list_uploads to return the mock data
    mock_file_service.list_uploads.return_value = mock_data
    # Make a GET request to list all uploads
    response = client.get(API_UPLOAD_ENDPOINT)
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the response contains the expected list of uploads
    assert 'uploads' in data and len(data['uploads']) == 2
    # Assert that the file details match the mock data
    assert data['uploads'][0]['fileId'] == '1' and data['uploads'][0]['originalFilename'] == 'test1.json'


def test_list_uploads_with_status_filter(client, setup_test_upload_folder, mock_file_service):
    """
    Tests listing uploads filtered by status.
    """
    # Create mock upload file data with different statuses
    mock_data = [
        {'fileId': '1', 'originalFilename': 'test1.json', 'status': UploadStatus.VALID.value},
        {'fileId': '2', 'originalFilename': 'test2.json', 'status': UploadStatus.INVALID.value},
        {'fileId': '3', 'originalFilename': 'test3.json', 'status': UploadStatus.VALID.value}
    ]
    # Configure mock_file_service.list_uploads to filter by status
    mock_file_service.list_uploads = MagicMock(side_effect=lambda status: [f for f in mock_data if f['status'] == status.value] if status else mock_data)
    # Make a GET request to list uploads with status=VALID filter
    response = client.get(f'{API_UPLOAD_ENDPOINT}?status={UploadStatus.VALID.value}')
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Parse the response JSON data
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the response indicates success
    assert data['success'] is True
    # Assert that the response contains only uploads with VALID status
    assert 'uploads' in data and len(data['uploads']) == 2
    assert all(f['status'] == UploadStatus.VALID.value for f in data['uploads'])
    # Make another request with status=INVALID filter
    response = client.get(f'{API_UPLOAD_ENDPOINT}?status={UploadStatus.INVALID.value}')
    data = json.loads(response.data.decode('utf-8'))
    # Assert that the filtered results are correct
    assert 'uploads' in data and len(data['uploads']) == 1
    assert data['uploads'][0]['status'] == UploadStatus.INVALID.value