"""
Implements the validate command for the JSON to Excel Conversion Tool CLI.

This module provides functionality to validate JSON files for syntax, structure, and complexity
without performing the full conversion to Excel. It helps users identify potential issues with
their JSON files before attempting conversion.
"""

import os  # v: built-in
import json  # v: built-in
import time  # v: built-in
from typing import Dict, List, Any, Optional  # v: built-in

from ..models.command_options import CommandOptions
from ..models.cli_response import CLIResponse, ResponseType
from ...backend.validators.json_validator import JSONValidator
from ...backend.models.json_data import JSONData
from ...backend.input_handler import InputHandler
from ...backend.models.error_response import ErrorResponse

from ..utils.path_utils import normalize_cli_path, validate_input_file
from ..utils.console_utils import (
    print_info,
    print_success,
    print_error,
    print_warning,
    format_file_size,
    ProgressSpinner
)

# Initialize global instances
json_validator = JSONValidator()
input_handler = InputHandler()

def execute_validate_command(options: CommandOptions) -> CLIResponse:
    """
    Executes the validate command to check JSON file syntax, structure, and complexity.
    
    Args:
        options: Command options provided by the user
        
    Returns:
        CLIResponse: Response object containing validation results or error information
    """
    # Check if input file is provided
    if not options.input_file:
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message="Input file is required for validate command",
            error=ErrorResponse(
                message="Input file is required",
                error_code="CLI_ERROR",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="CLI"
            )
        )
    
    # Normalize and validate the input file path
    input_file = normalize_cli_path(options.input_file)
    if not validate_input_file(input_file, options.verbose):
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Invalid input file: {input_file}",
            error=ErrorResponse(
                message=f"Invalid input file: {input_file}",
                error_code="FILE_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="CLI"
            )
        )
    
    # Show processing indicator
    spinner = ProgressSpinner(f"Validating JSON file: {input_file}")
    spinner.start()
    
    # Record start time for performance measurement
    start_time = time.time()
    
    try:
        # Read the JSON file
        file_info = input_handler.get_file_info(input_file)
        file_size = file_info['size']
        formatted_size = format_file_size(file_size)
        
        # Get the JSON data and analyze it
        json_data = input_handler.get_json_data(input_file)
        
        # Get structure information
        structure_info = json_data.structure_info
        
        # Get warnings that might affect conversion
        warnings = json_validator.get_validation_warnings(json_data)
        
        # Stop the spinner
        spinner.stop()
        
        # Calculate validation time
        validation_time = time.time() - start_time
        
        # Format the validation results
        validation_result = format_validation_result(structure_info, warnings, options.verbose)
        
        # Display the validation results if verbose mode is enabled
        if options.verbose:
            display_validation_results(validation_result, options.verbose)
        
        # Create successful response
        response = CLIResponse(
            response_type=ResponseType.SUCCESS,
            message=f"JSON file is valid: {input_file}",
            data=validation_result
        )
        
        # Add metadata
        response.add_metadata("file_path", input_file)
        response.add_metadata("file_size", file_size)
        response.add_metadata("file_size_formatted", formatted_size)
        response.add_metadata("validation_time", validation_time)
        response.add_metadata("warnings_count", len(warnings))
        
        return response
        
    except Exception as e:
        # Stop the spinner
        spinner.stop()
        
        # Handle error case
        error_message = str(e)
        if options.verbose:
            print_error(f"Error validating JSON file: {error_message}")
        
        # Create error response
        if isinstance(e, ErrorResponse):
            error = e
        else:
            error = ErrorResponse(
                message=f"Error validating JSON file: {error_message}",
                error_code="VALIDATION_ERROR",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="JSONValidator"
            )
        
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Failed to validate JSON file: {error_message}",
            error=error
        )

def format_validation_result(structure_info: Dict[str, Any], warnings: List[Dict[str, Any]], verbose: bool) -> Dict[str, Any]:
    """
    Formats the validation results into a user-friendly structure for display.
    
    Args:
        structure_info: Information about the JSON structure
        warnings: List of warnings from validation
        verbose: Whether to include detailed information
        
    Returns:
        Dict[str, Any]: Formatted validation results
    """
    result = {
        "valid": True,
        "structure": {
            "is_nested": structure_info.get("is_nested", False),
            "max_nesting_level": structure_info.get("max_nesting_level", 0),
            "contains_arrays": structure_info.get("contains_arrays", False),
            "array_count": structure_info.get("array_count", 0),
            "complexity_level": structure_info.get("complexity_level", "SIMPLE")
        },
        "warnings": warnings
    }
    
    # Add more detailed information if verbose mode is enabled
    if verbose:
        result["structure"]["array_paths"] = structure_info.get("array_paths", [])
        result["structure"]["complexity_score"] = structure_info.get("complexity_score", 0)
        
        # Add problematic paths if available
        problematic_paths = {}
        for warning in warnings:
            if "context" in warning and "arrays" in warning["context"]:
                if "large_arrays" not in problematic_paths:
                    problematic_paths["large_arrays"] = []
                for array_info in warning["context"]["arrays"]:
                    if "path" in array_info:
                        problematic_paths["large_arrays"].append(array_info["path"])
        
        if problematic_paths:
            result["problematic_paths"] = problematic_paths
    
    return result

def display_validation_results(results: Dict[str, Any], verbose: bool) -> None:
    """
    Displays the validation results to the console in a user-friendly format.
    
    Args:
        results: Validation results to display
        verbose: Whether to include detailed information
    """
    # Display overall result
    print_success("JSON file is valid and can be processed")
    
    # Display basic structure information
    structure = results["structure"]
    print_info(f"Structure information:")
    print_info(f"  Nested structure: {structure['is_nested']}")
    print_info(f"  Maximum nesting level: {structure['max_nesting_level']}")
    print_info(f"  Contains arrays: {structure['contains_arrays']}")
    if structure['contains_arrays']:
        print_info(f"  Array count: {structure['array_count']}")
    print_info(f"  Complexity level: {structure['complexity_level']}")
    
    # Display warnings if any
    warnings = results["warnings"]
    if warnings:
        print_warning(f"Found {len(warnings)} potential issues:")
        for i, warning in enumerate(warnings, 1):
            print_warning(f"  {i}. {warning['message']}")
            print_warning(f"     Severity: {warning['severity']}")
            print_warning(f"     Suggestion: {warning['suggestion']}")
    
    # Display additional information in verbose mode
    if verbose and "array_paths" in structure:
        print_info("Array paths:")
        for path in structure["array_paths"]:
            print_info(f"  - {path}")
        
        if "problematic_paths" in results:
            print_warning("Problematic paths detected:")
            for issue_type, paths in results["problematic_paths"].items():
                print_warning(f"  {issue_type}:")
                for path in paths:
                    print_warning(f"    - {path}")
    
    # Print a summary line
    issue_count = len(warnings)
    if issue_count == 0:
        print_success("No issues found. The JSON file should convert without problems.")
    elif issue_count < 3:
        print_warning(f"Found {issue_count} minor issues. The file should convert but may require attention.")
    else:
        print_warning(f"Found {issue_count} issues. The file may need modifications before conversion.")