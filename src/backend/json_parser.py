"""
Core component responsible for parsing, validating, and analyzing JSON data in the 
JSON to Excel Conversion Tool. This module handles JSON syntax validation, structure analysis,
and provides detailed information about JSON complexity to guide the transformation process.
"""

import json  # v: built-in
from typing import Dict, List, Any, Optional, Tuple, Union  # v: built-in

from .models.json_data import JSONData, JSONComplexity
from .models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from .exceptions import JSONParseError, JSONStructureError
from .constants import JSON_CONSTANTS
from .logger import get_logger
from .utils import timing_decorator, is_json_object, is_json_array, is_primitive_type

# Initialize logger for this module
logger = get_logger(__name__)

# Constants
MAX_NESTING_LEVEL = JSON_CONSTANTS['MAX_NESTING_LEVEL']


@timing_decorator
def parse_json_string(json_string: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
    """
    Parses a JSON string into a Python object.
    
    Args:
        json_string: The JSON string to parse
        
    Returns:
        Tuple containing parsed JSON (if successful) and error response (if failed)
    """
    try:
        parsed_json = json.loads(json_string)
        logger.debug(f"Successfully parsed JSON string")
        return parsed_json, None
    except json.JSONDecodeError as e:
        error = ErrorResponse(
            message=f"Invalid JSON syntax: {str(e)}",
            error_code=JSON_CONSTANTS["INVALID_FILE_TYPE"],
            category=ErrorCategory.PARSING_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONParser",
            context={"line": e.lineno, "column": e.colno, "position": e.pos}
        )
        error.add_resolution_step("Check the JSON syntax for errors")
        error.add_resolution_step("Validate the JSON using an online JSON validator")
        error.add_resolution_step("Fix any missing quotes, commas, or brackets")
        
        logger.error(f"JSON parse error: {str(e)} at line {e.lineno}, column {e.colno}")
        return None, error


def validate_json_structure(json_data: Dict[str, Any]) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates the structure of a JSON object.
    
    Args:
        json_data: The JSON data to validate
        
    Returns:
        Tuple containing validation result and error response (if failed)
    """
    if not isinstance(json_data, dict):
        error = ErrorResponse(
            message="Invalid JSON structure: Root element must be an object",
            error_code=JSON_CONSTANTS["JSON_STRUCTURE_ERROR"],
            category=ErrorCategory.PARSING_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="JSONParser",
            context={"actual_type": type(json_data).__name__}
        )
        error.add_resolution_step("Ensure your JSON data starts with an object (enclosed in '{}')")
        error.add_resolution_step("If your data starts with an array, consider wrapping it in an object")
        
        logger.error(f"JSON structure error: Root element is {type(json_data).__name__}, not an object")
        return False, error
    
    return True, None


@timing_decorator
def analyze_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the structure of a JSON object to determine its complexity and characteristics.
    
    Args:
        json_data: The JSON data to analyze
        
    Returns:
        Dictionary containing structure analysis results
    """
    temp_json_data = JSONData(json_data, "memory", 0)
    temp_json_data.analyze_structure()
    
    analysis_result = {
        "max_nesting_level": temp_json_data.max_nesting_level,
        "is_nested": temp_json_data.is_nested,
        "contains_arrays": temp_json_data.contains_arrays,
        "array_paths": temp_json_data.array_paths,
        "array_count": len(temp_json_data.array_paths),
        "complexity_score": temp_json_data.complexity_score,
        "complexity_level": temp_json_data.complexity_level.name,
        "flattening_strategy": temp_json_data.get_flattening_strategy()
    }
    
    logger.debug(f"JSON structure analysis: nesting={analysis_result['max_nesting_level']}, "
                 f"arrays={analysis_result['array_count']}, "
                 f"complexity={analysis_result['complexity_level']}")
    
    return analysis_result


def detect_nesting_level(obj: Any, current_level: int = 0) -> int:
    """
    Recursively detects the maximum nesting level in a JSON structure.
    
    Args:
        obj: The object to analyze
        current_level: The current nesting level (for recursion)
        
    Returns:
        Maximum nesting level detected
    """
    if isinstance(obj, dict):
        if not obj:  # Empty dict
            return current_level
        return max((detect_nesting_level(v, current_level + 1) for v in obj.values()), default=current_level)
    elif isinstance(obj, list):
        if not obj:  # Empty list
            return current_level
        return max((detect_nesting_level(item, current_level + 1) for item in obj), default=current_level)
    else:
        # Primitive value
        return current_level


def detect_arrays(obj: Any, path: str = "", array_paths: List[str] = None) -> List[str]:
    """
    Recursively detects arrays in a JSON structure and records their paths.
    
    Args:
        obj: The object to analyze
        path: The current path (for recursion)
        array_paths: List to collect paths where arrays were found
        
    Returns:
        List of paths where arrays were found
    """
    if array_paths is None:
        array_paths = []
        
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            detect_arrays(value, new_path, array_paths)
    elif isinstance(obj, list):
        # Add this path to array_paths
        if path:  # Skip the root level if it's an array
            array_paths.append(path)
        
        # Continue checking each item in the array
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            detect_arrays(item, new_path, array_paths)
            
    return array_paths


def create_json_data(json_data: Dict[str, Any], source_path: str, size_bytes: int) -> JSONData:
    """
    Creates a JSONData object from parsed JSON data.
    
    Args:
        json_data: The parsed JSON data
        source_path: Path to the source JSON file
        size_bytes: Size of the JSON file in bytes
        
    Returns:
        A JSONData object representing the JSON data
    """
    json_data_obj = JSONData(json_data, source_path, size_bytes)
    json_data_obj.analyze_structure()
    logger.debug(f"Created JSONData object from {source_path} ({size_bytes} bytes)")
    return json_data_obj


class JSONParser:
    """
    A class that provides JSON parsing, validation, and analysis functionality.
    """
    
    def __init__(self, max_nesting_level: Optional[int] = None):
        """
        Initializes a new JSONParser instance with optional custom parameters.
        
        Args:
            max_nesting_level: Maximum supported nesting level (default from constants)
        """
        self._max_nesting_level = max_nesting_level or MAX_NESTING_LEVEL
        logger.debug(f"Initialized JSONParser with max_nesting_level={self._max_nesting_level}")
    
    def parse_string(self, json_string: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
        """
        Parses a JSON string into a Python object.
        
        Args:
            json_string: The JSON string to parse
            
        Returns:
            Tuple containing parsed JSON and optional error
        """
        return parse_json_string(json_string)
    
    def validate(self, json_data: Dict[str, Any]) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates a JSON object for proper structure.
        
        Args:
            json_data: The JSON data to validate
            
        Returns:
            Tuple containing validation result and optional error
        """
        return validate_json_structure(json_data)
    
    def get_structure_info(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets detailed information about the structure of a JSON object.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            Dictionary containing structure information
        """
        return analyze_json_structure(json_data)
    
    def create_json_data(self, json_data: Dict[str, Any], source_path: str, size_bytes: int) -> JSONData:
        """
        Creates a JSONData object from parsed JSON data.
        
        Args:
            json_data: The parsed JSON data
            source_path: Path to the source JSON file
            size_bytes: Size of the JSON file in bytes
            
        Returns:
            A JSONData object representing the JSON data
        """
        return create_json_data(json_data, source_path, size_bytes)
    
    def check_nesting_depth(self, json_data: Dict[str, Any]) -> Tuple[bool, int]:
        """
        Checks if the nesting depth of a JSON structure exceeds the maximum allowed level.
        
        Args:
            json_data: The JSON data to check
            
        Returns:
            Tuple containing check result and actual nesting depth
        """
        depth = detect_nesting_level(json_data)
        within_limits = depth <= self._max_nesting_level
        
        if not within_limits:
            logger.warning(f"JSON nesting depth ({depth}) exceeds maximum allowed level ({self._max_nesting_level})")
        
        return within_limits, depth
    
    def find_arrays(self, json_data: Dict[str, Any]) -> List[str]:
        """
        Finds arrays in a JSON structure and their paths.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            List of paths where arrays were found
        """
        array_paths = detect_arrays(json_data)
        logger.debug(f"Found {len(array_paths)} arrays in JSON structure")
        return array_paths
    
    def get_recommended_strategy(self, json_data: Dict[str, Any]) -> str:
        """
        Determines the recommended transformation strategy based on JSON structure.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            Recommended strategy ('flat', 'nested', or 'array')
        """
        temp_json_data = JSONData(json_data, "memory", 0)
        strategy = temp_json_data.get_flattening_strategy()
        logger.debug(f"Recommended transformation strategy: {strategy}")
        return strategy