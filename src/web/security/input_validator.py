"""
Provides input validation and sanitization functionality for the web interface of the JSON to Excel Conversion Tool.
This module implements security measures to prevent injection attacks, validate form data, and ensure that user inputs
meet the required formats and constraints before processing.
"""

import re  # v: built-in
import html  # v: built-in
import typing  # v: built-in
from typing import Dict, Any, Optional, List, Tuple, Union  # v: built-in

from ...backend.logger import get_logger
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ...backend.constants import ERROR_CODES
from ..validators.form_validators import FormValidator
from ..validators.json_validators import validate_json_structure
from ..exceptions.api_exceptions import ValidationException, BadRequestException
from ..utils.response_formatter import ResponseFormatter

# Initialize logger
logger = get_logger(__name__)

# Regular expression patterns for security checks
SCRIPT_TAG_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
HTML_TAG_PATTERN = re.compile(r'<[^>]*>', re.IGNORECASE)
SQL_INJECTION_PATTERN = re.compile(r'(\b(select|insert|update|delete|drop|alter|union|create|where)\b)|([\'"]);\s*--|--', re.IGNORECASE)
DANGEROUS_PATH_PATTERN = re.compile(r'\.\.\/|\.\.\||\.\.\\', re.IGNORECASE)


def sanitize_string(input_string: str, allow_html: bool = False) -> str:
    """
    Sanitizes a string input to prevent XSS and other injection attacks.
    
    Args:
        input_string: The string to sanitize
        allow_html: Whether to allow some HTML tags in the input
        
    Returns:
        Sanitized string
    """
    # Handle None values
    if input_string is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(input_string, str):
        input_string = str(input_string)
    
    # Escape HTML if not allowed
    if not allow_html:
        input_string = html.escape(input_string)
    
    # Always remove script tags for security
    input_string = SCRIPT_TAG_PATTERN.sub('', input_string)
    
    # Remove all HTML tags if not allowed
    if not allow_html:
        input_string = HTML_TAG_PATTERN.sub('', input_string)
    
    # Remove potential SQL injection patterns
    input_string = SQL_INJECTION_PATTERN.sub('', input_string)
    
    return input_string


def sanitize_path(path: str) -> str:
    """
    Sanitizes a file path to prevent directory traversal attacks.
    
    Args:
        path: The file path to sanitize
        
    Returns:
        Sanitized path
    """
    # Handle None values
    if path is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(path, str):
        path = str(path)
    
    # Remove directory traversal patterns
    path = DANGEROUS_PATH_PATTERN.sub('', path)
    
    return path


def sanitize_form_data(form_data: Dict[str, Any], html_allowed_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitizes all string values in a form data dictionary.
    
    Args:
        form_data: Dictionary containing form data
        html_allowed_fields: List of field names where HTML is allowed
        
    Returns:
        Sanitized form data dictionary
    """
    if html_allowed_fields is None:
        html_allowed_fields = []
    
    sanitized_data = {}
    
    for key, value in form_data.items():
        # For string values
        if isinstance(value, str):
            allow_html = key in html_allowed_fields
            sanitized_data[key] = sanitize_string(value, allow_html)
        
        # For nested dictionaries
        elif isinstance(value, dict):
            sanitized_data[key] = sanitize_form_data(value, html_allowed_fields)
        
        # For lists
        elif isinstance(value, list):
            sanitized_list = []
            for item in value:
                if isinstance(item, str):
                    allow_html = key in html_allowed_fields
                    sanitized_list.append(sanitize_string(item, allow_html))
                elif isinstance(item, dict):
                    sanitized_list.append(sanitize_form_data(item, html_allowed_fields))
                else:
                    sanitized_list.append(item)
            sanitized_data[key] = sanitized_list
        
        # For other types (pass through)
        else:
            sanitized_data[key] = value
    
    return sanitized_data


def validate_and_sanitize_json(json_data: Dict[str, Any]) -> Tuple[bool, Optional[ErrorResponse], Optional[Dict[str, Any]]]:
    """
    Validates and sanitizes a JSON object.
    
    Args:
        json_data: The JSON data to validate and sanitize
        
    Returns:
        Tuple containing (success, error_response, sanitized_data)
    """
    # Validate JSON structure
    is_valid, error = validate_json_structure(json_data)
    
    if not is_valid:
        logger.warning(f"JSON validation failed: {error.message if error else 'Unknown error'}")
        return False, error, None
    
    # Sanitize the JSON data recursively
    sanitized_data = {}
    
    for key, value in json_data.items():
        # For string values
        if isinstance(value, str):
            sanitized_data[key] = sanitize_string(value, False)
        
        # For nested dictionaries
        elif isinstance(value, dict):
            _, _, sanitized_nested = validate_and_sanitize_json(value)
            if sanitized_nested:
                sanitized_data[key] = sanitized_nested
            else:
                sanitized_data[key] = {}
        
        # For lists
        elif isinstance(value, list):
            sanitized_list = []
            for item in value:
                if isinstance(item, str):
                    sanitized_list.append(sanitize_string(item, False))
                elif isinstance(item, dict):
                    _, _, sanitized_item = validate_and_sanitize_json(item)
                    if sanitized_item:
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append({})
                else:
                    sanitized_list.append(item)
            sanitized_data[key] = sanitized_list
        
        # For other types (pass through)
        else:
            sanitized_data[key] = value
    
    return True, None, sanitized_data


class InputValidator:
    """
    A class that provides input validation and sanitization functionality for the web interface.
    """
    
    def __init__(self):
        """
        Initializes a new InputValidator instance.
        """
        self._form_validator = FormValidator()
        logger.debug("InputValidator initialized")
    
    def sanitize_input(self, input_data: Any, allow_html: bool = False) -> Any:
        """
        Sanitizes user input to prevent injection attacks.
        
        Args:
            input_data: The input data to sanitize
            allow_html: Whether to allow HTML in string inputs
            
        Returns:
            Sanitized input data
        """
        # Handle None
        if input_data is None:
            return None
        
        # Handle strings
        if isinstance(input_data, str):
            return sanitize_string(input_data, allow_html)
        
        # Handle dictionaries
        if isinstance(input_data, dict):
            sanitized_dict = {}
            for key, value in input_data.items():
                sanitized_dict[key] = self.sanitize_input(value, allow_html)
            return sanitized_dict
        
        # Handle lists
        if isinstance(input_data, list):
            sanitized_list = []
            for item in input_data:
                sanitized_list.append(self.sanitize_input(item, allow_html))
            return sanitized_list
        
        # For other types (pass through)
        return input_data
    
    def validate_form_data(self, form_data: Dict[str, Any], 
                           required_fields: Optional[List[str]] = None,
                           html_allowed_fields: Optional[List[str]] = None) -> Tuple[bool, Union[Dict[str, Any], Dict[str, ErrorResponse]]]:
        """
        Validates and sanitizes form data from web requests.
        
        Args:
            form_data: Dictionary containing form data
            required_fields: List of fields that must be present and non-empty
            html_allowed_fields: List of fields where HTML is allowed
            
        Returns:
            Tuple containing (success, data_or_errors)
            If successful, data_or_errors is the sanitized form data
            If not successful, data_or_errors is a dictionary of field errors
        """
        if required_fields is None:
            required_fields = []
            
        if html_allowed_fields is None:
            html_allowed_fields = []
        
        # Sanitize form data
        sanitized_form_data = sanitize_form_data(form_data, html_allowed_fields)
        
        # Validate form data
        is_valid, error_dict = self._form_validator.validate_conversion_form(sanitized_form_data)
        
        if not is_valid:
            logger.warning(f"Form validation failed: {len(error_dict)} errors")
            return False, error_dict
        
        # Check required fields
        missing_required_fields = []
        for field in required_fields:
            if field not in sanitized_form_data or not sanitized_form_data[field]:
                missing_required_fields.append(field)
                error = ErrorResponse(
                    message=f"Required field '{field}' is missing or empty",
                    error_code=ERROR_CODES["VALIDATION_ERROR"],
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="InputValidator"
                )
                error_dict[field] = error
                logger.warning(f"Validation failed: Required field '{field}' is missing or empty")
        
        if missing_required_fields:
            return False, error_dict
        
        return True, sanitized_form_data
    
    def validate_json_payload(self, json_data: Dict[str, Any], 
                             required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validates and sanitizes JSON data from API requests.
        
        Args:
            json_data: Dictionary containing JSON data
            required_fields: List of fields that must be present and non-empty
            
        Returns:
            Validated and sanitized JSON data
            
        Raises:
            ValidationException: If validation fails
        """
        if required_fields is None:
            required_fields = []
        
        # Check required fields
        for field in required_fields:
            if field not in json_data or json_data[field] is None:
                logger.warning(f"Validation failed: Required field '{field}' is missing in JSON payload")
                raise ValidationException(
                    message=f"Required field '{field}' is missing",
                    validation_errors={
                        field: {
                            "message": f"Required field '{field}' is missing",
                            "code": ERROR_CODES["VALIDATION_ERROR"]
                        }
                    }
                )
        
        # Validate and sanitize JSON
        is_valid, error, sanitized_json_data = validate_and_sanitize_json(json_data)
        
        if not is_valid:
            logger.warning(f"JSON validation failed: {error.message if error else 'Unknown error'}")
            raise ValidationException(
                message="JSON validation failed",
                validation_errors={"json": error.to_dict() if error else {"message": "Invalid JSON structure"}}
            )
        
        return sanitized_json_data
    
    def validate_with_response(self, data: Dict[str, Any], validation_type: str):
        """
        Validates input data and returns a formatted response.
        
        Args:
            data: The data to validate
            validation_type: Type of validation to perform ('form' or 'json')
            
        Returns:
            A formatted validation response
        """
        if validation_type == 'form':
            is_valid, result = self.validate_form_data(data)
            return ResponseFormatter.validation_result(is_valid, result)
        
        elif validation_type == 'json':
            try:
                sanitized_data = self.validate_json_payload(data)
                return ResponseFormatter.validation_result(True, {"sanitized_data": sanitized_data})
            except ValidationException as e:
                return ResponseFormatter.validation_result(False, e.context.get("validation_errors", {}))
        
        else:
            logger.warning(f"Unknown validation type: {validation_type}")
            return ResponseFormatter.error(f"Unknown validation type: {validation_type}", status_code=400)
    
    def validate_with_exception(self, data: Dict[str, Any], validation_type: str) -> Dict[str, Any]:
        """
        Validates input data and raises an exception if invalid.
        
        Args:
            data: The data to validate
            validation_type: Type of validation to perform ('form' or 'json')
            
        Returns:
            Validated and sanitized data
            
        Raises:
            ValidationException: If validation fails
            BadRequestException: If validation type is unknown
        """
        if validation_type == 'form':
            is_valid, result = self.validate_form_data(data)
            
            if not is_valid:
                logger.warning("Form validation failed, raising ValidationException")
                raise ValidationException(
                    message="Form validation failed",
                    validation_errors={field: error.to_dict() for field, error in result.items()}
                )
            
            return result
        
        elif validation_type == 'json':
            return self.validate_json_payload(data)
        
        else:
            logger.warning(f"Unknown validation type: {validation_type}")
            raise BadRequestException(f"Unknown validation type: {validation_type}")