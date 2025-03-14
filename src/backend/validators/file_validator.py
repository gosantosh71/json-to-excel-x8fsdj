"""
Provides comprehensive file validation functionality for the JSON to Excel Conversion Tool.

This module validates file existence, permissions, size, and file type to ensure that
input files can be properly processed. It includes methods for validating both input
JSON files and output Excel file paths.
"""

import os
import os.path
from typing import Dict, List, Optional, Any, Tuple

from ..logger import get_logger
from ..models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..exceptions import (
    FileSystemException, 
    FileNotFoundError, 
    FilePermissionError, 
    FileSizeError, 
    InvalidFileTypeError
)
from ..constants import FILE_CONSTANTS, ERROR_CODES
from ..utils import (
    validate_file_path, 
    validate_file_extension, 
    get_file_size, 
    sanitize_file_path, 
    get_file_extension,
    is_json_file,
    format_file_size,
    PathUtils
)
from ..adapters.file_system_adapter import FileSystemAdapter

# Initialize logger for this module
logger = get_logger(__name__)

# Import constants from FILE_CONSTANTS
MAX_FILE_SIZE_MB = FILE_CONSTANTS['MAX_FILE_SIZE_MB']
MAX_FILE_SIZE_BYTES = FILE_CONSTANTS['MAX_FILE_SIZE_BYTES']
ALLOWED_EXTENSIONS = FILE_CONSTANTS['ALLOWED_EXTENSIONS']

def validate_file_exists(file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file exists at the specified path.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Sanitize the file path
    file_path = sanitize_file_path(file_path)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        error = ErrorResponse(
            message=f"File not found: {file_path}",
            error_code=ERROR_CODES['FILE_NOT_FOUND'],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileValidator"
        )
        error.add_context("file_path", file_path)
        error.add_resolution_step("Check that the file exists at the specified path")
        error.add_resolution_step("Verify that you have entered the correct file path")
        
        logger.error(f"File not found: {file_path}")
        return False, error
    
    return True, None

def validate_file_readable(file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file is readable with appropriate permissions.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # First validate that the file exists
    exists, error = validate_file_exists(file_path)
    if not exists:
        return False, error
    
    # Check if the file is readable
    if not os.access(file_path, os.R_OK):
        error = ErrorResponse(
            message=f"Permission denied: Cannot read file {file_path}",
            error_code=ERROR_CODES['PERMISSION_ERROR'],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileValidator"
        )
        error.add_context("file_path", file_path)
        error.add_resolution_step("Check file permissions and ensure you have read access")
        error.add_resolution_step("Try running the application with higher privileges if necessary")
        
        logger.error(f"Permission denied for file: {file_path}")
        return False, error
    
    return True, None

def validate_file_size(file_path: str, max_size_bytes: Optional[int] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file size is within the configured limits.
    
    Args:
        file_path: Path to the file to validate
        max_size_bytes: Maximum allowed file size in bytes
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # First validate that the file exists
    exists, error = validate_file_exists(file_path)
    if not exists:
        return False, error
    
    # Use default max size if not provided
    if max_size_bytes is None:
        max_size_bytes = MAX_FILE_SIZE_BYTES
    
    try:
        # Get the file size
        file_size = get_file_size(file_path)
        
        # Check if the file size exceeds the maximum allowed size
        if file_size > max_size_bytes:
            formatted_file_size = format_file_size(file_size)
            formatted_max_size = format_file_size(max_size_bytes)
            
            error = ErrorResponse(
                message=f"File too large: {formatted_file_size} exceeds maximum size of {formatted_max_size}",
                error_code=ERROR_CODES['FILE_TOO_LARGE'],
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="FileValidator"
            )
            error.add_context("file_path", file_path)
            error.add_context("file_size", file_size)
            error.add_context("max_size", max_size_bytes)
            error.add_resolution_step("Use a smaller file")
            error.add_resolution_step("Split the file into multiple smaller files")
            error.add_resolution_step("Increase the maximum file size limit in the configuration")
            
            logger.error(f"File too large: {file_path} ({formatted_file_size} > {formatted_max_size})")
            return False, error
    except Exception as e:
        error = ErrorResponse(
            message=f"Error checking file size for {file_path}: {str(e)}",
            error_code=ERROR_CODES['FILE_NOT_FOUND'],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileValidator"
        )
        error.add_context("file_path", file_path)
        error.add_context("error", str(e))
        logger.error(f"Error checking file size: {str(e)}")
        return False, error
    
    return True, None

def validate_file_extension(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file has an allowed extension.
    
    Args:
        file_path: Path to the file to validate
        allowed_extensions: List of allowed extensions
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Use default allowed extensions if not provided
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    # Get the file extension
    extension = get_file_extension(file_path)
    
    # Check if the extension is allowed
    if extension not in allowed_extensions:
        error = ErrorResponse(
            message=f"Invalid file extension: {extension}. Expected one of: {', '.join(allowed_extensions)}",
            error_code=ERROR_CODES['INVALID_EXTENSION'],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileValidator"
        )
        error.add_context("file_path", file_path)
        error.add_context("file_extension", extension)
        error.add_context("allowed_extensions", allowed_extensions)
        error.add_resolution_step(f"Use a file with one of the following extensions: {', '.join(allowed_extensions)}")
        
        logger.error(f"Invalid file extension: {extension} for file {file_path}")
        return False, error
    
    return True, None

def validate_output_path(file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that an output file path is valid and writable.
    
    Args:
        file_path: Path to the output file to validate
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Sanitize the file path
    file_path = sanitize_file_path(file_path)
    
    # Get the directory from the file path
    directory = os.path.dirname(file_path)
    
    # If directory is empty, use current directory
    if not directory:
        directory = os.getcwd()
    
    # Check if the directory exists, if not try to create it
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            error = ErrorResponse(
                message=f"Cannot create directory for output file: {directory}",
                error_code=ERROR_CODES['PERMISSION_ERROR'],
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="FileValidator"
            )
            error.add_context("directory", directory)
            error.add_context("error", str(e))
            error.add_resolution_step("Check if you have permission to create directories in this location")
            error.add_resolution_step("Specify a different output path")
            
            logger.error(f"Failed to create directory: {directory} - {str(e)}")
            return False, error
    
    # Check if the directory is writable
    if not os.access(directory, os.W_OK):
        error = ErrorResponse(
            message=f"Permission denied: Cannot write to directory {directory}",
            error_code=ERROR_CODES['PERMISSION_ERROR'],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileValidator"
        )
        error.add_context("directory", directory)
        error.add_resolution_step("Check directory permissions and ensure you have write access")
        error.add_resolution_step("Try running the application with higher privileges if necessary")
        error.add_resolution_step("Specify a different output path")
        
        logger.error(f"Permission denied for directory: {directory}")
        return False, error
    
    return True, None

def get_file_details(file_path: str) -> Dict[str, Any]:
    """
    Gets detailed information about a file including size, type, and path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file details
    """
    # Validate that the file exists
    exists, error = validate_file_exists(file_path)
    if not exists:
        raise FileNotFoundError(file_path=file_path)
    
    # Get file size
    file_size = get_file_size(file_path)
    
    # Get file extension
    extension = get_file_extension(file_path)
    
    # Format file size for display
    formatted_size = format_file_size(file_size)
    
    # Get absolute and normalized path
    absolute_path = os.path.abspath(file_path)
    normalized_path = os.path.normpath(absolute_path)
    
    return {
        'path': file_path,
        'absolute_path': absolute_path,
        'normalized_path': normalized_path,
        'size': file_size,
        'formatted_size': formatted_size,
        'extension': extension,
        'filename': os.path.basename(file_path),
        'directory': os.path.dirname(absolute_path),
        'is_readable': os.access(file_path, os.R_OK),
        'last_modified': os.path.getmtime(file_path)
    }

class FileValidator:
    """
    A class that provides comprehensive file validation functionality.
    """
    
    def __init__(
        self, 
        file_system_adapter: Optional[FileSystemAdapter] = None,
        max_file_size_bytes: Optional[int] = None,
        allowed_extensions: Optional[List[str]] = None
    ):
        """
        Initializes a new FileValidator instance with optional custom validation parameters.
        
        Args:
            file_system_adapter: Adapter for file system operations
            max_file_size_bytes: Maximum allowed file size in bytes
            allowed_extensions: List of allowed file extensions
        """
        self._file_system_adapter = file_system_adapter or FileSystemAdapter()
        self._max_file_size_bytes = max_file_size_bytes or MAX_FILE_SIZE_BYTES
        self._allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
        
        logger.debug(
            f"FileValidator initialized with max_file_size={format_file_size(self._max_file_size_bytes)}, "
            f"allowed_extensions={self._allowed_extensions}"
        )
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[ErrorResponse]]:
        """
        Performs comprehensive validation on a file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple containing overall validation result and list of error responses
        """
        errors = []
        
        # Validate that the file exists
        exists, error = validate_file_exists(file_path)
        if not exists:
            errors.append(error)
            return False, errors
        
        # Validate that the file is readable
        readable, error = validate_file_readable(file_path)
        if not readable:
            errors.append(error)
        
        # Validate the file size
        valid_size, error = validate_file_size(file_path, self._max_file_size_bytes)
        if not valid_size:
            errors.append(error)
        
        # Return result
        if errors:
            return False, errors
        else:
            return True, []
    
    def validate_json_file(self, file_path: str) -> Tuple[bool, List[ErrorResponse]]:
        """
        Validates that a file is a valid JSON file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple containing validation result and list of error responses
        """
        # First validate the file itself
        valid_file, file_errors = self.validate_file(file_path)
        if not valid_file:
            return False, file_errors
        
        # Validate that the file has a .json extension
        valid_extension, extension_error = validate_file_extension(file_path, ["json"])
        if not valid_extension and extension_error:
            return False, [extension_error]
        
        # If we get here, the file passed all validations
        return True, []
    
    def validate_output_path(self, file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates that an output file path is valid and writable.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple containing validation result and optional error response
        """
        return validate_output_path(file_path)
    
    def get_file_details(self, file_path: str) -> Dict[str, Any]:
        """
        Gets detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file details
        """
        return get_file_details(file_path)
    
    def is_valid_json_file(self, file_path: str) -> bool:
        """
        Checks if a file is a valid JSON file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a valid JSON file, False otherwise
        """
        valid, _ = self.validate_json_file(file_path)
        return valid