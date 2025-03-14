"""
Core component responsible for transforming JSON data into tabular format suitable for Excel output.

This module handles flattening of nested JSON structures, normalization of arrays, and 
conversion to pandas DataFrames that can be processed by the Excel generator.
"""

import pandas as pd  # v: 1.5.0+
import numpy as np  # v: 1.20.0+
from typing import Dict, List, Any, Optional, Tuple, Union  # v: built-in
from abc import ABC, abstractmethod  # v: built-in

from .models.json_data import JSONData, JSONComplexity
from .models.excel_options import ExcelOptions, ArrayHandlingStrategy
from .models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity
from .exceptions import TransformationException, NestedStructureError, MemoryError
from .constants import JSON_CONSTANTS
from .logger import get_logger
from .utils import (
    timing_decorator, 
    flatten_dict, 
    is_json_object, 
    is_json_array, 
    is_primitive_type
)

# Initialize module logger
logger = get_logger(__name__)

# Get the maximum nesting level from constants
MAX_NESTING_LEVEL = JSON_CONSTANTS['MAX_NESTING_LEVEL']


def flatten_json(json_data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """
    Flattens a nested JSON structure into a single-level dictionary with compound keys.
    
    Args:
        json_data: The nested JSON structure to flatten
        separator: Character used to join key components, defaults to '.'
        
    Returns:
        A flattened dictionary with compound keys
    """
    logger.debug(f"Flattening JSON structure with separator '{separator}'")
    
    if not isinstance(json_data, dict):
        logger.warning(f"Input is not a dictionary, returning as-is: {type(json_data)}")
        return json_data
    
    # Use the flatten_dict utility function from utils.py
    return flatten_dict(json_data, separator=separator)


def normalize_json_array(array_data: List[Any], parent_key: str = '') -> List[Dict[str, Any]]:
    """
    Normalizes a JSON array into a list of dictionaries suitable for DataFrame conversion.
    
    Args:
        array_data: The array to normalize
        parent_key: Key prefix for primitive values in the array
        
    Returns:
        A list of normalized dictionaries
    """
    logger.debug(f"Normalizing JSON array with {len(array_data)} items")
    normalized_items = []
    
    for i, item in enumerate(array_data):
        if is_json_object(item):
            # Already a dictionary, add it directly
            normalized_items.append(item)
        elif is_primitive_type(item):
            # For primitive types, create a dictionary with a default key
            # Use 'value' as key for primitive items or the parent_key if provided
            key = parent_key if parent_key else 'value'
            normalized_items.append({key: item})
        elif is_json_array(item):
            # Recursively normalize nested arrays
            nested_items = normalize_json_array(item, f"{parent_key}_{i}" if parent_key else f"item_{i}")
            normalized_items.extend(nested_items)
        else:
            # Unexpected type, convert to string
            logger.warning(f"Unexpected type in array: {type(item)}")
            normalized_items.append({parent_key or 'value': str(item)})
    
    return normalized_items


def join_array_values(array_data: List[Any], delimiter: str = ', ') -> str:
    """
    Joins array values into a single string with a delimiter.
    
    Args:
        array_data: The array values to join
        delimiter: The delimiter to use between values, defaults to ', '
        
    Returns:
        A string representation of the joined array values
    """
    logger.debug(f"Joining array values with delimiter '{delimiter}'")
    
    # Convert each item to a string representation
    string_items = []
    for item in array_data:
        if is_primitive_type(item):
            string_items.append(str(item))
        elif is_json_object(item) or is_json_array(item):
            # For objects and arrays, use a simplified string representation
            string_items.append(str(item))
        else:
            string_items.append(str(item))
    
    return delimiter.join(string_items)


def process_arrays_in_json(
    json_data: Dict[str, Any], 
    array_paths: List[str], 
    handling_strategy: ArrayHandlingStrategy
) -> Dict[str, Any]:
    """
    Processes arrays in a JSON structure according to the specified handling strategy.
    
    Args:
        json_data: The JSON data containing arrays
        array_paths: Paths to arrays in the JSON structure
        handling_strategy: Strategy for handling arrays (EXPAND or JOIN)
        
    Returns:
        Processed JSON with arrays handled according to strategy
    """
    logger.debug(f"Processing arrays using strategy: {handling_strategy.value}")
    
    # Create a deep copy to avoid modifying the original data
    processed_data = json_data.copy()
    
    for path in array_paths:
        # Get the array at the specified path
        current = processed_data
        parts = path.split('.')
        
        # Navigate to the parent of the array
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Found the array
                if part in current and isinstance(current[part], list):
                    array_data = current[part]
                    
                    if handling_strategy == ArrayHandlingStrategy.EXPAND:
                        # Normalize the array into multiple dictionaries
                        normalized_array = normalize_json_array(array_data, part)
                        current[part] = normalized_array
                    elif handling_strategy == ArrayHandlingStrategy.JOIN:
                        # Join array values into a single string
                        joined_value = join_array_values(array_data)
                        current[part] = joined_value
                    else:
                        logger.warning(f"Unknown array handling strategy: {handling_strategy}")
            else:
                # Navigate to the next level
                if part in current and isinstance(current[part], dict):
                    current = current[part]
                else:
                    logger.warning(f"Path {path} not found in JSON data")
                    break
    
    return processed_data


@timing_decorator
def json_to_dataframe(json_data: Dict[str, Any], options: Optional[ExcelOptions] = None) -> pd.DataFrame:
    """
    Converts JSON data to a pandas DataFrame.
    
    Args:
        json_data: The JSON data to convert
        options: Optional Excel options for customizing the conversion
        
    Returns:
        A pandas DataFrame representation of the JSON data
    """
    logger.info("Converting JSON data to DataFrame")
    
    # Handle empty data
    if not json_data:
        logger.warning("Empty JSON data, returning empty DataFrame")
        return pd.DataFrame()
    
    # Default options if not provided
    if options is None:
        options = ExcelOptions()
    
    # Handle different JSON structures
    if isinstance(json_data, list):
        logger.debug("Converting JSON array to DataFrame")
        # If the root is an array, convert it directly to a DataFrame
        df = pd.DataFrame(json_data)
    else:
        logger.debug("Converting JSON object to DataFrame")
        # If the root is an object, convert it to a single-row DataFrame
        df = pd.DataFrame([json_data])
    
    # Apply any Excel options that affect the DataFrame
    # (Future enhancement: Apply column formatting based on options)
    
    logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df


def validate_json_for_transformation(json_data: JSONData) -> Tuple[bool, Optional[ErrorResponse]]:
    """
    Validates that JSON data can be transformed without exceeding system limitations.
    
    Args:
        json_data: The JSON data to validate
        
    Returns:
        A tuple of (is_valid, error_response), where error_response is None if valid
    """
    logger.debug("Validating JSON data for transformation")
    
    # Check nesting level
    if json_data.max_nesting_level > MAX_NESTING_LEVEL:
        logger.warning(f"JSON nesting level ({json_data.max_nesting_level}) exceeds maximum ({MAX_NESTING_LEVEL})")
        error = ErrorResponse(
            message=f"JSON nesting level ({json_data.max_nesting_level}) exceeds maximum allowed ({MAX_NESTING_LEVEL})",
            error_code="E006",  # JSON_STRUCTURE_ERROR
            category=ErrorCategory.TRANSFORMATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source_component="DataTransformer"
        )
        error.add_context("nesting_level", json_data.max_nesting_level)
        error.add_context("max_nesting_level", MAX_NESTING_LEVEL)
        error.add_resolution_step("Reduce the nesting depth of your JSON structure")
        error.add_resolution_step("Pre-process the JSON to flatten deeply nested structures")
        return False, error
    
    # Check for extremely large arrays that might cause memory issues
    large_arrays_count = 0
    large_array_threshold = 10000  # Consider arrays with more than 10K items as large
    
    for path in json_data.array_paths:
        array_value = json_data.get_value_at_path(path)
        if isinstance(array_value, list) and len(array_value) > large_array_threshold:
            large_arrays_count += 1
            logger.warning(f"Large array detected at path {path} with {len(array_value)} items")
    
    if large_arrays_count > 0:
        logger.warning(f"JSON contains {large_arrays_count} large arrays that may impact performance")
        # This is a warning, not an error, so we don't return an error response
    
    # All validation checks passed
    return True, None


class TransformationStrategy(ABC):
    """
    An abstract base class for different JSON transformation strategies.
    
    This class defines the interface for transformation strategies that convert
    JSON data into pandas DataFrames using different approaches based on the 
    JSON structure.
    """
    
    @abstractmethod
    def transform(self, json_data: Dict[str, Any], options: ExcelOptions) -> pd.DataFrame:
        """
        Transforms JSON data into a pandas DataFrame.
        
        Args:
            json_data: The JSON data to transform
            options: Excel options for customizing the transformation
            
        Returns:
            A pandas DataFrame representation of the transformed data
        """
        pass


class FlatTransformationStrategy(TransformationStrategy):
    """
    A strategy for transforming flat JSON data (no nesting or arrays).
    
    This strategy is used for simple JSON structures where all values are at the root level
    and there are no nested objects or arrays.
    """
    
    def transform(self, json_data: Dict[str, Any], options: ExcelOptions) -> pd.DataFrame:
        """
        Transforms flat JSON data into a pandas DataFrame.
        
        Args:
            json_data: The flat JSON data to transform
            options: Excel options for customizing the transformation
            
        Returns:
            A pandas DataFrame representation of the transformed data
        """
        logger.debug("Using FlatTransformationStrategy")
        # For flat JSON, we can convert directly to a DataFrame
        return json_to_dataframe(json_data, options)


class NestedTransformationStrategy(TransformationStrategy):
    """
    A strategy for transforming nested JSON data.
    
    This strategy is used for JSON structures with nested objects but no arrays.
    It flattens the nested structure using dot notation for paths.
    """
    
    def transform(self, json_data: Dict[str, Any], options: ExcelOptions) -> pd.DataFrame:
        """
        Transforms nested JSON data into a pandas DataFrame with flattened structure.
        
        Args:
            json_data: The nested JSON data to transform
            options: Excel options for customizing the transformation
            
        Returns:
            A pandas DataFrame with flattened nested structure
        """
        logger.debug("Using NestedTransformationStrategy")
        # Flatten the nested structure
        flattened_data = flatten_json(json_data)
        # Convert to DataFrame
        return json_to_dataframe(flattened_data, options)


class ArrayTransformationStrategy(TransformationStrategy):
    """
    A strategy for transforming JSON data containing arrays.
    
    This strategy is used for JSON structures that contain arrays, optionally with nested objects.
    It processes arrays according to the specified array handling strategy.
    """
    
    def transform(self, json_data: Dict[str, Any], options: ExcelOptions, array_paths: List[str]) -> pd.DataFrame:
        """
        Transforms JSON data containing arrays into a pandas DataFrame.
        
        Args:
            json_data: The JSON data containing arrays to transform
            options: Excel options for customizing the transformation
            array_paths: Paths to arrays in the JSON structure
            
        Returns:
            A pandas DataFrame with processed arrays
        """
        logger.debug("Using ArrayTransformationStrategy")
        # Process arrays according to the handling strategy
        processed_data = process_arrays_in_json(json_data, array_paths, options.array_handling)
        
        # Check if the processed data also has nested structures
        has_nested = any(isinstance(v, dict) for v in processed_data.values())
        if has_nested:
            # Flatten nested structures
            processed_data = flatten_json(processed_data)
        
        # Convert to DataFrame
        return json_to_dataframe(processed_data, options)


class DataTransformer:
    """
    A class that transforms JSON data into tabular format suitable for Excel output.
    
    This class handles the transformation of various JSON structures (flat, nested, arrays)
    into pandas DataFrames that can be used to generate Excel files. It employs different
    transformation strategies based on the structure of the JSON data.
    """
    
    def __init__(self, options: Optional[ExcelOptions] = None):
        """
        Initializes a new DataTransformer instance with the specified options.
        
        Args:
            options: Excel options for customizing the transformation, or None to use defaults
        """
        self._options = options or ExcelOptions()
        self._logger = get_logger(__name__)
        self._logger.info("DataTransformer initialized")
    
    def transform_data(self, json_data: JSONData) -> Tuple[Optional[pd.DataFrame], Optional[ErrorResponse]]:
        """
        Transforms JSON data into a pandas DataFrame based on its structure and the configured options.
        
        Args:
            json_data: The JSON data to transform
            
        Returns:
            A tuple of (dataframe, error_response), where error_response is None if successful
        """
        self._logger.info(f"Starting transformation of JSON data from {json_data.source_path}")
        
        # First, ensure the JSON data has been analyzed
        if not json_data.is_analyzed:
            json_data.analyze_structure()
        
        # Validate the JSON data for transformation
        is_valid, error_response = validate_json_for_transformation(json_data)
        if not is_valid:
            self._logger.error(f"JSON validation failed: {error_response.message}")
            return None, error_response
        
        try:
            # Determine the appropriate transformation strategy
            strategy_type = json_data.get_flattening_strategy()
            self._logger.info(f"Using transformation strategy: {strategy_type}")
            
            # Apply the selected strategy
            if strategy_type == 'flat':
                df = self.transform_flat_json(json_data.content)
            elif strategy_type == 'nested':
                df = self.transform_nested_json(json_data.content)
            elif strategy_type == 'array':
                df = self.transform_json_with_arrays(json_data.content, json_data.array_paths)
            else:
                # Default to nested strategy if unknown
                self._logger.warning(f"Unknown strategy type: {strategy_type}, defaulting to nested")
                df = self.transform_nested_json(json_data.content)
            
            self._logger.info(f"Transformation completed successfully: {len(df)} rows, {len(df.columns)} columns")
            return df, None
            
        except NestedStructureError as e:
            self._logger.error(f"Nested structure error: {str(e)}")
            return None, e.error_response
        except MemoryError as e:
            self._logger.error(f"Memory error during transformation: {str(e)}")
            return None, e.error_response
        except Exception as e:
            self._logger.exception(f"Unexpected error during transformation: {str(e)}")
            error = ErrorResponse(
                message=f"Error during JSON transformation: {str(e)}",
                error_code="E999",  # UNKNOWN_ERROR
                category=ErrorCategory.TRANSFORMATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="DataTransformer"
            )
            error.add_context("error_type", type(e).__name__)
            error.add_resolution_step("Check JSON structure for unsupported patterns")
            error.add_resolution_step("Report this issue with details about your JSON data")
            return None, error
    
    def transform_flat_json(self, json_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transforms flat JSON data (no nesting or arrays) into a DataFrame.
        
        Args:
            json_data: The flat JSON data to transform
            
        Returns:
            A DataFrame representation of the flat JSON data
        """
        strategy = FlatTransformationStrategy()
        return strategy.transform(json_data, self._options)
    
    def transform_nested_json(self, json_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transforms nested JSON data into a DataFrame with flattened structure.
        
        Args:
            json_data: The nested JSON data to transform
            
        Returns:
            A DataFrame with flattened nested structure
        """
        strategy = NestedTransformationStrategy()
        return strategy.transform(json_data, self._options)
    
    def transform_json_with_arrays(self, json_data: Dict[str, Any], array_paths: List[str]) -> pd.DataFrame:
        """
        Transforms JSON data containing arrays into a DataFrame based on the configured array handling strategy.
        
        Args:
            json_data: The JSON data containing arrays to transform
            array_paths: Paths to arrays in the JSON structure
            
        Returns:
            A DataFrame with arrays processed according to strategy
        """
        strategy = ArrayTransformationStrategy()
        return strategy.transform(json_data, self._options, array_paths)
    
    def set_options(self, options: ExcelOptions) -> None:
        """
        Updates the transformation options.
        
        Args:
            options: New Excel options to use for transformations
        """
        self._options = options
        self._logger.info("Transformation options updated")
    
    def get_options(self) -> ExcelOptions:
        """
        Gets the current transformation options.
        
        Returns:
            The current Excel options
        """
        return self._options