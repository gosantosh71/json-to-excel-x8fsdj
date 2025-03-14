"""
Provides a centralized logging system for the JSON to Excel Conversion Tool.

This module configures Python's built-in logging system according to the application's
logging configuration, implements custom log filters, and exposes utility functions
for obtaining loggers and logging exceptions with detailed context.
"""

import logging  # v: built-in
import logging.config  # v: built-in
import os  # v: built-in
import sys  # v: built-in
import traceback  # v: built-in
import typing  # v: built-in
import re  # v: built-in
import json  # v: built-in
from pathlib import Path  # v: built-in

from .constants import CONFIG_ENV_PREFIX

# Global variables
_logging_initialized = False
_root_logger = logging.getLogger()
DEFAULT_LOGGING_CONFIG_PATH = "src/backend/config/logging_config.json"


def load_logging_config(config_path: typing.Optional[str] = None) -> dict:
    """
    Loads logging configuration from the logging config file.
    
    Args:
        config_path: Optional path to the configuration file. If not provided,
                    the default path will be used.
                    
    Returns:
        Dictionary containing the logging configuration.
    """
    config_path = config_path or DEFAULT_LOGGING_CONFIG_PATH
    config_file = Path(config_path)
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in logging config file {config_path}: {str(e)}")
    else:
        print(f"Warning: Logging configuration file not found at {config_path}.")
        
    # Return a basic default configuration if file not found or invalid
    return {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }


def initialize_logging(config_path: typing.Optional[str] = None) -> None:
    """
    Initializes the logging system using the application's logging configuration.
    
    Args:
        config_path: Optional path to the logging configuration file.
    """
    global _logging_initialized
    if _logging_initialized:
        return
    
    config = load_logging_config(config_path)
    logging.config.dictConfig(config)
    _logging_initialized = True
    
    # Get the root logger and set a debug message
    logger = logging.getLogger()
    logger.debug("Logging system initialized")
    
    # Apply environment-based log level if set
    env_level = get_environment_log_level()
    if env_level is not None:
        logger.setLevel(env_level)
        logger.debug(f"Log level set from environment: {logging.getLevelName(env_level)}")


def get_logger(name: str) -> logging.Logger:
    """
    Gets a logger instance for a specific module or component.
    
    Args:
        name: The name of the logger, typically __name__ of the calling module
        
    Returns:
        Logger instance for the specified name
    """
    # Ensure logging is initialized
    if not _logging_initialized:
        initialize_logging()
    
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, exception: Exception, message: str, context: typing.Optional[dict] = None) -> None:
    """
    Logs an exception with detailed context information.
    
    Args:
        logger: The logger to use
        exception: The exception to log
        message: A message describing what happened
        context: Optional dictionary of additional context information
    """
    exc_info = sys.exc_info()
    
    # Format the traceback
    tb_lines = traceback.format_exception(*exc_info)
    tb_text = ''.join(tb_lines)
    
    # Build the error message
    error_message = f"{message}\n"
    error_message += f"Exception Type: {type(exception).__name__}\n"
    error_message += f"Exception Message: {str(exception)}\n"
    
    # Add context if provided
    if context:
        error_message += "Context:\n"
        for key, value in context.items():
            error_message += f"  {key}: {value}\n"
    
    # Add the traceback
    error_message += f"Traceback:\n{tb_text}"
    
    # Log the error
    logger.error(error_message)


def get_log_level_from_string(level_name: str) -> int:
    """
    Converts a string log level name to a logging level constant.
    
    Args:
        level_name: The name of the log level (case-insensitive)
        
    Returns:
        The corresponding logging level constant (e.g., logging.INFO)
    """
    level_name = level_name.upper()
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return level_map.get(level_name, logging.INFO)


def set_log_level(level: int, logger_name: typing.Optional[str] = None) -> None:
    """
    Sets the log level for a specific logger or all loggers.
    
    Args:
        level: The log level to set (e.g., logging.INFO)
        logger_name: Optional logger name. If not provided, sets the root logger level.
    """
    # Ensure logging is initialized
    if not _logging_initialized:
        initialize_logging()
    
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = _root_logger
    
    logger.setLevel(level)
    logger.debug(f"Log level set to: {logging.getLevelName(level)}")


def get_environment_log_level() -> typing.Optional[int]:
    """
    Gets the log level from environment variable if set.
    
    Returns:
        The log level constant or None if not set
    """
    env_var_name = f"{CONFIG_ENV_PREFIX}LOG_LEVEL"
    level_str = os.environ.get(env_var_name)
    
    if level_str:
        return get_log_level_from_string(level_str)
    
    return None


class SensitiveDataFilter(logging.Filter):
    """
    A logging filter that masks sensitive information in log messages.
    """
    
    def __init__(self, sensitive_fields: typing.Optional[list] = None, mask_pattern: str = "***"):
        """
        Initializes a new SensitiveDataFilter instance.
        
        Args:
            sensitive_fields: List of field names to mask in log messages
            mask_pattern: String to use as a replacement for sensitive values
        """
        super().__init__()
        
        # Default list of sensitive fields if not provided
        self.sensitive_fields = sensitive_fields or [
            "password", "api_key", "token", "secret", "credential", 
            "authorization", "auth", "key", "pwd", "passwd"
        ]
        self.mask_pattern = mask_pattern
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filters a log record by masking sensitive information.
        
        Args:
            record: The LogRecord to filter
            
        Returns:
            True to include the record in the log output
        """
        if isinstance(record.msg, str):
            record.msg = self.mask_sensitive_data(record.msg)
        
        return True
    
    def mask_sensitive_data(self, text: str) -> str:
        """
        Masks sensitive data in a string.
        
        Args:
            text: The text to mask
            
        Returns:
            Text with sensitive data masked
        """
        if not isinstance(text, str):
            return text
            
        for field in self.sensitive_fields:
            # Match patterns like 'field=value'
            text = re.sub(
                rf'{field}=([^,\s)]+)', 
                f'{field}={self.mask_pattern}', 
                text
            )
            
            # Match patterns like 'field: value'
            text = re.sub(
                rf'{field}:\s*([^,\s)}]+)', 
                f'{field}: {self.mask_pattern}', 
                text
            )
            
            # Match patterns like "'field': 'value'" in JSON/dict representations
            text = re.sub(
                rf'[\'"]?{field}[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"](,)?', 
                f'\\"{field}\\":\\"{self.mask_pattern}\\"\\1', 
                text
            )
        
        return text


class LoggerAdapter(logging.LoggerAdapter):
    """
    A custom logger adapter that adds context information to log messages.
    """
    
    def __init__(self, logger: logging.Logger, extra: dict):
        """
        Initializes a new LoggerAdapter instance.
        
        Args:
            logger: The logger to adapt
            extra: Dictionary of extra context information
        """
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        """
        Processes the log message by adding context information.
        
        Args:
            msg: The log message
            kwargs: Additional keyword arguments
            
        Returns:
            Tuple of (modified_message, modified_kwargs)
        """
        # Format the message with extra context
        context_str = " ".join(f"{k}={v}" for k, v in self.extra.items())
        if context_str:
            msg = f"{msg} [{context_str}]"
        
        return msg, kwargs