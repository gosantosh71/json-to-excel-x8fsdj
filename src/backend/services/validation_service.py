"""
Provides a comprehensive validation service for the JSON to Excel Conversion Tool.

This service orchestrates the validation of JSON files, their structure, content, and output paths,
leveraging specialized validators to ensure data integrity throughout the conversion process.
"""

import os  # v: built-in
import json  # v: built-in
from typing import Dict, List, Any, Optional, Tuple  # v: built-in

from ..validators.json_validator import JSONValidator
from ..validators.file_validator import FileValidator
from ..models.json_data import JSONData
from ..models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..adapters.file_system_adapter import FileSystemAdapter
from ..exceptions import JSONParsingException, JSONValidationException, FileNotFoundError
from ..constants import JSON_CONSTANTS, FILE_CONSTANTS
from ..logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Import constants
MAX_FILE_SIZE_BYTES = FILE_CONSTANTS['MAX_FILE_SIZE_BYTES']
MAX_FILE_SIZE_MB = FILE_CONSTANTS['MAX_FILE_SIZE_MB']
MAX_NESTING_LEVEL = JSON_CONSTANTS['MAX_NESTING_LEVEL']

def create_validation_result(is_valid: bool, errors: List[ErrorResponse], details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Creates a standardized validation result dictionary with status and error information.
    
    Args:
        is_valid: Boolean indicating validation success
        errors: List of error responses 
        details: Additional details about the validation
        
    Returns:
        A validation result dictionary with status, errors, and details
    """
    result = {
        'is_valid': is_valid,
        'errors': [error.to_dict() for error in errors] if errors else []
    }
    
    if details:
        result['details'] = details
        
    return result

def merge_validation_errors(error_lists: List[List[ErrorResponse]]) -> List[ErrorResponse]:
    """
    Merges multiple lists of validation errors into a single list.
    
    Args:
        error_lists: List of error response lists to merge
        
    Returns:
        A combined list of all error responses
    """
    merged_errors = []
    for errors in error_lists:
        merged_errors.extend(errors)
    return merged_errors

class ValidationService:
    """
    A service class that orchestrates validation of JSON files, content, and output paths.
    """
    
    def __init__(
        self, 
        max_file_size_mb: Optional[int] = None,
        max_nesting_level: Optional[int] = None
    ):
        """
        Initializes a new ValidationService instance with optional custom validation parameters.
        
        Args:
            max_file_size_mb: Maximum allowed file size in megabytes
            max_nesting_level: Maximum allowed nesting level for JSON structures
        """
        self._max_file_size_bytes = max_file_size_mb * 1024 * 1024 if max_file_size_mb else MAX_FILE_SIZE_BYTES
        self._max_nesting_level = max_nesting_level or MAX_NESTING_LEVEL
        self._file_validator = FileValidator()
        self._json_validator = JSONValidator(
            max_nesting_level=self._max_nesting_level,
            max_file_size_bytes=self._max_file_size_bytes
        )
        self._file_system_adapter = FileSystemAdapter()
        
        logger.debug(
            f"ValidationService initialized with max_file_size={self._max_file_size_bytes} bytes, "
            f"max_nesting_level={self._max_nesting_level}"
        )
    
    def validate_json_file(self, file_path: str) -> Tuple[bool, List[ErrorResponse], Optional[JSONData]]:
        """
        Validates a JSON file for existence, readability, size, and content.
        
        Args:
            file_path: Path to the JSON file to validate
            
        Returns:
            Tuple containing validation result, list of errors, and JSONData if valid
        """
        errors = []
        
        # Validate file exists and is a JSON file
        is_valid_file, file_errors = self._file_validator.validate_json_file(file_path)
        if not is_valid_file:
            return False, file_errors, None
        
        # Check file size
        try:
            file_size = self._file_system_adapter.get_file_size(file_path)
            is_valid_size, size_error = self._json_validator.validate_file_size(file_size)
            if not is_valid_size and size_error:
                errors.append(size_error)
                return False, errors, None
        except Exception as e:
            error = ErrorResponse(
                message=f"Error checking file size: {str(e)}",
                error_code="E003",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="ValidationService"
            )
            errors.append(error)
            return False, errors, None
        
        # Read and validate JSON content
        try:
            json_content = self._file_system_adapter.read_json(file_path)
        except FileNotFoundError as e:
            error = ErrorResponse(
                message=f"File not found: {file_path}",
                error_code="E001",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="ValidationService"
            )
            errors.append(error)
            return False, errors, None
        except Exception as e:
            error = ErrorResponse(
                message=f"Error reading JSON file: {str(e)}",
                error_code="E001",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="ValidationService"
            )
            errors.append(error)
            return False, errors, None
        
        # Validate JSON syntax
        is_valid_json, json_error, parsed_json = self._json_validator.validate_json_string(json_content)
        if not is_valid_json:
            errors.append(json_error)
            return False, errors, None
        
        # Create JSONData object and analyze structure
        json_data = JSONData(
            content=parsed_json,
            source_path=file_path,
            size_bytes=file_size
        )
        json_data.analyze_structure()
        
        # Validate JSON structure and complexity
        is_valid_structure, structure_errors = self._json_validator.validate_json_data_object(json_data)
        if not is_valid_structure:
            errors.extend(structure_errors)
            return False, errors, json_data
        
        # All validations passed
        return True, [], json_data
    
    def validate_json_string(self, json_string: str) -> Tuple[bool, List[ErrorResponse], Optional[JSONData]]:
        """
        Validates a JSON string for syntax, structure, and complexity.
        
        Args:
            json_string: The JSON string to validate
            
        Returns:
            Tuple containing validation result, list of errors, and JSONData if valid
        """
        # Validate JSON syntax
        is_valid_json, json_error, parsed_json = self._json_validator.validate_json_string(json_string)
        if not is_valid_json:
            return False, [json_error], None
        
        # Estimate size of JSON
        size_bytes = len(json_string.encode('utf-8'))
        
        # Create JSONData object and analyze structure
        json_data = JSONData(
            content=parsed_json,
            source_path="memory",
            size_bytes=size_bytes
        )
        json_data.analyze_structure()
        
        # Validate JSON structure and complexity
        is_valid_structure, structure_errors = self._json_validator.validate_json_data_object(json_data)
        if not is_valid_structure:
            return False, structure_errors, json_data
        
        # All validations passed
        return True, [], json_data
    
    def validate_output_path(self, file_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates that an output file path is valid and writable.
        
        Args:
            file_path: Path where the output file will be written
            
        Returns:
            Tuple containing validation result and optional error
        """
        return self._file_validator.validate_output_path(file_path)
    
    def get_json_validation_warnings(self, json_data: JSONData) -> List[Dict[str, Any]]:
        """
        Gets warnings about potential issues with JSON data.
        
        Args:
            json_data: The JSONData object to analyze
            
        Returns:
            List of warning dictionaries with issue details
        """
        return self._json_validator.get_validation_warnings(json_data)
    
    def get_file_details(self, file_path: str) -> Dict[str, Any]:
        """
        Gets detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file details
        """
        return self._file_validator.get_file_details(file_path)
    
    def validate_conversion_parameters(
        self, 
        input_path: str, 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[ErrorResponse]]:
        """
        Validates parameters for the conversion process.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Path for the output Excel file
            options: Optional dictionary of conversion options
            
        Returns:
            Tuple containing validation result and list of errors
        """
        errors = []
        
        # Validate input file
        is_valid_input, input_errors, _ = self.validate_json_file(input_path)
        if not is_valid_input:
            errors.extend(input_errors)
        
        # Validate output path
        is_valid_output, output_error = self.validate_output_path(output_path)
        if not is_valid_output and output_error:
            errors.append(output_error)
        
        # Validate options if provided
        if options:
            # Example validation for common options
            if 'array_handling' in options:
                valid_modes = JSON_CONSTANTS.get('ARRAY_HANDLING_OPTIONS', ['expand', 'join'])
                if options['array_handling'] not in valid_modes:
                    error = ErrorResponse(
                        message=f"Invalid array handling mode: {options['array_handling']}. Valid modes: {', '.join(valid_modes)}",
                        error_code="E006",
                        category=ErrorCategory.VALIDATION_ERROR,
                        severity=ErrorSeverity.ERROR,
                        source_component="ValidationService"
                    )
                    errors.append(error)
        
        # Return validation result
        return len(errors) == 0, errors
    
    def create_validation_summary(self, json_data: JSONData) -> Dict[str, Any]:
        """
        Creates a summary of validation results including warnings and recommendations.
        
        Args:
            json_data: The JSONData object containing information about the JSON structure
            
        Returns:
            A dictionary containing validation summary information
        """
        # Get validation warnings
        warnings = self.get_json_validation_warnings(json_data)
        
        # Build summary with structure information
        summary = {
            'structure': {
                'is_nested': json_data.is_nested,
                'max_nesting_level': json_data.max_nesting_level,
                'contains_arrays': json_data.contains_arrays,
                'array_paths': json_data.array_paths,
                'complexity_score': json_data.complexity_score,
                'complexity_level': json_data.complexity_level.name,
                'flattening_strategy': json_data.get_flattening_strategy()
            },
            'warnings': warnings,
            'recommendations': []
        }
        
        # Add recommendations based on structure
        if json_data.is_nested and json_data.max_nesting_level > MAX_NESTING_LEVEL * 0.7:
            summary['recommendations'].append({
                'type': 'structure',
                'message': 'Consider simplifying the nested structure for better Excel rendering',
                'impact': 'high'
            })
        
        if json_data.contains_arrays and len(json_data.array_paths) > 5:
            summary['recommendations'].append({
                'type': 'arrays',
                'message': 'Multiple arrays detected - consider using array expansion mode for better results',
                'impact': 'medium'
            })
        
        if json_data.complexity_score > 7:
            summary['recommendations'].append({
                'type': 'complexity',
                'message': 'High complexity detected - conversion may take longer than usual',
                'impact': 'medium'
            })
            
        # Add performance expectations based on complexity
        if json_data.complexity_score < 3:
            summary['performance_estimate'] = 'fast'
        elif json_data.complexity_score < 7:
            summary['performance_estimate'] = 'normal'
        else:
            summary['performance_estimate'] = 'slow'
        
        return summary