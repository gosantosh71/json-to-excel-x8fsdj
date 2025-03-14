"""
Main entry point for the JSON to Excel Conversion Tool's command-line interface.
This module provides the executable script that users interact with to convert JSON files to Excel format through the command line, handling argument parsing, command execution, and result display.
"""

import sys  # v: built-in
import os  # v: built-in
from typing import List  # v: built-in

from .argument_parser import parse_args  # ./argument_parser
from .command_runner import main as run_cli  # ./command_runner
from .console_logger import ConsoleLogger, is_verbose_mode  # ./console_logger
from .help_text import VERSION, TOOL_NAME  # ./help_text

# Initialize logger
logger = ConsoleLogger(__name__, verbose=is_verbose_mode(None))


def main() -> int:
    """
    Main entry point function for the CLI application.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Display welcome message with tool name and version
    logger.info(f"{TOOL_NAME} v{VERSION}")

    try:
        # Try to execute the CLI with sys.argv[1:] using run_cli()
        exit_code = run_cli(sys.argv[1:])
        return exit_code
    except Exception as e:
        # Catch any unexpected exceptions and log them
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        return 1  # Return exit code 1 if an exception occurred


def display_welcome() -> None:
    """
    Displays a welcome message with tool information.
    """
    # Log an info message with the tool name and version
    logger.info(f"Starting {TOOL_NAME} v{VERSION}")

    # If verbose mode is enabled, display additional information about the tool
    if logger.is_verbose():
        logger.debug("Verbose mode is enabled")


if __name__ == "__main__":
    # Call the main function and exit with its return code
    sys.exit(main())