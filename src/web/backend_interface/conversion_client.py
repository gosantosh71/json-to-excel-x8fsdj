"""
Implements a client for the web application to interact with the backend conversion services of the JSON to Excel Conversion Tool.
This module extends the ServiceClient to provide specialized conversion functionality, handling file uploads, JSON validation, and Excel generation while abstracting the backend implementation details from the web interface.
"""

import logging  # v: built-in - For logging client operations and errors
import os  # v: built-in - For file path operations
from typing import Dict, List, Any, Optional, Tuple  # v: built-in - For type hints in function signatures

from .service_client import ServiceClient  # For base client interaction with backend services
from ..models.conversion_options import ConversionOptions  # For handling conversion configuration options
from ..models.conversion_job import ConversionJob  # For tracking conversion job status and results
from ..models.job_status import JobStatusEnum  # For defining job status values
from ...backend.models.error_response import ErrorResponse  # For handling error responses from backend services

# Initialize logger
logger = logging.getLogger(__name__)


class ConversionClient:
    """
    A client class that extends ServiceClient to provide specialized conversion functionality for the web interface.
    """

    def __init__(self, max_file_size_mb: Optional[int] = None, max_nesting_level: Optional[int] = None):
        """
        Initializes a new ConversionClient instance with the necessary dependencies.

        Args:
            max_file_size_mb: Maximum file size in MB.
            max_nesting_level: Maximum nesting level.
        """
        # Initialize _service_client with a new ServiceClient instance using provided parameters
        self._service_client = ServiceClient(max_file_size_mb=max_file_size_mb, max_nesting_level=max_nesting_level)
        # Set up logging for the conversion client
        self._logger = logger
        self._logger.info("ConversionClient initialized")

    def process_conversion_job(self, job: ConversionJob) -> bool:
        """
        Processes a conversion job, updating its status throughout the conversion process.

        Args:
            job: The ConversionJob object.

        Returns:
            Success flag indicating whether the conversion was successful
        """
        # Log the start of job processing
        self._logger.info(f"Starting processing conversion job: {job.job_id}")

        # Update job status to VALIDATING
        job.update_status(JobStatusEnum.VALIDATING, 10, "Validating input JSON file")

        # Validate the input JSON file using _service_client.validate_json_file
        success, validation_details = self._service_client.validate_json_file(job.input_file.file_path)
        if not success:
            # If validation fails, set job as failed with error details and return False
            error_response = self.create_error_response(validation_details)
            job.set_failed(error_response, "JSON validation failed")
            self._logger.error(f"JSON validation failed for job {job.job_id}: {error_response.message}")
            return False

        # Update job status to PROCESSING
        job.update_status(JobStatusEnum.PROCESSING, 25, "Converting JSON to Excel")

        # Get input file path and output file path from job
        input_path = job.input_file.file_path
        output_path = os.path.join(os.path.dirname(input_path), f"{os.path.splitext(os.path.basename(input_path))[0]}.xlsx")

        # Get conversion options from job
        options = job.options.to_dict()

        # Convert the file using _service_client.convert_file
        success, conversion_summary, error_details = self._service_client.convert_file(input_path, output_path, options)
        if success:
            # If conversion succeeds, set job as completed with output details and return True
            job.set_completed(output_path, os.path.basename(output_path), conversion_summary, "Conversion completed successfully")
            self._logger.info(f"Conversion job completed successfully: {job.job_id}")
            return True
        else:
            # If conversion fails, set job as failed with error details and return False
            error_response = self.create_error_response(error_details)
            job.set_failed(error_response, "Conversion failed")
            self._logger.error(f"Conversion job failed: {job.job_id}: {error_response.message}")
            return False

    def validate_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates a JSON file without performing the full conversion.

        Args:
            file_path: The path to the JSON file.

        Returns:
            Validation result (success/failure) and validation details or error
        """
        # Log the start of file validation
        self._logger.info(f"Validating JSON file: {file_path}")

        # Call _service_client.validate_json_file with file_path
        success, details = self._service_client.validate_json_file(file_path)

        # Return the validation result and details
        return success, details

    def validate_json_string(self, json_string: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates a JSON string without performing the full conversion.

        Args:
            json_string: The JSON string.

        Returns:
            Validation result (success/failure) and validation details or error
        """
        # Log the start of JSON string validation
        self._logger.info("Validating JSON string")

        # Call _service_client.validate_json_string with json_string
        success, details = self._service_client.validate_json_string(json_string)

        # Return the validation result and details
        return success, details

    def convert_file(self, input_path: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON file to Excel format.

        Args:
            input_path: The path to the input JSON file.
            output_path: The path to save the converted Excel file.
            options: Optional conversion options.

        Returns:
            Success flag, conversion summary, and any error details
        """
        # Log the start of file conversion
        self._logger.info(f"Converting JSON file: input_path={input_path}, output_path={output_path}, options={options}")

        # Call _service_client.convert_file with input_path, output_path, and options
        success, summary, error = self._service_client.convert_file(input_path, output_path, options)

        # Return the conversion result, summary, and any error details
        return success, summary, error

    def convert_json_string(self, json_string: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON string to Excel format.

        Args:
            json_string: The JSON data as a string.
            output_path: The path to save the converted Excel file.
            options: Optional conversion options.

        Returns:
            Success flag, conversion summary, and any error details
        """
        # Log the start of JSON string conversion
        self._logger.info(f"Converting JSON string: output_path={output_path}, options={options}")

        # Call _service_client.convert_json_string with json_string, output_path, and options
        success, summary, error = self._service_client.convert_json_string(json_string, output_path, options)

        # Return the conversion result, summary, and any error details
        return success, summary, error

    def convert_file_to_bytes(self, input_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON file to Excel format and returns the result as bytes.

        Args:
            input_path: The path to the input JSON file.
            options: Optional conversion options.

        Returns:
            Excel content as bytes, conversion summary, and any error details
        """
        # Log the start of file to bytes conversion
        self._logger.info(f"Converting JSON file to bytes: input_path={input_path}, options={options}")

        # Call _service_client.convert_file_to_bytes with input_path and options
        excel_bytes, summary, error = self._service_client.convert_file_to_bytes(input_path, options)

        # Return the Excel bytes, conversion summary, and any error details
        return excel_bytes, summary, error

    def convert_json_string_to_bytes(self, json_string: str, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON string to Excel format and returns the result as bytes.

        Args:
            json_string: The JSON data as a string.
            options: Optional conversion options.

        Returns:
            Excel content as bytes, conversion summary, and any error details
        """
        # Log the start of JSON string to bytes conversion
        self._logger.info(f"Converting JSON string to bytes: options={options}")

        # Call _service_client.convert_json_string_to_bytes with json_string and options
        excel_bytes, summary, error = self._service_client.convert_json_string_to_bytes(json_string, options)

        # Return the Excel bytes, conversion summary, and any error details
        return excel_bytes, summary, error

    def process_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes web form data into conversion options.

        Args:
            form_data: Dictionary of web form data.

        Returns:
            Processed conversion options
        """
        # Create ConversionOptions from form data using ConversionOptions.from_form_data
        conversion_options = ConversionOptions.from_form_data(form_data)
        # Convert options to dictionary using to_dict()
        options_dict = conversion_options.to_dict()
        # Return the options dictionary
        return options_dict

    def create_error_response(self, error_dict: Dict[str, Any]) -> ErrorResponse:
        """
        Creates an ErrorResponse object from an error dictionary.

        Args:
            error_dict: Dictionary containing error information.

        Returns:
            An ErrorResponse object created from the dictionary
        """
        # Create and return an ErrorResponse using ErrorResponse.from_dict(error_dict)
        return ErrorResponse.from_dict(error_dict)