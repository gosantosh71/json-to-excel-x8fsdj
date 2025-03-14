"""
Models for handling and analyzing JSON data structures.

This module provides data classes and utilities for representing, analyzing,
and processing JSON data within the JSON to Excel Conversion Tool.
"""

from dataclasses import dataclass  # v: built-in
import json  # v: built-in
from enum import Enum  # v: built-in
from typing import Dict, List, Any, Optional, Tuple, Union  # v: built-in

from ..constants import JSON_CONSTANTS


class JSONComplexity(Enum):
    """
    An enumeration of complexity levels for JSON structures, used to categorize 
    JSON data based on its structural complexity.
    """
    SIMPLE = 1       # Flat structure, no nesting, no arrays
    MODERATE = 2     # Some nesting (1-3 levels) or simple arrays
    COMPLEX = 3      # Deeper nesting (4-7 levels) or nested arrays
    VERY_COMPLEX = 4 # Extreme nesting (8+ levels) or complex array structures


def calculate_nesting_depth(obj: Any) -> int:
    """
    Recursively calculates the maximum nesting depth of a JSON structure.
    
    Args:
        obj: The JSON object to analyze
        
    Returns:
        int: The maximum nesting depth of the JSON structure
    """
    if isinstance(obj, dict):
        if not obj:  # Empty dict
            return 1
        return 1 + max(calculate_nesting_depth(v) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:  # Empty list
            return 1
        return 1 + max(calculate_nesting_depth(item) for item in obj)
    else:
        # Base case: primitive value
        return 0


def detect_arrays(obj: Any, path: str = "", array_paths: List[str] = None) -> List[str]:
    """
    Recursively detects arrays in a JSON structure and records their paths.
    
    Args:
        obj: The JSON object to analyze
        path: The current path in the JSON structure (for recursion)
        array_paths: List to collect paths where arrays were found
        
    Returns:
        List[str]: List of paths where arrays were found
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


def is_nested_structure(obj: Any) -> bool:
    """
    Determines if a JSON structure contains nested objects.
    
    Args:
        obj: The JSON object to analyze
        
    Returns:
        bool: True if the structure contains nested objects, False otherwise
    """
    if isinstance(obj, dict):
        # Check if any value is a dict or list
        for value in obj.values():
            if isinstance(value, (dict, list)):
                return True
        return False
    elif isinstance(obj, list):
        # Check if any item is a dict or list
        for item in obj:
            if isinstance(item, (dict, list)):
                return True
        return False
    else:
        # Primitive value
        return False


@dataclass
class JSONData:
    """
    A data class that represents JSON data with metadata and provides methods
    for analyzing its structure and complexity.
    """
    content: Dict[str, Any]
    source_path: str
    size_bytes: int
    
    # Analysis properties (initialized in __post_init__ or analyze_structure)
    is_nested: bool = False
    max_nesting_level: int = 0
    contains_arrays: bool = False
    array_paths: List[str] = None
    complexity_score: int = 0
    complexity_level: JSONComplexity = JSONComplexity.SIMPLE
    structure_info: Dict[str, Any] = None
    is_analyzed: bool = False
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.array_paths is None:
            self.array_paths = []
        if self.structure_info is None:
            self.structure_info = {}
    
    def analyze_structure(self) -> None:
        """
        Analyzes the JSON structure to determine its complexity, nesting level,
        and array presence.
        
        Updates the object's properties in-place.
        """
        # Calculate maximum nesting depth
        self.max_nesting_level = calculate_nesting_depth(self.content)
        
        # Determine if the structure is nested
        self.is_nested = is_nested_structure(self.content)
        
        # Detect arrays
        self.array_paths = detect_arrays(self.content)
        self.contains_arrays = len(self.array_paths) > 0
        
        # Calculate complexity score based on various factors
        # Nesting depth contributes significantly to complexity
        nesting_factor = min(self.max_nesting_level, JSON_CONSTANTS["MAX_NESTING_LEVEL"])
        nesting_score = (nesting_factor / JSON_CONSTANTS["MAX_NESTING_LEVEL"]) * 10
        
        # Arrays add complexity
        array_score = len(self.array_paths) * 0.5
        
        # File size can indicate complexity
        size_score = min(self.size_bytes / (1024 * 1024), 5)  # Cap at 5MB
        
        # Compute total complexity score
        self.complexity_score = int(nesting_score + array_score + size_score)
        
        # Determine complexity level
        if self.complexity_score < 3:
            self.complexity_level = JSONComplexity.SIMPLE
        elif self.complexity_score < 6:
            self.complexity_level = JSONComplexity.MODERATE
        elif self.complexity_score < 10:
            self.complexity_level = JSONComplexity.COMPLEX
        else:
            self.complexity_level = JSONComplexity.VERY_COMPLEX
        
        # Populate structure_info with analysis results
        self.structure_info = {
            "max_nesting_level": self.max_nesting_level,
            "is_nested": self.is_nested,
            "contains_arrays": self.contains_arrays,
            "array_count": len(self.array_paths),
            "array_paths": self.array_paths,
            "complexity_score": self.complexity_score,
            "complexity_level": self.complexity_level.name,
        }
        
        self.is_analyzed = True
    
    def get_value_at_path(self, path: str, separator: str = ".") -> Any:
        """
        Retrieves a value from the JSON structure at the specified path.
        
        Args:
            path: Dot-separated path to the value
            separator: The character used to separate path segments
            
        Returns:
            The value at the specified path or None if not found
        """
        if not path:
            return self.content
            
        parts = path.split(separator)
        current = self.content
        
        for part in parts:
            # Handle array indexing in path
            if part.endswith(']') and '[' in part:
                # Extract array name and index
                array_name, idx_str = part.split('[')
                idx = int(idx_str.rstrip(']'))
                
                # Navigate to the array
                if array_name:
                    if array_name not in current:
                        return None
                    current = current[array_name]
                
                # Access the array element
                if isinstance(current, list) and 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                # Regular object property
                if not isinstance(current, dict) or part not in current:
                    return None
                current = current[part]
                
        return current
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the JSONData object to a dictionary representation.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the JSONData object
        """
        if not self.is_analyzed:
            self.analyze_structure()
            
        return {
            "content": self.content,
            "source_path": self.source_path,
            "size_bytes": self.size_bytes,
            "is_nested": self.is_nested,
            "max_nesting_level": self.max_nesting_level,
            "contains_arrays": self.contains_arrays,
            "array_paths": self.array_paths,
            "complexity_score": self.complexity_score,
            "complexity_level": int(self.complexity_level.value),
            "structure_info": self.structure_info,
            "is_analyzed": self.is_analyzed
        }
    
    def to_json(self, include_content: bool = True, indent: int = 2) -> str:
        """
        Converts the JSONData object to a JSON string.
        
        Args:
            include_content: Whether to include the actual JSON content
            indent: Number of spaces for indentation
            
        Returns:
            str: A JSON string representation of the JSONData object
        """
        data_dict = self.to_dict()
        if not include_content:
            data_dict.pop("content", None)
            
        return json.dumps(data_dict, indent=indent)
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Generates a simple JSON schema based on the structure of the data.
        
        Returns:
            Dict[str, Any]: A JSON schema representation of the data structure
        """
        def _get_type(value):
            """Helper function to determine the JSON schema type of a value."""
            if value is None:
                return {"type": "null"}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, list):
                if not value:
                    return {"type": "array", "items": {}}
                    
                # Get the type of the first item as a sample
                sample_type = _get_type(value[0])
                
                # Check if all items have the same type
                if all(_get_type(item) == sample_type for item in value):
                    return {"type": "array", "items": sample_type}
                else:
                    return {"type": "array", "items": {}}
            elif isinstance(value, dict):
                properties = {k: _get_type(v) for k, v in value.items()}
                return {
                    "type": "object",
                    "properties": properties
                }
            else:
                return {"type": "unknown"}
        
        # Generate schema for the entire JSON structure
        return _get_type(self.content)
    
    def get_complexity_score(self) -> int:
        """
        Calculates a numerical score representing the complexity of the JSON structure.
        
        Returns:
            int: A complexity score based on nesting, arrays, and size
        """
        if not self.is_analyzed:
            self.analyze_structure()
            
        return self.complexity_score
    
    def get_flattening_strategy(self) -> str:
        """
        Determines the appropriate flattening strategy based on the JSON structure.
        
        Returns:
            str: The recommended flattening strategy ('flat', 'nested', or 'array')
        """
        if not self.is_analyzed:
            self.analyze_structure()
            
        if not self.is_nested and not self.contains_arrays:
            return 'flat'
        elif self.is_nested and not self.contains_arrays:
            return 'nested'
        elif self.contains_arrays:
            return 'array'
        else:
            return 'nested'  # Default strategy