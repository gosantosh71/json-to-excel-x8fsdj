import os  # v: built-in - For accessing environment variables
from dotenv import load_dotenv  # python-dotenv 0.19.0+ - For loading environment variables from .env files

from .app import create_app  # src/web/app.py - Import the Flask application factory function


def main():
    """
    Main entry point for running the development server
    """
    # Check if the script is being run directly
    if __name__ == "__main__":
        # Load environment variables from .env file if it exists
        load_dotenv()

        # Get host from environment variable or default to '0.0.0.0'
        host = os.getenv('FLASK_HOST', '0.0.0.0')

        # Get port from environment variable or default to 5000
        port = int(os.getenv('FLASK_PORT', 5000))

        # Get debug mode from environment variable or default to True
        debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

        # Create the Flask application instance
        app = create_app(os.getenv('FLASK_ENV', 'development'))

        # Run the Flask application with the specified host, port, and debug settings
        app.run(host=host, port=port, debug=debug)


# Create the Flask application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == "__main__":
    main()