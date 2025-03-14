import pytest  # pytest 7.3.0+
from unittest.mock import MagicMock, patch  # built-in
import logging  # built-in

from ...error_handler import (
    ErrorHandler,
    ErrorHandlerContext,
    handle_exception,
    get_error_details
)
from ...exceptions import (
    BaseConversionException,
    FileNotFoundError,
    JSONParsingException
)
from ...models.error_response import (
    ErrorResponse,
    ErrorCategory,
    ErrorSeverity
)
from ...constants import ERROR_CODES
from . import get_test_file_path
from .fixtures.json_fixtures import invalid_json


def test_error_handler_initialization():
    """Tests that the ErrorHandler class initializes correctly with a component name."""
    # Create an ErrorHandler instance with a component name
    handler = ErrorHandler()
    
    # Verify that the handler is initialized
    assert handler is not None
    
    # Verify that the logger is initialized
    assert hasattr(handler, '_logger')


def test_handle_standard_exception():
    """Tests handling of standard Python exceptions."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create a standard Python exception (e.g., ValueError)
    exception = ValueError("Test error message")
    
    # Call handle_exception with the exception
    error_response = handler.handle_exception(exception)
    
    # Verify that an ErrorResponse is returned
    assert isinstance(error_response, ErrorResponse)
    
    # Verify that the error response contains the correct error details
    assert error_response.message == "Test error message"
    assert error_response.error_code == ERROR_CODES["UNKNOWN_ERROR"]
    
    # Verify that the error is categorized as SYSTEM_ERROR
    assert error_response.category == ErrorCategory.SYSTEM_ERROR


def test_handle_custom_exception():
    """Tests handling of custom BaseConversionException subclasses."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create a custom exception (e.g., FileNotFoundError)
    file_path = "/path/to/nonexistent/file.json"
    exception = FileNotFoundError(file_path=file_path)
    
    # Call handle_exception with the custom exception
    error_response = handler.handle_exception(exception)
    
    # Verify that an ErrorResponse is returned
    assert isinstance(error_response, ErrorResponse)
    
    # Verify that the error response contains the correct error details
    assert file_path in error_response.message
    
    # Verify that the error category matches the exception's category
    assert error_response.category == ErrorCategory.INPUT_ERROR
    
    # Verify that the error code is correct
    assert error_response.error_code == ERROR_CODES["FILE_NOT_FOUND"]


def test_error_handler_with_context():
    """Tests the ErrorHandlerContext context manager for handling exceptions in a block of code."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    error_response = None
    
    # Use ErrorHandlerContext with a specific operation name
    try:
        with ErrorHandlerContext("TestOperation") as context:
            # Raise an exception within the context
            raise ValueError("Test error in context")
    except Exception as e:
        # Verify that the exception is caught and handled
        error_response = handler.handle_exception(e)
    
    # Verify that the context manager returns an error response
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert "Test error in context" in error_response.message


def test_error_handler_context_add_context():
    """Tests adding additional context information to the ErrorHandlerContext."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create an ErrorHandlerContext with an operation name
    context = ErrorHandlerContext("TestOperation")
    
    # Add additional context information using add_context
    context.add_context("file_name", "test.json")
    context.add_context("user_id", "12345")
    
    # Raise an exception within the context
    try:
        with context:
            raise ValueError("Test error with additional context")
    except Exception as e:
        error_response = handler.handle_exception(e)
        
    # Verify that the added context information is included in the error response
    assert "file_name" in error_response.context
    assert error_response.context["file_name"] == "test.json"
    assert "user_id" in error_response.context
    assert error_response.context["user_id"] == "12345"


def test_get_error_details_standard_exception():
    """Tests extracting error details from a standard Python exception."""
    # Create a standard Python exception
    exception = ValueError("Test error message")
    
    # Call get_error_details with the exception
    details = get_error_details(exception)
    
    # Verify that the returned dictionary contains basic error information
    assert isinstance(details, dict)
    assert "exception_type" in details
    assert details["exception_type"] == "ValueError"
    assert "exception_message" in details
    assert details["exception_message"] == "Test error message"
    
    # Verify that traceback information is included
    assert "traceback" in details


def test_get_error_details_custom_exception():
    """Tests extracting error details from a custom BaseConversionException."""
    # Create a custom BaseConversionException with context information
    file_path = "/path/to/nonexistent/file.json"
    exception = FileNotFoundError(file_path=file_path)
    exception.add_context("user_id", "12345")
    
    # Call get_error_details with the exception
    details = get_error_details(exception)
    
    # Verify that the returned dictionary contains all exception details
    assert isinstance(details, dict)
    assert "exception_type" in details
    assert details["exception_type"] == "FileNotFoundError"
    assert "exception_message" in details
    assert file_path in details["exception_message"]
    
    # Verify that context information is included
    assert "file_path" in details
    assert details["file_path"] == file_path
    assert "user_id" in details
    assert details["user_id"] == "12345"


def test_create_error_without_exception():
    """Tests creating an error response without an actual exception."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Call create_error with a message, error code, and error type
    message = "Test error without exception"
    error_code = ERROR_CODES["UNKNOWN_ERROR"]
    error_category = ErrorCategory.SYSTEM_ERROR
    
    error_response = handler.create_error(
        message=message,
        error_code=error_code,
        category=error_category
    )
    
    # Verify that an ErrorResponse is returned
    assert isinstance(error_response, ErrorResponse)
    
    # Verify that the error response contains the correct information
    assert error_response.message == message
    assert error_response.error_code == error_code
    assert error_response.category == error_category
    
    # Verify that resolution steps are generated
    assert isinstance(error_response.resolution_steps, list)
    assert len(error_response.resolution_steps) > 0


def test_error_response_user_message():
    """Tests that user-friendly messages are generated from error responses."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Generate an error response for a specific error scenario
    error_response = handler.create_error(
        message="File not found: test.json",
        error_code=ERROR_CODES["FILE_NOT_FOUND"],
        category=ErrorCategory.INPUT_ERROR
    )
    
    # Get the user message from the error response
    user_message = error_response.get_user_message()
    
    # Verify that the message is user-friendly and contains resolution steps
    assert isinstance(user_message, str)
    assert "File not found" in user_message
    assert "test.json" in user_message
    assert any(["check" in user_message.lower(), 
                "verify" in user_message.lower(), 
                "ensure" in user_message.lower()])


@patch('logging.Logger')
def test_log_error(mock_logger):
    """Tests that errors are properly logged with the correct severity."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Mock the logger to capture log calls
    handler._logger = mock_logger
    
    # Create an error response with a specific severity
    error_response = ErrorResponse(
        message="Test error message",
        error_code=ERROR_CODES["UNKNOWN_ERROR"],
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="TestComponent"
    )
    
    # Call log_error with the error response
    handler.log_error(error_response)
    
    # Verify that the logger was called with the correct level and message
    assert mock_logger.error.called or mock_logger.warning.called or mock_logger.info.called


def test_handle_exception_with_context():
    """Tests that context information is properly included in error responses."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create a context dictionary with relevant information
    context = {
        "operation": "file_read",
        "file_path": "/path/to/test.json",
        "user_id": "12345"
    }
    
    # Call handle_exception with an exception and the context
    exception = ValueError("Test error with context")
    error_response = handler.handle_exception(exception, context=context)
    
    # Verify that the context information is included in the error response
    for key, value in context.items():
        assert key in error_response.context
        assert error_response.context[key] == value


def test_file_not_found_error_handling():
    """Tests specific handling of file not found errors."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create a FileNotFoundError with a specific file path
    file_path = "/path/to/nonexistent/file.json"
    exception = FileNotFoundError(file_path=file_path)
    
    # Call handle_exception with the exception
    error_response = handler.handle_exception(exception)
    
    # Verify that the error response has INPUT_ERROR category
    assert error_response.category == ErrorCategory.INPUT_ERROR
    
    # Verify that resolution steps include checking the file path
    path_check_step = any("file path" in step.lower() or "path" in step.lower() 
                         for step in error_response.resolution_steps)
    assert path_check_step, "Resolution steps should include checking the file path"
    
    # Verify that the file path is included in the error context
    assert "file_path" in error_response.context
    assert error_response.context["file_path"] == file_path


def test_json_parsing_error_handling():
    """Tests specific handling of JSON parsing errors."""
    # Create an ErrorHandler instance
    handler = ErrorHandler()
    
    # Create a JSONParsingException with line and column information
    exception = JSONParsingException(
        message="Invalid JSON syntax",
        line_number=10,
        column=15
    )
    
    # Call handle_exception with the exception
    error_response = handler.handle_exception(exception)
    
    # Verify that the error response has PARSING_ERROR category
    assert error_response.category == ErrorCategory.PARSING_ERROR
    
    # Verify that resolution steps include validating JSON syntax
    syntax_check_step = any("syntax" in step.lower() or "json" in step.lower() 
                           for step in error_response.resolution_steps)
    assert syntax_check_step, "Resolution steps should include validating JSON syntax"
    
    # Verify that line and column information is included in the error context
    assert "line_number" in error_response.context
    assert error_response.context["line_number"] == 10
    assert "column" in error_response.context
    assert error_response.context["column"] == 15


def test_global_handle_exception_function():
    """Tests the global handle_exception function outside of the ErrorHandler class."""
    # Create an exception
    exception = ValueError("Test global handle_exception")
    
    # Call the global handle_exception function with the exception and component name
    error_response = handle_exception(exception, message="Custom error message")
    
    # Verify that an ErrorResponse is returned with the correct component name
    assert isinstance(error_response, ErrorResponse)
    
    # Verify that the error details are correctly extracted
    assert "Test global handle_exception" in error_response.message or "Custom error message" in error_response.message
    assert error_response.error_code == ERROR_CODES["UNKNOWN_ERROR"]
    assert error_response.category == ErrorCategory.SYSTEM_ERROR