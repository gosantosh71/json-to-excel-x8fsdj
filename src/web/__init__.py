import os  # built-in
from flask import Flask  # flask: 2.3.0+
from dotenv import load_dotenv  # python-dotenv 0.19.0+

from .config.flask_config import get_config  # src/web/config/flask_config.py
from .routes import register_routes  # src/web/routes.py
from .api.error_handler import register_error_handlers  # src/web/api/error_handler.py
from .security.csrf_protection import CSRFProtection  # src/web/security/csrf_protection.py
from .security.request_limiter import RateLimiter  # src/web/security/request_limiter.py
from .security.file_sanitizer import FileSanitizer  # src/web/security/file_sanitizer.py
from ..backend.logger import get_logger  # src/backend/logger.py

# Initialize logger
logger = get_logger(__name__)

# Initialize CSRF protection
csrf = CSRFProtection()

# Initialize rate limiter
rate_limiter = RateLimiter()

# Initialize file sanitizer
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

    # Setup upload directory for file uploads
    setup_upload_directory(app)

    # Log application initialization
    logger.info(f"Flask application '{app.name if hasattr(app, 'name') else ''}' created with config '{config_name}'")

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
    logging.basicConfig(level=log_level)

    # Configure logging for Flask and application modules
    app.logger.setLevel(log_level)
    logger.setLevel(log_level)

    # Log application startup information
    logger.info(f"Logging configured with level '{log_level}'")


def setup_upload_directory(app: Flask) -> None:
    """
    Ensures the upload directory exists and has proper permissions

    Args:
        app: Flask application instance

    Returns:
        None: Sets up the upload directory
    """
    # Get upload directory path from app configuration
    upload_dir = app.config.get('UPLOAD_FOLDER', './uploads')

    # Check if directory exists, create it if it doesn't
    if not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir)
            logger.info(f"Created upload directory: {upload_dir}")
        except OSError as e:
            logger.error(f"Could not create upload directory: {upload_dir} - {e}")
            raise

    # Set appropriate permissions on the directory
    try:
        os.chmod(upload_dir, 0o777)  # Read, write, and execute for all users
        logger.info(f"Set permissions for upload directory: {upload_dir}")
    except OSError as e:
        logger.warning(f"Could not set permissions for upload directory: {upload_dir} - {e}")

    # Log the upload directory setup
    logger.info(f"Upload directory setup completed: {upload_dir}")


__all__ = ['create_app']