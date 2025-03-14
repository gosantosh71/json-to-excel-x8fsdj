import os
import json  # built-in

# Import configuration classes and utilities from flask_config
from .flask_config import (
    BaseConfig,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    get_config
)

# Define the config directory path
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json_config(filename):
    """
    Loads a JSON configuration file from the config directory.
    
    Args:
        filename (str): Name of the JSON configuration file
        
    Returns:
        dict: Parsed JSON configuration as a dictionary
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the configuration file contains invalid JSON
    """
    try:
        config_path = os.path.join(CONFIG_DIR, filename)
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {filename} not found in {CONFIG_DIR}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in configuration file {filename}: {str(e)}", e.doc, e.pos)

# Load configuration files
upload_config = load_json_config('upload_config.json')
web_interface_config = load_json_config('web_interface_config.json')

# Export configuration classes and utilities for use by the web interface
__all__ = [
    'BaseConfig',
    'DevelopmentConfig',
    'TestingConfig',
    'ProductionConfig',
    'get_config',
    'upload_config',
    'web_interface_config',
    'load_json_config'
]