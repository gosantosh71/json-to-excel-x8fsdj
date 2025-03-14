import uuid
import hmac
import hashlib
import logging
from functools import wraps
from flask import Flask, request, session, abort, current_app

# Set up logger for CSRF-related events and errors
logger = logging.getLogger(__name__)

# Constants for CSRF token names in various contexts
CSRF_TOKEN_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-CSRF-Token'

class CSRFProtection:
    """
    Class that provides CSRF protection functionality for Flask applications.
    
    This class implements Cross-Site Request Forgery protection for Flask applications
    by generating and validating tokens for form submissions and AJAX requests.
    """
    
    def __init__(self, app=None):
        """
        Initializes the CSRF protection instance.
        
        Args:
            app (Flask, optional): Flask application instance
        """
        self.app = None
        self.enabled = True
        self.exempt_views = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initializes CSRF protection for a Flask application.
        
        Args:
            app (Flask): Flask application instance
        """
        self.app = app
        self.enabled = app.config.get('CSRF_ENABLED', True)
        
        # Ensure app has extensions dictionary
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        
        # Store the CSRF protection instance in app extensions
        app.extensions['csrf_protection'] = self
        
        # Set up before_request handler to ensure CSRF token exists
        app.before_request(self.protect)
        
        # Set up after_request handler to include CSRF token in response
        @app.after_request
        def include_csrf_token(response):
            # Only set CSRF cookie on text/html responses
            if self.enabled and 'text/html' in response.headers.get('Content-Type', ''):
                token = self.get_token()
                # Set token in session
                session[CSRF_TOKEN_NAME] = token
            return response
        
        logger.info(f"CSRF Protection initialized for app: {app.name if hasattr(app, 'name') else ''}")
    
    def exempt(self, view):
        """
        Marks a view function as exempt from CSRF protection.
        
        Args:
            view (function): The view function to exempt
            
        Returns:
            function: The view function (unchanged)
        """
        self.exempt_views.add(view)
        return view
    
    def protect(self):
        """
        Ensures a request has a valid CSRF token.
        
        This method is called before every request to ensure that requests
        that require CSRF protection have a valid token.
        """
        if not self.enabled:
            return
        
        if not self.requires_csrf_check():
            return
            
        if self.is_exempt():
            return
            
        token = self.get_token_from_request()
        
        if not token or not self.validate_token(token):
            logger.warning(f"CSRF validation failed for request to: {request.path}")
            abort(403, "CSRF token missing or invalid")
    
    def get_token(self):
        """
        Gets the current CSRF token or generates a new one.
        
        Returns:
            str: CSRF token
        """
        token = session.get(CSRF_TOKEN_NAME, None)
        if token is None:
            token = generate_csrf_token()
            session[CSRF_TOKEN_NAME] = token
        return token
    
    def validate_token(self, token):
        """
        Validates a CSRF token against the one stored in session.
        
        Args:
            token (str): The token to validate
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        stored_token = session.get(CSRF_TOKEN_NAME)
        
        if not stored_token:
            logger.warning("No CSRF token in session")
            return False
            
        valid = stored_token == token
        if not valid:
            logger.warning("CSRF token validation failed - token mismatch")
        
        return valid
    
    def get_token_from_request(self):
        """
        Extracts the CSRF token from a request (form or header).
        
        This method checks for the CSRF token in form data, headers, and JSON data.
        
        Returns:
            str: CSRF token or None if not found
        """
        # Check for token in form data
        token = request.form.get(CSRF_TOKEN_NAME)
        
        # If not in form, check headers
        if token is None:
            token = request.headers.get(CSRF_HEADER_NAME)
            
        # If not in headers, check JSON data
        if token is None and request.is_json:
            json_data = request.get_json(silent=True) or {}
            token = json_data.get(CSRF_TOKEN_NAME)
            
        return token
    
    def requires_csrf_check(self):
        """
        Determines if a request requires CSRF validation.
        
        CSRF validation is required for state-changing methods like
        POST, PUT, DELETE, and PATCH.
        
        Returns:
            bool: True if CSRF check is required, False otherwise
        """
        return request.method in ['POST', 'PUT', 'DELETE', 'PATCH']
    
    def is_exempt(self):
        """
        Checks if the current view function is exempt from CSRF protection.
        
        A view function can be exempt if it's in the exempt_views set or
        has the _csrf_exempt attribute.
        
        Returns:
            bool: True if exempt, False otherwise
        """
        view = current_app.view_functions.get(request.endpoint)
        
        if not view:
            return False
            
        if view in self.exempt_views:
            return True
            
        # Check for csrf_exempt attribute on the view function
        return hasattr(view, '_csrf_exempt') and view._csrf_exempt

def csrf_required(f):
    """
    Decorator that enforces CSRF protection on a route.
    
    This decorator can be used on specific routes to ensure
    they have CSRF protection, even if global protection is disabled.
    
    Args:
        f (function): The view function to protect
        
    Returns:
        function: Decorated function that validates CSRF token before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        csrf = current_app.extensions.get('csrf_protection')
        
        if csrf and csrf.requires_csrf_check() and not csrf.is_exempt():
            token = csrf.get_token_from_request()
            if not token or not csrf.validate_token(token):
                abort(403, "CSRF token missing or invalid")
                
        return f(*args, **kwargs)
    
    return decorated_function

def csrf_exempt(f):
    """
    Decorator that exempts a route from CSRF protection.
    
    This decorator can be used on specific routes to exempt
    them from CSRF protection, even if global protection is enabled.
    
    Args:
        f (function): The view function to exempt
        
    Returns:
        function: Decorated function that bypasses CSRF validation
    """
    f._csrf_exempt = True
    return f

def generate_csrf_token():
    """
    Generates a new CSRF token and stores it in the session.
    
    The token is a combination of a UUID and an HMAC signature
    created using the app's secret key for added security.
    
    Returns:
        str: Generated CSRF token
    """
    # Generate a random UUID
    token_uuid = str(uuid.uuid4())
    
    # Create an HMAC signature using the app's secret key
    if current_app and hasattr(current_app, 'secret_key') and current_app.secret_key:
        signature = hmac.new(
            current_app.secret_key.encode('utf-8'),
            token_uuid.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Combine UUID and signature
        token = f"{token_uuid}:{signature}"
    else:
        # Fallback if no secret key is available (not recommended for production)
        logger.warning("No secret key available for CSRF token generation")
        token = token_uuid
        
    # Store in session
    session[CSRF_TOKEN_NAME] = token
    
    return token