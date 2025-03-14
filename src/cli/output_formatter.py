"""
Provides high-level output formatting capabilities for the JSON to Excel Conversion Tool's CLI component.
This module integrates various formatters (text, table, JSON) to present conversion results, errors,
and data previews in a consistent, user-friendly manner in the terminal.
"""

import json  # v: built-in
from typing import Dict, List, Any, Optional, Union  # v: built-in

import pandas  # v: pandas 1.5.0+

from ..backend.logger import get_logger
from .models.cli_response import CLIResponse, ResponseType
from ..backend.models.error_response import ErrorResponse
from .utils.console_utils import is_color_supported, print_message, print_success, print_error, print_warning, print_info
from .formatters.text_formatter import TextFormatter
from .formatters.table_formatter import TableFormatter
from .formatters.json_preview_formatter import JSONPreviewFormatter

# Initialize logger
logger = get_logger(__name__)

# Global constants
DEFAULT_STYLE = "default"
USE_COLORS = is_color_supported()


def format_json_output(data: Union[Dict[str, Any], List[Any]], use_colors: bool = USE_COLORS) -> str:
    """
    Formats JSON data with indentation and optional color highlighting for display in the console.
    
    Args:
        data: The JSON data to format
        use_colors: Whether to use color highlighting
        
    Returns:
        Formatted JSON string with proper indentation and optional syntax highlighting
    """
    # Convert data to JSON string with indentation
    json_str = json.dumps(data, indent=2)
    
    # Apply syntax highlighting if requested and supported
    if use_colors:
        # Simple syntax highlighting using regular expressions could be added here
        # For now, we'll return the plain JSON
        pass
        
    return json_str


def format_table_output(
    data: Union[List[Dict[str, Any]], pandas.DataFrame],
    headers: Optional[List[str]] = None,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats tabular data as an ASCII table for display in the console.
    
    Args:
        data: The data to format as a table (DataFrame or list of dictionaries)
        headers: Optional list of headers for the table columns
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted ASCII table string
    """
    formatter = TableFormatter(style="DEFAULT", use_colors=use_colors)
    return formatter.format_data(data)


def format_json_preview(data: Union[Dict[str, Any], List[Any]], use_colors: bool = USE_COLORS) -> str:
    """
    Creates a formatted preview of JSON data with limited depth and items.
    
    Args:
        data: The JSON data to format
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted JSON preview string
    """
    formatter = JSONPreviewFormatter(style="DEFAULT", use_colors=use_colors)
    return formatter.format_preview(data)


def format_error_output(
    error: ErrorResponse,
    include_details: bool = False,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats an error response for display in the console with appropriate styling.
    
    Args:
        error: The error response to format
        include_details: Whether to include technical details
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted error message with optional details
    """
    formatter = TextFormatter(style="DEFAULT", use_colors=use_colors)
    return formatter.format_error(error)


def format_cli_response(
    response: CLIResponse,
    verbose: bool = False,
    use_colors: bool = USE_COLORS
) -> str:
    """
    Formats a CLIResponse object for display in the console with appropriate styling.
    
    Args:
        response: The CLIResponse object to format
        verbose: Whether to include detailed information
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted response message with optional details
    """
    formatter = TextFormatter(style="DEFAULT", use_colors=use_colors)
    formatted = formatter.format_cli_response(response)
    
    # Add data formatting if verbose and data exists
    if verbose and response.data:
        if isinstance(response.data, (dict, list)):
            data_str = format_json_output(response.data, use_colors)
            formatted += f"\n\nData:\n{data_str}"
            
    return formatted


def display_cli_response(
    response: CLIResponse,
    verbose: bool = False,
    use_colors: bool = USE_COLORS
) -> int:
    """
    Displays a CLIResponse object in the console with appropriate formatting and returns the exit code.
    
    Args:
        response: The CLIResponse object to display
        verbose: Whether to include detailed information
        use_colors: Whether to use colors in the output
        
    Returns:
        Exit code from the response (0 for success, non-zero for errors)
    """
    # Format the response message
    formatted_message = format_cli_response(response, verbose, use_colors)
    
    # Display using the appropriate function based on response type
    if response.response_type == ResponseType.SUCCESS:
        print_success(formatted_message)
    elif response.response_type == ResponseType.ERROR:
        print_error(formatted_message)
    elif response.response_type == ResponseType.WARNING:
        print_warning(formatted_message)
    elif response.response_type == ResponseType.INFO:
        print_info(formatted_message)
    else:
        # Default to standard message
        print_message(formatted_message)
    
    # Return the appropriate exit code
    return response.get_exit_code()


class OutputFormatter:
    """
    A class that provides methods for formatting and displaying various types of output in the 
    console with consistent styling.
    """
    
    def __init__(self, style: str = DEFAULT_STYLE, use_colors: bool = None):
        """
        Initializes a new OutputFormatter instance with the specified styling options.
        
        Args:
            style: The style to use for formatting
            use_colors: Whether to use colors in the output (auto-detect if None)
        """
        self._style = style or DEFAULT_STYLE
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        
        # Initialize the specific formatters
        self._text_formatter = TextFormatter(style=self._style, use_colors=self._use_colors)
        self._table_formatter = TableFormatter(style=self._style, use_colors=self._use_colors)
        self._json_formatter = JSONPreviewFormatter(style=self._style, use_colors=self._use_colors)
    
    def format_text(self, text: str) -> str:
        """
        Formats plain text with optional styling.
        
        Args:
            text: The text to format
            
        Returns:
            Formatted text string
        """
        return self._text_formatter.format_text(text)
    
    def format_json(self, data: Union[Dict[str, Any], List[Any]]) -> str:
        """
        Formats JSON data for display in the console.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Formatted JSON string
        """
        return format_json_output(data, self._use_colors)
    
    def format_json_preview(self, data: Union[Dict[str, Any], List[Any]]) -> str:
        """
        Creates a formatted preview of JSON data with limited depth and items.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Formatted JSON preview string
        """
        return self._json_formatter.format_preview(data)
    
    def format_json_structure(self, data: Union[Dict[str, Any], List[Any]]) -> str:
        """
        Generates a structural preview showing the types and nesting of JSON data.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Structural preview of the JSON data
        """
        return self._json_formatter.format_structure(data)
    
    def format_table(
        self,
        data: Union[List[Dict[str, Any]], pandas.DataFrame],
        headers: Optional[List[str]] = None
    ) -> str:
        """
        Formats tabular data for display in the console.
        
        Args:
            data: The data to format as a table
            headers: Optional list of headers for the table columns
            
        Returns:
            Formatted ASCII table string
        """
        return format_table_output(data, headers, self._use_colors)
    
    def format_error(self, error: ErrorResponse, include_details: bool = False) -> str:
        """
        Formats an error response for display in the console.
        
        Args:
            error: The error response to format
            include_details: Whether to include technical details
            
        Returns:
            Formatted error string
        """
        return format_error_output(error, include_details, self._use_colors)
    
    def format_cli_response(self, response: CLIResponse, verbose: bool = False) -> str:
        """
        Formats a CLIResponse object for display in the console.
        
        Args:
            response: The CLIResponse object to format
            verbose: Whether to include detailed information
            
        Returns:
            Formatted response string
        """
        return format_cli_response(response, verbose, self._use_colors)
    
    def display_cli_response(self, response: CLIResponse, verbose: bool = False) -> int:
        """
        Displays a CLIResponse object in the console and returns the exit code.
        
        Args:
            response: The CLIResponse object to display
            verbose: Whether to include detailed information
            
        Returns:
            Exit code from the response
        """
        return display_cli_response(response, verbose, self._use_colors)
    
    def print_message(self, message: str, message_type: str = "info") -> None:
        """
        Prints a formatted message to the console.
        
        Args:
            message: The message to print
            message_type: Type of message (info, success, error, warning)
        """
        formatted_message = self._text_formatter.format_text(message)
        
        if message_type.lower() == "success":
            print_success(formatted_message)
        elif message_type.lower() == "error":
            print_error(formatted_message)
        elif message_type.lower() == "warning":
            print_warning(formatted_message)
        else:  # Default to info
            print_info(formatted_message)
    
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
    
    def set_style(self, style: str) -> 'OutputFormatter':
        """
        Sets the style to use for formatting.
        
        Args:
            style: The style to use
            
        Returns:
            Self reference for method chaining
        """
        self._style = style
        self._text_formatter.set_style(style)
        self._table_formatter.set_style(style)
        self._json_formatter.set_style(style)
        return self
    
    def set_use_colors(self, use_colors: bool) -> 'OutputFormatter':
        """
        Sets whether to use colors in the formatted output.
        
        Args:
            use_colors: Whether to use colors
            
        Returns:
            Self reference for method chaining
        """
        self._use_colors = use_colors
        self._text_formatter.set_color_mode(use_colors)
        self._table_formatter.set_use_colors(use_colors)
        self._json_formatter.set_color_mode(use_colors)
        return self