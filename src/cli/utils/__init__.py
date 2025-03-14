"""
Initializes the utils package for the CLI component of the JSON to Excel Conversion Tool.
This module exposes utility functions and classes from the path_utils, console_utils, and time_utils
modules to provide a unified interface for file operations, console output, and timing functionality.
"""

# Import path utility functions
from .path_utils import (
    normalize_cli_path,
    validate_input_file,
    validate_output_file,
    get_file_extension,
    is_valid_json_file,
    is_valid_excel_file,
    ensure_directory_exists,
    is_path_writable,
    get_file_size,
    sanitize_filename,
    get_directory_from_path,
    get_filename_from_path,
    join_paths,
    is_safe_path
)

# Import console utility functions and classes
from .console_utils import (
    is_color_supported,
    colorize,
    get_terminal_size,
    clear_line,
    print_message,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_processing,
    print_cli_response,
    update_progress_bar,
    prompt_user,
    prompt_yes_no,
    format_file_size,
    format_time,
    ProgressSpinner
)

# Import time utility functions and classes
from .time_utils import (
    time_function,
    get_current_time,
    calculate_elapsed_time,
    format_elapsed_time,
    timing_context,
    ExecutionTimer,
    OperationTimingTracker
)

# Define the exports
__all__ = [
    # path_utils exports
    "normalize_cli_path",
    "validate_input_file",
    "validate_output_file",
    "get_file_extension",
    "is_valid_json_file",
    "is_valid_excel_file",
    "ensure_directory_exists",
    "is_path_writable",
    "get_file_size",
    "sanitize_filename",
    "get_directory_from_path",
    "get_filename_from_path",
    "join_paths",
    "is_safe_path",
    
    # console_utils exports
    "is_color_supported",
    "colorize",
    "get_terminal_size",
    "clear_line",
    "print_message",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_processing",
    "print_cli_response",
    "update_progress_bar",
    "prompt_user",
    "prompt_yes_no",
    "format_file_size",
    "format_time",
    "ProgressSpinner",
    
    # time_utils exports
    "time_function",
    "get_current_time",
    "calculate_elapsed_time",
    "format_elapsed_time",
    "timing_context",
    "ExecutionTimer",
    "OperationTimingTracker"
]