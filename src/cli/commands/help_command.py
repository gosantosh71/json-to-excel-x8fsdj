"""
Implements the help command functionality for the JSON to Excel Conversion Tool's command-line interface.
This module provides detailed help information about the tool and its commands, including usage instructions,
available options, and examples.
"""

import typing

from ..models.command_options import CommandOptions, CommandType
from ..models.cli_response import CLIResponse, ResponseType
from ..help_text import (
    TOOL_NAME, VERSION, HELP_TEXT, COMMAND_HELP, 
    COMMON_OPTIONS, EXAMPLES
)
from ...backend.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)


def execute_help_command(options: CommandOptions) -> CLIResponse:
    """
    Executes the help command, displaying general help information or command-specific help based on the provided options.
    
    Args:
        options: Command options provided by the user, potentially containing a specific command to get help for
        
    Returns:
        A CLIResponse object containing the help text and success status
    """
    logger.info("Executing help command")
    
    # Check if a specific command was requested
    if options.help_command:
        # Get help for the specific command
        help_text = get_command_help(options.help_command)
    else:
        # Get general help information
        help_text = get_general_help()
    
    # Return a formatted response with the help text
    return CLIResponse(
        response_type=ResponseType.INFO,
        message=help_text,
        data={"help_text": help_text}
    )


def get_general_help() -> str:
    """
    Generates general help information about the tool, including a list of available commands.
    
    Returns:
        Formatted general help text
    """
    # Create sections of the help text
    sections = []
    
    # Add tool name and version header
    sections.append(f"{TOOL_NAME} v{VERSION}")
    sections.append("=" * len(f"{TOOL_NAME} v{VERSION}"))
    
    # Add general description
    sections.append(HELP_TEXT["description"])
    
    # Add usage information
    sections.append("\nUsage:")
    sections.append(f"  {HELP_TEXT['usage']}")
    
    # Add available commands section
    sections.append("\nAvailable Commands:")
    for command_type in CommandType:
        command_info = COMMAND_HELP.get(command_type.value, {})
        if command_info:
            description = command_info.get("description", "")
            sections.append(f"  {command_type.value.lower():<10} {description}")
    
    # Add common options section
    common_options_text = format_options_section(COMMON_OPTIONS)
    if common_options_text:
        sections.append(f"\nCommon Options:")
        sections.append(common_options_text)
    
    # Add information on how to get command-specific help
    sections.append(f"\n{HELP_TEXT['general']}")
    
    # Join all sections into a single text
    return "\n".join(sections)


def get_command_help(command_name: str) -> str:
    """
    Generates detailed help information for a specific command.
    
    Args:
        command_name: The name of the command to get help for
        
    Returns:
        Formatted command-specific help text
    """
    # Convert command name to uppercase for matching with CommandType
    command_upper = command_name.upper()
    
    # Check if the command exists
    try:
        command_type = CommandType(command_upper)
    except ValueError:
        return f"Unknown command: {command_name}\n\nRun 'python json_to_excel.py help' for a list of available commands."
    
    # Get command help information
    command_help = COMMAND_HELP.get(command_type.value, {})
    if not command_help:
        return f"No help available for command: {command_name}"
    
    # Create sections of the help text
    sections = []
    
    # Add command name header
    sections.append(f"Command: {command_name}")
    sections.append("=" * len(f"Command: {command_name}"))
    
    # Add command description
    description = command_help.get("description", "")
    if description:
        sections.append(description)
    
    # Add command usage
    usage = command_help.get("usage", "")
    if usage:
        sections.append("\nUsage:")
        sections.append(f"  {usage}")
    
    # Add command-specific options
    options = command_help.get("options", {})
    options_text = format_options_section(options)
    if options_text:
        sections.append("\nCommand Options:")
        sections.append(options_text)
    
    # Add common options
    common_options_text = format_options_section(COMMON_OPTIONS)
    if common_options_text:
        sections.append("\nCommon Options:")
        sections.append(common_options_text)
    
    # Add examples
    examples_list = EXAMPLES.get(command_type.value, [])
    examples_text = format_examples_section(examples_list)
    if examples_text:
        sections.append("\nExamples:")
        sections.append(examples_text)
    
    # Join all sections into a single text
    return "\n".join(sections)


def format_options_section(options: dict) -> str:
    """
    Formats a section of command options for display in the help text.
    
    Args:
        options: Dictionary of option names and descriptions
        
    Returns:
        Formatted options section
    """
    if not options:
        return ""
    
    formatted_lines = []
    
    # Format each option with proper indentation
    for option, description in options.items():
        # Indent and align option descriptions
        formatted_lines.append(f"  {option:<20} {description}")
    
    return "\n".join(formatted_lines)


def format_examples_section(examples: list) -> str:
    """
    Formats a section of command examples for display in the help text.
    
    Args:
        examples: List of example command lines
        
    Returns:
        Formatted examples section
    """
    if not examples:
        return ""
    
    formatted_lines = []
    
    # Format each example with proper indentation
    for example in examples:
        formatted_lines.append(f"  {example}")
    
    return "\n".join(formatted_lines)