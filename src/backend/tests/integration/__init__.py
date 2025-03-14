"""
Initialization file for the integration tests package that provides common utilities, fixtures,
and setup functions for testing the integration between components of the JSON to Excel Conversion Tool.
This file enables consistent test configuration and shared resources across all integration test modules.
"""

import os  # v: built-in
import tempfile  # v: built-in
import pytest  # v: 7.3.0+

from ...pipelines.conversion_pipeline import ConversionPipeline
from ...input_handler import InputHandler
from ...data_transformer import DataTransformer
from ...excel_generator import ExcelGenerator
from ...services.validation_service import ValidationService
from ...services.conversion_service import ConversionService

# Define constants for test directories
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(os.path.dirname(TEST_DIR), 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')
EXPECTED_OUTPUT_DIR = os.path.join(FIXTURES_DIR, 'expected_output')

def create_temp_file(content, extension):
    """
    Creates a temporary file with the specified content and extension.
    
    Args:
        content: The content to write to the file
        extension: The file extension (e.g., '.json')
        
    Returns:
        Path to the created temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=extension)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return temp_path

def create_temp_json_file(json_content):
    """
    Creates a temporary JSON file with the specified content.
    
    Args:
        json_content: The JSON content to write to the file
        
    Returns:
        Path to the created temporary JSON file
    """
    import json
    json_string = json.dumps(json_content, indent=2)
    return create_temp_file(json_string, '.json')

def cleanup_temp_file(file_path):
    """
    Removes a temporary file if it exists.
    
    Args:
        file_path: Path to the file to clean up
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to clean up temporary file {file_path}: {e}")

def setup_pipeline(options=None):
    """
    Creates and configures a ConversionPipeline instance for testing.
    
    Args:
        options: Dictionary of options to pass to the pipeline
        
    Returns:
        A configured ConversionPipeline instance
    """
    input_handler = InputHandler()
    data_transformer = DataTransformer()
    excel_generator = ExcelGenerator()
    validation_service = ValidationService()
    conversion_service = ConversionService()
    
    pipeline = ConversionPipeline(
        input_handler=input_handler,
        data_transformer=data_transformer,
        excel_generator=excel_generator,
        validation_service=validation_service,
        conversion_service=conversion_service
    )
    
    return pipeline

def compare_excel_files(actual_file_path, expected_file_path):
    """
    Compares two Excel files by loading them as DataFrames and checking for equality.
    
    Args:
        actual_file_path: Path to the actual Excel file
        expected_file_path: Path to the expected Excel file
        
    Returns:
        True if the Excel files are equivalent, False otherwise
    """
    import pandas as pd
    
    # Load both Excel files as DataFrames
    actual_df = pd.read_excel(actual_file_path)
    expected_df = pd.read_excel(expected_file_path)
    
    # Compare the DataFrames
    try:
        pd.testing.assert_frame_equal(actual_df, expected_df)
        return True
    except AssertionError:
        return False