"""
Excel options model for the JSON to Excel Conversion Tool.

This module defines configuration options for Excel file generation,
including sheet naming, column formatting, and array handling strategies.
"""

from dataclasses import dataclass  # v: built-in
from enum import Enum  # v: built-in
from typing import Dict, List, Optional, Any  # v: built-in

from ..constants import EXCEL_CONSTANTS


class ArrayHandlingStrategy(Enum):
    """
    An enumeration defining strategies for handling arrays in JSON data during conversion to Excel.
    
    Attributes:
        EXPAND: Expand arrays into multiple rows (e.g., each array item becomes a separate row)
        JOIN: Join array elements into a single cell (e.g., using comma-separated values)
    """
    EXPAND = "expand"
    JOIN = "join"


@dataclass
class ExcelOptions:
    """
    A data class that represents configuration options for Excel file generation,
    including formatting preferences and array handling strategies.
    
    Attributes:
        sheet_name: The name of the Excel worksheet.
        array_handling: The strategy for handling arrays in JSON data.
        format_headers: Whether to apply formatting to header cells (e.g., bold, background color).
        freeze_header_row: Whether to freeze the header row for better navigation.
        auto_column_width: Whether to automatically adjust column widths based on content.
        apply_data_formatting: Whether to apply data type-specific formatting (e.g., date formats, numbers).
        column_formats: Dictionary mapping column names to Excel format strings.
        workbook_properties: Dictionary of workbook metadata properties.
        additional_options: Dictionary for any other options not covered by specific fields.
    """
    sheet_name: str
    array_handling: ArrayHandlingStrategy
    format_headers: bool
    freeze_header_row: bool
    auto_column_width: bool
    apply_data_formatting: bool
    column_formats: Optional[Dict[str, str]]
    workbook_properties: Optional[Dict[str, Any]]
    additional_options: Optional[Dict[str, Any]]

    def __init__(
        self,
        sheet_name: Optional[str] = None,
        array_handling: Optional[ArrayHandlingStrategy] = None,
        format_headers: Optional[bool] = None,
        freeze_header_row: Optional[bool] = None,
        auto_column_width: Optional[bool] = None,
        apply_data_formatting: Optional[bool] = None,
        column_formats: Optional[Dict[str, str]] = None,
        workbook_properties: Optional[Dict[str, Any]] = None,
        additional_options: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ExcelOptions instance with the provided configuration options.
        
        Args:
            sheet_name: The name of the Excel worksheet.
            array_handling: The strategy for handling arrays in JSON data.
            format_headers: Whether to apply formatting to header cells.
            freeze_header_row: Whether to freeze the header row.
            auto_column_width: Whether to automatically adjust column widths.
            apply_data_formatting: Whether to apply data type-specific formatting.
            column_formats: Dictionary mapping column names to Excel format strings.
            workbook_properties: Dictionary of workbook metadata properties.
            additional_options: Dictionary for any other options.
        """
        self.sheet_name = sheet_name or EXCEL_CONSTANTS["DEFAULT_SHEET_NAME"]
        self.array_handling = array_handling or ArrayHandlingStrategy.EXPAND
        self.format_headers = True if format_headers is None else format_headers
        self.freeze_header_row = False if freeze_header_row is None else freeze_header_row
        self.auto_column_width = True if auto_column_width is None else auto_column_width
        self.apply_data_formatting = True if apply_data_formatting is None else apply_data_formatting
        self.column_formats = column_formats or {}
        self.workbook_properties = workbook_properties or {}
        self.additional_options = additional_options or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ExcelOptions object to a dictionary representation.
        
        Returns:
            A dictionary representation of the ExcelOptions object
        """
        return {
            "sheet_name": self.sheet_name,
            "array_handling": self.array_handling.value,
            "format_headers": self.format_headers,
            "freeze_header_row": self.freeze_header_row,
            "auto_column_width": self.auto_column_width,
            "apply_data_formatting": self.apply_data_formatting,
            "column_formats": self.column_formats,
            "workbook_properties": self.workbook_properties,
            "additional_options": self.additional_options
        }

    @classmethod
    def from_dict(cls, options_dict: Dict[str, Any]) -> 'ExcelOptions':
        """
        Creates an ExcelOptions instance from a dictionary.
        
        Args:
            options_dict: A dictionary containing Excel options
            
        Returns:
            A new ExcelOptions instance
        """
        # Extract values with appropriate defaults
        sheet_name = options_dict.get("sheet_name")
        
        # Convert string array_handling value to enum if present
        array_handling_str = options_dict.get("array_handling")
        array_handling = None
        if array_handling_str:
            try:
                array_handling = ArrayHandlingStrategy(array_handling_str)
            except ValueError:
                # Default to EXPAND if invalid value
                array_handling = ArrayHandlingStrategy.EXPAND
        
        # Extract other values
        format_headers = options_dict.get("format_headers")
        freeze_header_row = options_dict.get("freeze_header_row")
        auto_column_width = options_dict.get("auto_column_width")
        apply_data_formatting = options_dict.get("apply_data_formatting")
        column_formats = options_dict.get("column_formats", {})
        workbook_properties = options_dict.get("workbook_properties", {})
        additional_options = options_dict.get("additional_options", {})
        
        return cls(
            sheet_name=sheet_name,
            array_handling=array_handling,
            format_headers=format_headers,
            freeze_header_row=freeze_header_row,
            auto_column_width=auto_column_width,
            apply_data_formatting=apply_data_formatting,
            column_formats=column_formats,
            workbook_properties=workbook_properties,
            additional_options=additional_options
        )
    
    def merge(self, other: 'ExcelOptions') -> 'ExcelOptions':
        """
        Merges this ExcelOptions instance with another, prioritizing non-default values from the other instance.
        
        Args:
            other: Another ExcelOptions instance to merge with
            
        Returns:
            A new ExcelOptions instance with merged values
        """
        # Start with values from this instance
        merged_dict = self.to_dict()
        
        # Update with non-default values from the other instance
        other_dict = other.to_dict()
        for key, value in other_dict.items():
            if value is not None:
                # Special handling for dictionaries - merge them instead of replacing
                if isinstance(value, dict) and isinstance(merged_dict.get(key), dict):
                    merged_dict[key].update(value)
                else:
                    merged_dict[key] = value
        
        # Create a new instance from the merged dictionary
        return self.from_dict(merged_dict)
    
    def get_column_format(self, column_name: str) -> Optional[str]:
        """
        Gets the format string for a specific column if defined.
        
        Args:
            column_name: The name of the column
            
        Returns:
            The format string for the column or None if not defined
        """
        if not self.column_formats:
            return None
            
        return self.column_formats.get(column_name)