# Standard library imports
import unittest.mock  # v: built-in - For creating mock objects in test fixtures
from typing import Dict, Optional  # v: built-in - For type hints in fixture functions
import os  # v: built-in - For file path operations in tests
import tempfile  # v: built-in - For creating temporary files and directories in tests

# Third-party library imports
import pytest  # v: 7.3.0+ - For creating test fixtures

# Local application imports
from src.web.services.conversion_service import ConversionService, create_conversion_error  # For testing the service class
from src.web.models.conversion_options import ConversionOptions  # For testing conversion options handling
from src.web.models.conversion_job import ConversionJob  # For testing job processing functionality
from src.web.models.job_status import JobStatusEnum  # For verifying job status transitions
from src.backend.models.error_response import ErrorCategory, ErrorSeverity, ErrorResponse  # For testing error categorization
from src.web.tests.fixtures.conversion_fixtures import create_test_conversion_job, create_test_conversion_options, create_test_form_data, create_conversion_result_summary, MockConversionClient  # For creating test conversion jobs


class TestConversionService:
    """
    Test class for the ConversionService, containing unit tests for all its methods and functionality.
    """

    def setup_method(self, method):
        """
        Set up test environment before each test method.

        Args:
            method: The test method being executed.
        """
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        # Create mock objects for dependencies (FileService, StorageService, ConversionClient)
        self.mock_file_service = unittest.mock.Mock()
        self.mock_storage_service = unittest.mock.Mock()
        self.mock_conversion_client = MockConversionClient()
        # Create a ConversionService instance with the mock dependencies
        self.service = ConversionService(
            file_service=self.mock_file_service,
            storage_service=self.mock_storage_service,
            conversion_client=self.mock_conversion_client
        )

    def teardown_method(self, method):
        """
        Clean up test environment after each test method.

        Args:
            method: The test method being executed.
        """
        # Remove temporary directory and files created during tests
        try:
            shutil.rmtree(self.temp_dir)
        except (OSError, FileNotFoundError):
            pass

    def test_process_conversion_job_success(self):
        """
        Test successful processing of a conversion job.
        """
        # Configure mock ConversionClient to return success
        self.mock_conversion_client.conversion_success = True
        # Create a test job using fixtures
        test_job = create_test_conversion_job()
        # Call self.service.process_conversion_job with the test job
        result = self.service.process_conversion_job(test_job)
        # Assert that the job was processed successfully
        assert result is True
        # Verify that the job status was updated correctly
        assert test_job.status.status == JobStatusEnum.COMPLETED
        # Verify that the output file path and name were set correctly
        assert test_job.output_file_path is not None
        assert test_job.output_file_name is not None

    def test_process_conversion_job_validation_failure(self):
        """
        Test handling of validation failures during job processing.
        """
        # Configure mock ConversionClient to return validation failure
        self.mock_conversion_client.validation_success = False
        # Create a test job using fixtures
        test_job = create_test_conversion_job()
        # Call self.service.process_conversion_job with the test job
        result = self.service.process_conversion_job(test_job)
        # Assert that the method returns False
        assert result is False
        # Verify that the job status was updated to FAILED
        assert test_job.status.status == JobStatusEnum.FAILED
        # Verify that the job has the correct error information
        assert test_job.status.error is not None

    def test_process_conversion_job_conversion_failure(self):
        """
        Test handling of conversion failures during job processing.
        """
        # Configure mock ConversionClient to pass validation but fail conversion
        self.mock_conversion_client.validation_success = True
        self.mock_conversion_client.conversion_success = False
        # Create a test job using fixtures
        test_job = create_test_conversion_job()
        # Call self.service.process_conversion_job with the test job
        result = self.service.process_conversion_job(test_job)
        # Assert that the method returns False
        assert result is False
        # Verify that the job status was updated to FAILED
        assert test_job.status.status == JobStatusEnum.FAILED
        # Verify that the job has the correct error information
        assert test_job.status.error is not None

    def test_validate_conversion_input_success(self):
        """
        Test successful validation of conversion input.
        """
        # Configure mock ConversionClient to return validation success
        self.mock_conversion_client.validation_success = True
        # Create a test job using fixtures
        test_job = create_test_conversion_job()
        # Call self.service.validate_conversion_input with the test job
        success, details, error = self.service.validate_conversion_input(test_job)
        # Assert that the method returns (True, validation_details, None)
        assert success is True
        assert error is None
        # Verify that the validation details contain expected information
        assert isinstance(details, dict)

    def test_validate_conversion_input_failure(self):
        """
        Test handling of validation failures.
        """
        # Configure mock ConversionClient to return validation failure
        self.mock_conversion_client.validation_success = False
        # Create a test job using fixtures
        test_job = create_test_conversion_job()
        # Call self.service.validate_conversion_input with the test job
        success, details, error = self.service.validate_conversion_input(test_job)
        # Assert that the method returns (False, error_details, error_response)
        assert success is False
        assert error is not None
        # Verify that the error_response has the correct category and severity
        assert error.category == ErrorCategory.VALIDATION_ERROR
        assert error.severity == ErrorSeverity.ERROR

    def test_convert_file_success(self):
        """
        Test successful direct file conversion.
        """
        # Configure mock ConversionClient to return conversion success
        self.mock_conversion_client.conversion_success = True
        # Create temporary input and output file paths
        input_path = os.path.join(self.temp_dir, "input.json")
        output_path = os.path.join(self.temp_dir, "output.xlsx")
        # Create test conversion options
        options = create_test_conversion_options()
        # Call self.service.convert_file with the paths and options
        success, summary, error = self.service.convert_file(input_path, output_path, options)
        # Assert that the method returns (True, conversion_summary, None)
        assert success is True
        assert error is None
        # Verify that the conversion summary contains expected information
        assert isinstance(summary, dict)

    def test_convert_file_failure(self):
        """
        Test handling of conversion failures in direct file conversion.
        """
        # Configure mock ConversionClient to return conversion failure
        self.mock_conversion_client.conversion_success = False
        # Create temporary input and output file paths
        input_path = os.path.join(self.temp_dir, "input.json")
        output_path = os.path.join(self.temp_dir, "output.xlsx")
        # Create test conversion options
        options = create_test_conversion_options()
        # Call self.service.convert_file with the paths and options
        success, details, error = self.service.convert_file(input_path, output_path, options)
        # Assert that the method returns (False, error_details, error_response)
        assert success is False
        assert error is not None
        # Verify that the error_response has the correct category and severity
        assert error.category == ErrorCategory.VALIDATION_ERROR
        assert error.severity == ErrorSeverity.ERROR

    def test_convert_file_input_not_found(self):
        """
        Test handling of missing input files in direct file conversion.
        """
        # Create a non-existent input file path
        input_path = os.path.join(self.temp_dir, "nonexistent.json")
        # Create a valid output file path
        output_path = os.path.join(self.temp_dir, "output.xlsx")
        # Create test conversion options
        options = create_test_conversion_options()
        # Call self.service.convert_file with the paths and options
        success, details, error = self.service.convert_file(input_path, output_path, options)
        # Assert that the method returns (False, error_details, error_response)
        assert success is False
        assert error is not None
        # Verify that the error_response has the correct category and message about file not found
        assert error.category == ErrorCategory.INPUT_ERROR
        assert "Input file not found" in error.message

    def test_generate_output_path(self):
        """
        Test generation of output file paths.
        """
        # Call self.service.generate_output_path with a job_id and original filename
        job_id = "test_job_id"
        original_filename = "data.json"
        output_path, output_filename = self.service.generate_output_path(job_id, original_filename)
        # Assert that the returned path contains the job_id
        assert job_id in output_path
        # Assert that the returned path has the .xlsx extension
        assert output_path.endswith(".xlsx")
        # Assert that the returned path is in the configured output directory
        assert "conversion_output" in output_path

    def test_process_form_data(self):
        """
        Test processing of web form data into conversion options.
        """
        # Create test form data with specific values
        form_data = {
            "sheet_name": "Custom Sheet",
            "array_handling": "join",
            "format_headers": "on",
            "auto_column_width": "on",
        }
        # Call self.service.process_form_data with the test form data
        conversion_options = self.service.process_form_data(form_data)
        # Assert that the returned ConversionOptions has the correct values from the form data
        assert conversion_options.sheet_name == "Custom Sheet"
        assert conversion_options.array_handling == "join"
        # Verify that the sheet_name, array_handling, and other options are correctly set
        assert conversion_options.format_headers is True
        assert conversion_options.auto_column_width is True

@pytest.mark.parametrize('job_fixture', [pytest.lazy_fixture('create_test_conversion_job')])
def test_process_conversion_job_success(job_fixture, mocker):
    """Tests that the process_conversion_job method successfully processes a conversion job when the backend conversion is successful."""
    # Arrange
    mock_conversion_client = mocker.MagicMock()
    mock_conversion_client.convert_file.return_value = (True, {}, None)
    service = ConversionService(conversion_client=mock_conversion_client)

    # Act
    service.process_conversion_job(job_fixture)

    # Assert
    assert job_fixture.status.status == JobStatusEnum.COMPLETED
    mock_conversion_client.convert_file.assert_called_once()


class TestCreateConversionError:
    """Test class for the create_conversion_error function, which creates standardized error responses."""

    def test_create_conversion_error_basic(self):
        """Test creation of a basic error response."""
        # Create a test error message
        test_message = "Test error message"
        # Call create_conversion_error with the message and basic parameters
        error_response = create_conversion_error(
            message=test_message,
            exception=None,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
        # Assert that the returned ErrorResponse has the correct message, category, and severity
        assert error_response.message == test_message
        assert error_response.category == ErrorCategory.VALIDATION_ERROR
        assert error_response.severity == ErrorSeverity.ERROR

    def test_create_conversion_error_with_exception(self):
        """Test creation of an error response with exception details."""
        # Create a test exception with specific details
        test_exception = ValueError("Invalid value")
        # Call create_conversion_error with the exception
        error_response = create_conversion_error(
            message="Test error",
            exception=test_exception,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
        # Assert that the returned ErrorResponse contains context information from the exception
        assert "exception_type" in error_response.context
        assert "exception_message" in error_response.context
        # Verify that the exception details are included in the error context
        assert error_response.context["exception_type"] == "ValueError"
        assert error_response.context["exception_message"] == "Invalid value"

    def test_create_conversion_error_with_resolution_steps(self):
        """Test that appropriate resolution steps are included in the error response."""
        # Call create_conversion_error with different error categories
        validation_error = create_conversion_error(
            message="Validation error",
            exception=None,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
        transformation_error = create_conversion_error(
            message="Transformation error",
            exception=None,
            category=ErrorCategory.TRANSFORMATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
        # Assert that each error response includes appropriate resolution steps based on the category
        assert "Check the input JSON file for syntax errors" in validation_error.resolution_steps
        assert "Review the transformation settings" in transformation_error.resolution_steps
        # Verify that validation errors include steps about checking JSON format
        assert "Ensure the JSON structure matches the expected format" in validation_error.resolution_steps
        # Verify that transformation errors include steps about simplifying complex structures
        assert "Simplify the JSON structure if possible" in transformation_error.resolution_steps