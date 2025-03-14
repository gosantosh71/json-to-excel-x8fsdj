"""
Provides specialized formatting utilities for generating JSON previews in the CLI component 
of the JSON to Excel Conversion Tool. This module creates concise, readable previews of JSON 
structures to help users understand the data they're converting without displaying the entire content.
"""

import json  # v: built-in
from typing import Dict, List, Any, Optional, Union  # v: built-in

from ..utils.console_utils import colorize, is_color_supported, get_terminal_size
from ...backend.json_parser import JSONParser

# Define formatting styles with their settings
PREVIEW_STYLES = {
    "DEFAULT": {
        "indent": 2,
        "max_depth": 3,
        "max_items": 3,
        "max_string_length": 30,
        "truncation_indicator": "...",
        "show_types": True
    },
    "COMPACT": {
        "indent": 0,
        "max_depth": 2,
        "max_items": 2,
        "max_string_length": 20,
        "truncation_indicator": "...",
        "show_types": False
    },
    "VERBOSE": {
        "indent": 4,
        "max_depth": 5,
        "max_items": 5,
        "max_string_length": 50,
        "truncation_indicator": "...",
        "show_types": True
    }
}

DEFAULT_STYLE = "DEFAULT"

TYPE_INDICATORS = {
    "object": "{",
    "array": "[",
    "string": "\"\""
}


def format_json_preview(data: Dict[str, Any], style: str = DEFAULT_STYLE, use_colors: bool = None) -> str:
    """
    Creates a formatted preview of JSON data with limited depth and items.
    
    Args:
        data: The JSON data to format
        style: The formatting style to use (DEFAULT, COMPACT, VERBOSE)
        use_colors: Whether to use colors in the output (defaults to terminal capability)
        
    Returns:
        Formatted JSON preview string
    """
    if style not in PREVIEW_STYLES:
        style = DEFAULT_STYLE
    
    if use_colors is None:
        use_colors = is_color_supported()
    
    formatter = JSONPreviewFormatter(style, use_colors)
    return formatter.format_preview(data)


def generate_structure_preview(data: Dict[str, Any], style: str = DEFAULT_STYLE, use_colors: bool = None) -> str:
    """
    Generates a structural preview of JSON data showing types and nesting.
    
    Args:
        data: The JSON data to format
        style: The formatting style to use (DEFAULT, COMPACT, VERBOSE)
        use_colors: Whether to use colors in the output (defaults to terminal capability)
        
    Returns:
        Structural preview of the JSON data
    """
    if style not in PREVIEW_STYLES:
        style = DEFAULT_STYLE
    
    if use_colors is None:
        use_colors = is_color_supported()
    
    formatter = JSONPreviewFormatter(style, use_colors)
    return formatter.format_structure(data)


def get_type_indicator(value: Any, use_colors: bool) -> str:
    """
    Returns a visual indicator for the type of a JSON value.
    
    Args:
        value: The value to get the type indicator for
        use_colors: Whether to apply color formatting
        
    Returns:
        Type indicator string
    """
    if isinstance(value, dict):
        indicator = TYPE_INDICATORS["object"]
        color = "CYAN" if use_colors else None
    elif isinstance(value, list):
        indicator = TYPE_INDICATORS["array"]
        color = "MAGENTA" if use_colors else None
    elif isinstance(value, str):
        indicator = TYPE_INDICATORS["string"]
        color = "GREEN" if use_colors else None
    elif isinstance(value, bool):
        indicator = str(value).lower()
        color = "YELLOW" if use_colors else None
    elif isinstance(value, (int, float)):
        indicator = str(value)
        color = "BLUE" if use_colors else None
    elif value is None:
        indicator = "null"
        color = "RED" if use_colors else None
    else:
        indicator = str(type(value).__name__)
        color = None
    
    if use_colors and color:
        return colorize(indicator, color)
    return indicator


def truncate_string(text: str, max_length: int, indicator: str) -> str:
    """
    Truncates a string to the specified maximum length with an indicator.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the string
        indicator: String to append if truncated
        
    Returns:
        Truncated string with indicator if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(indicator)] + indicator


class JSONPreviewFormatter:
    """
    A class that provides methods for generating formatted previews of JSON data.
    """
    
    def __init__(self, style: str = DEFAULT_STYLE, use_colors: bool = None):
        """
        Initializes a new JSONPreviewFormatter instance with the specified style and color settings.
        
        Args:
            style: The formatting style to use (DEFAULT, COMPACT, VERBOSE)
            use_colors: Whether to use colors in the output (defaults to terminal capability)
        """
        self._style = style or DEFAULT_STYLE
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        
        if self._style not in PREVIEW_STYLES:
            raise ValueError(f"Unknown style '{self._style}'. Available styles: {', '.join(PREVIEW_STYLES.keys())}")
        
        self._style_settings = PREVIEW_STYLES[self._style]
    
    def format_preview(self, data: Dict[str, Any]) -> str:
        """
        Creates a formatted preview of JSON data with limited depth and items.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Formatted JSON preview string
        """
        if data is None:
            return ""
        
        return self._format_value(data, 0)
    
    def format_structure(self, data: Dict[str, Any]) -> str:
        """
        Generates a structural preview showing the types and nesting of JSON data.
        
        Args:
            data: The JSON data to format
            
        Returns:
            Structural preview of the JSON data
        """
        if data is None:
            return ""
        
        # Use JSONParser to get structure information
        parser = JSONParser()
        structure_info = parser.get_structure_info(data)
        
        # Extract key structure information
        max_nesting = structure_info.get("max_nesting_level", 0)
        is_nested = structure_info.get("is_nested", False)
        contains_arrays = structure_info.get("contains_arrays", False)
        array_count = structure_info.get("array_count", 0)
        complexity = structure_info.get("complexity_level", "SIMPLE")
        
        # Format a summary of the structure
        summary = f"JSON Structure:"
        if self._use_colors:
            summary = colorize(summary, "BOLD")
        
        structure_lines = [
            summary,
            f"  - Nesting Level: {max_nesting}",
            f"  - Contains Nested Objects: {'Yes' if is_nested else 'No'}",
            f"  - Contains Arrays: {'Yes' if contains_arrays else 'No'}",
            f"  - Array Count: {array_count}",
            f"  - Complexity: {complexity}"
        ]
        
        # Add a type preview
        type_preview = self._format_value(data, 0)
        structure_lines.append("\nStructure Preview:")
        structure_lines.append(type_preview)
        
        return "\n".join(structure_lines)
    
    def format_value_preview(self, value: Any) -> str:
        """
        Formats a single JSON value for preview with type information.
        
        Args:
            value: The value to format
            
        Returns:
            Formatted value preview
        """
        # Format the value
        formatted_value = self._format_value(value, 0)
        
        # Add type information if enabled
        if self._style_settings.get("show_types", True):
            type_name = type(value).__name__
            if self._use_colors:
                type_name = colorize(type_name, "YELLOW")
            return f"{formatted_value} ({type_name})"
        
        return formatted_value
    
    def _format_value(self, value: Any, depth: int) -> str:
        """
        Internal method to recursively format a JSON value with depth tracking.
        
        Args:
            value: The value to format
            depth: Current nesting depth
            
        Returns:
            Recursively formatted value
        """
        max_depth = self._style_settings.get("max_depth", 3)
        if depth > max_depth:
            indicator = self._style_settings.get("truncation_indicator", "...")
            if self._use_colors:
                return colorize(indicator, "RED")
            return indicator
        
        if isinstance(value, dict):
            return self._format_object(value, depth)
        elif isinstance(value, list):
            return self._format_array(value, depth)
        elif isinstance(value, str):
            max_length = self._style_settings.get("max_string_length", 30)
            indicator = self._style_settings.get("truncation_indicator", "...")
            truncated = truncate_string(value, max_length, indicator)
            if self._use_colors:
                return colorize(f'"{truncated}"', "GREEN")
            return f'"{truncated}"'
        elif isinstance(value, bool):
            result = str(value).lower()
            if self._use_colors:
                return colorize(result, "YELLOW")
            return result
        elif isinstance(value, (int, float)):
            result = str(value)
            if self._use_colors:
                return colorize(result, "BLUE")
            return result
        elif value is None:
            result = "null"
            if self._use_colors:
                return colorize(result, "RED")
            return result
        else:
            # Fallback for unknown types
            return str(value)
    
    def _format_object(self, obj: Dict[str, Any], depth: int) -> str:
        """
        Internal method to format a JSON object with limited keys.
        
        Args:
            obj: The object to format
            depth: Current nesting depth
            
        Returns:
            Formatted object preview
        """
        if not obj:
            return "{}"
        
        indent = self._style_settings.get("indent", 2)
        max_items = self._style_settings.get("max_items", 3)
        indicator = self._style_settings.get("truncation_indicator", "...")
        
        # Calculate indentation
        indent_str = " " * indent
        current_indent = indent_str * depth
        next_indent = indent_str * (depth + 1)
        
        # Format each key-value pair up to max_items
        formatted_items = []
        keys = list(obj.keys())
        
        for i, key in enumerate(keys[:max_items]):
            value = obj[key]
            formatted_value = self._format_value(value, depth + 1)
            if self._use_colors:
                formatted_key = colorize(f'"{key}"', "CYAN")
            else:
                formatted_key = f'"{key}"'
            
            formatted_items.append(f"{next_indent}{formatted_key}: {formatted_value}")
        
        # Add indicator if there are more items
        if len(obj) > max_items:
            more_count = len(obj) - max_items
            more_indicator = f"{next_indent}/* {more_count} more... */"
            if self._use_colors:
                more_indicator = colorize(more_indicator, "RED")
            formatted_items.append(more_indicator)
        
        # Join items with commas
        joined_items = ",\n".join(formatted_items)
        
        # Assemble the formatted object
        result = "{\n" + joined_items + f"\n{current_indent}}}"
        return result
    
    def _format_array(self, arr: List[Any], depth: int) -> str:
        """
        Internal method to format a JSON array with limited items.
        
        Args:
            arr: The array to format
            depth: Current nesting depth
            
        Returns:
            Formatted array preview
        """
        if not arr:
            return "[]"
        
        indent = self._style_settings.get("indent", 2)
        max_items = self._style_settings.get("max_items", 3)
        indicator = self._style_settings.get("truncation_indicator", "...")
        
        # Calculate indentation
        indent_str = " " * indent
        current_indent = indent_str * depth
        next_indent = indent_str * (depth + 1)
        
        # Format each item up to max_items
        formatted_items = []
        
        for i, item in enumerate(arr[:max_items]):
            formatted_value = self._format_value(item, depth + 1)
            formatted_items.append(f"{next_indent}{formatted_value}")
        
        # Add indicator if there are more items
        if len(arr) > max_items:
            more_count = len(arr) - max_items
            more_indicator = f"{next_indent}/* {more_count} more... */"
            if self._use_colors:
                more_indicator = colorize(more_indicator, "RED")
            formatted_items.append(more_indicator)
        
        # Join items with commas
        joined_items = ",\n".join(formatted_items)
        
        # Assemble the formatted array
        result = "[\n" + joined_items + f"\n{current_indent}]"
        return result
    
    def set_style(self, style: str) -> 'JSONPreviewFormatter':
        """
        Changes the formatter's style settings.
        
        Args:
            style: The new style to use
            
        Returns:
            Self reference for method chaining
        """
        if style not in PREVIEW_STYLES:
            raise ValueError(f"Unknown style '{style}'. Available styles: {', '.join(PREVIEW_STYLES.keys())}")
        
        self._style = style
        self._style_settings = PREVIEW_STYLES[style]
        return self
    
    def set_color_mode(self, use_colors: bool) -> 'JSONPreviewFormatter':
        """
        Changes the formatter's color settings.
        
        Args:
            use_colors: Whether to use colors in the output
            
        Returns:
            Self reference for method chaining
        """
        self._use_colors = use_colors
        return self