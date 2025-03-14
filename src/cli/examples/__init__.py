"""
Examples package for the CLI module of the JSON to Excel Conversion Tool.

This package provides programmatic access to example documentation files
that demonstrate how to use the JSON to Excel Conversion Tool from the
command line.
"""

import os.path  # version: standard library

# Version information
__version__ = "1.0.0"

# Constants
EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_FILES = ["basic_usage.md", "advanced_usage.md", "batch_processing.md", "error_handling.md"]


def get_example_path(filename: str) -> str:
    """
    Returns the absolute path to a specific example file.
    
    Args:
        filename: The name of the example file.
        
    Returns:
        The absolute path to the example file.
        
    Raises:
        ValueError: If the requested filename is not in the list of available examples.
        FileNotFoundError: If the requested example file doesn't exist.
    """
    # Validate that the requested filename is in the list of available examples
    if filename not in EXAMPLE_FILES:
        raise ValueError(f"Example file '{filename}' not found. Available examples: {', '.join(EXAMPLE_FILES)}")
    
    # Construct the absolute path to the example file
    example_path = os.path.join(EXAMPLES_DIR, filename)
    
    # Check if the file exists
    if not os.path.exists(example_path):
        raise FileNotFoundError(f"Example file '{filename}' not found at path: {example_path}")
    
    return example_path


def get_example_content(filename: str) -> str:
    """
    Returns the content of a specific example file as a string.
    
    Args:
        filename: The name of the example file.
        
    Returns:
        The content of the example file as a string.
        
    Raises:
        ValueError: If the requested filename is not in the list of available examples.
        FileNotFoundError: If the requested example file doesn't exist.
        IOError: If there's an error reading the file.
    """
    # Get the path to the example file
    example_path = get_example_path(filename)
    
    # Open the file and read its contents
    try:
        with open(example_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise IOError(f"Error reading example file '{filename}': {str(e)}")


def list_examples() -> list:
    """
    Returns a list of available example files.
    
    Returns:
        A list of example filenames.
    """
    return EXAMPLE_FILES.copy()  # Return a copy to prevent modification of the original