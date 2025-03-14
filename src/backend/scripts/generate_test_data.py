#!/usr/bin/env python3
"""
Utility script for generating test JSON data files with various structures and complexities.

This script creates sample JSON files for testing the JSON to Excel Conversion Tool.
It can generate flat, nested, and array-based JSON structures with configurable parameters
to simulate real-world data scenarios.
"""

import json  # v: built-in
import os  # v: built-in
import random  # v: built-in
import argparse  # v: built-in
import datetime  # v: built-in
from typing import Dict, List, Any, Optional, Union  # v: built-in

from ..models.json_data import JSONData, JSONComplexity
from ..logger import get_logger
from ..utils import create_directory_if_not_exists
from ..constants import JSON_CONSTANTS

# Initialize logger
logger = get_logger(__name__)

# Default configuration
DEFAULT_OUTPUT_DIR = os.path.join('src', 'backend', 'tests', 'fixtures', 'sample_data')
DEFAULT_NUM_RECORDS = 10


def generate_flat_json(num_fields: int, include_all_types: bool) -> Dict[str, Any]:
    """
    Generates a flat JSON structure with simple key-value pairs.
    
    Args:
        num_fields: Number of fields to generate
        include_all_types: Whether to include all data types (string, number, boolean, null)
        
    Returns:
        A dictionary with flat key-value pairs
    """
    data = {}
    
    # Generate simple key-value pairs
    for i in range(num_fields):
        key = f"field_{i + 1}"
        
        if include_all_types:
            # Distribute different types across fields
            type_index = i % 5  # cycle through 5 types
            
            if type_index == 0:
                data[key] = generate_random_value("string")
            elif type_index == 1:
                data[key] = generate_random_value("number")
            elif type_index == 2:
                data[key] = generate_random_value("boolean")
            elif type_index == 3:
                data[key] = generate_random_value("null")
            else:
                data[key] = generate_random_value("date")
        else:
            # Just use strings for simplicity
            data[key] = generate_random_value("string")
    
    logger.debug(f"Generated flat JSON with {num_fields} fields")
    return data


def generate_nested_json(max_depth: int, max_children: int, include_arrays: bool) -> Dict[str, Any]:
    """
    Generates a nested JSON structure with configurable depth and complexity.
    
    Args:
        max_depth: Maximum nesting depth
        max_children: Maximum number of children per level
        include_arrays: Whether to include arrays in the structure
        
    Returns:
        A dictionary with nested objects and optionally arrays
    """
    def _generate_nested(current_depth: int) -> Union[Dict[str, Any], List[Any], Any]:
        if current_depth >= max_depth:
            # At max depth, return primitive values
            return generate_random_value("string")
        
        # Decide whether to create an object or array at this level
        if include_arrays and random.random() < 0.3:  # 30% chance of array when allowed
            # Create an array
            array_length = random.randint(1, max_children)
            array_items = []
            
            for _ in range(array_length):
                # Decide whether array items are objects or primitives
                if random.random() < 0.7:  # 70% chance of objects in arrays
                    array_items.append(_generate_nested(current_depth + 1))
                else:
                    array_items.append(generate_random_value())
                    
            return array_items
        else:
            # Create an object
            result = {}
            num_children = random.randint(1, max_children)
            
            for i in range(num_children):
                key = f"nested_field_{current_depth}_{i + 1}"
                result[key] = _generate_nested(current_depth + 1)
                
            return result
    
    # Start the recursive generation
    root = {
        "id": random.randint(1000, 9999),
        "name": f"Test Nested JSON {max_depth} Levels",
        "created_at": datetime.datetime.now().isoformat(),
        "data": _generate_nested(1)
    }
    
    logger.debug(f"Generated nested JSON with max depth {max_depth}")
    return root


def generate_array_json(num_arrays: int, max_array_length: int, use_object_arrays: bool) -> Dict[str, Any]:
    """
    Generates a JSON structure with arrays of objects or primitive values.
    
    Args:
        num_arrays: Number of arrays to include
        max_array_length: Maximum length of each array
        use_object_arrays: Whether arrays should contain objects or primitive values
        
    Returns:
        A dictionary containing arrays of values or objects
    """
    data = {
        "id": random.randint(1000, 9999),
        "name": "Array Test Data",
        "created_at": datetime.datetime.now().isoformat(),
        "description": f"JSON with {num_arrays} arrays, max length {max_array_length}",
    }
    
    for i in range(num_arrays):
        array_name = f"array_{i + 1}"
        array_length = random.randint(1, max_array_length)
        
        if use_object_arrays:
            # Generate array of objects
            data[array_name] = []
            for j in range(array_length):
                obj = {
                    "id": j + 1,
                    "name": f"Item {j + 1}",
                    "value": generate_random_value("number"),
                    "active": generate_random_value("boolean")
                }
                data[array_name].append(obj)
        else:
            # Generate array of primitive values
            data[array_name] = []
            for _ in range(array_length):
                data[array_name].append(generate_random_value())
    
    logger.debug(f"Generated JSON with {num_arrays} arrays")
    return data


def generate_complex_json(max_depth: int, max_breadth: int, array_probability: float) -> Dict[str, Any]:
    """
    Generates a complex JSON structure with a mix of nested objects and arrays.
    
    Args:
        max_depth: Maximum nesting depth
        max_breadth: Maximum number of properties per object
        array_probability: Probability (0-1) of generating an array vs object
        
    Returns:
        A complex dictionary with mixed nested objects and arrays
    """
    def _generate_complex(current_depth: int) -> Any:
        if current_depth >= max_depth:
            # At max depth, return primitive values
            return generate_random_value()
        
        # Decide whether to create a nested structure or primitive value
        if current_depth > 0 and random.random() < 0.3:
            # 30% chance to stop nesting early with a primitive value
            return generate_random_value()
        
        # Decide whether to create an object or array
        if random.random() < array_probability:
            # Create an array
            array_length = random.randint(1, max_breadth)
            return [_generate_complex(current_depth + 1) for _ in range(array_length)]
        else:
            # Create an object
            result = {}
            num_props = random.randint(1, max_breadth)
            
            for i in range(num_props):
                key = f"prop_{current_depth}_{i + 1}"
                result[key] = _generate_complex(current_depth + 1)
                
            return result
    
    # Create the root object with metadata
    root = {
        "metadata": {
            "id": random.randint(1000, 9999),
            "name": f"Complex JSON {max_depth}x{max_breadth}",
            "generated_at": datetime.datetime.now().isoformat(),
            "complexity": {
                "max_depth": max_depth,
                "max_breadth": max_breadth,
                "array_probability": array_probability
            }
        },
        # Main data content
        "content": _generate_complex(0)
    }
    
    logger.debug(f"Generated complex JSON with depth {max_depth}, breadth {max_breadth}")
    return root


def generate_random_value(value_type: str = None) -> Any:
    """
    Generates a random value of a specified or random type.
    
    Args:
        value_type: Type of value to generate ("string", "number", "boolean", "null", "date", "array")
                   If None, a random type will be chosen
    
    Returns:
        A random value of the specified type
    """
    # If no type specified, choose one randomly
    if value_type is None:
        value_type = random.choice(["string", "number", "boolean", "null", "date"])
    
    # Generate value based on type
    if value_type == "string":
        # Generate a random string of 5-15 characters
        length = random.randint(5, 15)
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
    elif value_type == "number":
        # Decide between integer and float
        if random.random() < 0.5:
            return random.randint(1, 1000)
        else:
            return round(random.uniform(1.0, 1000.0), 2)
    
    elif value_type == "boolean":
        return random.choice([True, False])
    
    elif value_type == "null":
        return None
    
    elif value_type == "date":
        # Generate a random date in ISO format
        year = random.randint(2000, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Using 28 to avoid invalid dates
        return f"{year}-{month:02d}-{day:02d}"
    
    elif value_type == "array":
        # Generate a small array of primitive values
        length = random.randint(1, 5)
        return [generate_random_value(random.choice(["string", "number", "boolean"])) 
                for _ in range(length)]
    
    else:
        logger.warning(f"Unknown value type: {value_type}, defaulting to string")
        return generate_random_value("string")


def save_json_file(data: Dict[str, Any], filename: str, output_dir: str) -> str:
    """
    Saves a JSON structure to a file with proper formatting.
    
    Args:
        data: The JSON data to save
        filename: Name of the output file
        output_dir: Directory where to save the file
        
    Returns:
        The full path to the saved file
    """
    # Ensure the output directory exists
    create_directory_if_not_exists(output_dir)
    
    # Construct full file path
    file_path = os.path.join(output_dir, filename)
    
    # Write JSON to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    file_size = os.path.getsize(file_path)
    logger.info(f"Saved JSON to {file_path} ({file_size} bytes)")
    
    return file_path


def analyze_and_print_json_info(data: Dict[str, Any], file_path: str) -> None:
    """
    Analyzes a JSON structure and prints information about its complexity.
    
    Args:
        data: The JSON data to analyze
        file_path: Path to the saved JSON file
    """
    # Create a JSONData object
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    json_data = JSONData(content=data, source_path=file_path, size_bytes=file_size)
    
    # Analyze the structure
    json_data.analyze_structure()
    
    # Print analysis information
    print(f"\nAnalysis of {os.path.basename(file_path)}:")
    print(f"  - Size: {file_size} bytes")
    print(f"  - Nesting Depth: {json_data.max_nesting_level}")
    print(f"  - Contains Arrays: {json_data.contains_arrays}")
    print(f"  - Array Paths: {len(json_data.array_paths)}")
    print(f"  - Complexity Level: {json_data.complexity_level.name}")
    print(f"  - Complexity Score: {json_data.complexity_score}")
    
    # Log the analysis
    logger.info(f"Analysis for {file_path}: complexity={json_data.complexity_level.name}, "
                f"depth={json_data.max_nesting_level}, arrays={len(json_data.array_paths)}")


def generate_all_test_files(output_dir: str, num_records: int) -> List[str]:
    """
    Generates a complete set of test JSON files with various structures.
    
    Args:
        output_dir: Directory where to save the files
        num_records: Base number of records to include in the files
        
    Returns:
        List of paths to the generated files
    """
    generated_files = []
    
    # Generate flat JSON (simple)
    flat_data = generate_flat_json(num_records, True)
    flat_file = save_json_file(flat_data, "flat_json_sample.json", output_dir)
    analyze_and_print_json_info(flat_data, flat_file)
    generated_files.append(flat_file)
    
    # Generate nested JSON (moderate complexity)
    nested_data = generate_nested_json(5, 3, False)
    nested_file = save_json_file(nested_data, "nested_json_sample.json", output_dir)
    analyze_and_print_json_info(nested_data, nested_file)
    generated_files.append(nested_file)
    
    # Generate nested JSON with arrays (higher complexity)
    nested_array_data = generate_nested_json(5, 3, True)
    nested_array_file = save_json_file(nested_array_data, "nested_with_arrays_sample.json", output_dir)
    analyze_and_print_json_info(nested_array_data, nested_array_file)
    generated_files.append(nested_array_file)
    
    # Generate array-based JSON (object arrays)
    array_obj_data = generate_array_json(5, num_records, True)
    array_obj_file = save_json_file(array_obj_data, "array_objects_sample.json", output_dir)
    analyze_and_print_json_info(array_obj_data, array_obj_file)
    generated_files.append(array_obj_file)
    
    # Generate array-based JSON (primitive arrays)
    array_prim_data = generate_array_json(5, num_records, False)
    array_prim_file = save_json_file(array_prim_data, "array_primitives_sample.json", output_dir)
    analyze_and_print_json_info(array_prim_data, array_prim_file)
    generated_files.append(array_prim_file)
    
    # Generate complex mixed JSON (high complexity)
    complex_data = generate_complex_json(7, 5, 0.4)
    complex_file = save_json_file(complex_data, "complex_mixed_sample.json", output_dir)
    analyze_and_print_json_info(complex_data, complex_file)
    generated_files.append(complex_file)
    
    # Generate large JSON (for performance testing)
    large_data = generate_complex_json(5, 10, 0.3)
    # Add more data to make it larger
    for i in range(20):
        large_data[f"extra_section_{i}"] = generate_nested_json(3, 5, True)
    large_file = save_json_file(large_data, "large_sample.json", output_dir)
    analyze_and_print_json_info(large_data, large_file)
    generated_files.append(large_file)
    
    # Generate invalid JSON for error testing
    # We'll create valid JSON data but save it with an error
    invalid_data = {"valid": "This is valid JSON data", "but": "saved with an error"}
    invalid_file_path = os.path.join(output_dir, "invalid_sample.json")
    
    with open(invalid_file_path, 'w', encoding='utf-8') as f:
        # Write valid JSON but add a syntax error
        f.write(json.dumps(invalid_data, indent=2)[:-1]) # Omit the closing brace
        f.write("\n  missing_brace: true\n")  # Add invalid JSON syntax
    
    logger.info(f"Saved invalid JSON to {invalid_file_path} for error testing")
    generated_files.append(invalid_file_path)
    
    logger.info(f"Generated {len(generated_files)} test JSON files in {output_dir}")
    return generated_files


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments for the script.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate test JSON files with various structures and complexities"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for generated files (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--num-records", "-n",
        type=int,
        default=DEFAULT_NUM_RECORDS,
        help=f"Base number of records to generate (default: {DEFAULT_NUM_RECORDS})"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["flat", "nested", "array", "complex", "all"],
        default="all",
        help="Type of JSON file to generate (default: all)"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main function that runs the script based on command line arguments.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info(f"Starting test data generation. Output dir: {args.output_dir}, "
                f"Num records: {args.num_records}, Type: {args.type}")
    
    try:
        # Ensure output directory exists
        create_directory_if_not_exists(args.output_dir)
        
        # Generate files based on the requested type
        if args.type == "flat":
            data = generate_flat_json(args.num_records, True)
            file_path = save_json_file(data, "flat_json_sample.json", args.output_dir)
            analyze_and_print_json_info(data, file_path)
        
        elif args.type == "nested":
            data = generate_nested_json(5, 3, True)
            file_path = save_json_file(data, "nested_json_sample.json", args.output_dir)
            analyze_and_print_json_info(data, file_path)
        
        elif args.type == "array":
            data = generate_array_json(5, args.num_records, True)
            file_path = save_json_file(data, "array_objects_sample.json", args.output_dir)
            analyze_and_print_json_info(data, file_path)
        
        elif args.type == "complex":
            data = generate_complex_json(7, 5, 0.4)
            file_path = save_json_file(data, "complex_mixed_sample.json", args.output_dir)
            analyze_and_print_json_info(data, file_path)
        
        else:  # "all"
            generate_all_test_files(args.output_dir, args.num_records)
        
        logger.info("Test data generation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)