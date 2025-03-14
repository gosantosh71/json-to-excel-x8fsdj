"""
Implements the command runner for the JSON to Excel Conversion Tool CLI.
This module is responsible for executing the appropriate command handler based on user input,
managing the command execution flow, and handling command results and errors.
"""

import sys  # v: built-in
from typing import List  # v: built-in
import traceback  # v: built-in

from .models.command_options import CommandOptions, CommandType  # ./models/command_options
from .models.cli_response import CLIResponse  # ./models/cli_response
from .models.cli_response import ResponseType  # ./models/cli_response
from .argument_parser import argument_parser  # ./argument_parser
from .commands.convert_command import execute_convert_command  # ./commands/convert_command
from .commands.validate_command import execute_validate_command  # ./commands/validate_command
from .commands.info_command import execute_info_command  # ./commands/info_command
from .commands.help_command import execute_help_command  # ./commands/help_command
from .utils.console_utils import print_cli_response, print_error  # ./utils/console_utils
from ..backend.logger import get_logger  # ../backend/logger

# Initialize logger
logger = get_logger(__name__)


def run_command(options: CommandOptions) -> CLIResponse:
    """
    Executes the appropriate command handler based on the command type in the provided options.

    Args:
        options: CommandOptions object containing the parsed command-line arguments.

    Returns:
        CLIResponse: Response from the command execution, containing the result or error information.
    """
    logger.info(f"Running command: {options.command}")

    # Check if options already contains an error
    if options.error:
        logger.warning(f"Command options contain an error: {options.error.message}")
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message="Invalid command options",
            error=options.error
        )

    # Command mapping dictionary
    command_mapping = {
        CommandType.CONVERT: execute_convert_command,
        CommandType.VALIDATE: execute_validate_command,
        CommandType.INFO: execute_info_command,
        CommandType.HELP: execute_help_command
    }

    # Get the appropriate execution function based on options.command
    execution_function = command_mapping.get(options.command)

    # Execute the command function with the options
    if execution_function:
        cli_response = execution_function(options)
    else:
        cli_response = CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Unknown command: {options.command}",
        )

    # Return the CLIResponse from the command execution
    return cli_response


def main(args: List[str]) -> int:
    """
    Main entry point for the CLI application that parses arguments and runs the appropriate command.

    Args:
        args: List of command-line arguments

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    logger.info("Starting CLI application")

    # Parse command-line arguments using argument_parser.parse_args()
    options, cli_response = argument_parser.parse_args(args)

    # If parsing returned an error response, print it and return its exit code
    if cli_response and cli_response.response_type == ResponseType.ERROR:
        print_cli_response(cli_response)
        return cli_response.get_exit_code()

    try:
        # Try to run the command using run_command() with the parsed options
        cli_response = run_command(options)

        # Print the command response using print_cli_response()
        print_cli_response(cli_response)

        # Return the exit code from the response
        return cli_response.get_exit_code()

    except Exception as e:
        # Catch and handle any unexpected exceptions:
        return handle_unexpected_error(e)


def cli_main():
    """
    Entry point for the CLI when run directly from the command line.
    """
    # Call main() with sys.argv[1:] to get the exit code
    exit_code = main(sys.argv[1:])

    # Exit the program with the returned exit code
    sys.exit(exit_code)


def handle_unexpected_error(exception: Exception) -> int:
    """
    Handles unexpected exceptions during command execution.

    Args:
        exception: The unexpected exception

    Returns:
        int: Exit code (always 1 for unexpected errors)
    """
    # Log the unexpected exception with traceback
    logger.error(f"An unexpected error occurred: {str(exception)}", exc_info=True)

    # Format a user-friendly error message
    error_message = f"An unexpected error occurred: {str(exception)}"

    # Print the error message using print_error()
    print_error(error_message)

    # Return exit code 1
    return 1