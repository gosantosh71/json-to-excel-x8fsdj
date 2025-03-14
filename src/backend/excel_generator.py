"""
Core component responsible for generating Excel files from transformed JSON data.

This module handles the creation, formatting, and saving of Excel workbooks,
ensuring proper column formatting, data type handling, and adherence to Excel limitations.
"""

import os  # v: built-in
from typing import Dict, List, Optional, Tuple, Union, Any, ByteString  # v: built-in

import pandas  # v: 1.5.0+
import openpyxl  # v: 3.1.0+

from .models.excel_options import ExcelOptions
from .models.error_response import ErrorCategory, ErrorSeverity, ErrorResponse
from .exceptions import ExcelException, ExcelRowLimitError, ExcelColumnLimitError, ExcelGenerationError
from .constants import EXCEL_CONSTANTS, ERROR_CODES
from .logger import get_logger
from .utils import timing_decorator, validate_file_path, ensure_directory_exists
from .formatters.excel_formatter import ExcelFormatter
from .formatters.column_formatter import ColumnFormatter

# Initialize module logger
logger = get_logger(__name__)


def validate_dataframe_for_excel(df: pandas.DataFrame) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that a DataFrame doesn't exceed Excel's row and column limits.
    
    Args:
        df: The pandas DataFrame to validate
        
    Returns:
        Tuple containing validation result (True/False) and error response if validation fails
    """
    if df is None or df.empty:
        logger.warning("DataFrame is empty or None")
        return True, None
    
    # Get the DataFrame dimensions
    rows, cols = df.shape
    
    # Check row limit
    if rows > EXCEL_CONSTANTS["MAX_ROWS"]:
        error_message = f"Data exceeds Excel's row limit: {rows} rows (maximum: {EXCEL_CONSTANTS['MAX_ROWS']})"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["EXCEL_ROW_LIMIT"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("row_count", rows)
        error_response.add_context("max_rows", EXCEL_CONSTANTS["MAX_ROWS"])
        
        error_response.add_resolution_step("Split the data into multiple sheets")
        error_response.add_resolution_step("Filter the data to reduce row count")
        error_response.add_resolution_step("Export to a different format without row limits")
        
        return False, error_response
    
    # Check column limit
    if cols > EXCEL_CONSTANTS["MAX_COLUMNS"]:
        error_message = f"Data exceeds Excel's column limit: {cols} columns (maximum: {EXCEL_CONSTANTS['MAX_COLUMNS']})"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["EXCEL_COLUMN_LIMIT"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("column_count", cols)
        error_response.add_context("max_columns", EXCEL_CONSTANTS["MAX_COLUMNS"])
        
        error_response.add_resolution_step("Restructure the data to reduce the number of columns")
        error_response.add_resolution_step("Select only essential fields to include in the output")
        error_response.add_resolution_step("Split the data across multiple sheets")
        
        return False, error_response
    
    logger.debug(f"DataFrame validated: {rows} rows, {cols} columns - within Excel limits")
    return True, None


def sanitize_excel_data(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    Sanitizes data in a DataFrame to prevent Excel formula injection and other issues.
    
    Args:
        df: The pandas DataFrame to sanitize
        
    Returns:
        Sanitized DataFrame
    """
    # Create a copy to avoid modifying the original
    sanitized_df = df.copy()
    
    # Get string columns
    string_columns = sanitized_df.select_dtypes(include=['object']).columns
    
    # Process each string column
    for column in string_columns:
        # Check if the column contains string values
        if sanitized_df[column].dtype == 'object':
            # Apply sanitization to prevent formula injection
            sanitized_df[column] = sanitized_df[column].apply(
                lambda x: f"'{x}" if isinstance(x, str) and any(x.startswith(c) for c in EXCEL_CONSTANTS["FORMULA_PREFIX_CHARS"]) else x
            )
    
    logger.debug(f"Sanitized {len(string_columns)} string columns to prevent formula injection")
    return sanitized_df


@timing_decorator
def dataframe_to_excel_file(
    df: pandas.DataFrame, 
    output_path: str, 
    options: Optional[ExcelOptions] = None
) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Converts a pandas DataFrame to an Excel file at the specified path.
    
    Args:
        df: The pandas DataFrame to convert
        output_path: Path where the Excel file will be saved
        options: Excel formatting and generation options
        
    Returns:
        Tuple containing success status (True/False) and error response if conversion fails
    """
    # Validate the output path
    if not validate_file_path(output_path):
        error_message = f"Invalid output file path: {output_path}"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["FILE_NOT_FOUND"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("output_path", output_path)
        error_response.add_resolution_step("Verify the output directory exists and is writable")
        error_response.add_resolution_step("Check that the file name is valid")
        
        return False, error_response
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not ensure_directory_exists(output_dir):
        error_message = f"Failed to create output directory: {output_dir}"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["PERMISSION_ERROR"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("output_dir", output_dir)
        error_response.add_resolution_step("Check directory permissions")
        error_response.add_resolution_step("Try a different output location")
        
        return False, error_response
    
    # Use default options if none provided
    if options is None:
        options = ExcelOptions()
    
    # Validate DataFrame against Excel limits
    valid, error_response = validate_dataframe_for_excel(df)
    if not valid:
        return False, error_response
    
    # Sanitize the DataFrame to prevent formula injection
    sanitized_df = sanitize_excel_data(df)
    
    try:
        # Create Excel formatter
        formatter = ExcelFormatter(options)
        
        # Generate the Excel file
        formatter.generate_excel_file(sanitized_df, output_path)
        
        logger.info(f"Successfully converted DataFrame to Excel file: {output_path}")
        return True, None
        
    except ExcelException as e:
        logger.error(f"Excel generation failed: {str(e)}")
        return False, e.error_response
        
    except Exception as e:
        error_message = f"Unexpected error generating Excel file: {str(e)}"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["EXCEL_GENERATION_ERROR"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("error_type", type(e).__name__)
        error_response.add_context("error_details", str(e))
        error_response.add_resolution_step("Check that you have write permissions for the output directory")
        error_response.add_resolution_step("Ensure the output file is not currently open in another application")
        
        return False, error_response


@timing_decorator
def dataframe_to_excel_bytes(
    df: pandas.DataFrame, 
    options: Optional[ExcelOptions] = None
) -> Tuple[Optional[ByteString], Optional[ErrorResponse]]:
    """
    Converts a pandas DataFrame to an Excel file in memory and returns it as bytes.
    
    Args:
        df: The pandas DataFrame to convert
        options: Excel formatting and generation options
        
    Returns:
        Tuple containing Excel file as bytes and error response if conversion fails
    """
    # Use default options if none provided
    if options is None:
        options = ExcelOptions()
    
    # Validate DataFrame against Excel limits
    valid, error_response = validate_dataframe_for_excel(df)
    if not valid:
        return None, error_response
    
    # Sanitize the DataFrame to prevent formula injection
    sanitized_df = sanitize_excel_data(df)
    
    try:
        # Create Excel formatter
        formatter = ExcelFormatter(options)
        
        # Generate the Excel file as bytes
        excel_bytes = formatter.generate_excel_bytes(sanitized_df)
        
        logger.info("Successfully converted DataFrame to Excel bytes")
        return excel_bytes, None
        
    except ExcelException as e:
        logger.error(f"Excel generation failed: {str(e)}")
        return None, e.error_response
        
    except Exception as e:
        error_message = f"Unexpected error generating Excel bytes: {str(e)}"
        logger.error(error_message)
        
        error_response = ErrorResponse(
            message=error_message,
            error_code=ERROR_CODES["EXCEL_GENERATION_ERROR"],
            category=ErrorCategory.OUTPUT_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="ExcelGenerator"
        )
        
        error_response.add_context("error_type", type(e).__name__)
        error_response.add_context("error_details", str(e))
        
        return None, error_response


class ExcelGenerator:
    """
    A class that handles the generation of Excel files from pandas DataFrames,
    with support for various formatting options and error handling.
    """
    
    def __init__(self, options: Optional[ExcelOptions] = None):
        """
        Initializes a new ExcelGenerator instance with the specified options.
        
        Args:
            options: Excel formatting and generation options (optional)
        """
        self._options = options or ExcelOptions()
        self._logger = get_logger(__name__)
        self._logger.debug("ExcelGenerator initialized")
    
    def generate_excel(self, df: pandas.DataFrame, output_path: str) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Generates an Excel file from a pandas DataFrame with the configured options.
        
        Args:
            df: The pandas DataFrame to convert to Excel
            output_path: Path where the Excel file will be saved
            
        Returns:
            Tuple containing success status (True/False) and error response if generation fails
        """
        self._logger.info(f"Generating Excel file at {output_path}")
        result = dataframe_to_excel_file(df, output_path, self._options)
        
        if result[0]:
            self._logger.info(f"Excel generation successful: {output_path}")
        else:
            self._logger.error(f"Excel generation failed: {result[1].message if result[1] else 'Unknown error'}")
            
        return result
    
    def generate_excel_bytes(self, df: pandas.DataFrame) -> Tuple[Optional[ByteString], Optional[ErrorResponse]]:
        """
        Generates an Excel file in memory from a pandas DataFrame and returns it as bytes.
        
        Args:
            df: The pandas DataFrame to convert to Excel
            
        Returns:
            Tuple containing Excel file as bytes and error response if generation fails
        """
        self._logger.info("Generating Excel file as bytes")
        result = dataframe_to_excel_bytes(df, self._options)
        
        if result[0] is not None:
            self._logger.info("Excel bytes generation successful")
        else:
            self._logger.error(f"Excel bytes generation failed: {result[1].message if result[1] else 'Unknown error'}")
            
        return result
    
    def set_options(self, options: ExcelOptions) -> None:
        """
        Updates the Excel generation options.
        
        Args:
            options: New Excel formatting and generation options
        """
        self._options = options
        self._logger.debug("Excel generator options updated")
    
    def get_options(self) -> ExcelOptions:
        """
        Gets the current Excel generation options.
        
        Returns:
            The current Excel formatting and generation options
        """
        return self._options