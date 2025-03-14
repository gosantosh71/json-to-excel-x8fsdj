"""
Initialization module for performance tests that provides common utilities, constants, 
and helper functions for measuring and validating performance metrics of the JSON to Excel 
Conversion Tool. This module establishes performance thresholds, defines test categories, 
and implements measurement utilities used across all performance test modules.
"""

import os  # standard library
import time  # standard library
import tempfile  # standard library
import json  # standard library
import contextlib  # standard library
from typing import Any, Dict, List, Tuple, Callable, Optional  # standard library
import pytest  # v: 7.3.0+

from ...monitoring.performance_tracker import PerformanceTracker, get_current_memory_usage

# Define file size categories in bytes
FILE_SIZE_CATEGORIES = {
    "small": 100 * 1024,  # 100KB
    "medium": 1 * 1024 * 1024,  # 1MB
    "large": 5 * 1024 * 1024,  # 5MB
}

# Define nesting depth categories
NESTING_DEPTH_CATEGORIES = {
    "shallow": 3,
    "medium": 5,
    "deep": 8,
    "very_deep": 10
}

# Define performance thresholds for different file size categories
PERFORMANCE_THRESHOLDS = {
    "small": {
        "total_time": 3.0,  # seconds
        "memory_mb": 100,  # megabytes
        "components": {
            "input_handler": 0.5,
            "json_parser": 0.5,
            "data_transformer": 1.0,
            "excel_generator": 1.0
        }
    },
    "medium": {
        "total_time": 10.0,  # seconds
        "memory_mb": 300,  # megabytes
        "components": {
            "input_handler": 2.0,
            "json_parser": 2.0,
            "data_transformer": 3.0,
            "excel_generator": 3.0
        }
    },
    "large": {
        "total_time": 30.0,  # seconds
        "memory_mb": 700,  # megabytes
        "components": {
            "input_handler": 5.0,
            "json_parser": 5.0,
            "data_transformer": 10.0,
            "excel_generator": 10.0
        }
    }
}

# Create a singleton instance of the performance tracker
performance_tracker = PerformanceTracker()


def measure_performance(func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, float]]:
    """
    Measures the execution time and memory usage of a function call.
    
    Args:
        func: The function to measure
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        A tuple containing (result, performance_metrics) where performance_metrics is a dict 
        with execution_time and memory_usage
    """
    # Record starting memory usage
    start_memory = get_current_memory_usage()
    
    # Record starting time
    start_time = time.time()
    
    # Execute the function
    result = func(*args, **kwargs)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Calculate memory usage delta
    end_memory = get_current_memory_usage()
    memory_usage = end_memory - start_memory
    
    # Create performance metrics
    performance_metrics = {
        "execution_time": execution_time,
        "memory_usage": memory_usage
    }
    
    return result, performance_metrics


def check_performance_against_threshold(performance_metrics: Dict[str, float], 
                                        size_category: str) -> bool:
    """
    Checks if performance metrics are within the defined thresholds for a given file size category.
    
    Args:
        performance_metrics: Dictionary containing performance metrics
        size_category: Size category to check against (small, medium, large)
        
    Returns:
        True if all metrics are within thresholds, False otherwise
    """
    # Get thresholds for the specified size category
    thresholds = PERFORMANCE_THRESHOLDS.get(size_category)
    if not thresholds:
        raise ValueError(f"Invalid size category: {size_category}")
    
    # Check total execution time
    if performance_metrics.get("execution_time", 0) > thresholds["total_time"]:
        return False
    
    # Check memory usage
    if performance_metrics.get("memory_usage", 0) > thresholds["memory_mb"]:
        return False
    
    # Check component-specific execution times
    for component, time_metric in performance_metrics.items():
        if component in thresholds["components"] and time_metric > thresholds["components"][component]:
            return False
    
    return True


def create_temp_file(content: str, suffix: str) -> str:
    """
    Creates a temporary file with the given content and returns its path.
    
    Args:
        content: Content to write to the file
        suffix: File suffix (extension)
        
    Returns:
        Path to the created temporary file
    """
    # Create a temporary file with the specified suffix
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    # Write the content to the file
    with open(temp_file.name, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return temp_file.name


def get_file_size_category(file_size_bytes: int) -> str:
    """
    Determines the size category of a file based on its size in bytes.
    
    Args:
        file_size_bytes: Size of the file in bytes
        
    Returns:
        Size category: 'small', 'medium', or 'large'
    """
    if file_size_bytes < FILE_SIZE_CATEGORIES["medium"]:
        return "small"
    elif file_size_bytes < FILE_SIZE_CATEGORIES["large"]:
        return "medium"
    else:
        return "large"


@contextlib.contextmanager
def performance_test_context():
    """
    Context manager for setting up and tearing down performance test environment.
    
    Returns:
        A context manager for performance testing
    """
    # Reset the performance tracker before the test
    performance_tracker.reset()
    
    try:
        # Yield control to the test
        yield
    finally:
        # Clean up any resources after the test
        # Log performance summary for debugging
        performance_summary = performance_tracker.get_performance_summary()


class PerformanceTestCase:
    """
    Base class for performance tests that provides common utilities and assertions.
    """
    
    def __init__(self):
        """
        Initializes a new PerformanceTestCase instance.
        """
        self._tracker = performance_tracker
    
    def measure_function(self, func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, float]]:
        """
        Measures the performance of a function call.
        
        Args:
            func: The function to measure
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            A tuple containing (result, performance_metrics)
        """
        return measure_performance(func, *args, **kwargs)
    
    def assert_performance_within_threshold(self, performance_metrics: Dict[str, float], 
                                           size_category: str) -> None:
        """
        Asserts that performance metrics are within the defined thresholds.
        
        Args:
            performance_metrics: Dictionary containing performance metrics
            size_category: Size category to check against (small, medium, large)
            
        Returns:
            None: Raises AssertionError if performance exceeds thresholds
        """
        within_threshold = check_performance_against_threshold(performance_metrics, size_category)
        
        if not within_threshold:
            # Construct a detailed error message
            thresholds = PERFORMANCE_THRESHOLDS.get(size_category, {})
            
            error_msg = f"Performance exceeds thresholds for {size_category} category:\n"
            
            # Add details for total time
            total_time = performance_metrics.get("execution_time", 0)
            time_threshold = thresholds.get("total_time", "N/A")
            error_msg += f"- Total time: {total_time:.2f}s (threshold: {time_threshold}s)\n"
            
            # Add details for memory usage
            memory_usage = performance_metrics.get("memory_usage", 0)
            memory_threshold = thresholds.get("memory_mb", "N/A")
            error_msg += f"- Memory usage: {memory_usage:.2f}MB (threshold: {memory_threshold}MB)\n"
            
            # Add details for component-specific times
            component_thresholds = thresholds.get("components", {})
            for component, time_metric in performance_metrics.items():
                if component in component_thresholds:
                    component_threshold = component_thresholds[component]
                    error_msg += f"- {component}: {time_metric:.2f}s (threshold: {component_threshold}s)\n"
            
            raise AssertionError(error_msg)
    
    def setup_test_files(self, json_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Sets up temporary test files for performance testing.
        
        Args:
            json_data: JSON data to write to the test file
            
        Returns:
            A tuple containing (json_file_path, excel_output_path)
        """
        # Convert JSON data to string
        json_content = json.dumps(json_data)
        
        # Create a temporary JSON file
        json_file_path = create_temp_file(json_content, ".json")
        
        # Create a temporary path for the Excel output
        excel_output_path = os.path.splitext(json_file_path)[0] + ".xlsx"
        
        return json_file_path, excel_output_path
    
    def teardown_test_files(self, file_paths: List[str]) -> None:
        """
        Cleans up temporary test files after testing.
        
        Args:
            file_paths: List of file paths to clean up
            
        Returns:
            None: Removes the temporary files
        """
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    # Log the cleanup operation
                    print(f"Warning: Failed to remove temporary file {file_path}: {str(e)}")