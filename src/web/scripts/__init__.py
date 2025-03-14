"""
Initialization module for scripts in the JSON to Excel Conversion Tool web interface.

This module exposes utility scripts for setup and maintenance tasks, including
file cleanup operations to prevent resource exhaustion in the upload directory.
"""

from .cleanup_uploads import cleanup_old_files, main

# Export the cleanup script functions
__all__ = ["cleanup_old_files", "main"]