"""
Initializes the API module for the JSON to Excel Conversion Tool web interface.
This module serves as the entry point for all API-related functionality, registering
the various API blueprints and error handlers with the Flask application.
"""

from flask import Flask  # v: 2.3.0+ - For accessing Flask application type hints

from .endpoints import api_blueprint, register_api  # Internal import - Main API blueprint for registering all API routes
from .upload_api import upload_blueprint, register_upload_routes  # Internal import - Blueprint for file upload API endpoints
from .conversion_api import conversion_blueprint  # Internal import - Blueprint for conversion API endpoints
from .job_api import job_blueprint, register_job_routes  # Internal import - Blueprint for job management API endpoints
from .status_api import status_api  # Internal import - Blueprint for status API endpoints
from .error_handler import register_error_handlers  # Internal import - Function to register error handlers with Flask app
from ...backend.logger import get_logger  # Internal import - For obtaining a logger instance

# Initialize logger for this module
logger = get_logger(__name__)


def init_api(app: Flask) -> None:
    """
    Initializes the API module by registering all API blueprints and error handlers
    with the Flask application.

    Args:
        app: Flask application instance

    Returns:
        None: This function doesn't return a value
    """
    # Log that API initialization is starting
    logger.info("Starting API initialization")

    # Register the main API blueprint with the Flask app using register_api(app)
    register_api(app)

    # Register the upload blueprint with the main API blueprint
    app.register_blueprint(upload_blueprint)

    # Register the conversion blueprint with the main API blueprint
    app.register_blueprint(conversion_blueprint)

    # Register the job routes with the main API blueprint using register_job_routes()
    register_job_routes()

    # Register the status API blueprint with the main API blueprint
    app.register_blueprint(status_api)

    # Register error handlers with the Flask app using register_error_handlers(app)
    register_error_handlers(app)

    # Log that API initialization is complete
    logger.info("API initialization complete")