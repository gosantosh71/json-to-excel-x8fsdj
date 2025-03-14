"""
Provides comprehensive JSON validation functionality for the JSON to Excel Conversion Tool.

This module validates JSON syntax, structure, complexity, and size to ensure that
input JSON files can be properly processed and converted to Excel format. It includes
methods for detecting nested structures, arrays, and potential conversion issues.
"""

import json  # v: built-in
import os  # v: built-in
from typing import Dict, List, Any, Optional, Tuple  # v: built-in
import jsonschema  # v: 4.17.0

from ..models.json_data import JSONData, JSONComplexity
from ..models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..exceptions import (
    JSONParsingException,
    JSONValidationException,
    JSONStructureException
)
from ..schemas.json_schema import (
    SchemaRegistry, 
    validate_against_schema,
    detect_structure_type,
    check_nesting_depth
)
from ..constants import JSON_CONSTANTS, FILE_CONSTANTS
from ..logger import get_logger

# Configure logger
logger = get_logger(__name__)

# Import constants
MAX_NESTING_LEVEL = JSON_CONSTANTS['MAX_NESTING_LEVEL']
MAX_FILE_SIZE_BYTES = FILE_CONSTANTS['MAX_FILE_SIZE_BYTES']
MAX_FILE_SIZE_MB = FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'] / (1024 * 1024)


def validate_json_syntax(json_string: str) -> Tuple[bool, Optional[ErrorResponse], Optional[Dict[str, Any]]]:
    """
    Validates that a string contains valid JSON syntax.
    
    Args:
        json_string: The string to validate as JSON
        
    Returns:
        Tuple containing validation result, optional error response, and parsed JSON if successful
    """
    try:
        parsed_json = json.loads(json_string)
        return True, None, parsed_json
    except json.JSONDecodeError as e:
        # Create detailed error response
        error_response = ErrorResponse(
            message=f"Invalid JSON syntax: {e.msg}",
            error_code="E005",
            category=ErrorCategory.PARSING_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        
        # Add context and resolution steps
        error_response.add_context("line_number", e.lineno)
        error_response.add_context("column", e.colno)
        error_response.add_context("position", e.pos)
        error_response.add_resolution_step("Check JSON syntax at the indicated position")
        error_response.add_resolution_step("Validate your JSON using an online JSON validator")
        error_response.add_resolution_step("Ensure all quotes, brackets, and commas are properly used")
        
        logger.error(f"JSON syntax validation failed: {e.msg} at line {e.lineno}, column {e.colno}")
        return False, error_response, None
    except Exception as e:
        # Handle unexpected errors
        error_response = ErrorResponse(
            message=f"Unexpected error parsing JSON: {str(e)}",
            error_code="E999",
            category=ErrorCategory.PARSING_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        error_response.add_resolution_step("Check the JSON content for any unusual formatting")
        error_response.add_resolution_step("Ensure the file encoding is UTF-8")
        
        logger.error(f"Unexpected JSON parsing error: {str(e)}")
        return False, error_response, None


def validate_json_structure(json_data: Dict[str, Any], structure_type: Optional[str] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates the structure of a JSON object against predefined schemas.
    
    Args:
        json_data: The parsed JSON data to validate
        structure_type: Optional structure type to validate against ('flat', 'nested', 'array')
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Detect structure type if not provided
    if structure_type is None:
        structure_type = detect_structure_type(json_data)
        logger.debug(f"Detected JSON structure type: {structure_type}")
    
    # Get schema registry and appropriate schema
    schema_registry = SchemaRegistry()
    schema = schema_registry.get_schema(structure_type)
    
    if not schema:
        error_response = ErrorResponse(
            message=f"No schema available for structure type: {structure_type}",
            error_code="E006",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        return False, error_response
    
    # Validate against schema
    is_valid, error_message = validate_against_schema(json_data, schema)
    
    if not is_valid:
        error_response = ErrorResponse(
            message=f"JSON structure validation failed: {error_message}",
            error_code="E006",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        error_response.add_context("structure_type", structure_type)
        error_response.add_resolution_step("Review the JSON structure for compliance with expected format")
        error_response.add_resolution_step("Check for inconsistencies in object properties or array items")
        
        logger.error(f"JSON structure validation failed for {structure_type} structure: {error_message}")
        return False, error_response
    
    return True, None


def validate_json_complexity(json_data: Dict[str, Any], max_nesting_level: Optional[int] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that JSON complexity is within acceptable limits.
    
    Args:
        json_data: The parsed JSON data to validate
        max_nesting_level: Optional maximum nesting level, defaults to constant
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Use default from constants if not provided
    if max_nesting_level is None:
        max_nesting_level = MAX_NESTING_LEVEL
    
    # Check nesting depth
    is_acceptable, actual_depth = check_nesting_depth(json_data, max_nesting_level)
    
    if not is_acceptable:
        error_response = ErrorResponse(
            message=f"JSON nesting depth ({actual_depth}) exceeds maximum allowed level ({max_nesting_level})",
            error_code="E006",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        error_response.add_context("actual_depth", actual_depth)
        error_response.add_context("max_depth", max_nesting_level)
        error_response.add_resolution_step("Simplify the JSON structure to reduce nesting depth")
        error_response.add_resolution_step("Consider pre-processing the JSON to flatten deeply nested structures")
        
        logger.error(f"JSON complexity validation failed: nesting depth {actual_depth} exceeds maximum {max_nesting_level}")
        return False, error_response
    
    return True, None


def validate_json_size(file_size_bytes: int, max_size_bytes: Optional[int] = None) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that JSON file size is within acceptable limits.
    
    Args:
        file_size_bytes: Size of the file in bytes
        max_size_bytes: Optional maximum size in bytes, defaults to constant
        
    Returns:
        Tuple containing validation result and optional error response
    """
    # Use default from constants if not provided
    if max_size_bytes is None:
        max_size_bytes = MAX_FILE_SIZE_BYTES
    
    # Check file size
    if file_size_bytes > max_size_bytes:
        file_size_mb = file_size_bytes / (1024 * 1024)
        max_size_mb = max_size_bytes / (1024 * 1024)
        
        error_response = ErrorResponse(
            message=f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)",
            error_code="E003",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONValidator"
        )
        error_response.add_context("file_size_bytes", file_size_bytes)
        error_response.add_context("max_size_bytes", max_size_bytes)
        error_response.add_resolution_step("Split the file into smaller JSON files")
        error_response.add_resolution_step("Remove unnecessary data to reduce file size")
        error_response.add_resolution_step("Contact system administrator to increase file size limit if necessary")
        
        logger.error(f"File size validation failed: {file_size_mb:.2f} MB exceeds maximum {max_size_mb:.2f} MB")
        return False, error_response
    
    return True, None


def validate_json_data(json_data: JSONData) -> Tuple[bool, List[ErrorResponse]]:
    """
    Performs comprehensive validation on a JSONData object.
    
    Args:
        json_data: The JSONData object to validate
        
    Returns:
        Tuple containing overall validation result and list of error responses
    """
    # Ensure the data has been analyzed
    if not json_data.is_analyzed:
        json_data.analyze_structure()
    
    # Collect error responses
    error_responses = []
    
    # Validate file size
    size_valid, size_error = validate_json_size(json_data.size_bytes)
    if not size_valid and size_error:
        error_responses.append(size_error)
    
    # Validate complexity
    complexity_valid, complexity_error = validate_json_complexity(json_data.content)
    if not complexity_valid and complexity_error:
        error_responses.append(complexity_error)
    
    # Validate structure - determine structure type from analysis
    structure_type = 'flat'
    if json_data.is_nested and json_data.contains_arrays:
        structure_type = 'nested'
    elif json_data.contains_arrays:
        structure_type = 'array'
    
    structure_valid, structure_error = validate_json_structure(json_data.content, structure_type)
    if not structure_valid and structure_error:
        error_responses.append(structure_error)
    
    # Overall validation result
    is_valid = len(error_responses) == 0
    
    if not is_valid:
        logger.warning(f"JSON data validation failed with {len(error_responses)} issues")
    else:
        logger.debug("JSON data validation passed all checks")
    
    return is_valid, error_responses


def get_validation_warnings(json_data: JSONData) -> List[Dict[str, Any]]:
    """
    Identifies potential issues with JSON data that might affect conversion.
    
    Args:
        json_data: The JSONData object to analyze
        
    Returns:
        List of warning dictionaries with issue details
    """
    # Ensure the data has been analyzed
    if not json_data.is_analyzed:
        json_data.analyze_structure()
    
    warnings = []
    
    # Check for deep nesting that approaches the limit
    if json_data.max_nesting_level > (MAX_NESTING_LEVEL * 0.8):
        warnings.append({
            "warning_type": "deep_nesting",
            "message": f"Deep nesting detected ({json_data.max_nesting_level} levels) approaching the limit of {MAX_NESTING_LEVEL}",
            "severity": "medium",
            "context": {"max_nesting_level": json_data.max_nesting_level, "limit": MAX_NESTING_LEVEL},
            "suggestion": "Consider simplifying the JSON structure to reduce nesting depth"
        })
    
    # Check for large arrays that might cause performance issues
    large_arrays = []
    for path in json_data.array_paths:
        array_value = json_data.get_value_at_path(path)
        if isinstance(array_value, list) and len(array_value) > 1000:
            large_arrays.append({"path": path, "length": len(array_value)})
    
    if large_arrays:
        warnings.append({
            "warning_type": "large_arrays",
            "message": f"Large arrays detected which might impact performance ({len(large_arrays)} arrays with >1000 items)",
            "severity": "medium",
            "context": {"arrays": large_arrays},
            "suggestion": "Consider limiting array sizes or processing the data in chunks"
        })
    
    # Check for potential Excel row/column limit issues
    # This is a simplified estimation - real implementation would be more precise
    potential_row_count = 1
    for path in json_data.array_paths:
        array_value = json_data.get_value_at_path(path)
        if isinstance(array_value, list):
            potential_row_count *= max(1, len(array_value))
    
    if potential_row_count > 1000000:  # Close to Excel's ~1.05M row limit
        warnings.append({
            "warning_type": "excel_row_limit",
            "message": f"Potential row count ({potential_row_count}) may exceed Excel's limit of 1,048,576 rows",
            "severity": "high",
            "context": {"estimated_rows": potential_row_count},
            "suggestion": "Consider filtering data or splitting into multiple sheets"
        })
    
    # Check for mixed data types in arrays
    mixed_type_arrays = []
    for path in json_data.array_paths:
        array_value = json_data.get_value_at_path(path)
        if isinstance(array_value, list) and len(array_value) > 1:
            types = set()
            for item in array_value:
                types.add(type(item).__name__)
            if len(types) > 1:
                mixed_type_arrays.append({"path": path, "types": list(types)})
    
    if mixed_type_arrays:
        warnings.append({
            "warning_type": "mixed_types",
            "message": f"Mixed data types detected in arrays ({len(mixed_type_arrays)} arrays), which may affect Excel formatting",
            "severity": "low",
            "context": {"arrays": mixed_type_arrays},
            "suggestion": "Consider normalizing data types for consistent formatting"
        })
    
    return warnings


def identify_problematic_paths(json_data: JSONData) -> Dict[str, List[str]]:
    """
    Identifies specific paths in the JSON structure that might cause issues.
    
    Args:
        json_data: The JSONData object to analyze
        
    Returns:
        Dictionary mapping issue types to lists of problematic JSON paths
    """
    # Ensure the data has been analyzed
    if not json_data.is_analyzed:
        json_data.analyze_structure()
    
    problematic_paths = {
        "deep_nesting": [],
        "large_arrays": [],
        "mixed_types": [],
        "long_strings": []
    }
    
    # Helper function to check all paths recursively
    def check_path(obj, current_path="", depth=0):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                # Check nesting depth
                if depth >= MAX_NESTING_LEVEL * 0.8:
                    problematic_paths["deep_nesting"].append(new_path)
                
                # Check string length
                if isinstance(value, str) and len(value) > 32767:  # Excel's cell content limit
                    problematic_paths["long_strings"].append(new_path)
                
                # Recurse into nested structures
                check_path(value, new_path, depth + 1)
                
        elif isinstance(obj, list):
            # Check array size
            if len(obj) > 1000:
                problematic_paths["large_arrays"].append(current_path)
            
            # Check for mixed types
            if len(obj) > 1:
                types = set(type(item).__name__ for item in obj)
                if len(types) > 1:
                    problematic_paths["mixed_types"].append(current_path)
            
            # Recurse into array items
            for i, item in enumerate(obj):
                new_path = f"{current_path}[{i}]"
                check_path(item, new_path, depth + 1)
    
    # Start the recursive check
    check_path(json_data.content)
    
    # Remove empty categories
    return {k: v for k, v in problematic_paths.items() if v}


class JSONValidator:
    """
    A class that provides comprehensive JSON validation functionality.
    """
    
    def __init__(
        self, 
        max_nesting_level: Optional[int] = None,
        max_file_size_bytes: Optional[int] = None,
        complexity_threshold: Optional[int] = None
    ):
        """
        Initializes a new JSONValidator instance with optional custom validation parameters.
        
        Args:
            max_nesting_level: Maximum allowed nesting depth
            max_file_size_bytes: Maximum allowed file size in bytes
            complexity_threshold: Threshold for complexity score
        """
        self._schema_registry = SchemaRegistry()
        self._max_nesting_level = max_nesting_level or MAX_NESTING_LEVEL
        self._max_file_size_bytes = max_file_size_bytes or MAX_FILE_SIZE_BYTES
        self._complexity_threshold = complexity_threshold or JSON_CONSTANTS['COMPLEXITY_THRESHOLD']
        
        logger.debug(f"JSONValidator initialized with: max_nesting_level={self._max_nesting_level}, "
                     f"max_file_size_bytes={self._max_file_size_bytes}, "
                     f"complexity_threshold={self._complexity_threshold}")
    
    def validate_json_string(self, json_string: str) -> Tuple[bool, Optional[ErrorResponse], Optional[Dict[str, Any]]]:
        """
        Validates that a string contains valid JSON syntax and parses it.
        
        Args:
            json_string: The string to validate as JSON
            
        Returns:
            Validation result, optional error, and parsed JSON if successful
        """
        return validate_json_syntax(json_string)
    
    def validate_json_object(self, json_data: Dict[str, Any], structure_type: Optional[str] = None) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates a JSON object against structure and complexity rules.
        
        Args:
            json_data: The parsed JSON data to validate
            structure_type: Optional structure type to validate against
            
        Returns:
            Validation result and optional error
        """
        # Validate structure first
        is_valid, error = validate_json_structure(json_data, structure_type)
        if not is_valid:
            return False, error
        
        # Then validate complexity
        is_valid, error = validate_json_complexity(json_data, self._max_nesting_level)
        if not is_valid:
            return False, error
        
        return True, None
    
    def validate_file_size(self, file_size_bytes: int) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates that a file size is within the configured limits.
        
        Args:
            file_size_bytes: Size of the file in bytes
            
        Returns:
            Validation result and optional error
        """
        return validate_json_size(file_size_bytes, self._max_file_size_bytes)
    
    def validate_json_data_object(self, json_data: JSONData) -> Tuple[bool, List[ErrorResponse]]:
        """
        Performs comprehensive validation on a JSONData object.
        
        Args:
            json_data: The JSONData object to validate
            
        Returns:
            Overall validation result and list of errors
        """
        return validate_json_data(json_data)
    
    def get_structure_info(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets detailed information about the structure of a JSON object.
        
        Args:
            json_data: The parsed JSON data to analyze
            
        Returns:
            Dictionary containing structure information
        """
        # Create a temporary JSONData object for analysis
        temp_json_data = JSONData(
            content=json_data,
            source_path="memory",
            size_bytes=len(json.dumps(json_data).encode('utf-8'))
        )
        temp_json_data.analyze_structure()
        
        # Extract and return structure information
        return {
            "is_nested": temp_json_data.is_nested,
            "max_nesting_level": temp_json_data.max_nesting_level,
            "contains_arrays": temp_json_data.contains_arrays,
            "array_paths": temp_json_data.array_paths,
            "complexity_score": temp_json_data.complexity_score,
            "complexity_level": temp_json_data.complexity_level.name,
            "flattening_strategy": temp_json_data.get_flattening_strategy()
        }
    
    def get_validation_warnings(self, json_data: JSONData) -> List[Dict[str, Any]]:
        """
        Gets warnings about potential issues with the JSON data.
        
        Args:
            json_data: The JSONData object to analyze
            
        Returns:
            List of warning dictionaries
        """
        return get_validation_warnings(json_data)
    
    def identify_problematic_paths(self, json_data: JSONData) -> Dict[str, List[str]]:
        """
        Identifies specific paths in the JSON structure that might cause issues.
        
        Args:
            json_data: The JSONData object to analyze
            
        Returns:
            Dictionary mapping issue types to problematic paths
        """
        return identify_problematic_paths(json_data)