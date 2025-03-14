import pytest  # pytest-7.3.0+ Testing framework for writing and running tests
from unittest.mock import Mock  # built-in For creating mock objects and patching dependencies
import queue  # built-in For testing the job queue implementation
import time  # built-in For testing timeouts and delays
import threading  # built-in For testing the worker thread functionality

from src.web.services.job_manager import JobManager  # For representing and tracking conversion jobs
from src.web.services.conversion_service import ConversionService  # For mocking the conversion service dependency
from src.web.services.file_service import FileService  # For mocking the file service dependency
from src.web.services.storage_service import StorageService  # For mocking the storage service dependency
from src.web.models.conversion_job import ConversionJob  # For creating and manipulating test job instances
from src.web.models.job_status import JobStatusEnum  # For checking job status in tests
from src.web.exceptions.job_exceptions import JobException, JobCreationException, JobNotFoundException, JobQueueFullException  # Base exception class for job-related errors
from src.web.tests.fixtures.job_fixtures import create_test_job, create_pending_job, create_processing_job, create_completed_job, create_failed_job  # Fixture for creating test conversion jobs
from src.web.tests.fixtures.file_fixtures import create_test_upload_file  # Fixture for creating test upload files
from src.backend.models.error_response import ErrorResponse  # For checking error responses in tests

@pytest.fixture
def mock_conversion_service():
    """Creates a mock ConversionService instance."""
    return Mock(spec=ConversionService)

@pytest.fixture
def mock_file_service():
    """Creates a mock FileService instance."""
    return Mock(spec=FileService)

@pytest.fixture
def mock_storage_service():
    """Creates a mock StorageService instance."""
    return Mock(spec=StorageService)

def test_job_manager_initialization(mock_conversion_service, mock_file_service, mock_storage_service):
    """Tests that the JobManager initializes correctly with default and custom dependencies."""
    # LD1: Create mock instances of ConversionService, FileService, and StorageService
    # LD1: Initialize a JobManager with default dependencies
    job_manager = JobManager()

    # LD1: Verify that internal services are created
    assert job_manager._conversion_service is not None
    assert job_manager._file_service is not None
    assert job_manager._storage_service is not None
    assert isinstance(job_manager._job_queue, queue.Queue)
    assert job_manager._worker_thread is not None
    assert job_manager._running is True

    # LD1: Initialize a JobManager with custom dependencies
    job_manager_custom = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service, storage_service=mock_storage_service)

    # LD1: Verify that the custom dependencies are used
    assert job_manager_custom._conversion_service == mock_conversion_service
    assert job_manager_custom._file_service == mock_file_service
    assert job_manager_custom._storage_service == mock_storage_service

    # LD1: Verify that the job queue is empty
    assert job_manager._job_queue.empty()

    # LD1: Verify that the worker thread is started
    assert job_manager._running is True
    assert job_manager._worker_thread is not None
    assert job_manager._worker_thread.is_alive()

def test_start_stop():
    """Tests that the JobManager correctly starts and stops the worker thread."""
    # LD1: Create a JobManager instance with mock dependencies
    job_manager = JobManager()

    # LD1: Call the stop method to ensure the worker thread is stopped
    job_manager.stop()

    # LD1: Verify that _running is False
    assert job_manager._running is False

    # LD1: Call the start method to start the worker thread
    job_manager.start()

    # LD1: Verify that _running is True
    assert job_manager._running is True

    # LD1: Verify that the worker thread is created and running
    assert job_manager._worker_thread is not None
    assert job_manager._worker_thread.is_alive()

    # LD1: Call start again to test that it handles being called when already running
    job_manager.start()

    # LD1: Call stop to shut down the worker thread
    job_manager.stop()

    # LD1: Verify that _running is False and the worker thread is stopped
    assert job_manager._running is False
    if job_manager._worker_thread:
        job_manager._worker_thread.join(timeout=1)
        assert not job_manager._worker_thread.is_alive()

def test_create_job_success(mock_conversion_service, mock_file_service, mock_storage_service):
    """Tests successful job creation with valid inputs."""
    # LD1: Create mock dependencies with successful responses
    test_upload_file = create_test_upload_file()
    mock_file_service.get_upload.return_value = (test_upload_file, None)
    mock_storage_service.save_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service, storage_service=mock_storage_service)

    # LD1: Call create_job with valid file_id and options
    test_options = {"sheet_name": "TestSheet"}
    job, error = job_manager.create_job(file_id="test_file", options=test_options)

    # LD1: Verify that FileService.get_upload was called with the correct file_id
    mock_file_service.get_upload.assert_called_once_with("test_file")

    # LD1: Verify that StorageService.save_conversion_job was called with a job instance
    mock_storage_service.save_conversion_job.assert_called_once()
    saved_job = mock_storage_service.save_conversion_job.call_args[0][0]
    assert isinstance(saved_job, ConversionJob)

    # LD1: Verify that the job was added to the queue
    assert not job_manager._job_queue.empty()

    # LD1: Verify that the returned job has the expected properties
    assert job is not None
    assert job.input_file == test_upload_file
    assert job.options == mock_conversion_service.process_form_data.return_value

    # LD1: Verify that no error response was returned
    assert error is None

def test_create_job_file_not_found(mock_conversion_service, mock_file_service, mock_storage_service):
    """Tests job creation when the specified file cannot be found."""
    # LD1: Create mock FileService that returns None for get_upload
    mock_file_service.get_upload.return_value = (None, ErrorResponse(message="File not found", error_code="FILE_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="FileService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service, storage_service=mock_storage_service)

    # LD1: Call create_job with a non-existent file_id
    job, error = job_manager.create_job(file_id="non_existent_file", options={})

    # LD1: Verify that FileService.get_upload was called with the correct file_id
    mock_file_service.get_upload.assert_called_once_with("non_existent_file")

    # LD1: Verify that no job was returned
    assert job is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "File not found"

    # LD1: Verify that the error message indicates the file was not found
    assert "File not found" in error.message

def test_create_job_queue_full(mock_conversion_service, mock_file_service, mock_storage_service):
    """Tests job creation when the job queue is at capacity."""
    # LD1: Create mock dependencies
    test_upload_file = create_test_upload_file()
    mock_file_service.get_upload.return_value = (test_upload_file, None)
    mock_storage_service.save_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service, storage_service=mock_storage_service)

    # LD1: Patch the MAX_ACTIVE_JOBS constant to a low value
    with pytest. MonkeyPatch.context() as mp:
        mp.setattr(job_manager, "MAX_ACTIVE_JOBS", 1)

        # LD1: Fill the job queue to capacity
        job_manager.create_job(file_id="test_file_1", options={})

        # LD1: Call create_job with valid inputs
        job, error = job_manager.create_job(file_id="test_file_2", options={})

        # LD1: Verify that no job was returned
        assert job is None

        # LD1: Verify that an appropriate error response was returned
        assert error is not None
        assert "Job queue is full" in error.message

        # LD1: Verify that the error message indicates the queue is full
        assert "Job queue is full" in error.message

def test_get_job_success(mock_storage_service):
    """Tests successful job retrieval with a valid job ID."""
    # LD1: Create a test job with a known job_id
    test_job = create_test_job(job_id="test_job_123")

    # LD1: Create mock StorageService that returns the test job for get_conversion_job
    mock_storage_service.get_conversion_job.return_value = (test_job, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job with the known job_id
    job, error = job_manager.get_job(job_id="test_job_123")

    # LD1: Verify that StorageService.get_conversion_job was called with the correct job_id
    mock_storage_service.get_conversion_job.assert_called_once_with("test_job_123")

    # LD1: Verify that the returned job matches the test job
    assert job == test_job

    # LD1: Verify that no error response was returned
    assert error is None

def test_get_job_not_found(mock_storage_service):
    """Tests job retrieval when the specified job cannot be found."""
    # LD1: Create mock StorageService that returns None for get_conversion_job
    mock_storage_service.get_conversion_job.return_value = (None, ErrorResponse(message="Job not found", error_code="JOB_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="StorageService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job with a non-existent job_id
    job, error = job_manager.get_job(job_id="non_existent_job")

    # LD1: Verify that StorageService.get_conversion_job was called with the correct job_id
    mock_storage_service.get_conversion_job.assert_called_once_with("non_existent_job")

    # LD1: Verify that no job was returned
    assert job is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Job not found"

    # LD1: Verify that the error message indicates the job was not found
    assert "Job not found" in error.message

def test_get_job_status_success(mock_storage_service, create_test_job_status):
    """Tests successful job status retrieval with a valid job ID."""
    # LD1: Create a test job with a known job_id and status
    test_job_status = create_test_job_status(job_id="test_job_123", status=JobStatusEnum.PROCESSING)

    # LD1: Create mock dependencies that return the test job
    mock_storage_service.get_conversion_job.return_value = (Mock(status=test_job_status), None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job_status with the known job_id
    status, error = job_manager.get_job_status(job_id="test_job_123")

    # LD1: Verify that the job status was retrieved
    assert status is not None

    # LD1: Verify that the status contains the expected information
    assert status["status"] == "processing"

    # LD1: Verify that no error response was returned
    assert error is None

def test_get_job_status_not_found(mock_storage_service):
    """Tests job status retrieval when the specified job cannot be found."""
    # LD1: Create mock dependencies that return None for get_job
    mock_storage_service.get_conversion_job.return_value = (None, ErrorResponse(message="Job not found", error_code="JOB_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="StorageService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job_status with a non-existent job_id
    status, error = job_manager.get_job_status(job_id="non_existent_job")

    # LD1: Verify that no status was returned
    assert status is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Job not found"

    # LD1: Verify that the error message indicates the job was not found
    assert "Job not found" in error.message

def test_get_job_result_success(mock_storage_service):
    """Tests successful job result retrieval for a completed job."""
    # LD1: Create a completed test job with a known job_id
    completed_job = create_completed_job()

    # LD1: Create mock dependencies that return the completed job
    mock_storage_service.get_conversion_job.return_value = (completed_job, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job_result with the known job_id
    result, error = job_manager.get_job_result(job_id="test_job_123")

    # LD1: Verify that the job result was retrieved
    assert result is not None

    # LD1: Verify that the result contains the expected information
    assert result["status"] == "completed"

    # LD1: Verify that no error response was returned
    assert error is None

def test_get_job_result_not_found(mock_storage_service):
    """Tests job result retrieval when the specified job cannot be found."""
    # LD1: Create mock dependencies that return None for get_job
    mock_storage_service.get_conversion_job.return_value = (None, ErrorResponse(message="Job not found", error_code="JOB_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="StorageService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job_result with a non-existent job_id
    result, error = job_manager.get_job_result(job_id="non_existent_job")

    # LD1: Verify that no result was returned
    assert result is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Job not found"

    # LD1: Verify that the error message indicates the job was not found
    assert "Job not found" in error.message

def test_get_job_result_not_complete(mock_storage_service):
    """Tests job result retrieval when the job is not yet complete."""
    # LD1: Create a pending test job with a known job_id
    pending_job = create_pending_job()

    # LD1: Create mock dependencies that return the pending job
    mock_storage_service.get_conversion_job.return_value = (pending_job, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call get_job_result with the known job_id
    result, error = job_manager.get_job_result(job_id="test_job_123")

    # LD1: Verify that no result was returned
    assert result is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Job is not complete"

    # LD1: Verify that the error message indicates the job is not complete
    assert "Job is not complete" in error.message

def test_get_output_file_success(mock_conversion_service):
    """Tests successful output file retrieval for a completed job."""
    # LD1: Create mock ConversionService that returns a file path and name
    mock_conversion_service.get_output_file.return_value = ("/tmp/output.xlsx", "output.xlsx", None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service)

    # LD1: Call get_output_file with a valid job_id
    file_path, file_name, error = job_manager.get_output_file(job_id="test_job_123")

    # LD1: Verify that ConversionService.get_output_file was called with the correct job_id
    mock_conversion_service.get_output_file.assert_called_once_with("test_job_123")

    # LD1: Verify that the file path and name were returned
    assert file_path == "/tmp/output.xlsx"
    assert file_name == "output.xlsx"

    # LD1: Verify that no error response was returned
    assert error is None

def test_get_output_file_error(mock_conversion_service):
    """Tests output file retrieval when an error occurs."""
    # LD1: Create mock ConversionService that returns an error for get_output_file
    mock_conversion_service.get_output_file.return_value = (None, None, ErrorResponse(message="Output file not found", error_code="FILE_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="ConversionService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service)

    # LD1: Call get_output_file with a valid job_id
    file_path, file_name, error = job_manager.get_output_file(job_id="test_job_123")

    # LD1: Verify that ConversionService.get_output_file was called with the correct job_id
    mock_conversion_service.get_output_file.assert_called_once_with("test_job_123")

    # LD1: Verify that no file path or name was returned
    assert file_path is None
    assert file_name is None

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Output file not found"

def test_cancel_job_success(mock_storage_service):
    """Tests successful job cancellation for a pending job."""
    # LD1: Create a pending test job with a known job_id
    pending_job = create_pending_job()

    # LD1: Create mock dependencies that return the pending job
    mock_storage_service.get_conversion_job.return_value = (pending_job, None)
    mock_storage_service.update_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call cancel_job with the known job_id
    success, error = job_manager.cancel_job(job_id="test_job_123")

    # LD1: Verify that the job was retrieved
    mock_storage_service.get_conversion_job.assert_called_once_with("test_job_123")

    # LD1: Verify that the job status was updated to FAILED
    assert pending_job.status.status == JobStatusEnum.FAILED

    # LD1: Verify that StorageService.update_conversion_job was called
    mock_storage_service.update_conversion_job.assert_called_once()

    # LD1: Verify that True was returned indicating success
    assert success is True

    # LD1: Verify that no error response was returned
    assert error is None

def test_cancel_job_not_found(mock_storage_service):
    """Tests job cancellation when the specified job cannot be found."""
    # LD1: Create mock dependencies that return None for get_job
    mock_storage_service.get_conversion_job.return_value = (None, ErrorResponse(message="Job not found", error_code="JOB_NOT_FOUND", category=ErrorResponse.INPUT_ERROR, severity=ErrorResponse.ERROR, source_component="StorageService"))

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call cancel_job with a non-existent job_id
    success, error = job_manager.cancel_job(job_id="non_existent_job")

    # LD1: Verify that False was returned indicating failure
    assert success is False

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert error.message == "Job not found"

    # LD1: Verify that the error message indicates the job was not found
    assert "Job not found" in error.message

def test_cancel_job_already_complete(mock_storage_service):
    """Tests job cancellation when the job is already complete."""
    # LD1: Create a completed test job with a known job_id
    completed_job = create_completed_job()

    # LD1: Create mock dependencies that return the completed job
    mock_storage_service.get_conversion_job.return_value = (completed_job, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call cancel_job with the known job_id
    success, error = job_manager.cancel_job(job_id="test_job_123")

    # LD1: Verify that False was returned indicating failure
    assert success is False

    # LD1: Verify that an appropriate error response was returned
    assert error is not None
    assert "Job is already complete" in error.message

    # LD1: Verify that the error message indicates the job is already complete
    assert "Job is already complete" in error.message

def test_list_jobs(mock_storage_service):
    """Tests listing all jobs with optional filtering by status."""
    # LD1: Create test jobs with different statuses
    pending_job = create_pending_job()
    completed_job = create_completed_job()
    failed_job = create_failed_job()

    # LD1: Create mock StorageService that returns the test jobs
    mock_storage_service.list_conversion_jobs.return_value = [pending_job, completed_job, failed_job]

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(storage_service=mock_storage_service)

    # LD1: Call list_jobs with no status filter
    jobs = job_manager.list_jobs()

    # LD1: Verify that all jobs are returned
    assert len(jobs) == 3
    assert pending_job.to_dict() in jobs
    assert completed_job.to_dict() in jobs
    assert failed_job.to_dict() in jobs

    # LD1: Call list_jobs with a status filter
    jobs = job_manager.list_jobs(status=JobStatusEnum.COMPLETED)

    # LD1: Verify that only jobs with the matching status are returned
    assert len(jobs) == 1
    assert completed_job.to_dict() in jobs

def test_get_queue_status():
    """Tests retrieving the current status of the job queue."""
    # LD1: Create a JobManager instance with mock dependencies
    job_manager = JobManager()

    # LD1: Add some jobs to the queue and active jobs
    pending_job = create_pending_job()
    job_manager._job_queue.put(pending_job)
    job_manager._active_jobs[pending_job.job_id] = pending_job

    # LD1: Call get_queue_status
    status = job_manager.get_queue_status()

    # LD1: Verify that the returned status contains the correct queue size
    assert status["queue_size"] == 1

    # LD1: Verify that the returned status contains the correct number of active jobs
    assert status["active_jobs"] == 1

    # LD1: Verify that the returned status contains the maximum number of active jobs
    assert status["max_active_jobs"] == job_manager.MAX_ACTIVE_JOBS

def test_worker_loop(mock_conversion_service, mock_storage_service):
    """Tests the worker loop functionality for processing jobs from the queue."""
    # LD1: Create mock dependencies
    test_upload_file = create_test_upload_file()
    mock_file_service = Mock()
    mock_file_service.get_upload.return_value = (test_upload_file, None)
    mock_storage_service.save_conversion_job.return_value = (True, None)
    mock_conversion_service.process_conversion_job.return_value = True
    mock_storage_service.update_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service, storage_service=mock_storage_service)

    # LD1: Create a test job and add it to the queue
    test_job = create_test_job()
    job_manager._job_queue.put(test_job)

    # LD1: Patch the _worker_loop method to run once and exit
    with pytest. MonkeyPatch.context() as mp:
        mp.setattr(job_manager, "_running", False)

        # LD1: Start the worker thread
        job_manager._worker_loop()

        # LD1: Verify that the job was removed from the queue
        assert job_manager._job_queue.empty()

        # LD1: Verify that ConversionService.process_conversion_job was called
        mock_conversion_service.process_conversion_job.assert_called_once_with(test_job)

        # LD1: Verify that StorageService.update_conversion_job was called
        mock_storage_service.update_conversion_job.assert_called_once_with(test_job)

def test_process_job_success(mock_conversion_service, mock_storage_service):
    """Tests successful processing of a job by the worker thread."""
    # LD1: Create mock dependencies
    mock_conversion_service.process_conversion_job.return_value = True
    mock_storage_service.update_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, storage_service=mock_storage_service)

    # LD1: Create a test job
    test_job = create_test_job()

    # LD1: Call the _process_job method directly with the test job
    job_manager._process_job(test_job)

    # LD1: Verify that ConversionService.process_conversion_job was called with the job
    mock_conversion_service.process_conversion_job.assert_called_once_with(test_job)

    # LD1: Verify that the job was added to and removed from _active_jobs
    assert test_job.job_id not in job_manager._active_jobs

    # LD1: Verify that StorageService.update_conversion_job was called with the updated job
    mock_storage_service.update_conversion_job.assert_called_once_with(test_job)

def test_process_job_error(mock_conversion_service, mock_storage_service):
    """Tests job processing when an error occurs during conversion."""
    # LD1: Create mock ConversionService that raises an exception for process_conversion_job
    mock_conversion_service.process_conversion_job.side_effect = Exception("Conversion failed")
    mock_storage_service.update_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, storage_service=mock_storage_service)

    # LD1: Create a test job
    test_job = create_test_job()

    # LD1: Call the _process_job method directly with the test job
    job_manager._process_job(test_job)

    # LD1: Verify that ConversionService.process_conversion_job was called with the job
    mock_conversion_service.process_conversion_job.assert_called_once_with(test_job)

    # LD1: Verify that the job status was updated to FAILED
    assert test_job.status.status == JobStatusEnum.FAILED

    # LD1: Verify that StorageService.update_conversion_job was called with the updated job
    mock_storage_service.update_conversion_job.assert_called_once_with(test_job)

def test_check_job_timeouts(mock_conversion_service, mock_storage_service):
    """Tests the timeout checking functionality for long-running jobs."""
    # LD1: Create mock dependencies
    mock_storage_service.update_conversion_job.return_value = (True, None)

    # LD1: Create a JobManager instance with the mock dependencies
    job_manager = JobManager(conversion_service=mock_conversion_service, storage_service=mock_storage_service)

    # LD1: Create a test job and add it to _active_jobs
    test_job = create_test_job()
    job_manager._active_jobs[test_job.job_id] = test_job

    # LD1: Set the job start time to exceed the timeout limit
    import datetime
    job_manager._job_start_times[test_job.job_id] = datetime.datetime.now() - datetime.timedelta(minutes=job_manager.JOB_TIMEOUT_MINUTES + 1)

    # LD1: Call the _check_job_timeouts method
    job_manager._check_job_timeouts()

    # LD1: Verify that the job was removed from _active_jobs
    assert test_job.job_id not in job_manager._active_jobs

    # LD1: Verify that the job status was updated to FAILED with a timeout error
    assert test_job.status.status == JobStatusEnum.FAILED
    assert "Job exceeded timeout" in test_job.status.message

    # LD1: Verify that StorageService.update_conversion_job was called with the updated job
    mock_storage_service.update_conversion_job.assert_called_once_with(test_job)