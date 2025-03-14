"""
Provides test fixtures for job-related tests in the web interface component of the JSON to Excel Conversion Tool.
These fixtures include functions to create test conversion jobs with various states and configurations for unit
and integration testing.
"""

import pytest  # v: 7.3.0+
import uuid  # v: built-in
import datetime  # v: built-in
from typing import Optional, Dict, Any  # v: built-in
from unittest.mock import Mock  # v: built-in

from ../../models.conversion_job import ConversionJob
from ../../models.job_status import JobStatus, JobStatusEnum
from ../../models.conversion_options import ConversionOptions, DefaultConversionOptions
from ./file_fixtures import create_test_upload_file
from ../../../backend.models.error_response import ErrorResponse, ErrorCategory

# Global constants for use in tests
TEST_JOB_ID = "test-job-123"
TEST_JOB_MESSAGE = "Test job message"


@pytest.fixture
def create_test_job_status(job_id: str = None, status: JobStatusEnum = None, 
                           progress_percentage: int = None, message: str = None) -> JobStatus:
    """
    Creates a JobStatus instance with test values for use in tests.
    
    Args:
        job_id: Optional job ID, defaults to TEST_JOB_ID
        status: Optional status, defaults to PENDING
        progress_percentage: Optional progress percentage, defaults to 0
        message: Optional status message, defaults to TEST_JOB_MESSAGE
        
    Returns:
        A JobStatus instance with test values
    """
    job_id = job_id or TEST_JOB_ID
    status = status or JobStatusEnum.PENDING
    progress_percentage = 0 if progress_percentage is None else progress_percentage
    message = message or TEST_JOB_MESSAGE
    
    return JobStatus(
        job_id=job_id,
        status=status,
        progress_percentage=progress_percentage,
        message=message
    )


@pytest.fixture
def create_test_job(job_id: str = None, options: ConversionOptions = None, 
                    status: JobStatusEnum = None, progress_percentage: int = None) -> ConversionJob:
    """
    Creates a ConversionJob instance with test values for use in tests.
    
    Args:
        job_id: Optional job ID, defaults to a new UUID
        options: Optional conversion options, defaults to default options
        status: Optional job status, defaults to PENDING
        progress_percentage: Optional progress percentage, defaults to 0
        
    Returns:
        A ConversionJob instance with test values
    """
    job_id = job_id or str(uuid.uuid4())
    upload_file = create_test_upload_file()
    options = options or DefaultConversionOptions.get_defaults()
    
    job = ConversionJob(
        job_id=job_id,
        input_file=upload_file,
        options=options
    )
    
    if status:
        job.update_status(
            status=status,
            progress_percentage=progress_percentage or 0,
            message=TEST_JOB_MESSAGE
        )
    
    return job


@pytest.fixture
def create_pending_job() -> ConversionJob:
    """
    Creates a ConversionJob instance with PENDING status for use in tests.
    
    Returns:
        A ConversionJob instance with PENDING status
    """
    return create_test_job(status=JobStatusEnum.PENDING, progress_percentage=0)


@pytest.fixture
def create_processing_job(progress_percentage: int = 50) -> ConversionJob:
    """
    Creates a ConversionJob instance with PROCESSING status for use in tests.
    
    Args:
        progress_percentage: Optional progress percentage, defaults to 50
        
    Returns:
        A ConversionJob instance with PROCESSING status
    """
    return create_test_job(status=JobStatusEnum.PROCESSING, progress_percentage=progress_percentage)


@pytest.fixture
def create_completed_job() -> ConversionJob:
    """
    Creates a ConversionJob instance with COMPLETED status for use in tests.
    
    Returns:
        A ConversionJob instance with COMPLETED status
    """
    job = create_test_job()
    job.set_completed(
        output_file_path="/tmp/output.xlsx",
        output_file_name="output.xlsx",
        conversion_summary={
            "rows": 100,
            "columns": 10,
            "processing_time": 1.5
        },
        message="Conversion completed successfully"
    )
    return job


@pytest.fixture
def create_failed_job() -> ConversionJob:
    """
    Creates a ConversionJob instance with FAILED status for use in tests.
    
    Returns:
        A ConversionJob instance with FAILED status
    """
    job = create_test_job()
    error = ErrorResponse(
        message="Conversion failed due to processing error",
        error_code="PROCESSING_ERROR",
        category=ErrorCategory.PROCESSING_ERROR,
        severity="ERROR",
        source_component="DataTransformer"
    )
    job.set_failed(error, message="Conversion failed")
    return job


@pytest.fixture
def create_job_dict(status: JobStatusEnum = JobStatusEnum.PENDING) -> Dict[str, Any]:
    """
    Creates a dictionary representation of a ConversionJob for use in tests.
    
    Args:
        status: Optional job status, defaults to PENDING
        
    Returns:
        A dictionary representation of a ConversionJob
    """
    job = create_test_job(status=status)
    return job.to_dict()


@pytest.fixture
def mock_job_manager(job_creation_success: bool = True, job_retrieval_success: bool = True) -> Mock:
    """
    Creates a mock JobManager for testing job-related functionality.
    
    Args:
        job_creation_success: Whether job creation should succeed
        job_retrieval_success: Whether job retrieval should succeed
        
    Returns:
        A mock JobManager with predetermined responses
    """
    mock_manager = Mock()
    
    # Setup test job and error response
    test_job = create_test_job()
    error_response = ErrorResponse(
        message="Test error",
        error_code="TEST_ERROR",
        category=ErrorCategory.PROCESSING_ERROR,
        severity="ERROR",
        source_component="TestComponent"
    )
    
    # Configure create_job method
    if job_creation_success:
        mock_manager.create_job.return_value = (test_job, None)
    else:
        mock_manager.create_job.return_value = (None, error_response)
    
    # Configure get_job method
    if job_retrieval_success:
        mock_manager.get_job.return_value = (test_job, None)
    else:
        mock_manager.get_job.return_value = (None, error_response)
    
    # Configure get_job_status method
    if job_retrieval_success:
        mock_manager.get_job_status.return_value = (test_job.get_status_dict(), None)
    else:
        mock_manager.get_job_status.return_value = (None, error_response)
    
    # Configure get_job_result method
    if job_retrieval_success:
        mock_manager.get_job_result.return_value = ({"status": "completed", "result": "test.xlsx"}, None)
    else:
        mock_manager.get_job_result.return_value = (None, error_response)
    
    return mock_manager


class MockJobManager:
    """
    A mock implementation of JobManager for testing without service dependencies.
    """
    
    def __init__(self, create_job_success: bool = True, get_job_success: bool = True, 
                 error_response: ErrorResponse = None):
        """
        Initializes a new MockJobManager with predetermined responses.
        
        Args:
            create_job_success: Whether job creation should succeed
            get_job_success: Whether job retrieval should succeed
            error_response: Custom error response to return on failure
        """
        self._jobs = {}
        self.create_job_success = create_job_success
        self.get_job_success = get_job_success
        self.error_response = error_response or ErrorResponse(
            message="Mock error",
            error_code="MOCK_ERROR",
            category=ErrorCategory.PROCESSING_ERROR,
            severity="ERROR",
            source_component="MockComponent"
        )
        
        # Add some test jobs to the dictionary
        test_job = create_test_job()
        self._jobs[test_job.job_id] = test_job
        
        completed_job = create_completed_job()
        self._jobs[completed_job.job_id] = completed_job
        
        failed_job = create_failed_job()
        self._jobs[failed_job.job_id] = failed_job
    
    def create_job(self, file_id: str, options: Dict[str, Any]) -> tuple[Optional[ConversionJob], Optional[ErrorResponse]]:
        """
        Mock implementation of create_job that returns predetermined results.
        
        Args:
            file_id: ID of the file to process
            options: Conversion options
            
        Returns:
            Tuple with (job, error_response)
        """
        if not self.create_job_success:
            return None, self.error_response
        
        job = create_test_job()
        self._jobs[job.job_id] = job
        return job, None
    
    def get_job(self, job_id: str) -> tuple[Optional[ConversionJob], Optional[ErrorResponse]]:
        """
        Mock implementation of get_job that returns predetermined results.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            Tuple with (job, error_response)
        """
        if not self.get_job_success:
            return None, self.error_response
        
        if job_id in self._jobs:
            return self._jobs[job_id], None
        
        return None, self.error_response
    
    def get_job_status(self, job_id: str) -> tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
        """
        Mock implementation of get_job_status that returns predetermined results.
        
        Args:
            job_id: ID of the job to get status for
            
        Returns:
            Tuple with (status_dict, error_response)
        """
        job_result = self.get_job(job_id)
        if job_result[0] is None:
            return None, self.error_response
        
        return job_result[0].get_status_dict(), None
    
    def get_job_result(self, job_id: str) -> tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
        """
        Mock implementation of get_job_result that returns predetermined results.
        
        Args:
            job_id: ID of the job to get result for
            
        Returns:
            Tuple with (result_dict, error_response)
        """
        job_result = self.get_job(job_id)
        if job_result[0] is None:
            return None, self.error_response
        
        job = job_result[0]
        if not job.is_complete():
            return None, ErrorResponse(
                message="Job not completed",
                error_code="JOB_INCOMPLETE",
                category=ErrorCategory.PROCESSING_ERROR,
                severity="ERROR",
                source_component="MockJobManager"
            )
        
        result = {
            "job_id": job.job_id,
            "status": job.status.status.value,
            "output_file": "output.xlsx" if job.status.status == JobStatusEnum.COMPLETED else None,
            "error": job.status.error.to_dict() if job.status.error else None
        }
        
        return result, None