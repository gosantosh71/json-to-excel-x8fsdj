import json  # v: built-in - For parsing and validating JSON responses
import unittest.mock  # v: built-in - For creating mock objects and patching functions

import pytest  # v: latest - Testing framework for writing and executing tests
from flask.testing import FlaskClient  # flask: 2.3.0+ - For simulating HTTP requests to the Flask application

from src.web.exceptions.file_exceptions import FileEmptyException  # src/web/exceptions/file_exceptions.py - Exception class for empty file errors
from src.web.exceptions.file_exceptions import FileSizeExceededException  # src/web/exceptions/file_exceptions.py - Exception class for file size exceeded errors
from src.web.exceptions.file_exceptions import FileUploadException  # src/web/exceptions/file_exceptions.py - Exception class for file upload errors
from src.web.exceptions.file_exceptions import InvalidJSONFileException  # src/web/exceptions/file_exceptions.py - Exception class for invalid JSON file errors
from src.web.exceptions.job_exceptions import JobNotFoundException  # src/web/exceptions/job_exceptions.py - Exception class for job not found errors
from src.web.exceptions.job_exceptions import JobProcessingException  # src/web/exceptions/job_exceptions.py - Exception class for job processing errors
from src.web.tests.conftest import app  # src/web/tests/conftest.py - Flask application fixture for testing
from src.web.tests.conftest import client  # src/web/tests/conftest.py - Flask test client fixture for making HTTP requests
from src.web.tests.conftest import mock_conversion_service  # src/web/tests/conftest.py - Mock ConversionService for testing conversion operations
from src.web.tests.conftest import mock_file_service  # src/web/tests/conftest.py - Mock FileService for testing file operations
from src.web.tests.conftest import mock_job_manager  # src/web/tests/conftest.py - Mock JobManager for testing job operations
from src.web.tests.fixtures.file_fixtures import create_empty_file_storage  # src/web/tests/fixtures/file_fixtures.py - Create empty file storage for testing empty file errors
from src.web.tests.fixtures.file_fixtures import create_invalid_json_file_storage  # src/web/tests/fixtures/file_fixtures.py - Create invalid JSON file storage for testing error handling
from src.web.tests.fixtures.file_fixtures import create_oversized_file_storage  # src/web/tests/fixtures/file_fixtures.py - Create oversized file storage for testing size limit errors
from src.web.tests.fixtures.file_fixtures import create_test_file_storage  # src/web/tests/fixtures/file_fixtures.py - Create mock file storage objects for testing


@pytest.mark.functional
def test_file_upload_error_handling(client: FlaskClient, mock_file_service: unittest.mock.MagicMock) -> None:
    """Tests that file upload errors are properly handled and appropriate error messages are returned."""
    # Configure mock_file_service.upload_file to raise FileUploadException
    mock_file_service.upload_file.side_effect = FileUploadException("Upload failed")

    # Make a POST request to '/api/upload' with a test file
    response = client.post('/api/upload', data={'file': create_test_file_storage()})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Parse the response JSON and verify it contains an error message
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "Upload failed" in data["error"]["message"]

    # Verify the error category is 'INPUT_ERROR'
    assert data["error"]["category"] == "input_error"


@pytest.mark.functional
def test_file_size_exceeded_error(client: FlaskClient, mock_file_service: unittest.mock.MagicMock,
                                  create_oversized_file_storage: create_oversized_file_storage) -> None:
    """Tests that file size limit errors are properly handled and appropriate error messages are returned."""
    # Configure mock_file_service.upload_file to raise FileSizeExceededException
    mock_file_service.upload_file.side_effect = FileSizeExceededException(
        filename="oversized.json", file_size=6000000, max_size=5000000
    )

    # Make a POST request to '/api/upload' with an oversized file
    response = client.post('/api/upload', data={'file': create_oversized_file_storage})

    # Verify the response status code is 413
    assert response.status_code == 413

    # Parse the response JSON and verify it contains an error message about file size
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "exceeds maximum allowed size" in data["error"]["message"]

    # Verify the error category is 'VALIDATION_ERROR'
    assert data["error"]["category"] == "validation_error"

    # Verify the response includes the maximum allowed file size
    assert "max_size" in data["error"]["context"]


@pytest.mark.functional
def test_empty_file_error(client: FlaskClient, mock_file_service: unittest.mock.MagicMock,
                        create_empty_file_storage: create_empty_file_storage) -> None:
    """Tests that empty file errors are properly handled and appropriate error messages are returned."""
    # Configure mock_file_service.upload_file to raise FileEmptyException
    mock_file_service.upload_file.side_effect = FileEmptyException(filename="empty.json")

    # Make a POST request to '/api/upload' with an empty file
    response = client.post('/api/upload', data={'file': create_empty_file_storage})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Parse the response JSON and verify it contains an error message about empty file
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "is empty" in data["error"]["message"]

    # Verify the error category is 'VALIDATION_ERROR'
    assert data["error"]["category"] == "validation_error"


@pytest.mark.functional
def test_invalid_json_error(client: FlaskClient, mock_file_service: unittest.mock.MagicMock,
                           create_invalid_json_file_storage: create_invalid_json_file_storage) -> None:
    """Tests that invalid JSON file errors are properly handled and appropriate error messages are returned."""
    # Configure mock_file_service.upload_file to raise InvalidJSONFileException
    mock_file_service.upload_file.side_effect = InvalidJSONFileException(filename="invalid.json", error_details="Invalid syntax")

    # Make a POST request to '/api/upload' with an invalid JSON file
    response = client.post('/api/upload', data={'file': create_invalid_json_file_storage})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Parse the response JSON and verify it contains an error message about invalid JSON
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "contains invalid JSON" in data["error"]["message"]

    # Verify the error category is 'VALIDATION_ERROR'
    assert data["error"]["category"] == "validation_error"

    # Verify the response includes details about the JSON parsing error
    assert "error_details" in data["error"]["context"]


@pytest.mark.functional
def test_job_not_found_error(client: FlaskClient, mock_job_manager: unittest.mock.MagicMock) -> None:
    """Tests that job not found errors are properly handled and appropriate error messages are returned."""
    # Configure mock_job_manager.get_job to raise JobNotFoundException
    mock_job_manager.get_job.side_effect = JobNotFoundException(job_id="nonexistent-job-id")

    # Make a GET request to '/api/jobs/nonexistent-job-id'
    response = client.get('/api/jobs/nonexistent-job-id/status')

    # Verify the response status code is 404
    assert response.status_code == 404

    # Parse the response JSON and verify it contains an error message about job not found
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "not found" in data["error"]["message"]

    # Verify the error category is 'INPUT_ERROR'
    assert data["error"]["category"] == "input_error"


@pytest.mark.functional
def test_job_processing_error(client: FlaskClient, mock_conversion_service: unittest.mock.MagicMock,
                             mock_job_manager: unittest.mock.MagicMock) -> None:
    """Tests that job processing errors are properly handled and appropriate error messages are returned."""
    # Configure mock_conversion_service.process_conversion_job to raise JobProcessingException
    mock_conversion_service.process_conversion_job.side_effect = JobProcessingException(job_id="test-job", message="Processing failed")

    # Make a POST request to '/api/convert' with valid conversion parameters
    response = client.post('/api/convert', data={"file_id": "test-file", "options": "{}"})

    # Verify the response status code is 500
    assert response.status_code == 500

    # Parse the response JSON and verify it contains an error message about processing failure
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "Processing failed" in data["error"]["message"]

    # Verify the error category is 'SYSTEM_ERROR'
    assert data["error"]["category"] == "system_error"


@pytest.mark.functional
def test_error_page_rendering(client: FlaskClient, mock_file_service: unittest.mock.MagicMock) -> None:
    """Tests that the error page is properly rendered with the correct error information."""
    # Configure mock_file_service.upload_file to raise InvalidJSONFileException
    mock_file_service.upload_file.side_effect = InvalidJSONFileException(filename="invalid.json", error_details="Invalid syntax")

    # Make a POST request to '/convert' with an invalid JSON file (non-API endpoint)
    response = client.post('/convert', data={'json_file': create_test_file_storage()})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Verify the response contains HTML for the error page
    assert "<html>" in response.get_data(as_text=True)
    assert "<title>Error</title>" in response.get_data(as_text=True)

    # Verify the error page contains the error message
    assert "contains invalid JSON" in response.get_data(as_text=True)

    # Verify the error page contains troubleshooting information
    assert "Check your JSON file for syntax errors" in response.get_data(as_text=True)


@pytest.mark.functional
def test_api_error_json_response(client: FlaskClient, mock_file_service: unittest.mock.MagicMock) -> None:
    """Tests that API endpoints return properly formatted JSON error responses."""
    # Configure mock_file_service.upload_file to raise FileUploadException
    mock_file_service.upload_file.side_effect = FileUploadException("Upload failed")

    # Make a POST request to '/api/upload' with a test file
    response = client.post('/api/upload', data={'file': create_test_file_storage()})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Verify the response content type is 'application/json'
    assert response.content_type == 'application/json'

    # Parse the response JSON and verify it has the expected structure
    data = json.loads(response.get_data(as_text=True))
    assert "success" in data
    assert "error" in data
    assert "message" in data["error"]
    assert "category" in data["error"]
    assert "severity" in data["error"]
    assert "status_code" not in data["error"]  # Status code should not be in error details

    # Verify the JSON contains error message, category, severity, and status fields
    assert data["success"] is False
    assert data["error"]["message"] == "Upload failed"
    assert data["error"]["category"] == "input_error"
    assert data["error"]["severity"] == "error"


@pytest.mark.functional
def test_validation_error_details(client: FlaskClient) -> None:
    """Tests that validation errors include detailed information about the validation failure."""
    # Make a POST request to '/api/convert' with missing required parameters
    response = client.post('/api/convert', data={})

    # Verify the response status code is 400
    assert response.status_code == 400

    # Parse the response JSON and verify it contains validation error details
    data = json.loads(response.get_data(as_text=True))
    assert "error" in data
    assert "message" in data["error"]
    assert "category" in data["error"]
    assert data["error"]["category"] == "validation_error"

    # Verify the response includes specific field validation errors
    assert "file_id" in data["error"]["message"]


@pytest.mark.functional
def test_error_recovery_suggestions(client: FlaskClient, mock_file_service: unittest.mock.MagicMock) -> None:
    """Tests that error responses include helpful recovery suggestions for users."""
    # Configure mock_file_service.upload_file to raise InvalidJSONFileException with specific error details
    mock_file_service.upload_file.side_effect = InvalidJSONFileException(
        filename="invalid.json", error_details="Missing quote in line 5"
    )

    # Make a POST request to '/api/upload' with an invalid JSON file
    response = client.post('/api/upload', data={'file': create_test_file_storage()})

    # Parse the response JSON
    data = json.loads(response.get_data(as_text=True))

    # Verify the response includes recovery suggestions
    assert "error" in data
    assert "resolution_steps" in data["error"]
    assert len(data["error"]["resolution_steps"]) > 0

    # Verify the suggestions are relevant to the specific error type
    assert "Check that your JSON file has valid syntax" in data["error"]["resolution_steps"]