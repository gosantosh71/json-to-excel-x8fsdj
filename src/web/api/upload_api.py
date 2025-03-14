"""
Implements the API endpoints for file upload functionality in the JSON to Excel Conversion Tool web interface.
This module provides routes for uploading JSON files, validating them, retrieving file information, and managing uploaded files.
"""

from typing import Dict, Optional
from flask import request, jsonify, Blueprint
import logging

from ..services.file_service import FileService
from ..models.upload_file import UploadStatus
from ..utils.response_formatter import ResponseFormatter
from ..security.file_sanitizer import FileSanitizer
from ..exceptions.file_exceptions import FileUploadException
from ...backend.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Create Blueprint for upload routes
upload_blueprint = Blueprint('upload', __name__, url_prefix='/api/uploads')

# Initialize services
file_service = FileService()
file_sanitizer = FileSanitizer()


def register_upload_routes(app):
    """
    Registers all upload-related routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(upload_blueprint)
    logger.info("Upload API routes registered successfully")


@upload_blueprint.route('', methods=['POST'])
def upload_file():
    """
    Handles file upload requests, validates the file, and stores it for processing.
    
    Returns:
        JSON response with upload status and file details
    """
    # Check if a file was included in the request
    if 'file' not in request.files:
        logger.warning("No file part in request")
        return ResponseFormatter.error("No file part in the request", status_code=400)
    
    file = request.files['file']
    
    # Check if the file is empty
    if not file or not file.filename:
        logger.warning("No file selected for upload")
        return ResponseFormatter.error("No file selected", status_code=400)
    
    # Validate the file
    try:
        # Validate file type and size
        file_sanitizer.validate_with_exceptions(file.filename, file.content_length)
        
        # Upload the file using the file service
        upload_file, error = file_service.upload_file(file)
        
        if error:
            logger.error(f"Error during file upload: {error.message}")
            return ResponseFormatter.error(error, status_code=400)
        
        # Get file details for the response
        file_details, _ = file_service.get_file_details(upload_file.file_id)
        
        logger.info(f"File uploaded successfully: {file.filename} (ID: {upload_file.file_id})")
        return ResponseFormatter.upload(upload_file, f"File '{file.filename}' uploaded successfully")
        
    except FileUploadException as e:
        logger.error(f"File upload exception: {str(e)}")
        return e.to_response()
    except Exception as e:
        logger.exception(f"Unexpected error during file upload: {str(e)}")
        return ResponseFormatter.error(f"File upload failed: {str(e)}", status_code=500)


@upload_blueprint.route('/<file_id>', methods=['GET'])
def get_upload(file_id: str):
    """
    Retrieves information about a specific uploaded file.
    
    Args:
        file_id: Unique identifier for the file
        
    Returns:
        JSON response with file details
    """
    # Get the upload file from the service
    upload_file, error = file_service.get_upload(file_id)
    
    if error:
        logger.warning(f"Failed to get upload with ID {file_id}: {error.message}")
        return ResponseFormatter.not_found("Upload", file_id)
    
    # Get detailed file information
    file_details, error = file_service.get_file_details(file_id)
    
    if error:
        logger.error(f"Error retrieving file details for {file_id}: {error.message}")
        return ResponseFormatter.error(error, status_code=400)
    
    logger.info(f"Retrieved upload information for file ID: {file_id}")
    return ResponseFormatter.success(file_details, f"File details for {upload_file.original_filename}")


@upload_blueprint.route('/<file_id>', methods=['DELETE'])
def delete_upload(file_id: str):
    """
    Deletes a specific uploaded file.
    
    Args:
        file_id: Unique identifier for the file
        
    Returns:
        JSON response with deletion status
    """
    # Delete the upload file
    success, error = file_service.delete_upload(file_id)
    
    if not success:
        logger.warning(f"Failed to delete upload with ID {file_id}: {error.message if error else 'Unknown error'}")
        if error:
            return ResponseFormatter.error(error, status_code=400)
        return ResponseFormatter.not_found("Upload", file_id)
    
    logger.info(f"Deleted upload with ID: {file_id}")
    return ResponseFormatter.success({"file_id": file_id}, "File deleted successfully")


@upload_blueprint.route('', methods=['GET'])
def list_uploads():
    """
    Lists all uploaded files with optional status filtering.
    
    Returns:
        JSON response with list of uploaded files
    """
    # Get status filter from query parameters
    status_param = request.args.get('status')
    status = None
    
    # Convert status string to enum if provided
    if status_param:
        try:
            status = UploadStatus(status_param)
        except ValueError:
            logger.warning(f"Invalid status filter: {status_param}")
            return ResponseFormatter.error(f"Invalid status filter: {status_param}", status_code=400)
    
    # Get list of uploads
    uploads = file_service.list_uploads(status)
    
    logger.info(f"Listed {len(uploads)} uploads" + (f" with status '{status.value}'" if status else ""))
    return ResponseFormatter.list(uploads, "upload")


@upload_blueprint.route('/<file_id>/validate', methods=['POST'])
def validate_upload(file_id: str):
    """
    Validates an uploaded JSON file for structure and format.
    
    Args:
        file_id: Unique identifier for the file
        
    Returns:
        JSON response with validation results
    """
    # Validate the upload file
    valid, error = file_service.validate_upload(file_id)
    
    if not valid:
        logger.warning(f"Validation failed for upload ID {file_id}: {error.message if error else 'Unknown error'}")
        if error:
            return ResponseFormatter.error(error, status_code=400)
        return ResponseFormatter.not_found("Upload", file_id)
    
    # Get file details with validation information
    file_details, error = file_service.get_file_details(file_id)
    
    if error:
        logger.error(f"Error retrieving file details after validation for {file_id}: {error.message}")
        return ResponseFormatter.error(error, status_code=400)
    
    logger.info(f"JSON file validation completed successfully for file ID: {file_id}")
    return ResponseFormatter.validation_result(True, file_details, "File validation successful")