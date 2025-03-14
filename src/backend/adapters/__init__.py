"""
Initializes the adapters package and exports adapter classes for the JSON to Excel Conversion Tool.

This file makes the adapter implementations accessible throughout the application by importing
and re-exporting them, simplifying imports for other modules.
"""

from .file_system_adapter import FileSystemAdapter, TempFileContext, TempDirectoryContext

# Define what should be exported when using 'from adapters import *'
__all__ = ["FileSystemAdapter", "TempFileContext", "TempDirectoryContext"]