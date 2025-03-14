"""
Implements the RESTful API endpoints for job management in the JSON to Excel Conversion Tool web interface.
This module provides routes for listing jobs, retrieving job details, and monitoring the job queue status,
complementing the conversion-specific endpoints in conversion_api.py.
"""

import logging  # v: built-in - For logging API operations
from flask import Blueprint, request, jsonify  # v: 2.3.0+ - For creating modular API routes and handling requests
from ..utils.response_formatter import ResponseFormatter  # For formatting consistent API responses
from ..services.job_manager import JobManager  # For managing conversion jobs
from ..models.job_status import JobStatusEnum  # For filtering jobs by status
from ..exceptions.job_exceptions import JobNotFoundException  # For handling job not found errors
from .endpoints import api_blueprint  # For registering job API routes

# Initialize logger
logger = logging.getLogger(__name__)

# Create a Blueprint for job-related API endpoints
job_blueprint = Blueprint('jobs', __name__, url_prefix='/api/jobs')

# Instantiate the JobManager
job_manager = JobManager()


@job_blueprint.route('/', methods=['GET'])
def list_jobs():
    """
    Lists all conversion jobs with optional status filtering.

    Returns:
        flask.Response: JSON response with list of jobs
    """
    # Log the list jobs request
    logger.info("Listing all conversion jobs")

    # Extract status filter from request.args if provided
    status_str = request.args.get('status')
    status = None

    # Convert status string to JobStatusEnum if provided
    if status_str:
        try:
            status = JobStatusEnum(status_str)
        except ValueError:
            return ResponseFormatter.error("Invalid status filter", status_code=400)

    # Get the list of jobs using job_manager.list_jobs(status)
    jobs = job_manager.list_jobs(status=status)

    # Return a formatted list response using ResponseFormatter.list(jobs, 'jobs')
    return ResponseFormatter.list(jobs, 'job')


@job_blueprint.route('/<job_id>', methods=['GET'])
def get_job_details(job_id: str):
    """
    Gets detailed information about a specific job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: JSON response with job details or error
    """
    # Log the job details request for job_id
    logger.info(f"Getting details for job ID: {job_id}")

    # Get the job using job_manager.get_job(job_id)
    job, error = job_manager.get_job(job_id)

    # If job not found, return a not found error response
    if error:
        return ResponseFormatter.not_found("Job", job_id)

    # Return a success response with the job details
    return ResponseFormatter.success(data={"job": job.to_dict()}, message="Job details")


@job_blueprint.route('/queue/status', methods=['GET'])
def get_queue_status():
    """
    Gets the current status of the job queue.

    Returns:
        flask.Response: JSON response with queue status information
    """
    # Log the queue status request
    logger.info("Getting job queue status")

    # Get the queue status using job_manager.get_queue_status()
    queue_status = job_manager.get_queue_status()

    # Return a success response with the queue status information
    return ResponseFormatter.success(data=queue_status, message="Job queue status")


def register_job_routes():
    """
    Registers the job API routes with the main API blueprint.

    Returns:
        None: This function doesn't return a value
    """
    # Register the job_blueprint with the main api_blueprint
    api_blueprint.register_blueprint(job_blueprint)

    # Log that job routes have been registered
    logger.info("Job API routes registered")