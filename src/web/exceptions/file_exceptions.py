"""
Custom exception classes for file-related errors in the web interface component of the JSON to Excel Conversion Tool.

This module provides a hierarchy of exception classes for handling various file operations including
upload, validation, storage, and download errors.
"""

from typing import Dict, Any, Optional, List  # v: built-in

from .api_exceptions import APIException
from ...backend.models.error_response import ErrorCategory, ErrorSeverity


class FileException(APIException):
    """Base exception class for all file-related exceptions in the web interface."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        status_code: int,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileException with error details.
        
        Args:
            message: Human-readable error message
            category: Category of the error
            severity: Severity level of the error
            status_code: HTTP status code for the error
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=category,
            severity=severity,
            status_code=status_code,
            context=context,
            original_exception=original_exception
        )


class FileUploadException(FileException):
    """Exception raised when there is an error uploading a file."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileUploadException with error details.
        
        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=400,
            context=context,
            original_exception=original_exception
        )


class FileSizeExceededException(FileException):
    """Exception raised when an uploaded file exceeds the maximum allowed size."""
    
    def __init__(
        self,
        filename: str,
        file_size: int,
        max_size: int,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileSizeExceededException with error details.
        
        Args:
            filename: Name of the file that exceeded the size limit
            file_size: Actual size of the file in bytes
            max_size: Maximum allowed file size in bytes
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"File '{filename}' size ({file_size} bytes) exceeds the maximum allowed size of {max_size} bytes"
        
        ctx = context or {}
        ctx.update({
            "filename": filename,
            "file_size": file_size,
            "max_size": max_size
        })
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=413,  # Payload Too Large
            context=ctx,
            original_exception=original_exception
        )


class FileTypeNotAllowedException(FileException):
    """Exception raised when an uploaded file has a disallowed file type."""
    
    def __init__(
        self,
        filename: str,
        allowed_extensions: List[str],
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileTypeNotAllowedException with error details.
        
        Args:
            filename: Name of the file with the disallowed type
            allowed_extensions: List of allowed file extensions
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        allowed_ext_str = ", ".join(allowed_extensions)
        message = f"File '{filename}' has an invalid type. Allowed file types: {allowed_ext_str}"
        
        ctx = context or {}
        ctx.update({
            "filename": filename,
            "allowed_extensions": allowed_extensions
        })
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=415,  # Unsupported Media Type
            context=ctx,
            original_exception=original_exception
        )


class FileEmptyException(FileException):
    """Exception raised when an uploaded file is empty."""
    
    def __init__(
        self,
        filename: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileEmptyException with error details.
        
        Args:
            filename: Name of the empty file
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"File '{filename}' is empty"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=400,  # Bad Request
            context=ctx,
            original_exception=original_exception
        )


class FileCorruptedException(FileException):
    """Exception raised when an uploaded file is corrupted or cannot be processed."""
    
    def __init__(
        self,
        filename: str,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileCorruptedException with error details.
        
        Args:
            filename: Name of the corrupted file
            error_details: Specific details about the corruption or processing failure
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"File '{filename}' is corrupted or cannot be processed"
        if error_details:
            message += f": {error_details}"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        if error_details:
            ctx.update({"error_details": error_details})
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=400,  # Bad Request
            context=ctx,
            original_exception=original_exception
        )


class FileStorageException(FileException):
    """Exception raised when there is an error storing an uploaded file."""
    
    def __init__(
        self,
        filename: str,
        storage_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileStorageException with error details.
        
        Args:
            filename: Name of the file that couldn't be stored
            storage_path: Path where the file was to be stored
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Error storing file '{filename}'"
        if storage_path:
            message += f" at '{storage_path}'"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        if storage_path:
            ctx.update({"storage_path": storage_path})
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=500,  # Internal Server Error
            context=ctx,
            original_exception=original_exception
        )


class FileDeletionException(FileException):
    """Exception raised when there is an error deleting a file."""
    
    def __init__(
        self,
        filename: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileDeletionException with error details.
        
        Args:
            filename: Name of the file that couldn't be deleted
            file_path: Path to the file that couldn't be deleted
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Error deleting file '{filename}'"
        if file_path:
            message += f" at '{file_path}'"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        if file_path:
            ctx.update({"file_path": file_path})
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.WARNING,  # File deletion failures are typically less critical
            status_code=500,  # Internal Server Error
            context=ctx,
            original_exception=original_exception
        )


class InvalidJSONFileException(FileException):
    """Exception raised when an uploaded JSON file has invalid format or structure."""
    
    def __init__(
        self,
        filename: str,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new InvalidJSONFileException with error details.
        
        Args:
            filename: Name of the invalid JSON file
            error_details: Specific details about the JSON formatting or structure issue
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"File '{filename}' contains invalid JSON"
        if error_details:
            message += f": {error_details}"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        if error_details:
            ctx.update({"error_details": error_details})
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=400,  # Bad Request
            context=ctx,
            original_exception=original_exception
        )


class FileDownloadException(FileException):
    """Exception raised when there is an error downloading or serving a file."""
    
    def __init__(
        self,
        filename: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new FileDownloadException with error details.
        
        Args:
            filename: Name of the file that couldn't be downloaded or served
            file_path: Path to the file that couldn't be downloaded or served
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Error downloading or serving file '{filename}'"
        if file_path:
            message += f" from '{file_path}'"
        
        ctx = context or {}
        ctx.update({"filename": filename})
        if file_path:
            ctx.update({"file_path": file_path})
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=500,  # Internal Server Error
            context=ctx,
            original_exception=original_exception
        )