"""
Configuration module for the JSON to Excel Conversion Tool web interface.

This module centralizes configuration loading from various sources including
environment variables, JSON configuration files, and default settings. It provides
a unified interface for accessing configuration throughout the web application.
"""

import os  # built-in
import json  # built-in
import logging  # built-in
from dotenv import load_dotenv  # v: 0.19.0+

from .config.flask_config import get_config
from .constants import FILE_PATHS, UPLOAD_CONSTANTS

# Set up logging
logger = logging.getLogger(__name__)

# Base directory for relative path resolution
basedir = os.path.abspath(os.path.dirname(__file__))

# Load JSON configuration files
try:
    with open(os.path.join(basedir, 'config', 'upload_config.json'), 'r') as f:
        upload_config = json.load(f)
except Exception as e:
    logger.warning(f"Failed to load upload_config.json: {e}")
    upload_config = {}

try:
    with open(os.path.join(basedir, 'config', 'web_interface_config.json'), 'r') as f:
        web_interface_config = json.load(f)
except Exception as e:
    logger.warning(f"Failed to load web_interface_config.json: {e}")
    web_interface_config = {}


def get_env_var(name, default):
    """
    Gets an environment variable with a default fallback value.
    
    Args:
        name (str): Name of the environment variable
        default (any): Default value to return if the environment variable is not set
        
    Returns:
        any: Environment variable value or default
    """
    return os.environ.get(name, default)


def get_flask_config():
    """
    Gets the appropriate Flask configuration class based on the environment.
    
    Returns:
        object: Flask configuration class instance
    """
    # Get environment name from FLASK_ENV environment variable
    env_name = get_env_var('FLASK_ENV', 'development')
    # Use get_config function from flask_config to get the appropriate configuration class
    return get_config(env_name)


def validate_config(config):
    """
    Validates critical configuration settings to ensure they are properly set.
    
    Args:
        config (dict): Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    valid = True
    
    # Check if SECRET_KEY is set and not using the default value in production
    if config.get('FLASK_ENV') == 'production' and config.get('SECRET_KEY') == 'default-secret-key-for-development':
        logger.warning("Production environment using default SECRET_KEY. This is a security risk!")
        valid = False
    
    # Verify upload folder is set and accessible
    upload_folder = config.get('UPLOAD_FOLDER')
    if not upload_folder:
        logger.warning("UPLOAD_FOLDER is not set in configuration")
        valid = False
    
    # Ensure max file size is set to a reasonable value
    max_size = config.get('MAX_CONTENT_LENGTH', 0)
    if max_size <= 0:
        logger.warning("Invalid MAX_CONTENT_LENGTH in configuration")
        valid = False
    elif max_size > 100 * 1024 * 1024:  # 100MB
        logger.warning(f"MAX_CONTENT_LENGTH is very large ({max_size / (1024*1024):.1f}MB). This might cause memory issues.")
    
    # Validate allowed extensions includes at least .json
    allowed_extensions = config.get('ALLOWED_EXTENSIONS', [])
    if not allowed_extensions or '.json' not in allowed_extensions:
        logger.warning("ALLOWED_EXTENSIONS must include '.json'")
        valid = False
    
    return valid


def ensure_directories_exist(config):
    """
    Ensures that required directories exist and are writable.
    
    Args:
        config (dict): Configuration dictionary with directory paths
    """
    # Get paths for upload, download, and temp directories
    upload_dir = config.get('UPLOAD_FOLDER')
    download_dir = config.get('DOWNLOAD_FOLDER')
    temp_dir = config.get('TEMP_FOLDER')
    
    for dir_path, dir_name in [
        (upload_dir, 'Upload'),
        (download_dir, 'Download'),
        (temp_dir, 'Temporary')
    ]:
        if not dir_path:
            logger.warning(f"{dir_name} directory path is not set")
            continue
            
        # Create each directory if it doesn't exist
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"{dir_name} directory created: {dir_path}")
            except OSError as e:
                logger.warning(f"Failed to create {dir_name.lower()} directory: {e}")
        
        # Check if directories are writable
        if not os.access(dir_path, os.W_OK):
            logger.warning(f"{dir_name} directory is not writable: {dir_path}")


def load_config():
    """
    Loads configuration from environment variables and configuration files,
    merging them into a unified configuration object.
    
    Returns:
        dict: Merged configuration dictionary with all settings
    """
    # Load environment variables from .env file if it exists
    dotenv_path = os.path.join(basedir, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logger.debug(f"Loaded environment variables from {dotenv_path}")
    
    # Get Flask configuration based on FLASK_ENV environment variable
    flask_config = get_flask_config()
    
    # Create unified configuration dictionary
    config = {
        # Flask environment and core settings
        'FLASK_ENV': get_env_var('FLASK_ENV', 'development'),
        'SECRET_KEY': get_env_var('SECRET_KEY', flask_config.SECRET_KEY),
        'DEBUG': flask_config.DEBUG,
        'TESTING': flask_config.TESTING,
        
        # File paths
        'UPLOAD_FOLDER': get_env_var('UPLOAD_FOLDER', upload_config.get('upload_folder', FILE_PATHS.get('UPLOAD_FOLDER'))),
        'DOWNLOAD_FOLDER': get_env_var('DOWNLOAD_FOLDER', FILE_PATHS.get('DOWNLOAD_FOLDER')),
        'TEMP_FOLDER': get_env_var('TEMP_FOLDER', FILE_PATHS.get('TEMP_FOLDER')),
        
        # Upload settings
        'MAX_CONTENT_LENGTH': int(get_env_var('MAX_CONTENT_LENGTH', 
                                          str(upload_config.get('max_file_size', UPLOAD_CONSTANTS.get('MAX_FILE_SIZE_BYTES', 5242880))))),
        'ALLOWED_EXTENSIONS': upload_config.get('allowed_extensions', UPLOAD_CONSTANTS.get('ALLOWED_EXTENSIONS', ['.json'])),
        
        # Security settings
        'WTF_CSRF_ENABLED': web_interface_config.get('security', {}).get('csrf_protection', True),
        'SESSION_TIMEOUT': int(get_env_var('SESSION_TIMEOUT', 
                                        str(web_interface_config.get('security', {}).get('session_timeout', 30)))),
        
        # Logging
        'LOG_LEVEL': get_env_var('LOG_LEVEL', web_interface_config.get('logging', {}).get('level', 'INFO')),
        
        # UI settings
        'UI_SETTINGS': web_interface_config.get('ui', {}),
        
        # Job management settings
        'JOB_SETTINGS': web_interface_config.get('job_management', {}),
        
        # Security settings (detailed)
        'SECURITY_SETTINGS': web_interface_config.get('security', {})
    }
    
    # Validate critical configuration settings
    if not validate_config(config):
        logger.warning("Configuration validation failed. Some settings may be incorrect.")
    
    # Ensure required directories exist
    ensure_directories_exist(config)
    
    logger.info("Configuration loaded successfully")
    return config


# Load configuration on module import
config = load_config()