"""
Integration tests for the command execution functionality of the JSON to Excel Conversion Tool CLI.
This module tests the command runner and command execution flow, ensuring that commands are properly
executed, arguments are correctly processed, and appropriate responses are returned.
"""

import os  # v: built-in
import tempfile  # v: built-in
import unittest.mock  # v: built-in
import pytest  # v: 7.3.0+
import io  # v: built-in
import sys  # v: built-in

from src.cli.models.command_options import CommandOptions, CommandType  # ./models/command_options
from src.cli.models.cli_response import CLIResponse, ResponseType  # ./models/cli_response
from src.cli.command_runner import run_command, cli_main, handle_unexpected_error  # ./command_runner
from src.cli.argument_parser import parse_args  # ./argument_parser
from src.cli.tests.fixtures import cli_fixtures  # ../fixtures/cli_fixtures
from src.cli.commands.convert_command import execute_convert_command  # ./commands/convert_command
from src.cli.commands.validate_command import execute_validate_command  # ./commands/validate_command
from src.cli.commands.info_command import execute_info_command  # ./commands/info_command
from src.cli.commands.help_command import execute_help_command  # ./commands/help_command


@pytest.fixture
def setup_test_files():
    """Sets up temporary test files for command execution tests."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define input and output file paths
        input_file = os.path.join(tmpdir, "test_input.json")
        output_file = os.path.join(tmpdir, "test_output.xlsx")

        # Yield the paths for use in tests
        yield tmpdir, input_file, output_file

        # Cleanup is handled automatically by TemporaryDirectory


def test_run_command_convert(setup_test_files):
    """Tests that the run_command function correctly executes the convert command."""
    # Extract setup variables
    tmpdir, input_file, output_file = setup_test_files

    # Create a sample JSON file
    with open(input_file, "w") as f:
        f.write('{"name": "test", "value": 123}')

    # Get basic command options for conversion
    options = cli_fixtures.get_basic_command_options()

    # Update the options with the test file paths
    options.input_file = input_file
    options.output_file = output_file
    options.command = CommandType.CONVERT

    # Execute run_command with the options
    response = run_command(options)

    # Verify the command execution was successful
    assert response.response_type == ResponseType.SUCCESS
    assert "Successfully converted" in response.message

    # Verify the output Excel file exists
    assert os.path.exists(output_file)


def test_run_command_validate(setup_test_files):
    """Tests that the run_command function correctly executes the validate command."""
    # Extract setup variables
    tmpdir, input_file, _ = setup_test_files

    # Create a sample JSON file
    with open(input_file, "w") as f:
        f.write('{"name": "test", "value": 123}')

    # Create command options for validation
    options = cli_fixtures.get_basic_command_options()
    options.input_file = input_file
    options.command = CommandType.VALIDATE

    # Execute run_command with the options
    response = run_command(options)

    # Verify the command execution was successful
    assert response.response_type == ResponseType.SUCCESS
    assert "JSON file is valid" in response.message


def test_run_command_info(setup_test_files):
    """Tests that the run_command function correctly executes the info command."""
    # Extract setup variables
    tmpdir, input_file, _ = setup_test_files

    # Create a sample JSON file
    with open(input_file, "w") as f:
        f.write('{"name": "test", "value": 123}')

    # Create command options for info command
    options = cli_fixtures.get_basic_command_options()
    options.input_file = input_file
    options.command = CommandType.INFO

    # Execute run_command with the options
    response = run_command(options)

    # Verify the command execution was successful
    assert response.response_type == ResponseType.SUCCESS
    assert "Successfully analyzed JSON file" in response.message


def test_run_command_help():
    """Tests that the run_command function correctly executes the help command."""
    # Create command options for help command
    options = cli_fixtures.get_basic_command_options()
    options.command = CommandType.HELP

    # Execute run_command with the options
    response = run_command(options)

    # Verify the command execution was successful
    assert response.response_type == ResponseType.INFO
    assert "JSON to Excel Conversion Tool" in response.message


def test_run_command_invalid_options():
    """Tests that the run_command function correctly handles invalid command options."""
    # Get invalid command options from fixtures
    options = cli_fixtures.get_invalid_command_options()

    # Execute run_command with the invalid options
    response = run_command(options)

    # Verify the command execution failed with appropriate error
    assert response.response_type == ResponseType.ERROR
    assert "Input file is required for convert command" in response.message

    # Verify the response contains validation error information
    assert response.error is not None
    assert response.error.message == "Input file is required for convert command"

    # Verify the exit code is non-zero
    assert response.get_exit_code() != 0


def test_run_command_with_mocks():
    """Tests the run_command function with mocked command handlers."""
    # Create mock objects for each command handler function
    mock_convert = unittest.mock.MagicMock(return_value=CLIResponse(response_type=ResponseType.SUCCESS, message="Convert mock"))
    mock_validate = unittest.mock.MagicMock(return_value=CLIResponse(response_type=ResponseType.SUCCESS, message="Validate mock"))
    mock_info = unittest.mock.MagicMock(return_value=CLIResponse(response_type=ResponseType.SUCCESS, message="Info mock"))
    mock_help = unittest.mock.MagicMock(return_value=CLIResponse(response_type=ResponseType.SUCCESS, message="Help mock"))

    # Patch the command handler functions with the mocks
    with unittest.mock.patch("src.cli.command_runner.execute_convert_command", mock_convert), \
            unittest.mock.patch("src.cli.command_runner.execute_validate_command", mock_validate), \
            unittest.mock.patch("src.cli.command_runner.execute_info_command", mock_info), \
            unittest.mock.patch("src.cli.command_runner.execute_help_command", mock_help):

        # Create command options for each command type
        convert_options = cli_fixtures.get_basic_command_options()
        convert_options.command = CommandType.CONVERT
        validate_options = cli_fixtures.get_basic_command_options()
        validate_options.command = CommandType.VALIDATE
        info_options = cli_fixtures.get_basic_command_options()
        info_options.command = CommandType.INFO
        help_options = cli_fixtures.get_basic_command_options()
        help_options.command = CommandType.HELP

        # Execute run_command with each command type
        convert_response = run_command(convert_options)
        validate_response = run_command(validate_options)
        info_response = run_command(info_options)
        help_response = run_command(help_options)

        # Verify each mock was called with the correct options
        mock_convert.assert_called_once_with(convert_options)
        mock_validate.assert_called_once_with(validate_options)
        mock_info.assert_called_once_with(info_options)
        mock_help.assert_called_once_with(help_options)

        # Verify run_command returned the expected responses
        assert convert_response.message == "Convert mock"
        assert validate_response.message == "Validate mock"
        assert info_response.message == "Info mock"
        assert help_response.message == "Help mock"


def test_run_cli_argument_parsing(setup_test_files):
    """Tests that the run_cli function correctly parses command line arguments."""
    # Extract setup variables
    tmpdir, input_file, output_file = setup_test_files

    # Create a sample JSON file
    with open(input_file, "w") as f:
        f.write('{"name": "test", "value": 123}')

    # Create command line arguments array for conversion
    args = ["convert", input_file, output_file]

    # Mock stdout to capture output
    with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        # Execute run_cli with the arguments
        exit_code = cli_main(args)

        # Verify the function returned the expected exit code
        assert exit_code == 0

        # Verify the captured output contains success message
        assert "Successfully converted" in mock_stdout.getvalue()

        # Verify the output Excel file exists
        assert os.path.exists(output_file)


def test_run_cli_error_handling():
    """Tests that the run_cli function correctly handles errors during execution."""
    # Create invalid command line arguments
    args = ["invalid_command"]

    # Mock stdout and stderr to capture output
    with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout, \
            unittest.mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:

        # Execute run_cli with the invalid arguments
        exit_code = cli_main(args)

        # Verify the function returned a non-zero exit code
        assert exit_code != 0

        # Verify the captured error output contains appropriate error message
        assert "Error: unrecognized arguments: invalid_command" in mock_stderr.getvalue()


def test_command_execution_flow(setup_test_files):
    """Tests the complete command execution flow from argument parsing to command execution."""
    # Extract setup variables
    tmpdir, input_file, output_file = setup_test_files

    # Create a sample JSON file
    with open(input_file, "w") as f:
        f.write('{"name": "test", "value": 123}')

    # Create command line arguments array for conversion
    args = ["convert", input_file, output_file]

    # Mock the parse_args function to verify it's called
    with unittest.mock.patch("src.cli.command_runner.argument_parser.parse_args") as mock_parse_args, \
            unittest.mock.patch("src.cli.command_runner.run_command") as mock_run_command:

        # Set up mock return values
        mock_options = cli_fixtures.get_basic_command_options()
        mock_options.input_file = input_file
        mock_options.output_file = output_file
        mock_parse_args.return_value = (mock_options, None)  # Simulate successful parsing

        mock_run_command.return_value = CLIResponse(response_type=ResponseType.SUCCESS, message="Conversion successful")

        # Execute run_cli with the arguments
        exit_code = cli_main(args)

        # Verify parse_args was called with the correct arguments
        mock_parse_args.assert_called_once_with(args)

        # Verify run_command was called with the options from parse_args
        mock_run_command.assert_called_once_with(mock_options)

        # Verify the function returned the expected exit code
        assert exit_code == 0


def test_command_execution_exception_handling():
    """Tests that exceptions during command execution are properly caught and handled."""
    # Create command options for testing
    options = cli_fixtures.get_basic_command_options()
    options.command = CommandType.CONVERT

    # Mock run_command to raise an exception
    with unittest.mock.patch("src.cli.command_runner.run_command") as mock_run_command, \
            unittest.mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:

        mock_run_command.side_effect = Exception("Simulated error")

        # Execute run_cli with arguments that will trigger the exception
        exit_code = cli_main(["convert", "input.json", "output.xlsx"])

        # Verify the function caught the exception and returned error exit code
        assert exit_code == 1

        # Verify the error was logged to stderr
        assert "An unexpected error occurred: Simulated error" in mock_stderr.getvalue()