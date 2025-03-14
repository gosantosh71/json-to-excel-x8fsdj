"""
Provides utility functions used throughout the JSON to Excel Conversion Tool backend.

This module contains reusable helper functions for file operations, performance monitoring,
data transformation, and other common tasks that support the core functionality of the application.
"""

import os  # v: built-in
import time  # v: built-in
import functools  # v: built-in
import typing  # v: built-in
from pathlib import Path  # v: built-in

from .constants import FILE_CONSTANTS
from .logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)


def timing_decorator(func: typing.Callable) -> typing.Callable:
    """
    A decorator that measures and logs the execution time of a function.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function that logs execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.6f} seconds")
        return result
    return wrapper


class Timer:
    """
    A context manager for measuring the execution time of a code block.
    """
    
    def __init__(self, name: typing.Optional[str] = None):
        """
        Initializes a new Timer instance with an optional name.
        
        Args:
            name: Optional name for the timer for identification in logs
        """
        self._name = name or "Timer"
        self._start_time = None
        self._logger = get_logger(__name__)
    
    def __enter__(self) -> 'Timer':
        """
        Enters the context and starts the timer.
        
        Returns:
            Self reference
        """
        self._start_time = time.time()
        return self
    
    def __exit__(self, exc_type: typing.Optional[typing.Type[Exception]], 
                 exc_val: typing.Optional[Exception], 
                 exc_tb: typing.Optional[typing.Any]) -> bool:
        """
        Exits the context, stops the timer, and logs the elapsed time.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
            
        Returns:
            False to propagate exceptions
        """
        elapsed_time = self.get_elapsed_time()
        self._logger.info(f"{self._name} completed in {elapsed_time:.6f} seconds")
        return False  # Propagate exceptions
    
    def get_elapsed_time(self) -> float:
        """
        Gets the elapsed time since the timer started.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start_time is None:
            raise ValueError("Timer has not been started")
        return time.time() - self._start_time


class PerformanceTracker:
    """
    A utility class for tracking and reporting performance metrics.
    """
    
    def __init__(self):
        """
        Initializes a new PerformanceTracker instance.
        """
        self._timings: typing.Dict[str, typing.List[float]] = {}
        self._logger = get_logger(__name__)
    
    def record_timing(self, operation_name: str, execution_time: float) -> None:
        """
        Records a timing measurement for a specific operation.
        
        Args:
            operation_name: Name of the operation being timed
            execution_time: Time taken for the operation in seconds
        """
        if operation_name not in self._timings:
            self._timings[operation_name] = []
        
        self._timings[operation_name].append(execution_time)
        self._logger.debug(f"Recorded timing for {operation_name}: {execution_time:.6f}s")
    
    def get_average_timing(self, operation_name: str) -> typing.Optional[float]:
        """
        Gets the average execution time for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Average execution time or None if no timings exist
        """
        if operation_name not in self._timings or not self._timings[operation_name]:
            return None
        
        timings = self._timings[operation_name]
        return sum(timings) / len(timings)
    
    def get_all_metrics(self) -> typing.Dict[str, typing.Dict[str, float]]:
        """
        Gets performance metrics for all tracked operations.
        
        Returns:
            Dictionary of operation metrics including min, max, avg, and count
        """
        metrics = {}
        
        for operation, timings in self._timings.items():
            if not timings:
                continue
                
            metrics[operation] = {
                "min": min(timings),
                "max": max(timings),
                "avg": sum(timings) / len(timings),
                "count": len(timings)
            }
        
        return metrics
    
    def reset(self) -> None:
        """
        Resets all timing measurements.
        """
        self._timings.clear()
        self._logger.debug("Performance tracker reset")


def validate_file_path(file_path: str) -> bool:
    """
    Validates a file path for existence and security concerns.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the path is valid, False otherwise
    """
    if not file_path:
        logger.error("File path is empty or None")
        return False
    
    # Normalize the path to handle different formats
    normalized_path = os.path.normpath(file_path)
    
    # Check for directory traversal
    if ".." in normalized_path.split(os.sep):
        logger.error(f"Directory traversal attempt detected in path: {file_path}")
        return False
    
    # Check if the file exists for input files
    if os.path.exists(file_path):
        if not os.access(file_path, os.R_OK):
            logger.error(f"File exists but is not readable: {file_path}")
            return False
    else:
        # If the file doesn't exist, check if its parent directory exists and is writable
        # This is useful for output files
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            logger.error(f"Parent directory does not exist: {parent_dir}")
            return False
        elif parent_dir and not os.access(parent_dir, os.W_OK):
            logger.error(f"Parent directory is not writable: {parent_dir}")
            return False
    
    return True


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitizes a file path to prevent directory traversal and other security issues.
    
    Args:
        file_path: Path to sanitize
        
    Returns:
        Sanitized file path
    """
    # Convert to absolute path
    abs_path = os.path.abspath(file_path)
    
    # Normalize the path
    normalized_path = os.path.normpath(abs_path)
    
    # Remove potentially dangerous characters
    base_dir = os.path.dirname(normalized_path)
    file_name = os.path.basename(normalized_path)
    file_name = ''.join(c for c in file_name if c.isalnum() or c in '._- ')
    
    sanitized_path = os.path.join(base_dir, file_name)
    
    return sanitized_path


def get_file_extension(file_path: str) -> str:
    """
    Gets the extension of a file from its path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase, without the dot)
    """
    _, extension = os.path.splitext(file_path)
    return extension.lower().lstrip('.')


def is_valid_extension(file_path: str, allowed_extensions: typing.List[str] = None) -> bool:
    """
    Checks if a file has an allowed extension.
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed extensions, defaults to FILE_CONSTANTS.ALLOWED_EXTENSIONS
        
    Returns:
        True if the extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = FILE_CONSTANTS["ALLOWED_EXTENSIONS"]
    
    extension = get_file_extension(file_path)
    return extension in allowed_extensions


def get_file_size(file_path: str) -> int:
    """
    Gets the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """
    Formats a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable file size (e.g., '1.2 MB')
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensures that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    if os.path.exists(directory_path):
        return os.path.isdir(directory_path)
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def flatten_dict(nested_dict: typing.Dict[str, typing.Any], parent_key: str = '', 
                separator: str = '.') -> typing.Dict[str, typing.Any]:
    """
    Flattens a nested dictionary into a single-level dictionary with compound keys.
    
    Args:
        nested_dict: The nested dictionary to flatten
        parent_key: The base key for nested keys
        separator: Character used to join key components
        
    Returns:
        Flattened dictionary with compound keys
    """
    flattened = {}
    
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            flattened.update(flatten_dict(value, new_key, separator))
        else:
            flattened[new_key] = value
    
    return flattened


def is_json_array(obj: typing.Any) -> bool:
    """
    Checks if a Python object is a list/array.
    
    Args:
        obj: The object to check
        
    Returns:
        True if the object is a list, False otherwise
    """
    return isinstance(obj, list)


def is_json_object(obj: typing.Any) -> bool:
    """
    Checks if a Python object is a dictionary/object.
    
    Args:
        obj: The object to check
        
    Returns:
        True if the object is a dictionary, False otherwise
    """
    return isinstance(obj, dict)


def is_primitive_type(obj: typing.Any) -> bool:
    """
    Checks if a Python object is a primitive type (str, int, float, bool, None).
    
    Args:
        obj: The object to check
        
    Returns:
        True if the object is a primitive type, False otherwise
    """
    return obj is None or isinstance(obj, (str, int, float, bool))


def safe_get(dictionary: typing.Dict[str, typing.Any], key: str, 
            default: typing.Any = None) -> typing.Any:
    """
    Safely gets a value from a dictionary with a default if the key doesn't exist.
    
    Args:
        dictionary: Dictionary to get the value from
        key: Key to look up
        default: Default value to return if key doesn't exist
        
    Returns:
        Value from the dictionary or the default
    """
    return dictionary.get(key, default)