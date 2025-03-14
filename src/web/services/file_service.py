"""
Provides a service layer for managing file operations in the web interface of the JSON to Excel Conversion Tool.
This service handles file uploads, validation, retrieval, and lifecycle management with proper security measures and error handling.
"""

import logging  # v: built-in
import os  # v: built-in
from typing import Dict, List, Optional, Tuple, Any  # v: built-in
from werkzeug.datastructures import FileStorage  # v: 2.3.0+
import uuid  # v: built-in

from ..models.upload_file import UploadFile, UploadStatus
from ..utils.file_utils import FileManager
from ..config.upload_config import upload_config
from ...backend.models.error_response import ErrorResponse
from ..exceptions.file_exceptions import FileUploadException, FileSizeExceededException, FileTypeNotAllowedException

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Get upload folder from configuration
UPLOAD_FOLDER = upload_config['upload_folder']


class FileService:
    """
    Service class that provides a high-level interface for file operations in the web interface,
    including upload, validation, retrieval, and management.
    """

    def __init__(self):
        """
        Initializes a new FileService instance with required dependencies.
        """
        self._file_manager = FileManager()
        self._uploads: Dict[str, UploadFile] = {}
        logger.info("FileService initialized")

    def upload_file(self, file: FileStorage) -> Tuple[Optional[UploadFile], Optional[ErrorResponse]]:
        """
        Handles the upload of a new file, including validation and storage.

        Args:
            file: The file to upload from a Flask request

        Returns:
            Tuple containing (upload_file, error_response)
        """
        if not file or not file.filename:
            logger.warning("Empty file or filename provided")
            return None, ErrorResponse.from_exception(
                FileUploadException("No file provided or empty filename")
            )

        logger.info(f"Processing file upload: {file.filename}")

        # Validate the file (size, type)
        valid, error = self._file_manager.validate_file(file)
        if not valid:
            logger.warning(f"File validation failed: {file.filename}")
            return None, error

        # Save the file
        file_path, error = self._file_manager.save_file(file)
        if error:
            logger.error(f"Failed to save file: {file.filename}")
            return None, error

        try:
            # Create UploadFile instance
            upload_file = UploadFile.from_werkzeug_file(file)
            
            # Validate JSON structure
            valid, error = upload_file.validate()
            
            # Store the file in our dictionary
            file_id = upload_file.file_id
            self._uploads[file_id] = upload_file
            
            logger.info(f"File uploaded successfully: {file.filename} (ID: {file_id})")
            return upload_file, None
            
        except Exception as e:
            logger.exception(f"Error processing upload for {file.filename}: {str(e)}")
            # Try to clean up the saved file if there was an error
            try:
                os.remove(file_path)
            except Exception:
                pass
                
            return None, ErrorResponse.from_exception(e)

    def get_upload(self, file_id: str) -> Tuple[Optional[UploadFile], Optional[ErrorResponse]]:
        """
        Retrieves an uploaded file by its ID.

        Args:
            file_id: Unique identifier for the file

        Returns:
            Tuple containing (upload_file, error_response)
        """
        if file_id in self._uploads:
            return self._uploads[file_id], None
        
        logger.warning(f"Upload not found for ID: {file_id}")
        return None, ErrorResponse(
            message=f"Upload not found for ID: {file_id}",
            error_code="UPLOAD_NOT_FOUND",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileService",
            context={"file_id": file_id}
        )

    def get_upload_path(self, file_id: str) -> Tuple[Optional[str], Optional[ErrorResponse]]:
        """
        Gets the file system path for an uploaded file.

        Args:
            file_id: Unique identifier for the file

        Returns:
            Tuple containing (file_path, error_response)
        """
        upload_file, error = self.get_upload(file_id)
        if error:
            return None, error
            
        return upload_file.file_path, None

    def delete_upload(self, file_id: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Deletes an uploaded file by its ID.

        Args:
            file_id: Unique identifier for the file

        Returns:
            Tuple containing (success, error_response)
        """
        upload_file, error = self.get_upload(file_id)
        if error:
            return False, error
            
        # Delete the physical file
        if not upload_file.delete_file():
            logger.error(f"Failed to delete file for upload ID: {file_id}")
            return False, ErrorResponse(
                message=f"Failed to delete file for upload ID: {file_id}",
                error_code="FILE_DELETE_ERROR",
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="FileService",
                context={"file_id": file_id, "file_path": upload_file.file_path}
            )
            
        # Remove from our dictionary
        del self._uploads[file_id]
        logger.info(f"Upload deleted successfully: {file_id}")
        return True, None

    def list_uploads(self, status: Optional[UploadStatus] = None) -> List[Dict]:
        """
        Lists all uploaded files with optional filtering.

        Args:
            status: Optional status filter

        Returns:
            List of upload file information dictionaries
        """
        result = []
        
        for upload_file in self._uploads.values():
            # Apply status filter if provided
            if status is not None and upload_file.status != status:
                continue
                
            # Convert to dictionary representation
            upload_dict = upload_file.to_dict()
            result.append(upload_dict)
            
        logger.debug(f"Listed {len(result)} uploads" + (f" with status {status.value}" if status else ""))
        return result

    def validate_upload(self, file_id: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates an uploaded file for JSON structure and format.

        Args:
            file_id: Unique identifier for the file

        Returns:
            Tuple containing (validation_result, error_response)
        """
        upload_file, error = self.get_upload(file_id)
        if error:
            return False, error
            
        # Validate the JSON file
        valid, error = upload_file.validate()
        
        if valid:
            logger.info(f"File validated successfully: {file_id}")
        else:
            logger.warning(f"File validation failed: {file_id}")
            
        return valid, error

    def get_file_details(self, file_id: str) -> Tuple[Optional[Dict], Optional[ErrorResponse]]:
        """
        Gets detailed information about an uploaded file.

        Args:
            file_id: Unique identifier for the file

        Returns:
            Tuple containing (file_details, error_response)
        """
        upload_file, error = self.get_upload(file_id)
        if error:
            return None, error
            
        # Get file details
        details = upload_file.get_file_details()
        logger.debug(f"Retrieved file details for upload ID: {file_id}")
        return details, None

    def cleanup_uploads(self, status: Optional[UploadStatus] = None, older_than_minutes: Optional[int] = None) -> Dict:
        """
        Cleans up uploaded files based on status or age.

        Args:
            status: Optional status filter
            older_than_minutes: Optional age filter in minutes

        Returns:
            Summary of cleanup operations
        """
        deleted_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Create a list of file IDs to delete
        to_delete = []
        
        for file_id, upload_file in list(self._uploads.items()):
            # Apply status filter if provided
            if status is not None and upload_file.status != status:
                skipped_count += 1
                continue
                
            # Apply age filter if provided
            if older_than_minutes is not None:
                import datetime
                cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=older_than_minutes)
                
                if upload_file.upload_timestamp > cutoff_time:
                    skipped_count += 1
                    continue
            
            to_delete.append(file_id)
        
        # Delete the uploads
        for file_id in to_delete:
            success, _ = self.delete_upload(file_id)
            if success:
                deleted_count += 1
            else:
                failed_count += 1
        
        result = {
            "deleted": deleted_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "total_processed": deleted_count + failed_count + skipped_count
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result

    def get_upload_count(self) -> Dict:
        """
        Gets the current count of uploaded files by status.

        Returns:
            Upload counts by status category
        """
        counts = {
            "total": len(self._uploads),
            "valid": 0,
            "invalid": 0,
            "pending": 0,
            "processed": 0,
            "error": 0
        }
        
        for upload_file in self._uploads.values():
            status = upload_file.status
            
            if status == UploadStatus.VALID:
                counts["valid"] += 1
            elif status == UploadStatus.INVALID:
                counts["invalid"] += 1
            elif status == UploadStatus.PENDING or status == UploadStatus.VALIDATING:
                counts["pending"] += 1
            elif status == UploadStatus.PROCESSED:
                counts["processed"] += 1
            elif status == UploadStatus.ERROR:
                counts["error"] += 1
        
        logger.debug(f"Upload counts: {counts}")
        return counts