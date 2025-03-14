"""
Provides utility functions for path manipulation and validation in the web interface
of the JSON to Excel Conversion Tool. This module handles path operations with a focus
on security, preventing directory traversal attacks, and ensuring proper file system access.
"""

import os  # v: built-in
import os.path  # v: built-in
from typing import Optional  # v: built-in

from ../../backend/logger import get_logger
from ../config/upload_config import upload_config
from ../../backend/utils import sanitize_file_path

# Initialize logger for this module
logger = get_logger(__name__)

# Constants for file paths
UPLOAD_FOLDER = upload_config['upload_folder']
TEMP_FOLDER = os.path.join(os.path.dirname(UPLOAD_FOLDER), 'temp')


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Creates a directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory to create
        
    Returns:
        True if the directory exists or was created successfully, False otherwise
    """
    # Sanitize the directory path for security
    directory_path = sanitize_file_path(directory_path)
    
    try:
        # Check if directory already exists
        if os.path.isdir(directory_path):
            logger.debug(f"Directory already exists: {directory_path}")
            return True
        
        # Create directory and any necessary parent directories
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def get_absolute_path(path: str) -> str:
    """
    Converts a relative path to an absolute path.
    
    Args:
        path: The path to convert
        
    Returns:
        Absolute path
    """
    # Sanitize the path for security
    path = sanitize_file_path(path)
    
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    logger.debug(f"Converted path to absolute: {path} -> {abs_path}")
    
    return abs_path


def get_directory_from_path(file_path: str) -> str:
    """
    Extracts the directory part from a file path.
    
    Args:
        file_path: Path to extract directory from
        
    Returns:
        Directory path
    """
    # Sanitize the file path for security
    file_path = sanitize_file_path(file_path)
    
    # Extract directory
    directory = os.path.dirname(file_path)
    return directory


def get_filename_from_path(file_path: str) -> str:
    """
    Extracts the filename from a file path.
    
    Args:
        file_path: Path to extract filename from
        
    Returns:
        Filename
    """
    # Sanitize the file path for security
    file_path = sanitize_file_path(file_path)
    
    # Extract filename
    filename = os.path.basename(file_path)
    return filename


def get_filename_without_extension(file_path: str) -> str:
    """
    Extracts the filename without extension from a file path.
    
    Args:
        file_path: Path to extract filename from
        
    Returns:
        Filename without extension
    """
    # Sanitize the file path for security
    file_path = sanitize_file_path(file_path)
    
    # Extract filename and remove extension
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    
    return filename_without_ext


def is_path_writable(path: str) -> bool:
    """
    Checks if a path is writable.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is writable, False otherwise
    """
    # Sanitize the path for security
    path = sanitize_file_path(path)
    
    try:
        # If path exists, check if it's writable
        if os.path.exists(path):
            return os.access(path, os.W_OK)
        
        # If path doesn't exist, check if parent directory is writable
        parent_dir = os.path.dirname(path)
        if parent_dir:
            return os.access(parent_dir, os.W_OK)
        
        # If no parent directory (e.g., file in current directory)
        return os.access(os.getcwd(), os.W_OK)
    except Exception as e:
        logger.error(f"Error checking if path is writable {path}: {str(e)}")
        return False


def is_path_within_directory(path: str, directory: str) -> bool:
    """
    Checks if a path is within a specified directory (prevents directory traversal).
    
    Args:
        path: Path to check
        directory: Directory that should contain the path
        
    Returns:
        True if the path is within the directory, False otherwise
    """
    # Sanitize both paths for security
    path = sanitize_file_path(path)
    directory = sanitize_file_path(directory)
    
    # Convert both to absolute paths
    abs_path = os.path.abspath(path)
    abs_directory = os.path.abspath(directory)
    
    # Path is within directory if it starts with the directory path
    # We add os.sep at the end to ensure it's a proper subdirectory
    # e.g., /tmp/dir is not within /tmp/d
    if not abs_directory.endswith(os.sep):
        abs_directory += os.sep
    
    is_within = abs_path.startswith(abs_directory)
    if not is_within:
        logger.warning(f"Security: Path {abs_path} is not within directory {abs_directory}")
    
    return is_within


def join_paths(base_path: str, relative_path: str) -> str:
    """
    Securely joins paths to prevent directory traversal.
    
    Args:
        base_path: Base path
        relative_path: Relative path to join
        
    Returns:
        Joined path, sanitized and validated
    """
    # Sanitize both paths for security
    base_path = sanitize_file_path(base_path)
    relative_path = sanitize_file_path(relative_path)
    
    # Join paths
    joined_path = os.path.join(base_path, relative_path)
    
    # Ensure the result is within the base path to prevent directory traversal
    if not is_path_within_directory(joined_path, base_path):
        logger.warning(f"Security: Attempted path traversal detected. Returning base path instead.")
        return base_path
    
    return joined_path


def get_upload_path(filename: str) -> str:
    """
    Gets the full path in the upload directory.
    
    Args:
        filename: Name of the file
        
    Returns:
        Full path in the upload directory
    """
    # Sanitize the filename for security
    filename = sanitize_file_path(filename)
    
    # Join paths securely
    full_path = join_paths(UPLOAD_FOLDER, filename)
    
    return full_path


def get_temp_path(filename: str) -> str:
    """
    Gets the full path in the temporary directory.
    
    Args:
        filename: Name of the file
        
    Returns:
        Full path in the temporary directory
    """
    # Sanitize the filename for security
    filename = sanitize_file_path(filename)
    
    # Join paths securely
    full_path = join_paths(TEMP_FOLDER, filename)
    
    return full_path


def ensure_upload_directory() -> bool:
    """
    Ensures the upload directory exists.
    
    Returns:
        True if the directory exists or was created successfully, False otherwise
    """
    return ensure_directory_exists(UPLOAD_FOLDER)


def ensure_temp_directory() -> bool:
    """
    Ensures the temporary directory exists.
    
    Returns:
        True if the directory exists or was created successfully, False otherwise
    """
    return ensure_directory_exists(TEMP_FOLDER)


def normalize_path(path: str) -> str:
    """
    Normalizes a path by resolving symlinks and removing redundant separators.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path
    """
    # Sanitize the path for security
    path = sanitize_file_path(path)
    
    # Normalize path
    normalized_path = os.path.normpath(path)
    
    # Resolve symbolic links
    try:
        real_path = os.path.realpath(normalized_path)
        return real_path
    except Exception as e:
        logger.error(f"Error normalizing path {path}: {str(e)}")
        return normalized_path