"""
Initialization module for the configuration package.

This module provides access to application settings and logging configuration.
It loads JSON configuration files, handles environment variable overrides,
and exposes configuration objects to other parts of the application.

Example:
    Accessing configuration values:
    >>> from backend.config import config
    >>> max_file_size = config['system']['max_file_size']
    
    Loading custom configuration:
    >>> from backend.config import get_config
    >>> custom_config = get_config('path/to/custom_config.json')
"""

import os  # built-in
import json  # built-in
from typing import Any, Dict, Optional  # built-in

# Constants for configuration
CONFIG_ENV_PREFIX = "JSON2EXCEL_"
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_config.json')
LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.json')


def load_config_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON configuration file.
    
    Args:
        file_path: Path to the JSON configuration file
        
    Returns:
        Parsed configuration dictionary
        
    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in configuration file {file_path}: {str(e)}", e.doc, e.pos)


def get_env_override(key: str, default: Any) -> Any:
    """
    Get an environment variable override for a configuration setting.
    
    Args:
        key: Configuration key (will be prefixed and upper-cased for env var lookup)
        default: Default value to return if no environment variable exists
        
    Returns:
        Environment variable value or default
        
    Example:
        >>> get_env_override('max_file_size', 5242880)
        # Returns value of JSON2EXCEL_MAX_FILE_SIZE if set, otherwise 5242880
    """
    env_var_name = f"{CONFIG_ENV_PREFIX}{key.upper()}"
    return os.environ.get(env_var_name, default)


def apply_env_overrides(config: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Recursively apply environment variable overrides to configuration dictionary.
    
    Args:
        config: Configuration dictionary to update
        prefix: Prefix for nested keys (used in recursion)
        
    Returns:
        Configuration with environment overrides applied
        
    Example:
        >>> apply_env_overrides({'system': {'max_file_size': 5242880}})
        # Returns config with any matching environment variables applied
    """
    if not isinstance(config, dict):
        return config
        
    result = config.copy()
    
    for key, value in config.items():
        env_key = f"{prefix}_{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively process nested dictionaries
            result[key] = apply_env_overrides(value, env_key)
        else:
            # Check for environment variable override
            env_value = get_env_override(env_key, value)
            
            # Convert env_value to the same type as the original value
            if env_value != value and isinstance(env_value, str):
                try:
                    if isinstance(value, bool):
                        # Special handling for boolean values
                        env_value = env_value.lower() in ('true', 'yes', '1')
                    elif isinstance(value, int):
                        env_value = int(env_value)
                    elif isinstance(value, float):
                        env_value = float(env_value)
                    elif isinstance(value, list):
                        # Handle comma-separated list values
                        env_value = [item.strip() for item in env_value.split(',')]
                    # String values don't need conversion
                except (ValueError, TypeError):
                    # If conversion fails, use the string value
                    pass
            
            result[key] = env_value
            
    return result


def get_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file and apply environment variable overrides.
    
    Args:
        config_path: Path to the configuration file (optional, uses default if not provided)
        
    Returns:
        Complete configuration dictionary with overrides applied
        
    Example:
        >>> config = get_config()  # Load default config
        >>> custom_config = get_config('custom_config.json')  # Load custom config
    """
    # Use provided path or default
    path = config_path if config_path else DEFAULT_CONFIG_PATH
    
    # Load base configuration
    config_data = load_config_file(path)
    
    # Apply environment variable overrides
    config_data = apply_env_overrides(config_data)
    
    return config_data


def get_logging_config(log_level: Optional[str] = None) -> Dict[str, Any]:
    """
    Load logging configuration from file and apply any overrides.
    
    Args:
        log_level: Optional log level to override all loggers
        
    Returns:
        Logging configuration dictionary
        
    Example:
        >>> logging_config = get_logging_config()  # Load default logging config
        >>> debug_config = get_logging_config('DEBUG')  # Override with DEBUG level
    """
    # Load logging configuration
    logging_config_data = load_config_file(LOGGING_CONFIG_PATH)
    
    # Override log level if provided
    if log_level:
        # Set root logger level
        if 'root' in logging_config_data:
            logging_config_data['root']['level'] = log_level
        
        # Set all other logger levels
        if 'loggers' in logging_config_data:
            for logger in logging_config_data['loggers'].values():
                if 'level' in logger:
                    logger['level'] = log_level
    
    # Apply any environment variable overrides related to logging
    logging_config_data = apply_env_overrides(logging_config_data, "LOGGING")
    
    return logging_config_data


# Load configuration on module import
try:
    config = get_config()
    logging_config = get_logging_config(config.get('system', {}).get('log_level'))
except Exception as e:
    # Provide basic configuration if loading fails
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.error(f"Failed to load configuration: {str(e)}")
    
    # Set fallback configurations
    config = {
        'system': {
            'max_file_size': 5242880,  # 5MB
            'max_nesting_level': 10,
            'temp_directory': './temp',
            'log_level': 'INFO',
            'log_file': 'json_to_excel.log'
        },
        'conversion': {
            'array_handling': 'expand',
            'default_sheet_name': 'Sheet1',
            'excel_format': 'xlsx'
        },
        'web_interface': {
            'enabled': False,
            'port': 5000,
            'host': '127.0.0.1',
            'upload_folder': './uploads',
            'max_upload_size': 5242880
        }
    }
    
    logging_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }

# Ensure exports are clearly defined for importers
__all__ = ['config', 'logging_config', 'get_config', 'get_logging_config']