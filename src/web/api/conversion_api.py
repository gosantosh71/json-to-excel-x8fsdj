"""
Implements the RESTful API endpoints for JSON to Excel conversion operations in the web interface.
This module provides routes for creating conversion jobs, checking job status, retrieving conversion results,
and downloading Excel files.
"""

import logging  # v: built-in
import os  # v: built-in

from flask import Blueprint  # v: 2.3.0+
from flask import request  # v: 2.3.0+
from flask import send_file  # v: 2.3.0+
from flask import url_for  # v: 2.3.0+

from ..utils.response_formatter import ResponseFormatter  # For formatting consistent API responses
from ..services.job_manager import JobManager  # For managing conversion jobs
from ..services.conversion_service import ConversionService  # For handling conversion operations
from ..models.conversion_options import ConversionOptions  # For configuring conversion settings
from ..exceptions.job_exceptions import JobNotFoundException  # For handling job not found errors
from ..exceptions.job_exceptions import JobQueueFullException  # For handling queue full errors

# Initialize logger
logger = logging.getLogger(__name__)

# Create Flask Blueprint for conversion API routes
conversion_blueprint = Blueprint('conversion', __name__, url_prefix='/api/conversion')

# Initialize JobManager and ConversionService
job_manager = JobManager()
conversion_service = ConversionService()


@conversion_blueprint.route('/jobs', methods=['POST'])
def create_conversion_job():
    """
    Creates a new JSON to Excel conversion job.

    Returns:
        flask.Response: JSON response with job details or error
    """
    logger.info("Creating new conversion job")

    try:
        # Extract file_id from request.form
        file_id = request.form.get('file_id')
        if not file_id:
            logger.error("File ID is missing in the request")
            return ResponseFormatter.error("File ID is required", status_code=400)

        # Extract conversion options from request.form
        options = request.form.to_dict()

        # Process form data into ConversionOptions
        conversion_options = conversion_service.process_form_data(options)

        # Create a new job using job_manager.create_job(file_id, options)
        job, error = job_manager.create_job(file_id, conversion_options)

        # If job creation fails, return an error response
        if error:
            logger.error(f"Job creation failed: {error.message}")
            return ResponseFormatter.error(error, status_code=500)

        # Return a success response with the job details
        logger.info(f"Job created successfully: {job.job_id}")
        return ResponseFormatter.job(job, message="Job created successfully", status_code=201)

    except JobQueueFullException as e:
        logger.error(f"Job queue is full: {str(e)}")
        return ResponseFormatter.error(str(e), status_code=503)
    except Exception as e:
        logger.exception("Error creating conversion job")
        return ResponseFormatter.error(str(e), status_code=500)


@conversion_blueprint.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id: str):
    """
    Gets the current status of a conversion job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: JSON response with job status or error
    """
    logger.info(f"Getting status for job: {job_id}")

    # Get the job status using job_manager.get_job_status(job_id)
    status_data, error = job_manager.get_job_status(job_id)

    # If job not found, return a not found error response
    if error:
        logger.warning(f"Job not found: {job_id}")
        return ResponseFormatter.not_found("Job", job_id)

    # Return a success response with the job status
    logger.info(f"Job status retrieved successfully: {job_id}")
    return ResponseFormatter.job_status(status_data, message="Job status retrieved successfully")


@conversion_blueprint.route('/jobs/<job_id>/result', methods=['GET'])
def get_job_result(job_id: str):
    """
    Gets the result of a completed conversion job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: JSON response with job result or error
    """
    logger.info(f"Getting result for job: {job_id}")

    # Get the job result using job_manager.get_job_result(job_id)
    result, error = job_manager.get_job_result(job_id)

    # If job not found or not complete, return an error response
    if error:
        logger.warning(f"Job not found or not complete: {job_id}")
        return ResponseFormatter.error(error, status_code=404)

    # Get the output file path and name using job_manager.get_output_file(job_id)
    output_file_path, output_file_name, error = job_manager.get_output_file(job_id)

    # If file not found, return a not found error response
    if error:
        logger.warning(f"Output file not found for job: {job_id}")
        return ResponseFormatter.error(error, status_code=404)

    # Generate a download URL
    download_url = url_for('conversion.download_file', job_id=job_id)

    # Return a success response with the result and download URL
    file_info = {"file_name": output_file_name, "file_path": output_file_path}
    logger.info(f"Job result retrieved successfully: {job_id}")
    return ResponseFormatter.download(download_url, file_info=file_info)


@conversion_blueprint.route('/jobs/<job_id>/download', methods=['GET'])
def download_file(job_id: str):
    """
    Downloads the Excel file generated by a conversion job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: Excel file for download or error response
    """
    logger.info(f"Downloading file for job: {job_id}")

    # Get the output file path and name using job_manager.get_output_file(job_id)
    output_file_path, output_file_name, error = job_manager.get_output_file(job_id)

    # If file not found, return a not found error response
    if error:
        logger.warning(f"Output file not found for job: {job_id}")
        return ResponseFormatter.error(error, status_code=404)

    try:
        # Return the Excel file using send_file() with appropriate headers for download
        logger.info(f"Serving file for download: {output_file_path}")
        return send_file(output_file_path, as_attachment=True, download_name=output_file_name)
    except Exception as e:
        logger.exception(f"Error serving file for download: {output_file_path}")
        return ResponseFormatter.error(str(e), status_code=500)


@conversion_blueprint.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id: str):
    """
    Cancels a pending or in-progress conversion job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: JSON response with cancellation result
    """
    logger.info(f"Cancelling job: {job_id}")

    # Cancel the job using job_manager.cancel_job(job_id)
    success, error = job_manager.cancel_job(job_id)

    # If cancellation fails, return an error response
    if error:
        logger.error(f"Job cancellation failed: {error.message}")
        return ResponseFormatter.error(error, status_code=500)

    # Return a success response indicating the job was cancelled
    logger.info(f"Job cancelled successfully: {job_id}")
    return ResponseFormatter.success(message="Job cancelled successfully")


@conversion_blueprint.route('/validate', methods=['POST'])
def validate_json():
    """
    Validates a JSON file without performing the full conversion.

    Returns:
        flask.Response: JSON response with validation results
    """
    logger.info("Validating JSON file")

    try:
        # Extract file_id from request.form
        file_id = request.form.get('file_id')
        if not file_id:
            logger.error("File ID is missing in the request")
            return ResponseFormatter.error("File ID is required", status_code=400)

        # Extract conversion options from request.form
        options = request.form.to_dict()

        # Process form data into ConversionOptions
        conversion_options = conversion_service.process_form_data(options)

        # Create a temporary job for validation
        from ..models.upload_file import UploadFile
        upload_file, error = job_manager._file_service.get_upload(file_id)
        if error:
            logger.error(f"Upload file not found: {error.message}")
            return ResponseFormatter.error(error, status_code=400)
        
        from ..models.conversion_job import ConversionJob
        job = ConversionJob(input_file=upload_file, options=conversion_options)

        # Validate the job using conversion_service.validate_conversion_input(job)
        is_valid, details, error = conversion_service.validate_conversion_input(job)

        # Return a validation result response
        logger.info(f"JSON validation completed: is_valid={is_valid}")
        return ResponseFormatter.validation_result(is_valid, details, message="JSON validation completed")

    except Exception as e:
        logger.exception("Error validating JSON file")
        return ResponseFormatter.error(str(e), status_code=500)