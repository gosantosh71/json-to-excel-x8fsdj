"""
Provides a centralized error handling system for the JSON to Excel Conversion Tool.

This module implements a comprehensive approach to error management, including error detection,
categorization, logging, and user-friendly message generation. It serves as the core component
for handling exceptions throughout the application.
"""

import traceback  # v: built-in
import sys  # v: built-in
import typing  # v: built-in
import time  # v: built-in
import functools  # v: built-in
from typing import Dict, Any, Optional, List, Type, Union, Callable  # v: built-in

from .logger import get_logger, log_exception
from .exceptions import BaseConversionException
from .models.error_response import ErrorCategory, ErrorSeverity, ErrorResponse
from .constants import ERROR_CODES
from .config import config

# Initialize logger for this module
logger = get_logger(__name__)


def handle_exception(exception: Exception, message: Optional[str] = None, 
                    context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
    """
    Handles an exception by logging it and creating an appropriate error response.
    
    Args:
        exception: The exception to handle
        message: Optional custom message to override the exception message
        context: Additional context information for the error
        
    Returns:
        Structured error response object
    """
    # If this is already a BaseConversionException, use its error_response
    if isinstance(exception, BaseConversionException):
        # Log the exception with context
        log_exception(
            logger, 
            exception, 
            message or str(exception), 
            context or exception.context
        )
        return exception.error_response
    
    # If not a BaseConversionException, create a generic error response
    error_response = create_error_response(exception, message, context)
    
    # Log the unexpected exception with traceback
    log_exception(
        logger,
        exception,
        message or f"Unexpected error: {str(exception)}",
        context or {}
    )
    
    return error_response


def create_error_response(exception: Exception, message: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
    """
    Creates a standardized error response for an exception.
    
    Args:
        exception: The exception to create a response for
        message: Optional custom message to override the exception message
        context: Additional context information for the error
        
    Returns:
        Structured error response object
    """
    # Use provided message or exception message
    final_message = message or str(exception)
    
    # Get formatted traceback for detailed debugging
    traceback_str = format_traceback(exception)
    
    # Create context dictionary if not provided
    if context is None:
        context = {}
    
    # Add exception details to context
    exception_details = get_exception_details(exception)
    context.update(exception_details)
    
    # Determine if the error is recoverable
    recoverable = is_recoverable_error(exception)
    
    # Create the error response
    error_response = ErrorResponse(
        message=final_message,
        error_code=ERROR_CODES["UNKNOWN_ERROR"],
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.CRITICAL if not recoverable else ErrorSeverity.ERROR,
        source_component="System",
        context=context,
        resolution_steps=suggest_resolution(exception),
        is_recoverable=recoverable,
        traceback=traceback_str
    )
    
    return error_response


def get_exception_details(exception: Exception) -> Dict[str, Any]:
    """
    Extracts detailed information from an exception.
    
    Args:
        exception: The exception to extract details from
        
    Returns:
        Dictionary with exception details
    """
    details = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception)
    }
    
    # Add traceback if available
    tb = format_traceback(exception)
    if tb:
        details["traceback"] = tb
    
    # Add additional attributes from the exception
    for attr in dir(exception):
        # Skip private attributes, methods, and common attributes
        if (not attr.startswith('_') and
            not callable(getattr(exception, attr)) and
            attr not in ('args', 'with_traceback', 'traceback')):
            try:
                value = getattr(exception, attr)
                # Only include serializable values
                if isinstance(value, (str, int, float, bool, list, dict, tuple, set)) or value is None:
                    details[f"exception_{attr}"] = value
            except Exception:
                pass
    
    return details


def format_traceback(exception: Optional[Exception] = None) -> str:
    """
    Formats an exception traceback into a readable string.
    
    Args:
        exception: The exception to format, or None to use current exception info
        
    Returns:
        Formatted traceback string
    """
    # If no exception is provided, get the current exception info
    if exception is None:
        exc_type, exc_value, exc_traceback = sys.exc_info()
    else:
        exc_type = type(exception)
        exc_value = exception
        exc_traceback = getattr(exception, '__traceback__', None)
    
    # If there's no traceback, return an empty string
    if not exc_traceback:
        return ""
    
    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    return tb_text


def is_recoverable_error(exception: Exception) -> bool:
    """
    Determines if an error is recoverable based on its type and severity.
    
    Args:
        exception: The exception to evaluate
        
    Returns:
        True if the error is recoverable, False otherwise
    """
    # If it's a BaseConversionException, use its is_recoverable method
    if isinstance(exception, BaseConversionException):
        return exception.is_recoverable()
    
    # For standard exceptions, determine based on type
    # Generally, permission, resource, and value errors may be recoverable
    recoverable_types = (
        ValueError, 
        TypeError, 
        OSError, 
        IOError, 
        PermissionError, 
        FileNotFoundError
    )
    
    # Memory errors and system errors are generally not recoverable
    non_recoverable_types = (
        MemoryError, 
        SystemError, 
        KeyboardInterrupt, 
        SystemExit
    )
    
    if isinstance(exception, recoverable_types):
        return True
    if isinstance(exception, non_recoverable_types):
        return False
    
    # Default to recoverable for unknown exception types
    return True


def suggest_resolution(exception: Exception) -> List[str]:
    """
    Suggests resolution steps for a given error type.
    
    Args:
        exception: The exception to suggest resolutions for
        
    Returns:
        List of suggested resolution steps
    """
    # If it's a BaseConversionException with resolution steps, use those
    if isinstance(exception, BaseConversionException) and hasattr(exception, 'resolution_steps'):
        return exception.resolution_steps
    
    # Determine appropriate suggestions based on exception type
    if isinstance(exception, (FileNotFoundError, IOError)):
        return [
            "Verify that the file exists and has the correct path",
            "Check that you have appropriate permissions to access the file",
            "Ensure the file is not open in another application"
        ]
    elif isinstance(exception, PermissionError):
        return [
            "Check the file permissions",
            "Run the application with appropriate user privileges",
            "Verify that you have write access to the output directory"
        ]
    elif isinstance(exception, ValueError):
        return [
            "Check the input values for errors",
            "Ensure the JSON file is properly formatted",
            "Verify that file paths are valid"
        ]
    elif isinstance(exception, (MemoryError, OverflowError)):
        return [
            "Try using a smaller input file",
            "Close other applications to free memory",
            "Consider using chunked processing for large files"
        ]
    
    # Generic suggestions for unknown error types
    return [
        "Check the log files for more detailed error information",
        "Verify that input files are valid and accessible",
        "Ensure the application has the necessary permissions",
        "Contact support if the issue persists"
    ]


def exception_handler(handler: Optional[Callable] = None):
    """
    Decorator that wraps a function with exception handling.
    
    Args:
        handler: Optional custom exception handler
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use the provided handler or the default handler
                error_handler = handler or handle_exception
                return error_handler(e)
        return wrapper
    return decorator


class ErrorHandler:
    """
    Centralized error handling class for managing exceptions throughout the application.
    """
    
    def __init__(self):
        """
        Initializes a new ErrorHandler instance.
        """
        self._error_handlers = {}  # Dict to store custom handlers
        self._recoverable_errors = {}  # Dict to store recoverability status
        self._logger = get_logger(self.__class__.__name__)
    
    def register_handler(self, exception_type: Type[Exception], 
                         handler: Callable, recoverable: bool = True) -> None:
        """
        Registers a custom handler for a specific exception type.
        
        Args:
            exception_type: Type of exception to handle
            handler: Function to handle the exception
            recoverable: Whether the exception is recoverable
        """
        self._error_handlers[exception_type] = handler
        self._recoverable_errors[exception_type] = recoverable
        self._logger.debug(f"Registered handler for {exception_type.__name__}")
    
    def handle_exception(self, exception: Exception, message: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        Handles an exception using registered handlers or default handling.
        
        Args:
            exception: The exception to handle
            message: Optional custom message
            context: Additional context information
            
        Returns:
            Error response structure
        """
        # Check if there's a registered handler for this exception type
        handler = None
        for exc_type, exc_handler in self._error_handlers.items():
            if isinstance(exception, exc_type):
                handler = exc_handler
                break
        
        # If a handler is found, use it
        if handler:
            self._logger.debug(f"Using registered handler for {type(exception).__name__}")
            return handler(exception, message, context)
        
        # Otherwise, use the default handle_exception function
        self._logger.debug(f"Using default handler for {type(exception).__name__}")
        return handle_exception(exception, message, context)
    
    def is_recoverable(self, exception: Exception) -> bool:
        """
        Determines if an exception is recoverable based on registered information.
        
        Args:
            exception: The exception to check
            
        Returns:
            True if recoverable, False otherwise
        """
        # Check registered recoverability status
        for exc_type, recoverable in self._recoverable_errors.items():
            if isinstance(exception, exc_type):
                return recoverable
        
        # Fall back to default implementation
        return is_recoverable_error(exception)
    
    def wrap_function(self, func: Callable) -> Callable:
        """
        Wraps a function with exception handling.
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function with error handling
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                return self.handle_exception(exc)
        return wrapper
    
    def create_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a context dictionary with additional information.
        
        Args:
            base_context: Base context dictionary
            
        Returns:
            Enhanced context dictionary
        """
        context = base_context.copy()
        
        # Add timestamp
        context["timestamp"] = time.time()
        
        # Add system information
        context["system_info"] = {
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        return context


class ErrorContext:
    """
    Context manager for handling exceptions within a block of code.
    """
    
    def __init__(self, context_name: Optional[str] = None, 
                context: Optional[Dict[str, Any]] = None,
                error_handler: Optional[ErrorHandler] = None):
        """
        Initializes a new ErrorContext instance.
        
        Args:
            context_name: Optional name for the context
            context: Dictionary of context information
            error_handler: Optional custom error handler
        """
        self._context_name = context_name
        self._context = context or {}
        self._error_handler = error_handler or ErrorHandler()
        self._logger = get_logger(self.__class__.__name__)
    
    def __enter__(self) -> 'ErrorContext':
        """
        Enters the context for exception handling.
        
        Returns:
            Self reference
        """
        if self._context_name:
            self._logger.debug(f"Entering error context: {self._context_name}")
        return self
    
    def __exit__(self, exc_type: Optional[Type[Exception]], 
                exc_val: Optional[Exception], 
                exc_tb: Optional[traceback.TracebackType]) -> bool:
        """
        Exits the context and handles any exceptions that occurred.
        
        Args:
            exc_type: Exception type that was raised or None
            exc_val: Exception instance that was raised or None
            exc_tb: Exception traceback or None
            
        Returns:
            True to suppress the exception, False to propagate it
        """
        # Check if an exception occurred
        if exc_type is not None and exc_val is not None:
            # Handle the exception
            self._error_handler.handle_exception(
                exc_val, 
                context=self._context
            )
            
            if self._context_name:
                self._logger.debug(f"Exiting error context with error: {self._context_name}")
            
            # Return True to suppress the exception (it's been handled)
            return True
        
        if self._context_name:
            self._logger.debug(f"Exiting error context successfully: {self._context_name}")
        
        # No exception occurred
        return False
    
    def add_context(self, key: str, value: Any) -> 'ErrorContext':
        """
        Adds additional context information.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            Self reference for method chaining
        """
        self._context[key] = value
        return self