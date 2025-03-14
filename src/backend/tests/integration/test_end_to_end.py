# Standard library imports
import os  # v: built-in
import tempfile  # v: built-in
import json  # v: built-in

# Third-party library imports
import pytest  # v: 7.3.0+
import pandas as pd  # v: 1.5.0+

# Local application/library specific imports
from ...pipelines.conversion_pipeline import ConversionPipeline  # Implements the core conversion pipeline
from ...input_handler import InputHandler  # Handles JSON input file processing
from ...data_transformer import DataTransformer  # Transforms JSON data to tabular format
from ...excel_generator import ExcelGenerator  # Generates Excel files from transformed data
from ...models.excel_options import ExcelOptions, ArrayHandlingStrategy  # Configures Excel output options
from ..fixtures.json_fixtures import flat_json, nested_json, array_json, complex_json, invalid_json, get_invalid_json_string  # Provides test JSON structures
from ..fixtures.excel_fixtures import default_excel_options, array_expand_options, array_join_options, load_expected_excel  # Provides Excel options and expected outputs

# Define global constants for test directories
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(os.path.dirname(TEST_DIR), 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')


def create_temp_file(content: str, extension: str) -> str:
    """Creates a temporary file with the specified content and extension.

    Args:
        content (str): The content to write to the file.
        extension (str): The file extension (e.g., "json", "xlsx").

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


def create_temp_json_file(json_content: dict) -> str:
    """Creates a temporary JSON file with the specified content.

    Args:
        json_content (dict): The JSON content to write to the file.

    Returns:
        str: Path to the created temporary JSON file
    """
    # Serialize the json_content to a string
    json_string = json.dumps(json_content)
    # Call create_temp_file with the JSON string and '.json' extension
    return create_temp_file(json_string, 'json')


def cleanup_temp_file(file_path: str) -> None:
    """Removes a temporary file if it exists.

    Args:
        file_path (str): The path to the temporary file.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Remove the file if it exists
        os.remove(file_path)


def compare_excel_files(actual_file_path: str, expected_file_path: str) -> bool:
    """Compares two Excel files by loading them as DataFrames and checking for equality.

    Args:
        actual_file_path (str): Path to the actual Excel file.
        expected_file_path (str): Path to the expected Excel file.

    Returns:
        bool: True if the Excel files are equivalent, False otherwise
    """
    # Load both Excel files as pandas DataFrames
    actual_df = pd.read_excel(actual_file_path)
    expected_df = pd.read_excel(expected_file_path)

    # Compare the DataFrames for equality
    return actual_df.equals(expected_df)


def test_end_to_end_flat_json(flat_json, default_excel_options):
    """Tests end-to-end conversion of flat JSON to Excel"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(flat_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, default_excel_options.to_dict())

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_nested_json(nested_json, default_excel_options):
    """Tests end-to-end conversion of nested JSON to Excel"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(nested_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, default_excel_options.to_dict())

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_array_json_expand(array_json, array_expand_options):
    """Tests end-to-end conversion of JSON with arrays using expand strategy"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(array_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, array_expand_options.to_dict())

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_array_json_join(array_json, array_join_options):
    """Tests end-to-end conversion of JSON with arrays using join strategy"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(array_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, array_join_options.to_dict())

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_complex_json(complex_json, default_excel_options):
    """Tests end-to-end conversion of complex JSON with deep nesting and arrays"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(complex_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, default_excel_options.to_dict())

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_invalid_json(invalid_json, default_excel_options):
    """Tests end-to-end conversion with invalid JSON input"""
    # Create temporary input and output file paths
    input_file_path = create_temp_file(invalid_json, 'json')
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, default_excel_options.to_dict())

    # Assert that the conversion failed
    assert success is False
    assert error is not None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_invalid_output_path(flat_json, default_excel_options):
    """Tests end-to-end conversion with invalid output file path"""
    # Create temporary input file path
    input_file_path = create_temp_json_file(flat_json)
    output_file_path = '/invalid/path/output.xlsx'  # Invalid output path

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, default_excel_options.to_dict())

    # Assert that the conversion failed
    assert success is False
    assert error is not None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)


def test_end_to_end_custom_options(flat_json):
    """Tests end-to-end conversion with custom Excel options"""
    # Define custom Excel options
    custom_options = {
        'sheet_name': 'CustomSheet',
        'format_headers': False,
    }

    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(flat_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, _, error = pipeline.execute(input_file_path, output_file_path, custom_options)

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_pipeline_components(flat_json):
    """Tests that all pipeline components work together correctly"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(flat_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Initialize pipeline components
    input_handler = InputHandler()
    data_transformer = DataTransformer()
    excel_generator = ExcelGenerator()

    # Execute the conversion pipeline
    pipeline = ConversionPipeline(input_handler, data_transformer, excel_generator)
    success, _, error = pipeline.execute(input_file_path, output_file_path)

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)


def test_end_to_end_performance(flat_json):
    """Tests performance metrics of the end-to-end conversion process"""
    # Create temporary input and output file paths
    input_file_path = create_temp_json_file(flat_json)
    output_file_path = create_temp_file('', 'xlsx')

    # Execute the conversion pipeline
    pipeline = ConversionPipeline()
    success, summary, error = pipeline.execute(input_file_path, output_file_path)

    # Assert that the conversion was successful
    assert success is True
    assert error is None

    # Assert that performance metrics are present in the summary
    assert 'performance' in summary
    assert 'total_execution_time' in summary['performance']

    # Clean up temporary files
    cleanup_temp_file(input_file_path)
    cleanup_temp_file(output_file_path)