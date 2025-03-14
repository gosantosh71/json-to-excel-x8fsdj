"""
Gunicorn configuration file for the JSON to Excel Conversion Tool web interface.

This file defines server settings, worker configuration, logging options, and other 
parameters for running the Flask application in a production environment using 
the Gunicorn WSGI HTTP server.
"""

import os
import multiprocessing
import json
import pathlib

# Load web interface configuration
config_path = pathlib.Path(__file__).parent / "config" / "web_interface_config.json"
try:
    with open(config_path, 'r') as f:
        web_interface_config = json.load(f)
        server = web_interface_config.get('server', {})
        logging = web_interface_config.get('logging', {})
except Exception as e:
    print(f"Error loading configuration: {e}")
    web_interface_config = {
        "server": {"host": "127.0.0.1", "port": 5000},
        "logging": {"level": "INFO"}
    }
    server = web_interface_config['server']
    logging = web_interface_config['logging']

# Gunicorn server socket binding
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# Number of worker processes
# Recommended formula: (2 x $num_cores) + 1
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker class/type
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')

# Maximum number of simultaneous connections per worker
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', 1000))

# Timeout for worker processes (seconds)
timeout = int(os.getenv('GUNICORN_TIMEOUT', 30))

# Time to wait for requests on a Keep-Alive connection (seconds)
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', 2))

# Maximum number of requests a worker will process before restarting
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', 1000))

# Maximum jitter to add to max_requests to avoid all workers restarting at once
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', 50))

# Access log file location ('-' for stdout)
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')

# Error log file location ('-' for stderr)
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')

# Log level
loglevel = os.getenv('GUNICORN_LOG_LEVEL', logging.get('level', 'info').lower())

# Process name
proc_name = os.getenv('GUNICORN_PROC_NAME', 'json-to-excel-web')

# WSGI application path
wsgi_app = 'wsgi:application'

def on_starting(server):
    """
    Hook function that executes when Gunicorn starts.
    
    Args:
        server: The Gunicorn server instance
    """
    server.log.info(f"Starting JSON to Excel Web Interface on {bind}")
    
    # Ensure required directories exist
    logs_dir = pathlib.Path('logs')
    uploads_dir = pathlib.Path('uploads')
    results_dir = pathlib.Path('results')
    tmp_dir = pathlib.Path('tmp')
    
    for directory in [logs_dir, uploads_dir, results_dir, tmp_dir]:
        directory.mkdir(exist_ok=True)
        server.log.info(f"Ensured directory exists: {directory}")

def post_fork(server, worker):
    """
    Hook function that executes after a worker has been forked.
    
    Args:
        server: The Gunicorn server instance
        worker: The worker instance
    """
    server.log.info(f"Worker {worker.pid} spawned")
    
    # Configure worker-specific settings
    worker_tmp_dir = pathlib.Path('tmp') / f"worker-{worker.pid}"
    worker_tmp_dir.mkdir(exist_ok=True)
    
    # Set concurrency limits based on configuration
    max_jobs = web_interface_config.get('job_management', {}).get('limits', {}).get('max_active_jobs', 10)
    server.log.info(f"Worker {worker.pid} configured with max_jobs={max_jobs}")

def worker_exit(server, worker):
    """
    Hook function that executes when a worker exits.
    
    Args:
        server: The Gunicorn server instance
        worker: The worker instance
    """
    server.log.info(f"Worker {worker.pid} exited")
    
    # Perform cleanup operations
    worker_tmp_dir = pathlib.Path('tmp') / f"worker-{worker.pid}"
    if worker_tmp_dir.exists():
        import shutil
        try:
            shutil.rmtree(worker_tmp_dir)
            server.log.info(f"Cleaned up worker temporary directory: {worker_tmp_dir}")
        except Exception as e:
            server.log.error(f"Error cleaning up worker directory: {str(e)}")

def on_exit(server):
    """
    Hook function that executes when Gunicorn exits.
    
    Args:
        server: The Gunicorn server instance
    """
    server.log.info("JSON to Excel Web Interface shutting down")
    
    # Perform final cleanup operations
    # Note: We don't remove all temp files here to preserve in-progress downloads
    # Temp file cleanup should be handled by a scheduled task
    server.log.info("Shutdown complete")