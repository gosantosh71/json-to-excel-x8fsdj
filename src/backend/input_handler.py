"""
Handles the reading and validation of JSON input files for the JSON to Excel Conversion Tool.

This module is responsible for file access, validation, and initial processing of JSON files,
serving as the entry point for data in the conversion pipeline.
"""

import os  # v: built-in
import json  # v: built-in
from typing import Dict, Any, Optional, Tuple, List  # v: built-in

from .logger import get_logger
from .adapters.file_system_adapter import FileSystemAdapter
from .validators.file_validator import FileValidator
from .models.json_data import JSONData
from .constants import FILE_CONSTANTS
from .config import get_config_value
from .exceptions import (
    FileNotFoundError,
    InvalidFileTypeError,
    FileTooLargeError,
    JSONParseError
)
from .utils import Timer, sanitize_file_path

# Initialize logger for this module
logger = get_logger(__name__)

# Get maximum file size from configuration
MAX_FILE_SIZE = get_config_value('system.max_file_size', FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'])

def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Reads and validates a JSON file from the filesystem.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        InvalidFileTypeError: If the file is not a JSON file
        FileTooLargeError: If the file exceeds size limits
        JSONParseError: If the file contains invalid JSON
    """
    # Sanitize the file path to prevent security issues
    file_path = sanitize_file_path(file_path)
    
    logger.info(f"Reading JSON file: {file_path}")
    
    # Validate the file
    validator = FileValidator()
    valid, errors = validator.validate_json_file(file_path)
    
    if not valid:
        if errors:
            error = errors[0]  # Get the first error
            error_message = error.get_user_message()
            error_code = error.error_code
            
            # Map to appropriate exception types
            if error_code == 'E001':
                raise FileNotFoundError(file_path=file_path)
            elif error_code == 'E002':
                raise InvalidFileTypeError(
                    file_path=file_path,
                    expected_type="json",
                    actual_type=file_path.split('.')[-1] if '.' in file_path else "unknown"
                )
            elif error_code == 'E003':
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                raise FileTooLargeError(
                    file_path=file_path,
                    file_size=file_size,
                    max_size=MAX_FILE_SIZE
                )
        
        # Generic error if not caught above
        raise Exception(f"Failed to validate JSON file: {file_path}")
    
    # Read the file and parse JSON
    file_adapter = FileSystemAdapter()
    
    try:
        with Timer("JSON file read operation"):
            # Use file system adapter to read the file
            json_data = file_adapter.read_json_file(file_path)
        
        logger.debug(f"Successfully read JSON file: {file_path}")
        return json_data
        
    except Exception as e:
        logger.error(f"Error reading JSON file: {str(e)}")
        if isinstance(e, json.JSONDecodeError):
            raise JSONParseError(
                message=f"Invalid JSON format in file: {file_path}",
                line_number=e.lineno,
                column=e.colno,
                error_details=e.msg
            )
        # Re-raise other exceptions
        raise

def get_json_data(file_path: str) -> JSONData:
    """
    Reads a JSON file and returns a JSONData object with structure analysis.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        JSONData object containing the parsed data and structure analysis
        
    Raises:
        Same exceptions as read_json_file()
    """
    # Sanitize the file path
    file_path = sanitize_file_path(file_path)
    
    # Get file details
    validator = FileValidator()
    file_details = validator.get_file_details(file_path)
    file_size = file_details['size']
    
    # Read the JSON content
    json_content = read_json_file(file_path)
    
    # Create a JSONData object
    json_data = JSONData(
        content=json_content,
        source_path=file_path,
        size_bytes=file_size
    )
    
    # Analyze the JSON structure
    json_data.analyze_structure()
    
    # Log information about the JSON structure
    complexity = json_data.complexity_level.name
    nesting_level = json_data.max_nesting_level
    contains_arrays = json_data.contains_arrays
    logger.info(
        f"JSON structure analysis completed: complexity={complexity}, "
        f"nesting_level={nesting_level}, contains_arrays={contains_arrays}"
    )
    
    return json_data

def validate_json_file(file_path: str) -> bool:
    """
    Validates a JSON file without reading its content.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        True if the file is a valid JSON file, False otherwise
    """
    # Sanitize the file path
    file_path = sanitize_file_path(file_path)
    
    validator = FileValidator()
    valid, _ = validator.validate_json_file(file_path)
    
    logger.debug(f"JSON file validation result for {file_path}: {'valid' if valid else 'invalid'}")
    return valid

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Gets detailed information about a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing file information
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Sanitize the file path
    file_path = sanitize_file_path(file_path)
    
    file_adapter = FileSystemAdapter()
    file_info = file_adapter.get_file_info(file_path)
    
    return file_info

class InputHandler:
    """
    Handles the reading and validation of input JSON files.
    """
    
    def __init__(
        self,
        file_adapter: Optional[FileSystemAdapter] = None,
        file_validator: Optional[FileValidator] = None,
        max_file_size: Optional[int] = None
    ):
        """
        Initializes a new InputHandler instance.
        
        Args:
            file_adapter: Custom FileSystemAdapter instance (optional)
            file_validator: Custom FileValidator instance (optional)
            max_file_size: Custom maximum file size (optional)
        """
        self._file_adapter = file_adapter or FileSystemAdapter()
        self._file_validator = file_validator or FileValidator()
        self._max_file_size = max_file_size or MAX_FILE_SIZE
        
        logger.debug(
            f"InputHandler initialized with max_file_size={self._max_file_size} bytes"
        )
    
    def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Reads and validates a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data as a dictionary
            
        Raises:
            Same exceptions as module-level read_json_file()
        """
        return read_json_file(file_path)
    
    def get_json_data(self, file_path: str) -> JSONData:
        """
        Reads a JSON file and returns a JSONData object with structure analysis.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            JSONData object containing the parsed data and structure analysis
            
        Raises:
            Same exceptions as module-level get_json_data()
        """
        return get_json_data(file_path)
    
    def validate_json_file(self, file_path: str) -> bool:
        """
        Validates a JSON file without reading its content.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if the file is a valid JSON file, False otherwise
        """
        return validate_json_file(file_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Gets detailed information about a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing file information
        """
        return get_file_info(file_path)
    
    def process_json_file(self, file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Processes a JSON file and returns both the parsed data and structure analysis.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Tuple containing parsed JSON data and structure analysis
            
        Raises:
            Same exceptions as get_json_data()
        """
        json_data = self.get_json_data(file_path)
        return json_data.content, json_data.structure_info