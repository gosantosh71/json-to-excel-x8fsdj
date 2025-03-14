"""
Custom exception classes for job-related errors in the web interface component.

This module provides a hierarchy of exception classes for handling various
job processing scenarios including creation, retrieval, processing, cancellation,
and timeout errors.
"""

from typing import Dict, Any, Optional  # v: built-in

from .api_exceptions import APIException
from ...backend.models.error_response import ErrorCategory, ErrorSeverity


class JobException(APIException):
    """Base exception class for all job-related exceptions in the web interface."""

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
        Initialize a new JobException with error details.

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


class JobCreationException(JobException):
    """Exception raised when there is an error creating a new conversion job."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobCreationException with error details.

        Args:
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=500,
            context=context,
            original_exception=original_exception
        )


class JobNotFoundException(JobException):
    """Exception raised when a requested job cannot be found."""

    def __init__(
        self,
        job_id: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobNotFoundException with error details.

        Args:
            job_id: Identifier of the job that could not be found
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Job with ID '{job_id}' not found."
        context = context or {}
        context["job_id"] = job_id
        
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=404,
            context=context,
            original_exception=original_exception
        )


class JobProcessingException(JobException):
    """Exception raised when there is an error processing a conversion job."""

    def __init__(
        self,
        job_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobProcessingException with error details.

        Args:
            job_id: Identifier of the job that encountered processing issues
            message: Human-readable error message
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        context = context or {}
        context["job_id"] = job_id
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=500,
            context=context,
            original_exception=original_exception
        )


class JobCancellationException(JobException):
    """Exception raised when there is an error cancelling a job."""

    def __init__(
        self,
        job_id: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobCancellationException with error details.

        Args:
            job_id: Identifier of the job that could not be cancelled
            reason: Reason for the cancellation failure
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Error cancelling job with ID '{job_id}'."
        if reason:
            message += f" Reason: {reason}"
            
        context = context or {}
        context["job_id"] = job_id
        if reason:
            context["reason"] = reason
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=400,
            context=context,
            original_exception=original_exception
        )


class JobAlreadyCompleteException(JobException):
    """Exception raised when attempting to modify a job that is already complete."""

    def __init__(
        self,
        job_id: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobAlreadyCompleteException with error details.

        Args:
            job_id: Identifier of the completed job
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Job with ID '{job_id}' is already complete and cannot be modified."
        context = context or {}
        context["job_id"] = job_id
        
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=409,
            context=context,
            original_exception=original_exception
        )


class JobQueueFullException(JobException):
    """Exception raised when the job queue is at capacity and cannot accept new jobs."""

    def __init__(
        self,
        queue_limit: int,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobQueueFullException with error details.

        Args:
            queue_limit: Maximum number of jobs allowed in the queue
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Job queue is full (limit: {queue_limit}). Please try again later."
        context = context or {}
        context["queue_limit"] = queue_limit
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=503,
            context=context,
            original_exception=original_exception
        )


class JobTimeoutException(JobException):
    """Exception raised when a job exceeds its time limit."""

    def __init__(
        self,
        job_id: str,
        timeout_minutes: int,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobTimeoutException with error details.

        Args:
            job_id: Identifier of the job that timed out
            timeout_minutes: Time limit for job execution in minutes
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Job with ID '{job_id}' exceeded the time limit of {timeout_minutes} minutes."
        context = context or {}
        context["job_id"] = job_id
        context["timeout_minutes"] = timeout_minutes
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=408,
            context=context,
            original_exception=original_exception
        )


class JobResultNotFoundException(JobException):
    """Exception raised when a job's result file cannot be found."""

    def __init__(
        self,
        job_id: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new JobResultNotFoundException with error details.

        Args:
            job_id: Identifier of the job whose result file could not be found
            file_path: Expected path of the result file (if known)
            context: Additional contextual information
            original_exception: Original exception that caused this error
        """
        message = f"Result file for job with ID '{job_id}' could not be found."
        if file_path:
            message += f" Expected location: {file_path}"
            
        context = context or {}
        context["job_id"] = job_id
        if file_path:
            context["file_path"] = file_path
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=404,
            context=context,
            original_exception=original_exception
        )