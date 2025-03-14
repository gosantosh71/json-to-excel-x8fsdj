"""
Provides functionality for formatting tabular data as ASCII tables for the command line interface 
of the JSON to Excel Conversion Tool. This module handles the conversion of various data structures 
(DataFrames, dictionaries, lists) into formatted tables with proper alignment, borders, and styling 
for CLI display.
"""

import pandas  # v: pandas 1.5.0+
from typing import Dict, List, Any, Optional, Union  # v: built-in

from ...backend.logger import get_logger
from ..utils.console_utils import get_terminal_size, is_color_supported

# Initialize logger
logger = get_logger(__name__)

# Table style definitions
TABLE_STYLES = {
    "DEFAULT": {
        "border": True,
        "header_style": "bold",
        "max_column_width": 30,
        "alignment": "left",
        "border_chars": {"+": "+", "-": "-", "|": "|"}
    },
    "COMPACT": {
        "border": False,
        "header_style": "bold",
        "max_column_width": 20,
        "alignment": "left",
        "border_chars": {"+": " ", "-": " ", "|": " "}
    },
    "GRID": {
        "border": True,
        "header_style": "bold",
        "max_column_width": 40,
        "alignment": "left",
        "border_chars": {"+": "+", "-": "─", "|": "│"}
    }
}

def get_table_style(style: str) -> Dict[str, Any]:
    """
    Gets the table style settings based on the specified style name.
    
    Args:
        style: Name of the style to retrieve
        
    Returns:
        Dictionary of style settings
    """
    if style in TABLE_STYLES:
        return TABLE_STYLES[style]
    
    logger.warning(f"Invalid table style requested: {style}. Using DEFAULT.")
    return TABLE_STYLES["DEFAULT"]

def calculate_column_widths(df: pandas.DataFrame, max_column_width: int) -> Dict[str, int]:
    """
    Calculates appropriate column widths based on data content and terminal size.
    
    Args:
        df: Pandas DataFrame containing the data
        max_column_width: Maximum allowed width for any column
        
    Returns:
        Dictionary mapping column names to widths
    """
    # Get terminal width
    terminal_width, _ = get_terminal_size()
    
    # Start with minimum width based on column names
    column_widths = {col: min(max(len(str(col)), 3), max_column_width) for col in df.columns}
    
    # Update widths based on data values
    for col in df.columns:
        # Get maximum string length in the column (handling NaN values)
        max_data_width = df[col].astype(str).map(len).max()
        if not pandas.isna(max_data_width):  # Check if max_data_width is not NaN
            # Update column width with the minimum of data width and max_column_width
            column_widths[col] = min(max(column_widths[col], max_data_width), max_column_width)
    
    # Check if total width exceeds terminal width
    border_width = 1 if terminal_width > 0 else 0  # Border width per column
    total_width = sum(column_widths.values()) + (len(df.columns) + 1) * border_width * 2
    
    if total_width > terminal_width and terminal_width > 0:
        # Adjust column widths proportionally to fit terminal
        available_width = terminal_width - (len(df.columns) + 1) * border_width * 2
        scaling_factor = available_width / sum(column_widths.values())
        
        for col in column_widths:
            # Ensure minimum width of 3
            column_widths[col] = max(3, int(column_widths[col] * scaling_factor))
    
    return column_widths

def format_cell(value: Any, width: int, alignment: str = 'left') -> str:
    """
    Formats a cell value to fit within a specified width with alignment.
    
    Args:
        value: Cell value to format
        width: Target width for the cell
        alignment: Text alignment ('left', 'right', or 'center')
        
    Returns:
        Formatted cell string
    """
    # Convert value to string, handling None and NaN
    if value is None:
        text = ""
    elif pandas.isna(value):
        text = ""
    else:
        text = str(value)
    
    # Truncate if too long
    if len(text) > width:
        text = text[:width-3] + "..."
    
    # Apply alignment
    if alignment.lower() == 'right':
        return text.rjust(width)
    elif alignment.lower() == 'center':
        return text.center(width)
    else:  # Default to left align
        return text.ljust(width)

def dataframe_to_table(df: pandas.DataFrame, style: str = 'DEFAULT', use_colors: bool = True) -> str:
    """
    Converts a pandas DataFrame to an ASCII table.
    
    Args:
        df: The DataFrame to convert
        style: Table style to use
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted ASCII table string
    """
    # Check if DataFrame is empty
    if df.empty:
        return "Empty table"
    
    # Get style settings
    style_settings = get_table_style(style)
    border = style_settings["border"]
    max_column_width = style_settings["max_column_width"]
    alignment = style_settings["alignment"]
    border_chars = style_settings["border_chars"]
    
    # Calculate column widths
    column_widths = calculate_column_widths(df, max_column_width)
    
    # Prepare table components
    lines = []
    
    # Create horizontal line
    if border:
        horizontal_line = border_chars["+"]
        for col in df.columns:
            horizontal_line += border_chars["-"] * (column_widths[col] + 2) + border_chars["+"]
        lines.append(horizontal_line)
    
    # Create header row
    header_line = border_chars["|"] if border else ""
    for col in df.columns:
        header_text = format_cell(col, column_widths[col], alignment)
        header_line += f" {header_text} {border_chars['|'] if border else ''}"
    lines.append(header_line)
    
    # Add separator after header
    if border:
        lines.append(horizontal_line)
    
    # Create data rows
    for _, row in df.iterrows():
        data_line = border_chars["|"] if border else ""
        for col in df.columns:
            cell_text = format_cell(row[col], column_widths[col], alignment)
            data_line += f" {cell_text} {border_chars['|'] if border else ''}"
        lines.append(data_line)
    
    # Add bottom border
    if border:
        lines.append(horizontal_line)
    
    # Join lines into a table
    table = "\n".join(lines)
    
    return table

def dict_to_table(data: Dict[str, Any], style: str = 'DEFAULT', use_colors: bool = True) -> str:
    """
    Converts a dictionary to a two-column ASCII table with keys and values.
    
    Args:
        data: Dictionary to convert
        style: Table style to use
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted ASCII table string
    """
    # Handle empty dictionary
    if not data:
        return "Empty table"
    
    # Convert dictionary to DataFrame with key-value columns
    df = pandas.DataFrame(list(data.items()), columns=['Key', 'Value'])
    
    # Convert DataFrame to table
    return dataframe_to_table(df, style, use_colors)

def list_to_table(data: List[Dict[str, Any]], style: str = 'DEFAULT', use_colors: bool = True) -> str:
    """
    Converts a list of dictionaries to an ASCII table.
    
    Args:
        data: List of dictionaries to convert
        style: Table style to use
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted ASCII table string
    """
    # Handle empty list
    if not data:
        return "Empty table"
    
    # Convert list of dictionaries to DataFrame
    df = pandas.DataFrame(data)
    
    # Convert DataFrame to table
    return dataframe_to_table(df, style, use_colors)

def format_table(data: Union[pandas.DataFrame, Dict[str, Any], List[Dict[str, Any]]], 
                style: str = 'DEFAULT', use_colors: bool = True) -> str:
    """
    Formats data as an ASCII table with optional styling.
    
    Args:
        data: Data to format (DataFrame, dictionary, or list of dictionaries)
        style: Table style to use
        use_colors: Whether to use colors in the output
        
    Returns:
        Formatted ASCII table string
    """
    # Determine data type and call appropriate conversion function
    if isinstance(data, pandas.DataFrame):
        return dataframe_to_table(data, style, use_colors)
    elif isinstance(data, dict):
        return dict_to_table(data, style, use_colors)
    elif isinstance(data, list):
        if not data:  # Handle empty list
            return "Empty table"
        if all(isinstance(item, dict) for item in data):
            return list_to_table(data, style, use_colors)
        else:
            logger.warning("List contains non-dictionary items, cannot format as table")
            return str(data)
    else:
        logger.warning(f"Unsupported data type for table formatting: {type(data)}")
        return str(data)

class TableFormatter:
    """
    A class that provides methods for formatting various data structures as ASCII tables for CLI display.
    """
    
    def __init__(self, style: str = 'DEFAULT', use_colors: bool = None):
        """
        Initializes a new TableFormatter instance with the specified styling options.
        
        Args:
            style: Table style to use
            use_colors: Whether to use colors in the output (auto-detect if None)
        """
        self._style = style if style in TABLE_STYLES else 'DEFAULT'
        if style not in TABLE_STYLES:
            logger.warning(f"Invalid table style: {style}. Using DEFAULT.")
        
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        self._logger = get_logger(__name__)
        
    def format_data(self, data: Union[pandas.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Formats data as an ASCII table based on its type.
        
        Args:
            data: Data to format (DataFrame, dictionary, or list of dictionaries)
            
        Returns:
            Formatted ASCII table string
        """
        return format_table(data, self._style, self._use_colors)
    
    def format_dataframe(self, df: pandas.DataFrame) -> str:
        """
        Formats a pandas DataFrame as an ASCII table.
        
        Args:
            df: DataFrame to format
            
        Returns:
            Formatted ASCII table string
        """
        return dataframe_to_table(df, self._style, self._use_colors)
    
    def format_dict(self, data: Dict[str, Any]) -> str:
        """
        Formats a dictionary as a two-column ASCII table.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted ASCII table string
        """
        return dict_to_table(data, self._style, self._use_colors)
    
    def format_list(self, data: List[Dict[str, Any]]) -> str:
        """
        Formats a list of dictionaries as an ASCII table.
        
        Args:
            data: List of dictionaries to format
            
        Returns:
            Formatted ASCII table string
        """
        return list_to_table(data, self._style, self._use_colors)
    
    def set_style(self, style: str) -> None:
        """
        Sets the table style to use for formatting.
        
        Args:
            style: Style name to use
            
        Returns:
            None: Updates style in-place
        """
        if style not in TABLE_STYLES:
            self._logger.warning(f"Invalid table style: {style}. Using current style: {self._style}.")
            return
        
        self._style = style
        self._logger.debug(f"Table style set to: {style}")
    
    def set_use_colors(self, use_colors: bool) -> None:
        """
        Sets whether to use colors in the formatted output.
        
        Args:
            use_colors: Whether to use colors
            
        Returns:
            None: Updates color setting in-place
        """
        self._use_colors = use_colors
        self._logger.debug(f"Table color setting set to: {use_colors}")