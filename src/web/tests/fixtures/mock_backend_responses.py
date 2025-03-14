"""
Provides mock backend response fixtures for testing the web interface of the JSON to Excel Conversion Tool.
This module contains predefined response structures that simulate backend service responses for validation, conversion, and error scenarios, allowing tests to run without actual backend dependencies.
"""
import pytest  # v: 7.3.0+ - For creating test fixtures
from typing import Dict, Optional, Tuple  # v: built-in - For type hints in fixture functions
from unittest.mock import Mock  # v: built-in - For creating mock objects in test fixtures
from datetime import datetime  # v: built-in - For generating timestamps in mock responses

from src.backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity  # For creating standardized error responses in test fixtures
from src.web.backend_interface.conversion_client import ConversionClient  # For mocking the conversion client interface

VALID_JSON_RESPONSE = '{"is_valid": true, "structure": {"type": "object", "properties": {"name": "string", "value": "number"}}, "size": 1024, "complexity": {"nesting_level": 2, "has_arrays": true}}'
INVALID_JSON_RESPONSE = '{"is_valid": false, "error": {"message": "Invalid JSON syntax", "line": 3, "column": 15}}'
SUCCESSFUL_CONVERSION_RESPONSE = '{"success": true, "output_file": "output.xlsx", "rows": 10, "columns": 5, "processing_time_ms": 234}'
FAILED_CONVERSION_RESPONSE = '{"success": false, "error": {"message": "Failed to convert JSON", "category": "TRANSFORMATION_ERROR", "code": 500}}'


@pytest.fixture
def create_mock_validation_response(is_valid: bool, structure_info: Dict, error_info: Dict) -> Dict:
    """
    Creates a mock validation response for testing JSON validation functionality.

    Parameters:
        is_valid (bool): Whether the JSON is valid
        structure_info (dict): Information about the JSON structure
        error_info (dict): Information about the validation error

    Returns:
        dict: A dictionary containing mock validation response
    """
    response = {"is_valid": is_valid}  # Step 1: Create a base response dictionary with is_valid flag
    if is_valid:
        response.update(structure_info)  # Step 2: If is_valid is True, add structure_info to the response
    else:
        response.update({"error": error_info})  # Step 3: If is_valid is False, add error_info to the response
    return response  # Step 4: Return the complete response dictionary


@pytest.fixture
def create_mock_conversion_response(success: bool, output_file: str, rows: int, columns: int, error_info: Dict) -> Dict:
    """
    Creates a mock conversion response for testing JSON to Excel conversion functionality.

    Parameters:
        success (bool): Whether the conversion was successful
        output_file (str): The name of the output file
        rows (int): The number of rows in the output file
        columns (int): The number of columns in the output file
        error_info (dict): Information about the conversion error

    Returns:
        dict: A dictionary containing mock conversion response
    """
    response = {"success": success}  # Step 1: Create a base response dictionary with success flag
    if success:
        response.update({
            "output_file": output_file,
            "rows": rows,
            "columns": columns,
            "processing_time_ms": 234
        })  # Step 2: If success is True, add output_file, rows, columns, and processing time to the response
    else:
        response.update({"error": error_info})  # Step 3: If success is False, add error_info to the response
    return response  # Step 4: Return the complete response dictionary


@pytest.fixture
def create_mock_error_response(message: str, category: ErrorCategory, code: int, severity: ErrorSeverity) -> ErrorResponse:
    """
    Creates a mock error response for testing error handling functionality.

    Parameters:
        message (str): The error message
        category (ErrorCategory): The category of the error
        code (int): The error code
        severity (ErrorSeverity): The severity of the error

    Returns:
        ErrorResponse: An ErrorResponse instance with the specified parameters
    """
    message = message or "Test error message"  # Step 1: Set message to the provided value or a default error message
    category = category or ErrorCategory.VALIDATION_ERROR  # Step 2: Set category to the provided value or ErrorCategory.VALIDATION_ERROR
    code = code or 400  # Step 3: Set code to the provided value or 400
    severity = severity or ErrorSeverity.ERROR  # Step 4: Set severity to the provided value or ErrorSeverity.ERROR
    return ErrorResponse(message=message, error_code=str(code), category=category, severity=severity, source_component="Test")  # Step 5: Create and return a new ErrorResponse with these values


@pytest.fixture
def mock_validation_success() -> Tuple[bool, Dict, None]:
    """
    Creates a mock successful validation response for testing.

    Returns:
        tuple: (True, dict, None)
    """
    response = {"is_valid": True, "structure": {"type": "object", "properties": {"name": "string", "value": "number"}}, "size": 1024, "complexity": {"nesting_level": 2, "has_arrays": True}}  # Step 1: Create a successful validation response using create_mock_validation_response
    return True, response, None  # Step 2: Return (True, response, None) to simulate successful validation


@pytest.fixture
def mock_validation_failure(create_mock_error_response: ErrorResponse) -> Tuple[bool, None, Dict]:
    """
    Creates a mock failed validation response for testing.

    Returns:
        tuple: (False, None, dict)
    """
    error = create_mock_error_response  # Step 1: Create an error response using create_mock_error_response
    error_dict = error.to_dict()  # Step 2: Convert the error response to a dictionary
    return False, None, error_dict  # Step 3: Return (False, None, error_dict) to simulate failed validation


@pytest.fixture
def mock_conversion_success() -> Tuple[bool, Dict, None]:
    """
    Creates a mock successful conversion response for testing.

    Returns:
        tuple: (True, dict, None)
    """
    response = {"success": True, "output_file": "output.xlsx", "rows": 10, "columns": 5, "processing_time_ms": 234}  # Step 1: Create a successful conversion response using create_mock_conversion_response
    return True, response, None  # Step 2: Return (True, response, None) to simulate successful conversion


@pytest.fixture
def mock_conversion_failure(create_mock_error_response: ErrorResponse) -> Tuple[bool, None, Dict]:
    """
    Creates a mock failed conversion response for testing.

    Returns:
        tuple: (False, None, dict)
    """
    error = create_mock_error_response  # Step 1: Create an error response using create_mock_error_response
    error_dict = error.to_dict()  # Step 2: Convert the error response to a dictionary
    return False, None, error_dict  # Step 3: Return (False, None, error_dict) to simulate failed conversion


@pytest.fixture
def mock_conversion_client(validation_success: bool, conversion_success: bool, mock_validation_success: Tuple[bool, Dict, None], mock_validation_failure: Tuple[bool, None, Dict], mock_conversion_success: Tuple[bool, Dict, None], mock_conversion_failure: Tuple[bool, None, Dict]) -> Mock:
    """
    Creates a mock ConversionClient for testing without backend dependencies.

    Parameters:
        validation_success (bool): Whether validation should succeed
        conversion_success (bool): Whether conversion should succeed

    Returns:
        Mock: A mock ConversionClient with predetermined responses
    """
    client = Mock(spec=ConversionClient)  # Step 1: Create a mock ConversionClient object
    if validation_success:
        client.validate_file.return_value = mock_validation_success  # Step 2: Configure validate_file to return mock_validation_success or mock_validation_failure based on validation_success
    else:
        client.validate_file.return_value = mock_validation_failure
    if conversion_success:
        client.convert_file.return_value = mock_conversion_success  # Step 3: Configure convert_file to return mock_conversion_success or mock_conversion_failure based on conversion_success
    else:
        client.convert_file.return_value = mock_conversion_failure
    client.process_conversion_job.return_value = conversion_success  # Step 4: Configure process_conversion_job to return conversion_success
    return client  # Step 5: Return the mock client


class MockBackendResponse:
    """
    A utility class for generating standardized mock backend responses for testing.
    """

    def __init__(self):
        """
        Initializes a new MockBackendResponse instance.
        """
        pass  # Step 1: Initialize the class with default values

    def validation_success(self, structure_info: Dict) -> Dict:
        """
        Generates a successful validation response with customizable details.

        Parameters:
            structure_info (dict): Additional structure information to include in the response

        Returns:
            dict: A dictionary containing a successful validation response
        """
        response = {"is_valid": True, "structure": {"type": "object", "properties": {"name": "string", "value": "number"}}, "size": 1024, "complexity": {"nesting_level": 2, "has_arrays": True}}  # Step 1: Create a base successful validation response
        if structure_info:
            response["structure"].update(structure_info)  # Step 2: Merge with provided structure_info if any
        return response  # Step 3: Return the complete response dictionary

    def validation_error(self, message: str, line: int, column: int) -> Dict:
        """
        Generates a validation error response with customizable details.

        Parameters:
            message (str): The error message
            line (int): The line number where the error occurred
            column (int): The column number where the error occurred

        Returns:
            dict: A dictionary containing a validation error response
        """
        response = {"is_valid": False, "error": {"message": "Invalid JSON syntax", "line": 3, "column": 15}}  # Step 1: Create a base validation error response
        response["error"]["message"] = message  # Step 2: Set custom message, line, and column if provided
        response["error"]["line"] = line
        response["error"]["column"] = column
        return response  # Step 3: Return the complete error response dictionary

    def conversion_success(self, output_file: str, rows: int, columns: int) -> Dict:
        """
        Generates a successful conversion response with customizable details.

        Parameters:
            output_file (str): The name of the output file
            rows (int): The number of rows in the output file
            columns (int): The number of columns in the output file

        Returns:
            dict: A dictionary containing a successful conversion response
        """
        response = {"success": True, "output_file": "output.xlsx", "rows": 10, "columns": 5}  # Step 1: Create a base successful conversion response
        response["output_file"] = output_file  # Step 2: Set custom output_file, rows, and columns if provided
        response["rows"] = rows
        response["columns"] = columns
        response["processing_time_ms"] = 234  # Add processing time and other metadata
        return response  # Step 3: Return the complete response dictionary

    def conversion_error(self, message: str, category: ErrorCategory, code: int) -> Dict:
        """
        Generates a conversion error response with customizable details.

        Parameters:
            message (str): The error message
            category (ErrorCategory): The category of the error
            code (int): The error code

        Returns:
            dict: A dictionary containing a conversion error response
        """
        response = {"success": False, "error": {"message": "Failed to convert JSON", "category": "TRANSFORMATION_ERROR", "code": 500}}  # Step 1: Create a base conversion error response
        response["error"]["message"] = message  # Step 2: Set custom message, category, and code if provided
        response["error"]["category"] = category.value
        response["error"]["code"] = code
        return response  # Step 3: Return the complete error response dictionary

    def create_error_response(self, message: str, category: ErrorCategory, code: int, severity: ErrorSeverity) -> ErrorResponse:
        """
        Creates an ErrorResponse object with the specified details.

        Parameters:
            message (str): The error message
            category (ErrorCategory): The category of the error
            code (int): The error code
            severity (ErrorSeverity): The severity of the error

        Returns:
            ErrorResponse: An ErrorResponse instance with the specified parameters
        """
        return ErrorResponse(message=message, error_code=str(code), category=category, severity=severity, source_component="Test")  # Step 1: Create and return a new ErrorResponse with the provided parameters
        # Step 2: Add standard resolution steps based on the error category


class MockConversionClient:
    """
    A mock implementation of ConversionClient for testing without backend dependencies.
    """

    def __init__(self, validation_success: bool = True, conversion_success: bool = True, validation_result: Dict = None, conversion_result: Dict = None, error_response: Dict = None):
        """
        Initializes a new MockConversionClient with predetermined responses.

        Parameters:
            validation_success (bool): Whether validation should succeed (default: True)
            conversion_success (bool): Whether conversion should succeed (default: True)
            validation_result (dict): The validation result (default: a successful validation response)
            conversion_result (dict): The conversion result (default: a successful conversion response)
            error_response (dict): The error response (default: a default error response)
        """
        self.validation_success = validation_success  # Step 1: Set validation_success to the provided value or True
        self.conversion_success = conversion_success  # Step 2: Set conversion_success to the provided value or True
        self.validation_result = validation_result or {"is_valid": True, "structure": {"type": "object", "properties": {"name": "string", "value": "number"}}, "size": 1024, "complexity": {"nesting_level": 2, "has_arrays": True}}  # Step 3: Set validation_result to the provided value or a default successful validation response
        self.conversion_result = conversion_result or {"success": True, "output_file": "output.xlsx", "rows": 10, "columns": 5, "processing_time_ms": 234}  # Step 4: Set conversion_result to the provided value or a default successful conversion response
        self.error_response = error_response or {"message": "Test error message", "category": "VALIDATION_ERROR", "code": 400, "severity": "ERROR"}  # Step 5: Set error_response to the provided value or a default error response

    def validate_file(self, file_path: str) -> Tuple[bool, Dict, Optional[Dict]]:
        """
        Mock implementation of validate_file that returns predetermined results.

        Parameters:
            file_path (str): The path to the file to validate

        Returns:
            tuple: (bool, dict, Optional[dict])
        """
        if self.validation_success:
            return True, self.validation_result, None  # Step 1: If validation_success is True, return (True, validation_result, None)
        else:
            return False, None, self.error_response  # Step 2: If validation_success is False, return (False, None, error_response)

    def convert_file(self, input_path: str, output_path: str, options: Dict) -> Tuple[bool, Dict, Optional[Dict]]:
        """
        Mock implementation of convert_file that returns predetermined results.

        Parameters:
            input_path (str): The path to the input file
            output_path (str): The path to the output file
            options (dict): The conversion options

        Returns:
            tuple: (bool, dict, Optional[dict])
        """
        if self.conversion_success:
            return True, self.conversion_result, None  # Step 1: If conversion_success is True, return (True, conversion_result, None)
        else:
            return False, None, self.error_response  # Step 2: If conversion_success is False, return (False, None, error_response)

    def process_conversion_job(self, job: object) -> bool:
        """
        Mock implementation of process_conversion_job that returns predetermined results.

        Parameters:
            job (object): The conversion job object

        Returns:
            bool: Success flag
        """
        # Update job status to completed with conversion_result
        # Update job status to failed with error_response
        return self.conversion_success  # Step 1: If conversion_success is True, update job status to completed with conversion_result # Step 2: If conversion_success is False, update job status to failed with error_response # Step 3: Return conversion_success