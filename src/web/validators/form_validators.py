"""
Provides form validation functionality for the web interface of the JSON to Excel Conversion Tool.

This module implements validators for form inputs, ensuring they meet required formats and
constraints before processing. It serves as a validation layer to prevent invalid inputs and
ensure data integrity.
"""

import re  # v: built-in
from typing import Dict, Optional, Any, List, Tuple, Union  # v: built-in

from ...backend.logger import get_logger
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ...backend.constants import ERROR_CODES
from ..models.conversion_options import ConversionOptions
from ..exceptions.api_exceptions import ValidationException
from ..constants import WEB_CONSTANTS

# Initialize logger
logger = get_logger(__name__)

# Validation constants and patterns
SHEET_NAME_PATTERN = re.compile(r'^[\w\s\-\.]{1,31}$')
FILENAME_PATTERN = re.compile(r'^[\w\s\-\.]{1,255}$')
VALID_ARRAY_HANDLING_OPTIONS = ["expand", "join"]
MAX_SHEET_NAME_LENGTH = 31  # Excel's limit


def validate_required_field(form_data: Dict[str, Any], field_name: str) -> tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a required field is present and not empty in form data.

    Args:
        form_data: The form data dictionary
        field_name: The name of the required field

    Returns:
        A tuple containing (is_valid, error_response) where error_response is None if valid
    """
    if field_name not in form_data or form_data[field_name] is None or form_data[field_name] == "":
        error = ErrorResponse(
            message=f"Required field '{field_name}' is missing or empty",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("field_name", field_name)
        error.add_resolution_step(f"Please provide a value for '{field_name}'")
        
        logger.warning(f"Validation failed: Required field '{field_name}' is missing or empty")
        return False, error
    
    return True, None


def validate_sheet_name(sheet_name: str) -> tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a sheet name follows Excel naming conventions.

    Args:
        sheet_name: The sheet name to validate

    Returns:
        A tuple containing (is_valid, error_response) where error_response is None if valid
    """
    # Check if sheet_name is not None and not empty
    if sheet_name is None or sheet_name == "":
        error = ErrorResponse(
            message="Sheet name cannot be empty",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("sheet_name", sheet_name)
        error.add_resolution_step("Please provide a valid sheet name")
        
        logger.warning("Validation failed: Sheet name is empty")
        return False, error
    
    # Check if sheet_name length is within Excel's limit
    if len(sheet_name) > MAX_SHEET_NAME_LENGTH:
        error = ErrorResponse(
            message=f"Sheet name exceeds maximum length of {MAX_SHEET_NAME_LENGTH} characters",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("sheet_name", sheet_name)
        error.add_context("max_length", MAX_SHEET_NAME_LENGTH)
        error.add_resolution_step(f"Please provide a sheet name with {MAX_SHEET_NAME_LENGTH} or fewer characters")
        
        logger.warning(f"Validation failed: Sheet name exceeds maximum length: {sheet_name}")
        return False, error
    
    # Check if sheet_name matches the allowed pattern
    if not SHEET_NAME_PATTERN.match(sheet_name):
        error = ErrorResponse(
            message="Sheet name contains invalid characters",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("sheet_name", sheet_name)
        error.add_context("allowed_pattern", SHEET_NAME_PATTERN.pattern)
        error.add_resolution_step("Sheet name should contain only letters, numbers, spaces, hyphens, and periods")
        
        logger.warning(f"Validation failed: Sheet name contains invalid characters: {sheet_name}")
        return False, error
    
    return True, None


def validate_output_filename(filename: str) -> tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that an output filename follows proper naming conventions.

    Args:
        filename: The filename to validate

    Returns:
        A tuple containing (is_valid, error_response) where error_response is None if valid
    """
    # Check if filename is not None and not empty
    if filename is None or filename == "":
        error = ErrorResponse(
            message="Output filename cannot be empty",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("filename", filename)
        error.add_resolution_step("Please provide a valid output filename")
        
        logger.warning("Validation failed: Output filename is empty")
        return False, error
    
    # Check if filename matches the allowed pattern
    if not FILENAME_PATTERN.match(filename):
        error = ErrorResponse(
            message="Output filename contains invalid characters",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("filename", filename)
        error.add_context("allowed_pattern", FILENAME_PATTERN.pattern)
        error.add_resolution_step("Filename should contain only letters, numbers, spaces, hyphens, and periods")
        
        logger.warning(f"Validation failed: Output filename contains invalid characters: {filename}")
        return False, error
    
    return True, None


def validate_array_handling(array_handling: str) -> tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that the array handling option is valid.

    Args:
        array_handling: The array handling option to validate

    Returns:
        A tuple containing (is_valid, error_response) where error_response is None if valid
    """
    # Check if array_handling is not None
    if array_handling is None:
        # Default to "expand" if not provided
        return True, None
    
    # Check if array_handling is a valid option
    if array_handling not in VALID_ARRAY_HANDLING_OPTIONS:
        error = ErrorResponse(
            message="Invalid array handling option",
            error_code=ERROR_CODES["VALIDATION_ERROR"],
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="form_validators"
        )
        error.add_context("array_handling", array_handling)
        error.add_context("valid_options", VALID_ARRAY_HANDLING_OPTIONS)
        error.add_resolution_step(f"Please select one of the valid options: {', '.join(VALID_ARRAY_HANDLING_OPTIONS)}")
        
        logger.warning(f"Validation failed: Invalid array handling option: {array_handling}")
        return False, error
    
    return True, None


class FormValidator:
    """
    A class that provides comprehensive form validation functionality for the web interface.
    """
    
    def validate_conversion_form(self, form_data: Dict[str, Any]) -> tuple[bool, Dict[str, ErrorResponse]]:
        """
        Validates a conversion form submission.

        Args:
            form_data: Dictionary containing form data

        Returns:
            A tuple containing (is_valid, field_errors) where field_errors is a dictionary
            mapping field names to error responses
        """
        errors = {}
        
        # Validate sheet_name if provided
        if "sheet_name" in form_data:
            is_valid, error = validate_sheet_name(form_data["sheet_name"])
            if not is_valid:
                errors["sheet_name"] = error
        
        # Validate output_filename if provided
        if "output_filename" in form_data:
            is_valid, error = validate_output_filename(form_data["output_filename"])
            if not is_valid:
                errors["output_filename"] = error
        
        # Validate array_handling if provided
        if "array_handling" in form_data:
            is_valid, error = validate_array_handling(form_data["array_handling"])
            if not is_valid:
                errors["array_handling"] = error
        
        # Create and validate ConversionOptions
        try:
            options = ConversionOptions.from_form_data(form_data)
            is_valid, error_message = options.validate()
            if not is_valid and error_message:
                error = ErrorResponse(
                    message=error_message,
                    error_code=ERROR_CODES["VALIDATION_ERROR"],
                    category=ErrorCategory.VALIDATION_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="form_validators"
                )
                errors["conversion_options"] = error
        except Exception as e:
            logger.error(f"Error validating conversion options: {str(e)}", exc_info=True)
            error = ErrorResponse(
                message="Error validating conversion options",
                error_code=ERROR_CODES["VALIDATION_ERROR"],
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="form_validators"
            )
            error.add_context("exception", str(e))
            errors["conversion_options"] = error
        
        return len(errors) == 0, errors
    
    def validate_with_exception(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates form data and raises a ValidationException if invalid.

        Args:
            form_data: Dictionary containing form data

        Returns:
            The validated form data

        Raises:
            ValidationException: If validation fails
        """
        is_valid, errors = self.validate_conversion_form(form_data)
        
        if not is_valid:
            # Create validation exception with all error details
            validation_errors = {field: error.to_dict() for field, error in errors.items()}
            
            exception = ValidationException(
                message="Form validation failed",
                validation_errors=validation_errors
            )
            
            logger.warning("Form validation failed, raising ValidationException")
            raise exception
        
        return form_data