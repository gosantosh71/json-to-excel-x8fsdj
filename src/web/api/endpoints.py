"""
Defines the core API endpoints and blueprint registration for the JSON to Excel Conversion Tool web interface.
This module serves as the central API router, registering all API routes with the Flask application
and providing a consistent interface for API operations.
"""

from flask import Blueprint, request, jsonify  # v: 2.3.0+

from ..utils.response_formatter import ResponseFormatter
from ...backend.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Create API blueprint
api_blueprint = Blueprint('api', __name__, url_prefix='/api')


def register_api(app):
    """
    Registers the API blueprint and all API endpoints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(api_blueprint)
    logger.info("API routes registered with Flask application")


@api_blueprint.route('/health', methods=['GET'])
def api_health_check():
    """
    Provides a health check endpoint for the API to verify it's operational.
    
    Returns:
        flask.Response: JSON response with API health status
    """
    health_status = {
        "status": "healthy",
        "service": "JSON to Excel Conversion Tool",
        "timestamp": "2023-01-01T00:00:00Z"
    }
    return ResponseFormatter.success(health_status, "API is operational")


@api_blueprint.route('/version', methods=['GET'])
def api_version():
    """
    Returns the current API version information.
    
    Returns:
        flask.Response: JSON response with API version details
    """
    version_info = {
        "version": "1.0.0",
        "release_date": "2023-01-01"
    }
    return ResponseFormatter.success(version_info, "API version information")


@api_blueprint.route('/docs', methods=['GET'])
def api_documentation():
    """
    Returns information about available API endpoints and their usage.
    
    Returns:
        flask.Response: JSON response with API documentation
    """
    api_docs = {
        "endpoints": [
            {
                "path": "/api/health",
                "method": "GET",
                "description": "Health check endpoint to verify API is operational",
                "example": {
                    "url": "/api/health",
                    "response": {
                        "success": True,
                        "message": "API is operational",
                        "data": {
                            "status": "healthy",
                            "service": "JSON to Excel Conversion Tool"
                        }
                    }
                }
            },
            {
                "path": "/api/version",
                "method": "GET",
                "description": "Returns the current API version information",
                "example": {
                    "url": "/api/version",
                    "response": {
                        "success": True,
                        "message": "API version information",
                        "data": {
                            "version": "1.0.0",
                            "release_date": "2023-01-01"
                        }
                    }
                }
            },
            {
                "path": "/api/docs",
                "method": "GET",
                "description": "Returns information about available API endpoints"
            },
            {
                "path": "/api/upload",
                "method": "POST",
                "description": "Upload a JSON file for conversion",
                "request": {
                    "content_type": "multipart/form-data",
                    "parameters": {
                        "file": "JSON file to convert (required)"
                    }
                },
                "response": {
                    "success": True,
                    "message": "File uploaded successfully",
                    "file": {
                        "file_id": "unique-identifier",
                        "original_filename": "example.json"
                    }
                }
            },
            {
                "path": "/api/convert",
                "method": "POST",
                "description": "Convert an uploaded JSON file to Excel",
                "request": {
                    "content_type": "application/json",
                    "parameters": {
                        "file_id": "ID of the uploaded file (required)",
                        "options": {
                            "sheet_name": "Optional sheet name",
                            "array_handling": "expand or join"
                        }
                    }
                }
            },
            {
                "path": "/api/status/{job_id}",
                "method": "GET",
                "description": "Check the status of a conversion job"
            },
            {
                "path": "/api/download/{file_id}",
                "method": "GET",
                "description": "Download a converted Excel file"
            }
        ]
    }
    return ResponseFormatter.success(api_docs, "API documentation")