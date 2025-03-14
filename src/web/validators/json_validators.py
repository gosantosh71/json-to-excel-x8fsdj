"""
Provides JSON validation functionality for the web interface of the JSON to Excel Conversion Tool.
This module implements validators for JSON files uploaded through the web interface,
ensuring they meet the requirements for conversion to Excel format.
"""

import os  # v: built-in
import json  # v: built-in
import logging  # v: built-in
from typing import Dict, List, Any, Optional, Tuple, Union  # v: built-in

from ...backend.validators.json_validator import JSONValidator
from ...backend.models.error_response import ErrorResponse
from ../models.upload_file import UploadFile, UploadStatus
from ../exceptions.file_exceptions import InvalidJSONFileException, FileCorruptedException
from ../config.web_interface_config import web_config

# Initialize logger
logger = logging.getLogger(__name__)

# Constants from configuration
MAX_NESTING_LEVEL = web_config['json_validation']['max_nesting_level']
MAX_FILE_SIZE_MB = web_config['json_validation']['max_file_size_mb']
MAX_FILE_SIZE_BYTES = web_config['json_validation']['max_file_size_mb'] * 1024 * 1024


def validate_json_structure(json_data: Dict[str, Any]) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates the structure of a JSON file to ensure it can be properly converted to Excel.
    
    Args:
        json_data: The JSON data to validate
        
    Returns:
        Tuple containing validation result and optional error response
    """
    validator = JSONValidator()
    is_valid, error = validator.validate_json_object(json_data)
    return is_valid, error


def get_json_structure_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a JSON object and returns information about its structure and complexity.
    
    Args:
        json_data: The JSON data to analyze
        
    Returns:
        Dictionary containing structure information
    """
    validator = JSONValidator()
    return validator.get_structure_info(json_data)


def get_validation_warnings(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identifies potential issues with JSON data that might affect conversion quality.
    
    Args:
        json_data: The JSON data to analyze
        
    Returns:
        List of warning dictionaries with issue details
    """
    # Create a temporary JSONData object to analyze
    from ...backend.models.json_data import JSONData
    
    temp_json_data = JSONData(
        content=json_data,
        source_path="memory",
        size_bytes=len(json.dumps(json_data).encode('utf-8'))
    )
    temp_json_data.analyze_structure()
    
    validator = JSONValidator()
    return validator.get_validation_warnings(temp_json_data)


def read_json_file(file_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
    """
    Reads and parses a JSON file from the filesystem.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Tuple containing parsed JSON data and optional error
    """
    if not os.path.exists(file_path):
        error = ErrorResponse(
            message=f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            category="INPUT_ERROR",
            severity="ERROR",
            source_component="json_validators"
        )
        return None, error
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            parsed_json = json.loads(content)
            return parsed_json, None
        except json.JSONDecodeError as e:
            error = ErrorResponse(
                message=f"Invalid JSON format: {str(e)}",
                error_code="JSON_PARSE_ERROR",
                category="PARSING_ERROR",
                severity="ERROR",
                source_component="json_validators"
            )
            error.add_context("line", e.lineno)
            error.add_context("column", e.colno)
            error.add_resolution_step("Check JSON syntax at the specified location")
            error.add_resolution_step("Use a JSON validator to identify syntax errors")
            
            logger.error(f"JSON parsing error in file {file_path}: {str(e)}")
            return None, error
        
    except Exception as e:
        error = ErrorResponse(
            message=f"Error reading file: {str(e)}",
            error_code="FILE_READ_ERROR",
            category="INPUT_ERROR",
            severity="ERROR",
            source_component="json_validators"
        )
        logger.error(f"Error reading JSON file {file_path}: {str(e)}")
        return None, error


class WebJSONValidator:
    """
    A class that provides JSON validation functionality for the web interface.
    """
    
    def __init__(self, max_nesting_level: Optional[int] = None, max_file_size_mb: Optional[int] = None):
        """
        Initializes a new WebJSONValidator instance with optional custom parameters.
        
        Args:
            max_nesting_level: Maximum allowed nesting level in JSON
            max_file_size_mb: Maximum allowed file size in MB
        """
        self._max_nesting_level = max_nesting_level or MAX_NESTING_LEVEL
        self._max_file_size_bytes = (max_file_size_mb or MAX_FILE_SIZE_MB) * 1024 * 1024
        self._backend_validator = JSONValidator(max_nesting_level=self._max_nesting_level, 
                                              max_file_size_bytes=self._max_file_size_bytes)
        
        logger.debug(f"WebJSONValidator initialized with max_nesting_level={self._max_nesting_level}, "
                    f"max_file_size_bytes={self._max_file_size_bytes}")
        
    def validate_upload_file(self, upload_file: UploadFile) -> Tuple[bool, Optional[ErrorResponse], Optional[Dict[str, Any]]]:
        """
        Validates an uploaded JSON file for proper format and structure.
        
        Args:
            upload_file: The uploaded file to validate
            
        Returns:
            Tuple containing validation result, optional error, and parsed JSON if successful
        """
        upload_file.status = UploadStatus.VALIDATING
        logger.info(f"Validating JSON file: {upload_file.original_filename} (size: {upload_file.file_size} bytes)")
        
        # Check file size
        is_valid_size, size_error = self._backend_validator.validate_file_size(upload_file.file_size)
        if not is_valid_size:
            upload_file.status = UploadStatus.INVALID
            logger.warning(f"File size validation failed: {upload_file.original_filename} ({upload_file.file_size} bytes)")
            return False, size_error, None
        
        # Read and parse JSON file
        parsed_json, parse_error = read_json_file(upload_file.file_path)
        if parse_error:
            upload_file.status = UploadStatus.INVALID
            logger.warning(f"JSON parsing failed: {upload_file.original_filename}")
            return False, parse_error, None
        
        # Validate JSON structure
        is_valid_structure, structure_error = self._backend_validator.validate_json_object(parsed_json)
        if not is_valid_structure:
            upload_file.status = UploadStatus.INVALID
            logger.warning(f"JSON structure validation failed: {upload_file.original_filename}")
            return False, structure_error, None
        
        # All validation passed
        upload_file.status = UploadStatus.VALID
        logger.info(f"JSON validation successful: {upload_file.original_filename}")
        return True, None, parsed_json
    
    def validate_with_exceptions(self, upload_file: UploadFile) -> Dict[str, Any]:
        """
        Validates an uploaded JSON file and raises exceptions for validation failures.
        
        Args:
            upload_file: The uploaded file to validate
            
        Returns:
            Parsed JSON data if validation succeeds
            
        Raises:
            FileSizeExceededException: If file size exceeds the maximum allowed size
            InvalidJSONFileException: If the JSON format or structure is invalid
            FileCorruptedException: If the file is corrupt or cannot be processed
        """
        is_valid, error, parsed_json = self.validate_upload_file(upload_file)
        
        if not is_valid:
            if error and "exceeds maximum allowed size" in error.message:
                logger.error(f"File size exceeded: {upload_file.original_filename} ({upload_file.file_size} bytes)")
                from ../exceptions.file_exceptions import FileSizeExceededException
                raise FileSizeExceededException(
                    filename=upload_file.original_filename,
                    file_size=upload_file.file_size,
                    max_size=self._max_file_size_bytes
                )
            elif error and ("JSON syntax" in error.message or "structure validation" in error.message):
                logger.error(f"Invalid JSON format in file: {upload_file.original_filename}")
                raise InvalidJSONFileException(
                    filename=upload_file.original_filename,
                    error_details=error.message
                )
            elif error and "structure" in error.message:
                logger.error(f"Invalid JSON structure in file: {upload_file.original_filename}")
                raise InvalidJSONFileException(
                    filename=upload_file.original_filename,
                    error_details=error.message
                )
            else:
                logger.error(f"File validation failed with unknown error: {upload_file.original_filename}")
                raise FileCorruptedException(
                    filename=upload_file.original_filename,
                    error_details=error.message if error else "Unknown validation error"
                )
        
        return parsed_json
    
    def analyze_json_file(self, upload_file: UploadFile) -> Dict[str, Any]:
        """
        Analyzes a JSON file and returns information about its structure and complexity.
        
        Args:
            upload_file: The uploaded file to analyze
            
        Returns:
            Dictionary containing structure analysis and warnings
            
        Raises:
            InvalidJSONFileException: If the JSON cannot be parsed or analyzed
        """
        # Read and parse JSON file
        parsed_json, parse_error = read_json_file(upload_file.file_path)
        if parse_error:
            logger.error(f"Cannot analyze JSON file due to parsing error: {upload_file.original_filename}")
            raise InvalidJSONFileException(
                filename=upload_file.original_filename,
                error_details=parse_error.message
            )
        
        # Get structure information
        structure_info = self._backend_validator.get_structure_info(parsed_json)
        
        # Get warnings about potential issues
        from ...backend.models.json_data import JSONData
        temp_json_data = JSONData(
            content=parsed_json,
            source_path=upload_file.file_path,
            size_bytes=upload_file.file_size
        )
        temp_json_data.analyze_structure()
        warnings = self._backend_validator.get_validation_warnings(temp_json_data)
        
        # Combine results
        result = {
            "structure": structure_info,
            "warnings": warnings,
            "file_info": {
                "name": upload_file.original_filename,
                "size": upload_file.file_size,
                "path": upload_file.file_path
            }
        }
        
        logger.info(f"JSON analysis completed for {upload_file.original_filename}")
        return result
    
    def get_conversion_recommendations(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides recommendations for conversion options based on JSON structure.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            Dictionary containing recommended conversion options
        """
        structure_info = self._backend_validator.get_structure_info(json_data)
        
        # Determine recommended array handling based on structure
        array_handling = "expand"
        if structure_info["contains_arrays"]:
            # For large arrays or deeply nested arrays, joining might be better
            if any("large_arrays" in str(structure_info)) or structure_info["max_nesting_level"] > 3:
                array_handling = "join"
        
        # Determine recommended sheet name based on structure
        sheet_name = "Sheet1"
        
        # If there's a clear top-level object name, use it
        if isinstance(json_data, dict) and len(json_data) == 1:
            key = next(iter(json_data))
            if isinstance(key, str) and key.isalnum():
                sheet_name = key.capitalize()
        
        recommendations = {
            "array_handling": array_handling,
            "sheet_name": sheet_name,
            "structure_complexity": structure_info["complexity_level"],
            "max_nesting_level": structure_info["max_nesting_level"],
            "contains_arrays": structure_info["contains_arrays"]
        }
        
        logger.debug(f"Generated conversion recommendations: {recommendations}")
        return recommendations