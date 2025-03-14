"""
Provides utility functions for file operations in the web interface of the JSON to Excel Conversion Tool.

This module handles file validation, sanitization, storage, and cleanup with a focus on security and proper error handling.
"""

import os  # v: built-in
import os.path  # v: built-in
from datetime import datetime  # v: built-in
import uuid  # v: built-in
from typing import Dict, List, Optional, Tuple, Any  # v: built-in
from werkzeug.utils import secure_filename  # v: 2.3.0+
from flask import FileStorage  # v: 2.3.0+

from ../../backend/logger import get_logger
from .path_utils import (
    ensure_directory_exists,
    get_upload_path,
    get_temp_path,
    ensure_upload_directory,
    ensure_temp_directory,
    is_path_within_directory
)
from ../config/upload_config import upload_config
from ../../backend/models/error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ../../backend/utils import (
    sanitize_file_path,
    get_file_extension,
    get_file_size,
    format_file_size
)
from ../exceptions/file_exceptions import (
    FileException,
    FileSizeExceededException,
    FileTypeNotAllowedException,
    FileStorageException
)

# Initialize logger for this module
logger = get_logger(__name__)

# Constants from configuration
MAX_FILE_SIZE = upload_config['max_file_size']
ALLOWED_EXTENSIONS = upload_config['allowed_extensions']
UPLOAD_FOLDER = upload_config['upload_folder']
FILE_CLEANUP_CONFIG = upload_config['file_cleanup']


def generate_unique_filename(original_filename: str) -> str:
    """
    Generates a unique filename to prevent collisions and overwriting.
    
    Args:
        original_filename: The original filename
        
    Returns:
        Unique filename with UUID prefix
    """
    # Extract the file extension
    extension = os.path.splitext(original_filename)[1]
    
    # Generate a UUID for uniqueness
    unique_id = str(uuid.uuid4())
    
    # Create a new filename with UUID prefix and original extension
    unique_filename = f"{unique_id}{extension}"
    
    logger.debug(f"Generated unique filename: {unique_filename} from original: {original_filename}")
    return unique_filename


def is_allowed_file(filename: str) -> bool:
    """
    Checks if a file has an allowed extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        True if the file extension is allowed, False otherwise
    """
    # Get the file extension using utility function
    extension = get_file_extension(filename)
    
    # Check if the extension is in the allowed list
    # Handle extensions with or without dots
    is_allowed = extension in [ext.lstrip('.') for ext in ALLOWED_EXTENSIONS]
    
    if not is_allowed:
        logger.warning(f"File type not allowed: {filename} (extension: {extension})")
    
    return is_allowed


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent security issues.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Use werkzeug's secure_filename to sanitize
    sanitized = secure_filename(filename)
    
    # Ensure the filename is not empty after sanitization
    if not sanitized:
        # Generate a default filename if sanitization results in empty string
        sanitized = f"file_{uuid.uuid4().hex[:8]}"
        logger.warning(f"Filename sanitized to empty string, using default: {sanitized}")
    
    logger.debug(f"Sanitized filename: {sanitized} from original: {filename}")
    return sanitized


def save_uploaded_file(file: FileStorage, custom_filename: Optional[str] = None) -> Tuple[str, Optional[ErrorResponse]]:
    """
    Saves an uploaded file with validation and security checks.
    
    Args:
        file: The uploaded file object
        custom_filename: Optional custom filename to use
        
    Returns:
        Tuple with saved file path and optional error response
    """
    # Ensure the upload directory exists
    if not ensure_upload_directory():
        error_msg = f"Failed to create upload directory: {UPLOAD_FOLDER}"
        logger.error(error_msg)
        return "", ErrorResponse(
            message=error_msg,
            error_code="UPLOAD_DIR_ERROR",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils"
        )
    
    # Validate the file is not empty
    if not file or not file.filename:
        error_msg = "No file was uploaded or filename is empty"
        logger.error(error_msg)
        return "", ErrorResponse(
            message=error_msg,
            error_code="EMPTY_FILE",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils"
        )
    
    # Check if the file size exceeds the limit
    try:
        # Read the content once to check its size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer to the beginning
        
        if file_size > MAX_FILE_SIZE:
            error_msg = f"File size ({format_file_size(file_size)}) exceeds the maximum allowed size ({format_file_size(MAX_FILE_SIZE)})"
            logger.warning(error_msg)
            return "", ErrorResponse(
                message=error_msg,
                error_code="FILE_TOO_LARGE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils",
                context={"file_size": file_size, "max_size": MAX_FILE_SIZE}
            )
    except Exception as e:
        error_msg = f"Error checking file size: {str(e)}"
        logger.error(error_msg)
        return "", ErrorResponse(
            message=error_msg,
            error_code="FILE_SIZE_CHECK_ERROR",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils",
            context={"exception": str(e)}
        )
    
    # Validate the file has an allowed extension
    if not is_allowed_file(file.filename):
        error_msg = f"File type not allowed: {file.filename}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        logger.warning(error_msg)
        return "", ErrorResponse(
            message=error_msg,
            error_code="INVALID_FILE_TYPE",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils",
            context={"filename": file.filename, "allowed_extensions": ALLOWED_EXTENSIONS}
        )
    
    # Get filename - either custom or sanitized original
    if custom_filename:
        filename = sanitize_filename(custom_filename)
    else:
        original_filename = file.filename
        filename = sanitize_filename(original_filename)
    
    # Generate a unique filename to prevent collisions
    unique_filename = generate_unique_filename(filename)
    
    # Get the full path
    file_path = get_upload_path(unique_filename)
    
    # Save the file
    try:
        file.save(file_path)
        logger.info(f"File saved successfully: {file_path}")
        return file_path, None
    except Exception as e:
        error_msg = f"Failed to save file: {str(e)}"
        logger.error(error_msg)
        return "", ErrorResponse(
            message=error_msg,
            error_code="FILE_SAVE_ERROR",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils",
            context={"exception": str(e), "file_path": file_path}
        )


def delete_file(file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Deletes a file with security checks.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        Tuple with success flag and optional error response
    """
    # Sanitize the file path
    sanitized_path = sanitize_file_path(file_path)
    
    # Verify the path is within the upload directory
    if not is_path_within_directory(sanitized_path, UPLOAD_FOLDER):
        error_msg = f"Cannot delete file outside of upload directory: {file_path}"
        logger.warning(error_msg)
        return False, ErrorResponse(
            message=error_msg,
            error_code="SECURITY_ERROR",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils",
            context={"file_path": file_path}
        )
    
    # Check if the file exists
    if not os.path.exists(sanitized_path):
        error_msg = f"File not found: {sanitized_path}"
        logger.warning(error_msg)
        return False, ErrorResponse(
            message=error_msg,
            error_code="FILE_NOT_FOUND",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.WARNING,
            source_component="file_utils",
            context={"file_path": sanitized_path}
        )
    
    # Delete the file
    try:
        os.remove(sanitized_path)
        logger.info(f"File deleted successfully: {sanitized_path}")
        return True, None
    except Exception as e:
        error_msg = f"Failed to delete file: {str(e)}"
        logger.error(error_msg)
        return False, ErrorResponse(
            message=error_msg,
            error_code="FILE_DELETE_ERROR",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_utils",
            context={"exception": str(e), "file_path": sanitized_path}
        )


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Gets detailed information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    # Sanitize the file path
    sanitized_path = sanitize_file_path(file_path)
    
    # Check if the file exists
    if not os.path.exists(sanitized_path):
        logger.warning(f"File not found: {sanitized_path}")
        return {
            "exists": False,
            "file_path": sanitized_path,
            "error": "File not found"
        }
    
    try:
        # Get file stats
        stats = os.stat(sanitized_path)
        
        # Get file size
        size_bytes = stats.st_size
        formatted_size = format_file_size(size_bytes)
        
        # Get file creation and modification times
        creation_time = datetime.fromtimestamp(stats.st_ctime)
        modification_time = datetime.fromtimestamp(stats.st_mtime)
        
        # Get file extension
        filename = os.path.basename(sanitized_path)
        extension = get_file_extension(filename)
        
        # Compile file information
        file_info = {
            "exists": True,
            "file_path": sanitized_path,
            "filename": filename,
            "extension": extension,
            "size_bytes": size_bytes,
            "size_formatted": formatted_size,
            "creation_time": creation_time,
            "modification_time": modification_time,
            "is_allowed_type": extension in [ext.lstrip('.') for ext in ALLOWED_EXTENSIONS]
        }
        
        logger.debug(f"Retrieved file info: {filename}, size: {formatted_size}")
        return file_info
        
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return {
            "exists": True,
            "file_path": sanitized_path,
            "error": str(e)
        }


def cleanup_old_files(max_age_minutes: Optional[int] = None) -> Tuple[int, List[str]]:
    """
    Removes files older than a specified age from the upload directory.
    
    Args:
        max_age_minutes: Maximum age of files in minutes, defaults to config value
        
    Returns:
        Tuple with count of deleted files and list of deleted file paths
    """
    # Use provided max_age_minutes or default from config
    if max_age_minutes is None:
        max_age_minutes = FILE_CLEANUP_CONFIG.get('max_age_minutes', 60)
    
    # Check if file cleanup is enabled
    if not FILE_CLEANUP_CONFIG.get('enabled', False):
        logger.info("File cleanup is disabled in configuration")
        return 0, []
    
    logger.info(f"Starting file cleanup for files older than {max_age_minutes} minutes")
    
    # Calculate the cutoff time
    cutoff_time = datetime.now().timestamp() - (max_age_minutes * 60)
    
    deleted_files = []
    
    try:
        # Iterate through files in the upload directory
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
                
            # Check if the file is older than the cutoff
            mtime = os.path.getmtime(file_path)
            if mtime < cutoff_time:
                try:
                    # Delete the file
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logger.debug(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete old file {file_path}: {str(e)}")
        
        logger.info(f"File cleanup completed. Deleted {len(deleted_files)} files.")
        return len(deleted_files), deleted_files
        
    except Exception as e:
        logger.error(f"Error during file cleanup: {str(e)}")
        return 0, []


class FileManager:
    """
    A class that provides a comprehensive interface for file operations in the web application.
    """
    
    def __init__(self):
        """
        Initializes a new FileManager instance.
        """
        self._upload_folder = UPLOAD_FOLDER
        self._allowed_extensions = ALLOWED_EXTENSIONS
        self._max_file_size = MAX_FILE_SIZE
        
        # Ensure required directories exist
        ensure_upload_directory()
        ensure_temp_directory()
        
        logger.debug("FileManager initialized")
    
    def save_file(self, file: FileStorage, custom_filename: Optional[str] = None) -> Tuple[str, Optional[ErrorResponse]]:
        """
        Saves an uploaded file with validation and security checks.
        
        Args:
            file: The uploaded file object
            custom_filename: Optional custom filename to use
            
        Returns:
            Tuple with saved file path and optional error response
        """
        return save_uploaded_file(file, custom_filename)
    
    def delete_file(self, file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Deletes a file with security checks.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Tuple with success flag and optional error response
        """
        return delete_file(file_path)
    
    def list_files(self, extension_filter: Optional[str] = None) -> List[str]:
        """
        Lists files in the upload directory with optional filtering.
        
        Args:
            extension_filter: Optional extension to filter files by
            
        Returns:
            List of file paths
        """
        files = []
        
        try:
            # Iterate through files in the upload directory
            for filename in os.listdir(self._upload_folder):
                file_path = os.path.join(self._upload_folder, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                
                # Apply extension filter if provided
                if extension_filter is not None:
                    # Remove leading dot if present in the filter
                    ext_filter = extension_filter.lstrip('.')
                    # Check if file has the desired extension
                    if get_file_extension(filename) != ext_filter:
                        continue
                
                files.append(file_path)
            
            logger.debug(f"Listed {len(files)} files" + 
                        (f" with extension {extension_filter}" if extension_filter else ""))
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def get_file_details(self, file_path: str) -> Dict[str, Any]:
        """
        Gets detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        return get_file_info(file_path)
    
    def cleanup_old_files(self, max_age_minutes: Optional[int] = None) -> Tuple[int, List[str]]:
        """
        Removes files older than a specified age from the upload directory.
        
        Args:
            max_age_minutes: Maximum age of files in minutes, defaults to config value
            
        Returns:
            Tuple with count of deleted files and list of deleted file paths
        """
        return cleanup_old_files(max_age_minutes)
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates a file against size and type restrictions.
        
        Args:
            file: The file to validate
            
        Returns:
            Tuple with validation result and optional error response
        """
        # Check if file is empty
        if not file or not file.filename:
            error_msg = "No file was provided or filename is empty"
            logger.warning(error_msg)
            return False, ErrorResponse(
                message=error_msg,
                error_code="EMPTY_FILE",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils"
            )
        
        # Check file size
        try:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > self._max_file_size:
                error_msg = f"File size ({format_file_size(file_size)}) exceeds the maximum allowed size ({format_file_size(self._max_file_size)})"
                logger.warning(error_msg)
                return False, ErrorResponse(
                    message=error_msg,
                    error_code="FILE_TOO_LARGE",
                    category=ErrorCategory.VALIDATION_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="file_utils",
                    context={"file_size": file_size, "max_size": self._max_file_size}
                )
        except Exception as e:
            error_msg = f"Error checking file size: {str(e)}"
            logger.error(error_msg)
            return False, ErrorResponse(
                message=error_msg,
                error_code="FILE_SIZE_CHECK_ERROR",
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils",
                context={"exception": str(e)}
            )
        
        # Check file type
        if not is_allowed_file(file.filename):
            error_msg = f"File type not allowed: {file.filename}. Allowed types: {', '.join(self._allowed_extensions)}"
            logger.warning(error_msg)
            return False, ErrorResponse(
                message=error_msg,
                error_code="INVALID_FILE_TYPE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils",
                context={"filename": file.filename, "allowed_extensions": self._allowed_extensions}
            )
        
        # All validations passed
        logger.debug(f"File validation successful: {file.filename}")
        return True, None
    
    def create_temp_file(self, prefix: str, extension: str, content: Optional[bytes] = None) -> Tuple[str, Optional[ErrorResponse]]:
        """
        Creates a temporary file for processing.
        
        Args:
            prefix: Prefix for the filename
            extension: File extension
            content: Optional content to write to the file
            
        Returns:
            Tuple with temporary file path and optional error response
        """
        # Ensure temp directory exists
        if not ensure_temp_directory():
            error_msg = "Failed to create temporary directory"
            logger.error(error_msg)
            return "", ErrorResponse(
                message=error_msg,
                error_code="TEMP_DIR_ERROR",
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils"
            )
        
        # Generate a unique filename for the temp file
        temp_filename = f"{prefix}_{uuid.uuid4().hex}"
        if not extension.startswith('.'):
            extension = f".{extension}"
        temp_filename = f"{temp_filename}{extension}"
        
        # Get full path
        temp_file_path = get_temp_path(temp_filename)
        
        try:
            # Create the file
            if content is not None:
                with open(temp_file_path, 'wb') as f:
                    f.write(content)
            else:
                # Just create an empty file
                with open(temp_file_path, 'w') as f:
                    pass
            
            logger.debug(f"Created temporary file: {temp_file_path}")
            return temp_file_path, None
            
        except Exception as e:
            error_msg = f"Error creating temporary file: {str(e)}"
            logger.error(error_msg)
            return "", ErrorResponse(
                message=error_msg,
                error_code="TEMP_FILE_ERROR",
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_utils",
                context={"exception": str(e), "temp_file_path": temp_file_path}
            )