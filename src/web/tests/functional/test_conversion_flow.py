import os  # v: built-in - For file path operations in tests
import json  # v: built-in - For parsing JSON responses from the API
import time  # v: built-in - For adding delays in tests when needed
import unittest.mock  # v: built-in - For mocking dependencies in tests

import pytest  # v: >=7.0.0 - Testing framework for writing and executing tests

from ..fixtures.conversion_fixtures import create_test_conversion_options, create_test_form_data, mock_conversion_service, create_conversion_result_summary
from ..fixtures.file_fixtures import create_test_file_storage, create_test_json_file_storage, create_invalid_json_file_storage, setup_test_upload_folder
from ..conftest import mock_file_service, mock_storage_service, mock_job_manager


@pytest.mark.functional
def test_successful_conversion_flow(client, mock_file_service, mock_storage_service, mock_job_manager,
                                    mock_conversion_service, create_test_json_file_storage, create_test_form_data,
                                    create_conversion_result_summary):
    """
    Tests the complete conversion flow from file upload to download with successful conversion.
    """
    # Set up mock services to return successful responses
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()
    # Create test form data for conversion options
    form_data = create_test_form_data()
    # Create a conversion result summary
    result_summary = create_conversion_result_summary()

    # Configure mock_job_manager to return a successful job
    mock_job_manager.create_job.return_value = (True, None)
    # Configure mock_conversion_service to return success and the result summary
    mock_conversion_service.process_conversion_job.return_value = True
    mock_conversion_service.convert_file.return_value = (True, result_summary, None)
    # Configure mock_storage_service to return a valid download path
    mock_storage_service.get_output_file.return_value = ("/path/to/download", "download.xlsx", None)

    # Send a POST request to /upload with the test file
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'completed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "completed"

    # Send a GET request to /download/{job_id} to download the result
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
            response = client.get(f"/api/conversion/jobs/{job_id}/download")

    # Verify the response status code is 200
    assert response.status_code == 200
    # Verify the response content type is 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.content_type == "application/vnd.ms-excel"
    # Verify the response has the correct Content-Disposition header
    assert f"attachment; filename=download.xlsx" in response.headers["Content-Disposition"]


@pytest.mark.functional
def test_conversion_flow_with_invalid_json(client, mock_file_service, mock_storage_service, mock_job_manager,
                                            mock_conversion_service, create_invalid_json_file_storage, create_test_form_data):
    """
    Tests the conversion flow with an invalid JSON file to verify proper error handling.
    """
    # Create an invalid JSON file storage object
    test_file = create_invalid_json_file_storage()
    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Configure mock_conversion_service to return validation failure
    mock_conversion_service.process_conversion_job.return_value = False
    mock_conversion_service.validate_conversion_input.return_value = (False, {}, {"message": "Invalid JSON"})

    # Send a POST request to /upload with the invalid file
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200 (upload succeeds)
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data})

    # Verify the response status code is 200 (job creation succeeds)
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'failed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "failed"
    # Verify the error message indicates JSON validation failure
    assert "JSON validation failed" in response.get_json()["status"]["message"]


@pytest.mark.functional
def test_conversion_flow_with_nested_json(client, mock_file_service, mock_storage_service, mock_job_manager,
                                           mock_conversion_service, create_test_json_file_storage, create_test_form_data,
                                           create_conversion_result_summary):
    """
    Tests the conversion flow with a nested JSON structure to verify proper flattening.
    """
    # Create a test JSON file storage object with nested structure
    test_file = create_test_json_file_storage(file_type="nested")
    # Create test form data for conversion options
    form_data = create_test_form_data()
    # Create a conversion result summary with flattened structure details
    result_summary = create_conversion_result_summary(rows=150, columns=12)

    # Configure mock services to return successful responses
    mock_conversion_service.process_conversion_job.return_value = True
    mock_conversion_service.convert_file.return_value = (True, result_summary, None)
    mock_storage_service.get_output_file.return_value = ("/path/to/download", "download.xlsx", None)

    # Send a POST request to /upload with the nested JSON file
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'completed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "completed"
    # Verify the result summary contains information about flattened nested structures
    # Send a GET request to /download/{job_id} to download the result
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
            response = client.get(f"/api/conversion/jobs/{job_id}/download")

    # Verify the response status code is 200
    assert response.status_code == 200


@pytest.mark.functional
def test_conversion_flow_with_array_handling_options(client, mock_file_service, mock_storage_service, mock_job_manager,
                                                      mock_conversion_service, create_test_json_file_storage, create_test_form_data,
                                                      create_conversion_result_summary):
    """
    Tests the conversion flow with different array handling options to verify proper array processing.
    """
    # Create a test JSON file storage object with arrays
    test_file = create_test_json_file_storage(file_type="nested")
    # Create test form data with array_handling set to 'expand'
    form_data_expand = create_test_form_data(array_handling="expand")
    # Create a conversion result summary for expanded arrays
    result_summary_expand = create_conversion_result_summary(rows=200, columns=12)

    # Configure mock services to return successful responses
    mock_conversion_service.process_conversion_job.return_value = True
    mock_conversion_service.convert_file.return_value = (True, result_summary_expand, None)
    mock_storage_service.get_output_file.return_value = ("/path/to/download_expand", "download_expand.xlsx", None)

    # Send a POST request to /upload with the JSON file containing arrays
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and 'expand' form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data_expand})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'completed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "completed"
    # Verify the result summary indicates arrays were expanded

    # Repeat the test with array_handling set to 'join'
    form_data_join = create_test_form_data(array_handling="join")
    result_summary_join = create_conversion_result_summary(rows=100, columns=15)
    mock_conversion_service.convert_file.return_value = (True, result_summary_join, None)
    mock_storage_service.get_output_file.return_value = ("/path/to/download_join", "download_join.xlsx", None)

    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data_join})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'completed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "completed"
    # Verify the result summary indicates arrays were joined


@pytest.mark.functional
def test_conversion_flow_job_cancellation(client, mock_file_service, mock_storage_service, mock_job_manager,
                                           mock_conversion_service, create_test_json_file_storage, create_test_form_data):
    """
    Tests the ability to cancel a conversion job in progress.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()
    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Configure mock_job_manager to simulate a long-running job
    mock_job_manager.create_job.return_value = (True, None)
    mock_job_manager.get_job_status.return_value = ({"status": "processing"}, None)

    # Send a POST request to /upload with the test file
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status is 'processing'
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "processing"

    # Send a POST request to /cancel/{job_id} to cancel the job
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs/{job_id}/cancel")

    # Verify the response status code is 200
    assert response.status_code == 200

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the status is now 'failed' with a cancellation message
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "failed"
    assert "Job cancelled by user" in response.get_json()["status"]["message"]


@pytest.mark.functional
def test_conversion_flow_with_custom_options(client, mock_file_service, mock_storage_service, mock_job_manager,
                                              mock_conversion_service, create_test_json_file_storage, create_test_form_data,
                                              create_conversion_result_summary):
    """
    Tests the conversion flow with custom Excel formatting options.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()
    # Create test form data with custom options (sheet_name, format_headers, auto_column_width)
    form_data = create_test_form_data(sheet_name="CustomSheet", format_headers=False, auto_column_width=False)
    # Create a conversion result summary
    result_summary = create_conversion_result_summary()

    # Configure mock services to return successful responses
    mock_conversion_service.process_conversion_job.return_value = True
    mock_conversion_service.convert_file.return_value = (True, result_summary, None)
    mock_storage_service.get_output_file.return_value = ("/path/to/download", "download.xlsx", None)

    # Send a POST request to /upload with the test file
    with unittest.mock.patch('src.web.routes.file_service', mock_file_service):
        with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
            with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
                response = client.post("/api/uploads", data={"file": (test_file.stream, test_file.filename)})

    # Verify the response status code is 200
    assert response.status_code == 200
    # Extract the file_id from the response
    file_id = response.get_json()["file"]["fileId"]

    # Send a POST request to /convert with the file_id and custom form data
    with unittest.mock.patch('src.web.api.conversion_api.job_manager', mock_job_manager):
        response = client.post(f"/api/conversion/jobs", data={"file_id": file_id, **form_data})

    # Verify the response status code is 200
    assert response.status_code == 201
    # Extract the job_id from the response
    job_id = response.get_json()["job"]["job_id"]

    # Send a GET request to /status/{job_id} to check job status
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        response = client.get(f"/api/conversion/jobs/{job_id}/status")

    # Verify the response status code is 200 and status is 'completed'
    assert response.status_code == 200
    assert response.get_json()["status"]["status"] == "completed"
    # Verify the result summary contains the custom options that were applied

    # Send a GET request to /download/{job_id} to download the result
    with unittest.mock.patch('src.web.routes.job_manager', mock_job_manager):
        with unittest.mock.patch('src.web.routes.conversion_service', mock_conversion_service):
            response = client.get(f"/api/conversion/jobs/{job_id}/download")

    # Verify the response status code is 200
    assert response.status_code == 200