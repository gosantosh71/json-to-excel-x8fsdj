"""
Performance test module that evaluates the JSON to Excel Conversion Tool's ability to handle large JSON files. This module tests the performance and resource usage of the conversion process with files of varying sizes to ensure the tool meets performance requirements.
"""

import os  # standard library
import tempfile  # standard library
import json  # standard library
import pandas as pd  # v: 1.5.0+
import pytest  # v: 7.0.0+

from . import (
    PERFORMANCE_THRESHOLDS,
    FILE_SIZE_CATEGORIES,
    measure_performance,
    check_performance_against_threshold,
    create_temp_file,
    get_file_size_category
)

from ...input_handler import InputHandler
from ...json_parser import JSONParser
from ...data_transformer import DataTransformer
from ...excel_generator import ExcelGenerator
from ...scripts.generate_test_data import (
    generate_flat_json,
    generate_nested_json,
    generate_array_json,
    generate_complex_json
)
from ...models.json_data import JSONData
from .. import create_temp_json_file, cleanup_temp_file

# Define test file sizes
TEST_FILE_SIZES = {"small": 100 * 1024, "medium": 1 * 1024 * 1024, "large": 5 * 1024 * 1024}

# Define test record counts
TEST_RECORD_COUNTS = {"small": 100, "medium": 1000, "large": 5000}


def generate_large_flat_json(num_records):
    """
    Generates a large flat JSON file with the specified number of records.
    
    Args:
        num_records: Number of records to generate
        
    Returns:
        A dictionary containing a large number of flat key-value pairs
    """
    result = {"records": []}
    
    # Generate num_records flat JSON objects
    for i in range(num_records):
        record = generate_flat_json(10, True)  # 10 fields per record, include all types
        record["id"] = i + 1
        result["records"].append(record)
    
    return result


def generate_large_nested_json(num_records, max_depth):
    """
    Generates a large nested JSON file with the specified number of records.
    
    Args:
        num_records: Number of records to generate
        max_depth: Maximum nesting depth
        
    Returns:
        A dictionary containing a large number of nested objects
    """
    result = {"records": []}
    
    # Generate num_records nested JSON objects
    for i in range(num_records):
        record = generate_nested_json(max_depth, 3, True)  # max_depth, 3 children per level, include arrays
        record["id"] = i + 1
        result["records"].append(record)
    
    return result


def generate_large_array_json(num_records, max_array_length):
    """
    Generates a large JSON file with arrays containing the specified number of records.
    
    Args:
        num_records: Number of records to generate
        max_array_length: Maximum length of arrays
        
    Returns:
        A dictionary containing large arrays of objects or values
    """
    result = {
        "string_array": [],
        "number_array": [],
        "boolean_array": [],
        "object_array": [],
        "mixed_array": []
    }
    
    # Populate arrays
    for i in range(num_records):
        # Add to different array types
        result["string_array"].append(f"string_{i}")
        result["number_array"].append(i)
        result["boolean_array"].append(i % 2 == 0)
        
        if i < max_array_length:
            # Create complex objects for object array (limit to max_array_length)
            result["object_array"].append(generate_flat_json(5, True))
        
        # Mixed array with different types
        if i % 3 == 0:
            result["mixed_array"].append(f"string_{i}")
        elif i % 3 == 1:
            result["mixed_array"].append(i)
        else:
            result["mixed_array"].append(generate_flat_json(3, True))
    
    return result


def create_test_file(json_data, target_size_bytes):
    """
    Creates a temporary test file with the specified JSON content and target size.
    
    Args:
        json_data: JSON data to write to the file
        target_size_bytes: Target file size in bytes
        
    Returns:
        Path to the created temporary file
    """
    # Convert to JSON string
    json_string = json.dumps(json_data)
    current_size = len(json_string.encode('utf-8'))
    
    # If current size is less than target, pad with additional data
    if current_size < target_size_bytes:
        padding_needed = target_size_bytes - current_size
        
        # Create a padding object with repeated data
        padding_obj = {"padding": "x" * (padding_needed // 10)}
        
        # Add padding to the JSON data
        if isinstance(json_data, dict):
            json_data["padding"] = padding_obj
            json_string = json.dumps(json_data)
    
    # Create a temporary file with the JSON content
    fd, temp_path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(json_string)
    except Exception as e:
        os.close(fd)
        os.unlink(temp_path)
        raise e
    
    return temp_path


def measure_component_performance(component_name, component_function, *args, **kwargs):
    """
    Measures the performance of a specific component in the conversion pipeline.
    
    Args:
        component_name: Name of the component
        component_function: Function to measure
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Performance metrics for the component
    """
    # Use measure_performance utility to get metrics
    result, metrics = measure_performance(component_function, *args, **kwargs)
    
    # Log the results
    print(f"{component_name} performance: {metrics['execution_time']:.4f}s, {metrics['memory_usage']:.2f}MB")
    
    return {
        component_name: metrics["execution_time"],
        "memory_usage": metrics["memory_usage"],
        "result": result
    }


def run_end_to_end_performance_test(json_file_path, excel_output_path):
    """
    Runs an end-to-end performance test of the JSON to Excel conversion process.
    
    Args:
        json_file_path: Path to the JSON input file
        excel_output_path: Path for the Excel output file
        
    Returns:
        Performance metrics for the entire conversion process
    """
    # Create instances of all required components
    input_handler = InputHandler()
    json_parser = JSONParser()
    data_transformer = DataTransformer()
    excel_generator = ExcelGenerator()
    
    # Measure input handling performance
    print(f"Processing input file: {json_file_path}")
    json_data, input_metrics = measure_performance(input_handler.read_json_file, json_file_path)
    
    # Create JSONData object
    json_data_obj = JSONData(json_data, json_file_path, os.path.getsize(json_file_path))
    json_data_obj.analyze_structure()
    
    # Measure transformation performance
    print("Transforming JSON data to tabular format")
    transform_result, transform_metrics = measure_performance(data_transformer.transform_data, json_data_obj)
    df, _ = transform_result  # Unpack the tuple (df, error)
    
    # Measure Excel generation performance
    print(f"Generating Excel file: {excel_output_path}")
    success, excel_metrics = measure_performance(excel_generator.generate_excel, df, excel_output_path)
    
    # Calculate total metrics
    total_time = input_metrics["execution_time"] + transform_metrics["execution_time"] + excel_metrics["execution_time"]
    peak_memory = max(input_metrics["memory_usage"], transform_metrics["memory_usage"], excel_metrics["memory_usage"])
    
    # Return comprehensive metrics
    return {
        "total_time": total_time,
        "peak_memory": peak_memory,
        "input_handler": input_metrics["execution_time"],
        "data_transformer": transform_metrics["execution_time"],
        "excel_generator": excel_metrics["execution_time"]
    }


@pytest.mark.performance
def test_small_flat_json_performance():
    """
    Tests the performance of converting a small flat JSON file to Excel.
    """
    # Generate a small flat JSON file
    json_data = generate_large_flat_json(TEST_RECORD_COUNTS["small"])
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["small"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for small files
        size_category = "small"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} files"
            
        # Check component-specific thresholds
        for component, time in [
            ("input_handler", metrics["input_handler"]),
            ("data_transformer", metrics["data_transformer"]),
            ("excel_generator", metrics["excel_generator"])
        ]:
            assert time <= PERFORMANCE_THRESHOLDS[size_category]["components"][component], \
                f"{component} time ({time:.2f}s) exceeds threshold for {size_category} files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
def test_medium_flat_json_performance():
    """
    Tests the performance of converting a medium-sized flat JSON file to Excel.
    """
    # Generate a medium-sized flat JSON file
    json_data = generate_large_flat_json(TEST_RECORD_COUNTS["medium"])
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["medium"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for medium files
        size_category = "medium"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} files"
            
        # Check component-specific thresholds
        for component, time in [
            ("input_handler", metrics["input_handler"]),
            ("data_transformer", metrics["data_transformer"]),
            ("excel_generator", metrics["excel_generator"])
        ]:
            assert time <= PERFORMANCE_THRESHOLDS[size_category]["components"][component], \
                f"{component} time ({time:.2f}s) exceeds threshold for {size_category} files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
@pytest.mark.slow
def test_large_flat_json_performance():
    """
    Tests the performance of converting a large flat JSON file to Excel.
    """
    # Generate a large flat JSON file
    json_data = generate_large_flat_json(TEST_RECORD_COUNTS["large"])
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["large"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for large files
        size_category = "large"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} files"
            
        # Check component-specific thresholds
        for component, time in [
            ("input_handler", metrics["input_handler"]),
            ("data_transformer", metrics["data_transformer"]),
            ("excel_generator", metrics["excel_generator"])
        ]:
            assert time <= PERFORMANCE_THRESHOLDS[size_category]["components"][component], \
                f"{component} time ({time:.2f}s) exceeds threshold for {size_category} files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
def test_medium_nested_json_performance():
    """
    Tests the performance of converting a medium-sized nested JSON file to Excel.
    """
    # Generate a medium-sized nested JSON file with moderate depth
    json_data = generate_large_nested_json(TEST_RECORD_COUNTS["medium"] // 10, 5)
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["medium"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for medium files
        size_category = "medium"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} nested files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} nested files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
@pytest.mark.slow
def test_large_nested_json_performance():
    """
    Tests the performance of converting a large nested JSON file to Excel.
    """
    # Generate a large nested JSON file with significant depth
    json_data = generate_large_nested_json(TEST_RECORD_COUNTS["large"] // 10, 7)
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["large"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for large files
        size_category = "large"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} nested files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} nested files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
def test_medium_array_json_performance():
    """
    Tests the performance of converting a medium-sized JSON file with arrays to Excel.
    """
    # Generate a medium-sized JSON file with arrays
    json_data = generate_large_array_json(TEST_RECORD_COUNTS["medium"], 100)
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["medium"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that performance meets requirements for medium files
        size_category = "medium"
        assert metrics["total_time"] <= PERFORMANCE_THRESHOLDS[size_category]["total_time"], \
            f"Total time ({metrics['total_time']:.2f}s) exceeds threshold for {size_category} array files"
            
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS[size_category]["memory_mb"], \
            f"Memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for {size_category} array files"
                
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)


@pytest.mark.performance
def test_component_performance_input_handler():
    """
    Tests the performance of the InputHandler component with files of different sizes.
    """
    input_handler = InputHandler()
    
    for size_category in ["small", "medium", "large"]:
        # Generate a JSON file of the appropriate size
        json_data = generate_large_flat_json(TEST_RECORD_COUNTS[size_category])
        json_file_path = create_test_file(json_data, TEST_FILE_SIZES[size_category])
        
        try:
            # Measure performance of InputHandler.read_json_file
            _, metrics = measure_performance(input_handler.read_json_file, json_file_path)
            
            # Verify performance against threshold
            assert metrics["execution_time"] <= PERFORMANCE_THRESHOLDS[size_category]["components"]["input_handler"], \
                f"InputHandler execution time ({metrics['execution_time']:.2f}s) exceeds threshold for {size_category} files"
        finally:
            cleanup_temp_file(json_file_path)


@pytest.mark.performance
def test_component_performance_json_parser():
    """
    Tests the performance of the JSONParser component with files of different sizes.
    """
    json_parser = JSONParser()
    
    for size_category in ["small", "medium", "large"]:
        # Generate a JSON file of the appropriate size
        json_data = generate_large_flat_json(TEST_RECORD_COUNTS[size_category])
        json_string = json.dumps(json_data)
        
        # Measure performance of JSONParser.parse_string
        _, metrics = measure_performance(json_parser.parse_string, json_string)
        
        # Verify performance against threshold
        assert metrics["execution_time"] <= PERFORMANCE_THRESHOLDS[size_category]["components"]["json_parser"], \
            f"JSONParser execution time ({metrics['execution_time']:.2f}s) exceeds threshold for {size_category} files"


@pytest.mark.performance
def test_component_performance_data_transformer():
    """
    Tests the performance of the DataTransformer component with files of different sizes.
    """
    data_transformer = DataTransformer()
    
    for size_category in ["small", "medium", "large"]:
        # Generate a JSON file of the appropriate size
        json_data = generate_large_flat_json(TEST_RECORD_COUNTS[size_category])
        
        # Create a JSONData object
        json_data_obj = JSONData(json_data, "memory", len(json.dumps(json_data)))
        json_data_obj.analyze_structure()
        
        # Measure performance of DataTransformer.transform
        _, metrics = measure_performance(data_transformer.transform_data, json_data_obj)
        
        # Verify performance against threshold
        assert metrics["execution_time"] <= PERFORMANCE_THRESHOLDS[size_category]["components"]["data_transformer"], \
            f"DataTransformer execution time ({metrics['execution_time']:.2f}s) exceeds threshold for {size_category} files"


@pytest.mark.performance
def test_component_performance_excel_generator():
    """
    Tests the performance of the ExcelGenerator component with DataFrames of different sizes.
    """
    excel_generator = ExcelGenerator()
    
    for size_category in ["small", "medium", "large"]:
        # Create a DataFrame of the appropriate size
        num_rows = TEST_RECORD_COUNTS[size_category]
        df = pd.DataFrame({
            f'col_{i}': [f'value_{i}_{j}' for j in range(num_rows)]
            for i in range(10)  # 10 columns
        })
        
        # Create a temporary output file
        fd, excel_output_path = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
        
        try:
            # Measure performance of ExcelGenerator.generate_excel
            _, metrics = measure_performance(
                excel_generator.generate_excel, 
                df, 
                excel_output_path
            )
            
            # Verify performance against threshold
            assert metrics["execution_time"] <= PERFORMANCE_THRESHOLDS[size_category]["components"]["excel_generator"], \
                f"ExcelGenerator execution time ({metrics['execution_time']:.2f}s) exceeds threshold for {size_category} files"
        finally:
            cleanup_temp_file(excel_output_path)


@pytest.mark.performance
@pytest.mark.slow
def test_memory_usage_large_files():
    """
    Tests the memory usage when processing large JSON files.
    """
    # Generate a large JSON file
    json_data = generate_complex_json(6, 6, 0.3)  # depth, breadth, array_probability
    json_file_path = create_test_file(json_data, TEST_FILE_SIZES["large"])
    excel_output_path = json_file_path.replace('.json', '.xlsx')
    
    try:
        # Run the end-to-end performance test with memory tracking
        metrics = run_end_to_end_performance_test(json_file_path, excel_output_path)
        
        # Verify that peak memory usage is within acceptable limits
        assert metrics["peak_memory"] <= PERFORMANCE_THRESHOLDS["large"]["memory_mb"], \
            f"Peak memory usage ({metrics['peak_memory']:.2f}MB) exceeds threshold for large files"
    finally:
        # Clean up temporary files
        cleanup_temp_file(json_file_path)
        cleanup_temp_file(excel_output_path)