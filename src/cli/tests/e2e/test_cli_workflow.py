"""
End-to-end tests for the JSON to Excel Conversion Tool's CLI workflow.
This module verifies the complete functionality of the CLI component by testing
real command execution with actual file processing, ensuring that the entire
conversion pipeline works correctly from user input to Excel output.
"""

import pytest  # v: 7.3.0+
import os  # v: built-in
import tempfile  # v: built-in
import subprocess  # v: built-in
import json  # v: built-in
import pandas  # v: 1.5.0+

from src.cli.command_runner import run_cli  # src/cli/command_runner.py
from src.cli.tests.fixtures import cli_fixtures  # src/cli/tests/fixtures/cli_fixtures.py
from src.backend.tests.fixtures import json_fixtures  # src/backend/tests/fixtures/json_fixtures.py
from src.backend.tests.fixtures import excel_fixtures  # src/backend/tests/fixtures/excel_fixtures.py


@pytest.fixture
def setup_test_environment():
    """
    Sets up a temporary test environment with sample files for CLI workflow testing.

    Returns:
        tuple: A tuple containing temporary directory path, input file paths, and output file paths
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories for input and output files
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        # Create paths for sample JSON files and output Excel files
        input_file = os.path.join(input_dir, "sample.json")
        output_file = os.path.join(output_dir, "output.xlsx")

        # Yield the temporary directory and file paths
        yield temp_dir, input_file, output_file

        # Clean up temporary files after test completion
        # (Handled automatically by TemporaryDirectory context manager)


def create_sample_files(temp_dir, json_data, filename):
    """
    Creates sample JSON files in the test environment.

    Args:
        temp_dir (str): The path to the temporary directory
        json_data (dict): The JSON data to write to the file
        filename (str): The name of the JSON file to create

    Returns:
        str: Path to the created JSON file
    """
    # Construct the full file path within the temporary directory
    file_path = os.path.join(temp_dir, filename)

    # Write the JSON data to the file with proper formatting
    with open(file_path, "w") as f:
        json.dump(json_data, f)

    return file_path


def test_basic_conversion_workflow(setup_test_environment, flat_json):
    """
    Tests the basic JSON to Excel conversion workflow using the CLI.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        flat_json (dict): Fixture providing a flat JSON structure

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample flat JSON file in the test environment
    create_sample_files(temp_dir, flat_json, "sample.json")

    # Construct the CLI command for basic conversion
    command = ["python", "json_to_excel.py", input_file, output_file]

    # Execute the CLI command using subprocess.run()
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the output Excel file exists
    assert os.path.exists(output_file)

    # Read the Excel file and validate its content
    df = pandas.read_excel(output_file)

    # Verify the Excel file contains the expected data from the JSON
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "John Doe"


def test_complex_conversion_workflow(setup_test_environment, nested_json):
    """
    Tests the conversion workflow with complex nested JSON structures.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        nested_json (dict): Fixture providing a nested JSON structure

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample nested JSON file in the test environment
    create_sample_files(temp_dir, nested_json, "sample.json")

    # Construct the CLI command for conversion with custom options
    command = ["python", "json_to_excel.py", input_file, output_file, "--sheet-name", "Data"]

    # Execute the CLI command using subprocess.run()
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the output Excel file exists
    assert os.path.exists(output_file)

    # Read the Excel file and validate its content
    df = pandas.read_excel(output_file)

    # Verify the Excel file contains the expected flattened nested structure
    assert "name" in df.columns
    assert "contact.email" in df.columns
    assert df.iloc[0]["name"] == "John Doe"

    # Verify column names use dot notation for nested paths
    assert "contact.address.city" in df.columns


def test_array_handling_workflow(setup_test_environment, array_json):
    """
    Tests the conversion workflow with JSON containing arrays using different array handling options.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        array_json (dict): Fixture providing a JSON structure with arrays

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample JSON file with arrays in the test environment
    create_sample_files(temp_dir, array_json, "sample.json")

    # Construct the CLI command with array-handling=expand option
    command_expand = ["python", "json_to_excel.py", input_file, output_file, "--array-handling", "expand"]

    # Execute the CLI command using subprocess.run()
    result_expand = subprocess.run(command_expand, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result_expand.returncode == 0

    # Verify the output Excel file exists
    assert os.path.exists(output_file)

    # Validate that arrays were expanded into multiple rows
    df_expand = pandas.read_excel(output_file)
    assert len(df_expand) > 1
    assert "name" in df_expand.columns
    assert "tags" not in df_expand.columns

    # Construct another CLI command with array-handling=join option
    output_file_join = os.path.join(temp_dir, "output_join.xlsx")
    command_join = ["python", "json_to_excel.py", input_file, output_file_join, "--array-handling", "join"]

    # Execute the second CLI command using subprocess.run()
    result_join = subprocess.run(command_join, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result_join.returncode == 0

    # Verify the second output Excel file exists
    assert os.path.exists(output_file_join)

    # Validate that arrays were joined as comma-separated values
    df_join = pandas.read_excel(output_file_join)
    assert len(df_join) == 1
    assert "name" in df_join.columns
    assert "tags" in df_join.columns
    assert isinstance(df_join["tags"][0], str)


def test_error_handling_workflow(setup_test_environment):
    """
    Tests the CLI's error handling for various error scenarios.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Test file not found scenario:
    # Construct CLI command with non-existent input file
    command_not_found = ["python", "json_to_excel.py", "non_existent_file.json", output_file]

    # Execute the command using subprocess.run()
    result_not_found = subprocess.run(command_not_found, capture_output=True, text=True)

    # Verify the command failed (non-zero return code)
    assert result_not_found.returncode != 0

    # Verify the error output contains 'File not found' message
    assert "File not found" in result_not_found.stderr

    # Test invalid JSON scenario:
    # Create a file with invalid JSON syntax
    invalid_json_file = os.path.join(temp_dir, "invalid.json")
    with open(invalid_json_file, "w") as f:
        f.write('{"name": "Test", value: 123}')  # Missing quotes

    # Construct CLI command with the invalid JSON file
    command_invalid_json = ["python", "json_to_excel.py", invalid_json_file, output_file]

    # Execute the command using subprocess.run()
    result_invalid_json = subprocess.run(command_invalid_json, capture_output=True, text=True)

    # Verify the command failed (non-zero return code)
    assert result_invalid_json.returncode != 0

    # Verify the error output contains 'Invalid JSON format' message
    assert "Invalid JSON format" in result_invalid_json.stderr

    # Test invalid arguments scenario:
    # Construct CLI command with missing required arguments
    command_invalid_args = ["python", "json_to_excel.py"]  # Missing input and output files

    # Execute the command using subprocess.run()
    result_invalid_args = subprocess.run(command_invalid_args, capture_output=True, text=True)

    # Verify the command failed (non-zero return code)
    assert result_invalid_args.returncode != 0

    # Verify the error output contains usage information
    assert "usage:" in result_invalid_args.stderr


def test_verbose_output_workflow(setup_test_environment, flat_json):
    """
    Tests the CLI's verbose output mode with detailed progress information.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        flat_json (dict): Fixture providing a flat JSON structure

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample JSON file in the test environment
    create_sample_files(temp_dir, flat_json, "sample.json")

    # Construct the CLI command with --verbose flag
    command = ["python", "json_to_excel.py", input_file, output_file, "--verbose"]

    # Execute the CLI command using subprocess.run() with stdout capture
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the output Excel file exists
    assert os.path.exists(output_file)

    # Verify the stdout contains detailed progress information
    assert "[i] Starting conversion process..." in result.stdout
    assert "[i] Reading JSON file:" in result.stdout

    # Verify the stdout contains file size information
    assert "[i] JSON file size:" in result.stdout

    # Verify the stdout contains processing time information
    assert "[i] Conversion completed successfully in" in result.stdout

    # Verify the stdout contains structure information
    assert "[i] Created 1 worksheet with" in result.stdout


def test_help_command_workflow():
    """
    Tests the CLI's help command functionality.

    Args:
        None

    Returns:
        None: Test assertion results
    """
    # Construct the CLI command with --help flag
    command = ["python", "json_to_excel.py", "--help"]

    # Execute the CLI command using subprocess.run() with stdout capture
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the stdout contains usage information
    assert "usage:" in result.stdout

    # Verify the stdout contains argument descriptions
    assert "arguments:" in result.stdout

    # Verify the stdout contains examples section
    assert "examples:" in result.stdout


def test_info_command_workflow(setup_test_environment, nested_json):
    """
    Tests the CLI's info command functionality for displaying JSON file information.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        nested_json (dict): Fixture providing a nested JSON file

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample nested JSON file in the test environment
    create_sample_files(temp_dir, nested_json, "sample.json")

    # Construct the CLI command with info subcommand
    command = ["python", "json_to_excel.py", "info", input_file]

    # Execute the CLI command using subprocess.run() with stdout capture
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the stdout contains file information
    assert "File Information:" in result.stdout

    # Verify the stdout contains structure analysis
    assert "Structure Analysis:" in result.stdout

    # Verify the stdout contains nesting information
    assert "Nesting Level:" in result.stdout

    # Test info command with different output format (json)
    command_json = ["python", "json_to_excel.py", "info", input_file, "--format=json"]

    # Construct the CLI command with info subcommand and --format=json
    result_json = subprocess.run(command_json, capture_output=True, text=True)

    # Execute the CLI command using subprocess.run() with stdout capture
    assert result_json.returncode == 0

    # Verify the command executed successfully (return code 0)
    assert result_json.returncode == 0

    # Verify the stdout contains valid JSON
    try:
        json.loads(result_json.stdout)
    except json.JSONDecodeError:
        assert False, "Output is not valid JSON"

    # Parse the JSON output and verify it contains the expected information
    json_output = json.loads(result_json.stdout)
    assert "file_info" in json_output
    assert "structure_info" in json_output


def test_validate_command_workflow(setup_test_environment, flat_json):
    """
    Tests the CLI's validate command functionality for validating JSON files.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        flat_json (dict): Fixture providing a flat JSON file

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample valid JSON file in the test environment
    create_sample_files(temp_dir, flat_json, "sample.json")

    # Construct the CLI command with validate subcommand
    command = ["python", "json_to_excel.py", "validate", input_file]

    # Execute the CLI command using subprocess.run() with stdout capture
    result = subprocess.run(command, capture_output=True, text=True)

    # Verify the command executed successfully (return code 0)
    assert result.returncode == 0

    # Verify the stdout contains validation success message
    assert "JSON file is valid" in result.stdout

    # Create an invalid JSON file in the test environment
    invalid_json_file = os.path.join(temp_dir, "invalid.json")
    with open(invalid_json_file, "w") as f:
        f.write('{"name": "Test", value: 123}')  # Missing quotes

    # Construct the CLI command with validate subcommand for the invalid file
    command_invalid = ["python", "json_to_excel.py", "validate", invalid_json_file]

    # Execute the CLI command using subprocess.run() with stdout capture
    result_invalid = subprocess.run(command_invalid, capture_output=True, text=True)

    # Verify the command failed (non-zero return code)
    assert result_invalid.returncode != 0

    # Verify the stdout contains validation failure message with details
    assert "Failed to validate JSON file" in result_invalid.stderr


def test_programmatic_api_workflow(setup_test_environment, flat_json):
    """
    Tests the CLI's programmatic API usage through direct function calls.

    Args:
        setup_test_environment (tuple): Fixture providing temporary directory and file paths
        flat_json (dict): Fixture providing a flat JSON file

    Returns:
        None: Test assertion results
    """
    # Get temporary directory and file paths from setup
    temp_dir, input_file, output_file = setup_test_environment

    # Create a sample JSON file in the test environment
    create_sample_files(temp_dir, flat_json, "sample.json")

    # Construct command-line arguments as a list
    args = ["convert", input_file, output_file]

    # Call run_cli() directly with the arguments
    exit_code = run_cli(args)

    # Verify the function returned exit code 0
    assert exit_code == 0

    # Verify the output Excel file exists
    assert os.path.exists(output_file)

    # Read the Excel file and validate its content
    df = pandas.read_excel(output_file)
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "John Doe"