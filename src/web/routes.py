from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint, abort  # flask: 2.3.0+
from .services.file_service import FileService  # src/web/services/file_service.py
from .services.conversion_service import ConversionService  # src/web/services/conversion_service.py
from .services.job_manager import JobManager  # src/web/services/job_manager.py
from .api.endpoints import register_api  # src/web/api/endpoints.py
from .api.upload_api import register_upload_routes  # src/web/api/upload_api.py
from .api.conversion_api import conversion_blueprint  # src/web/api/conversion_api.py
from ..backend.logger import get_logger  # src/backend/logger.py

# Initialize logger
logger = get_logger(__name__)

# Create Blueprint for web routes
web_blueprint = Blueprint('web', __name__)

# Initialize services
file_service = FileService()
conversion_service = ConversionService()
job_manager = JobManager()


def register_routes(app: Flask) -> None:
    """
    Registers all web routes and API endpoints with the Flask application
    
    Args:
        app: Flask application instance
    
    Returns:
        None: Registers routes with the Flask app
    """
    # Register the web_blueprint with the Flask app
    app.register_blueprint(web_blueprint)
    # Register API endpoints using register_api(app)
    register_api(app)
    # Register upload routes using register_upload_routes(app)
    register_upload_routes(app)
    # Register conversion_blueprint with the Flask app
    app.register_blueprint(conversion_blueprint)
    # Log that all routes have been registered
    logger.info("All routes registered with Flask application")


@web_blueprint.route('/', methods=['GET'])
@web_blueprint.route('/index', methods=['GET'])
def index() -> str:
    """
    Renders the home page with file upload form
    
    Args:
        None
    
    Returns:
        str: Rendered HTML template
    """
    # Log the request for the index page
    logger.info("Rendering index page")
    # Render the index.html template with title 'Home'
    # Set active_page to 'home' for navigation highlighting
    return render_template('index.html', title='Home', active_page='home')


@web_blueprint.route('/about', methods=['GET'])
def about() -> str:
    """
    Renders the about page with information about the tool
    
    Args:
        None
    
    Returns:
        str: Rendered HTML template
    """
    # Log the request for the about page
    logger.info("Rendering about page")
    # Render the about.html template with title 'About'
    # Set active_page to 'about' for navigation highlighting
    return render_template('about.html', title='About', active_page='about')


@web_blueprint.route('/help', methods=['GET'])
def help() -> str:
    """
    Renders the help page with usage instructions
    
    Args:
        None
    
    Returns:
        str: Rendered HTML template
    """
    # Log the request for the help page
    logger.info("Rendering help page")
    # Render the help.html template with title 'Help'
    # Set active_page to 'help' for navigation highlighting
    return render_template('help.html', title='Help', active_page='help')


@web_blueprint.route('/upload', methods=['POST'])
def upload_file() -> str:
    """
    Handles file upload from the web interface
    
    Args:
        None
    
    Returns:
        str: Rendered HTML template or redirect
    """
    # Log the file upload request
    logger.info("Handling file upload request")
    # Check if the request contains a file
    if 'json_file' not in request.files:
        # If no file is found, flash an error message and redirect to index
        flash('No file part', 'error')
        return redirect(url_for('web.index'))
    # Get the file from request.files['json_file']
    file = request.files['json_file']
    # Upload the file using file_service.upload_file(file)
    upload_file_result, error = file_service.upload_file(file)
    # If upload fails, flash the error message and redirect to index
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.index'))
    # Redirect to the convert route with the file_id
    return redirect(url_for('web.convert', file_id=upload_file_result.file_id))


@web_blueprint.route('/convert/<file_id>', methods=['GET'])
def convert(file_id: str) -> str:
    """
    Renders the conversion page with options for a specific file
    
    Args:
        file_id: Unique identifier for the file
    
    Returns:
        str: Rendered HTML template or redirect
    """
    # Log the conversion page request for file_id
    logger.info(f"Rendering conversion page for file ID: {file_id}")
    # Get the upload file using file_service.get_upload(file_id)
    upload_file, error = file_service.get_upload(file_id)
    # If file not found, flash an error message and redirect to index
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.index'))
    # Get detailed file information using file_service.get_file_details(file_id)
    file_details, error = file_service.get_file_details(file_id)
    # Render the convert.html template with file details
    # Set active_page to 'convert' for navigation highlighting
    return render_template('convert.html', title='Convert', file=file_details, active_page='convert')


@web_blueprint.route('/convert/<file_id>/process', methods=['POST'])
@conversion_blueprint.route('/jobs/<file_id>/process', methods=['POST'])
def process_conversion(file_id: str) -> str:
    """
    Processes the conversion form submission and starts the conversion job
    
    Args:
        file_id: Unique identifier for the file
    
    Returns:
        str: Redirect to status page
    """
    # Log the conversion process request for file_id
    logger.info(f"Processing conversion for file ID: {file_id}")
    # Get the upload file using file_service.get_upload(file_id)
    upload_file, error = file_service.get_upload(file_id)
    # If file not found, flash an error message and redirect to index
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.index'))
    # Extract conversion options from request.form
    options = request.form.to_dict()
    # Process form data into ConversionOptions using conversion_service.process_form_data()
    conversion_options = conversion_service.process_form_data(options)
    # Create a new job using job_manager.create_job(file_id, options)
    job, error = job_manager.create_job(file_id, conversion_options)
    # If job creation fails, flash an error message and redirect to convert page
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.convert', file_id=file_id))
    # Redirect to the status page with the job_id
    return redirect(url_for('web.conversion_status', job_id=job.job_id))


@web_blueprint.route('/status/<job_id>', methods=['GET'])
def conversion_status(job_id: str) -> str:
    """
    Renders the status page for a conversion job
    
    Args:
        job_id: Unique identifier for the job
    
    Returns:
        str: Rendered HTML template or redirect
    """
    # Log the status page request for job_id
    logger.info(f"Rendering status page for job ID: {job_id}")
    # Get the job using job_manager.get_job(job_id)
    job, error = job_manager.get_job(job_id)
    # If job not found, flash an error message and redirect to index
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.index'))
    # Render the status.html template with job details
    # Set active_page to 'status' for navigation highlighting
    return render_template('status.html', title='Status', job=job, active_page='status')


@web_blueprint.route('/results/<job_id>', methods=['GET'])
def conversion_results(job_id: str) -> str:
    """
    Renders the results page for a completed conversion job
    
    Args:
        job_id: Unique identifier for the job
    
    Returns:
        str: Rendered HTML template or redirect
    """
    # Log the results page request for job_id
    logger.info(f"Rendering results page for job ID: {job_id}")
    # Get the job using job_manager.get_job(job_id)
    job, error = job_manager.get_job(job_id)
    # If job not found, flash an error message and redirect to index
    if error:
        flash(error.message, 'error')
        return redirect(url_for('web.index'))
    # If job is not complete, redirect to the status page
    if not job.is_complete():
        return redirect(url_for('web.conversion_status', job_id=job_id))
    # Get the job result using job_manager.get_job_result(job_id)
    result, error = job_manager.get_job_result(job_id)
    # Generate a download URL using url_for('conversion.download_file', job_id=job_id)
    download_url = url_for('conversion.download_file', job_id=job_id)
    # Render the results.html template with job details and download URL
    # Set active_page to 'results' for navigation highlighting
    return render_template('results.html', title='Results', job=job, download_url=download_url, active_page='results')


@web_blueprint.errorhandler(404)
def error_404(e: Exception) -> str:
    """
    Handles 404 Not Found errors
    
    Args:
        e: Exception object
    
    Returns:
        str: Rendered HTML template
    """
    # Log the 404 error
    logger.warning(f"404 error: {e}")
    # Render the error.html template with error details
    # Set status code to 404
    # Set active_page to 'error' for navigation highlighting
    return render_template('error.html', title='Error', error=e, active_page='error'), 404


@web_blueprint.errorhandler(500)
def error_500(e: Exception) -> str:
    """
    Handles 500 Internal Server Error errors
    
    Args:
        e: Exception object
    
    Returns:
        str: Rendered HTML template
    """
    # Log the 500 error with exception details
    logger.exception(f"500 error: {e}")
    # Render the error.html template with error details
    # Set status code to 500
    # Set active_page to 'error' for navigation highlighting
    return render_template('error.html', title='Error', error=e, active_page='error'), 500