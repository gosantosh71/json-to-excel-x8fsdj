"""
Entry point for the security module of the JSON to Excel Conversion Tool's web interface.

This module provides comprehensive security protections including CSRF protection,
file sanitization, input validation, and rate limiting to safeguard the web interface
against common attacks and security vulnerabilities.
"""

import logging  # v: built-in

# Import security-related classes and functions
from .csrf_protection import CSRFProtection, csrf_required, csrf_exempt
from .file_sanitizer import FileSanitizer, sanitize_filename, sanitize_excel_cell_content
from .input_validator import InputValidator, sanitize_string, sanitize_path
from .request_limiter import RateLimiter, rate_limit, exempt_from_rate_limit

# Import logging functionality
from ...backend.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Define what is exported from this module
__all__ = [
    "CSRFProtection", "csrf_required", "csrf_exempt",
    "FileSanitizer", "sanitize_filename", "sanitize_excel_cell_content", 
    "InputValidator", "sanitize_string", "sanitize_path",
    "RateLimiter", "rate_limit", "exempt_from_rate_limit",
    "init_security"
]

def init_security(app):
    """
    Initializes all security components for a Flask application.
    
    This function sets up CSRF protection, rate limiting, file sanitization,
    and input validation for the provided Flask application. It returns a
    dictionary containing all initialized security components for further
    configuration if needed.
    
    Args:
        app (Flask): The Flask application to secure
        
    Returns:
        dict: Dictionary containing initialized security components
    """
    logger.info(f"Initializing security components for Flask application")
    
    # Initialize CSRF protection
    csrf = CSRFProtection()
    csrf.init_app(app)
    logger.debug("CSRF protection initialized")
    
    # Initialize rate limiting
    rate_limiter = RateLimiter()
    rate_limiter.init_app(app)
    logger.debug("Rate limiting initialized")
    
    # Create file sanitizer
    file_sanitizer = FileSanitizer()
    logger.debug("File sanitizer initialized")
    
    # Create input validator
    input_validator = InputValidator()
    logger.debug("Input validator initialized")
    
    # Return all security components
    security_components = {
        'csrf': csrf,
        'rate_limiter': rate_limiter,
        'file_sanitizer': file_sanitizer,
        'input_validator': input_validator
    }
    
    logger.info("Security components successfully initialized")
    return security_components