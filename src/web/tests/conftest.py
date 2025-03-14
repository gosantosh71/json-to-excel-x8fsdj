"""
Pytest configuration file for the web interface component of the JSON to Excel Conversion Tool.
This file defines fixtures, configuration, and setup/teardown procedures that are shared across
different test modules in the web interface test suite.
"""

import pytest  # v: 7.3.0+ - Testing framework for creating fixtures and test configuration
import os  # v: built-in - For file path operations in test fixtures
import tempfile  # v: built-in - For creating temporary directories and files in tests
from flask import Flask  # v: 2.3.0+ - For creating test clients and application contexts

from .fixtures.file_fixtures import create_test_upload_file, setup_test_upload_folder, teardown_test_upload_folder, MockFileStorage, create_test_json_file_storage  # src/web/tests/fixtures/file_fixtures.py - For creating test upload file instances in fixtures
from .fixtures.conversion_fixtures import create_test_conversion_options, create_default_conversion_options  # src/web/tests/fixtures/conversion_fixtures.py - For creating test conversion options
from .fixtures.job_fixtures import create_test_conversion_job, create_pending_job, create_completed_job  # src/web/tests/fixtures/job_fixtures.py - For creating test conversion jobs
from '../../app' import create_app  # src/web/app.py - For creating Flask application instances for testing

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_DIR = os.path.join(TEST_DIR, 'fixtures', 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(TEST_DIR, 'fixtures', 'expected_output')


def pytest_configure(config):
    """
    Configures pytest for the web interface tests by registering custom markers.

    Args:
        config: Pytest configuration object

    Returns:
        None: No return value
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test.")  # Register the 'unit' marker for unit tests
    config.addinivalue_line("markers", "integration: mark test as an integration test.")  # Register the 'integration' marker for integration tests
    config.addinivalue_line("markers", "functional: mark test as a functional test.")  # Register the 'functional' marker for functional tests
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test.")  # Register the 'e2e' marker for end-to-end tests


def get_sample_json_path(filename: str) -> str:
    """
    Returns the absolute path to a sample JSON file in the test fixtures.

    Args:
        filename: Name of the sample JSON file

    Returns:
        Absolute path to the sample JSON file
    """
    sample_path = os.path.join(SAMPLE_DATA_DIR, filename)  # Construct the path to the specified sample JSON file
    return os.path.abspath(sample_path)  # Return the absolute path


def get_expected_excel_path(filename: str) -> str:
    """
    Returns the absolute path to an expected Excel output file in the test fixtures.

    Args:
        filename: Name of the expected Excel file

    Returns:
        Absolute path to the expected Excel file
    """
    expected_path = os.path.join(EXPECTED_OUTPUT_DIR, filename)  # Construct the path to the specified expected Excel file
    return os.path.abspath(expected_path)  # Return the absolute path


@pytest.fixture
def app() -> Flask:
    """
    Creates a Flask application instance configured for testing.

    Args:
        None

    Returns:
        Flask application instance
    """
    flask_app = create_app("testing")  # Create a Flask application using create_app() with testing configuration
    flask_app.config.update({  # Configure the app for testing (disable CSRF, set testing flag)
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })

    yield flask_app  # Return the configured app


@pytest.fixture
def client(app: Flask):
    """
    Creates a test client for the Flask application.

    Args:
        app: Flask application instance

    Returns:
        Flask test client
    """
    return app.test_client()  # Create a test client from the app fixture


@pytest.fixture
def app_context(app: Flask):
    """
    Creates an application context for the Flask application.

    Args:
        app: Flask application instance

    Returns:
        Flask application context
    """
    with app.app_context():  # Push an application context for the app fixture
        yield  # Yield the context for use in tests
        # Teardown occurs after the yield
        pass


@pytest.fixture
def test_upload_folder() -> str:
    """
    Sets up and tears down a test upload folder for file operations.

    Args:
        None

    Returns:
        Path to the test upload folder
    """
    test_folder = setup_test_upload_folder()  # Call setup_test_upload_folder() to create the test folder
    yield test_folder  # Yield the folder path for use in tests
    teardown_test_upload_folder()  # Call teardown_test_upload_folder() to clean up after tests


@pytest.fixture
def test_upload_file(test_upload_folder: str) -> MockFileStorage:
    """
    Creates a test upload file instance for testing.

    Args:
        test_upload_folder: Path to the test upload folder

    Returns:
        Test upload file instance
    """
    upload_file = create_test_upload_file()  # Create a test upload file using create_test_upload_file()
    upload_file.file_path = os.path.join(test_upload_folder, upload_file.file_path)  # Set the file path to be within the test upload folder
    return upload_file  # Return the created upload file instance


@pytest.fixture
def test_json_file(test_upload_folder: str) -> str:
    """
    Creates a test JSON file for testing file uploads.

    Args:
        test_upload_folder: Path to the test upload folder

    Returns:
        Path to the created JSON file
    """
    test_file = create_test_json_file_storage()  # Create a test JSON file storage using create_test_json_file_storage()
    file_path = os.path.join(test_upload_folder, test_file.filename)
    test_file.save(file_path)  # Save the file to the test upload folder
    return file_path  # Return the path to the saved file


@pytest.fixture
def test_conversion_job(test_upload_file) -> MockFileStorage:
    """
    Creates a test conversion job for testing the conversion process.

    Args:
        test_upload_file: A test upload file instance

    Returns:
        Test conversion job instance
    """
    conversion_job = create_test_conversion_job()  # Create a test conversion job using create_test_conversion_job()
    conversion_job.input_file = test_upload_file  # Set the input file to the test upload file
    return conversion_job  # Return the created conversion job instance