"""
Provides the core service for converting JSON data to Excel format.

This service coordinates the JSON parsing, data transformation, and Excel generation processes,
serving as the central component that ties together the various stages of the conversion pipeline.
"""

import os  # v: built-in
import pandas  # v: 1.5.0+
from typing import Dict, List, Any, Optional, Tuple  # v: built-in

from ..models.json_data import JSONData
from ..models.excel_options import ExcelOptions
from ..models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from ..json_parser import JSONParser
from ..data_transformer import DataTransformer
from ..excel_generator import ExcelGenerator
from ..input_handler import InputHandler
from ..error_handler import ErrorHandler
from ..logger import get_logger
from ..utils import timing_decorator, Timer, validate_file_path
from ..constants import JSON_CONSTANTS, FILE_CONSTANTS
from ..exceptions import TransformationException, ExcelGenerationException

# Initialize logger for this module
logger = get_logger(__name__)


def create_conversion_summary(json_data: JSONData, dataframe: pandas.DataFrame, 
                             output_path: str, execution_time: float) -> Dict[str, Any]:
    """
    Creates a summary of the conversion process with statistics and metadata.
    
    Args:
        json_data: The JSON data that was processed
        dataframe: The transformed DataFrame
        output_path: Path to the output Excel file
        execution_time: Total execution time in seconds
    
    Returns:
        A dictionary containing conversion summary information
    """
    # Extract JSON structure information
    json_structure = {
        "nesting_level": json_data.max_nesting_level,
        "contains_arrays": json_data.contains_arrays,
        "array_count": len(json_data.array_paths) if json_data.array_paths else 0,
        "complexity": json_data.complexity_level.name
    }
    
    # Get DataFrame statistics
    rows, columns = dataframe.shape
    
    # Calculate file sizes
    input_size = json_data.size_bytes
    output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    
    # Create the summary dictionary
    summary = {
        "input": {
            "file_path": json_data.source_path,
            "size_bytes": input_size,
            "size_mb": round(input_size / (1024 * 1024), 2) if input_size > 0 else 0,
            "structure": json_structure
        },
        "output": {
            "file_path": output_path,
            "size_bytes": output_size,
            "size_mb": round(output_size / (1024 * 1024), 2) if output_size > 0 else 0,
            "rows": rows,
            "columns": columns
        },
        "performance": {
            "execution_time_seconds": round(execution_time, 3),
            "rows_per_second": round(rows / execution_time, 2) if execution_time > 0 else 0
        },
        "status": "success"
    }
    
    return summary


class ConversionService:
    """
    A service class that coordinates the conversion of JSON data to Excel format,
    orchestrating the parsing, transformation, and Excel generation processes.
    """
    
    def __init__(self, max_file_size_mb: Optional[int] = None, max_nesting_level: Optional[int] = None):
        """
        Initializes a new ConversionService instance with optional custom parameters.
        
        Args:
            max_file_size_mb: Maximum file size in MB (defaults to FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'])
            max_nesting_level: Maximum nesting level (defaults to JSON_CONSTANTS['MAX_NESTING_LEVEL'])
        """
        # Set maximum file size from parameter or use default
        self._max_file_size_bytes = max_file_size_mb * 1024 * 1024 if max_file_size_mb else FILE_CONSTANTS['MAX_FILE_SIZE_BYTES']
        
        # Set maximum nesting level from parameter or use default
        self._max_nesting_level = max_nesting_level or JSON_CONSTANTS['MAX_NESTING_LEVEL']
        
        # Initialize core components
        self._json_parser = JSONParser()
        self._data_transformer = DataTransformer()
        self._excel_generator = ExcelGenerator()
        self._input_handler = InputHandler()
        self._error_handler = ErrorHandler()
        self._logger = get_logger(__name__)
        
        self._logger.info(f"ConversionService initialized with max_file_size={self._max_file_size_bytes} bytes, "
                          f"max_nesting_level={self._max_nesting_level}")

    @timing_decorator
    def convert_json_to_excel(self, input_path: str, output_path: str, 
                             excel_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]:
        """
        Converts a JSON file to Excel format, handling the entire conversion process.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Path to the output Excel file
            excel_options: Optional Excel formatting options
        
        Returns:
            Tuple of (success status, conversion summary, error response if any)
        """
        self._logger.info(f"Starting conversion of JSON file '{input_path}' to Excel file '{output_path}'")
        
        try:
            # Validate input and output file paths
            if not validate_file_path(input_path):
                raise ValueError(f"Invalid input file path: {input_path}")
            
            if not validate_file_path(output_path):
                raise ValueError(f"Invalid output file path: {output_path}")
            
            # Parse the JSON file
            with Timer("JSON parsing"):
                self._logger.debug(f"Parsing JSON file: {input_path}")
                parsed_json = self._input_handler.read_json_file(input_path)
                json_data = self._json_parser.create_json_data(
                    parsed_json, 
                    input_path, 
                    os.path.getsize(input_path)
                )
            
            # Analyze the JSON structure
            json_data.analyze_structure()
            
            # Check if nesting level exceeds the maximum
            if json_data.max_nesting_level > self._max_nesting_level:
                self._logger.warning(f"JSON nesting level ({json_data.max_nesting_level}) exceeds "
                                     f"maximum allowed level ({self._max_nesting_level})")
            
            # Create Excel options from provided options or use defaults
            excel_opts = ExcelOptions.from_dict(excel_options) if excel_options else ExcelOptions()
            
            # Configure the data transformer based on the JSON structure
            flattening_strategy = json_data.get_flattening_strategy()
            self._data_transformer.set_array_handling(excel_opts.array_handling.value)
            
            # Transform the JSON data to a DataFrame
            with Timer("Data transformation"):
                self._logger.debug(f"Transforming JSON data to DataFrame using strategy: {flattening_strategy}")
                df, error = self._data_transformer.transform_data(json_data)
                if error:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Generate the Excel file from the DataFrame
            with Timer("Excel generation"):
                self._logger.debug(f"Generating Excel file: {output_path}")
                success, error = self._excel_generator.generate_excel(df, output_path)
                if not success:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Create a summary of the conversion
            summary = create_conversion_summary(json_data, df, output_path, execution_time=0) # Timing will be overwritten by decorator
            
            self._logger.info(f"Successfully converted JSON file to Excel: {input_path} -> {output_path}")
            return True, summary, None
            
        except Exception as e:
            self._logger.error(f"Error during conversion: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, TransformationException):
                error_response.category = ErrorCategory.TRANSFORMATION_ERROR
            elif isinstance(e, ExcelGenerationException):
                error_response.category = ErrorCategory.OUTPUT_ERROR
            
            error_response.add_context("input_path", input_path)
            error_response.add_context("output_path", output_path)
            
            return False, {"status": "error", "error": error_response.to_dict()}, error_response

    @timing_decorator
    def convert_json_string_to_excel(self, json_string: str, output_path: str, 
                                   excel_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]:
        """
        Converts a JSON string to Excel format, handling the entire conversion process.
        
        Args:
            json_string: JSON content as a string
            output_path: Path to the output Excel file
            excel_options: Optional Excel formatting options
        
        Returns:
            Tuple of (success status, conversion summary, error response if any)
        """
        self._logger.info(f"Starting conversion of JSON string to Excel file '{output_path}'")
        
        try:
            # Validate output file path
            if not validate_file_path(output_path):
                raise ValueError(f"Invalid output file path: {output_path}")
            
            # Parse the JSON string
            with Timer("JSON parsing"):
                self._logger.debug("Parsing JSON string")
                parsed_json, error = self._json_parser.parse_string(json_string)
                if error:
                    return False, {"status": "error", "error": error.to_dict()}, error
                
                # Create a JSONData object with memory as source
                json_data = self._json_parser.create_json_data(
                    parsed_json, 
                    "memory", 
                    len(json_string)
                )
            
            # Analyze the JSON structure
            json_data.analyze_structure()
            
            # Create Excel options from provided options or use defaults
            excel_opts = ExcelOptions.from_dict(excel_options) if excel_options else ExcelOptions()
            
            # Configure the data transformer based on the JSON structure
            flattening_strategy = json_data.get_flattening_strategy()
            self._data_transformer.set_array_handling(excel_opts.array_handling.value)
            
            # Transform the JSON data to a DataFrame
            with Timer("Data transformation"):
                self._logger.debug(f"Transforming JSON data to DataFrame using strategy: {flattening_strategy}")
                df, error = self._data_transformer.transform_data(json_data)
                if error:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Generate the Excel file from the DataFrame
            with Timer("Excel generation"):
                self._logger.debug(f"Generating Excel file: {output_path}")
                success, error = self._excel_generator.generate_excel(df, output_path)
                if not success:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Create a summary of the conversion
            summary = create_conversion_summary(json_data, df, output_path, execution_time=0) # Timing will be overwritten by decorator
            
            self._logger.info(f"Successfully converted JSON string to Excel: {output_path}")
            return True, summary, None
            
        except Exception as e:
            self._logger.error(f"Error during conversion: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, TransformationException):
                error_response.category = ErrorCategory.TRANSFORMATION_ERROR
            elif isinstance(e, ExcelGenerationException):
                error_response.category = ErrorCategory.OUTPUT_ERROR
            
            error_response.add_context("output_path", output_path)
            
            return False, {"status": "error", "error": error_response.to_dict()}, error_response

    @timing_decorator
    def convert_json_to_excel_bytes(self, input_path: str, 
                                 excel_options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[ErrorResponse]]:
        """
        Converts a JSON file to Excel format and returns the result as bytes.
        
        Args:
            input_path: Path to the input JSON file
            excel_options: Optional Excel formatting options
        
        Returns:
            Tuple of (Excel content as bytes, conversion summary, error response if any)
        """
        self._logger.info(f"Starting conversion of JSON file '{input_path}' to Excel bytes")
        
        try:
            # Validate input file path
            if not validate_file_path(input_path):
                raise ValueError(f"Invalid input file path: {input_path}")
            
            # Parse the JSON file
            with Timer("JSON parsing"):
                self._logger.debug(f"Parsing JSON file: {input_path}")
                parsed_json = self._input_handler.read_json_file(input_path)
                json_data = self._json_parser.create_json_data(
                    parsed_json, 
                    input_path, 
                    os.path.getsize(input_path)
                )
            
            # Analyze the JSON structure
            json_data.analyze_structure()
            
            # Create Excel options from provided options or use defaults
            excel_opts = ExcelOptions.from_dict(excel_options) if excel_options else ExcelOptions()
            
            # Configure the data transformer based on the JSON structure
            flattening_strategy = json_data.get_flattening_strategy()
            self._data_transformer.set_array_handling(excel_opts.array_handling.value)
            
            # Transform the JSON data to a DataFrame
            with Timer("Data transformation"):
                self._logger.debug(f"Transforming JSON data to DataFrame using strategy: {flattening_strategy}")
                df, error = self._data_transformer.transform_data(json_data)
                if error:
                    return None, {"status": "error", "error": error.to_dict()}, error
            
            # Generate the Excel content as bytes
            with Timer("Excel generation"):
                self._logger.debug("Generating Excel content as bytes")
                excel_bytes, error = self._excel_generator.generate_excel_bytes(df)
                if error:
                    return None, {"status": "error", "error": error.to_dict()}, error
            
            # Create a summary of the conversion (without file size since we're not writing to disk)
            summary = {
                "input": {
                    "file_path": input_path,
                    "size_bytes": json_data.size_bytes,
                    "size_mb": round(json_data.size_bytes / (1024 * 1024), 2) if json_data.size_bytes > 0 else 0,
                    "structure": {
                        "nesting_level": json_data.max_nesting_level,
                        "contains_arrays": json_data.contains_arrays,
                        "array_count": len(json_data.array_paths) if json_data.array_paths else 0,
                        "complexity": json_data.complexity_level.name
                    }
                },
                "output": {
                    "size_bytes": len(excel_bytes) if excel_bytes else 0,
                    "size_mb": round(len(excel_bytes) / (1024 * 1024), 2) if excel_bytes else 0,
                    "rows": df.shape[0],
                    "columns": df.shape[1]
                },
                "performance": {
                    "execution_time_seconds": 0,  # Will be overwritten by decorator
                    "rows_per_second": 0  # Will be calculated
                },
                "status": "success"
            }
            
            self._logger.info(f"Successfully converted JSON file to Excel bytes: {input_path}")
            return excel_bytes, summary, None
            
        except Exception as e:
            self._logger.error(f"Error during conversion: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, TransformationException):
                error_response.category = ErrorCategory.TRANSFORMATION_ERROR
            elif isinstance(e, ExcelGenerationException):
                error_response.category = ErrorCategory.OUTPUT_ERROR
            
            error_response.add_context("input_path", input_path)
            
            return None, {"status": "error", "error": error_response.to_dict()}, error_response

    @timing_decorator
    def convert_json_data_to_excel(self, json_data: JSONData, output_path: str, 
                                 excel_options: Optional[ExcelOptions] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]:
        """
        Converts a JSONData object to Excel format, handling transformation and Excel generation.
        
        Args:
            json_data: JSONData object containing the parsed JSON
            output_path: Path to the output Excel file
            excel_options: Optional Excel formatting options
        
        Returns:
            Tuple of (success status, conversion summary, error response if any)
        """
        self._logger.info(f"Starting conversion of JSONData to Excel file '{output_path}'")
        
        try:
            # Validate output file path
            if not validate_file_path(output_path):
                raise ValueError(f"Invalid output file path: {output_path}")
            
            # Configure the data transformer based on the JSON structure
            array_handling = excel_options.array_handling.value if excel_options else "expand"
            self._data_transformer.set_array_handling(array_handling)
            
            # Transform the JSON data to a DataFrame
            with Timer("Data transformation"):
                self._logger.debug("Transforming JSONData to DataFrame")
                df, error = self._data_transformer.transform_data(json_data)
                if error:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Generate the Excel file from the DataFrame
            with Timer("Excel generation"):
                self._logger.debug(f"Generating Excel file: {output_path}")
                success, error = self._excel_generator.generate_excel(df, output_path)
                if not success:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Create a summary of the conversion
            summary = create_conversion_summary(json_data, df, output_path, execution_time=0) # Timing will be overwritten by decorator
            
            self._logger.info(f"Successfully converted JSONData to Excel: {output_path}")
            return True, summary, None
            
        except Exception as e:
            self._logger.error(f"Error during conversion: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, TransformationException):
                error_response.category = ErrorCategory.TRANSFORMATION_ERROR
            elif isinstance(e, ExcelGenerationException):
                error_response.category = ErrorCategory.OUTPUT_ERROR
            
            error_response.add_context("output_path", output_path)
            
            return False, {"status": "error", "error": error_response.to_dict()}, error_response

    @timing_decorator
    def convert_dataframe_to_excel(self, dataframe: pandas.DataFrame, output_path: str, 
                                 excel_options: Optional[ExcelOptions] = None,
                                 json_data: Optional[JSONData] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]:
        """
        Converts a pandas DataFrame to Excel format.
        
        Args:
            dataframe: The pandas DataFrame to convert
            output_path: Path to the output Excel file
            excel_options: Optional Excel formatting options
            json_data: Optional JSONData for context in the summary
        
        Returns:
            Tuple of (success status, conversion summary, error response if any)
        """
        self._logger.info(f"Starting conversion of DataFrame to Excel file '{output_path}'")
        
        try:
            # Validate output file path
            if not validate_file_path(output_path):
                raise ValueError(f"Invalid output file path: {output_path}")
            
            # Generate the Excel file from the DataFrame
            with Timer("Excel generation"):
                self._logger.debug(f"Generating Excel file: {output_path}")
                success, error = self._excel_generator.generate_excel(dataframe, output_path)
                if not success:
                    return False, {"status": "error", "error": error.to_dict()}, error
            
            # Create a summary of the conversion
            rows, columns = dataframe.shape
            output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            summary = {
                "input": {
                    "type": "DataFrame",
                    "rows": rows,
                    "columns": columns
                },
                "output": {
                    "file_path": output_path,
                    "size_bytes": output_size,
                    "size_mb": round(output_size / (1024 * 1024), 2) if output_size > 0 else 0,
                    "rows": rows,
                    "columns": columns
                },
                "performance": {
                    "execution_time_seconds": 0,  # Will be overwritten by decorator
                },
                "status": "success"
            }
            
            # Add JSON structure info if provided
            if json_data:
                summary["input"]["structure"] = {
                    "nesting_level": json_data.max_nesting_level,
                    "contains_arrays": json_data.contains_arrays,
                    "array_count": len(json_data.array_paths) if json_data.array_paths else 0,
                    "complexity": json_data.complexity_level.name
                }
            
            self._logger.info(f"Successfully converted DataFrame to Excel: {output_path}")
            return True, summary, None
            
        except Exception as e:
            self._logger.error(f"Error during conversion: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, ExcelGenerationException):
                error_response.category = ErrorCategory.OUTPUT_ERROR
            
            error_response.add_context("output_path", output_path)
            error_response.add_context("dataframe_shape", f"{dataframe.shape[0]}x{dataframe.shape[1]}")
            
            return False, {"status": "error", "error": error_response.to_dict()}, error_response

    @timing_decorator
    def transform_json_to_dataframe(self, json_data: JSONData, 
                                  array_handling: str) -> Tuple[Optional[pandas.DataFrame], Optional[ErrorResponse]]:
        """
        Transforms JSON data into a pandas DataFrame.
        
        Args:
            json_data: The JSONData to transform
            array_handling: Strategy for handling arrays ('expand' or 'join')
        
        Returns:
            Tuple of (resulting DataFrame, error response if any)
        """
        self._logger.info("Starting transformation of JSON data to DataFrame")
        
        try:
            # Configure the data transformer with the specified array handling strategy
            self._data_transformer.set_array_handling(array_handling)
            
            # Transform the JSON data to a DataFrame
            with Timer("Data transformation"):
                self._logger.debug(f"Transforming JSON data to DataFrame with array_handling={array_handling}")
                df, error = self._data_transformer.transform_data(json_data)
                if error:
                    return None, error
            
            self._logger.info(f"Successfully transformed JSON data to DataFrame with {df.shape[0]} rows and {df.shape[1]} columns")
            return df, None
            
        except Exception as e:
            self._logger.error(f"Error during transformation: {str(e)}")
            error_response = self._error_handler.handle_exception(e)
            
            if isinstance(e, TransformationException):
                error_response.category = ErrorCategory.TRANSFORMATION_ERROR
            
            return None, error_response

    def set_max_file_size(self, max_file_size_mb: int) -> None:
        """
        Sets the maximum file size limit for JSON input files.
        
        Args:
            max_file_size_mb: Maximum file size in MB
        """
        self._max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self._logger.info(f"Updated maximum file size to {max_file_size_mb} MB ({self._max_file_size_bytes} bytes)")

    def set_max_nesting_level(self, max_nesting_level: int) -> None:
        """
        Sets the maximum nesting level for JSON structures.
        
        Args:
            max_nesting_level: Maximum nesting level allowed
        """
        self._max_nesting_level = max_nesting_level
        self._logger.info(f"Updated maximum nesting level to {max_nesting_level}")