"""
Initialization module for the test fixtures package in the web interface component of the JSON to Excel Conversion Tool.
This file exports commonly used test fixtures from the various fixture modules, making them available for direct import from the fixtures package.
"""

import os  # v: built-in - For file path operations in test fixtures
from .file_fixtures import (  # Import file fixture for creating test upload files
    create_test_upload_file,
    setup_test_upload_folder,
    teardown_test_upload_folder,
    get_sample_json_path,
    create_test_file_storage,
    create_test_json_file_storage,
    MockFileStorage,
)
from .conversion_fixtures import (  # Import conversion fixture for creating test conversion options
    create_test_conversion_options,
    create_default_conversion_options,
    MockConversionClient,
    mock_conversion_service,
)
from .job_fixtures import (  # Import job fixture for creating test conversion jobs
    create_test_conversion_job,
    create_pending_job,
    create_processing_job,
    create_completed_job,
    create_failed_job,
    MockJobManager,
    mock_job_manager,
)

FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))  # Constant for the fixtures directory path
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')  # Constant for the sample data directory path
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')  # Constant for the expected output directory path

__all__ = [  # Expose all imported fixtures for direct use
    'create_test_upload_file',
    'setup_test_upload_folder',
    'teardown_test_upload_folder',
    'get_sample_json_path',
    'create_test_file_storage',
    'create_test_json_file_storage',
    'MockFileStorage',
    'create_test_conversion_options',
    'create_default_conversion_options',
    'create_test_conversion_job',
    'create_pending_job',
    'create_processing_job',
    'create_completed_job',
    'create_failed_job',
    'MockJobManager',
    'mock_job_manager',
    'MockConversionClient',
    'mock_conversion_service',
    'FIXTURES_DIR',
    'SAMPLE_DATA_DIR',
    'EXPECTED_OUTPUT_DIR'
]