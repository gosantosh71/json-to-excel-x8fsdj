"""
Initialization file for the CLI end-to-end tests package that provides common imports, constants, and utility functions
specific to E2E testing of the JSON to Excel Conversion Tool's command-line interface. This file serves as a central
point for E2E test configuration and shared resources.
"""

import os  # v: built-in
import pytest  # v: 7.3.0+
import tempfile  # v: built-in
import subprocess  # v: built-in
import json  # v: built-in
import pandas  # v: 1.5.0+
import sys  # v: built-in

from src.cli.command_runner import run_cli  # src/cli/command_runner.py
from src.cli.tests.fixtures import get_basic_command_options  # src/cli/tests/fixtures/__init__.py
from src.cli.tests.fixtures import get_complex_command_options  # src/cli/tests/fixtures/__init__.py
from src.cli.tests.fixtures import get_conversion_success_data  # src/cli/tests/fixtures/__init__.py

# Define constants for E2E test directories and file paths
E2E_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
CLI_ROOT_DIR = os.path.abspath(os.path.join(E2E_TESTS_DIR, '..', '..', '..'))
PYTHON_EXECUTABLE = sys.executable
CLI_SCRIPT_PATH = os.path.join(CLI_ROOT_DIR, 'json_to_excel.py')


def run_cli_command(args: list) -> subprocess.CompletedProcess:
    """
    Executes a CLI command as a subprocess for E2E testing.

    Args:
        args: List of command-line arguments to pass to the CLI script

    Returns:
        subprocess.CompletedProcess: Result of the subprocess execution, containing return code and output
    """
    # Construct the full command with Python executable and CLI script path
    command = [PYTHON_EXECUTABLE, CLI_SCRIPT_PATH] + args

    # Execute the command using subprocess.run with captured stdout and stderr
    completed_process = subprocess.run(command, capture_output=True, text=True)

    # Return the completed process object with return code and output
    return completed_process


def create_test_json_file(json_data: dict, file_path: str) -> str:
    """
    Creates a JSON file with the given content for E2E testing.

    Args:
        json_data: The dictionary to write as JSON content
        file_path: The path to create the JSON file at

    Returns:
        str: Path to the created JSON file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the JSON data to the file with proper formatting
    with open(file_path, 'w') as f:
        json.dump(json_data, f)

    # Return the path to the created file
    return file_path


def verify_excel_output(excel_path: str, expected_data: dict, check_column_names: bool = True) -> bool:
    """
    Verifies that an Excel file exists and contains the expected data.

    Args:
        excel_path: Path to the Excel file to verify
        expected_data: Dictionary containing the expected data in the Excel file
        check_column_names: Whether to verify column names

    Returns:
        bool: True if verification passes, False otherwise
    """
    # Check if the Excel file exists
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        return False

    # Read the Excel file using pandas
    try:
        df = pandas.read_excel(excel_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    # Verify the data matches the expected content
    for column, expected_value in expected_data.items():
        if column not in df.columns:
            print(f"Error: Column '{column}' not found in Excel file")
            return False
        actual_value = df[column][0]
        if actual_value != expected_value:
            print(f"Error: Value in column '{column}' is '{actual_value}', expected '{expected_value}'")
            return False

    # Optionally verify column names
    if check_column_names:
        expected_columns = list(expected_data.keys())
        actual_columns = list(df.columns)
        if expected_columns != actual_columns:
            print(f"Error: Column names do not match. Expected: {expected_columns}, Actual: {actual_columns}")
            return False

    # Return True if all verifications pass
    return True


@pytest.fixture
def setup_e2e_test_environment():
    """
    Sets up a test environment for E2E testing with temporary directories.

    Returns:
        dict: Dictionary containing paths to test directories and files
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories for input and output files
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        # Return a dictionary with paths to the test environment directories
        test_environment = {
            "temp_dir": temp_dir,
            "input_dir": input_dir,
            "output_dir": output_dir
        }

        # Yield the temporary directory and file paths
        yield test_environment

        # Clean up the temporary directory after the test
        # (Handled automatically by TemporaryDirectory context manager)