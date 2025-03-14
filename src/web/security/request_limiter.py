"""
Rate limiting functionality for the JSON to Excel Conversion Tool's web interface.

This module provides rate limiting capabilities to prevent abuse by limiting the
number of requests a client can make within a specified time period.
"""

import logging
import time
from functools import wraps

from flask import Flask, request, current_app, abort

# Import configuration
from ..config.web_interface_config import security

# Configure logger
logger = logging.getLogger(__name__)

# Load default settings from configuration
DEFAULT_REQUESTS_PER_MINUTE = security['rate_limiting']['requests_per_minute']
DEFAULT_UPLOAD_REQUESTS_PER_MINUTE = security['rate_limiting']['upload_requests_per_minute']
RATE_LIMITING_ENABLED = security['rate_limiting']['enabled']


def rate_limit(requests_per_minute):
    """
    Decorator that applies rate limiting to a route.
    
    Args:
        requests_per_minute (int): Maximum number of requests allowed per minute
        
    Returns:
        function: Decorator function that applies rate limiting
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # If rate limiting is disabled globally, call the original function
            if not RATE_LIMITING_ENABLED:
                return f(*args, **kwargs)
                
            # Get the rate limiter instance from the app
            limiter = current_app.extensions.get('rate_limiter')
            if not limiter:
                logger.warning("Rate limiter not initialized, skipping rate limit check")
                return f(*args, **kwargs)
                
            # Check if current endpoint is exempt from rate limiting
            if limiter.is_exempt():
                return f(*args, **kwargs)
                
            # Get client IP and check the rate limit
            client_ip = limiter.get_client_ip()
            if limiter.limit(client_ip, requests_per_minute):
                return f(*args, **kwargs)
            else:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                abort(429, description="Too many requests. Please try again later.")
                
        return wrapper
    return decorator


def exempt_from_rate_limit(f):
    """
    Decorator that exempts a route from rate limiting.
    
    Args:
        f (function): The view function to exempt
        
    Returns:
        function: Decorated function that bypasses rate limiting
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
        
    # Set an attribute on the function to mark it as exempt
    wrapper.rate_limit_exempt = True
    return wrapper


class RateLimiter:
    """
    Class that provides rate limiting functionality for Flask applications.
    
    This class tracks request counts per client IP and enforces rate limits
    to prevent abuse of the web interface.
    """
    
    def __init__(self, app=None):
        """
        Initialize the rate limiter instance.
        
        Args:
            app (Flask, optional): Flask application instance
        """
        self.app = None
        self.enabled = RATE_LIMITING_ENABLED
        self.request_counts = {}  # IP -> [timestamps]
        self.request_timestamps = {}  # IP -> {timestamp -> count}
        self.exempt_views = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize rate limiting for a Flask application.
        
        Args:
            app (Flask): Flask application instance
        """
        self.app = app
        
        # Check if rate limiting is enabled in app config
        if hasattr(app, 'config'):
            self.enabled = app.config.get('RATE_LIMITING_ENABLED', RATE_LIMITING_ENABLED)
        
        # Register extension with the app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['rate_limiter'] = self
        
        # Set up clean up task
        @app.before_request
        def cleanup_before_request():
            self.cleanup_old_requests()
            
        logger.info(f"Rate limiting {'enabled' if self.enabled else 'disabled'} for {app.name}")
    
    def limit(self, client_ip, requests_per_minute):
        """
        Apply rate limiting to a request.
        
        Args:
            client_ip (str): IP address of the client
            requests_per_minute (int): Maximum requests allowed per minute
            
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        # If rate limiting is disabled, always allow the request
        if not self.enabled:
            return True
            
        current_time = time.time()
        time_window = 60  # 1 minute in seconds
        
        # Initialize client request data if not present
        if client_ip not in self.request_timestamps:
            self.request_timestamps[client_ip] = {}
            
        # Clean up old timestamps for this client
        client_timestamps = self.request_timestamps[client_ip]
        for timestamp in list(client_timestamps.keys()):
            if current_time - timestamp > time_window:
                del client_timestamps[timestamp]
        
        # Count requests in the current time window
        request_count = sum(client_timestamps.values())
        
        # Check if the client has exceeded the rate limit
        if request_count >= requests_per_minute:
            logger.warning(f"Rate limit exceeded: {client_ip} made {request_count} requests in the last minute")
            return False
            
        # Update request count for the current timestamp
        client_timestamps[current_time] = client_timestamps.get(current_time, 0) + 1
        
        return True
    
    def exempt(self, view):
        """
        Mark a view function as exempt from rate limiting.
        
        Args:
            view (function): The view function to exempt
            
        Returns:
            function: The view function (unchanged)
        """
        self.exempt_views.add(view)
        return view
    
    def is_exempt(self):
        """
        Check if the current view function is exempt from rate limiting.
        
        Returns:
            bool: True if exempt, False otherwise
        """
        # Get current view function
        view_func = current_app.view_functions.get(request.endpoint)
        
        # Check if it's in the exempt set or has exempt attribute
        is_exempt = (
            view_func in self.exempt_views or
            getattr(view_func, 'rate_limit_exempt', False)
        )
        
        return is_exempt
    
    def get_client_ip(self):
        """
        Get the client IP address from the request.
        
        Returns:
            str: Client IP address
        """
        # Check X-Forwarded-For header first (for clients behind proxies)
        if request.headers.get('X-Forwarded-For'):
            client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        else:
            client_ip = request.remote_addr or '0.0.0.0'
            
        return client_ip
    
    def cleanup_old_requests(self):
        """
        Remove expired request data to prevent memory leaks.
        """
        if not self.enabled:
            return
            
        current_time = time.time()
        expired_threshold = 3600  # 1 hour in seconds
        
        # Track clients with no recent activity to remove them completely
        clients_to_remove = []
        
        # Check all clients
        for client_ip, timestamps in self.request_timestamps.items():
            # Check if client has any recent activity
            if timestamps and max(timestamps.keys()) < current_time - expired_threshold:
                clients_to_remove.append(client_ip)
                
        # Remove expired client data
        for client_ip in clients_to_remove:
            del self.request_timestamps[client_ip]
            
        if clients_to_remove:
            logger.debug(f"Cleaned up request data for {len(clients_to_remove)} inactive clients")