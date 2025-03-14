"""
Provides test fixtures for Excel-related tests in the JSON to Excel conversion tool.

This module contains predefined Excel options configurations, utility functions for
loading expected Excel files, and methods for creating test DataFrames for
validation purposes.
"""

import os  # v: built-in
import pytest  # v: 7.3.0+
import pandas as pd  # v: 1.5.0+
from pathlib import Path  # v: built-in

from ...models.excel_options import ExcelOptions, ArrayHandlingStrategy
from ...constants import EXCEL_CONSTANTS

# Constants for fixture file paths
FIXTURES_DIR = Path(__file__).parent
EXPECTED_OUTPUT_DIR = FIXTURES_DIR / 'expected_output'

def load_expected_excel(filename: str) -> pd.DataFrame:
    """
    Loads an expected Excel file from the expected_output directory as a pandas DataFrame.
    
    Args:
        filename: The name of the Excel file to load
        
    Returns:
        The Excel file content as a DataFrame
    """
    file_path = EXPECTED_OUTPUT_DIR / filename
    return pd.read_excel(file_path)

def get_excel_file_path(filename: str) -> Path:
    """
    Gets the full path to an expected Excel file in the expected_output directory.
    
    Args:
        filename: The name of the Excel file
        
    Returns:
        The full path to the Excel file
    """
    return EXPECTED_OUTPUT_DIR / filename

def create_test_dataframe(data_type: str) -> pd.DataFrame:
    """
    Creates a test DataFrame with sample data for Excel generation tests.
    
    Args:
        data_type: The type of test data to create ('flat', 'nested', or 'array')
        
    Returns:
        A DataFrame with test data based on the specified type
    """
    if data_type == 'flat':
        # Create a simple flat DataFrame
        return pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'age': [30, 25, 40],
            'active': [True, False, True]
        })
    
    elif data_type == 'nested':
        # Create a DataFrame with compound column names using dot notation
        return pd.DataFrame({
            'id': [1, 2],
            'name': ['John Doe', 'Jane Smith'],
            'contact.email': ['john@example.com', 'jane@example.com'],
            'contact.phone': ['555-1234', '555-5678'],
            'address.street': ['123 Main St', '456 Oak Ave'],
            'address.city': ['Anytown', 'Somewhere'],
            'address.zip': ['12345', '67890']
        })
    
    elif data_type == 'array':
        # Create a DataFrame with expanded array data
        return pd.DataFrame({
            'id': [1, 1, 2],
            'name': ['John Doe', 'John Doe', 'Jane Smith'],
            'orders.id': [101, 102, 201],
            'orders.product': ['Laptop', 'Mouse', 'Keyboard'],
            'orders.price': [999.99, 24.99, 49.99]
        })
    
    else:
        raise ValueError(f"Unknown data_type: {data_type}")

# Excel options fixtures
@pytest.fixture
def default_excel_options():
    """
    Provides default Excel options for testing.
    
    Returns:
        ExcelOptions with default settings
    """
    return ExcelOptions()

@pytest.fixture
def custom_excel_options():
    """
    Provides custom Excel options with non-default settings for testing.
    
    Returns:
        ExcelOptions with custom settings
    """
    return ExcelOptions(
        sheet_name="Custom Sheet",
        format_headers=True,
        freeze_header_row=True,
        auto_column_width=True,
        apply_data_formatting=True,
        column_formats={
            "id": "0",
            "price": "#,##0.00",
            "date": "yyyy-mm-dd"
        },
        workbook_properties={
            "title": "Test Workbook",
            "author": "Test Framework"
        }
    )

@pytest.fixture
def array_expand_options():
    """
    Provides Excel options with array expansion strategy.
    
    Returns:
        ExcelOptions with array expansion strategy
    """
    return ExcelOptions(
        array_handling=ArrayHandlingStrategy.EXPAND
    )

@pytest.fixture
def array_join_options():
    """
    Provides Excel options with array join strategy.
    
    Returns:
        ExcelOptions with array join strategy
    """
    return ExcelOptions(
        array_handling=ArrayHandlingStrategy.JOIN
    )

# Expected Excel output fixtures
@pytest.fixture
def expected_flat_excel():
    """
    Provides expected Excel output for flat JSON conversion.
    
    Returns:
        DataFrame containing the expected Excel output for flat JSON
    """
    return load_expected_excel('expected_flat.xlsx')

@pytest.fixture
def expected_nested_excel():
    """
    Provides expected Excel output for nested JSON conversion.
    
    Returns:
        DataFrame containing the expected Excel output for nested JSON
    """
    return load_expected_excel('expected_nested.xlsx')

@pytest.fixture
def expected_array_excel():
    """
    Provides expected Excel output for JSON with arrays.
    
    Returns:
        DataFrame containing the expected Excel output for JSON with arrays
    """
    return load_expected_excel('expected_array.xlsx')

# Test DataFrame fixtures
@pytest.fixture
def test_flat_dataframe():
    """
    Provides a test DataFrame with flat structure.
    
    Returns:
        DataFrame with a flat structure for testing
    """
    return create_test_dataframe('flat')

@pytest.fixture
def test_nested_dataframe():
    """
    Provides a test DataFrame with nested structure using dot notation.
    
    Returns:
        DataFrame with a nested structure for testing
    """
    return create_test_dataframe('nested')

@pytest.fixture
def test_array_dataframe():
    """
    Provides a test DataFrame with expanded array data.
    
    Returns:
        DataFrame with expanded array data for testing
    """
    return create_test_dataframe('array')