"""
Implements the convert command for the JSON to Excel Conversion Tool CLI.
This module handles the conversion of JSON files to Excel format through the command-line interface,
providing user feedback, progress indication, and error handling throughout the conversion process.
"""

import os
from typing import Dict, Any

from ..models.command_options import CommandOptions
from ..models.cli_response import CLIResponse, ResponseType
from ...backend.services.conversion_service import ConversionService
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..utils.console_utils import (
    print_info, print_success, print_error, print_warning, print_processing,
    ProgressSpinner, format_file_size, format_time
)
from ..utils.path_utils import validate_input_file, validate_output_file, get_file_size
from ..utils.time_utils import ExecutionTimer
from ...backend.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

def execute_convert_command(options: CommandOptions) -> CLIResponse:
    """
    Executes the convert command to transform a JSON file into an Excel file.
    
    Args:
        options: Command-line options provided by the user
        
    Returns:
        A response object containing the result of the command execution
    """
    logger.info(f"Executing convert command: {options.input_file} -> {options.output_file}")
    
    # Validate command options
    if not options.validate():
        logger.error(f"Invalid command options: {options.error.message if options.error else 'Unknown error'}")
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message="Invalid command options",
            error=options.error
        )
    
    # Validate input file
    if not validate_input_file(options.input_file, options.verbose):
        logger.error(f"Invalid input file: {options.input_file}")
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Invalid input file: {options.input_file}",
            error=ErrorResponse(
                message=f"Invalid input file: {options.input_file}",
                error_code="CLI_ERROR",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="CLI"
            )
        )
    
    # Validate output file
    if not validate_output_file(options.output_file, options.verbose):
        logger.error(f"Invalid output file: {options.output_file}")
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Invalid output file: {options.output_file}",
            error=ErrorResponse(
                message=f"Invalid output file: {options.output_file}",
                error_code="CLI_ERROR",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="CLI"
            )
        )
    
    # Get input file size
    input_file_size = get_file_size(options.input_file)
    
    # Display initial information
    if options.verbose:
        print_info(f"Starting conversion process...")
        print_info(f"Reading JSON file: {options.input_file}")
        print_info(f"JSON file size: {format_file_size(input_file_size)}")
    else:
        print_processing(f"Converting {options.input_file} to {options.output_file}")
    
    # Create a progress spinner for visual feedback
    spinner = ProgressSpinner("Processing JSON file...")
    spinner.start()
    
    # Start the timer to measure execution time
    with ExecutionTimer() as timer:
        try:
            # Create a conversion service
            conversion_service = ConversionService()
            
            # Get Excel options from command options
            excel_options = options.get_excel_options()
            
            # Update spinner message
            spinner.update_message("Flattening nested structures...")
            
            # Execute the conversion
            success, summary, error = conversion_service.convert_json_to_excel(
                options.input_file,
                options.output_file,
                excel_options.to_dict()
            )
            
            # Stop the spinner
            spinner.stop()
            
            if success:
                # Display success message
                execution_time = summary.get("performance", {}).get("execution_time_seconds", 0)
                rows = summary.get("output", {}).get("rows", 0)
                columns = summary.get("output", {}).get("columns", 0)
                
                print_success(f"Conversion completed successfully in {format_time(execution_time)}")
                print_success(f"Created Excel file: {options.output_file}")
                
                if options.verbose:
                    print_info(f"Created {rows} rows and {columns} columns")
                    # Display detailed summary
                    display_conversion_summary(summary, options.verbose)
                
                # Create success response
                return CLIResponse(
                    response_type=ResponseType.SUCCESS,
                    message=f"Successfully converted {options.input_file} to {options.output_file}",
                    data=summary
                )
            else:
                # Display error message
                if error:
                    print_error(error.get_user_message())
                else:
                    print_error("Conversion failed with unknown error")
                
                # Create error response
                return CLIResponse(
                    response_type=ResponseType.ERROR,
                    message="Conversion failed",
                    error=error,
                    data=summary
                )
        except Exception as e:
            # Stop the spinner in case of exception
            spinner.stop()
            
            # Log the exception
            logger.exception(f"Unexpected error during conversion: {str(e)}")
            
            # Display error message
            print_error(f"Conversion failed: {str(e)}")
            
            # Create error response
            return CLIResponse(
                response_type=ResponseType.ERROR,
                message=f"Conversion failed: {str(e)}",
                error=ErrorResponse(
                    message=f"Unexpected error during conversion: {str(e)}",
                    error_code="UNKNOWN_ERROR",
                    category=ErrorCategory.SYSTEM_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
            )
        finally:
            # Ensure the spinner is stopped
            if spinner.is_active():
                spinner.stop()

def display_conversion_summary(summary: Dict[str, Any], verbose: bool) -> None:
    """
    Displays a summary of the conversion process with statistics.
    
    Args:
        summary: Dictionary containing conversion summary information
        verbose: Whether to display detailed information
    """
    # Extract key statistics
    input_file = summary.get("input", {}).get("file_path", "")
    input_size = summary.get("input", {}).get("size_bytes", 0)
    output_file = summary.get("output", {}).get("file_path", "")
    output_size = summary.get("output", {}).get("size_bytes", 0)
    rows = summary.get("output", {}).get("rows", 0)
    columns = summary.get("output", {}).get("columns", 0)
    execution_time = summary.get("performance", {}).get("execution_time_seconds", 0)
    
    # Display conversion summary section
    print_info("Conversion Summary:")
    print_info(f"  - Input file: {input_file}")
    print_info(f"  - Output file: {output_file}")
    print_info(f"  - Execution time: {format_time(execution_time)}")
    
    # Display additional details if verbose
    if verbose:
        # JSON structure information
        json_structure = summary.get("input", {}).get("structure", {})
        nesting_level = json_structure.get("nesting_level", 0)
        contains_arrays = json_structure.get("contains_arrays", False)
        array_count = json_structure.get("array_count", 0)
        complexity = json_structure.get("complexity", "")
        
        print_info("\nJSON Structure Information:")
        print_info(f"  - Nesting level: {nesting_level}")
        print_info(f"  - Contains arrays: {contains_arrays}")
        if contains_arrays:
            print_info(f"  - Array count: {array_count}")
        print_info(f"  - Complexity: {complexity}")
        
        # Data statistics
        print_info("\nData Statistics:")
        print_info(f"  - Rows: {rows}")
        print_info(f"  - Columns: {columns}")
        
        # File size information
        input_size_formatted = format_file_size(input_size)
        output_size_formatted = format_file_size(output_size)
        size_ratio = (output_size / input_size) if input_size > 0 else 0
        
        print_info("\nFile Size Information:")
        print_info(f"  - Input size: {input_size_formatted}")
        print_info(f"  - Output size: {output_size_formatted}")
        print_info(f"  - Size ratio: {size_ratio:.2f}x")
        
        # Performance metrics
        rows_per_second = summary.get("performance", {}).get("rows_per_second", 0)
        
        print_info("\nPerformance Metrics:")
        print_info(f"  - Execution time: {format_time(execution_time)}")
        print_info(f"  - Rows per second: {rows_per_second:.2f}")