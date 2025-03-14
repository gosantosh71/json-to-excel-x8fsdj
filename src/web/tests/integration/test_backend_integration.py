# Standard library imports
import os  # v: built-in - For file path operations
import tempfile  # v: built-in - For creating temporary files and directories
import unittest.mock  # v: built-in - For creating mock objects in tests

# Third-party library imports
import pytest  # v: 7.3.0+ - Testing framework for writing and running tests

# Local application imports
from src.web.backend_interface.conversion_client import ConversionClient  # For interacting with backend conversion services
from src.web.backend_interface.service_client import ServiceClient  # For base client for backend service interactions
from src.web.models.conversion_job import ConversionJob  # For tracking conversion jobs
from src.web.models.conversion_options import ConversionOptions  # For handling conversion configuration options
from src.web.models.upload_file import UploadFile  # For representing uploaded files
from src.backend.models.error_response import ErrorResponse  # For handling standardized error responses
from src.web.tests.fixtures.file_fixtures import create_test_upload_file, get_sample_json_path  # For creating test upload files
from src.web.tests.fixtures.conversion_fixtures import create_test_conversion_options, create_test_conversion_job, create_test_form_data  # For creating test conversion options


@pytest.fixture
def setup_test_environment():
    """Sets up the test environment with temporary directories and files."""
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "test_input.json")
    output_path = os.path.join(temp_dir, "test_output.xlsx")
    return {"temp_dir": temp_dir, "input_path": input_path, "output_path": output_path}


@pytest.fixture
def teardown_test_environment(setup_test_environment):
    """Cleans up the test environment after tests are complete."""
    test_env = setup_test_environment
    yield
    # Remove temporary files created during tests
    if os.path.exists(test_env["input_path"]):
        os.remove(test_env["input_path"])
    if os.path.exists(test_env["output_path"]):
        os.remove(test_env["output_path"])
    # Remove temporary directories created during tests
    if os.path.exists(test_env["temp_dir"]):
        shutil.rmtree(test_env["temp_dir"])


@pytest.fixture
def create_conversion_client():
    """Creates a ConversionClient instance for testing."""
    return ConversionClient()


def test_conversion_client_initialization():
    """Tests that the ConversionClient can be properly initialized."""
    client = ConversionClient()
    assert client is not None
    assert isinstance(client, ConversionClient)


def test_validate_file(create_conversion_client, get_sample_json_path):
    """Tests that the ConversionClient can validate JSON files correctly."""
    client = create_conversion_client
    sample_file_path = get_sample_json_path()
    success, details = client.validate_file(sample_file_path)
    assert success is True
    assert "structure" in details


def test_validate_invalid_file(create_conversion_client, setup_test_environment):
    """Tests that the ConversionClient correctly identifies invalid JSON files."""
    client = create_conversion_client
    test_env = setup_test_environment
    invalid_file_path = test_env["input_path"]
    with open(invalid_file_path, "w") as f:
        f.write("invalid json")
    success, details = client.validate_file(invalid_file_path)
    assert success is False
    assert "errors" in details


def test_convert_file(create_conversion_client, get_sample_json_path, setup_test_environment):
    """Tests that the ConversionClient can convert JSON files to Excel correctly."""
    client = create_conversion_client
    sample_file_path = get_sample_json_path()
    test_env = setup_test_environment
    output_path = test_env["output_path"]
    success, summary, error = client.convert_file(sample_file_path, output_path)
    assert success is True
    assert os.path.exists(output_path)
    assert "input" in summary
    assert "output" in summary


def test_convert_file_with_options(create_conversion_client, get_sample_json_path, setup_test_environment, create_test_conversion_options):
    """Tests that the ConversionClient respects conversion options."""
    client = create_conversion_client
    sample_file_path = get_sample_json_path()
    test_env = setup_test_environment
    output_path = test_env["output_path"]
    options = create_test_conversion_options
    options_dict = options.to_dict()
    success, summary, error = client.convert_file(sample_file_path, output_path, options_dict)
    assert success is True
    assert os.path.exists(output_path)
    assert "input" in summary
    assert "output" in summary
    assert summary["output"]["file_path"] == output_path


def test_convert_file_to_bytes(create_conversion_client, get_sample_json_path):
    """Tests that the ConversionClient can convert JSON files to Excel bytes."""
    client = create_conversion_client
    sample_file_path = get_sample_json_path()
    excel_bytes, summary, error = client.convert_file_to_bytes(sample_file_path)
    assert excel_bytes is not None
    assert isinstance(excel_bytes, bytes)
    assert excel_bytes[:4] == b'PK\x03\x04'


def test_process_conversion_job(create_conversion_client, create_test_conversion_job, setup_test_environment):
    """Tests that the ConversionClient can process conversion jobs correctly."""
    client = create_conversion_client
    job = create_test_conversion_job
    test_env = setup_test_environment
    job.input_file.file_path = get_sample_json_path()
    success = client.process_conversion_job(job)
    assert success is True
    assert job.status.is_complete()
    assert job.output_file_path is not None


def test_process_form_data(create_conversion_client, create_test_form_data):
    """Tests that the ConversionClient can process form data into conversion options."""
    client = create_conversion_client
    form_data = create_test_form_data
    options = client.process_form_data(form_data)
    assert isinstance(options, dict)
    assert "sheet_name" in options
    assert "array_handling" in options
    assert options["sheet_name"] == "Test Sheet"


def test_error_handling(create_conversion_client, setup_test_environment):
    """Tests that the ConversionClient properly handles and reports errors."""
    client = create_conversion_client
    test_env = setup_test_environment
    non_existent_file = "non_existent_file.json"
    success, details = client.validate_file(non_existent_file)
    assert success is False
    assert "message" in details
    assert "error_code" in details


def test_integration_with_service_client():
    """Tests the integration between ConversionClient and ServiceClient."""
    # Create a mock ServiceClient
    mock_service_client = unittest.mock.Mock(spec=ServiceClient)

    # Configure the mock to return predetermined responses
    mock_service_client.validate_json_file.return_value = (True, {"status": "success"})
    mock_service_client.convert_file.return_value = (True, {"status": "success"}, None)

    # Create a ConversionClient that uses the mock ServiceClient
    conversion_client = ConversionClient()
    conversion_client._service_client = mock_service_client

    # Call methods on the ConversionClient
    success, details = conversion_client.validate_file("test_file.json")
    assert success is True
    assert "status" in details

    success, summary, error = conversion_client.convert_file("test_file.json", "output.xlsx")
    assert success is True
    assert "status" in summary
    assert error is None

    # Verify that the ServiceClient methods are called with correct parameters
    mock_service_client.validate_json_file.assert_called_with("test_file.json")
    mock_service_client.convert_file.assert_called_with("test_file.json", "output.xlsx", None)

    # Verify that the ConversionClient correctly processes the ServiceClient responses
    assert success is True
    assert "status" in summary