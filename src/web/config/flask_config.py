import os
from dotenv import load_dotenv  # python-dotenv 0.19.0+
import json

# Calculate the base directory (parent directory of the current file's directory)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Load upload_config.json
upload_config_path = os.path.join(os.path.dirname(__file__), 'upload_config.json')
with open(upload_config_path, 'r') as f:
    upload_config = json.load(f)

# Load web_interface_config.json
web_interface_config_path = os.path.join(os.path.dirname(__file__), 'web_interface_config.json')
with open(web_interface_config_path, 'r') as f:
    web_interface_config = json.load(f)


class BaseConfig:
    """Base configuration class with common settings for all environments"""
    # Secret key for session management - use environment variable or default
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
    
    # Debug and testing flags - defaults to False
    DEBUG = False
    TESTING = False
    
    # File upload settings from upload_config.json or environment variables
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', upload_config.get('upload_folder', './uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', str(upload_config.get('max_file_size', 5242880))))
    ALLOWED_EXTENSIONS = upload_config.get('allowed_extensions', ['.json'])
    
    # Security settings from web_interface_config.json or environment variables
    WTF_CSRF_ENABLED = web_interface_config.get('security', {}).get('csrf_protection', True)
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 
                                       str(web_interface_config.get('security', {}).get('session_timeout', 30))))
    
    # Logging settings - default to INFO
    LOG_LEVEL = os.environ.get('LOG_LEVEL', web_interface_config.get('logging', {}).get('level', 'INFO'))


class DevelopmentConfig(BaseConfig):
    """Configuration class for development environment"""
    # Enable debug mode for development
    DEBUG = True


class TestingConfig(BaseConfig):
    """Configuration class for testing environment"""
    # Enable testing mode
    TESTING = True
    DEBUG = True
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Use a test-specific upload folder
    UPLOAD_FOLDER = os.path.join(basedir, 'tests', 'uploads')


class ProductionConfig(BaseConfig):
    """Configuration class for production environment"""
    # Disable debug mode for production
    DEBUG = False
    
    # Ensure CSRF protection is enabled for production
    WTF_CSRF_ENABLED = True
    
    # Set default log level to WARNING for production
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    @classmethod
    def init_app(cls, app):
        """Initialize the application with production-specific settings"""
        # Ensure SECRET_KEY is properly set for production
        if app.config['SECRET_KEY'] == 'default-secret-key-for-development':
            raise ValueError("Production environment must have SECRET_KEY set in environment variables")


def get_config(config_name):
    """
    Returns the appropriate configuration class based on the environment name
    
    Args:
        config_name (str): Name of the environment configuration to use
        
    Returns:
        object: Configuration class for the specified environment
    """
    # Load environment variables from .env file if it exists
    load_dotenv(os.path.join(basedir, '.env'))
    
    # Map environment names to configuration classes
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    # Return the configuration class for the specified environment name
    # Default to DevelopmentConfig if the specified environment is not found
    return config_map.get(config_name, DevelopmentConfig)