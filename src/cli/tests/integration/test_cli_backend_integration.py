"""
Integration tests for verifying the correct integration between the CLI component and backend services
of the JSON to Excel Conversion Tool. This module focuses on testing the interaction between CLI
commands and the backend conversion services, ensuring that data flows correctly between these components.
"""

import os  # v: built-in
import tempfile  # v: built-in
import unittest.mock  # v: built-in
import pytest  # v: 7.3.0+
import json  # v: built-in

from ...models.command_options import CommandOptions, CommandType  # src/cli/models/command_options.py
from ...models.cli_response import CLIResponse, ResponseType  # src/cli/models/cli_response.py
from ...commands.convert_command import execute_convert_command  # src/cli/commands/convert_command.py
from ...command_runner import run_command  # src/cli/command_runner.py
from ....backend.services.conversion_service import ConversionService  # src/backend/services/conversion_service.py
from ....backend.json_parser import JSONParser  # src/backend/json_parser.py
from ..fixtures import cli_fixtures  # src/cli/tests/fixtures/cli_fixtures.py
from ....backend.tests.fixtures import json_fixtures  # src/backend/tests/fixtures/json_fixtures.py
from ....backend.tests.fixtures import excel_fixtures  # src/backend/tests/fixtures/excel_fixtures.py


@pytest.fixture
def setup_test_files():
    """
    Sets up temporary test files for CLI-backend integration tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = os.path.join(tmpdir, "input.json")
        output_file_path = os.path.join(tmpdir, "output.xlsx")
        yield tmpdir, input_file_path, output_file_path


def test_cli_backend_integration_basic(setup_test_files, flat_json):
    """
    Tests basic integration between CLI and backend conversion service.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Write flat JSON test data to the input file
    with open(input_file_path, "w") as f:
        json.dump(flat_json, f)

    # Get basic command options for conversion
    options = cli_fixtures.get_basic_command_options()

    # Update the options with the test file paths
    options.input_file = input_file_path
    options.output_file = output_file_path

    # Execute the convert command using run_command
    cli_response = run_command(options)

    # Verify the command execution was successful
    assert cli_response.response_type == ResponseType.SUCCESS
    assert os.path.exists(output_file_path)

    # Verify the response contains appropriate summary information
    assert "input_file" in cli_response.data
    assert "output_file" in cli_response.data


def test_cli_backend_integration_complex(setup_test_files, nested_json):
    """
    Tests integration with complex JSON structures between CLI and backend.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Write nested JSON test data to the input file
    with open(input_file_path, "w") as f:
        json.dump(nested_json, f)

    # Get complex command options for conversion
    options = cli_fixtures.get_complex_command_options()

    # Update the options with the test file paths
    options.input_file = input_file_path
    options.output_file = output_file_path

    # Execute the convert command using run_command
    cli_response = run_command(options)

    # Verify the command execution was successful
    assert cli_response.response_type == ResponseType.SUCCESS
    assert os.path.exists(output_file_path)

    # Verify the response contains appropriate summary information
    assert "input_file" in cli_response.data
    assert "output_file" in cli_response.data

    # Verify complex options were correctly applied to the output
    # Add specific assertions related to complex options here


def test_cli_backend_error_propagation(setup_test_files):
    """
    Tests that errors from backend components are properly propagated to CLI responses.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Create a non-existent input file path
    non_existent_file = os.path.join(tmpdir, "non_existent.json")

    # Get basic command options for conversion
    options = cli_fixtures.get_basic_command_options()

    # Update the options with the non-existent input file path
    options.input_file = non_existent_file
    options.output_file = output_file_path

    # Execute the convert command using run_command
    cli_response = run_command(options)

    # Verify the command execution failed with appropriate error
    assert cli_response.response_type == ResponseType.ERROR
    assert "File not found" in cli_response.message

    # Verify the error response contains file not found information
    assert cli_response.error.error_code == "FILE_NOT_FOUND"
    assert cli_response.error.context["file_path"] == non_existent_file

    # Create an invalid JSON file with syntax errors
    invalid_json_file = os.path.join(tmpdir, "invalid.json")
    with open(invalid_json_file, "w") as f:
        f.write('{"name": "Test", "value": 123, "missing": }')

    # Update the options with the invalid JSON file path
    options.input_file = invalid_json_file

    # Execute the convert command using run_command
    cli_response = run_command(options)

    # Verify the command execution failed with JSON parsing error
    assert cli_response.response_type == ResponseType.ERROR
    assert "Invalid JSON format" in cli_response.message

    # Verify the error response contains JSON syntax error information
    assert cli_response.error.error_code == "JSON_PARSE_ERROR"
    assert "line" in cli_response.error.context
    assert "column" in cli_response.error.context


def test_cli_backend_integration_with_mocks(setup_test_files):
    """
    Tests CLI-backend integration using mocked backend components.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Create mock objects for ConversionService and JSONParser
    mock_conversion_service = unittest.mock.Mock(spec=ConversionService)
    mock_json_parser = unittest.mock.Mock(spec=JSONParser)

    # Configure the mocks to return expected values
    mock_conversion_service.convert_json_to_excel.return_value = (True, {"status": "success"}, None)
    mock_json_parser.parse_string.return_value = ({"key": "value"}, None)

    # Patch the backend components with the mocks
    with unittest.mock.patch('src.cli.commands.convert_command.ConversionService', return_value=mock_conversion_service), \
         unittest.mock.patch('src.backend.json_parser.JSONParser', return_value=mock_json_parser):

        # Get basic command options for testing
        options = cli_fixtures.get_basic_command_options()

        # Update the options with the test file paths
        options.input_file = input_file_path
        options.output_file = output_file_path

        # Execute the convert command with the mocked backend
        cli_response = run_command(options)

        # Verify the mocks were called with the expected parameters
        mock_conversion_service.convert_json_to_excel.assert_called_once()
        #mock_json_parser.parse_string.assert_called_once()

        # Verify the command execution produced the expected result
        assert cli_response.response_type == ResponseType.SUCCESS
        assert "Successfully converted" in cli_response.message

        # Verify the CLI correctly processed the backend response
        assert cli_response.data["status"] == "success"


def test_cli_backend_performance_metrics(setup_test_files, flat_json):
    """
    Tests that performance metrics from backend are correctly included in CLI responses.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Write flat JSON test data to the input file
    with open(input_file_path, "w") as f:
        json.dump(flat_json, f)

    # Get basic command options with verbose flag enabled
    options = cli_fixtures.get_basic_command_options()
    options.verbose = True

    # Update the options with the test file paths
    options.input_file = input_file_path
    options.output_file = output_file_path

    # Execute the convert command using run_command
    cli_response = run_command(options)

    # Verify the command execution was successful
    assert cli_response.response_type == ResponseType.SUCCESS

    # Extract performance metrics from the response
    performance_metrics = cli_response.data.get("performance", {})

    # Verify that execution time is included in the metrics
    assert "execution_time_seconds" in performance_metrics

    # Verify that file size information is included in the metrics
    assert "input" in cli_response.data
    assert "size_bytes" in cli_response.data["input"]

    # Verify that JSON structure information is included in the metrics
    assert "structure" in cli_response.data["input"]
    assert "nesting_level" in cli_response.data["input"]["structure"]


def test_cli_backend_option_propagation(setup_test_files, nested_json):
    """
    Tests that CLI options are correctly propagated to backend services.
    """
    tmpdir, input_file_path, output_file_path = setup_test_files

    # Write nested JSON test data to the input file
    with open(input_file_path, "w") as f:
        json.dump(nested_json, f)

    # Create mock for ConversionService
    mock_conversion_service = unittest.mock.Mock(spec=ConversionService)
    mock_conversion_service.convert_json_to_excel.return_value = (True, {"status": "success"}, None)

    # Patch the backend ConversionService with the mock
    with unittest.mock.patch('src.cli.commands.convert_command.ConversionService', return_value=mock_conversion_service):

        # Get command options with specific array handling and sheet name
        options = cli_fixtures.get_basic_command_options()
        options.array_handling = "join"
        options.sheet_name = "TestData"

        # Update the options with the test file paths
        options.input_file = input_file_path
        options.output_file = output_file_path

        # Execute the convert command with the mocked backend
        cli_response = run_command(options)

        # Verify the mock was called with the correct excel_options
        mock_conversion_service.convert_json_to_excel.assert_called_once()
        call_args = mock_conversion_service.convert_json_to_excel.call_args
        excel_options = call_args[0][2]  # Access the excel_options argument

        # Verify that array_handling option was correctly passed
        assert excel_options["array_handling"] == "join"

        # Verify that sheet_name option was correctly passed
        assert excel_options["sheet_name"] == "TestData"