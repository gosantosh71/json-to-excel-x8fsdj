"""
Provides file validation functionality for the web interface of the JSON to Excel Conversion Tool.
This module implements validators for uploaded files, ensuring they meet size limits, have allowed
extensions, and contain valid JSON content. It serves as a security layer to prevent malicious file
uploads and ensure data integrity.
"""

import os  # v: built-in
import json  # v: built-in
from typing import List, Optional, Tuple, Union  # v: built-in
from werkzeug.datastructures import FileStorage  # v: 2.3.0+

from ...backend.logger import get_logger
from ..config.upload_config import upload_config
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..models.upload_file import UploadFile, UploadStatus
from ..utils.file_utils import is_allowed_file, get_file_info
from ..security.file_sanitizer import FileSanitizer
from ..exceptions.file_exceptions import (
    FileException,
    FileSizeExceededException, 
    FileTypeNotAllowedException,
    InvalidJSONFileException
)

# Initialize logger
logger = get_logger(__name__)

# Global constants from configuration
MAX_FILE_SIZE = upload_config['max_file_size']
ALLOWED_EXTENSIONS = upload_config['allowed_extensions']


def validate_file_size(file_path: str, max_size: Optional[int] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file does not exceed the maximum allowed size.
    
    Args:
        file_path: Path to the file to validate
        max_size: Optional maximum size in bytes, defaults to MAX_FILE_SIZE from config
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Use default MAX_FILE_SIZE if not provided
    if max_size is None:
        max_size = MAX_FILE_SIZE
    
    try:
        # Get the file size
        file_size = os.path.getsize(file_path)
        
        # Check if size exceeds maximum
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            file_size_mb = file_size / (1024 * 1024)
            
            # Create error response
            error_response = ErrorResponse(
                message=f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)",
                error_code="FILE_TOO_LARGE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_validators"
            )
            
            # Add context and resolution steps
            error_response.add_context("file_size", file_size)
            error_response.add_context("max_size", max_size)
            error_response.add_resolution_step("Upload a smaller file")
            error_response.add_resolution_step("Split your data into multiple files")
            
            logger.warning(f"File size validation failed: {file_path} ({file_size} bytes)")
            return False, error_response
        
        # File size is within limits
        return True, None
        
    except Exception as e:
        # Handle file access errors
        error_response = ErrorResponse(
            message=f"Error checking file size: {str(e)}",
            error_code="FILE_ACCESS_ERROR",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_validators"
        )
        error_response.add_context("file_path", file_path)
        error_response.add_context("exception", str(e))
        
        logger.error(f"Error checking file size for {file_path}: {str(e)}")
        return False, error_response


def validate_file_type(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a file has an allowed extension.
    
    Args:
        file_path: Path to the file to validate
        allowed_extensions: Optional list of allowed extensions, defaults to ALLOWED_EXTENSIONS from config
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Use default ALLOWED_EXTENSIONS if not provided
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    # Extract just the filename for extension checking
    filename = os.path.basename(file_path)
    
    # Check if the file has an allowed extension
    if not is_allowed_file(filename):
        extension = os.path.splitext(filename)[1].lower() or "unknown"
        allowed_ext_str = ", ".join(allowed_extensions)
        
        # Create error response
        error_response = ErrorResponse(
            message=f"File type not allowed: {extension}. Allowed types: {allowed_ext_str}",
            error_code="INVALID_FILE_TYPE",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_validators"
        )
        
        # Add context and resolution steps
        error_response.add_context("file_path", file_path)
        error_response.add_context("file_extension", extension)
        error_response.add_context("allowed_extensions", allowed_extensions)
        error_response.add_resolution_step(f"Upload a file with one of the allowed extensions: {allowed_ext_str}")
        
        logger.warning(f"File type validation failed: {file_path} (extension: {extension})")
        return False, error_response
    
    # File type is allowed
    return True, None


def validate_json_content(file_path: str) -> Tuple[bool, Optional[ErrorResponse], Optional[dict]]:
    """
    Validates that a file contains valid JSON content.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple containing validation result, optional error response, and parsed JSON if valid
    """
    try:
        # Open and read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the content as JSON
        try:
            parsed_json = json.loads(content)
            logger.debug(f"Successfully validated JSON content in file: {file_path}")
            return True, None, parsed_json
            
        except json.JSONDecodeError as e:
            # JSON parsing error
            error_response = ErrorResponse(
                message=f"Invalid JSON format: {str(e)}",
                error_code="JSON_PARSE_ERROR",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="file_validators"
            )
            
            # Add context and resolution steps
            error_response.add_context("file_path", file_path)
            error_response.add_context("error_details", str(e))
            error_response.add_context("line_number", e.lineno)
            error_response.add_context("column", e.colno)
            error_response.add_resolution_step("Check the JSON syntax at the indicated location")
            error_response.add_resolution_step("Validate your JSON using an online JSON validator")
            
            logger.error(f"JSON validation failed for {file_path}: {str(e)} at line {e.lineno}, column {e.colno}")
            return False, error_response, None
            
    except Exception as e:
        # File reading or other error
        error_response = ErrorResponse(
            message=f"Error reading file: {str(e)}",
            error_code="FILE_READ_ERROR",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="file_validators"
        )
        error_response.add_context("file_path", file_path)
        error_response.add_context("exception", str(e))
        
        logger.error(f"Error reading file for JSON validation: {file_path}: {str(e)}")
        return False, error_response, None


class WebFileValidator:
    """
    A class that provides comprehensive file validation functionality for the web interface.
    """
    
    def __init__(self, max_file_size: Optional[int] = None, allowed_extensions: Optional[List[str]] = None):
        """
        Initializes a new WebFileValidator instance with optional custom validation parameters.
        
        Args:
            max_file_size: Custom maximum file size in bytes
            allowed_extensions: Custom list of allowed file extensions
        """
        self._max_file_size = max_file_size or MAX_FILE_SIZE
        self._allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
        self._file_sanitizer = FileSanitizer()
        
        logger.debug(f"WebFileValidator initialized with max_file_size={self._max_file_size}, "
                     f"allowed_extensions={self._allowed_extensions}")
    
    def validate_upload(self, file: FileStorage) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates an uploaded file from a Flask request.
        
        Args:
            file: The uploaded file object
            
        Returns:
            Tuple containing validation result and optional error response
        """
        # Check if file was actually uploaded
        if not file or not file.filename:
            error_response = ErrorResponse(
                message="No file was uploaded or filename is empty",
                error_code="MISSING_FILE",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="WebFileValidator"
            )
            logger.warning("File validation failed: No file uploaded")
            return False, error_response
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer to beginning
        
        if file_size > self._max_file_size:
            max_size_mb = self._max_file_size / (1024 * 1024)
            file_size_mb = file_size / (1024 * 1024)
            
            error_response = ErrorResponse(
                message=f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)",
                error_code="FILE_TOO_LARGE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="WebFileValidator"
            )
            error_response.add_context("file_size", file_size)
            error_response.add_context("max_size", self._max_file_size)
            error_response.add_resolution_step("Upload a smaller file")
            
            logger.warning(f"File size validation failed: {file.filename} ({file_size} bytes)")
            return False, error_response
        
        # Check file type
        if not is_allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1].lower() or "unknown"
            allowed_ext_str = ", ".join(self._allowed_extensions)
            
            error_response = ErrorResponse(
                message=f"File type not allowed: {extension}. Allowed types: {allowed_ext_str}",
                error_code="INVALID_FILE_TYPE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="WebFileValidator"
            )
            error_response.add_context("filename", file.filename)
            error_response.add_context("file_extension", extension)
            error_response.add_context("allowed_extensions", self._allowed_extensions)
            error_response.add_resolution_step(f"Upload a file with one of the allowed extensions: {allowed_ext_str}")
            
            logger.warning(f"File type validation failed: {file.filename}")
            return False, error_response
        
        # All validations passed
        logger.debug(f"Upload validation successful for file: {file.filename}")
        return True, None
    
    def validate_json_file(self, file_or_path: Union[str, UploadFile]) -> Tuple[bool, Optional[ErrorResponse], Optional[dict]]:
        """
        Validates a JSON file for proper format and content.
        
        Args:
            file_or_path: Path to the file or UploadFile object
            
        Returns:
            Tuple containing validation result, optional error response, and parsed JSON if valid
        """
        # Determine the file path
        if isinstance(file_or_path, UploadFile):
            file_path = file_or_path.file_path
        else:
            file_path = file_or_path
        
        # Validate file type
        type_valid, type_error = validate_file_type(file_path, self._allowed_extensions)
        if not type_valid:
            return False, type_error, None
        
        # Validate file size
        size_valid, size_error = validate_file_size(file_path, self._max_file_size)
        if not size_valid:
            return False, size_error, None
        
        # Validate JSON content
        content_valid, content_error, parsed_json = validate_json_content(file_path)
        if not content_valid:
            return False, content_error, None
        
        # Perform additional security validation using sanitizer
        try:
            sanitized_content = self._file_sanitizer.sanitize_content(parsed_json)
            if sanitized_content is None:
                error_response = ErrorResponse(
                    message="Security validation failed during content sanitization",
                    error_code="SECURITY_VALIDATION_ERROR",
                    category=ErrorCategory.VALIDATION_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="WebFileValidator"
                )
                error_response.add_context("file_path", file_path)
                
                logger.error(f"Security validation failed for file: {file_path}")
                return False, error_response, None
        except Exception as e:
            error_response = ErrorResponse(
                message=f"Security validation failed: {str(e)}",
                error_code="SECURITY_VALIDATION_ERROR",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="WebFileValidator"
            )
            error_response.add_context("file_path", file_path)
            error_response.add_context("exception", str(e))
            
            logger.error(f"Security validation failed for file: {file_path}: {str(e)}")
            return False, error_response, None
        
        # All validations passed
        logger.info(f"JSON file validation successful for: {file_path}")
        return True, None, parsed_json
    
    def validate_with_exceptions(self, file_or_path: Union[str, UploadFile]) -> dict:
        """
        Validates a file and raises appropriate exceptions instead of returning errors.
        
        Args:
            file_or_path: Path to the file or UploadFile object
            
        Returns:
            Parsed JSON data if validation passes
            
        Raises:
            FileSizeExceededException: If file size exceeds the maximum allowed size
            FileTypeNotAllowedException: If file type is not allowed
            InvalidJSONFileException: If JSON content is invalid
        """
        # First run validation to get any errors
        is_valid, error, parsed_json = self.validate_json_file(file_or_path)
        
        if not is_valid:
            # Determine the appropriate exception type based on the error
            if error and "exceeds maximum allowed size" in error.message:
                file_path = file_or_path.file_path if isinstance(file_or_path, UploadFile) else file_or_path
                file_size = os.path.getsize(file_path)
                
                raise FileSizeExceededException(
                    filename=os.path.basename(file_path),
                    file_size=file_size,
                    max_size=self._max_file_size
                )
            elif error and "File type not allowed" in error.message:
                file_path = file_or_path.file_path if isinstance(file_or_path, UploadFile) else file_or_path
                
                raise FileTypeNotAllowedException(
                    filename=os.path.basename(file_path),
                    allowed_extensions=self._allowed_extensions
                )
            elif error and "Invalid JSON format" in error.message:
                file_path = file_or_path.file_path if isinstance(file_or_path, UploadFile) else file_or_path
                
                raise InvalidJSONFileException(
                    filename=os.path.basename(file_path),
                    error_details=error.message
                )
            else:
                # Generic file exception for other errors
                file_path = file_or_path.file_path if isinstance(file_or_path, UploadFile) else file_or_path
                
                raise FileException(
                    message=error.message if error else "Unknown validation error",
                    category=ErrorCategory.VALIDATION_ERROR,
                    severity=ErrorSeverity.ERROR,
                    status_code=400,
                    context={"file_path": file_path}
                )
        
        # Return the parsed JSON data if validation passes
        return parsed_json