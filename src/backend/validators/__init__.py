"""
Validators module for the JSON to Excel Conversion Tool.

This module initializes the validators package and exports key validation classes and functions 
for JSON and file validation. It serves as the entry point for all validation functionality 
in the JSON to Excel Conversion Tool.
"""

# Import JSON validation components
from .json_validator import (
    JSONValidator,  # For validating JSON data structure, syntax, and complexity
    validate_json_syntax,  # For validating JSON syntax and parsing JSON strings
    validate_json_structure,  # For validating JSON structure against schemas
    validate_json_complexity,  # For validating JSON complexity and nesting depth
    validate_json_size,  # For validating JSON file size
    validate_json_data,  # For performing comprehensive validation on JSONData objects
    get_validation_warnings,  # For identifying potential issues with JSON data
    identify_problematic_paths  # For identifying problematic paths in JSON structures
)

# Import file validation components
from .file_validator import (
    FileValidator,  # For validating file existence, permissions, size, and type
    validate_file_exists,  # For validating file existence
    validate_file_readable,  # For validating file readability
    validate_file_size,  # For validating file size
    validate_file_extension,  # For validating file extension
    validate_output_path,  # For validating output file path
    get_file_details,  # For getting detailed file information
    MAX_FILE_SIZE_MB,  # Constant defining maximum allowed file size in MB
    ALLOWED_EXTENSIONS  # Constant defining list of allowed file extensions
)

# Export all validation components
__all__ = [
    # JSON validation
    'JSONValidator',
    'validate_json_syntax',
    'validate_json_structure',
    'validate_json_complexity',
    'validate_json_size',
    'validate_json_data',
    'get_validation_warnings',
    'identify_problematic_paths',
    
    # File validation
    'FileValidator',
    'validate_file_exists',
    'validate_file_readable',
    'validate_file_size',
    'validate_file_extension',
    'validate_output_path',
    'get_file_details',
    'MAX_FILE_SIZE_MB',
    'ALLOWED_EXTENSIONS'
]