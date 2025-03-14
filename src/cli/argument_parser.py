"""
Implements the command-line argument parser for the JSON to Excel Conversion Tool.

This module is responsible for parsing and validating command-line arguments,
converting them into structured CommandOptions objects, and providing helpful
error messages for invalid inputs.
"""

import argparse  # v: built-in
import sys  # v: built-in
import os  # v: built-in
from typing import List, Dict, Optional, Tuple, Any  # v: built-in
import json  # v: built-in

from .models.command_options import CommandOptions, CommandType
from .models.cli_response import CLIResponse, ResponseType
from .utils.path_utils import validate_input_file, validate_output_file, normalize_cli_path
from ..backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from .help_text import TOOL_NAME, VERSION, HELP_TEXT, COMMAND_HELP, COMMON_OPTIONS, EXAMPLES
from ..backend.constants import ERROR_CODES

# Initialize logger
logger = get_logger(__name__)


class ArgumentParser(argparse.ArgumentParser):
    """
    Custom ArgumentParser class that overrides error handling to provide more user-friendly error messages.
    """
    
    def __init__(self, **kwargs):
        """Initializes a new ArgumentParser instance with custom error handling."""
        super().__init__(**kwargs)
    
    def error(self, message: str) -> None:
        """
        Custom error handler that provides user-friendly error messages and exits gracefully.
        
        Args:
            message: The error message from argparse
        """
        # Format error message for better readability
        formatted_message = f"Error: {message}"
        print(formatted_message, file=sys.stderr)
        print(f"Try '{os.path.basename(sys.argv[0])} --help' for more information.", file=sys.stderr)
        sys.exit(2)
    
    def print_help(self, file=None):
        """
        Custom help printer that formats help text in a more readable way.
        
        Args:
            file: File to print the help text to (default: stdout)
        """
        # Get standard help text from parent class
        help_text = super().format_help()
        
        # Format with tool name and version
        formatted_help = f"{TOOL_NAME} v{VERSION}\n{'-' * len(TOOL_NAME + ' v' + VERSION)}\n\n{help_text}"
        
        # Print to the specified file or stdout
        if file is None:
            file = sys.stdout
        print(formatted_help, file=file)


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for the CLI application.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser instance
    """
    # Create main parser
    parser = ArgumentParser(
        description=HELP_TEXT["description"],
        add_help=False  # We'll add a custom help option
    )
    
    # Add version argument
    parser.add_argument('--version', action='version', version=f'{TOOL_NAME} v{VERSION}')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # CONVERT command
    convert_parser = subparsers.add_parser(
        'convert', 
        help=COMMAND_HELP["CONVERT"]["description"],
        add_help=False
    )
    convert_parser.add_argument('input_file', help=COMMAND_HELP["CONVERT"]["options"]["input_json_file"])
    convert_parser.add_argument('output_file', help=COMMAND_HELP["CONVERT"]["options"]["output_excel_file"])
    convert_parser.add_argument('--sheet-name', help=COMMAND_HELP["CONVERT"]["options"]["--sheet-name NAME"])
    convert_parser.add_argument(
        '--array-handling', 
        choices=['expand', 'join'],
        help=COMMAND_HELP["CONVERT"]["options"]["--array-handling MODE"]
    )
    convert_parser.add_argument(
        '--chunk-size', 
        type=int,
        help=COMMAND_HELP["CONVERT"]["options"]["--chunk-size SIZE"]
    )
    convert_parser.add_argument(
        '--fields', 
        help=COMMAND_HELP["CONVERT"]["options"]["--fields FIELDS"]
    )
    
    # VALIDATE command
    validate_parser = subparsers.add_parser(
        'validate', 
        help=COMMAND_HELP["VALIDATE"]["description"],
        add_help=False
    )
    validate_parser.add_argument('input_file', help=COMMAND_HELP["VALIDATE"]["options"]["input_json_file"])
    
    # INFO command
    info_parser = subparsers.add_parser(
        'info', 
        help=COMMAND_HELP["INFO"]["description"],
        add_help=False
    )
    info_parser.add_argument('input_file', help=COMMAND_HELP["INFO"]["options"]["input_json_file"])
    info_parser.add_argument(
        '--format', 
        choices=['text', 'json'],
        default='text',
        help=COMMAND_HELP["INFO"]["options"]["--format FORMAT"]
    )
    
    # HELP command
    help_parser = subparsers.add_parser(
        'help', 
        help=COMMAND_HELP["HELP"]["description"],
        add_help=False
    )
    help_parser.add_argument(
        'help_command', 
        nargs='?',
        help=COMMAND_HELP["HELP"]["options"]["command"]
    )
    
    # Add common options to all subparsers
    for subparser in [convert_parser, validate_parser, info_parser, help_parser]:
        subparser.add_argument('--verbose', action='store_true', help=COMMON_OPTIONS["--verbose"])
        subparser.add_argument('--help', action='store_true', help=COMMON_OPTIONS["--help"])
    
    return parser


def parse_args(args: List[str]) -> Tuple[CommandOptions, Optional[CLIResponse]]:
    """
    Parses command-line arguments and converts them to a CommandOptions object.
    
    Args:
        args: List of command-line arguments
        
    Returns:
        Tuple[CommandOptions, Optional[CLIResponse]]: Parsed command options and response (if error)
    """
    # Create the argument parser
    parser = create_parser()
    
    # If no args provided, show help and return
    if not args:
        # Handle empty arguments as a request for help
        return handle_help_command(parser, None)
    
    try:
        # Parse the arguments
        parsed_args = parser.parse_args(args)
        
        # Handle special case for help command
        if parsed_args.command == 'help':
            return handle_help_command(parser, parsed_args.help_command)
            
        # Handle case where --help is specified
        if hasattr(parsed_args, 'help') and parsed_args.help:
            return handle_help_command(parser, parsed_args.command)
        
        # Convert args to dict for CommandOptions
        args_dict = vars(parsed_args)
        
        # Map command string to CommandType enum
        command_str = args_dict.pop('command', 'HELP').upper()
        args_dict['command'] = command_str
        
        # Create CommandOptions object
        options = CommandOptions.from_dict(args_dict)
        
        # Validate the options
        valid, error_response = validate_args(args_dict)
        if not valid:
            options.error = error_response
            
            # Create a CLI response with the error
            cli_response = CLIResponse(
                response_type=ResponseType.ERROR,
                message=error_response.message,
                error=error_response
            )
            
            return options, cli_response
        
        # Return the options and no response (success)
        return options, None
        
    except SystemExit:
        # Handle argparse's built-in exit (e.g., from --help)
        sys.exit(0)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Failed to parse command-line arguments: {str(e)}", exc_info=True)
        
        error_response = ErrorResponse(
            message=f"Failed to parse command-line arguments: {str(e)}",
            error_code=ERROR_CODES["INVALID_FILE_TYPE"],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="CLI"
        )
        
        # Create options with error
        options = CommandOptions(
            command=CommandType.HELP,
            error=error_response
        )
        
        # Create a CLI response with the error
        cli_response = CLIResponse(
            response_type=ResponseType.ERROR,
            message=error_response.message,
            error=error_response
        )
        
        return options, cli_response


def handle_help_command(parser: argparse.ArgumentParser, command: Optional[str]) -> Tuple[CommandOptions, CLIResponse]:
    """
    Handles the help command, generating appropriate help text for the specified command or general help.
    
    Args:
        parser: ArgumentParser instance
        command: Optional command to get help for
        
    Returns:
        Tuple[CommandOptions, CLIResponse]: Help command options and response with help text
    """
    # Create a CommandOptions object for the HELP command
    options = CommandOptions(command=CommandType.HELP, help_command=command)
    
    # Generate the help text
    help_text = format_help_text(command)
    
    # Create a response with the help text
    response = CLIResponse(
        response_type=ResponseType.INFO,
        message=help_text
    )
    
    return options, response


def format_help_text(command: str, format_type: Optional[str] = None) -> str:
    """
    Formats help text for display, including command usage, options, and examples.
    
    Args:
        command: Command to get help for
        format_type: Optional format type (e.g., 'json')
        
    Returns:
        str: Formatted help text
    """
    # If format_type is 'json', return JSON formatted help
    if format_type == 'json':
        if command and command.upper() in COMMAND_HELP:
            help_data = COMMAND_HELP[command.upper()]
        else:
            help_data = {
                "commands": {k: {"description": v["description"]} for k, v in COMMAND_HELP.items()},
                "general": HELP_TEXT
            }
        return json.dumps(help_data, indent=2)
    
    # Format header with tool name and version
    result = f"{TOOL_NAME} v{VERSION}\n{'-' * len(TOOL_NAME + ' v' + VERSION)}\n\n"
    
    # If a specific command is requested and it exists in COMMAND_HELP
    if command and command.upper() in COMMAND_HELP:
        cmd = command.upper()
        cmd_help = COMMAND_HELP[cmd]
        
        # Add command description
        result += f"{cmd_help['description']}\n\n"
        
        # Add usage information
        result += f"USAGE:\n  {cmd_help['usage']}\n\n"
        
        # Add options
        result += "ARGUMENTS:\n"
        for arg, desc in cmd_help['options'].items():
            result += f"  {arg.ljust(20)} {desc}\n"
        
        # Add common options
        result += "\nCOMMON OPTIONS:\n"
        for opt, desc in COMMON_OPTIONS.items():
            result += f"  {opt.ljust(20)} {desc}\n"
        
        # Add examples if available
        if cmd in EXAMPLES:
            result += "\nEXAMPLES:\n"
            for example in EXAMPLES[cmd]:
                result += f"  {example}\n"
            
    else:
        # General help
        result += f"{HELP_TEXT['description']}\n\n"
        result += f"USAGE:\n  {HELP_TEXT['usage']}\n\n"
        
        # Add available commands
        result += "COMMANDS:\n"
        for cmd, details in COMMAND_HELP.items():
            result += f"  {cmd.lower().ljust(15)} {details['description']}\n"
        
        # Add general help note
        result += f"\n{HELP_TEXT['general']}\n"
    
    return result


def validate_args(args: Dict[str, Any]) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates command-line arguments for correctness and consistency.
    
    Args:
        args: Dictionary of arguments
        
    Returns:
        Tuple[bool, Optional[ErrorResponse]]: Validation result and error response if validation fails
    """
    # Extract command
    command = args.get('command', 'HELP')
    verbose = args.get('verbose', False)
    
    # Validate command-specific requirements
    if command == 'CONVERT':
        # For CONVERT, we need input_file and output_file
        input_file = args.get('input_file')
        output_file = args.get('output_file')
        
        # Validate both input and output files
        return validate_file_args(command, input_file, output_file, verbose)
        
    elif command == 'VALIDATE':
        # For VALIDATE, we need input_file
        input_file = args.get('input_file')
        
        # Validate input file only
        return validate_file_args(command, input_file, None, verbose)
        
    elif command == 'INFO':
        # For INFO, we need input_file
        input_file = args.get('input_file')
        
        # Validate input file only
        return validate_file_args(command, input_file, None, verbose)
        
    # HELP command or unrecognized command - no validation needed
    return True, None


def validate_file_args(command: str, input_file: Optional[str], output_file: Optional[str], 
                     verbose: bool) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates file arguments for existence, permissions, and correct format.
    
    Args:
        command: Command being executed
        input_file: Input file path
        output_file: Output file path
        verbose: Whether verbose output is enabled
        
    Returns:
        Tuple[bool, Optional[ErrorResponse]]: Validation result and error response if validation fails
    """
    # Validate input file if required
    if input_file and not validate_input_file(input_file, verbose=False):
        logger.error(f"Invalid input file: '{input_file}'")
        return False, ErrorResponse(
            message=f"Invalid input file: '{input_file}'",
            error_code=ERROR_CODES["INVALID_FILE_TYPE"],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="CLI"
        )
    
    # Validate output file if required
    if output_file and not validate_output_file(output_file, verbose=False):
        logger.error(f"Invalid output file: '{output_file}'")
        return False, ErrorResponse(
            message=f"Invalid output file: '{output_file}'",
            error_code=ERROR_CODES["INVALID_FILE_TYPE"],
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="CLI"
        )
    
    return True, None