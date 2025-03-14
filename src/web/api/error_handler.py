"""
Implements a centralized error handling system for the web API component of the JSON to Excel Conversion Tool.

This module registers error handlers for various exception types, provides consistent error response formatting,
and ensures proper logging of errors that occur during API requests.
"""

from typing import Dict, Any
import traceback

from flask import Flask, jsonify, request, current_app  # v: 2.3.0+
import werkzeug.exceptions  # v: 2.3.0+

from ..exceptions.api_exceptions import APIException
from ..exceptions.file_exceptions import FileException
from ..exceptions.job_exceptions import JobException
from ...backend.exceptions import BaseConversionException
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..utils.response_formatter import ResponseFormatter
from ...backend.logger import get_logger, log_exception

# Initialize logger for this module
logger = get_logger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Registers all error handlers with the Flask application.
    
    Args:
        app: The Flask application instance
    """
    # Register handlers for custom exception types
    app.register_error_handler(APIException, handle_api_exception)
    app.register_error_handler(FileException, handle_file_exception)
    app.register_error_handler(JobException, handle_job_exception)
    app.register_error_handler(BaseConversionException, handle_conversion_exception)
    
    # Register handler for standard HTTP exceptions
    app.register_error_handler(werkzeug.exceptions.HTTPException, handle_http_exception)
    
    # Register fallback handler for all other exceptions
    app.register_error_handler(Exception, handle_generic_exception)
    
    logger.info("Error handlers registered with Flask application")


def handle_api_exception(exception: APIException):
    """
    Handles APIException instances by converting them to appropriate HTTP responses.
    
    Args:
        exception: The APIException instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    log_exception(logger, exception, f"API exception: {str(exception)}", context)
    return exception.to_response()


def handle_file_exception(exception: FileException):
    """
    Handles FileException instances by converting them to appropriate HTTP responses.
    
    Args:
        exception: The FileException instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    log_exception(logger, exception, f"File exception: {str(exception)}", context)
    return exception.to_response()


def handle_job_exception(exception: JobException):
    """
    Handles JobException instances by converting them to appropriate HTTP responses.
    
    Args:
        exception: The JobException instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    log_exception(logger, exception, f"Job exception: {str(exception)}", context)
    return exception.to_response()


def handle_conversion_exception(exception: BaseConversionException):
    """
    Handles BaseConversionException instances from the backend by converting them to appropriate HTTP responses.
    
    Args:
        exception: The BaseConversionException instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    log_exception(logger, exception, f"Conversion exception: {str(exception)}", context)
    
    # Create an error response from the exception details
    error_response = ErrorResponse(
        message=exception.message,
        error_code=exception.error_code,
        category=exception.category,
        severity=exception.severity,
        source_component=exception.source_component,
        context=exception.context,
        resolution_steps=exception.resolution_steps,
        traceback=exception.traceback_str
    )
    
    # Determine an appropriate HTTP status code based on the error category
    status_code = 500  # Default to internal server error
    if exception.category == ErrorCategory.INPUT_ERROR:
        status_code = 400  # Bad request
    elif exception.category == ErrorCategory.VALIDATION_ERROR:
        status_code = 422  # Unprocessable entity
    
    # Format the response using the ResponseFormatter
    return ResponseFormatter.error(error_response, status_code)


def handle_http_exception(exception: werkzeug.exceptions.HTTPException):
    """
    Handles standard HTTP exceptions from Werkzeug by converting them to consistent JSON responses.
    
    Args:
        exception: The HTTPException instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    logger.error(f"HTTP exception: {str(exception)}", extra=context)
    
    # Get error message from exception description if available
    error_message = str(exception)
    if hasattr(exception, 'description') and exception.description:
        error_message = exception.description
    
    # Format the error response
    return ResponseFormatter.error(
        error=error_message,
        status_code=exception.code,
        context=context
    )


def handle_generic_exception(exception: Exception):
    """
    Handles any unhandled exceptions by converting them to 500 Internal Server Error responses.
    
    Args:
        exception: The Exception instance
        
    Returns:
        flask.Response: JSON response with error details
    """
    context = get_request_context()
    
    # Log the full exception details
    tb_text = traceback.format_exc()
    logger.critical(f"Unhandled exception: {str(exception)}\n{tb_text}", extra=context)
    
    # Create generic error response
    error_response = ErrorResponse(
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_SERVER_ERROR",
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.CRITICAL,
        source_component="web_api",
        context=context,
        traceback=tb_text
    )
    
    # Format the response
    return ResponseFormatter.error(error_response, 500)


def get_request_context() -> Dict[str, Any]:
    """
    Extracts relevant context information from the current request for error logging.
    
    Returns:
        dict: Dictionary with request context information
    """
    context = {}
    
    try:
        if request:
            # Add basic request information
            context["method"] = request.method
            context["path"] = request.path
            
            # Add request headers (excluding any sensitive ones)
            headers = {k: v for k, v in request.headers.items() 
                      if k.lower() not in ['authorization', 'cookie', 'x-csrf-token']}
            context["headers"] = headers
            
            # Add request arguments
            context["args"] = dict(request.args)
            
            # Add remote address if available
            if request.remote_addr:
                context["remote_addr"] = request.remote_addr
    except RuntimeError:
        # Handle case where there is no active request context
        pass
    
    return context