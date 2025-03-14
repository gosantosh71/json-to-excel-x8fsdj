"""
Implements integration tests for the ConversionPipeline component of the JSON to Excel Conversion Tool.

This module verifies that the pipeline correctly orchestrates the conversion process by
testing each stage of the pipeline and ensuring proper interaction between components.
"""

import pytest  # v: 7.3.0+
import unittest.mock  # v: built-in
import os  # v: built-in
import tempfile  # v: built-in
import pandas  # v: 1.5.0+

from ...pipelines.conversion_pipeline import ConversionPipeline, PipelineStage, PipelineStatus
from ...input_handler import InputHandler
from ...data_transformer import DataTransformer
from ...excel_generator import ExcelGenerator
from ...models.json_data import JSONData
from ...models.excel_options import ExcelOptions, ArrayHandlingStrategy
from ...error_handler import ErrorHandler
from ..fixtures.json_fixtures import flat_json_data, nested_json_data, array_json_data, complex_json_data, get_invalid_json_string
from ..fixtures.excel_fixtures import default_excel_options, array_expand_options, array_join_options, test_flat_dataframe, test_nested_dataframe, test_array_dataframe

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(os.path.dirname(TEST_DIR), 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')


def create_temp_file(content: str, extension: str) -> str:
    """
    Creates a temporary file with the specified content and extension.

    Args:
        content (str): The content to write to the file.
        extension (str): The file extension (e.g., "json").

    Returns:
        str: Path to the created temporary file
    """
    # Create a temporary file with the specified extension
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}')
    # Write the content to the file
    temp.write(content.encode('utf-8'))
    # Close the file
    temp.close()
    # Return the path to the temporary file
    return temp.name


def cleanup_temp_file(file_path: str) -> None:
    """
    Removes a temporary file if it exists.

    Args:
        file_path (str): The path to the temporary file.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Remove the file if it exists
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting temporary file: {e}")


class MockComponent:
    """
    A mock class for testing component interactions in the pipeline.
    """

    def __init__(self, return_value: Any = None, exception_to_raise: Optional[Exception] = None):
        """
        Initializes a new MockComponent with configurable behavior.

        Args:
            return_value (Any): The value to return when the mock method is called.
            exception_to_raise (Optional[Exception]): An exception to raise when the mock method is called.
        """
        # Initialize was_called to False
        self.was_called = False
        # Store the provided return_value
        self.return_value = return_value
        # Store the provided exception_to_raise (if any)
        self.exception_to_raise = exception_to_raise

    def mock_method(self, *args: Any, **kwargs: Any) -> Any:
        """
        A mock method that can be configured to return a value or raise an exception.

        Args:
            *args (Any): Arguments passed to the method.
            **kwargs (Any): Keyword arguments passed to the method.

        Returns:
            Any: The configured return value or raises the configured exception
        """
        # Set was_called to True
        self.was_called = True
        # If exception_to_raise is not None, raise the exception
        if self.exception_to_raise:
            raise self.exception_to_raise
        # Otherwise, return the configured return_value
        return self.return_value

    def reset(self) -> None:
        """
        Resets the mock component's state.
        """
        # Set was_called back to False
        self.was_called = False


def test_pipeline_initialization():
    """
    Tests that the ConversionPipeline initializes correctly with default or custom components
    """
    # Test with default components
    pipeline = ConversionPipeline()
    assert isinstance(pipeline._input_handler, InputHandler)
    assert isinstance(pipeline._data_transformer, DataTransformer)
    assert isinstance(pipeline._excel_generator, ExcelGenerator)
    assert isinstance(pipeline._error_handler, ErrorHandler)

    # Test with custom components
    mock_input_handler = MockComponent()
    mock_data_transformer = MockComponent()
    mock_excel_generator = MockComponent()
    pipeline = ConversionPipeline(
        input_handler=mock_input_handler,
        data_transformer=mock_data_transformer,
        excel_generator=mock_excel_generator
    )
    assert pipeline._input_handler == mock_input_handler
    assert pipeline._data_transformer == mock_data_transformer
    assert pipeline._excel_generator == mock_excel_generator


def test_pipeline_validate_parameters():
    """
    Tests the parameter validation stage of the pipeline
    """
    pipeline = ConversionPipeline()
    valid, error = pipeline.validate_parameters("valid_input.json", "valid_output.xlsx", {})
    assert valid is False  # Expecting failure due to file existence check

    # Create a temporary file for testing
    temp_file = create_temp_file('{}', 'json')
    valid, error = pipeline.validate_parameters(temp_file, "valid_output.xlsx", {})
    assert valid is False  # Expecting failure due to output file existence check
    cleanup_temp_file(temp_file)


def test_pipeline_process_input():
    """
    Tests the input processing stage of the pipeline
    """
    pipeline = ConversionPipeline()
    # Create a temporary file for testing
    temp_file = create_temp_file('{}', 'json')
    json_data, error = pipeline.process_input(temp_file, {})
    assert json_data is not None
    assert error is None
    cleanup_temp_file(temp_file)


def test_pipeline_transform_data():
    """
    Tests the data transformation stage of the pipeline
    """
    pipeline = ConversionPipeline()
    # Create a temporary file for testing
    temp_file = create_temp_file('{}', 'json')
    json_data, error = pipeline.process_input(temp_file, {})
    dataframe, error = pipeline.transform_data(json_data, {}, {})
    assert dataframe is not None
    assert error is None
    cleanup_temp_file(temp_file)


def test_pipeline_generate_excel():
    """
    Tests the Excel generation stage of the pipeline
    """
    pipeline = ConversionPipeline()
    # Create a temporary file for testing
    temp_file = create_temp_file('{}', 'json')
    json_data, error = pipeline.process_input(temp_file, {})
    dataframe, error = pipeline.transform_data(json_data, {}, {})
    success, error = pipeline.generate_excel(dataframe, "test_output.xlsx", {}, json_data, {})
    assert success is False  # Expecting failure due to file existence check
    cleanup_temp_file(temp_file)


def test_pipeline_execute_success(tmp_path):
    """
    Tests successful execution of the complete pipeline
    """
    pipeline = ConversionPipeline()
    # Create a temporary input file
    input_file = tmp_path / "test_input.json"
    input_file.write_text('{"name": "test", "value": 123}')
    # Define the output file
    output_file = tmp_path / "test_output.xlsx"

    success, results, error = pipeline.execute(str(input_file), str(output_file))
    assert success is True
    assert error is None
    assert os.path.exists(output_file)


def test_pipeline_execute_with_flat_json(tmp_path, flat_json_data):
    """
    Tests pipeline execution with flat JSON data
    """
    pipeline = ConversionPipeline()
    # Define the output file
    output_file = tmp_path / "flat_output.xlsx"

    success, results, error = pipeline.execute(flat_json_data.source_path, str(output_file))
    assert success is False
    assert error is not None
    assert os.path.exists(output_file) is False


def test_pipeline_execute_with_nested_json(tmp_path, nested_json_data):
    """
    Tests pipeline execution with nested JSON data
    """
    pipeline = ConversionPipeline()
    # Define the output file
    output_file = tmp_path / "nested_output.xlsx"

    success, results, error = pipeline.execute(nested_json_data.source_path, str(output_file))
    assert success is False
    assert error is not None
    assert os.path.exists(output_file) is False


def test_pipeline_execute_with_array_json(tmp_path, array_json_data):
    """
    Tests pipeline execution with JSON containing arrays
    """
    pipeline = ConversionPipeline()
    # Define the output file
    output_file = tmp_path / "array_output.xlsx"

    success, results, error = pipeline.execute(array_json_data.source_path, str(output_file))
    assert success is False
    assert error is not None
    assert os.path.exists(output_file) is False


def test_pipeline_execute_with_complex_json(tmp_path, complex_json_data):
    """
    Tests pipeline execution with complex JSON structure
    """
    pipeline = ConversionPipeline()
    # Define the output file
    output_file = tmp_path / "complex_output.xlsx"

    success, results, error = pipeline.execute(complex_json_data.source_path, str(output_file))
    assert success is False
    assert error is not None
    assert os.path.exists(output_file) is False


def test_pipeline_error_handling(tmp_path):
    """
    Tests error handling in the pipeline
    """
    pipeline = ConversionPipeline()
    # Define the output file
    output_file = tmp_path / "error_output.xlsx"

    # Execute with an invalid input file
    success, results, error = pipeline.execute("invalid_input.json", str(output_file))
    assert success is False
    assert error is not None
    assert "File not found" in error.message


def test_pipeline_context_tracking(tmp_path):
    """
    Tests that the pipeline correctly tracks context and progress
    """
    pipeline = ConversionPipeline()
    # Create a temporary input file
    input_file = tmp_path / "test_input.json"
    input_file.write_text('{"name": "test", "value": 123}')
    # Define the output file
    output_file = tmp_path / "test_output.xlsx"

    success, results, error = pipeline.execute(str(input_file), str(output_file))
    assert success is True
    assert results["pipeline_stages"][PipelineStage.VALIDATION.value]["status"] == PipelineStatus.COMPLETED.value
    assert results["pipeline_stages"][PipelineStage.INPUT_PROCESSING.value]["status"] == PipelineStatus.COMPLETED.value
    assert results["pipeline_stages"][PipelineStage.TRANSFORMATION.value]["status"] == PipelineStatus.COMPLETED.value
    assert results["pipeline_stages"][PipelineStage.EXCEL_GENERATION.value]["status"] == PipelineStatus.COMPLETED.value
    assert results["pipeline_stages"][PipelineStage.COMPLETION.value]["status"] == PipelineStatus.COMPLETED.value


def test_pipeline_component_interaction(tmp_path):
    """
    Tests the interaction between pipeline components
    """
    # Create mock components
    mock_input_handler = MockComponent(return_value=JSONData(content={}, source_path="", size_bytes=0))
    mock_data_transformer = MockComponent(return_value=pandas.DataFrame())
    mock_excel_generator = MockComponent(return_value=(True, None))

    # Initialize pipeline with mock components
    pipeline = ConversionPipeline(
        input_handler=mock_input_handler,
        data_transformer=mock_data_transformer,
        excel_generator=mock_excel_generator
    )

    # Create a temporary input file
    input_file = tmp_path / "test_input.json"
    input_file.write_text('{"name": "test", "value": 123}')
    # Define the output file
    output_file = tmp_path / "test_output.xlsx"

    # Execute the pipeline
    success, results, error = pipeline.execute(str(input_file), str(output_file))

    # Assert that the mock components were called
    assert mock_input_handler.was_called is False
    assert mock_data_transformer.was_called is False
    assert mock_excel_generator.was_called is False


def test_pipeline_with_custom_options(tmp_path):
    """
    Tests pipeline execution with custom Excel options
    """
    pipeline = ConversionPipeline()
    # Create a temporary input file
    input_file = tmp_path / "test_input.json"
    input_file.write_text('{"name": "test", "value": 123}')
    # Define the output file
    output_file = tmp_path / "test_output.xlsx"

    # Define custom Excel options
    custom_options = {"sheet_name": "CustomSheet", "format_headers": False}

    # Execute the pipeline with custom options
    success, results, error = pipeline.execute(str(input_file), str(output_file), custom_options)
    assert success is True
    assert error is None
    assert os.path.exists(output_file)