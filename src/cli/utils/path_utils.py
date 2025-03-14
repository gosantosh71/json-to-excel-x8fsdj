"""
Provides utility functions for file path operations in the CLI component of the JSON to Excel Conversion Tool.
This module handles path validation, normalization, and manipulation to ensure secure and consistent file operations
across different platforms.
"""

import os  # v: built-in
import os.path  # v: built-in
import pathlib  # v: built-in
import typing  # v: built-in
import re  # v: built-in

from ...backend.logger import get_logger
from .console_utils import print_error
from ...backend.constants import FILE_CONSTANTS

# Initialize logger
logger = get_logger(__name__)

# Pattern for detecting unsafe characters in filenames
UNSAFE_PATH_PATTERN = re.compile(r'[\\/:*?"<>|]')


def normalize_cli_path(path: str) -> str:
    """
    Normalizes a file path provided via command line to ensure consistent format across platforms.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized absolute path
    """
    if path is None or path == "":
        return None
    
    # Expand user directory if path contains ~ (home directory)
    if '~' in path:
        path = os.path.expanduser(path)
    
    # Convert to absolute path if it's a relative path
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # Normalize path to resolve any '..' or '.' components
    path = os.path.normpath(path)
    
    # Replace backslashes with forward slashes for consistency
    path = path.replace('\\', '/')
    
    logger.debug(f"Normalized path: {path}")
    return path


def validate_input_file(file_path: str, verbose: bool = False) -> bool:
    """
    Validates that an input file exists, is readable, and has the correct extension.
    
    Args:
        file_path: Path to the input file
        verbose: Whether to print error messages
        
    Returns:
        True if the file is valid, False otherwise
    """
    # Normalize the path
    file_path = normalize_cli_path(file_path)
    if not file_path:
        if verbose:
            print_error("File path cannot be empty")
        logger.error("Empty input file path provided")
        return False
    
    # Check if the file exists
    if not os.path.exists(file_path):
        if verbose:
            print_error(f"File not found: {file_path}")
        logger.error(f"Input file not found: {file_path}")
        return False
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        if verbose:
            print_error(f"Not a file: {file_path}")
        logger.error(f"Input path is not a file: {file_path}")
        return False
    
    # Check if the file is readable
    if not os.access(file_path, os.R_OK):
        if verbose:
            print_error(f"Permission denied: Cannot read file {file_path}")
        logger.error(f"Permission denied for input file: {file_path}")
        return False
    
    # Check if the file has a valid extension
    if not is_valid_json_file(file_path):
        if verbose:
            print_error(f"Invalid file type: {file_path}. Expected JSON file.")
        logger.error(f"Invalid file type for input: {file_path}")
        return False
    
    # All validations passed
    logger.debug(f"Input file validated successfully: {file_path}")
    return True


def validate_output_file(file_path: str, verbose: bool = False) -> bool:
    """
    Validates that an output file path is writable and has the correct extension.
    
    Args:
        file_path: Path to the output file
        verbose: Whether to print error messages
        
    Returns:
        True if the file path is valid, False otherwise
    """
    # Normalize the path
    file_path = normalize_cli_path(file_path)
    if not file_path:
        if verbose:
            print_error("Output file path cannot be empty")
        logger.error("Empty output file path provided")
        return False
    
    # Get the directory part of the path
    directory = get_directory_from_path(file_path)
    
    # Check if the directory exists, try to create it if not
    if not os.path.exists(directory):
        created = ensure_directory_exists(directory)
        if not created:
            if verbose:
                print_error(f"Cannot create directory: {directory}")
            logger.error(f"Failed to create output directory: {directory}")
            return False
    
    # Check if the directory is writable
    if not is_path_writable(directory):
        if verbose:
            print_error(f"Permission denied: Cannot write to directory {directory}")
        logger.error(f"Permission denied for output directory: {directory}")
        return False
    
    # Check if the file has a valid extension
    if not is_valid_excel_file(file_path):
        if verbose:
            print_error(f"Invalid file type: {file_path}. Expected Excel file (.xlsx, .xls).")
        logger.error(f"Invalid file type for output: {file_path}")
        return False
    
    # Check if the file already exists and is writable
    if os.path.exists(file_path):
        if not is_path_writable(file_path):
            if verbose:
                print_error(f"Permission denied: Cannot write to file {file_path}")
            logger.error(f"Permission denied for output file: {file_path}")
            return False
        else:
            if verbose:
                print_error(f"Warning: File {file_path} already exists and will be overwritten.")
            logger.warning(f"Output file already exists and will be overwritten: {file_path}")
    
    # All validations passed
    logger.debug(f"Output file path validated successfully: {file_path}")
    return True


def get_file_extension(file_path: str) -> str:
    """
    Gets the extension of a file from its path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase, without the dot)
    """
    if not file_path:
        return ""
    
    _, extension = os.path.splitext(file_path)
    extension = extension.lower().lstrip(".")
    
    return extension


def is_valid_json_file(file_path: str) -> bool:
    """
    Checks if a file has a .json extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file has a .json extension, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in FILE_CONSTANTS["ALLOWED_EXTENSIONS"]


def is_valid_excel_file(file_path: str) -> bool:
    """
    Checks if a file has a valid Excel extension (.xlsx, .xls).
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file has a valid Excel extension, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in ["xlsx", "xls"]


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensures that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    if not directory_path:
        return False
    
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        return True
    
    try:
        # Create the directory and any necessary parent directories
        os.makedirs(directory_path, exist_ok=True)
        logger.debug(f"Created directory: {directory_path}")
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def is_path_writable(path: str) -> bool:
    """
    Checks if a path is writable.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is writable, False otherwise
    """
    if not path:
        return False
    
    try:
        # Check if the path exists
        if os.path.exists(path):
            # If it's a file, check if it's writable
            if os.path.isfile(path):
                return os.access(path, os.W_OK)
            # If it's a directory, check if it's writable
            elif os.path.isdir(path):
                return os.access(path, os.W_OK)
        # If the path doesn't exist, check if the parent directory is writable
        else:
            parent_dir = get_directory_from_path(path)
            return os.access(parent_dir, os.W_OK) if parent_dir else False
    except Exception as e:
        logger.error(f"Error checking if path is writable {path}: {str(e)}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Gets the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    if not file_path or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return 0
    
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        logger.error(f"Error getting file size for {file_path}: {str(e)}")
        return 0


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to remove invalid characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return ""
    
    # Replace unsafe characters
    sanitized = UNSAFE_PATH_PATTERN.sub('_', filename)
    
    # Remove leading and trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def get_directory_from_path(file_path: str) -> str:
    """
    Extracts the directory part from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Directory path
    """
    if not file_path:
        return ""
    
    return os.path.dirname(file_path)


def get_filename_from_path(file_path: str) -> str:
    """
    Extracts the filename part from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Filename
    """
    if not file_path:
        return ""
    
    return os.path.basename(file_path)


def join_paths(base_path: str, relative_path: str) -> str:
    """
    Joins path components in a platform-independent way.
    
    Args:
        base_path: Base path
        relative_path: Relative path to join
        
    Returns:
        Joined path
    """
    if not base_path or not relative_path:
        return base_path or relative_path or ""
    
    joined_path = os.path.join(base_path, relative_path)
    return os.path.normpath(joined_path)


def is_safe_path(base_path: str, path: str) -> bool:
    """
    Checks if a path is safe (no directory traversal).
    
    Args:
        base_path: Base directory path
        path: Path to check
        
    Returns:
        True if the path is safe, False otherwise
    """
    if not base_path or not path:
        return False
    
    # Normalize both paths for comparison
    base_path = os.path.normpath(os.path.abspath(base_path))
    full_path = os.path.normpath(os.path.abspath(os.path.join(base_path, path)))
    
    # Check if the normalized path starts with the normalized base path
    is_safe = full_path.startswith(base_path)
    
    if not is_safe:
        logger.warning(f"Unsafe path detected: {path} (base: {base_path})")
    
    return is_safe