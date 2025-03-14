"""
Constants for the web interface of the JSON to Excel Conversion Tool.

This module defines all constant values used throughout the web interface,
ensuring consistency across different components. It includes file paths,
upload settings, HTTP status codes, UI messages, and security configurations.
"""

import os  # v: built-in
from ..backend.constants import FILE_CONSTANTS, EXCEL_CONSTANTS

# Application metadata
VERSION = "1.0.0"
APP_NAME = "JSON to Excel Conversion Tool - Web Interface"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')
TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')

# Web application general constants
WEB_CONSTANTS = {
    "VERSION": VERSION,
    "APP_NAME": APP_NAME,
    "DEFAULT_SHEET_NAME": EXCEL_CONSTANTS["DEFAULT_SHEET_NAME"],
    "DEFAULT_ARRAY_HANDLING": "expand",  # Default array handling mode
}

# File path constants for the web application
FILE_PATHS = {
    "BASE_DIR": BASE_DIR,
    "UPLOAD_FOLDER": UPLOAD_FOLDER,
    "DOWNLOAD_FOLDER": DOWNLOAD_FOLDER,
    "TEMP_FOLDER": TEMP_FOLDER,
    "STATIC_FOLDER": os.path.join(BASE_DIR, 'static'),
    "TEMPLATES_FOLDER": os.path.join(BASE_DIR, 'templates'),
}

# Constants related to file upload handling
UPLOAD_CONSTANTS = {
    "MAX_FILE_SIZE_BYTES": FILE_CONSTANTS["MAX_FILE_SIZE_BYTES"],
    "ALLOWED_EXTENSIONS": FILE_CONSTANTS["ALLOWED_EXTENSIONS"],
    "MAX_FILENAME_LENGTH": 100,
    "DISALLOW_SPECIAL_CHARS": True,
}

# Constants related to job management
JOB_CONSTANTS = {
    "MAX_ACTIVE_JOBS": 5,
    "JOB_TIMEOUT_SECONDS": 300,  # 5 minutes
    "JOB_CLEANUP_INTERVAL_SECONDS": 600,  # 10 minutes
    "COMPLETED_JOB_RETENTION_SECONDS": 3600,  # 1 hour
}

# HTTP status codes used in API responses
HTTP_STATUS = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500,
}

# User-friendly messages displayed in the web interface
UI_MESSAGES = {
    "UPLOAD_SUCCESS": "File uploaded successfully.",
    "CONVERSION_STARTED": "Conversion started. Please wait...",
    "CONVERSION_COMPLETED": "Conversion completed successfully.",
    "CONVERSION_FAILED": "Conversion failed. Please check the error details.",
    "INVALID_FILE_TYPE": "Invalid file type. Only JSON files are allowed.",
    "FILE_TOO_LARGE": f"File too large. Maximum file size is {FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'] / (1024 * 1024):.1f} MB.",
    "NO_FILE_SELECTED": "No file selected. Please choose a file to upload.",
}

# Security-related constants for the web interface
SECURITY_CONSTANTS = {
    "CSRF_ENABLED": True,
    "SESSION_TIMEOUT_MINUTES": 30,
    "RATE_LIMIT_REQUESTS_PER_MINUTE": 60,
    "UPLOAD_RATE_LIMIT_PER_MINUTE": 10,
}

# Default configuration values for conversion options
DEFAULT_CONFIG = {
    "sheet_name": EXCEL_CONSTANTS["DEFAULT_SHEET_NAME"],
    "array_handling": "expand",  # Default array handling mode
    "format_headers": True,
    "auto_column_width": True,
    "apply_data_formatting": True,
}