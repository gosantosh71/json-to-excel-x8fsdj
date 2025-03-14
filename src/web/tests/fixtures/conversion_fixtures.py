# Standard library imports
import unittest.mock  # v: built-in - For creating mock objects in test fixtures
from typing import Dict, Optional  # v: built-in - For type hints in fixture functions

# Third-party library imports
import pytest  # v: 7.3.0+ - For creating test fixtures

# Local application imports
from src.backend.models.excel_options import ArrayHandlingStrategy, ExcelOptions  # For defining array handling strategies in test fixtures
from src.web.models.conversion_job import ConversionJob  # For creating test conversion job instances
from src.web.models.conversion_options import ConversionOptions, DefaultConversionOptions  # For creating test conversion option instances
from src.web.services.conversion_service import ConversionService  # For mocking the conversion service in tests
from src.web.tests.fixtures.file_fixtures import create_test_upload_file  # For creating test upload file instances
from src.web.tests.fixtures.job_fixtures import create_test_job  # For creating test job instances

TEST_CONVERSION_OPTIONS = '{"sheet_name": "Test Sheet", "array_handling": "expand", "format_headers": True, "auto_column_width": True, "apply_data_formatting": True}'
TEST_EXCEL_OPTIONS = '{"sheet_name": "Test Sheet", "array_handling": "EXPAND", "format_headers": True, "freeze_header_row": False, "auto_column_width": True, "apply_data_formatting": True}'


@pytest.fixture
def create_test_conversion_options(
    sheet_name: Optional[str] = None,
    array_handling: Optional[str] = None,
    format_headers: Optional[bool] = None,
    auto_column_width: Optional[bool] = None,
    apply_data_formatting: Optional[bool] = None,
) -> ConversionOptions:
    """
    Creates a ConversionOptions instance with test values for use in tests.

    Args:
        sheet_name (Optional[str]): The sheet name for the conversion options.
        array_handling (Optional[str]): The array handling strategy for the conversion options.
        format_headers (Optional[bool]): Whether to format headers for the conversion options.
        auto_column_width (Optional[bool]): Whether to automatically adjust column width for the conversion options.
        apply_data_formatting (Optional[bool]): Whether to apply data formatting for the conversion options.

    Returns:
        ConversionOptions: A ConversionOptions instance with test values
    """
    test_sheet_name = sheet_name if sheet_name is not None else "Test Sheet"
    test_array_handling = array_handling if array_handling is not None else "expand"
    test_format_headers = format_headers if format_headers is not None else True
    test_auto_column_width = auto_column_width if auto_column_width is not None else True
    test_apply_data_formatting = apply_data_formatting if apply_data_formatting is not None else True

    return ConversionOptions(
        sheet_name=test_sheet_name,
        array_handling=test_array_handling,
        format_headers=test_format_headers,
        auto_column_width=test_auto_column_width,
        apply_data_formatting=test_apply_data_formatting,
    )


@pytest.fixture
def create_default_conversion_options() -> ConversionOptions:
    """
    Creates a ConversionOptions instance with default values for use in tests.

    Returns:
        ConversionOptions: A ConversionOptions instance with default values
    """
    return DefaultConversionOptions.get_defaults()


@pytest.fixture
def create_test_excel_options(
    sheet_name: Optional[str] = None,
    array_handling: Optional[ArrayHandlingStrategy] = None,
    format_headers: Optional[bool] = None,
    auto_column_width: Optional[bool] = None,
) -> ExcelOptions:
    """
    Creates an ExcelOptions instance with test values for use in tests.

    Args:
        sheet_name (Optional[str]): The sheet name for the Excel options.
        array_handling (Optional[ArrayHandlingStrategy]): The array handling strategy for the Excel options.
        format_headers (Optional[bool]): Whether to format headers for the Excel options.
        auto_column_width (Optional[bool]): Whether to automatically adjust column width for the Excel options.

    Returns:
        ExcelOptions: An ExcelOptions instance with test values
    """
    test_sheet_name = sheet_name if sheet_name is not None else "Test Sheet"
    test_array_handling = array_handling if array_handling is not None else ArrayHandlingStrategy.EXPAND
    test_format_headers = format_headers if format_headers is not None else True
    test_auto_column_width = auto_column_width if auto_column_width is not None else True

    return ExcelOptions(
        sheet_name=test_sheet_name,
        array_handling=test_array_handling,
        format_headers=test_format_headers,
        auto_column_width=test_auto_column_width,
    )


@pytest.fixture
def create_test_conversion_job_with_options(options: ConversionOptions) -> ConversionJob:
    """
    Creates a ConversionJob instance with specified conversion options for use in tests.

    Args:
        options (ConversionOptions): The conversion options to use for the job.

    Returns:
        ConversionJob: A ConversionJob instance with the specified options
    """
    test_upload_file = create_test_upload_file()
    test_job = create_test_job(options=options)
    return test_job


@pytest.fixture
def create_test_conversion_job() -> ConversionJob:
    """
    Creates a ConversionJob instance with default conversion options for use in tests.

    Returns:
        ConversionJob: A ConversionJob instance with default options
    """
    default_options = create_default_conversion_options()
    test_job = create_test_conversion_job_with_options(options=default_options)
    return test_job


@pytest.fixture
def create_test_conversion_options_dict(
    sheet_name: Optional[str] = None, array_handling: Optional[str] = None
) -> Dict[str, str]:
    """
    Creates a dictionary representation of conversion options for use in tests.

    Args:
        sheet_name (Optional[str]): The sheet name for the conversion options.
        array_handling (Optional[str]): The array handling strategy for the conversion options.

    Returns:
        Dict[str, str]: A dictionary representation of conversion options
    """
    test_conversion_options = create_test_conversion_options(
        sheet_name=sheet_name, array_handling=array_handling
    )
    return test_conversion_options.to_dict()


@pytest.fixture
def create_test_form_data(
    sheet_name: Optional[str] = None,
    array_handling: Optional[str] = None,
    format_headers: Optional[bool] = None,
    auto_column_width: Optional[bool] = None,
) -> Dict[str, str]:
    """
    Creates a dictionary representing form data for conversion options in tests.

    Args:
        sheet_name (Optional[str]): The sheet name for the conversion options.
        array_handling (Optional[str]): The array handling strategy for the conversion options.
        format_headers (Optional[bool]): Whether to format headers for the conversion options.
        auto_column_width (Optional[bool]): Whether to automatically adjust column width for the conversion options.

    Returns:
        Dict[str, str]: A dictionary representing form data for conversion options
    """
    form_data = {}

    form_data["sheet_name"] = sheet_name if sheet_name is not None else "Test Sheet"
    form_data["array_handling"] = array_handling if array_handling is not None else "expand"
    form_data["format_headers"] = "on" if format_headers is not None and format_headers else ""
    form_data["auto_column_width"] = "on" if auto_column_width is not None and auto_column_width else ""

    return form_data


@pytest.fixture
def mock_conversion_service(
    success: bool = True, result: Optional[Dict] = None, error: Optional[Dict] = None
) -> unittest.mock.Mock:
    """
    Creates a mock ConversionService for testing conversion functionality.

    Args:
        success (bool): Whether the conversion should succeed.
        result (Optional[Dict]): The result of the conversion.
        error (Optional[Dict]): The error of the conversion.

    Returns:
        unittest.mock.Mock: A mock ConversionService with predetermined responses
    """
    mock_service = unittest.mock.Mock(spec=ConversionService)
    mock_service.process_conversion_job.return_value = success
    mock_service.validate_conversion_input.return_value = (success, result, error)
    mock_service.convert_file.return_value = (success, result, error)
    return mock_service


@pytest.fixture
def create_conversion_result_summary(
    rows: int = 100, columns: int = 10, duration_seconds: float = 2.5
) -> Dict[str, float]:
    """
    Creates a sample conversion result summary for testing.

    Args:
        rows (int): The number of rows in the converted Excel file.
        columns (int): The number of columns in the converted Excel file.
        duration_seconds (float): The duration of the conversion process in seconds.

    Returns:
        Dict[str, float]: A dictionary containing conversion result summary
    """
    summary = {"rows": rows, "columns": columns, "duration_seconds": duration_seconds}
    summary["file_size_mb"] = 1.2
    summary["timestamp"] = "2024-01-01T00:00:00"
    return summary


class MockConversionClient:
    """
    A mock implementation of ConversionClient for testing without backend dependencies.
    """

    def __init__(
        self,
        validation_success: bool = True,
        conversion_success: bool = True,
        validation_result: Optional[Dict] = None,
        conversion_result: Optional[Dict] = None,
        error_response: Optional[Dict] = None,
    ):
        """
        Initializes a new MockConversionClient with predetermined responses.

        Args:
            validation_success (bool): Whether file validation should succeed.
            conversion_success (bool): Whether file conversion should succeed.
            validation_result (Optional[Dict]): The result of file validation.
            conversion_result (Optional[Dict]): The result of file conversion.
            error_response (Optional[Dict]): The error response.
        """
        self.validation_success = validation_success
        self.conversion_success = conversion_success
        self.validation_result = validation_result or {}
        self.conversion_result = conversion_result or {}
        self.error_response = error_response

    def validate_file(self, file_path: str) -> Tuple[bool, Dict, Optional[Dict]]:
        """
        Mock implementation of validate_file that returns predetermined results.

        Args:
            file_path (str): The path to the file to validate.

        Returns:
            Tuple[bool, Dict, Optional[Dict]]: (validation_success, validation_result, error_response)
        """
        return (self.validation_success, self.validation_result, self.error_response)

    def convert_file(
        self, input_path: str, output_path: str, options: ExcelOptions
    ) -> Tuple[bool, Dict, Optional[Dict]]:
        """
        Mock implementation of convert_file that returns predetermined results.

        Args:
            input_path (str): The path to the input file.
            output_path (str): The path to the output file.
            options (ExcelOptions): The conversion options.

        Returns:
            Tuple[bool, Dict, Optional[Dict]]: (conversion_success, conversion_result, error_response)
        """
        return (self.conversion_success, self.conversion_result, self.error_response)

    def process_conversion_job(self, job: ConversionJob) -> bool:
        """
        Mock implementation of process_conversion_job that returns predetermined results.

        Args:
            job (ConversionJob): The conversion job to process.

        Returns:
            bool: Success flag
        """
        return self.conversion_success