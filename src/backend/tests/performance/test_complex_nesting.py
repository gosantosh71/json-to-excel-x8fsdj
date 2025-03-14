"""
Performance test module that evaluates the JSON to Excel Conversion Tool's ability to handle complex nested JSON structures. This module tests the performance and resource usage of the conversion process with varying levels of nesting depth to ensure the tool meets performance requirements for complex hierarchical data.
"""

import os  # standard library
import tempfile  # standard library
import json  # standard library
import copy  # standard library
import pytest  # v: 7.0.0+

from . import (
    PERFORMANCE_THRESHOLDS,
    NESTING_DEPTH_CATEGORIES,
    measure_performance,
    check_performance_against_threshold,
    create_temp_file
)
from ...input_handler import InputHandler
from ...json_parser import JSONParser
from ...data_transformer import DataTransformer
from ...excel_generator import ExcelGenerator
from ...models.json_data import JSONData
from ...monitoring.performance_tracker import PerformanceTracker, get_current_memory_usage
from ...tests.fixtures.json_fixtures import complex_json

# Define test parameters
TEST_NESTING_DEPTHS = {
    "shallow": 3,
    "medium": 5,
    "deep": 8,
    "very_deep": 10
}

TEST_FILE_SIZES = {
    "small": 100 * 1024,  # 100KB
    "medium": 1 * 1024 * 1024  # 1MB
}

def generate_nested_json_with_depth(max_depth, current_depth=0):
    """
    Generates a nested JSON structure with the specified maximum nesting depth.
    
    Args:
        max_depth: Maximum depth of nesting
        current_depth: Current depth in the recursion
        
    Returns:
        A dictionary with nested structure of the specified depth
    """
    # Create a base dictionary with some key-value pairs
    result = {
        f"key_{current_depth}_1": f"value_{current_depth}_1",
        f"key_{current_depth}_2": current_depth * 10,
        f"key_{current_depth}_3": True if current_depth % 2 == 0 else False
    }
    
    # If we haven't reached max depth, add a nested object
    if current_depth < max_depth:
        result[f"nested_{current_depth}"] = generate_nested_json_with_depth(max_depth, current_depth + 1)
    
    return result

def create_nested_test_file(max_depth):
    """
    Creates a temporary test file with a nested JSON structure of the specified depth.
    
    Args:
        max_depth: Maximum depth of nesting
        
    Returns:
        Path to the created temporary file
    """
    # Generate a nested JSON structure
    nested_json = generate_nested_json_with_depth(max_depth)
    
    # Convert the JSON structure to a string
    json_content = json.dumps(nested_json)
    
    # Create a temporary file with the JSON content
    temp_file_path = create_temp_file(json_content, ".json")
    
    return temp_file_path

def measure_nesting_performance(max_depth):
    """
    Measures the performance of processing a nested JSON structure with the specified depth.
    
    Args:
        max_depth: Maximum depth of nesting
        
    Returns:
        Performance metrics for processing the nested structure
    """
    # Create a nested test file with the specified depth
    json_file_path = create_nested_test_file(max_depth)
    
    # Create temporary output file path
    output_path = os.path.splitext(json_file_path)[0] + ".xlsx"
    
    # Initialize components
    performance_metrics = run_nested_json_performance_test(json_file_path, output_path)
    
    # Clean up temporary files
    try:
        os.remove(json_file_path)
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        print(f"Warning: Could not remove temporary files: {str(e)}")
    
    return performance_metrics

def run_nested_json_performance_test(json_file_path, excel_output_path):
    """
    Runs a complete performance test for a nested JSON structure with the specified depth.
    
    Args:
        json_file_path: Path to the JSON file
        excel_output_path: Path to the output Excel file
        
    Returns:
        Performance metrics for the entire conversion process
    """
    # Create instances of all required components
    input_handler = InputHandler()
    json_parser = JSONParser()
    data_transformer = DataTransformer()
    excel_generator = ExcelGenerator()
    
    performance_metrics = {}
    
    # Measure performance of InputHandler.process_input
    result, metrics = measure_performance(input_handler.read_json_file, json_file_path)
    performance_metrics["input_handler"] = metrics["execution_time"]
    
    # Measure performance of JSONParser.parse_string
    parsed_result, metrics = measure_performance(json_parser.parse_string, result)
    performance_metrics["json_parser"] = metrics["execution_time"]
    
    parsed_json, error = parsed_result
    if error:
        raise Exception(f"Error parsing JSON: {error.message}")
    
    # Measure performance of DataTransformer.transform
    transform_result, metrics = measure_performance(data_transformer.transform_data, parsed_json)
    performance_metrics["data_transformer"] = metrics["execution_time"]
    
    dataframe, error = transform_result
    if error:
        raise Exception(f"Error transforming data: {error.message}")
    
    # Measure performance of ExcelGenerator.generate_excel
    excel_result, metrics = measure_performance(excel_generator.generate_excel, dataframe, excel_output_path)
    performance_metrics["excel_generator"] = metrics["execution_time"]
    
    # Calculate total execution time
    performance_metrics["execution_time"] = (
        performance_metrics["input_handler"] +
        performance_metrics["json_parser"] +
        performance_metrics["data_transformer"] +
        performance_metrics["excel_generator"]
    )
    
    # Measure memory usage
    performance_metrics["memory_usage"] = get_current_memory_usage()
    
    return performance_metrics

def modify_complex_json_depth(json_data, target_depth):
    """
    Modifies the complex JSON test fixture to have a specific nesting depth.
    
    Args:
        json_data: Modified JSON data with the target nesting depth
        target_depth: Target nesting depth
        
    Returns:
        Modified JSON data with the target nesting depth
    """
    # Create a deep copy of the input JSON data
    data_copy = copy.deepcopy(json_data)
    
    # Calculate the current maximum nesting depth
    temp_json_data = JSONData(data_copy, "memory", 0)
    temp_json_data.analyze_structure()
    current_depth = temp_json_data.max_nesting_level
    
    # If target_depth > current depth, add additional nesting levels
    if target_depth > current_depth:
        current = data_copy
        for i in range(current_depth, target_depth):
            # Find a leaf node to extend
            if "profile" in current and isinstance(current["profile"], dict):
                current = current["profile"]
            elif "personal" in current and isinstance(current["personal"], dict):
                current = current["personal"]
            elif "contact" in current and isinstance(current["contact"], dict):
                current = current["contact"]
            elif "address" in current and isinstance(current["address"], dict):
                current = current["address"]
            else:
                # Create a new nested level
                current[f"level_{i}"] = {}
                current = current[f"level_{i}"]
    
    # If target_depth < current depth, reduce nesting levels
    elif target_depth < current_depth:
        # For simplicity, we'll create a new structure with the target depth
        data_copy = generate_nested_json_with_depth(target_depth)
    
    return data_copy

@pytest.mark.performance
def test_shallow_nesting_performance():
    """
    Tests the performance of converting a JSON file with shallow nesting (3 levels) to Excel.
    """
    # Measure performance with shallow nesting depth (3 levels)
    performance_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["shallow"])
    
    # Verify that performance metrics are within thresholds for small files
    is_within_threshold = check_performance_against_threshold(
        performance_metrics, "small")
    
    assert is_within_threshold, f"Performance exceeds thresholds for shallow nesting: {performance_metrics}"

@pytest.mark.performance
def test_medium_nesting_performance():
    """
    Tests the performance of converting a JSON file with medium nesting (5 levels) to Excel.
    """
    # Measure performance with medium nesting depth (5 levels)
    performance_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["medium"])
    
    # Verify that performance metrics are within thresholds for medium files
    is_within_threshold = check_performance_against_threshold(
        performance_metrics, "medium")
    
    assert is_within_threshold, f"Performance exceeds thresholds for medium nesting: {performance_metrics}"

@pytest.mark.performance
@pytest.mark.slow
def test_deep_nesting_performance():
    """
    Tests the performance of converting a JSON file with deep nesting (8 levels) to Excel.
    """
    # Measure performance with deep nesting depth (8 levels)
    performance_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["deep"])
    
    # Verify that performance metrics are within thresholds for medium files
    is_within_threshold = check_performance_against_threshold(
        performance_metrics, "medium")
    
    assert is_within_threshold, f"Performance exceeds thresholds for deep nesting: {performance_metrics}"

@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.xfail(reason='May exceed performance thresholds')
def test_very_deep_nesting_performance():
    """
    Tests the performance of converting a JSON file with very deep nesting (10 levels) to Excel.
    """
    # Measure performance with very deep nesting depth (10 levels)
    performance_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["very_deep"])
    
    # Verify that performance metrics are within thresholds for medium files
    is_within_threshold = check_performance_against_threshold(
        performance_metrics, "medium")
    
    assert is_within_threshold, f"Performance exceeds thresholds for very deep nesting: {performance_metrics}"
    # Note: This test is expected to potentially fail due to extreme nesting

@pytest.mark.performance
def test_complex_json_fixture_performance(complex_json):
    """
    Tests the performance of converting the complex JSON fixture to Excel.
    """
    # Use the complex_json fixture from json_fixtures
    temp_dir = tempfile.mkdtemp()
    json_file_path = os.path.join(temp_dir, "complex.json")
    excel_output_path = os.path.join(temp_dir, "complex.xlsx")
    
    # Write complex JSON to file
    with open(json_file_path, 'w') as f:
        json.dump(complex_json, f)
    
    # Run the nested JSON performance test
    performance_metrics = run_nested_json_performance_test(json_file_path, excel_output_path)
    
    # Verify that performance metrics are within thresholds
    is_within_threshold = check_performance_against_threshold(
        performance_metrics, "medium")
    
    # Clean up temporary files
    try:
        os.remove(json_file_path)
        if os.path.exists(excel_output_path):
            os.remove(excel_output_path)
        os.rmdir(temp_dir)
    except Exception as e:
        print(f"Warning: Could not remove temporary files: {str(e)}")
    
    assert is_within_threshold, f"Performance exceeds thresholds for complex JSON fixture: {performance_metrics}"

@pytest.mark.performance
def test_nesting_depth_impact():
    """
    Tests the impact of increasing nesting depth on performance metrics.
    """
    # Measure performance with multiple nesting depths (3, 5, 8)
    shallow_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["shallow"])
    medium_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["medium"])
    deep_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["deep"])
    
    # Compare performance metrics across different depths
    assert shallow_metrics["execution_time"] <= medium_metrics["execution_time"], \
        "Unexpected performance improvement with increased nesting depth"
    assert medium_metrics["execution_time"] <= deep_metrics["execution_time"], \
        "Unexpected performance improvement with increased nesting depth"
    
    # Verify that performance degrades in a predictable manner
    depth_impact_factor = deep_metrics["execution_time"] / shallow_metrics["execution_time"]
    assert depth_impact_factor < 5, \
        f"Nesting depth has a severe performance impact: {depth_impact_factor}x slower from shallow to deep"

@pytest.mark.performance
@pytest.mark.slow
def test_memory_usage_with_deep_nesting():
    """
    Tests the memory usage when processing deeply nested JSON structures.
    """
    # Create a deeply nested JSON structure (8 levels)
    json_file_path = create_nested_test_file(TEST_NESTING_DEPTHS["deep"])
    output_path = os.path.splitext(json_file_path)[0] + ".xlsx"
    
    # Track memory usage during the conversion process
    initial_memory = get_current_memory_usage()
    performance_metrics = run_nested_json_performance_test(json_file_path, output_path)
    final_memory = get_current_memory_usage()
    
    # Calculate memory delta
    memory_delta = final_memory - initial_memory
    
    # Clean up temporary files
    try:
        os.remove(json_file_path)
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        print(f"Warning: Could not remove temporary files: {str(e)}")
    
    # Verify that peak memory usage is within acceptable limits
    memory_threshold = PERFORMANCE_THRESHOLDS["medium"]["memory_mb"]
    assert memory_delta <= memory_threshold, \
        f"Memory usage for deep nesting ({memory_delta} MB) exceeds threshold ({memory_threshold} MB)"

@pytest.mark.performance
def test_component_performance_with_nesting():
    """
    Tests the performance of individual components when processing nested JSON.
    """
    # Create JSON structures with different nesting depths
    shallow_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["shallow"])
    deep_metrics = measure_nesting_performance(TEST_NESTING_DEPTHS["deep"])
    
    # Measure performance of each component
    shallow_components = {
        "input_handler": shallow_metrics["input_handler"],
        "json_parser": shallow_metrics["json_parser"],
        "data_transformer": shallow_metrics["data_transformer"],
        "excel_generator": shallow_metrics["excel_generator"]
    }
    
    deep_components = {
        "input_handler": deep_metrics["input_handler"],
        "json_parser": deep_metrics["json_parser"],
        "data_transformer": deep_metrics["data_transformer"],
        "excel_generator": deep_metrics["excel_generator"]
    }
    
    # Identify which components are most affected by nesting depth
    impact_factors = {}
    for component in shallow_components.keys():
        if shallow_components[component] > 0:  # Avoid division by zero
            impact_factors[component] = deep_components[component] / shallow_components[component]
        else:
            impact_factors[component] = 1.0  # Default if shallow time is 0
    
    # Verify that each component's performance is within thresholds
    for component, time in deep_components.items():
        component_threshold = PERFORMANCE_THRESHOLDS["medium"]["components"].get(component, 5.0)
        assert time <= component_threshold, \
            f"Component {component} exceeds time threshold with deep nesting: {time}s > {component_threshold}s"