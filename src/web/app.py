import os  # v: built-in - For accessing environment variables and file paths
from dotenv import load_dotenv  # python-dotenv 0.19.0+ - For loading environment variables from .env files
from flask import Flask  # flask: 2.3.0+ - Web framework for the application

from .config.flask_config import get_config  # src/web/config/flask_config.py - For loading the appropriate Flask configuration based on environment
from .routes import register_routes  # src/web/routes.py - For registering web routes and view functions with the Flask application
from .api.error_handler import register_error_handlers  # src/web/api/error_handler.py - For registering error handlers with the Flask application
from .security.csrf_protection import CSRFProtection  # src/web/security/csrf_protection.py - For implementing CSRF protection in the web interface
from .security.request_limiter import RateLimiter  # src/web/security/request_limiter.py - For implementing rate limiting to prevent abuse
from .security.file_sanitizer import FileSanitizer  # src/web/security/file_sanitizer.py - For sanitizing and validating file uploads
from ..backend.logger import get_logger  # src/backend/logger.py - For obtaining a logger instance

# Initialize logger
logger = get_logger(__name__)

# Initialize CSRF protection
csrf = CSRFProtection()

# Initialize Rate Limiter
rate_limiter = RateLimiter()

# Initialize File Sanitizer
file_sanitizer = FileSanitizer()


def create_app(config_name: str) -> Flask:
    """
    Factory function that creates and configures a Flask application instance

    Args:
        config_name: Name of the environment configuration to use

    Returns:
        Configured Flask application instance
    """
    # Create a new Flask application instance
    app = Flask(__name__)

    # Load configuration from get_config(config_name)
    app.config.from_object(get_config(config_name))

    # Initialize CSRF protection with csrf.init_app(app)
    csrf.init_app(app)

    # Initialize rate limiting with rate_limiter.init_app(app)
    rate_limiter.init_app(app)

    # Register error handlers with register_error_handlers(app)
    register_error_handlers(app)

    # Register routes with register_routes(app)
    register_routes(app)

    # Configure logging based on app configuration
    configure_logging(app)

    # Setup upload directory
    setup_upload_directory(app)

    # Log application startup information
    logger.info(f"Flask application '{app.name if hasattr(app, 'name') else ''}' created in {config_name} mode")

    # Return the configured Flask application
    return app


def configure_logging(app: Flask) -> None:
    """
    Configures logging for the Flask application

    Args:
        app: Flask application instance

    Returns:
        None: Configures logging for Flask and application modules
    """
    # Get log level from app configuration
    log_level = app.config.get('LOG_LEVEL', 'INFO')

    # Set up logging handlers and formatters
    # (Implementation details would go here, e.g., file rotation, etc.)
    # For example:
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    # Configure logging for Flask and application modules
    # (Implementation details would go here, e.g., setting log levels for specific modules)
    logger.setLevel(log_level)

    # Log application startup information
    logger.info(f"Logging configured with level: {log_level}")


def setup_upload_directory(app: Flask) -> None:
    """
    Ensures the upload directory exists and has proper permissions

    Args:
        app: Flask application instance

    Returns:
        None: Creates the upload directory and sets permissions
    """
    # Get upload directory path from app configuration
    upload_dir = app.config.get('UPLOAD_FOLDER', './uploads')

    # Check if directory exists, create it if it doesn't
    if not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir, exist_ok=True)
            logger.info(f"Created upload directory: {upload_dir}")
        except OSError as e:
            logger.error(f"Failed to create upload directory: {upload_dir} - {str(e)}")
            raise

    # Set appropriate permissions on the directory
    # (Implementation details would go here, e.g., setting chmod permissions)
    # For example:
    # os.chmod(upload_dir, 0o777)

    # Log the upload directory setup
    logger.info(f"Upload directory set up: {upload_dir}")