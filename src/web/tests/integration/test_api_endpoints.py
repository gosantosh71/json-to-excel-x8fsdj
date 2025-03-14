import pytest  # pytest: 7.3.0+ - Testing framework for writing and running tests
import json  # json: built-in - For parsing and validating JSON responses
import io  # io: built-in - For creating in-memory file objects
import os  # os: built-in - For file path operations
from unittest.mock import Mock  # unittest.mock: built-in - For mocking dependencies in tests

from ..app import create_app  # src/web/app.py - For creating a test Flask application instance
from ..fixtures.file_fixtures import create_test_json_file_storage  # src/web/tests/fixtures/file_fixtures.py - For creating test JSON file objects
from ..fixtures.file_fixtures import create_invalid_json_file_storage  # src/web/tests/fixtures/file_fixtures.py - For creating invalid JSON file objects for testing error handling
from ..fixtures.file_fixtures import create_oversized_file_storage  # src/web/tests/fixtures/file_fixtures.py - For creating oversized file objects for testing validation
from ..fixtures.job_fixtures import create_test_job  # src/web/tests/fixtures/job_fixtures.py - For creating test conversion job objects
from ..fixtures.job_fixtures import create_completed_job  # src/web/tests/fixtures/job_fixtures.py - For creating completed conversion job objects
from ..fixtures.job_fixtures import create_failed_job  # src/web/tests/fixtures/job_fixtures.py - For creating failed conversion job objects
from ..models.job_status import JobStatusEnum  # src/web/models/job_status.py - For checking job status in tests

TEST_UPLOAD_ENDPOINT = '/api/uploads'
TEST_CONVERSION_ENDPOINT = '/api/conversion/jobs'
TEST_HEALTH_ENDPOINT = '/api/health'


@pytest.fixture
def test_app():
    """Fixture that creates a Flask test client for API testing"""
    app = create_app('testing')  # Create a Flask application using create_app('testing')
    app.config['TESTING'] = True  # Configure the app for testing
    client = app.test_client()  # Create a test client from the app
    with app.app_context():  # Set up an application context
        yield client  # Yield the test client for use in tests
    # Clean up after tests are complete


def test_health_endpoint(test_app):
    """Tests that the health check endpoint returns a successful response"""
    response = test_app.get(TEST_HEALTH_ENDPOINT)  # Make a GET request to the health endpoint
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'status' in data and data['status'] == 'ok'  # Assert that the response contains 'status' key with value 'ok'


def test_upload_endpoint_success(test_app, create_test_json_file_storage):
    """Tests successful file upload to the upload endpoint"""
    test_file = create_test_json_file_storage  # Create a test JSON file using the fixture
    data = {'file': (test_file.stream, test_file.filename, test_file.content_type)}
    response = test_app.post(TEST_UPLOAD_ENDPOINT, data=data, content_type='multipart/form-data')  # Make a POST request to the upload endpoint with the file
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is True  # Assert that the response contains 'success' key with value True
    assert 'file_id' in data and data['file_id']  # Assert that the response contains 'file_id' key with a non-empty value
    assert 'file' in data  # Assert that the response contains file details


def test_upload_endpoint_invalid_json(test_app, create_invalid_json_file_storage):
    """Tests error handling when uploading invalid JSON"""
    test_file = create_invalid_json_file_storage  # Create an invalid JSON file using the fixture
    data = {'file': (test_file.stream, test_file.filename, test_file.content_type)}
    response = test_app.post(TEST_UPLOAD_ENDPOINT, data=data, content_type='multipart/form-data')  # Make a POST request to the upload endpoint with the file
    assert response.status_code == 400  # Assert that the response status code is 400
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about invalid JSON


def test_upload_endpoint_oversized_file(test_app, create_oversized_file_storage):
    """Tests error handling when uploading a file that exceeds size limits"""
    test_file = create_oversized_file_storage  # Create an oversized file using the fixture
    data = {'file': (test_file.stream, test_file.filename, test_file.content_type)}
    response = test_app.post(TEST_UPLOAD_ENDPOINT, data=data, content_type='multipart/form-data')  # Make a POST request to the upload endpoint with the file
    assert response.status_code == 413  # Assert that the response status code is 413
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about file size


def test_upload_endpoint_no_file(test_app):
    """Tests error handling when no file is provided to the upload endpoint"""
    response = test_app.post(TEST_UPLOAD_ENDPOINT, content_type='multipart/form-data')  # Make a POST request to the upload endpoint without a file
    assert response.status_code == 400  # Assert that the response status code is 400
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about missing file


def test_conversion_endpoint_success(test_app, monkeypatch):
    """Tests successful creation of a conversion job"""
    mock_job_manager = Mock()
    mock_job_manager.create_job.return_value = (Mock(), None)  # Mock the JobManager to return a successful job creation
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    data = {'file_id': 'test_file_id', 'sheet_name': 'test_sheet'}  # Create form data with file_id and conversion options
    response = test_app.post(TEST_CONVERSION_ENDPOINT, data=data)  # Make a POST request to the conversion endpoint with the form data
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is True  # Assert that the response contains 'success' key with value True
    assert 'job_id' in data and data['job_id']  # Assert that the response contains 'job_id' key with a non-empty value
    assert 'job' in data  # Assert that the response contains job details


def test_conversion_endpoint_missing_file_id(test_app):
    """Tests error handling when file_id is missing from conversion request"""
    data = {'sheet_name': 'test_sheet'}  # Create form data without file_id
    response = test_app.post(TEST_CONVERSION_ENDPOINT, data=data)  # Make a POST request to the conversion endpoint with the form data
    assert response.status_code == 400  # Assert that the response status code is 400
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about missing file_id


def test_job_status_endpoint(test_app, monkeypatch, create_test_job):
    """Tests retrieving job status from the status endpoint"""
    test_job = create_test_job()  # Create a test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the test job
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get(f'/api/conversion/jobs/{test_job.job_id}/status')  # Make a GET request to the job status endpoint with the job_id
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is True  # Assert that the response contains 'success' key with value True
    assert 'status' in data and data['status']['status'] == 'pending'  # Assert that the response contains 'status' key with the expected job status
    assert 'progress_percentage' in data  # Assert that the response contains 'progress_percentage' key


def test_job_status_endpoint_not_found(test_app, monkeypatch):
    """Tests error handling when job_id is not found"""
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (None, Mock())  # Mock the JobManager to return a not found error
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get('/api/conversion/jobs/nonexistent_job_id/status')  # Make a GET request to the job status endpoint with a non-existent job_id
    assert response.status_code == 404  # Assert that the response status code is 404
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about job not found


def test_job_result_endpoint_completed(test_app, monkeypatch, create_completed_job):
    """Tests retrieving results for a completed job"""
    test_job = create_completed_job()  # Create a completed test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the completed job
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get(f'/api/conversion/jobs/{test_job.job_id}/result')  # Make a GET request to the job result endpoint with the job_id
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is True  # Assert that the response contains 'success' key with value True
    assert 'download_url' in data and data['download_url']  # Assert that the response contains 'download_url' key with a non-empty value
    assert 'file_info' in data  # Assert that the response contains result details


def test_job_result_endpoint_not_completed(test_app, monkeypatch, create_test_job):
    """Tests error handling when requesting results for a job that is not completed"""
    test_job = create_test_job()  # Create a pending test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the pending job
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get(f'/api/conversion/jobs/{test_job.job_id}/result')  # Make a GET request to the job result endpoint with the job_id
    assert response.status_code == 400  # Assert that the response status code is 400
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about job not completed


def test_job_result_endpoint_failed(test_app, monkeypatch, create_failed_job):
    """Tests error handling when requesting results for a failed job"""
    test_job = create_failed_job()  # Create a failed test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the failed job
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get(f'/api/conversion/jobs/{test_job.job_id}/result')  # Make a GET request to the job result endpoint with the job_id
    assert response.status_code == 400  # Assert that the response status code is 400
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about job failure


def test_download_endpoint(test_app, monkeypatch, create_completed_job):
    """Tests downloading an Excel file from the download endpoint"""
    test_job = create_completed_job()  # Create a completed test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the completed job
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    mock_send_file = Mock(return_value='test_response')
    monkeypatch.setattr('src.web.api.conversion_api.send_file', mock_send_file)  # Mock the send_file function to return a test response
    response = test_app.get(f'/api/conversion/jobs/{test_job.job_id}/download')  # Make a GET request to the download endpoint with the job_id
    assert response.status_code == 200  # Assert that the response status code is 200
    mock_send_file.assert_called_once()  # Assert that the response contains the expected content type for Excel
    assert 'test_response' == response.data.decode()  # Assert that the response contains the expected content disposition header


def test_download_endpoint_not_found(test_app, monkeypatch):
    """Tests error handling when job_id is not found for download"""
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (None, Mock())  # Mock the JobManager to return a not found error
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.get('/api/conversion/jobs/nonexistent_job_id/download')  # Make a GET request to the download endpoint with a non-existent job_id
    assert response.status_code == 404  # Assert that the response status code is 404
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is False  # Assert that the response contains 'success' key with value False
    assert 'error' in data  # Assert that the response contains an error message about job not found


def test_cancel_job_endpoint(test_app, monkeypatch, create_test_job):
    """Tests cancelling a job through the cancel endpoint"""
    test_job = create_test_job()  # Create a test job using the fixture
    mock_job_manager = Mock()
    mock_job_manager.get_job.return_value = (test_job, None)  # Mock the JobManager to return the test job
    mock_job_manager.cancel_job.return_value = (True, None)  # Mock the JobManager to return successful cancellation
    monkeypatch.setattr('src.web.api.conversion_api.job_manager', mock_job_manager)
    response = test_app.post(f'/api/conversion/jobs/{test_job.job_id}/cancel')  # Make a POST request to the cancel endpoint with the job_id
    assert response.status_code == 200  # Assert that the response status code is 200
    data = json.loads(response.data.decode('utf-8'))  # Parse the response data as JSON
    assert 'success' in data and data['success'] is True  # Assert that the response contains 'success' key with value True
    assert 'message' in data  # Assert that the response contains a message about successful cancellation