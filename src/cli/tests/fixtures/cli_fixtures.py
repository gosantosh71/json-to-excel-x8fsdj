"""
Provides test fixtures for the CLI component of the JSON to Excel Conversion Tool.

This module contains functions that generate sample command options, CLI responses,
and error responses for use in unit, integration, and end-to-end tests of the CLI interface.
"""

import os  # v: built-in
import json  # v: built-in
from typing import Dict, Any  # v: built-in

from ../../models.command_options import CommandOptions, CommandType
from ../../models.cli_response import CLIResponse, ResponseType
from ../../backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity


def get_basic_command_options() -> CommandOptions:
    """
    Creates a CommandOptions instance with basic options for testing standard conversion scenarios.
    
    Returns:
        CommandOptions: A CommandOptions instance with basic conversion settings
    """
    args = load_sample_args("basic_args.json")
    return CommandOptions.from_dict(args)


def get_complex_command_options() -> CommandOptions:
    """
    Creates a CommandOptions instance with complex options for testing advanced conversion scenarios.
    
    Returns:
        CommandOptions: A CommandOptions instance with advanced conversion settings
    """
    args = load_sample_args("complex_args.json")
    return CommandOptions.from_dict(args)


def get_invalid_command_options() -> CommandOptions:
    """
    Creates a CommandOptions instance with invalid options for testing error handling.
    
    Returns:
        CommandOptions: A CommandOptions instance with invalid settings
    """
    args = load_sample_args("invalid_args.json")
    return CommandOptions.from_dict(args)


def get_success_response(message: str, data: Dict[str, Any]) -> CLIResponse:
    """
    Creates a CLIResponse instance representing a successful command execution.
    
    Args:
        message: The success message to display
        data: Additional data to include in the response
        
    Returns:
        CLIResponse: A CLIResponse instance with SUCCESS type
    """
    return CLIResponse(
        response_type=ResponseType.SUCCESS,
        message=message,
        data=data,
        metadata={"timestamp": "2023-05-20T15:30:45", "version": "1.0.0"}
    )


def get_error_response(message: str, error: ErrorResponse) -> CLIResponse:
    """
    Creates a CLIResponse instance representing a failed command execution.
    
    Args:
        message: The error message to display
        error: The ErrorResponse object with detailed error information
        
    Returns:
        CLIResponse: A CLIResponse instance with ERROR type
    """
    return CLIResponse(
        response_type=ResponseType.ERROR,
        message=message,
        error=error,
        metadata={"timestamp": "2023-05-20T15:30:45", "version": "1.0.0"}
    )


def get_validation_error(message: str) -> ErrorResponse:
    """
    Creates an ErrorResponse instance for validation errors.
    
    Args:
        message: The validation error message
        
    Returns:
        ErrorResponse: An ErrorResponse instance for validation errors
    """
    error = ErrorResponse(
        message=message,
        error_code="CLI_VALIDATION_ERROR",
        category=ErrorCategory.VALIDATION_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="cli.argument_parser"
    )
    
    # Add common resolution steps for validation errors
    error.add_resolution_step("Check the command syntax and try again")
    error.add_resolution_step("Use the --help option for usage information")
    error.add_resolution_step("Verify that all required arguments are provided")
    
    return error


def get_file_not_found_error(file_path: str) -> ErrorResponse:
    """
    Creates an ErrorResponse instance for file not found errors.
    
    Args:
        file_path: The path to the file that couldn't be found
        
    Returns:
        ErrorResponse: An ErrorResponse instance for file not found errors
    """
    error = ErrorResponse(
        message=f"File not found: '{file_path}'",
        error_code="FILE_NOT_FOUND",
        category=ErrorCategory.INPUT_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="cli.command_runner"
    )
    
    # Add context with the file path
    error.add_context("file_path", file_path)
    
    # Add resolution steps for file not found errors
    error.add_resolution_step("Check if the file exists at the specified location")
    error.add_resolution_step("Verify that the file path is correct")
    error.add_resolution_step("Ensure you have permission to access the file")
    
    return error


def get_json_parsing_error(file_path: str, error_details: str) -> ErrorResponse:
    """
    Creates an ErrorResponse instance for JSON parsing errors.
    
    Args:
        file_path: The path to the JSON file with parsing errors
        error_details: Detailed information about the parsing error
        
    Returns:
        ErrorResponse: An ErrorResponse instance for JSON parsing errors
    """
    error = ErrorResponse(
        message=f"Invalid JSON format in file: '{file_path}'",
        error_code="JSON_PARSE_ERROR",
        category=ErrorCategory.PARSING_ERROR,
        severity=ErrorSeverity.ERROR,
        source_component="backend.json_parser"
    )
    
    # Add context with the file path and error details
    error.add_context("file_path", file_path)
    error.add_context("error_details", error_details)
    
    # Add resolution steps for JSON parsing errors
    error.add_resolution_step("Check the JSON syntax for errors")
    error.add_resolution_step("Validate the JSON using a JSON validator tool")
    error.add_resolution_step("Fix any formatting or syntax issues in the JSON file")
    
    return error


def get_conversion_success_data() -> Dict[str, Any]:
    """
    Creates sample data for a successful conversion response.
    
    Returns:
        Dict[str, Any]: A dictionary with sample conversion result data
    """
    return {
        "input_file": {
            "path": "sample_data.json",
            "size": 1254789,  # bytes
            "format": "json"
        },
        "output_file": {
            "path": "result.xlsx",
            "size": 874562,  # bytes
            "format": "xlsx"
        },
        "stats": {
            "rows": 150,
            "columns": 12,
            "processing_time": 2.3,  # seconds
            "memory_used": 125.7  # MB
        },
        "settings": {
            "sheet_name": "Sheet1",
            "array_handling": "expand"
        }
    }


def load_sample_args(filename: str) -> Dict[str, Any]:
    """
    Loads sample command arguments from a JSON file.
    
    Args:
        filename: The name of the sample arguments file
        
    Returns:
        Dict[str, Any]: A dictionary containing the loaded arguments
    """
    # Construct path to sample args directory relative to this file
    fixtures_dir = os.path.dirname(os.path.abspath(__file__))
    sample_args_dir = os.path.join(fixtures_dir, "sample_args")
    file_path = os.path.join(sample_args_dir, filename)
    
    # Read and parse the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)