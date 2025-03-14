"""
Error response models for the JSON to Excel Conversion Tool.

This module defines standardized error structures and classifications used
throughout the application to ensure consistent error handling and reporting.
"""

from enum import Enum  # v: built-in
from typing import Dict, List, Optional, Any  # v: built-in
from datetime import datetime  # v: built-in
import uuid  # v: built-in

from ..constants import ERROR_CODES


class ErrorCategory(Enum):
    """Enumeration of error categories used to classify different types of errors in the application."""
    INPUT_ERROR = "input_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    TRANSFORMATION_ERROR = "transformation_error"
    OUTPUT_ERROR = "output_error"
    SYSTEM_ERROR = "system_error"


class ErrorSeverity(Enum):
    """Enumeration of error severity levels used to indicate the impact of errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorResponse:
    """
    A standardized structure for error responses throughout the application,
    providing detailed error information, context, and resolution steps.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        source_component: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None,
        is_recoverable: Optional[bool] = None,
        traceback: Optional[str] = None
    ):
        """
        Initialize a new ErrorResponse with error details.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            category: Category of the error
            severity: Severity level of the error
            source_component: Component where the error occurred
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
            is_recoverable: Whether the error is recoverable
            traceback: Stack trace for debugging (if available)
        """
        self.error_id = str(uuid.uuid4())
        self.error_code = error_code if error_code else ERROR_CODES["UNKNOWN_ERROR"]
        self.message = message
        self.category = category
        self.severity = severity
        self.source_component = source_component
        self.timestamp = datetime.now()
        self.context = context or {}
        self.resolution_steps = resolution_steps or []
        
        # Determine if error is recoverable based on severity if not explicitly provided
        if is_recoverable is None:
            self.is_recoverable = (
                severity == ErrorSeverity.INFO or 
                severity == ErrorSeverity.WARNING
            )
        else:
            self.is_recoverable = is_recoverable
            
        self.traceback = traceback

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error response to a dictionary representation.

        Returns:
            A dictionary containing all error response details
        """
        return {
            'error_id': self.error_id,
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'source_component': self.source_component,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'resolution_steps': self.resolution_steps,
            'is_recoverable': self.is_recoverable,
            'traceback': self.traceback
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorResponse':
        """
        Create an ErrorResponse instance from a dictionary representation.

        Args:
            data: Dictionary containing error response data

        Returns:
            An ErrorResponse instance created from the dictionary
        """
        # Convert string values back to enum types
        category = ErrorCategory(data.get('category'))
        severity = ErrorSeverity(data.get('severity'))
        
        # Create instance with required fields
        instance = cls(
            message=data.get('message', ''),
            error_code=data.get('error_code', ERROR_CODES["UNKNOWN_ERROR"]),
            category=category,
            severity=severity,
            source_component=data.get('source_component', ''),
            context=data.get('context', {}),
            resolution_steps=data.get('resolution_steps', []),
            is_recoverable=data.get('is_recoverable'),
            traceback=data.get('traceback')
        )
        
        # Set fields that would be generated in __init__ 
        if 'error_id' in data:
            instance.error_id = data['error_id']
        
        if 'timestamp' in data:
            # Parse the ISO format timestamp
            instance.timestamp = datetime.fromisoformat(data['timestamp'])
            
        return instance

    def get_user_message(self) -> str:
        """
        Generate a user-friendly error message.

        Returns:
            A formatted message suitable for display to users
        """
        user_message = f"Error: {self.message}"
        
        if self.resolution_steps:
            user_message += "\n\nSuggested actions:"
            for i, step in enumerate(self.resolution_steps, 1):
                user_message += f"\n{i}. {step}"
                
        return user_message

    def get_log_entry(self) -> str:
        """
        Generate a detailed log entry for the error.

        Returns:
            A formatted log entry with detailed error information
        """
        log_entry = (
            f"ERROR [{self.error_id}] - {self.error_code}: "
            f"[{self.category.value.upper()}] {self.message} "
            f"(source: {self.source_component}, time: {self.timestamp.isoformat()})"
        )
        
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            log_entry += f"\nContext: {context_str}"
            
        if self.traceback:
            log_entry += f"\nTraceback: {self.traceback}"
            
        return log_entry

    def add_context(self, key: str, value: Any) -> 'ErrorResponse':
        """
        Add additional context information to the error response.

        Args:
            key: Context information key
            value: Context information value

        Returns:
            Self reference for method chaining
        """
        self.context[key] = value
        return self

    def add_resolution_step(self, step: str) -> 'ErrorResponse':
        """
        Add a suggested resolution step to the error response.

        Args:
            step: Resolution step description

        Returns:
            Self reference for method chaining
        """
        self.resolution_steps.append(step)
        return self