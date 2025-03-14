"""
JSON Schema validation utilities for the JSON to Excel Conversion Tool.

This package provides tools and utilities for validating JSON structures,
detecting JSON complexity, and handling nested JSON objects. It serves as
the central point for all schema-related functionality in the application.

Key components:
- Schema validation: Validate JSON against predefined or custom schemas
- Structure analysis: Detect and analyze JSON structure types
- Nesting validation: Check and calculate JSON nesting depth
- Schema generation: Create schemas dynamically from JSON data
- Schema registry: Manage and retrieve schema definitions

These utilities support the core JSON Structure Validation feature and
help prepare data for the Nested JSON Flattening process.
"""

from .json_schema import (
    create_schema_for_json,
    validate_against_schema,
    get_schema_for_structure_type,
    detect_structure_type,
    check_nesting_depth,
    calculate_nesting_depth,
    generate_dynamic_schema,
    SchemaRegistry,
    BASE_SCHEMA,
    FLAT_JSON_SCHEMA,
    NESTED_JSON_SCHEMA,
    ARRAY_JSON_SCHEMA,
    MAX_NESTING_LEVEL
)

__all__ = [
    "create_schema_for_json",
    "validate_against_schema",
    "get_schema_for_structure_type",
    "detect_structure_type",
    "check_nesting_depth",
    "calculate_nesting_depth",
    "generate_dynamic_schema",
    "SchemaRegistry",
    "BASE_SCHEMA",
    "FLAT_JSON_SCHEMA", 
    "NESTED_JSON_SCHEMA",
    "ARRAY_JSON_SCHEMA",
    "MAX_NESTING_LEVEL"
]