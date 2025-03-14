"""
Custom exception classes for API-related errors in the web interface.

This module provides a hierarchy of exception classes that correspond to
standard HTTP status codes and error conditions, enabling consistent error
handling and response formatting across the web API.
"""

from typing import Dict, Any, Optional  # v: built-in
from flask import jsonify  # v: 2.3.0+

from ...backend.models.error_response import ErrorCategory, ErrorSeverity, ErrorResponse


class APIException(Exception):
    """Base exception class for all API-related exceptions in the web interface."""

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
        Initialize a new APIException with error details.

        Args:
            message: Human-readable error message
            category: Category of the error
            severity: Severity level of the error
            status_code: HTTP status code for the error
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.status_code = status_code
        self.context = context or {}
        self.original_exception = original_exception

    def to_response(self):
        """
        Convert the exception to a Flask response object.

        Returns:
            A JSON response containing error details with the appropriate status code
        """
        error_response = ErrorResponse(
            message=self.message,
            error_code=str(self.status_code),
            category=self.category,
            severity=self.severity,
            source_component="web_api",
            context=self.context,
            traceback=str(self.original_exception) if self.original_exception else None
        )
        
        return jsonify(error_response.to_dict()), self.status_code

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary representation.

        Returns:
            A dictionary containing error details
        """
        result = {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "status_code": self.status_code
        }
        
        if self.context:
            result["context"] = self.context
            
        return result


class BadRequestException(APIException):
    """Exception for invalid client requests (HTTP 400)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new BadRequestException with error details.

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


class UnauthorizedException(APIException):
    """Exception for authentication failures (HTTP 401)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new UnauthorizedException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=401,
            context=context,
            original_exception=original_exception
        )


class ForbiddenException(APIException):
    """Exception for permission issues (HTTP 403)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new ForbiddenException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=403,
            context=context,
            original_exception=original_exception
        )


class NotFoundException(APIException):
    """Exception for resource not found errors (HTTP 404)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new NotFoundException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=404,
            context=context,
            original_exception=original_exception
        )


class MethodNotAllowedException(APIException):
    """Exception for unsupported HTTP methods (HTTP 405)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new MethodNotAllowedException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=405,
            context=context,
            original_exception=original_exception
        )


class ConflictException(APIException):
    """Exception for resource conflicts (HTTP 409)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new ConflictException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=409,
            context=context,
            original_exception=original_exception
        )


class UnsupportedMediaTypeException(APIException):
    """Exception for unsupported media types (HTTP 415)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new UnsupportedMediaTypeException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=415,
            context=context,
            original_exception=original_exception
        )


class RateLimitExceededException(APIException):
    """Exception for rate limit exceeded errors (HTTP 429)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new RateLimitExceededException with error details.

        Args:
            message: Human-readable error message
            retry_after: Seconds after which the client should retry
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        context = context or {}
        if retry_after is not None:
            context["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=429,
            context=context,
            original_exception=original_exception
        )


class InternalServerErrorException(APIException):
    """Exception for unexpected server errors (HTTP 500)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new InternalServerErrorException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            status_code=500,
            context=context,
            original_exception=original_exception
        )


class ServiceUnavailableException(APIException):
    """Exception for temporary service unavailability (HTTP 503)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new ServiceUnavailableException with error details.

        Args:
            message: Human-readable error message
            retry_after: Seconds after which the client should retry
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        context = context or {}
        if retry_after is not None:
            context["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            status_code=503,
            context=context,
            original_exception=original_exception
        )


class ValidationException(APIException):
    """Exception for request validation failures."""

    def __init__(
        self,
        message: str,
        validation_errors: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize a new ValidationException with error details.

        Args:
            message: Human-readable error message
            validation_errors: Dictionary of validation error details
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        context = context or {}
        if validation_errors is not None:
            context["validation_errors"] = validation_errors
            
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=400,
            context=context,
            original_exception=original_exception
        )