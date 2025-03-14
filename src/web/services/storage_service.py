"""
Provides a service layer for managing file storage operations in the web interface of the JSON to Excel Conversion Tool.
This service handles the storage, retrieval, and management of uploaded JSON files and generated Excel files, with a focus
on security, error handling, and proper resource management.
"""

import os
import json
import datetime
import typing
import threading
import time
from werkzeug.datastructures import FileStorage

from ..config.upload_config import upload_config
from ..config.web_interface_config import web_interface_config
from ...backend.logger import get_logger
from ..models.upload_file import UploadFile
from ..models.conversion_job import ConversionJob
from ...backend.adapters.file_system_adapter import FileSystemAdapter
from ..utils.file_utils import FileManager
from ..utils.path_utils import ensure_upload_directory, get_upload_path, is_path_within_directory
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..exceptions.file_exceptions import FileStorageException, FileDeletionException

# Initialize logger
logger = get_logger(__name__)

# Configuration constants
UPLOAD_FOLDER = upload_config['upload_folder']
MAX_FILE_SIZE = upload_config['max_file_size']
ALLOWED_EXTENSIONS = upload_config['allowed_extensions']
FILE_CLEANUP_CONFIG = upload_config['file_cleanup']
JOB_CLEANUP_CONFIG = web_interface_config['job_management']['cleanup']


def create_storage_error_response(message: str, exception: Exception, 
                                 category: ErrorCategory, severity: ErrorSeverity) -> ErrorResponse:
    """
    Creates a standardized error response for storage-related errors.
    
    Args:
        message: Error message
        exception: The exception that occurred
        category: Error category
        severity: Error severity
        
    Returns:
        A standardized error response object
    """
    # Create error response with provided details
    error_response = ErrorResponse(
        message=message,
        error_code="STORAGE_ERROR",
        category=category,
        severity=severity,
        source_component="StorageService",
        context={"exception": str(exception)} if exception else {},
        resolution_steps=["Check file permissions", "Ensure disk space is available"]
    )
    
    # Add context information from the exception if available
    if isinstance(exception, FileStorageException) or isinstance(exception, FileDeletionException):
        error_response.add_context("file_path", getattr(exception, "file_path", "unknown"))
    
    # Add resolution steps based on error type
    if isinstance(exception, FileStorageException):
        error_response.add_resolution_step("Verify the upload directory is writable")
    elif isinstance(exception, FileDeletionException):
        error_response.add_resolution_step("Check if the file is in use by another process")
    
    # Log the error with appropriate level
    if severity == ErrorSeverity.ERROR or severity == ErrorSeverity.CRITICAL:
        logger.error(f"Storage error: {message}", exc_info=exception is not None)
    else:
        logger.warning(f"Storage warning: {message}")
        
    return error_response


class StorageService:
    """
    Service class that manages file storage operations for the web interface, including uploads, 
    retrievals, and cleanup.
    """
    
    def __init__(self):
        """
        Initializes the StorageService with necessary adapters and ensures storage directories exist.
        """
        self._file_system_adapter = FileSystemAdapter(base_directory=UPLOAD_FOLDER)
        self._file_manager = FileManager()
        
        # Ensure upload directory exists
        ensure_upload_directory()
        
        # Initialize caches for uploads and jobs
        self._upload_cache = {}  # file_id -> UploadFile
        self._job_cache = {}     # job_id -> ConversionJob
        
        # Initialize cleanup thread
        self._cleanup_thread = None
        self._cleanup_running = False
        
        # Start cleanup thread if enabled
        if FILE_CLEANUP_CONFIG.get('enabled', False) or JOB_CLEANUP_CONFIG.get('enabled', False):
            self.start_cleanup_thread()
            
        logger.info("StorageService initialized")
        
    def save_uploaded_file(self, file: FileStorage) -> typing.Tuple[typing.Optional[UploadFile], typing.Optional[ErrorResponse]]:
        """
        Saves an uploaded file and creates an UploadFile record.
        
        Args:
            file: The uploaded file to save
            
        Returns:
            The created UploadFile instance and optional error
        """
        if not file:
            error = ErrorResponse(
                message="No file provided",
                error_code="EMPTY_FILE",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService"
            )
            return None, error
        
        try:
            # Create UploadFile from werkzeug FileStorage
            upload_file = UploadFile.from_werkzeug_file(file)
            
            # Validate the file
            is_valid, error = upload_file.validate()
            if not is_valid:
                # Delete the physical file if validation fails
                upload_file.delete_file()
                return None, error
            
            # Add to cache
            self._upload_cache[upload_file.file_id] = upload_file
            
            logger.info(f"File saved successfully: {upload_file.original_filename} (ID: {upload_file.file_id})")
            return upload_file, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Failed to save uploaded file: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return None, error
    
    def get_upload_file(self, file_id: str) -> typing.Tuple[typing.Optional[UploadFile], typing.Optional[ErrorResponse]]:
        """
        Retrieves an UploadFile by its ID.
        
        Args:
            file_id: ID of the file to retrieve
            
        Returns:
            The UploadFile instance and optional error
        """
        upload_file = self._upload_cache.get(file_id)
        
        if not upload_file:
            error = ErrorResponse(
                message=f"File not found with ID: {file_id}",
                error_code="FILE_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"file_id": file_id}
            )
            return None, error
            
        return upload_file, None
    
    def delete_upload_file(self, file_id: str) -> typing.Tuple[bool, typing.Optional[ErrorResponse]]:
        """
        Deletes an uploaded file by its ID.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            Success flag and optional error
        """
        upload_file, error = self.get_upload_file(file_id)
        if not upload_file:
            return False, error
            
        try:
            # Delete the physical file
            if not upload_file.delete_file():
                error = ErrorResponse(
                    message=f"Failed to delete file: {upload_file.file_path}",
                    error_code="FILE_DELETE_ERROR",
                    category=ErrorCategory.SYSTEM_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="StorageService",
                    context={"file_id": file_id, "file_path": upload_file.file_path}
                )
                return False, error
                
            # Remove from cache
            del self._upload_cache[file_id]
            
            logger.info(f"File deleted successfully: ID {file_id}, path {upload_file.file_path}")
            return True, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Error deleting file: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, error
    
    def save_conversion_job(self, job: ConversionJob) -> typing.Tuple[bool, typing.Optional[ErrorResponse]]:
        """
        Saves a conversion job to the storage service.
        
        Args:
            job: The conversion job to save
            
        Returns:
            Success flag and optional error
        """
        if not job:
            error = ErrorResponse(
                message="No job provided",
                error_code="EMPTY_JOB",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService"
            )
            return False, error
            
        try:
            # Convert to dictionary and store in cache
            self._job_cache[job.job_id] = job
            
            logger.info(f"Job saved successfully: ID {job.job_id}")
            return True, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Failed to save job: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, error
    
    def get_conversion_job(self, job_id: str) -> typing.Tuple[typing.Optional[ConversionJob], typing.Optional[ErrorResponse]]:
        """
        Retrieves a conversion job by its ID.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            The ConversionJob instance and optional error
        """
        job = self._job_cache.get(job_id)
        
        if not job:
            error = ErrorResponse(
                message=f"Job not found with ID: {job_id}",
                error_code="JOB_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job_id}
            )
            return None, error
            
        return job, None
    
    def update_conversion_job(self, job: ConversionJob) -> typing.Tuple[bool, typing.Optional[ErrorResponse]]:
        """
        Updates an existing conversion job.
        
        Args:
            job: The job to update
            
        Returns:
            Success flag and optional error
        """
        if not job:
            error = ErrorResponse(
                message="No job provided",
                error_code="EMPTY_JOB",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService"
            )
            return False, error
            
        if job.job_id not in self._job_cache:
            error = ErrorResponse(
                message=f"Job not found with ID: {job.job_id}",
                error_code="JOB_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job.job_id}
            )
            return False, error
            
        try:
            # Update the job in the cache
            self._job_cache[job.job_id] = job
            
            logger.info(f"Job updated successfully: ID {job.job_id}")
            return True, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Failed to update job: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, error
    
    def delete_conversion_job(self, job_id: str) -> typing.Tuple[bool, typing.Optional[ErrorResponse]]:
        """
        Deletes a conversion job by its ID.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            Success flag and optional error
        """
        if job_id not in self._job_cache:
            error = ErrorResponse(
                message=f"Job not found with ID: {job_id}",
                error_code="JOB_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job_id}
            )
            return False, error
            
        try:
            # Get the job
            job = self._job_cache[job_id]
            
            # Delete output file if exists
            if job.output_file_path and os.path.exists(job.output_file_path):
                try:
                    os.remove(job.output_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete output file for job {job_id}: {str(e)}")
            
            # Remove from cache
            del self._job_cache[job_id]
            
            logger.info(f"Job deleted successfully: ID {job_id}")
            return True, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Error deleting job: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, error
    
    def list_upload_files(self) -> typing.List[UploadFile]:
        """
        Lists all uploaded files in the storage service.
        
        Returns:
            List of UploadFile instances
        """
        return list(self._upload_cache.values())
    
    def list_conversion_jobs(self) -> typing.List[ConversionJob]:
        """
        Lists all conversion jobs in the storage service.
        
        Returns:
            List of ConversionJob instances
        """
        return list(self._job_cache.values())
    
    def save_output_file(self, job_id: str, file_path: str, file_name: str) -> typing.Tuple[bool, typing.Optional[ErrorResponse]]:
        """
        Saves an output file for a conversion job.
        
        Args:
            job_id: ID of the job
            file_path: Path to the output file
            file_name: Name of the output file
            
        Returns:
            Success flag and optional error
        """
        # Get the job
        job, error = self.get_conversion_job(job_id)
        if not job:
            return False, error
            
        # Validate that the file exists
        if not os.path.exists(file_path):
            error = ErrorResponse(
                message=f"Output file not found: {file_path}",
                error_code="FILE_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job_id, "file_path": file_path}
            )
            return False, error
            
        try:
            # Update the job with output file information
            job.output_file_path = file_path
            job.output_file_name = file_name
            
            # Update the job in storage
            success, error = self.update_conversion_job(job)
            if not success:
                return False, error
            
            logger.info(f"Output file saved for job {job_id}: {file_path}")
            return True, None
            
        except Exception as e:
            error = create_storage_error_response(
                message=f"Failed to save output file: {str(e)}",
                exception=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, error
    
    def get_output_file(self, job_id: str) -> typing.Tuple[typing.Optional[str], typing.Optional[str], typing.Optional[ErrorResponse]]:
        """
        Gets the output file path for a conversion job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Output file path, file name, and optional error
        """
        # Get the job
        job, error = self.get_conversion_job(job_id)
        if not job:
            return None, None, error
            
        # Check if the job has an output file
        if not job.output_file_path or not job.output_file_name:
            error = ErrorResponse(
                message=f"No output file available for job: {job_id}",
                error_code="NO_OUTPUT_FILE",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job_id}
            )
            return None, None, error
            
        # Validate that the file exists
        if not os.path.exists(job.output_file_path):
            error = ErrorResponse(
                message=f"Output file not found: {job.output_file_path}",
                error_code="FILE_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="StorageService",
                context={"job_id": job_id, "file_path": job.output_file_path}
            )
            return None, None, error
            
        return job.output_file_path, job.output_file_name, None
    
    def cleanup_old_files(self) -> typing.Tuple[int, typing.List[str]]:
        """
        Cleans up old uploaded files based on configuration.
        
        Returns:
            Count of deleted files and list of deleted file paths
        """
        if not FILE_CLEANUP_CONFIG.get('enabled', False):
            logger.debug("File cleanup is disabled")
            return 0, []
            
        try:
            # Get max age from config
            max_age_minutes = FILE_CLEANUP_CONFIG.get('max_age_minutes', 60)
            
            # Clean up files
            count, deleted_files = self._file_manager.cleanup_old_files(max_age_minutes)
            
            # Update upload cache to remove deleted files
            for file_path in deleted_files:
                for file_id, upload_file in list(self._upload_cache.items()):
                    if upload_file.file_path == file_path:
                        del self._upload_cache[file_id]
                        break
            
            logger.info(f"Cleaned up {count} old files")
            return count, deleted_files
            
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return 0, []
    
    def cleanup_old_jobs(self) -> typing.Tuple[int, typing.List[str]]:
        """
        Cleans up old conversion jobs based on configuration.
        
        Returns:
            Count of deleted jobs and list of deleted job IDs
        """
        if not JOB_CLEANUP_CONFIG.get('enabled', False):
            logger.debug("Job cleanup is disabled")
            return 0, []
            
        try:
            # Get retention period from config
            retention_minutes = JOB_CLEANUP_CONFIG.get('completed_job_retention_minutes', 60)
            
            # Calculate cutoff time
            cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=retention_minutes)
            
            # Track deleted jobs
            deleted_count = 0
            deleted_job_ids = []
            
            # Iterate through jobs
            for job_id, job in list(self._job_cache.items()):
                # Check if job is completed and older than cutoff
                if job.is_complete() and job.completed_at and job.completed_at < cutoff_time:
                    # Delete the job
                    success, _ = self.delete_conversion_job(job_id)
                    if success:
                        deleted_count += 1
                        deleted_job_ids.append(job_id)
            
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return deleted_count, deleted_job_ids
            
        except Exception as e:
            logger.error(f"Error during job cleanup: {str(e)}")
            return 0, []
    
    def start_cleanup_thread(self) -> None:
        """
        Starts a background thread for periodic cleanup operations.
        """
        if self._cleanup_running:
            logger.warning("Cleanup thread is already running")
            return
            
        self._cleanup_running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        
        logger.info("Cleanup thread started")
    
    def stop_cleanup_thread(self) -> None:
        """
        Stops the background cleanup thread.
        """
        self._cleanup_running = False
        
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
            
        self._cleanup_thread = None
        logger.info("Cleanup thread stopped")
    
    def _cleanup_worker(self) -> None:
        """
        Worker function for the background cleanup thread.
        """
        logger.info("Cleanup worker thread started")
        
        while self._cleanup_running:
            try:
                # Run file cleanup
                if FILE_CLEANUP_CONFIG.get('enabled', False):
                    self.cleanup_old_files()
                
                # Run job cleanup
                if JOB_CLEANUP_CONFIG.get('enabled', False):
                    self.cleanup_old_jobs()
                    
            except Exception as e:
                logger.error(f"Error in cleanup worker: {str(e)}")
            
            # Sleep for the configured interval
            cleanup_interval = JOB_CLEANUP_CONFIG.get('interval_minutes', 30) * 60  # Convert to seconds
            time.sleep(cleanup_interval)
            
        logger.info("Cleanup worker thread stopped")
    
    def __del__(self):
        """
        Destructor that ensures the cleanup thread is stopped.
        """
        self.stop_cleanup_thread()