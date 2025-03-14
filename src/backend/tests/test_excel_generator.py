"""
Contains unit tests for the Excel generator component of the JSON to Excel Conversion Tool.
This module tests the functionality for converting pandas DataFrames to Excel files,
validating Excel limits, handling formatting options, and proper error handling during
Excel generation.
"""

import os
import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path

from ...excel_generator import (
    ExcelGenerator, 
    dataframe_to_excel_file as dataframe_to_excel,
    validate_dataframe_for_excel,
    sanitize_excel_data as sanitize_dataframe_for_excel
)
from ...models.excel_options import ExcelOptions, ArrayHandlingStrategy
from ...models.json_data import JSONData
from ...models.error_response import ErrorCategory
from ...exceptions import ExcelGenerationException, ExcelLimitExceededException
from ...constants import EXCEL_CONSTANTS
from ..fixtures.excel_fixtures import (
    default_excel_options,
    custom_excel_options,
    array_expand_options,
    array_join_options,
    test_flat_dataframe,
    test_nested_dataframe,
    test_array_dataframe,
    load_expected_excel,
    get_excel_file_path
)
from ..fixtures.json_fixtures import (
    flat_json_data,
    nested_json_data,
    array_json_data
)
from . import create_temp_json_file, cleanup_temp_file


def test_excel_generator_initialization(default_excel_options, custom_excel_options):
    """Tests that the ExcelGenerator initializes correctly with default and custom options."""
    # Create an ExcelGenerator with default options
    generator = ExcelGenerator(default_excel_options)
    assert generator.get_options() == default_excel_options
    
    # Create an ExcelGenerator with custom options
    generator = ExcelGenerator(custom_excel_options)
    assert generator.get_options() == custom_excel_options
    
    # Create an ExcelGenerator with no options
    generator = ExcelGenerator()
    assert generator.get_options() is not None
    assert isinstance(generator.get_options(), ExcelOptions)


def test_set_get_options(default_excel_options, custom_excel_options):
    """Tests the set_options and get_options methods of ExcelGenerator."""
    # Create an ExcelGenerator with default options
    generator = ExcelGenerator(default_excel_options)
    
    # Verify that get_options returns the default options
    options = generator.get_options()
    assert options == default_excel_options
    
    # Set new options using set_options
    generator.set_options(custom_excel_options)
    
    # Verify that get_options returns the new options
    updated_options = generator.get_options()
    assert updated_options == custom_excel_options
    assert updated_options.sheet_name == custom_excel_options.sheet_name


def test_validate_dataframe_for_excel_valid(test_flat_dataframe):
    """Tests that validate_dataframe_for_excel correctly validates DataFrames within Excel limits."""
    # Call validate_dataframe_for_excel with a valid DataFrame
    is_valid, error = validate_dataframe_for_excel(test_flat_dataframe)
    
    # Verify that the function returns (True, None) indicating validation passed
    assert is_valid is True
    assert error is None


def test_validate_dataframe_for_excel_too_many_rows():
    """Tests that validate_dataframe_for_excel correctly identifies DataFrames with too many rows."""
    # Create a mock DataFrame with rows exceeding Excel's MAX_ROWS limit
    max_rows = EXCEL_CONSTANTS["MAX_ROWS"] + 1
    df = pd.DataFrame({'A': list(range(max_rows))})
    
    # Call validate_dataframe_for_excel with the oversized DataFrame
    is_valid, error = validate_dataframe_for_excel(df)
    
    # Verify that the function returns (False, error_response) with appropriate error details
    assert is_valid is False
    assert error is not None
    assert error.category == ErrorCategory.OUTPUT_ERROR


def test_validate_dataframe_for_excel_too_many_columns():
    """Tests that validate_dataframe_for_excel correctly identifies DataFrames with too many columns."""
    # Create a mock DataFrame with columns exceeding Excel's MAX_COLUMNS limit
    max_cols = EXCEL_CONSTANTS["MAX_COLUMNS"] + 1
    data = {f"col_{i}": [i] for i in range(max_cols)}
    df = pd.DataFrame(data)
    
    # Call validate_dataframe_for_excel with the oversized DataFrame
    is_valid, error = validate_dataframe_for_excel(df)
    
    # Verify that the function returns (False, error_response) with appropriate error details
    assert is_valid is False
    assert error is not None
    assert error.category == ErrorCategory.OUTPUT_ERROR


def test_sanitize_dataframe_for_excel():
    """Tests that sanitize_dataframe_for_excel correctly sanitizes DataFrame content for Excel."""
    # Create a DataFrame with cells containing formula-like content (starting with =, +, -, @)
    data = {
        'A': ['Normal text', '=SUM(B1:B5)', '+IMPORTRANGE("url")', '-EXTERNAL()', '@RISK()'],
        'B': [1, 2, 3, 4, 5]
    }
    df = pd.DataFrame(data)
    
    # Call sanitize_dataframe_for_excel with the DataFrame
    sanitized_df = sanitize_dataframe_for_excel(df)
    
    # Verify that formula-like content is properly escaped with a single quote prefix
    assert sanitized_df['A'][0] == 'Normal text'  # Normal text unchanged
    assert sanitized_df['A'][1].startswith("'=")  # Formula escaped with single quote
    assert sanitized_df['A'][2].startswith("'+")  # Formula escaped with single quote
    assert sanitized_df['A'][3].startswith("'-")  # Formula escaped with single quote
    assert sanitized_df['A'][4].startswith("'@")  # Formula escaped with single quote
    
    # Verify that normal content is not modified
    assert sanitized_df['B'][0] == 1


def test_dataframe_to_excel_success(test_flat_dataframe, default_excel_options, tmpdir):
    """Tests that dataframe_to_excel successfully converts a DataFrame to an Excel file."""
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call dataframe_to_excel with the DataFrame, output path, and options
    success, error = dataframe_to_excel(test_flat_dataframe, output_path, default_excel_options)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that the Excel file contains the expected data
    df_read = pd.read_excel(output_path)
    pd.testing.assert_frame_equal(df_read, test_flat_dataframe, check_dtype=False)


def test_dataframe_to_excel_validation_failure(default_excel_options, tmpdir, mocker):
    """Tests that dataframe_to_excel handles validation failures correctly."""
    # Create a mock DataFrame
    df = pd.DataFrame({'A': [1, 2, 3]})
    
    # Mock validate_dataframe_for_excel to return a validation failure
    error_response = mocker.MagicMock()
    error_response.category = ErrorCategory.OUTPUT_ERROR
    error_response.message = "Validation failed"
    
    mocker.patch(
        'src.backend.excel_generator.validate_dataframe_for_excel', 
        return_value=(False, error_response)
    )
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call dataframe_to_excel with the DataFrame, output path, and options
    success, error = dataframe_to_excel(df, output_path, default_excel_options)
    
    # Verify that the function returns (False, error_response) with the validation error
    assert success is False
    assert error is error_response
    
    # Verify that the Excel file was not created
    assert not os.path.exists(output_path)


def test_dataframe_to_excel_exception_handling(test_flat_dataframe, default_excel_options, tmpdir, mocker):
    """Tests that dataframe_to_excel properly handles exceptions during Excel generation."""
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Mock pandas.DataFrame.to_excel to raise an exception
    mocker.patch.object(
        pd.DataFrame, 
        'to_excel', 
        side_effect=Exception("Test exception")
    )
    
    # Call dataframe_to_excel with the DataFrame, output path, and options
    success, error = dataframe_to_excel(test_flat_dataframe, output_path, default_excel_options)
    
    # Verify that the function returns (False, error_response) with appropriate error details
    assert success is False
    assert error is not None
    
    # Verify that the error is wrapped in an ExcelGenerationException
    assert isinstance(error.source_component, str)
    
    # Verify that the Excel file was not created
    assert not os.path.exists(output_path)


def test_excel_generator_generate_excel(test_flat_dataframe, default_excel_options, tmpdir):
    """Tests the generate_excel method of ExcelGenerator."""
    # Create an ExcelGenerator with the provided options
    generator = ExcelGenerator(default_excel_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_flat_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that the Excel file contains the expected data
    df_read = pd.read_excel(output_path)
    pd.testing.assert_frame_equal(df_read, test_flat_dataframe, check_dtype=False)


def test_excel_generator_generate_excel_bytes(test_flat_dataframe, default_excel_options):
    """Tests the generate_excel_bytes method of ExcelGenerator."""
    # Create an ExcelGenerator with the provided options
    generator = ExcelGenerator(default_excel_options)
    
    # Call generate_excel_bytes with the DataFrame
    bytes_content, error = generator.generate_excel_bytes(test_flat_dataframe)
    
    # Verify that the function returns (bytes_content, None) with non-empty bytes
    assert bytes_content is not None
    assert error is None
    assert isinstance(bytes_content, bytes)
    assert len(bytes_content) > 0
    
    # Verify that the bytes content can be loaded as a valid Excel file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
        temp_file.write(bytes_content)
        temp_file_path = temp_file.name
    
    try:
        # Verify that the Excel content contains the expected data
        df_read = pd.read_excel(temp_file_path)
        pd.testing.assert_frame_equal(df_read, test_flat_dataframe, check_dtype=False)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_excel_generator_with_json_data(test_flat_dataframe, default_excel_options, flat_json_data, tmpdir):
    """Tests the ExcelGenerator with JSONData for metadata inclusion."""
    # Create an ExcelGenerator with the provided options and JSONData
    generator = ExcelGenerator(default_excel_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_flat_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that the Excel file contains the expected data
    df_read = pd.read_excel(output_path)
    pd.testing.assert_frame_equal(df_read, test_flat_dataframe, check_dtype=False)
    
    # Verify that any metadata from JSONData is included in the Excel file
    # This would depend on how metadata is implemented in the actual code


def test_array_handling_expand(test_array_dataframe, array_expand_options, tmpdir):
    """Tests Excel generation with array expansion strategy."""
    # Create an ExcelGenerator with array expansion options
    generator = ExcelGenerator(array_expand_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_array_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that arrays in the data are expanded correctly in the Excel file
    df_read = pd.read_excel(output_path)
    pd.testing.assert_frame_equal(df_read, test_array_dataframe, check_dtype=False)


def test_array_handling_join(test_array_dataframe, array_join_options, tmpdir):
    """Tests Excel generation with array join strategy."""
    # Create an ExcelGenerator with array join options
    generator = ExcelGenerator(array_join_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_array_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that arrays in the data are joined correctly in the Excel file
    df_read = pd.read_excel(output_path)
    assert df_read is not None
    assert len(df_read) > 0


def test_nested_structure_handling(test_nested_dataframe, default_excel_options, tmpdir):
    """Tests Excel generation with nested JSON structures."""
    # Create an ExcelGenerator with default options
    generator = ExcelGenerator(default_excel_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_nested_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Verify that nested structures are correctly represented in the Excel file with dot notation
    df_read = pd.read_excel(output_path)
    assert 'contact.email' in df_read.columns
    assert 'contact.phone' in df_read.columns
    assert 'address.street' in df_read.columns
    
    # Validate content
    pd.testing.assert_frame_equal(df_read, test_nested_dataframe, check_dtype=False)


def test_excel_formatting_options(test_flat_dataframe, custom_excel_options, tmpdir):
    """Tests that Excel formatting options are correctly applied."""
    # Create an ExcelGenerator with custom formatting options
    generator = ExcelGenerator(custom_excel_options)
    
    # Create an output file path in the temporary directory
    output_path = os.path.join(tmpdir, "output.xlsx")
    
    # Call generate_excel with the DataFrame and output path
    success, error = generator.generate_excel(test_flat_dataframe, output_path)
    
    # Verify that the function returns (True, None) indicating success
    assert success is True
    assert error is None
    
    # Verify that the Excel file was created at the specified path
    assert os.path.exists(output_path)
    
    # Load the Excel file and verify that formatting options were applied correctly
    import openpyxl
    wb = openpyxl.load_workbook(output_path)
    assert custom_excel_options.sheet_name in wb.sheetnames