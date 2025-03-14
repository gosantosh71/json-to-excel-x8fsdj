"""
Implements a high-level console formatting interface for the JSON to Excel Conversion Tool's CLI component.
This module bridges the low-level console utilities with the application's output needs, providing 
consistent styling, color management, and formatted display of various data types including conversion
results, errors, and progress indicators.
"""

import json  # v: built-in
import typing
from typing import Dict, List, Any, Optional, Union

import pandas  # v: 1.5.0+

from ..backend.logger import get_logger
from ..backend.models.error_response import ErrorResponse
from .models.cli_response import CLIResponse, ResponseType
from .utils.console_utils import (
    is_color_supported,
    colorize,
    print_message,
    print_success,
    print_error,
    print_warning,
    print_info
)
from .progress_bar import ProgressBar, IndeterminateProgressBar

# Initialize logger
logger = get_logger(__name__)

# Default style for console output
DEFAULT_STYLE = "default"

# Determine if colors should be used based on terminal capabilities
USE_COLORS = is_color_supported()


def format_json_output(data: Union[Dict[str, Any], List[Any]], use_colors: bool = USE_COLORS) -> str:
    """
    Formats JSON data with indentation and optional color highlighting for display in the console.
    
    Args:
        data: JSON data to format (dictionary or list)
        use_colors: Whether to apply color highlighting
        
    Returns:
        Formatted JSON string with proper indentation and optional syntax highlighting
    """
    # Convert the data to a JSON string with indentation
    formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Apply syntax highlighting if requested and available
    if use_colors:
        # A simple syntax highlighting for JSON
        if isinstance(data, dict):
            for key in data.keys():
                key_with_quotes = f'"{key}"'
                formatted_json = formatted_json.replace(
                    f'{key_with_quotes}:', 
                    f'{colorize(key_with_quotes, "BLUE")}:'
                )
    
    return formatted_json


def format_table_output(
    data: Union[List[Dict[str, Any]], pandas.DataFrame],
    headers: Optional[List[str]] = None,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats tabular data as an ASCII table for display in the console.
    
    Args:
        data: Tabular data as a DataFrame or list of dictionaries
        headers: Column headers (derived from data if not provided)
        use_colors: Whether to apply color to the header row
        
    Returns:
        Formatted ASCII table string
    """
    # If data is a Pandas DataFrame, convert to list of dicts
    if isinstance(data, pandas.DataFrame):
        if headers is None:
            headers = list(data.columns)
        data_dicts = data.to_dict('records')
    else:
        data_dicts = data
        # Extract headers from dictionary keys if not provided
        if headers is None and data_dicts:
            headers = list(data_dicts[0].keys())
    
    if not headers or not data_dicts:
        return "Empty table"
    
    # Calculate column widths based on content
    col_widths = {header: len(str(header)) for header in headers}
    for row in data_dicts:
        for header in headers:
            if header in row:
                col_widths[header] = max(
                    col_widths[header], 
                    len(str(row.get(header, "")))
                )
    
    # Create table header
    header_row = " | ".join(
        str(header).ljust(col_widths[header]) for header in headers
    )
    separator = "-+-".join("-" * col_widths[header] for header in headers)
    
    # Apply color to header row if requested
    if use_colors:
        header_row = colorize(header_row, "CYAN", bold=True)
    
    # Create table body
    table_rows = [header_row, separator]
    for row in data_dicts:
        table_rows.append(
            " | ".join(
                str(row.get(header, "")).ljust(col_widths[header]) 
                for header in headers
            )
        )
    
    return "\n".join(table_rows)


def format_error_output(
    error: ErrorResponse,
    include_details: bool = False,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats an error response for display in the console with appropriate styling.
    
    Args:
        error: The error response to format
        include_details: Whether to include additional error details
        use_colors: Whether to apply color to the error message
        
    Returns:
        Formatted error message with optional details
    """
    # Get the basic user message
    message = error.get_user_message()
    
    # Add additional details if requested
    if include_details:
        message += f"\n\nError Code: {error.error_code}"
        message += f"\nCategory: {error.category.value}"
        
        if error.resolution_steps:
            message += "\n\nResolution Steps:"
            for i, step in enumerate(error.resolution_steps, 1):
                message += f"\n{i}. {step}"
    
    # Apply color based on error severity
    if use_colors:
        color = "RED"
        if hasattr(error, 'severity'):
            if error.severity.value == "warning":
                color = "YELLOW"
            elif error.severity.value == "info":
                color = "BLUE"
        
        message = colorize(message, color)
    
    return message


def format_cli_response(
    response: CLIResponse,
    verbose: bool = False,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats a CLIResponse object for display in the console with appropriate styling.
    
    Args:
        response: The CLI response to format
        verbose: Whether to include additional details
        use_colors: Whether to apply color to the message
        
    Returns:
        Formatted response message with optional details
    """
    # Get the basic formatted output
    message = response.get_formatted_output()
    
    # Determine color based on response type
    color = None
    if response.response_type == ResponseType.SUCCESS:
        color = "GREEN"
    elif response.response_type == ResponseType.ERROR:
        color = "RED"
    elif response.response_type == ResponseType.WARNING:
        color = "YELLOW"
    elif response.response_type == ResponseType.INFO:
        color = "BLUE"
    
    # Apply color if requested
    if use_colors and color:
        message = colorize(message, color)
    
    # Add data details if verbose mode is enabled
    if verbose and response.data:
        message += "\n\nDetails:"
        message += "\n" + format_json_output(response.data, use_colors)
    
    return message


def display_cli_response(
    response: CLIResponse,
    verbose: bool = False,
    use_colors: bool = USE_COLORS
) -> int:
    """
    Displays a CLIResponse object in the console with appropriate formatting and returns the exit code.
    
    Args:
        response: The CLI response to display
        verbose: Whether to include additional details
        use_colors: Whether to apply color to the message
        
    Returns:
        Exit code from the response (0 for success, non-zero for errors)
    """
    formatted_message = format_cli_response(response, verbose, use_colors)
    
    # Determine appropriate print function based on response type
    if response.response_type == ResponseType.SUCCESS:
        print_success(formatted_message)
    elif response.response_type == ResponseType.ERROR:
        print_error(formatted_message)
    elif response.response_type == ResponseType.WARNING:
        print_warning(formatted_message)
    elif response.response_type == ResponseType.INFO:
        print_info(formatted_message)
    else:
        # Fallback to standard print_message
        print_message(formatted_message)
    
    # Return the exit code from the response
    return response.get_exit_code()


class ConsoleFormatter:
    """
    A class that provides methods for formatting and displaying various types of output
    in the console with consistent styling.
    """
    
    def __init__(self, style: str = DEFAULT_STYLE, use_colors: bool = USE_COLORS):
        """
        Initializes a new ConsoleFormatter instance with the specified styling options.
        
        Args:
            style: The style to use for formatting (e.g., "default", "minimal")
            use_colors: Whether to use color in the formatted output
        """
        self._style = style
        self._use_colors = use_colors
        self._progress_bar = None
        self._spinner = None
    
    def format_message(self, message: str, message_type: str) -> str:
        """
        Formats a plain text message with optional styling.
        
        Args:
            message: The message to format
            message_type: The type of message (e.g., "success", "error")
            
        Returns:
            Formatted message string
        """
        color = None
        if message_type == "success":
            color = "GREEN"
        elif message_type == "error":
            color = "RED"
        elif message_type == "warning":
            color = "YELLOW"
        elif message_type == "info":
            color = "BLUE"
        
        if self._use_colors and color:
            return colorize(message, color)
        
        return message
    
    def print_message(self, message: str, message_type: str) -> None:
        """
        Prints a formatted message to the console.
        
        Args:
            message: The message to print
            message_type: The type of message (e.g., "success", "error")
        """
        formatted_message = self.format_message(message, message_type)
        
        if message_type == "success":
            print_success(formatted_message)
        elif message_type == "error":
            print_error(formatted_message)
        elif message_type == "warning":
            print_warning(formatted_message)
        elif message_type == "info":
            print_info(formatted_message)
        else:
            print_message(formatted_message)
    
    def print_success(self, message: str) -> None:
        """
        Prints a success message to the console.
        
        Args:
            message: The success message to print
        """
        self.print_message(message, "success")
    
    def print_error(self, message: str) -> None:
        """
        Prints an error message to the console.
        
        Args:
            message: The error message to print
        """
        self.print_message(message, "error")
    
    def print_warning(self, message: str) -> None:
        """
        Prints a warning message to the console.
        
        Args:
            message: The warning message to print
        """
        self.print_message(message, "warning")
    
    def print_info(self, message: str) -> None:
        """
        Prints an informational message to the console.
        
        Args:
            message: The informational message to print
        """
        self.print_message(message, "info")
    
    def format_json(self, data: Union[Dict[str, Any], List[Any]]) -> str:
        """
        Formats JSON data for display in the console.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Formatted JSON string
        """
        return format_json_output(data, self._use_colors)
    
    def format_table(
        self,
        data: Union[List[Dict[str, Any]], pandas.DataFrame],
        headers: Optional[List[str]] = None
    ) -> str:
        """
        Formats tabular data for display in the console.
        
        Args:
            data: The tabular data to format
            headers: Optional column headers
            
        Returns:
            Formatted table string
        """
        return format_table_output(data, headers, self._use_colors)
    
    def format_error(
        self,
        error: ErrorResponse,
        include_details: bool = False
    ) -> str:
        """
        Formats an error response for display in the console.
        
        Args:
            error: The error response to format
            include_details: Whether to include additional error details
            
        Returns:
            Formatted error string
        """
        return format_error_output(error, include_details, self._use_colors)
    
    def display_error(
        self,
        error: ErrorResponse,
        include_details: bool = False
    ) -> None:
        """
        Displays a formatted error response in the console.
        
        Args:
            error: The error response to display
            include_details: Whether to include additional error details
        """
        formatted_error = self.format_error(error, include_details)
        self.print_error(formatted_error)
    
    def display_cli_response(
        self,
        response: CLIResponse,
        verbose: bool = False
    ) -> int:
        """
        Displays a CLIResponse object in the console and returns the exit code.
        
        Args:
            response: The CLI response to display
            verbose: Whether to include additional details
            
        Returns:
            Exit code from the response
        """
        return display_cli_response(response, verbose, self._use_colors)
    
    def start_progress_bar(
        self,
        total: float,
        prefix: str = "Progress:",
        suffix: str = "",
        bar_length: int = 40,
        show_eta: bool = True
    ) -> None:
        """
        Starts a progress bar for tracking operation progress.
        
        Args:
            total: Total value representing 100% completion
            prefix: Text displayed before the progress bar
            suffix: Text displayed after the progress bar
            bar_length: Length of the progress bar in characters
            show_eta: Whether to show ETA information
        """
        # If there's already an active progress bar, stop it first
        if self._progress_bar and self._progress_bar.is_active():
            self.finish_progress_bar()
        
        # Create and start a new progress bar
        self._progress_bar = ProgressBar(
            total=total,
            prefix=prefix,
            suffix=suffix,
            bar_length=bar_length,
            use_colors=self._use_colors,
            show_eta=show_eta
        )
        self._progress_bar.start()
    
    def update_progress_bar(
        self,
        current: float,
        suffix: Optional[str] = None
    ) -> None:
        """
        Updates the active progress bar with a new value.
        
        Args:
            current: Current progress value
            suffix: Optional new suffix text to display
        """
        if not self._progress_bar or not self._progress_bar.is_active():
            logger.warning("No active progress bar to update")
            return
        
        self._progress_bar.update(current, suffix)
    
    def finish_progress_bar(self) -> None:
        """
        Completes the active progress bar.
        """
        if not self._progress_bar or not self._progress_bar.is_active():
            logger.warning("No active progress bar to finish")
            return
        
        self._progress_bar.finish()
        self._progress_bar = None
    
    def start_spinner(self, message: str = "Processing...") -> None:
        """
        Starts an indeterminate progress spinner for operations with unknown duration.
        
        Args:
            message: Message to display alongside the spinner
        """
        # If there's already an active spinner, stop it first
        if self._spinner and self._spinner.is_active():
            self.stop_spinner()
        
        # Create and start a new spinner
        self._spinner = IndeterminateProgressBar(
            message=message,
            use_colors=self._use_colors
        )
        self._spinner.start()
    
    def update_spinner_message(self, message: str) -> None:
        """
        Updates the message displayed with the active spinner.
        
        Args:
            message: New message to display
        """
        if not self._spinner or not self._spinner.is_active():
            logger.warning("No active spinner to update")
            return
        
        self._spinner.update_message(message)
    
    def stop_spinner(self, clear: bool = True) -> None:
        """
        Stops the active progress spinner.
        
        Args:
            clear: Whether to clear the spinner from the console
        """
        if not self._spinner or not self._spinner.is_active():
            logger.warning("No active spinner to stop")
            return
        
        self._spinner.stop(clear)
        self._spinner = None
    
    def set_style(self, style: str) -> None:
        """
        Sets the style to use for formatting.
        
        Args:
            style: The style to use
        """
        self._style = style
    
    def set_use_colors(self, use_colors: bool) -> None:
        """
        Sets whether to use colors in the formatted output.
        
        Args:
            use_colors: Whether to use colors
        """
        self._use_colors = use_colors
    
    def is_progress_active(self) -> bool:
        """
        Checks if a progress bar is currently active.
        
        Returns:
            True if a progress bar is active, False otherwise
        """
        return self._progress_bar is not None and self._progress_bar.is_active()
    
    def is_spinner_active(self) -> bool:
        """
        Checks if a spinner is currently active.
        
        Returns:
            True if a spinner is active, False otherwise
        """
        return self._spinner is not None and self._spinner.is_active()