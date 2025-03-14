"""
Utility package for the web interface of the JSON to Excel Conversion Tool.

This module imports and exposes utility functions and classes from various utility
modules to provide a clean, organized interface for file handling, path manipulation,
timing operations, and API response formatting in the web interface.
"""

# Import utilities from file_utils
from .file_utils import (
    FileManager,
    generate_unique_filename,
    is_allowed_file,
    sanitize_filename,
    save_uploaded_file,
    delete_file,
    get_file_info,
    cleanup_old_files
)

# Import utilities from path_utils
from .path_utils import (
    ensure_directory_exists,
    get_absolute_path,
    get_directory_from_path,
    get_filename_from_path,
    get_filename_without_extension,
    is_path_writable,
    is_path_within_directory,
    join_paths,
    get_upload_path,
    get_temp_path,
    ensure_upload_directory,
    ensure_temp_directory,
    normalize_path
)

# Import utilities from time_utils
from .time_utils import (
    Timer,
    ExecutionTimer,
    AsyncExecutionTimer,
    ProgressTracker,
    get_current_timestamp,
    get_iso_timestamp,
    measure_execution_time,
    time_function,
    async_time_function,
    format_elapsed_time
)

# Import utilities from response_formatter
from .response_formatter import ResponseFormatter

# Define exports
__all__ = [
    # File handling utilities
    'FileManager',
    'generate_unique_filename',
    'is_allowed_file',
    'sanitize_filename',
    'save_uploaded_file',
    'delete_file',
    'get_file_info',
    'cleanup_old_files',
    
    # Path manipulation utilities
    'ensure_directory_exists',
    'get_absolute_path',
    'get_directory_from_path',
    'get_filename_from_path',
    'get_filename_without_extension',
    'is_path_writable',
    'is_path_within_directory',
    'join_paths',
    'get_upload_path',
    'get_temp_path',
    'ensure_upload_directory',
    'ensure_temp_directory',
    'normalize_path',
    
    # Timing utilities
    'Timer',
    'ExecutionTimer',
    'AsyncExecutionTimer',
    'ProgressTracker',
    'get_current_timestamp',
    'get_iso_timestamp',
    'measure_execution_time',
    'time_function',
    'async_time_function',
    'format_elapsed_time',
    
    # Response formatting utilities
    'ResponseFormatter'
]