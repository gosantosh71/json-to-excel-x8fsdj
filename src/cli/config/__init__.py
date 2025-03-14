"""
Initializes the configuration module for the CLI component of the JSON to Excel Conversion Tool.
This module loads CLI-specific configuration from JSON files and provides access to configuration
values throughout the CLI application.
"""

import os  # v: built-in
import json  # v: built-in
import typing  # v: built-in

from ...backend.config import load_config_file
from ...backend.logger import get_logger
from ..utils.path_utils import normalize_cli_path

# Initialize logger
logger = get_logger(__name__)

# Path to CLI configuration file
CLI_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'cli_config.json')

def load_cli_config() -> dict:
    """
    Loads the CLI-specific configuration from the JSON file.
    
    Returns:
        dict: CLI configuration dictionary
    """
    try:
        # Normalize the path to the CLI configuration file
        config_path = normalize_cli_path(CLI_CONFIG_PATH)
        logger.debug(f"Loading CLI configuration from: {config_path}")
        
        # Load the configuration using load_config_file from backend.config
        config = load_config_file(config_path)
        
        # Log the successful loading of the configuration
        if config:
            logger.info("CLI configuration loaded successfully")
        else:
            logger.warning("CLI configuration not found or empty, using defaults")
            # Provide basic defaults
            config = {
                "commands": {},
                "options": {},
                "display": {},
                "examples": {},
                "performance": {}
            }
        
        return config
        
    except Exception as e:
        # Handle any exceptions during loading and return a default configuration
        logger.error(f"Failed to load CLI configuration: {str(e)}")
        logger.warning("Using default CLI configuration")
        
        # Return a minimal default configuration
        return {
            "commands": {},
            "options": {},
            "display": {},
            "examples": {},
            "performance": {}
        }

# Load CLI configuration
cli_config = load_cli_config()

def get_command_config(command_name: str) -> dict:
    """
    Gets the configuration for a specific command.
    
    Args:
        command_name: Name of the command
        
    Returns:
        dict: Command configuration or empty dict if not found
    """
    # Check if the command exists in cli_config['commands']
    if 'commands' in cli_config and command_name in cli_config['commands']:
        return cli_config['commands'][command_name]
    
    # If not, log a warning and return an empty dictionary
    logger.warning(f"Configuration for command '{command_name}' not found")
    return {}

def get_option_config(option_name: str) -> dict:
    """
    Gets the configuration for a specific command-line option.
    
    Args:
        option_name: Name of the option
        
    Returns:
        dict: Option configuration or empty dict if not found
    """
    # Check if the option exists in cli_config['options']
    if 'options' in cli_config and option_name in cli_config['options']:
        return cli_config['options'][option_name]
    
    # If not, log a warning and return an empty dictionary
    logger.warning(f"Configuration for option '{option_name}' not found")
    return {}

def get_display_config(section: typing.Optional[str] = None) -> dict:
    """
    Gets the display configuration or a specific section of it.
    
    Args:
        section: Section name or None for entire display config
        
    Returns:
        dict: Display configuration or section
    """
    # If section is None, return the entire display configuration
    if section is None:
        return cli_config.get('display', {})
    
    # If section is provided, check if it exists in cli_config['display']
    display_config = cli_config.get('display', {})
    if section in display_config:
        return display_config[section]
    
    # If not, log a warning and return an empty dictionary
    logger.warning(f"Display configuration section '{section}' not found")
    return {}

def get_examples(example_type: typing.Optional[str] = None) -> list:
    """
    Gets the command examples from the configuration.
    
    Args:
        example_type: Type of examples to retrieve or None for all
        
    Returns:
        list: List of command examples
    """
    examples = cli_config.get('examples', {})
    
    # If example_type is None, return all examples as a flattened list
    if example_type is None:
        # Flatten all example lists into a single list
        all_examples = []
        for example_list in examples.values():
            if isinstance(example_list, list):
                all_examples.extend(example_list)
        return all_examples
    
    # If example_type is provided, check if it exists in cli_config['examples']
    if example_type in examples:
        return examples[example_type]
    
    # If not, log a warning and return an empty list
    logger.warning(f"Examples of type '{example_type}' not found")
    return []

def reload_cli_config() -> dict:
    """
    Reloads the CLI configuration from the JSON file.
    
    Returns:
        dict: Updated CLI configuration dictionary
    """
    global cli_config
    # Call load_cli_config() to reload the configuration
    cli_config = load_cli_config()
    
    # Log the configuration reload
    logger.info("CLI configuration reloaded")
    
    # Return the updated configuration
    return cli_config