# Standard library imports
import time  # v: built-in - For adding delays in tests to simulate processing time
import unittest.mock  # v: built-in - For creating mock objects and patching functions

# Third-party library imports
import pytest  # v: latest - For test fixtures and assertions

# Local application imports
from src.web.models.conversion_job import ConversionJob  # For representing and testing conversion jobs
from src.web.models.job_status import JobStatusEnum  # For checking job status in tests
from src.web.services.conversion_service import ConversionService  # For handling the actual conversion process
from src.web.services.file_service import FileService  # For managing uploaded files
from src.web.services.job_manager import JobManager  # The main service being tested for job management
from src.web.services.storage_service import StorageService  # For storing and retrieving job data
from src.web.tests.fixtures.conversion_fixtures import MockConversionClient  # For mocking the conversion client
from src.web.tests.fixtures.conversion_fixtures import create_test_conversion_options  # For creating test conversion options
from src.web.tests.fixtures.file_fixtures import create_test_upload_file  # For creating test upload files
from src.web.tests.fixtures.job_fixtures import create_test_job  # For creating test job instances


@pytest.mark.integration
def test_job_creation(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that a job can be successfully created with the JobManager.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Create a test upload file ID
    file_id = "test_file_id"

    # Create test conversion options
    options = create_test_conversion_options()

    # Call job_manager.create_job with the file ID and options
    job, error = job_manager.create_job(file_id, options)

    # Assert that a job was returned and no error occurred
    assert job is not None
    assert error is None

    # Assert that the job has the expected properties
    assert job.input_file is not None
    assert job.options is not None

    # Assert that the job status is PENDING
    assert job.status.status == JobStatusEnum.PENDING


@pytest.mark.integration
def test_job_retrieval(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that a created job can be retrieved by its ID.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Create a test job and save it to storage
    test_job = create_test_job()
    mock_storage_service.save_conversion_job(test_job)

    # Call job_manager.get_job with the job ID
    retrieved_job, error = job_manager.get_job(test_job.job_id)

    # Assert that the job was retrieved successfully
    assert retrieved_job is not None
    assert error is None

    # Assert that the retrieved job has the same ID as the created job
    assert retrieved_job.job_id == test_job.job_id


@pytest.mark.integration
def test_job_status_retrieval(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that the status of a job can be retrieved.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Create a test job and save it to storage
    test_job = create_test_job()
    mock_storage_service.save_conversion_job(test_job)

    # Call job_manager.get_job_status with the job ID
    status, error = job_manager.get_job_status(test_job.job_id)

    # Assert that the status was retrieved successfully
    assert status is not None
    assert error is None

    # Assert that the status contains the expected fields (status, progress_percentage, message)
    assert "status" in status
    assert "progress_percentage" in status
    assert "message" in status


@pytest.mark.integration
def test_job_processing(mock_file_service: FileService, mock_storage_service: StorageService,
                       mock_conversion_service: ConversionService) -> None:
    """Tests the complete job processing flow from creation to completion.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.
        mock_conversion_service: Mocked ConversionService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service,
                             storage_service=mock_storage_service)

    # Configure the mock_conversion_service to successfully process jobs
    mock_conversion_service.process_conversion_job.return_value = True

    # Create a test upload file ID
    file_id = "test_file_id"

    # Create test conversion options
    options = create_test_conversion_options()

    # Call job_manager.create_job with the file ID and options
    job, error = job_manager.create_job(file_id, options)

    # Start the job manager worker thread
    job_manager.start()

    # Wait for the job to be processed
    time.sleep(1)

    # Get the job result using job_manager.get_job_result
    result, error = job_manager.get_job_result(job.job_id)

    # Assert that the job was completed successfully
    assert result is not None
    assert error is None

    # Assert that the job result contains the expected data
    assert result["status"] == JobStatusEnum.COMPLETED.value

    # Stop the job manager worker thread
    job_manager.stop()


@pytest.mark.integration
def test_job_processing_failure(mock_file_service: FileService, mock_storage_service: StorageService,
                                mock_conversion_service: ConversionService) -> None:
    """Tests that job processing failures are handled correctly.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.
        mock_conversion_service: Mocked ConversionService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service,
                             storage_service=mock_storage_service)

    # Configure the mock_conversion_service to fail when processing jobs
    mock_conversion_service.process_conversion_job.return_value = False

    # Create a test upload file ID
    file_id = "test_file_id"

    # Create test conversion options
    options = create_test_conversion_options()

    # Call job_manager.create_job with the file ID and options
    job, error = job_manager.create_job(file_id, options)

    # Start the job manager worker thread
    job_manager.start()

    # Wait for the job to be processed
    time.sleep(1)

    # Get the job status using job_manager.get_job_status
    status, error = job_manager.get_job_status(job.job_id)

    # Assert that the job status is FAILED
    assert status["status"] == JobStatusEnum.FAILED.value

    # Assert that the job has an error message
    assert status["message"] is not None

    # Stop the job manager worker thread
    job_manager.stop()


@pytest.mark.integration
def test_multiple_job_processing(mock_file_service: FileService, mock_storage_service: StorageService,
                                 mock_conversion_service: ConversionService) -> None:
    """Tests that multiple jobs can be processed concurrently.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.
        mock_conversion_service: Mocked ConversionService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=mock_conversion_service, file_service=mock_file_service,
                             storage_service=mock_storage_service)

    # Configure the mock_conversion_service to successfully process jobs
    mock_conversion_service.process_conversion_job.return_value = True

    # Create multiple test jobs with different file IDs
    num_jobs = 3
    jobs = []
    for i in range(num_jobs):
        file_id = f"test_file_id_{i}"
        options = create_test_conversion_options()
        job, error = job_manager.create_job(file_id, options)
        jobs.append(job)

    # Start the job manager worker thread
    job_manager.start()

    # Wait for all jobs to be processed
    time.sleep(2)

    # Check the status of each job
    for job in jobs:
        status, error = job_manager.get_job_status(job.job_id)

        # Assert that all jobs were completed successfully
        assert status["status"] == JobStatusEnum.COMPLETED.value

    # Stop the job manager worker thread
    job_manager.stop()


@pytest.mark.integration
def test_job_queue_limits(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that the job queue enforces maximum active job limits.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Patch the MAX_ACTIVE_JOBS constant to a small value for testing
    with unittest.mock.patch("src.web.services.job_manager.MAX_ACTIVE_JOBS", 1):
        # Create jobs up to the MAX_ACTIVE_JOBS limit
        file_id_1 = "test_file_id_1"
        options = create_test_conversion_options()
        job_1, error_1 = job_manager.create_job(file_id_1, options)

        # Assert that all jobs were created successfully
        assert job_1 is not None
        assert error_1 is None

        # Try to create one more job beyond the limit
        file_id_2 = "test_file_id_2"
        job_2, error_2 = job_manager.create_job(file_id_2, options)

        # Assert that job creation fails with a JobQueueFullException
        assert job_2 is None
        assert error_2 is not None
        assert "Job queue is full" in error_2.message

        # Assert that the error message indicates the queue is full
        assert "Job queue is full" in error_2.message


@pytest.mark.integration
def test_job_result_retrieval(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that the result of a completed job can be retrieved.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Create a test job that is already completed
    test_job = create_test_job(status=JobStatusEnum.COMPLETED)

    # Save the job to storage
    mock_storage_service.save_conversion_job(test_job)

    # Call job_manager.get_job_result with the job ID
    result, error = job_manager.get_job_result(test_job.job_id)

    # Assert that the result was retrieved successfully
    assert result is not None
    assert error is None

    # Assert that the result contains the expected fields (job_id, status, output_file_path, etc.)
    assert "job_id" in result
    assert "status" in result
    assert "output_file_path" in result


@pytest.mark.integration
def test_job_cancellation(mock_file_service: FileService, mock_storage_service: StorageService) -> None:
    """Tests that a job can be cancelled while in progress.

    Args:
        mock_file_service: Mocked FileService instance.
        mock_storage_service: Mocked StorageService instance.

    Returns:
        None: This test doesn't return a value
    """
    # Create a JobManager instance with the mock services
    job_manager = JobManager(conversion_service=None, file_service=mock_file_service, storage_service=mock_storage_service)

    # Create a test job with PROCESSING status
    test_job = create_test_job(status=JobStatusEnum.PROCESSING)

    # Save the job to storage
    mock_storage_service.save_conversion_job(test_job)

    # Call job_manager.cancel_job with the job ID
    success, error = job_manager.cancel_job(test_job.job_id)

    # Assert that the cancellation was successful
    assert success is True
    assert error is None

    # Get the job status
    status, error = job_manager.get_job_status(test_job.job_id)

    # Assert that the job status is FAILED
    assert status["status"] == JobStatusEnum.FAILED.value

    # Assert that the error message indicates the job was cancelled
    assert "Job cancelled by user" in status["message"]