"""
Custom exception classes for the JSON to Excel Conversion Tool.

This module provides a hierarchy of exception types that correspond to different error scenarios
in the application, enabling structured error handling, detailed error reporting, and appropriate
user feedback for various failure modes.
"""

import traceback  # v: built-in
from typing import Dict, Any, Optional, List  # v: built-in

from .constants import ERROR_CODES
from .models.error_response import ErrorCategory, ErrorSeverity, ErrorResponse


class BaseConversionException(Exception):
    """Base exception class for all custom exceptions in the JSON to Excel Conversion Tool."""

    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        source_component: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None
    ):
        """
        Initializes a new BaseConversionException with detailed error information.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            category: Category of the error
            severity: Severity level of the error
            source_component: Component where the error occurred
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.source_component = source_component
        self.context = context or {}
        self.resolution_steps = resolution_steps or []
        
        # Capture current traceback information
        self.traceback_str = traceback.format_exc() if traceback.format_exc() != "NoneType: None\n" else None
        
        # Create error response object
        self.error_response = ErrorResponse(
            message=message,
            error_code=error_code,
            category=category,
            severity=severity,
            source_component=source_component,
            context=self.context,
            resolution_steps=self.resolution_steps,
            traceback=self.traceback_str
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the exception to a dictionary representation.

        Returns:
            A dictionary containing all exception details
        """
        return self.error_response.to_dict()

    def get_user_message(self) -> str:
        """
        Gets a user-friendly error message.

        Returns:
            A formatted message suitable for display to users
        """
        return self.error_response.get_user_message()

    def add_context(self, key: str, value: Any) -> 'BaseConversionException':
        """
        Adds additional context information to the exception.

        Args:
            key: Context information key
            value: Context information value

        Returns:
            Self reference for method chaining
        """
        self.context[key] = value
        self.error_response.add_context(key, value)
        return self

    def add_resolution_step(self, step: str) -> 'BaseConversionException':
        """
        Adds a suggested resolution step to the exception.

        Args:
            step: Resolution step description

        Returns:
            Self reference for method chaining
        """
        self.resolution_steps.append(step)
        self.error_response.add_resolution_step(step)
        return self

    def is_recoverable(self) -> bool:
        """
        Determines if the exception is recoverable based on severity.

        Returns:
            True if the exception is recoverable, False otherwise
        """
        return (
            self.severity == ErrorSeverity.WARNING or 
            self.severity == ErrorSeverity.ERROR
        )


class FileSystemException(BaseConversionException):
    """Base exception class for file system related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None
    ):
        """
        Initializes a new FileSystemException with file path information.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            file_path: Path to the file that caused the error
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
        """
        context = context or {}
        context["file_path"] = file_path
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="FileSystem",
            context=context,
            resolution_steps=resolution_steps
        )
        self.file_path = file_path


class FileNotFoundError(FileSystemException):
    """Exception raised when a required file cannot be found."""

    def __init__(
        self,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new FileNotFoundError.

        Args:
            file_path: Path to the file that could not be found
            context: Additional contextual information about the error
        """
        message = f"File not found: {file_path}"
        resolution_steps = [
            "Check that the file exists at the specified path",
            "Verify that you have permission to access the file",
            "Ensure that the file path is correctly specified"
        ]
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.FILE_NOT_FOUND,
            file_path=file_path,
            context=context,
            resolution_steps=resolution_steps
        )


class InvalidFileTypeError(FileSystemException):
    """Exception raised when a file has an invalid or unsupported type."""

    def __init__(
        self,
        file_path: str,
        expected_type: str,
        actual_type: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new InvalidFileTypeError.

        Args:
            file_path: Path to the file with invalid type
            expected_type: The expected file type (e.g., "json")
            actual_type: The actual file type found
            context: Additional contextual information about the error
        """
        message = f"Invalid file type: Expected '{expected_type}', got '{actual_type}'"
        resolution_steps = [
            f"Select a file with the correct '{expected_type}' extension",
            "Ensure the file content matches the expected format"
        ]
        
        context = context or {}
        context["expected_type"] = expected_type
        context["actual_type"] = actual_type
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.INVALID_FILE_TYPE,
            file_path=file_path,
            context=context,
            resolution_steps=resolution_steps
        )
        self.expected_type = expected_type
        self.actual_type = actual_type


class FileTooLargeError(FileSystemException):
    """Exception raised when a file exceeds the maximum allowed size."""

    def __init__(
        self,
        file_path: str,
        file_size: int,
        max_size: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new FileTooLargeError.

        Args:
            file_path: Path to the file that is too large
            file_size: Actual size of the file in bytes
            max_size: Maximum allowed size in bytes
            context: Additional contextual information about the error
        """
        file_size_mb = file_size / (1024 * 1024)
        max_size_mb = max_size / (1024 * 1024)
        
        message = f"File too large: {file_size_mb:.2f} MB exceeds maximum size of {max_size_mb:.2f} MB"
        resolution_steps = [
            "Split the file into smaller files",
            "Use chunked processing option for large files",
            "Reduce the file size by removing unnecessary data"
        ]
        
        context = context or {}
        context["file_size"] = file_size
        context["max_size"] = max_size
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.FILE_TOO_LARGE,
            file_path=file_path,
            context=context,
            resolution_steps=resolution_steps
        )
        self.file_size = file_size
        self.max_size = max_size


class PermissionError(FileSystemException):
    """Exception raised when file system permissions prevent an operation."""

    def __init__(
        self,
        file_path: str,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new PermissionError.

        Args:
            file_path: Path to the file causing the permission error
            operation: The operation that was attempted (e.g., "read", "write")
            context: Additional contextual information about the error
        """
        message = f"Permission denied: Cannot {operation} file '{file_path}'"
        resolution_steps = [
            "Check file permissions",
            "Run the application with appropriate privileges",
            "Ensure the file is not locked by another process"
        ]
        
        context = context or {}
        context["operation"] = operation
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.PERMISSION_ERROR,
            file_path=file_path,
            context=context,
            resolution_steps=resolution_steps
        )
        self.operation = operation


class JSONException(BaseConversionException):
    """Base exception class for JSON processing related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None
    ):
        """
        Initializes a new JSONException.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
        """
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.PARSING_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONParser",
            context=context,
            resolution_steps=resolution_steps
        )


class JSONParseError(JSONException):
    """Exception raised when JSON content cannot be parsed due to syntax errors."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new JSONParseError.

        Args:
            message: Human-readable error message
            line_number: Line number where the error occurred
            column: Column number where the error occurred
            error_details: Detailed description of the parsing error
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Check the JSON syntax for errors",
            "Validate the JSON using an online JSON validator",
            "Fix any missing quotes, commas, or brackets"
        ]
        
        context = context or {}
        if line_number is not None:
            context["line_number"] = line_number
        if column is not None:
            context["column"] = column
        if error_details:
            context["error_details"] = error_details
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.JSON_PARSE_ERROR,
            context=context,
            resolution_steps=resolution_steps
        )
        self.line_number = line_number
        self.column = column
        self.error_details = error_details


class JSONStructureError(JSONException):
    """Exception raised when JSON structure is valid but doesn't meet expected format."""

    def __init__(
        self,
        message: str,
        expected_structure: Optional[str] = None,
        actual_structure: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new JSONStructureError.

        Args:
            message: Human-readable error message
            expected_structure: Description of the expected JSON structure
            actual_structure: Description of the actual JSON structure found
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Check the structure of your JSON file",
            "Ensure the JSON matches the expected format",
            "Review the documentation for correct JSON format requirements"
        ]
        
        context = context or {}
        if expected_structure:
            context["expected_structure"] = expected_structure
        if actual_structure:
            context["actual_structure"] = actual_structure
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.JSON_STRUCTURE_ERROR,
            context=context,
            resolution_steps=resolution_steps
        )
        self.expected_structure = expected_structure
        self.actual_structure = actual_structure


class TransformationException(BaseConversionException):
    """Base exception class for data transformation related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None
    ):
        """
        Initializes a new TransformationException.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
        """
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.TRANSFORMATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="DataTransformer",
            context=context,
            resolution_steps=resolution_steps
        )


class NestedStructureError(TransformationException):
    """Exception raised when nested JSON structure is too complex to process."""

    def __init__(
        self,
        message: str,
        nesting_level: int,
        max_nesting_level: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new NestedStructureError.

        Args:
            message: Human-readable error message
            nesting_level: Actual nesting level found in the JSON
            max_nesting_level: Maximum supported nesting level
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Simplify the JSON structure to reduce nesting",
            "Pre-process the JSON to flatten deeply nested structures",
            f"Keep nesting level below {max_nesting_level} levels"
        ]
        
        context = context or {}
        context["nesting_level"] = nesting_level
        context["max_nesting_level"] = max_nesting_level
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.JSON_STRUCTURE_ERROR,
            context=context,
            resolution_steps=resolution_steps
        )
        self.nesting_level = nesting_level
        self.max_nesting_level = max_nesting_level


class MemoryError(TransformationException):
    """Exception raised when an operation exceeds available memory."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new MemoryError.

        Args:
            message: Human-readable error message
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Use a smaller input file",
            "Try chunked processing for large files",
            "Close other applications to free memory",
            "Increase system memory if possible"
        ]
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.MEMORY_ERROR,
            context=context,
            resolution_steps=resolution_steps
        )
        # Override severity to CRITICAL for memory errors
        self.severity = ErrorSeverity.CRITICAL
        self.error_response.severity = ErrorSeverity.CRITICAL


class ExcelException(BaseConversionException):
    """Base exception class for Excel generation related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        resolution_steps: Optional[List[str]] = None
    ):
        """
        Initializes a new ExcelException.

        Args:
            message: Human-readable error message
            error_code: Unique code identifying the error type
            context: Additional contextual information about the error
            resolution_steps: Suggested steps to resolve the error
        """
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator",
            context=context,
            resolution_steps=resolution_steps
        )


class ExcelRowLimitError(ExcelException):
    """Exception raised when data exceeds Excel's maximum row limit."""

    def __init__(
        self,
        row_count: int,
        max_rows: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ExcelRowLimitError.

        Args:
            row_count: Actual number of rows in the data
            max_rows: Maximum number of rows supported by Excel
            context: Additional contextual information about the error
        """
        message = f"Excel row limit exceeded: {row_count} rows exceed Excel's limit of {max_rows} rows"
        resolution_steps = [
            "Split the data into multiple sheets",
            "Filter the data to reduce row count",
            "Export to a different format without row limits"
        ]
        
        context = context or {}
        context["row_count"] = row_count
        context["max_rows"] = max_rows
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.EXCEL_ROW_LIMIT,
            context=context,
            resolution_steps=resolution_steps
        )
        self.row_count = row_count
        self.max_rows = max_rows


class ExcelColumnLimitError(ExcelException):
    """Exception raised when data exceeds Excel's maximum column limit."""

    def __init__(
        self,
        column_count: int,
        max_columns: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ExcelColumnLimitError.

        Args:
            column_count: Actual number of columns in the data
            max_columns: Maximum number of columns supported by Excel
            context: Additional contextual information about the error
        """
        message = f"Excel column limit exceeded: {column_count} columns exceed Excel's limit of {max_columns} columns"
        resolution_steps = [
            "Restructure the data to reduce the number of columns",
            "Select only essential fields to include in the output",
            "Split the data across multiple sheets"
        ]
        
        context = context or {}
        context["column_count"] = column_count
        context["max_columns"] = max_columns
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.EXCEL_COLUMN_LIMIT,
            context=context,
            resolution_steps=resolution_steps
        )
        self.column_count = column_count
        self.max_columns = max_columns


class ExcelGenerationError(ExcelException):
    """Exception raised when Excel file generation fails for other reasons."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ExcelGenerationError.

        Args:
            message: Human-readable error message
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Check that you have write permissions for the output directory",
            "Ensure the output file is not currently open in another application",
            "Verify that openpyxl library is correctly installed"
        ]
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.EXCEL_GENERATION_ERROR,
            context=context,
            resolution_steps=resolution_steps
        )


class ConfigurationException(BaseConversionException):
    """Exception raised for configuration related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ConfigurationException.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the error
            context: Additional contextual information about the error
        """
        resolution_steps = [
            "Check the configuration file for errors",
            "Verify that all required configuration settings are present",
            "Ensure configuration values are of the correct type"
        ]
        
        context = context or {}
        if config_key:
            context["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code=ERROR_CODES.CONFIG_ERROR,
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="Configuration",
            context=context,
            resolution_steps=resolution_steps
        )
        self.config_key = config_key