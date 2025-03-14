"""
Provides text formatting utilities for the CLI component of the JSON to Excel Conversion Tool.
This module handles the formatting of various types of text output including plain text, JSON data,
lists, key-value pairs, and error messages for display in the command-line interface.
"""

import json  # v: built-in
import textwrap  # v: built-in
from typing import Dict, List, Optional, Any, Union  # v: built-in

from ..utils.console_utils import colorize, is_color_supported, get_terminal_size
from ..models.cli_response import CLIResponse, ResponseType
from ...backend.models.error_response import ErrorResponse

# Dictionary of text styles with indentation and wrapping properties
TEXT_STYLES = {"DEFAULT": {"indent": 2, "wrap_width": 80}, "COMPACT": {"indent": 0, "wrap_width": 100}, "VERBOSE": {"indent": 4, "wrap_width": 60}}
DEFAULT_STYLE = "DEFAULT"
SECTION_SEPARATOR = "="
LIST_BULLET = "• "
KEY_VALUE_SEPARATOR = ": "


def format_text(text: str, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats plain text with optional indentation and wrapping.
    
    Args:
        text: The text to format
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted text string
    """
    if not text:
        return ""
    
    # Get style settings or use defaults
    style_settings = TEXT_STYLES.get(style, TEXT_STYLES[DEFAULT_STYLE])
    indent = style_settings["indent"]
    wrap_width = style_settings["wrap_width"]
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Adjust wrap width based on terminal size if set to 'auto'
    if wrap_width == 'auto':
        terminal_width, _ = get_terminal_size()
        wrap_width = terminal_width - indent * 2
    
    # Apply wrapping and indentation
    if wrap_width > 0:
        wrapped_text = textwrap.fill(
            text,
            width=wrap_width,
            initial_indent=" " * indent,
            subsequent_indent=" " * indent
        )
    else:
        # If wrapping is disabled, just add indentation
        wrapped_text = " " * indent + text
    
    return wrapped_text


def format_json(data: dict, indent: int = 2, use_colors: Optional[bool] = None) -> str:
    """
    Formats JSON data with proper indentation and optional syntax highlighting.
    
    Args:
        data: The JSON data to format
        indent: The indentation level for the JSON output
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted JSON string
    """
    if data is None:
        return ""
    
    # Convert to JSON string with indentation
    json_str = json.dumps(data, indent=indent)
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Apply syntax highlighting if colors are supported
    if use_colors:
        # Simple syntax highlighting for JSON
        import re
        
        # Highlight keys
        json_str = re.sub(
            r'("([^"]+)"\s*:)',
            lambda m: colorize(m.group(1), "CYAN"),
            json_str
        )
        
        # Highlight string values
        json_str = re.sub(
            r'(:\s*"([^"]+)")',
            lambda m: ": " + colorize(f'"{m.group(2)}"', "GREEN"),
            json_str
        )
        
        # Highlight numbers
        json_str = re.sub(
            r'(:\s*)(\d+\.?\d*)',
            lambda m: m.group(1) + colorize(m.group(2), "BLUE"),
            json_str
        )
        
        # Highlight true, false, null
        json_str = re.sub(
            r'(:\s*)(true|false|null)',
            lambda m: m.group(1) + colorize(m.group(2), "MAGENTA"),
            json_str
        )
    
    return json_str


def format_list(items: list, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats a list of items with bullet points and optional indentation.
    
    Args:
        items: The list of items to format
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted list string
    """
    if not items:
        return ""
    
    # Get style settings or use defaults
    style_settings = TEXT_STYLES.get(style, TEXT_STYLES[DEFAULT_STYLE])
    indent = style_settings["indent"]
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Format each item with a bullet point
    formatted_items = []
    for item in items:
        bullet = LIST_BULLET
        if use_colors:
            bullet = colorize(bullet, "CYAN")
        
        formatted_item = " " * indent + bullet + str(item)
        formatted_items.append(formatted_item)
    
    # Join formatted items with newlines
    return "\n".join(formatted_items)


def format_key_value(data: dict, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats key-value pairs with proper alignment and optional coloring.
    
    Args:
        data: The key-value pairs to format
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted key-value string
    """
    if not data:
        return ""
    
    # Get style settings or use defaults
    style_settings = TEXT_STYLES.get(style, TEXT_STYLES[DEFAULT_STYLE])
    indent = style_settings["indent"]
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Find the maximum key length for alignment
    max_key_length = max(len(str(key)) for key in data.keys())
    
    # Format each key-value pair
    formatted_pairs = []
    for key, value in data.items():
        key_str = str(key)
        value_str = str(value)
        
        # Apply color to key if colors are supported
        if use_colors:
            key_str = colorize(key_str, "CYAN")
        
        # Format with alignment
        formatted_pair = " " * indent + key_str.ljust(max_key_length) + KEY_VALUE_SEPARATOR + value_str
        formatted_pairs.append(formatted_pair)
    
    # Join formatted pairs with newlines
    return "\n".join(formatted_pairs)


def format_sections(sections: dict, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats multiple sections with headers and content.
    
    Args:
        sections: Dictionary mapping section headers to content
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted sections string
    """
    if not sections:
        return ""
    
    # Get style settings or use defaults
    style_settings = TEXT_STYLES.get(style, TEXT_STYLES[DEFAULT_STYLE])
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Format each section
    formatted_sections = []
    for header, content in sections.items():
        # Format header
        if use_colors:
            header = colorize(header, "YELLOW", bold=True)
        
        # Add header and separator line
        formatted_section = header + "\n" + SECTION_SEPARATOR * len(header)
        
        # Format content based on its type
        if isinstance(content, str):
            formatted_content = format_text(content, style, use_colors)
        elif isinstance(content, list):
            formatted_content = format_list(content, style, use_colors)
        elif isinstance(content, dict):
            formatted_content = format_key_value(content, style, use_colors)
        else:
            formatted_content = format_text(str(content), style, use_colors)
        
        # Add formatted content to the section
        formatted_section += "\n" + formatted_content
        
        # Add the section to the list
        formatted_sections.append(formatted_section)
    
    # Join sections with double newlines
    return "\n\n".join(formatted_sections)


def format_error(error: ErrorResponse, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats an error response with message and resolution steps.
    
    Args:
        error: The error response to format
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted error string
    """
    # Get the user-friendly message from the error
    user_message = error.get_user_message()
    
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # Apply error color (red) if colors are supported
    if use_colors:
        user_message = colorize(user_message, "RED")
    
    # Format with appropriate style
    return format_text(user_message, style, use_colors)


def format_cli_response(response: CLIResponse, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None) -> str:
    """
    Formats a CLIResponse object based on its response type and content.
    
    Args:
        response: The CLIResponse object to format
        style: The style name to apply (must be a key in TEXT_STYLES)
        use_colors: Whether to use colors (defaults to terminal capability)
        
    Returns:
        Formatted response string
    """
    # Determine color support
    if use_colors is None:
        use_colors = is_color_supported()
    
    # If we have an error, format it
    if response.error:
        return format_error(response.error, style, use_colors)
    
    # Format message based on response type
    result = ""
    if response.response_type == ResponseType.SUCCESS:
        message = response.message
        if use_colors:
            message = colorize(message, "GREEN")
        result = format_text(message, style, use_colors)
    
    elif response.response_type == ResponseType.ERROR:
        message = response.message
        if use_colors:
            message = colorize(message, "RED")
        result = format_text(message, style, use_colors)
    
    elif response.response_type == ResponseType.WARNING:
        message = response.message
        if use_colors:
            message = colorize(message, "YELLOW")
        result = format_text(message, style, use_colors)
    
    elif response.response_type == ResponseType.INFO:
        message = response.message
        if use_colors:
            message = colorize(message, "BLUE")
        result = format_text(message, style, use_colors)
    
    # Include additional data if present
    if response.data:
        data_str = "\n\nAdditional Information:"
        if use_colors:
            data_str = colorize(data_str, "CYAN", bold=True)
        
        formatted_data = format_json(response.data, indent=4, use_colors=use_colors)
        result += "\n" + data_str + "\n" + formatted_data
    
    return result


class TextFormatter:
    """
    A class that provides methods for formatting various types of text output for the CLI.
    """
    
    def __init__(self, style: str = DEFAULT_STYLE, use_colors: Optional[bool] = None):
        """
        Initializes a new TextFormatter instance with the specified style and color settings.
        
        Args:
            style: The style name to use (must be a key in TEXT_STYLES)
            use_colors: Whether to use colors (defaults to terminal capability)
        """
        # Validate that the style exists in TEXT_STYLES
        if style not in TEXT_STYLES:
            raise ValueError(f"Invalid style: {style}. Must be one of {list(TEXT_STYLES.keys())}")
        
        # Store the style name
        self._style = style
        
        # Determine color support
        if use_colors is None:
            self._use_colors = is_color_supported()
        else:
            self._use_colors = use_colors
    
    def format_text(self, text: str) -> str:
        """
        Formats plain text using the formatter's style settings.
        
        Args:
            text: The text to format
            
        Returns:
            Formatted text string
        """
        return format_text(text, self._style, self._use_colors)
    
    def format_json(self, data: dict) -> str:
        """
        Formats JSON data using the formatter's style settings.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Formatted JSON string
        """
        indent = TEXT_STYLES[self._style]["indent"]
        return format_json(data, indent, self._use_colors)
    
    def format_list(self, items: list) -> str:
        """
        Formats a list of items using the formatter's style settings.
        
        Args:
            items: The list of items to format
            
        Returns:
            Formatted list string
        """
        return format_list(items, self._style, self._use_colors)
    
    def format_key_value(self, data: dict) -> str:
        """
        Formats key-value pairs using the formatter's style settings.
        
        Args:
            data: The key-value pairs to format
            
        Returns:
            Formatted key-value string
        """
        return format_key_value(data, self._style, self._use_colors)
    
    def format_sections(self, sections: dict) -> str:
        """
        Formats multiple sections using the formatter's style settings.
        
        Args:
            sections: Dictionary mapping section headers to content
            
        Returns:
            Formatted sections string
        """
        return format_sections(sections, self._style, self._use_colors)
    
    def format_error(self, error: ErrorResponse) -> str:
        """
        Formats an error response using the formatter's style settings.
        
        Args:
            error: The error response to format
            
        Returns:
            Formatted error string
        """
        return format_error(error, self._style, self._use_colors)
    
    def format_cli_response(self, response: CLIResponse) -> str:
        """
        Formats a CLIResponse object using the formatter's style settings.
        
        Args:
            response: The CLIResponse object to format
            
        Returns:
            Formatted response string
        """
        return format_cli_response(response, self._style, self._use_colors)
    
    def set_style(self, style: str) -> 'TextFormatter':
        """
        Changes the formatter's style settings.
        
        Args:
            style: The new style to use (must be a key in TEXT_STYLES)
            
        Returns:
            Self reference for method chaining
        """
        if style not in TEXT_STYLES:
            raise ValueError(f"Invalid style: {style}. Must be one of {list(TEXT_STYLES.keys())}")
        
        self._style = style
        return self
    
    def set_color_mode(self, use_colors: bool) -> 'TextFormatter':
        """
        Changes the formatter's color settings.
        
        Args:
            use_colors: Whether to use colors
            
        Returns:
            Self reference for method chaining
        """
        self._use_colors = use_colors
        return self