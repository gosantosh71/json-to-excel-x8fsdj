import os  # v: built-in - For accessing environment variables

from .app import create_app  # src/web/app.py - For creating the Flask application

# Create the Flask application instance, defaulting to 'production' if FLASK_ENV is not set
application = create_app(os.getenv('FLASK_ENV', 'production'))