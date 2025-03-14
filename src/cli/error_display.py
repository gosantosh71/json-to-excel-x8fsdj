"""
Provides specialized error display functionality for the CLI component of the JSON to Excel Conversion Tool.
This module handles the formatting and presentation of error messages to users in a clear, consistent,
and user-friendly manner, with appropriate styling and context information.
"""

import os  # v: built-in
import textwrap  # v: built-in
import typing  # v: built-in

from ..backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..backend.logger import get_logger
from .models.cli_response import CLIResponse, ResponseType
from .utils.console_utils import print_error, print_warning, colorize, is_color_supported

# Initialize logger
logger = get_logger(__name__)

# Global variables
USE_COLORS = is_color_supported()
VERBOSE_ENV_VAR = "JSON2EXCEL_VERBOSE"
ERROR_SYMBOLS = {
    "ERROR": "[!]",
    "WARNING": "[!]", 
    "INFO": "[i]"
}
ERROR_COLORS = {
    "ERROR": "RED",
    "WARNING": "YELLOW",
    "INFO": "BLUE"
}
INDENT_SIZE = 2
MAX_LINE_LENGTH = 80


def is_verbose_mode(verbose_param: typing.Optional[bool] = None) -> bool:
    """
    Determines if verbose error output mode is enabled based on environment variable or parameter.
    
    Args:
        verbose_param: Explicit verbose parameter which overrides environment setting if provided
        
    Returns:
        True if verbose mode is enabled, False otherwise
    """
    # If explicit parameter is provided, it takes precedence
    if verbose_param is not None:
        return verbose_param
    
    # Check environment variable
    env_value = os.environ.get(VERBOSE_ENV_VAR, '').lower()
    return env_value in ('1', 'true', 'yes', 'on')


def format_error_message(message: str, error_type: typing.Optional[str] = None, use_colors: bool = USE_COLORS) -> str:
    """
    Formats an error message with appropriate styling and indentation.
    
    Args:
        message: The error message to format
        error_type: Type of error (ERROR, WARNING, INFO)
        use_colors: Whether to use colored output
        
    Returns:
        Formatted error message
    """
    # Default to ERROR if not specified
    if error_type is None:
        error_type = "ERROR"
    
    # Get the symbol and color for this error type
    symbol = ERROR_SYMBOLS.get(error_type, ERROR_SYMBOLS["ERROR"])
    color = ERROR_COLORS.get(error_type, ERROR_COLORS["ERROR"])
    
    # Format the message with the symbol prefix
    formatted_message = f"{symbol} {message}"
    
    # Apply color if requested
    if use_colors:
        formatted_message = colorize(formatted_message, color)
    
    return formatted_message


def format_resolution_steps(steps: typing.List[str], use_colors: bool = USE_COLORS) -> str:
    """
    Formats resolution steps into a readable list with proper indentation.
    
    Args:
        steps: List of resolution steps
        use_colors: Whether to use colored output
        
    Returns:
        Formatted resolution steps
    """
    if not steps:
        return ""
    
    # Create header for resolution steps
    header = "Troubleshooting steps:"
    if use_colors:
        header = colorize(header, "CYAN", bold=True)
    
    # Format each step with bullet points and indentation
    indent = " " * INDENT_SIZE
    formatted_steps = [f"{indent}• {step}" for step in steps]
    
    # Join all steps into a single string
    return header + "\n" + "\n".join(formatted_steps)


def wrap_text(text: str, width: int = MAX_LINE_LENGTH, indent: int = INDENT_SIZE) -> str:
    """
    Wraps text to a specified width with proper indentation for multi-line messages.
    
    Args:
        text: Text to wrap
        width: Maximum line width
        indent: Number of spaces to indent continued lines
        
    Returns:
        Wrapped and indented text
    """
    # Use textwrap to wrap the text
    wrapped_text = textwrap.fill(
        text,
        width=width,
        subsequent_indent=" " * indent
    )
    
    return wrapped_text


def display_error(error: ErrorResponse, verbose: typing.Optional[bool] = None) -> None:
    """
    Displays an error message to the user with appropriate formatting.
    
    Args:
        error: The error response to display
        verbose: Whether to display verbose error information
    """
    # Determine if verbose mode is enabled
    is_verbose = is_verbose_mode(verbose)
    
    # Get the user-friendly message
    message = error.get_user_message()
    
    # Determine error type based on severity
    error_type = "ERROR"
    if error.severity == ErrorSeverity.WARNING:
        error_type = "WARNING"
    elif error.severity == ErrorSeverity.INFO:
        error_type = "INFO"
    
    # Format the message
    formatted_message = format_error_message(message, error_type)
    
    # Add resolution steps if available
    if error.resolution_steps:
        formatted_message += "\n\n" + format_resolution_steps(error.resolution_steps)
    
    # Add additional error details if in verbose mode
    if is_verbose:
        details = (
            f"\nError Code: {error.error_code}"
            f"\nCategory: {error.category.value}"
            f"\nComponent: {error.source_component}"
        )
        
        if error.context:
            context_str = ", ".join(f"{k}={v}" for k, v in error.context.items())
            details += f"\nContext: {context_str}"
        
        if error.traceback and is_verbose:
            details += f"\n\nTraceback:\n{error.traceback}"
            
        formatted_message += "\n" + details
    
    # Display the message using the appropriate print function
    if error_type == "WARNING":
        print_warning(formatted_message)
        logger.warning(f"Displayed warning: {error.message}")
    else:
        print_error(formatted_message)
        logger.error(f"Displayed error: {error.message}")


def display_cli_error(response: CLIResponse, verbose: typing.Optional[bool] = None) -> None:
    """
    Displays an error from a CLIResponse object with appropriate formatting.
    
    Args:
        response: The CLI response containing the error
        verbose: Whether to display verbose error information
    """
    # Check if the response contains an error
    if response.error:
        display_error(response.error, verbose)
        return
    
    # If no error object but response type is ERROR or WARNING, display the message
    if response.response_type in (ResponseType.ERROR, ResponseType.WARNING):
        error_type = response.response_type.value
        message = format_error_message(response.message, error_type)
        
        if error_type == "WARNING":
            print_warning(message)
            logger.warning(f"Displayed warning: {response.message}")
        else:
            print_error(message)
            logger.error(f"Displayed error: {response.message}")


def create_error_display_string(error: ErrorResponse, verbose: typing.Optional[bool] = None) -> str:
    """
    Creates a formatted error display string without printing it.
    
    Args:
        error: The error response to format
        verbose: Whether to include verbose error information
        
    Returns:
        Formatted error display string
    """
    # Determine if verbose mode is enabled
    is_verbose = is_verbose_mode(verbose)
    
    # Get the user-friendly message
    message = error.get_user_message()
    
    # Determine error type based on severity
    error_type = "ERROR"
    if error.severity == ErrorSeverity.WARNING:
        error_type = "WARNING"
    elif error.severity == ErrorSeverity.INFO:
        error_type = "INFO"
    
    # Format the message (without colors as this is for a string)
    formatted_message = format_error_message(message, error_type, False)
    
    # Add resolution steps if available
    if error.resolution_steps:
        formatted_message += "\n\n" + format_resolution_steps(error.resolution_steps, False)
    
    # Add additional error details if in verbose mode
    if is_verbose:
        details = (
            f"\nError Code: {error.error_code}"
            f"\nCategory: {error.category.value}"
            f"\nComponent: {error.source_component}"
        )
        
        if error.context:
            context_str = ", ".join(f"{k}={v}" for k, v in error.context.items())
            details += f"\nContext: {context_str}"
        
        if error.traceback:
            details += f"\n\nTraceback:\n{error.traceback}"
            
        formatted_message += "\n" + details
    
    return formatted_message


class ErrorDisplayFormatter:
    """
    A class that handles the formatting of error messages for display in the CLI.
    """
    
    def __init__(self, use_colors: bool = USE_COLORS, verbose: bool = None, max_width: int = MAX_LINE_LENGTH):
        """
        Initializes a new ErrorDisplayFormatter with the specified display settings.
        
        Args:
            use_colors: Whether to use colored output
            verbose: Whether to include verbose error information
            max_width: Maximum line width for wrapped text
        """
        self._use_colors = use_colors
        self._verbose = is_verbose_mode(verbose)
        self._max_width = max_width
    
    def format_error(self, error: ErrorResponse) -> str:
        """
        Formats an ErrorResponse into a display string.
        
        Args:
            error: The error response to format
            
        Returns:
            Formatted error display string
        """
        # Get the user-friendly message
        message = error.get_user_message()
        
        # Determine error type based on severity
        error_type = "ERROR"
        if error.severity == ErrorSeverity.WARNING:
            error_type = "WARNING"
        elif error.severity == ErrorSeverity.INFO:
            error_type = "INFO"
        
        # Format the message
        formatted_message = format_error_message(message, error_type, self._use_colors)
        
        # Add resolution steps if available
        if error.resolution_steps:
            formatted_message += "\n\n" + format_resolution_steps(error.resolution_steps, self._use_colors)
        
        # Add additional error details if in verbose mode
        if self._verbose:
            formatted_message += "\n" + self._format_error_details(error)
        
        return formatted_message
    
    def format_cli_response(self, response: CLIResponse) -> str:
        """
        Formats a CLIResponse containing an error into a display string.
        
        Args:
            response: The CLI response to format
            
        Returns:
            Formatted error display string
        """
        # Check if the response contains an error
        if response.error:
            return self.format_error(response.error)
        
        # If no error object but response type is ERROR or WARNING, format the message
        if response.response_type in (ResponseType.ERROR, ResponseType.WARNING):
            error_type = response.response_type.value
            return format_error_message(response.message, error_type, self._use_colors)
        
        # Not an error response
        return response.message
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Sets the verbose mode for the formatter.
        
        Args:
            verbose: Whether to enable verbose mode
        """
        self._verbose = verbose
    
    def set_use_colors(self, use_colors: bool) -> None:
        """
        Sets whether to use colors in formatted output.
        
        Args:
            use_colors: Whether to use colors
        """
        self._use_colors = use_colors
    
    def set_max_width(self, max_width: int) -> None:
        """
        Sets the maximum line width for formatted output.
        
        Args:
            max_width: Maximum line width
        """
        self._max_width = max_width
    
    def _format_error_details(self, error: ErrorResponse) -> str:
        """
        Formats detailed error information for verbose mode.
        
        Args:
            error: The error response to format
            
        Returns:
            Formatted error details
        """
        details = [
            f"Error Code: {error.error_code}",
            f"Category: {error.category.value}",
            f"Severity: {error.severity.value}",
            f"Component: {error.source_component}",
            f"Error ID: {error.error_id}",
        ]
        
        if error.context:
            context_str = ", ".join(f"{k}={v}" for k, v in error.context.items())
            details.append(f"Context: {context_str}")
        
        if error.traceback:
            details.append(f"\nTraceback:\n{error.traceback}")
        
        # Format with indentation
        indent = " " * INDENT_SIZE
        details_str = "\n".join(f"{indent}{detail}" for detail in details)
        
        return details_str