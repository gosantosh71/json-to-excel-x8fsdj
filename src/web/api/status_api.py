import logging  # v: built-in - For logging API requests and errors
from flask import Blueprint, request, jsonify, current_app  # v: 2.3.0+
from ..services.job_manager import JobManager  # Internal import - For retrieving job status information
from ..models.job_status import JobStatusEnum  # Internal import - For filtering jobs by status
from ..utils.response_formatter import ResponseFormatter  # Internal import - For formatting consistent API responses
from ..exceptions.job_exceptions import JobNotFoundException  # Internal import - For handling job not found errors
from ...backend.logger import get_logger  # Internal import - For obtaining a logger instance

# Initialize logger
logger = get_logger(__name__)

# Create Blueprint for status API
status_api = Blueprint('status_api', __name__, url_prefix='/api/status')

# Define global job_manager variable
job_manager = None


def get_job_manager() -> JobManager:
    """
    Gets or initializes the job manager instance.

    Returns:
        JobManager: The job manager instance
    """
    global job_manager
    if job_manager is None:
        job_manager = JobManager()
    return job_manager


@status_api.route('/job/<string:job_id>', methods=['GET'])
def get_job_status_endpoint(job_id: str):
    """
    API endpoint for retrieving the status of a specific job.

    Args:
        job_id (str): The ID of the job.

    Returns:
        flask.Response: JSON response with job status information
    """
    logger.info(f"Status request for job_id: {job_id}")
    job_manager = get_job_manager()
    status, error = job_manager.get_job_status(job_id)

    if error:
        return ResponseFormatter.error(error, status_code=400)

    if status is None:
        return ResponseFormatter.not_found("Job", job_id)

    return ResponseFormatter.job_status(status)


@status_api.route('/queue', methods=['GET'])
def get_queue_status_endpoint():
    """
    API endpoint for retrieving the overall status of the job queue.

    Returns:
        flask.Response: JSON response with queue status information
    """
    logger.info("Queue status request")
    job_manager = get_job_manager()
    queue_status = job_manager.get_queue_status()
    return ResponseFormatter.success(queue_status)


@status_api.route('/jobs', methods=['GET'])
def list_jobs_endpoint():
    """
    API endpoint for listing all jobs with optional status filtering.

    Returns:
        flask.Response: JSON response with list of jobs
    """
    logger.info("List jobs request")
    job_manager = get_job_manager()
    status_filter = request.args.get('status')

    if status_filter:
        try:
            status_filter = JobStatusEnum(status_filter)
        except ValueError:
            return ResponseFormatter.error("Invalid status filter", status_code=400)

    jobs = job_manager.list_jobs(status_filter)
    return ResponseFormatter.list(jobs, item_type='job')


# Export the Blueprint
exports = [status_api]