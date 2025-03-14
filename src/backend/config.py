"""
Centralizes configuration management for the JSON to Excel Conversion Tool.

This module loads configuration settings from JSON files, applies environment variable overrides,
and provides a unified interface for accessing configuration values throughout the application.
"""

import os  # v: built-in
import json  # v: built-in
import typing  # v: built-in
import logging  # v: built-in

from .constants import (
    DEFAULT_CONFIG_PATH, 
    LOGGING_CONFIG_PATH, 
    CONFIG_ENV_PREFIX,
    DEFAULT_CONFIG
)
from .utils import merge_dicts, get_nested_value, set_nested_value

# Initialize logger for this module
logger = logging.getLogger(__name__)

def load_config_file(file_path: str) -> dict:
    """
    Loads and parses a JSON configuration file.
    
    Args:
        file_path: Path to the JSON configuration file
        
    Returns:
        Parsed configuration dictionary
    """
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {file_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Configuration file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file {file_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration file {file_path}: {str(e)}")
        return {}

def get_env_value(env_var: str, default_value: typing.Any) -> typing.Any:
    """
    Gets an environment variable value with type conversion.
    
    Args:
        env_var: Name of the environment variable
        default_value: Default value to return if not found (also determines type)
        
    Returns:
        Environment variable value converted to appropriate type
    """
    value = os.environ.get(env_var)
    if value is None:
        return default_value
    
    # Convert value to the same type as default_value
    try:
        if isinstance(default_value, bool):
            return value.lower() in ('true', 'yes', '1', 'y')
        elif isinstance(default_value, int):
            return int(value)
        elif isinstance(default_value, float):
            return float(value)
        elif isinstance(default_value, list):
            return value.split(',')
        else:
            return value
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert environment variable {env_var}: {str(e)}")
        return default_value

def get_env_override(key: str, default: typing.Any) -> typing.Any:
    """
    Gets an environment variable override for a configuration setting.
    
    Args:
        key: Configuration key
        default: Default value if no override exists
        
    Returns:
        Environment variable value or default
    """
    env_var = f"{CONFIG_ENV_PREFIX}{key.upper()}"
    return get_env_value(env_var, default)

def apply_env_overrides(config: dict, prefix: str = '') -> dict:
    """
    Recursively applies environment variable overrides to configuration dictionary.
    
    Args:
        config: Configuration dictionary to update
        prefix: Prefix for nested keys (used in recursion)
        
    Returns:
        Configuration with environment overrides applied
    """
    result = config.copy()
    
    for key, value in config.items():
        env_key = f"{prefix}_{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively apply overrides to nested dictionaries
            result[key] = apply_env_overrides(value, env_key)
        else:
            # Check for environment variable override
            env_value = get_env_override(env_key, value)
            if env_value != value:
                logger.debug(f"Override applied for {env_key}: {type(value).__name__}({value}) -> {type(env_value).__name__}({env_value})")
                result[key] = env_value
    
    return result

def load_config(config_path: str = None) -> dict:
    """
    Loads configuration from file and applies environment variable overrides.
    
    Args:
        config_path: Path to the configuration file (optional)
        
    Returns:
        Complete configuration dictionary with overrides applied
    """
    config_path = config_path or DEFAULT_CONFIG_PATH
    
    # Load configuration from file
    file_config = load_config_file(config_path)
    
    # Merge with default configuration (file config takes precedence)
    if not file_config:
        logger.warning(f"Using default configuration due to issues with {config_path}")
        config = DEFAULT_CONFIG.copy()
    else:
        config = merge_dicts(DEFAULT_CONFIG.copy(), file_config)
    
    # Apply environment variable overrides
    config = apply_env_overrides(config)
    
    # Log the loaded configuration (mask sensitive values)
    log_config = {}
    for section, section_config in config.items():
        if isinstance(section_config, dict):
            log_config[section] = {
                k: '***' if any(s in k.lower() for s in ['password', 'secret', 'key', 'token']) else v
                for k, v in section_config.items()
            }
        else:
            log_config[section] = section_config
    
    logger.debug(f"Loaded configuration: {log_config}")
    return config

def load_logging_config() -> dict:
    """
    Loads logging configuration from file and applies any overrides.
    
    Returns:
        Logging configuration dictionary
    """
    # Try to load from config file
    logging_config = load_config_file(LOGGING_CONFIG_PATH)
    
    # If loading failed, use a basic default configuration
    if not logging_config:
        logging_config = {
            'version': 1,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout',
                },
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console'],
            }
        }
    
    # Check for log level override from environment
    log_level = os.environ.get(f"{CONFIG_ENV_PREFIX}LOG_LEVEL")
    if log_level:
        # Update root logger level
        if 'root' in logging_config:
            logging_config['root']['level'] = log_level
        
        # Update all other logger levels
        if 'loggers' in logging_config:
            for logger_name in logging_config['loggers']:
                logging_config['loggers'][logger_name]['level'] = log_level
    
    # Apply any other environment variable overrides for logging
    logging_config = apply_env_overrides(logging_config, 'LOGGING')
    
    return logging_config

def get_config_value(path: str, default: typing.Any = None) -> typing.Any:
    """
    Gets a configuration value using dot notation path.
    
    Args:
        path: Path to the configuration value (e.g., 'system.max_file_size')
        default: Default value to return if path doesn't exist
        
    Returns:
        Configuration value or default if not found
    """
    value = get_nested_value(config, path)
    return default if value is None else value

def set_config_value(path: str, value: typing.Any) -> bool:
    """
    Sets a configuration value using dot notation path.
    
    Args:
        path: Path to the configuration value (e.g., 'system.max_file_size')
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        set_nested_value(config, path, value)
        logger.info(f"Configuration updated: {path} = {value}")
        return True
    except Exception as e:
        logger.error(f"Failed to update configuration at {path}: {str(e)}")
        return False

def reload_config() -> dict:
    """
    Reloads the configuration from file.
    
    Returns:
        Updated configuration dictionary
    """
    global config
    config = load_config()
    logger.info("Configuration reloaded")
    return config

# Initialize configuration at module level
config = load_config()
logging_config = load_logging_config()