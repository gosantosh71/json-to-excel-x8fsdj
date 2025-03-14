"""
Defines the data model for conversion options in the web interface of the JSON to Excel Conversion Tool.

This module provides a structured way to configure conversion settings from web form data 
and validate user inputs before processing.
"""

from dataclasses import dataclass  # v: built-in
from typing import Dict, Optional, Any  # v: built-in

from ../../backend/models/excel_options import ArrayHandlingStrategy, ExcelOptions
from ..constants import WEB_CONSTANTS


@dataclass
class ConversionOptions:
    """
    A data class that represents configuration options for JSON to Excel conversion in the web interface.
    """
    sheet_name: str
    array_handling: str
    format_headers: bool
    auto_column_width: bool
    apply_data_formatting: bool
    additional_options: Optional[Dict[str, Any]]

    def __init__(
        self,
        sheet_name: Optional[str] = None,
        array_handling: Optional[str] = None,
        format_headers: Optional[bool] = None,
        auto_column_width: Optional[bool] = None,
        apply_data_formatting: Optional[bool] = None,
        additional_options: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new ConversionOptions instance with the provided configuration options.
        
        Args:
            sheet_name: The name of the Excel worksheet.
            array_handling: How to handle arrays in JSON data ('expand' or 'join').
            format_headers: Whether to apply formatting to header cells.
            auto_column_width: Whether to automatically adjust column widths.
            apply_data_formatting: Whether to apply data type-specific formatting.
            additional_options: Dictionary for any other options.
        """
        self.sheet_name = sheet_name or WEB_CONSTANTS["DEFAULT_SHEET_NAME"]
        self.array_handling = array_handling or "expand"
        self.format_headers = True if format_headers is None else format_headers
        self.auto_column_width = True if auto_column_width is None else auto_column_width
        self.apply_data_formatting = True if apply_data_formatting is None else apply_data_formatting
        self.additional_options = additional_options or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ConversionOptions object to a dictionary representation.
        
        Returns:
            A dictionary representation of the ConversionOptions object
        """
        return {
            "sheet_name": self.sheet_name,
            "array_handling": self.array_handling,
            "format_headers": self.format_headers,
            "auto_column_width": self.auto_column_width,
            "apply_data_formatting": self.apply_data_formatting,
            "additional_options": self.additional_options
        }
    
    def to_excel_options(self) -> ExcelOptions:
        """
        Converts web ConversionOptions to backend ExcelOptions.
        
        Returns:
            An ExcelOptions instance for backend processing
        """
        options_dict = self.to_dict()
        
        # Map array_handling string to ArrayHandlingStrategy enum
        if self.array_handling == "expand":
            array_strategy = ArrayHandlingStrategy.EXPAND
        elif self.array_handling == "join":
            array_strategy = ArrayHandlingStrategy.JOIN
        else:
            array_strategy = ArrayHandlingStrategy.EXPAND  # Default
        
        # Replace the string with the enum
        options_dict["array_handling"] = array_strategy
        
        # Create the ExcelOptions instance
        return ExcelOptions.from_dict(options_dict)

    @classmethod
    def from_dict(cls, options_dict: Dict[str, Any]) -> 'ConversionOptions':
        """
        Creates a ConversionOptions instance from a dictionary.
        
        Args:
            options_dict: A dictionary containing conversion options
            
        Returns:
            A new ConversionOptions instance
        """
        # Extract values with appropriate defaults
        sheet_name = options_dict.get("sheet_name")
        array_handling = options_dict.get("array_handling")
        format_headers = options_dict.get("format_headers")
        auto_column_width = options_dict.get("auto_column_width")
        apply_data_formatting = options_dict.get("apply_data_formatting")
        additional_options = options_dict.get("additional_options", {})
        
        return cls(
            sheet_name=sheet_name,
            array_handling=array_handling,
            format_headers=format_headers,
            auto_column_width=auto_column_width,
            apply_data_formatting=apply_data_formatting,
            additional_options=additional_options
        )
    
    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> 'ConversionOptions':
        """
        Creates a ConversionOptions instance from web form data.
        
        Args:
            form_data: Dictionary containing form data from the web interface
            
        Returns:
            A new ConversionOptions instance
        """
        # Extract values with appropriate defaults
        sheet_name = form_data.get("sheet_name", WEB_CONSTANTS["DEFAULT_SHEET_NAME"])
        array_handling = form_data.get("array_handling", "expand")
        
        # Handle boolean values from form checkboxes
        # Form checkboxes typically send 'on' or are missing, so convert to boolean
        format_headers = bool(form_data.get("format_headers", True))
        auto_column_width = bool(form_data.get("auto_column_width", True))
        apply_data_formatting = bool(form_data.get("apply_data_formatting", True))
        
        # Extract any additional options
        additional_options = {}
        for key, value in form_data.items():
            if key not in ["sheet_name", "array_handling", "format_headers", 
                           "auto_column_width", "apply_data_formatting"]:
                additional_options[key] = value
        
        return cls(
            sheet_name=sheet_name,
            array_handling=array_handling,
            format_headers=format_headers,
            auto_column_width=auto_column_width,
            apply_data_formatting=apply_data_formatting,
            additional_options=additional_options
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validates the conversion options for correctness.
        
        Returns:
            A tuple containing (is_valid, error_message)
            where is_valid is a boolean indicating validity and
            error_message is None if valid or an error message string if invalid.
        """
        # Check if sheet_name is not empty
        if not self.sheet_name:
            return False, "Sheet name cannot be empty."
        
        # Check if array_handling is valid
        if self.array_handling not in ["expand", "join"]:
            return False, "Array handling must be either 'expand' or 'join'."
        
        # All validations passed
        return True, None


class DefaultConversionOptions:
    """
    A class that provides default conversion options for the web interface.
    """
    
    @staticmethod
    def get_defaults() -> ConversionOptions:
        """
        Returns the default conversion options.
        
        Returns:
            A ConversionOptions instance with default values
        """
        return ConversionOptions(
            sheet_name=WEB_CONSTANTS["DEFAULT_SHEET_NAME"],
            array_handling="expand",
            format_headers=True,
            auto_column_width=True,
            apply_data_formatting=True,
            additional_options={}
        )
    
    @staticmethod
    def get_default_dict() -> Dict[str, Any]:
        """
        Returns the default conversion options as a dictionary.
        
        Returns:
            A dictionary with default conversion options
        """
        return DefaultConversionOptions.get_defaults().to_dict()