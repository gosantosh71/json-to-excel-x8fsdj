"""
Provides JSON schema definitions and utilities for validating and analyzing
JSON structures in the JSON to Excel Conversion Tool.

This module defines schema templates for different JSON structure types
(flat, nested, array-based) and offers functions to validate JSON data
against these schemas, detect structure types, and check nesting depth.
"""

import json  # v: built-in
import jsonschema  # v: 4.17.0
import logging  # v: built-in
from typing import Dict, List, Any, Optional, Union, Tuple  # v: built-in

from ..models.json_data import JSONData
from ..constants import JSON_CONSTANTS

# Set up module logger
logger = logging.getLogger(__name__)

# Import maximum nesting level from constants
MAX_NESTING_LEVEL = JSON_CONSTANTS['MAX_NESTING_LEVEL']

# Basic JSON schema template
BASE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True
}

# Schema for flat JSON (no nested objects or arrays)
FLAT_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": {
        "not": {
            "type": ["object", "array"]
        }
    }
}

# Schema for nested JSON (allows nested objects)
NESTED_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True
}

# Schema for array-based JSON
ARRAY_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "items": {
            "type": "array"
        }
    }
}


def create_schema_for_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a JSON schema based on the structure of provided JSON data.
    
    Args:
        json_data: The JSON data for which to create a schema
        
    Returns:
        A JSON schema that describes the structure of the input data
    """
    def _get_type(value: Any) -> Dict[str, Any]:
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
            if not value:  # Empty array
                return {"type": "array", "items": {}}
            
            # Check if all items have the same type
            item_types = set()
            for item in value:
                if isinstance(item, dict):
                    item_types.add("object")
                elif isinstance(item, list):
                    item_types.add("array")
                elif isinstance(item, bool):
                    item_types.add("boolean")
                elif isinstance(item, int):
                    item_types.add("integer")
                elif isinstance(item, float):
                    item_types.add("number")
                elif isinstance(item, str):
                    item_types.add("string")
                elif item is None:
                    item_types.add("null")
                    
            if len(item_types) == 1:
                # All items are the same type
                item_type = item_types.pop()
                if item_type == "object" and isinstance(value[0], dict):
                    # For arrays of objects, create a schema for the first object
                    return {
                        "type": "array",
                        "items": _create_object_schema(value[0])
                    }
                else:
                    return {
                        "type": "array",
                        "items": {"type": item_type}
                    }
            else:
                # Mixed types
                return {
                    "type": "array",
                    "items": {}
                }
        elif isinstance(value, dict):
            return _create_object_schema(value)
        else:
            # Fallback for unknown types
            return {"type": "string"}
    
    def _create_object_schema(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a schema for a JSON object."""
        properties = {}
        for key, value in obj.items():
            properties[key] = _get_type(value)
            
        return {
            "type": "object",
            "properties": properties
        }
    
    # Start creating the schema based on the root object
    schema = _create_object_schema(json_data)
    
    # Add standard schema identifier
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    
    return schema


def validate_against_schema(json_data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates JSON data against a specified schema.
    
    Args:
        json_data: The JSON data to validate
        schema: The JSON schema to validate against
        
    Returns:
        A tuple containing validation result (True/False) and error message if validation fails
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        # Extract meaningful information from the validation error
        error_path = ".".join(str(path) for path in e.path) if e.path else "root"
        error_message = f"Validation failed at {error_path}: {e.message}"
        logger.debug(f"JSON schema validation error: {error_message}")
        return False, error_message
    except Exception as e:
        # Handle other validation exceptions
        error_message = f"Schema validation error: {str(e)}"
        logger.error(error_message)
        return False, error_message


def get_schema_for_structure_type(structure_type: str) -> Dict[str, Any]:
    """
    Returns the appropriate schema based on the JSON structure type.
    
    Args:
        structure_type: The type of JSON structure ('flat', 'nested', or 'array')
        
    Returns:
        The schema corresponding to the specified structure type
    """
    if structure_type == 'flat':
        return FLAT_JSON_SCHEMA
    elif structure_type == 'nested':
        return NESTED_JSON_SCHEMA
    elif structure_type == 'array':
        return ARRAY_JSON_SCHEMA
    else:
        # Default to base schema if structure_type is not recognized
        logger.warning(f"Unknown structure type: {structure_type}, using base schema")
        return BASE_SCHEMA


def detect_structure_type(json_data: Dict[str, Any]) -> str:
    """
    Detects the structure type of JSON data (flat, nested, or array-based).
    
    Args:
        json_data: The JSON data to analyze
        
    Returns:
        The detected structure type ('flat', 'nested', or 'array')
    """
    if not isinstance(json_data, dict):
        logger.warning("Input is not a dictionary, cannot determine structure type")
        return 'unknown'
    
    has_nested_objects = False
    has_arrays = False
    
    # Check for nested objects and arrays
    for value in json_data.values():
        if isinstance(value, dict):
            has_nested_objects = True
        elif isinstance(value, list):
            has_arrays = True
            # Check if any array contains objects or other arrays
            for item in value:
                if isinstance(item, (dict, list)):
                    has_nested_objects = True
                    break
    
    # Determine structure type based on findings
    if has_nested_objects:
        return 'nested'
    elif has_arrays:
        return 'array'
    else:
        return 'flat'


def check_nesting_depth(json_data: Dict[str, Any], max_depth: Optional[int] = None) -> Tuple[bool, int]:
    """
    Checks if the JSON nesting depth exceeds the maximum allowed level.
    
    Args:
        json_data: The JSON data to check
        max_depth: Maximum allowed nesting depth, defaults to MAX_NESTING_LEVEL
        
    Returns:
        A tuple containing a boolean indicating if depth is acceptable and the actual depth
    """
    if max_depth is None:
        max_depth = MAX_NESTING_LEVEL
    
    actual_depth = calculate_nesting_depth(json_data, 0)
    is_acceptable = actual_depth <= max_depth
    
    if not is_acceptable:
        logger.warning(
            f"JSON nesting depth ({actual_depth}) exceeds maximum allowed level ({max_depth})"
        )
    
    return is_acceptable, actual_depth


def calculate_nesting_depth(obj: Any, current_depth: int) -> int:
    """
    Recursively calculates the maximum nesting depth of a JSON structure.
    
    Args:
        obj: The object to analyze
        current_depth: The current nesting depth (for recursion)
        
    Returns:
        The maximum nesting depth of the JSON structure
    """
    if obj is None:
        return current_depth
        
    if isinstance(obj, dict):
        if not obj:  # Empty dictionary
            return current_depth + 1
        # Find maximum depth among all values
        return max(
            calculate_nesting_depth(value, current_depth + 1)
            for value in obj.values()
        )
    elif isinstance(obj, list):
        if not obj:  # Empty list
            return current_depth + 1
        # Find maximum depth among all items
        return max(
            calculate_nesting_depth(item, current_depth + 1)
            for item in obj
        )
    else:
        # Base case: primitive value
        return current_depth


def generate_dynamic_schema(json_data: JSONData) -> Dict[str, Any]:
    """
    Generates a dynamic JSON schema based on the provided JSONData instance.
    
    Args:
        json_data: The JSONData instance containing information about the JSON structure
        
    Returns:
        A JSON schema tailored to the specific structure of the input data
    """
    # Ensure the data has been analyzed
    if not json_data.is_analyzed:
        json_data.analyze_structure()
    
    # Get base schema from the JSONData instance
    schema = json_data.get_schema()
    
    # Enhance schema with additional constraints based on structure_info
    if json_data.structure_info:
        # Add metadata about the schema
        schema["title"] = "Generated Schema for JSON data"
        schema["description"] = f"Auto-generated schema for {json_data.source_path}"
        
        # Add validation for arrays if applicable
        if json_data.contains_arrays:
            # This is a simplified approach; in a real implementation,
            # we would add more specific array validation rules
            schema["containsArrays"] = True
            schema["arrayPaths"] = json_data.array_paths
        
        # Add validation for nesting depth
        if json_data.is_nested:
            schema["maxNestingLevel"] = json_data.max_nesting_level
    
    return schema


class SchemaRegistry:
    """
    A registry for managing and retrieving JSON schemas used for validation.
    """
    
    def __init__(self):
        """
        Initializes a new SchemaRegistry with predefined schemas.
        """
        self._schemas = {
            'base': BASE_SCHEMA,
            'flat': FLAT_JSON_SCHEMA,
            'nested': NESTED_JSON_SCHEMA,
            'array': ARRAY_JSON_SCHEMA
        }
    
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a schema by name from the registry.
        
        Args:
            schema_name: The name of the schema to retrieve
            
        Returns:
            The requested schema or None if not found
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]
        else:
            logger.warning(f"Schema '{schema_name}' not found in registry")
            return None
    
    def register_schema(self, schema_name: str, schema: Dict[str, Any]) -> bool:
        """
        Adds a new schema to the registry or updates an existing one.
        
        Args:
            schema_name: The name to associate with the schema
            schema: The JSON schema to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Validate that the schema is a valid JSON schema
        try:
            # Check if it has the basic requirements of a JSON schema
            if not isinstance(schema, dict) or "$schema" not in schema:
                logger.warning(f"Invalid schema format for '{schema_name}'")
                return False
                
            # Add or update the schema in the registry
            self._schemas[schema_name] = schema
            logger.info(f"Schema '{schema_name}' registered successfully")
            return True
        except Exception as e:
            logger.error(f"Error registering schema '{schema_name}': {str(e)}")
            return False
    
    def validate(self, json_data: Dict[str, Any], schema_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validates JSON data against a named schema in the registry.
        
        Args:
            json_data: The JSON data to validate
            schema_name: The name of the schema to validate against
            
        Returns:
            Validation result and error message if validation fails
        """
        schema = self.get_schema(schema_name)
        if not schema:
            return False, f"Schema '{schema_name}' not found in registry"
        
        return validate_against_schema(json_data, schema)