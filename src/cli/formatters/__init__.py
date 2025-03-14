"""
Initializes the formatters package for the CLI component of the JSON to Excel Conversion Tool.

This module exports the various formatter classes and utility functions that handle
different aspects of output formatting for the command-line interface, including
text formatting, table formatting, and JSON preview formatting.
"""

# Version information
__version__ = "1.0.0"

# Import formatter classes
from .table_formatter import TableFormatter
from .text_formatter import TextFormatter
from .json_preview_formatter import JSONPreviewFormatter

# Import utility functions
from .table_formatter import format_table
from .text_formatter import (
    format_text,
    format_json,
    format_list,
    format_key_value,
    format_sections,
    format_error,
    format_cli_response
)
from .json_preview_formatter import (
    format_json_preview,
    generate_structure_preview
)

# Import style constants
from .table_formatter import TABLE_STYLES
from .text_formatter import TEXT_STYLES
from .json_preview_formatter import PREVIEW_STYLES

# Define what's exported when using "from cli.formatters import *"
__all__ = [
    # Classes
    "TableFormatter",
    "TextFormatter", 
    "JSONPreviewFormatter",
    
    # Functions
    "format_table",
    "format_text",
    "format_json",
    "format_list",
    "format_key_value",
    "format_sections",
    "format_error",
    "format_cli_response",
    "format_json_preview",
    "generate_structure_preview",
    
    # Constants
    "TABLE_STYLES",
    "TEXT_STYLES",
    "PREVIEW_STYLES",
    "__version__"
]