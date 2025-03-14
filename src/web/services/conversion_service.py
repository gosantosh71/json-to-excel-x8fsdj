import logging  # v: built-in - For logging service operations and errors
import os  # v: built-in - For file path operations
from typing import Dict, List, Any, Optional, Tuple  # v: built-in - For type hints in function signatures
from uuid import uuid4  # v: built-in - For generating unique output filenames
from datetime import datetime  # v: built-in - For tracking conversion timing

from ..models.conversion_job import ConversionJob  # For representing and tracking conversion jobs
from ..models.conversion_options import ConversionOptions  # For configuring conversion settings
from ..models.job_status import JobStatusEnum  # For tracking job status
from ..backend_interface.conversion_client import ConversionClient  # For interfacing with backend conversion functionality
from .file_service import FileService  # For managing uploaded files
from .storage_service import StorageService  # For managing output file storage
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity  # For standardized error handling
from ..config.web_interface_config import web_interface_config  # For accessing web interface configuration

# Initialize logger
logger = logging.getLogger(__name__)

# Global constants
OUTPUT_DIR = web_interface_config['conversion']['output_directory']
MAX_FILE_SIZE_MB = web_interface_config['conversion']['max_file_size_mb']


def create_conversion_error(message: str, exception: Exception, category: ErrorCategory, severity: ErrorSeverity) -> ErrorResponse:
    """
    Creates a standardized error response for conversion-related errors.

    Args:
        message: A human-readable error message.
        exception: The exception that occurred during the conversion process.
        category: The category of the error (e.g., VALIDATION_ERROR, TRANSFORMATION_ERROR).
        severity: The severity of the error (e.g., ERROR, WARNING).

    Returns:
        ErrorResponse: A standardized error response object.
    """
    error_response = ErrorResponse(
        message=message,
        error_code="CONVERSION_ERROR",  # Generic conversion error code
        category=category,
        severity=severity,
        source_component="ConversionService"
    )

    # Add context information from the exception if available
    if exception:
        error_response.add_context("exception_type", type(exception).__name__)
        error_response.add_context("exception_message", str(exception))

    # Add resolution steps based on the error type
    if category == ErrorCategory.VALIDATION_ERROR:
        error_response.add_resolution_step("Check the input JSON file for syntax errors")
        error_response.add_resolution_step("Ensure the JSON structure matches the expected format")
    elif category == ErrorCategory.TRANSFORMATION_ERROR:
        error_response.add_resolution_step("Review the transformation settings")
        error_response.add_resolution_step("Simplify the JSON structure if possible")
    elif category == ErrorCategory.SYSTEM_ERROR:
        error_response.add_resolution_step("Check the system logs for more information")
        error_response.add_resolution_step("Ensure the system has enough resources (memory, disk space)")

    # Log the error with appropriate level based on severity
    if severity == ErrorSeverity.ERROR or severity == ErrorSeverity.CRITICAL:
        logger.error(f"Conversion error: {message}", exc_info=exception)
    else:
        logger.warning(f"Conversion warning: {message}", exc_info=exception)

    return error_response


class ConversionService:
    """
    Service class that coordinates JSON to Excel conversion operations in the web interface,
    handling job processing, validation, and error management.
    """

    def __init__(self, file_service: Optional[FileService] = None, storage_service: Optional[StorageService] = None,
                 conversion_client: Optional[ConversionClient] = None):
        """
        Initializes a new ConversionService instance with the necessary dependencies.

        Args:
            file_service: Optional FileService instance for managing uploaded files.
            storage_service: Optional StorageService instance for managing output file storage.
            conversion_client: Optional ConversionClient instance for interfacing with backend conversion functionality.
        """
        self._file_service = file_service or FileService()
        self._storage_service = storage_service or StorageService()
        self._conversion_client = conversion_client or ConversionClient(MAX_FILE_SIZE_MB)
        self._logger = logger
        self._logger.info("ConversionService initialized")

    def process_conversion_job(self, job: ConversionJob) -> bool:
        """
        Processes a conversion job, updating its status throughout the conversion process.

        Args:
            job: The ConversionJob object.

        Returns:
            bool: Success flag indicating whether the conversion was successful.
        """
        self._logger.info(f"Starting processing conversion job: {job.job_id}")
        job.update_status(JobStatusEnum.VALIDATING, 10, "Validating input JSON file")

        input_path = job.input_file.file_path
        validation_result, validation_details, error = self.validate_conversion_input(job)

        if not validation_result:
            job.set_failed(error, "JSON validation failed")
            self._logger.error(f"JSON validation failed for job {job.job_id}: {error.message}")
            return False

        job.update_status(JobStatusEnum.PROCESSING, 25, "Converting JSON to Excel")

        output_path, output_filename = self.generate_output_path(job.job_id, job.input_file.original_filename)
        options = job.options.to_excel_options()

        success, conversion_summary, error = self._conversion_client.convert_file(input_path, output_path, options.to_dict())

        if success:
            job.set_completed(output_path, output_filename, conversion_summary, "Conversion completed successfully")
            self._logger.info(f"Conversion job completed successfully: {job.job_id}")
            return True
        else:
            job.set_failed(error, "Conversion failed")
            self._logger.error(f"Conversion job failed: {job.job_id}: {error.message}")
            return False

    def validate_conversion_input(self, job: ConversionJob) -> Tuple[bool, dict, Optional[ErrorResponse]]:
        """
        Validates a JSON file without performing the full conversion.

        Args:
            job: The ConversionJob object.

        Returns:
            Tuple[bool, dict, Optional[ErrorResponse]]: Validation result, details, and optional error.
        """
        self._logger.info(f"Starting validation for job {job.job_id}")
        input_path = job.input_file.file_path

        success, details = self._conversion_client.validate_file(input_path)

        if success:
            return True, details, None
        else:
            error = create_conversion_error(
                message="Invalid JSON file",
                exception=Exception(details.get("message", "Unknown validation error")),
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, details, error

    def convert_file(self, input_path: str, output_path: str, options: Optional[ConversionOptions] = None) -> Tuple[bool, dict, Optional[ErrorResponse]]:
        """
        Converts a JSON file to Excel format without using the job system.

        Args:
            input_path: Path to the input JSON file.
            output_path: Path to the output Excel file.
            options: Optional ConversionOptions object.

        Returns:
            Tuple[bool, dict, Optional[ErrorResponse]]: Success flag, conversion summary, and optional error.
        """
        self._logger.info("Starting direct file conversion")

        if not os.path.exists(input_path):
            error = create_conversion_error(
                message=f"Input file not found: {input_path}",
                exception=FileNotFoundError(input_path),
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR
            )
            return False, {}, error

        if options is None:
            options = ConversionOptions()

        excel_options = options.to_excel_options()

        success, conversion_summary, error = self._conversion_client.convert_file(input_path, output_path, excel_options.to_dict())

        if success:
            return True, conversion_summary, None
        else:
            return False, {}, error

    def get_output_file(self, job_id: str) -> Tuple[Optional[str], Optional[str], Optional[ErrorResponse]]:
        """
        Gets the output file path for a completed conversion job.

        Args:
            job_id: The ID of the conversion job.

        Returns:
            Tuple[Optional[str], Optional[str], Optional[ErrorResponse]]: Output file path, file name, and optional error.
        """
        job, error = self._storage_service.get_conversion_job(job_id)
        if error:
            return None, None, error

        return job.output_file_path, job.output_file_name, None

    def generate_output_path(self, job_id: str, original_filename: str) -> Tuple[str, str]:
        """
        Generates a unique output file path for a conversion job.

        Args:
            job_id: The ID of the conversion job.
            original_filename: The original filename of the input file.

        Returns:
            Tuple[str, str]: Output file path and output file name.
        """
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        filename = f"{job_id}_{os.path.splitext(original_filename)[0]}.xlsx"
        output_path = os.path.join(OUTPUT_DIR, filename)

        return output_path, filename

    def process_form_data(self, form_data: Dict[str, Any]) -> ConversionOptions:
        """
        Processes web form data into conversion options.

        Args:
            form_data: Dictionary containing form data.

        Returns:
            ConversionOptions: Processed conversion options.
        """
        return ConversionOptions.from_form_data(form_data)