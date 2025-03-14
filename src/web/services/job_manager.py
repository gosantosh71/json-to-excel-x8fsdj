import logging  # v: built-in - For logging service operations and errors
import threading  # v: built-in - For implementing concurrent job processing
import queue  # v: built-in - For implementing the job queue
import time  # v: built-in - For implementing delays and timeouts
import uuid  # v: built-in - For generating unique job identifiers
import typing  # v: built-in - For type hints in function signatures
import datetime  # v: built-in - For tracking job creation and completion times
from typing import Dict, List, Any, Optional, Tuple  # v: built-in - For type hints in function signatures

from ..models.conversion_job import ConversionJob  # For representing and tracking conversion jobs
from ..models.job_status import JobStatusEnum  # For tracking job status
from .conversion_service import ConversionService  # For handling the actual conversion process
from .file_service import FileService  # For managing uploaded files
from .storage_service import StorageService  # For storing and retrieving job data
from ..exceptions.job_exceptions import JobException, JobCreationException, JobNotFoundException, JobProcessingException, JobQueueFullException, JobTimeoutException  # For specific job-related exceptions
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity  # For standardized error responses
from ...backend.models.error_response import ErrorCategory  # For categorizing errors
from ...backend.models.error_response import ErrorSeverity  # For indicating error severity
from ..config.web_interface_config import web_interface_config  # For accessing job management configuration

# Initialize logger
logger = logging.getLogger(__name__)

# Global constants
JOB_MANAGEMENT_CONFIG = web_interface_config['job_management']
MAX_ACTIVE_JOBS = JOB_MANAGEMENT_CONFIG['limits']['max_active_jobs']
JOB_TIMEOUT_MINUTES = JOB_MANAGEMENT_CONFIG['limits']['job_timeout_minutes']


def create_job_error_response(message: str, exception: Exception) -> ErrorResponse:
    """
    Creates a standardized error response for job-related errors.

    Args:
        message (str): A human-readable error message.
        exception (Exception): The exception that occurred.

    Returns:
        ErrorResponse: A standardized error response object
    """
    # Create an ErrorResponse with the provided message, ErrorCategory.SYSTEM_ERROR, and ErrorSeverity.ERROR
    error_response = ErrorResponse(
        message=message,
        error_code="JOB_ERROR",
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="JobManager"
    )

    # Add context information from the exception if available
    if exception:
        error_response.add_context("exception_type", type(exception).__name__)
        error_response.add_context("exception_message", str(exception))

    # Add resolution steps based on the error type
    error_response.add_resolution_step("Check the system logs for more information")
    error_response.add_resolution_step("Ensure the system has enough resources (memory, disk space)")

    # Log the error with appropriate level
    logger.error(f"Job error: {message}", exc_info=exception)

    # Return the created ErrorResponse
    return error_response


class JobManager:
    """
    Service class that manages the lifecycle of conversion jobs in the web interface,
    including creation, queuing, processing, and status tracking.
    """

    def __init__(self, conversion_service: Optional[ConversionService] = None,
                 file_service: Optional[FileService] = None,
                 storage_service: Optional[StorageService] = None):
        """
        Initializes a new JobManager instance with the necessary dependencies.

        Args:
            conversion_service (Optional[ConversionService]): Conversion service instance.
            file_service (Optional[FileService]): File service instance.
            storage_service (Optional[StorageService]): Storage service instance.
        """
        # Initialize _conversion_service with the provided ConversionService instance or create a new one if not provided
        self._conversion_service = conversion_service or ConversionService()
        # Initialize _file_service with the provided FileService instance or create a new one if not provided
        self._file_service = file_service or FileService()
        # Initialize _storage_service with the provided StorageService instance or create a new one if not provided
        self._storage_service = storage_service or StorageService()
        # Initialize _job_queue as a new Queue instance
        self._job_queue: queue.Queue[ConversionJob] = queue.Queue(maxsize=MAX_ACTIVE_JOBS)
        # Initialize _worker_thread as None
        self._worker_thread: Optional[threading.Thread] = None
        # Initialize _running as False
        self._running: bool = False
        # Initialize _active_jobs as an empty dictionary
        self._active_jobs: Dict[str, ConversionJob] = {}
        # Initialize _job_start_times as an empty dictionary
        self._job_start_times: Dict[str, datetime.datetime] = {}
        # Set up logging for the job manager
        logger.info("JobManager initialized")
        # Start the worker thread
        self.start()

    def start(self) -> None:
        """
        Starts the job manager worker thread.
        """
        # If _running is already True, log a warning and return
        if self._running:
            logger.warning("JobManager is already running")
            return
        # Set _running to True
        self._running = True
        # Create a new Thread that calls _worker_loop()
        self._worker_thread = threading.Thread(target=self._worker_loop)
        # Set the thread as a daemon thread
        self._worker_thread.daemon = True
        # Start the thread
        self._worker_thread.start()
        # Log that the job manager has started
        logger.info("JobManager started")

    def stop(self) -> None:
        """
        Stops the job manager worker thread.
        """
        # Set _running to False
        self._running = False
        # If _worker_thread is running, wait for it to finish
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join()
        # Set _worker_thread to None
        self._worker_thread = None
        # Log that the job manager has stopped
        logger.info("JobManager stopped")

    def create_job(self, file_id: str, options: Dict[str, Any]) -> Tuple[Optional[ConversionJob], Optional[ErrorResponse]]:
        """
        Creates a new conversion job and adds it to the processing queue.

        Args:
            file_id (str): The ID of the uploaded file.
            options (Dict[str, Any]): The conversion options.

        Returns:
            Tuple[Optional[ConversionJob], Optional[ErrorResponse]]: The created job and optional error.
        """
        try:
            # Check if the number of active jobs is at or above MAX_ACTIVE_JOBS
            if self._job_queue.full():
                # If queue is full, raise JobQueueFullException
                raise JobQueueFullException(queue_limit=MAX_ACTIVE_JOBS)
            # Get the uploaded file using _file_service.get_upload(file_id)
            upload_file, error = self._file_service.get_upload(file_id)
            # If file not found, return None and the error
            if error:
                return None, error
            # Create a new ConversionJob with the upload_file and options
            job = ConversionJob(input_file=upload_file, options=self._conversion_service.process_form_data(options))
            # Save the job using _storage_service.save_conversion_job(job)
            success, error = self._storage_service.save_conversion_job(job)
            if error:
                return None, error
            # Add the job to the _job_queue
            self._job_queue.put(job)
            # Log that a new job has been created and queued
            logger.info(f"New job created and queued: {job.job_id}")
            # Return the job and None for error
            return job, None
        except JobQueueFullException as e:
            error = create_job_error_response(message=str(e), exception=e)
            return None, error
        except Exception as e:
            error = create_job_error_response(message="Failed to create job", exception=e)
            return None, error

    def get_job(self, job_id: str) -> Tuple[Optional[ConversionJob], Optional[ErrorResponse]]:
        """
        Retrieves a job by its ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            Tuple[Optional[ConversionJob], Optional[ErrorResponse]]: The job and optional error.
        """
        # Get the job using _storage_service.get_conversion_job(job_id)
        job, error = self._storage_service.get_conversion_job(job_id)
        # Return the job and any error response
        return job, error

    def get_job_status(self, job_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
        """
        Gets the current status of a job.

        Args:
            job_id (str): The ID of the job.

        Returns:
            Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]: Job status dictionary and optional error.
        """
        # Get the job using get_job(job_id)
        job, error = self.get_job(job_id)
        # If job not found, return None and the error
        if error:
            return None, error
        # Get the job status dictionary using job.get_status_dict()
        status_dict = job.status.to_dict()
        # Return the status dictionary and None for error
        return status_dict, None

    def get_job_result(self, job_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
        """
        Gets the result of a completed job.

        Args:
            job_id (str): The ID of the job.

        Returns:
            Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]: Job result dictionary and optional error.
        """
        # Get the job using get_job(job_id)
        job, error = self.get_job(job_id)
        # If job not found, return None and the error
        if error:
            return None, error
        # Check if the job is complete using job.is_complete()
        if not job.is_complete():
            # If not complete, create an error response and return None and the error
            error = create_job_error_response(message="Job is not complete", exception=JobProcessingException(job_id=job_id, message="Job is not complete"))
            return None, error
        # Get the job result using job.get_result()
        result = job.get_result()
        # Return the result dictionary and None for error
        return result, None

    def get_output_file(self, job_id: str) -> Tuple[Optional[str], Optional[str], Optional[ErrorResponse]]:
        """
        Gets the output file path for a completed job.

        Args:
            job_id (str): The ID of the job.

        Returns:
            Tuple[Optional[str], Optional[str], Optional[ErrorResponse]]: Output file path, file name, and optional error.
        """
        # Call _conversion_service.get_output_file(job_id)
        output_file_path, output_file_name, error = self._conversion_service.get_output_file(job_id)
        # Return the output file path, file name, and any error response
        return output_file_path, output_file_name, error

    def cancel_job(self, job_id: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Cancels a pending or in-progress job.

        Args:
            job_id (str): The ID of the job.

        Returns:
            Tuple[bool, Optional[ErrorResponse]]: Success flag and optional error.
        """
        # Get the job using get_job(job_id)
        job, error = self.get_job(job_id)
        # If job not found, return False and the error
        if error:
            return False, error
        # Check if the job is already complete using job.is_complete()
        if job.is_complete():
            # If complete, create an error response and return False and the error
            error = create_job_error_response(message="Job is already complete and cannot be cancelled", exception=JobProcessingException(job_id=job_id, message="Job is already complete and cannot be cancelled"))
            return False, error
        # Remove the job from _active_jobs if present
        if job_id in self._active_jobs:
            del self._active_jobs[job_id]
        # Create an error response for cancellation
        cancellation_error = ErrorResponse(message="Job cancelled by user", error_code="JOB_CANCELLED", category=ErrorCategory.SYSTEM_ERROR, severity=ErrorSeverity.WARNING, source_component="JobManager")
        # Set the job as failed with the cancellation error
        job.set_failed(cancellation_error, "Job cancelled by user")
        # Update the job in storage
        success, error = self._storage_service.update_conversion_job(job)
        if error:
            return False, error
        # Log that the job has been cancelled
        logger.info(f"Job cancelled: {job_id}")
        # Return True and None for error
        return True, None

    def list_jobs(self, status: Optional[JobStatusEnum] = None) -> List[Dict[str, Any]]:
        """
        Lists all jobs with optional filtering.

        Args:
            status (Optional[JobStatusEnum]): The status to filter jobs by.

        Returns:
            List[Dict[str, Any]]: List of job dictionaries.
        """
        # Get all jobs using _storage_service.list_conversion_jobs()
        all_jobs = self._storage_service.list_conversion_jobs()
        # Create an empty result list
        result = []
        # For each job, check if it matches the status filter if provided
        for job in all_jobs:
            if status is None or job.status.status == status:
                # If it matches or no filter is provided, add job.to_dict() to the result list
                result.append(job.to_dict())
        # Return the list of job dictionaries
        return result

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the job queue.

        Returns:
            Dict[str, Any]: Queue status information.
        """
        # Get the current queue size using _job_queue.qsize()
        queue_size = self._job_queue.qsize()
        # Count the number of active jobs in _active_jobs
        active_jobs = len(self._active_jobs)
        # Create a status dictionary with queue_size, active_jobs, and max_active_jobs
        status = {
            "queue_size": queue_size,
            "active_jobs": active_jobs,
            "max_active_jobs": MAX_ACTIVE_JOBS
        }
        # Return the status dictionary
        return status

    def _worker_loop(self) -> None:
        """
        Main worker loop that processes jobs from the queue.
        """
        # Log when the worker loop starts
        logger.info("Worker loop started")
        # While _running is True:
        while self._running:
            try:
                # Try to get a job from _job_queue with a timeout
                job = self._job_queue.get(timeout=1)
                # If a job is retrieved, process it using _process_job(job)
                self._process_job(job)
                # Indicate that the job is complete
                self._job_queue.task_done()
            except queue.Empty:
                # Handle queue.Empty exception
                pass
            except Exception as e:
                # Handle any exceptions and log them
                logger.error(f"Error in worker loop: {str(e)}", exc_info=True)
            finally:
                # Check for job timeouts
                self._check_job_timeouts()
                # Sleep briefly to prevent CPU overuse
                time.sleep(0.1)
        # Log when the worker loop exits
        logger.info("Worker loop exited")

    def _process_job(self, job: ConversionJob) -> None:
        """
        Processes a single conversion job.

        Args:
            job (ConversionJob): The job to process.
        """
        # Log the start of job processing
        logger.info(f"Processing job: {job.job_id}")
        # Add the job to _active_jobs with job_id as key
        self._active_jobs[job.job_id] = job
        # Record the start time in _job_start_times
        self._job_start_times[job.job_id] = datetime.datetime.now()
        try:
            # Try to process the job using _conversion_service.process_conversion_job(job)
            success = self._conversion_service.process_conversion_job(job)
            # If processing succeeds, log success
            if success:
                logger.info(f"Job processed successfully: {job.job_id}")
            else:
                # If processing fails, log the failure
                logger.error(f"Job processing failed: {job.job_id}")
        except Exception as e:
            # Handle any exceptions and log them
            logger.error(f"Error processing job {job.job_id}: {str(e)}", exc_info=True)
            # Create an error response
            error = create_job_error_response(message="Error processing job", exception=e)
            # Set the job as failed with the error
            job.set_failed(error)
        finally:
            # Remove the job from _active_jobs and _job_start_times
            if job.job_id in self._active_jobs:
                del self._active_jobs[job.job_id]
            if job.job_id in self._job_start_times:
                del self._job_start_times[job.job_id]
            # Update the job in storage using _storage_service.update_conversion_job(job)
            self._storage_service.update_conversion_job(job)

    def _check_job_timeouts(self) -> None:
        """
        Checks for and handles jobs that have exceeded their timeout.
        """
        # Get the current time
        now = datetime.datetime.now()
        # Create a list of job_ids to check
        timed_out_jobs = []
        # For each job_id in _job_start_times:
        for job_id, start_time in self._job_start_times.items():
            # Calculate how long the job has been running
            duration = now - start_time
            # If the duration exceeds JOB_TIMEOUT_MINUTES, handle the timeout
            if duration.total_seconds() > JOB_TIMEOUT_MINUTES * 60:
                timed_out_jobs.append(job_id)

        # For each timed out job:
        for job_id in timed_out_jobs:
            try:
                # Get the job using get_job(job_id)
                job, error = self.get_job(job_id)
                if not job:
                    logger.warning(f"Job not found while checking timeout: {job_id}")
                    continue

                # Create a timeout error response
                timeout_error = ErrorResponse(message=f"Job exceeded timeout of {JOB_TIMEOUT_MINUTES} minutes", error_code="JOB_TIMEOUT", category=ErrorCategory.SYSTEM_ERROR, severity=ErrorSeverity.ERROR, source_component="JobManager")
                # Set the job as failed with the timeout error
                job.set_failed(timeout_error)
            except Exception as e:
                logger.error(f"Error handling timeout for job {job_id}: {str(e)}", exc_info=True)
            finally:
                # Remove the job from _active_jobs and _job_start_times
                if job_id in self._active_jobs:
                    del self._active_jobs[job_id]
                if job_id in self._job_start_times:
                    del self._job_start_times[job_id]
                # Update the job in storage
                self._storage_service.update_conversion_job(job)
                # Log that the job has timed out
                logger.info(f"Job timed out: {job_id}")

    def __del__(self) -> None:
        """
        Destructor that ensures the worker thread is stopped.
        """
        # Call stop() to ensure the worker thread is properly terminated
        self.stop()