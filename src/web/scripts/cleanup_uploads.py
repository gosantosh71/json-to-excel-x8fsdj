#!/usr/bin/env python3
"""
A utility script that performs automated cleanup of old uploaded JSON files 
in the web interface of the JSON to Excel Conversion Tool.
This script can be run manually or scheduled as a cron job to ensure the 
upload directory doesn't accumulate unnecessary files.
"""

import os
import sys
import argparse
from datetime import datetime

from ...backend.logger import get_logger
from ..config.upload_config import upload_config
from ..utils.file_utils import cleanup_old_files
from ..utils.path_utils import ensure_upload_directory, path_utils
from ..services.storage_service import StorageService

# Initialize logger for this script
logger = get_logger(__name__)

# Constants from configuration
UPLOAD_FOLDER = upload_config['upload_folder']
DEFAULT_MAX_AGE_MINUTES = upload_config['file_cleanup']['max_age_minutes']

def parse_arguments():
    """
    Parses command line arguments for the script.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Cleanup old uploaded JSON files in the web interface.'
    )
    parser.add_argument(
        '--max-age', 
        type=int, 
        default=DEFAULT_MAX_AGE_MINUTES,
        help=f'Maximum age of files in minutes (default: {DEFAULT_MAX_AGE_MINUTES})'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Simulate cleanup without deleting files'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable detailed output'
    )
    return parser.parse_args()

def main():
    """
    Main function that runs the file cleanup process.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Log the start of the cleanup process
    logger.info("Starting uploaded files cleanup process")
    
    # Ensure the upload directory exists
    if not ensure_upload_directory():
        logger.error(f"Upload directory {UPLOAD_FOLDER} does not exist and could not be created")
        return 1
    
    # Get the max_age from arguments or use default
    max_age = args.max_age
    
    # Log dry run mode if enabled
    if args.dry_run:
        logger.info(f"DRY RUN: Simulating cleanup only - files older than {max_age} minutes will not be deleted")
    
    try:
        # Using direct file_utils approach
        if args.dry_run:
            # In dry-run mode, simulate deletion without actually removing files
            count = 0
            deleted_files = []
            cutoff_time = datetime.now().timestamp() - (max_age * 60)
            
            # Iterate through files in the upload directory
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                    
                # Check if the file is older than the cutoff
                mtime = os.path.getmtime(file_path)
                if mtime < cutoff_time:
                    count += 1
                    deleted_files.append(file_path)
                    
            logger.info(f"DRY RUN: Would delete {count} files")
        else:
            # Actually delete the files using the utility function
            count, deleted_files = cleanup_old_files(max_age)
            logger.info(f"Successfully deleted {count} files")
        
        # If verbose is enabled, log the list of deleted/would-be-deleted files
        if args.verbose:
            if len(deleted_files) > 0:
                logger.info(f"{'Would delete' if args.dry_run else 'Deleted'} the following files:")
                for file_path in deleted_files:
                    logger.info(f"  {file_path}")
            else:
                logger.info("No files found that match the deletion criteria")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error occurred during cleanup: {str(e)}")
        if args.verbose:
            # In verbose mode, include the full stack trace
            import traceback
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())