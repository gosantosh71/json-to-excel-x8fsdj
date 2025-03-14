"""
Provides a utility class for formatting consistent API responses in the web interface of the JSON to Excel Conversion Tool.

This module ensures that all API endpoints return standardized JSON responses with appropriate
status codes, data structures, and error handling.
"""

import logging  # v: built-in
import typing  # v: built-in

from flask import jsonify  # v: 2.3.0+

from ../../backend/models/error_response import ErrorResponse
from ../models/conversion_job import ConversionJob
from ../models/upload_file import UploadFile

# Initialize logger for this module
logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Utility class that provides static methods for formatting consistent API responses in the web interface.
    """

    @staticmethod
    def success(data: typing.Optional[typing.Dict] = None, message: str = "Success", status_code: int = 200):
        """
        Creates a standardized success response with optional data.

        Args:
            data: Optional dictionary containing response data
            message: Success message
            status_code: HTTP status code

        Returns:
            A JSON response with success status and data
        """
        response = {
            "success": True,
            "message": message
        }
        
        if data:
            response["data"] = data
            
        logger.debug(f"Success response: {message} with status {status_code}")
        return jsonify(response), status_code

    @staticmethod
    def error(error: typing.Union[ErrorResponse, str], status_code: int = 400, context: typing.Optional[typing.Dict] = None):
        """
        Creates a standardized error response from an ErrorResponse object or error details.

        Args:
            error: ErrorResponse object or error message string
            status_code: HTTP status code
            context: Additional context for the error

        Returns:
            A JSON response with error details
        """
        response = {
            "success": False,
        }
        
        if isinstance(error, ErrorResponse):
            # Convert ErrorResponse to dictionary
            error_dict = error.to_dict()
            response["error"] = error_dict
        else:
            # Simple error message
            response["error"] = {
                "message": str(error)
            }
            
        if context:
            response["context"] = context
            
        logger.info(f"Error response: {error} with status {status_code}")
        return jsonify(response), status_code

    @staticmethod
    def job(job: ConversionJob, message: str = "Job details", status_code: int = 200):
        """
        Creates a standardized response for a conversion job.

        Args:
            job: ConversionJob object
            message: Response message
            status_code: HTTP status code

        Returns:
            A JSON response with job details
        """
        response = {
            "success": True,
            "message": message,
            "job": job.to_dict()
        }
        
        logger.debug(f"Job response: {message} for job ID {job.job_id}")
        return jsonify(response), status_code

    @staticmethod
    def upload(upload_file: UploadFile, message: str = "File uploaded successfully", status_code: int = 200):
        """
        Creates a standardized response for a file upload.

        Args:
            upload_file: UploadFile object
            message: Response message
            status_code: HTTP status code

        Returns:
            A JSON response with upload details
        """
        response = {
            "success": True,
            "message": message,
            "file": upload_file.to_dict()
        }
        
        logger.debug(f"Upload response: {message} for file {upload_file.original_filename}")
        return jsonify(response), status_code

    @staticmethod
    def job_status(status_data: typing.Dict, message: str = "Job status", status_code: int = 200):
        """
        Creates a standardized response for a job status update.

        Args:
            status_data: Dictionary containing job status information
            message: Response message
            status_code: HTTP status code

        Returns:
            A JSON response with job status details
        """
        response = {
            "success": True,
            "message": message,
            "status": status_data
        }
        
        logger.debug(f"Job status response: {message}")
        return jsonify(response), status_code

    @staticmethod
    def not_found(resource_type: str, resource_id: str):
        """
        Creates a standardized response for resource not found errors.

        Args:
            resource_type: Type of resource that wasn't found
            resource_id: ID of the resource that wasn't found

        Returns:
            A JSON response with not found error
        """
        message = f"{resource_type} not found: {resource_id}"
        return ResponseFormatter.error(message, status_code=404)

    @staticmethod
    def list(items: typing.List, item_type: str, metadata: typing.Optional[typing.Dict] = None):
        """
        Creates a standardized response for list operations.

        Args:
            items: List of items
            item_type: Type of items (used for the response key)
            metadata: Optional metadata about the list (count, pagination, etc.)

        Returns:
            A JSON response with list of items
        """
        response = {
            "success": True,
            "message": f"Found {len(items)} {item_type}(s)",
            f"{item_type}s": items
        }
        
        if metadata:
            response["metadata"] = metadata
            
        logger.debug(f"List response: {len(items)} {item_type}(s)")
        return jsonify(response), 200

    @staticmethod
    def validation_result(is_valid: bool, details: typing.Dict, message: str = "Validation result"):
        """
        Creates a standardized response for validation results.

        Args:
            is_valid: Whether validation was successful
            details: Validation details
            message: Response message

        Returns:
            A JSON response with validation results
        """
        response = {
            "success": True,
            "message": message,
            "is_valid": is_valid,
            "validation_details": details
        }
        
        # Use 200 for valid results, 400 for invalid
        status_code = 200 if is_valid else 400
        
        logger.debug(f"Validation response: {message}, is_valid: {is_valid}")
        return jsonify(response), status_code

    @staticmethod
    def download(download_url: str, file_info: typing.Optional[typing.Dict] = None):
        """
        Creates a standardized response with download information.

        Args:
            download_url: URL for downloading the file
            file_info: Optional information about the file

        Returns:
            A JSON response with download information
        """
        response = {
            "success": True,
            "message": "File is ready for download",
            "download_url": download_url
        }
        
        if file_info:
            response["file_info"] = file_info
            
        logger.debug(f"Download response: URL {download_url}")
        return jsonify(response), 200