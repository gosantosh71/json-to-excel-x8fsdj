"""
Unit tests for the command runner component of the JSON to Excel Conversion Tool.
This file contains test cases to verify the correct execution of CLI commands,
error handling, and integration with the argument parser and command implementations.
"""

import pytest  # v: 7.3.0+
import unittest.mock  # v: built-in
import io  # v: built-in
import sys  # v: built-in

from src.cli.command_runner import run_command, run_cli  # src/cli/command_runner.py
from src.cli.models.command_options import CommandOptions, CommandType  # src/cli/models/command_options.py
from src.cli.models.cli_response import CLIResponse, ResponseType  # src/cli/models/cli_response.py
from src.cli.tests.fixtures.cli_fixtures import get_basic_command_options, get_complex_command_options, get_invalid_command_options, get_success_response, get_error_response, get_validation_error, get_file_not_found_error, get_conversion_success_data  # src/cli/tests/fixtures/cli_fixtures.py
from src.cli.commands.convert_command import execute_convert_command  # src/cli/commands/convert_command.py
from src.cli.commands.validate_command import execute_validate_command  # src/cli/commands/validate_command.py
from src.cli.commands.info_command import execute_info_command  # src/cli/commands/info_command.py
from src.cli.commands.help_command import execute_help_command  # src/cli/commands/help_command.py
from src.cli.argument_parser import parse_arguments  # src/cli/argument_parser.py


@pytest.mark.parametrize('command_options', [get_basic_command_options(), get_complex_command_options()])
def test_run_command_convert_success(command_options):
    """
    Tests that the run_command function correctly executes the convert command and returns a success response.
    """
    # Create a mock for execute_convert_command that returns a success response
    mock_execute_convert_command = unittest.mock.MagicMock(return_value=get_success_response("Conversion successful", get_conversion_success_data()))

    # Patch the execute_convert_command import in command_runner module
    with unittest.mock.patch('src.cli.command_runner.execute_convert_command', mock_execute_convert_command):
        # Call run_command with the parameterized command options
        response = run_command(command_options)

        # Assert that execute_convert_command was called once with the command options
        mock_execute_convert_command.assert_called_once_with(command_options)

        # Assert that the returned response is the expected success response
        assert response.message == "Conversion successful"
        assert response.data == get_conversion_success_data()

        # Assert that the response type is SUCCESS
        assert response.response_type == ResponseType.SUCCESS


def test_run_command_convert_error():
    """
    Tests that the run_command function correctly handles errors during convert command execution.
    """
    # Create a mock for execute_convert_command that returns an error response
    mock_execute_convert_command = unittest.mock.MagicMock(return_value=get_error_response("Conversion failed", get_validation_error("Invalid input file")))

    # Patch the execute_convert_command import in command_runner module
    with unittest.mock.patch('src.cli.command_runner.execute_convert_command', mock_execute_convert_command):
        # Call run_command with basic command options
        options = get_basic_command_options()
        response = run_command(options)

        # Assert that execute_convert_command was called once with the command options
        mock_execute_convert_command.assert_called_once_with(options)

        # Assert that the returned response is the expected error response
        assert response.message == "Conversion failed"
        assert response.error.message == "Invalid input file"

        # Assert that the response type is ERROR
        assert response.response_type == ResponseType.ERROR


def test_run_command_validate_success():
    """
    Tests that the run_command function correctly executes the validate command and returns a success response.
    """
    # Create command options for the validate command
    options = CommandOptions(command=CommandType.VALIDATE, input_file="test.json")

    # Create a mock for execute_validate_command that returns a success response
    mock_execute_validate_command = unittest.mock.MagicMock(return_value=get_success_response("Validation successful", {}))

    # Patch the execute_validate_command import in command_runner module
    with unittest.mock.patch('src.cli.command_runner.execute_validate_command', mock_execute_validate_command):
        # Call run_command with the validate command options
        response = run_command(options)

        # Assert that execute_validate_command was called once with the command options
        mock_execute_validate_command.assert_called_once_with(options)

        # Assert that the returned response is the expected success response
        assert response.message == "Validation successful"
        assert response.data == {}

        # Assert that the response type is SUCCESS
        assert response.response_type == ResponseType.SUCCESS


def test_run_command_info_success():
    """
    Tests that the run_command function correctly executes the info command and returns a success response.
    """
    # Create command options for the info command
    options = CommandOptions(command=CommandType.INFO, input_file="test.json")

    # Create a mock for execute_info_command that returns a success response
    mock_execute_info_command = unittest.mock.MagicMock(return_value=get_success_response("Info retrieved", {}))

    # Patch the execute_info_command import in command_runner module
    with unittest.mock.patch('src.cli.command_runner.execute_info_command', mock_execute_info_command):
        # Call run_command with the info command options
        response = run_command(options)

        # Assert that execute_info_command was called once with the command options
        mock_execute_info_command.assert_called_once_with(options)

        # Assert that the returned response is the expected success response
        assert response.message == "Info retrieved"
        assert response.data == {}

        # Assert that the response type is INFO
        assert response.response_type == ResponseType.SUCCESS


def test_run_command_help_success():
    """
    Tests that the run_command function correctly executes the help command and returns a success response.
    """
    # Create command options for the help command
    options = CommandOptions(command=CommandType.HELP)

    # Create a mock for execute_help_command that returns a success response
    mock_execute_help_command = unittest.mock.MagicMock(return_value=get_success_response("Help displayed", {}))

    # Patch the execute_help_command import in command_runner module
    with unittest.mock.patch('src.cli.command_runner.execute_help_command', mock_execute_help_command):
        # Call run_command with the help command options
        response = run_command(options)

        # Assert that execute_help_command was called once with the command options
        mock_execute_help_command.assert_called_once_with(options)

        # Assert that the returned response is the expected success response
        assert response.message == "Help displayed"
        assert response.data == {}

        # Assert that the response type is INFO
        assert response.response_type == ResponseType.SUCCESS


def test_run_command_invalid_command():
    """
    Tests that the run_command function correctly handles invalid command types.
    """
    # Create command options with an invalid command type
    options = CommandOptions(command="INVALID")

    # Call run_command with the invalid command options
    response = run_command(options)

    # Assert that the returned response has ERROR type
    assert response.response_type == ResponseType.ERROR

    # Assert that the error message mentions invalid command
    assert "Unknown command" in response.message


def test_run_command_validation_failure():
    """
    Tests that the run_command function correctly handles command options validation failures.
    """
    # Create invalid command options that will fail validation
    options = get_invalid_command_options()

    # Mock the validate method to return False and set an error
    mock_validate = unittest.mock.MagicMock(return_value=False)
    options.validate = mock_validate

    # Call run_command with the invalid command options
    response = run_command(options)

    # Assert that the returned response has ERROR type
    assert response.response_type == ResponseType.ERROR

    # Assert that the error message contains the validation error
    assert "Input file is required" in response.message


def test_run_cli_success():
    """
    Tests that the run_cli function correctly parses arguments, executes the command, and returns the appropriate exit code for successful execution.
    """
    # Create test command-line arguments
    test_args = ["convert", "input.json", "output.xlsx"]

    # Create a mock for parse_arguments that returns command options
    mock_parse_arguments = unittest.mock.MagicMock(return_value=(get_basic_command_options(), None))

    # Create a mock for run_command that returns a success response
    mock_run_command = unittest.mock.MagicMock(return_value=get_success_response("Conversion successful", {}))

    # Patch stdout to capture output
    with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        # Patch parse_arguments and run_command
        with unittest.mock.patch('src.cli.command_runner.parse_arguments', mock_parse_arguments):
            with unittest.mock.patch('src.cli.command_runner.run_command', mock_run_command):
                # Call run_cli with the test arguments
                exit_code = run_cli(test_args)

                # Assert that parse_arguments was called once with the arguments
                mock_parse_arguments.assert_called_once_with(test_args)

                # Assert that run_command was called once with the command options
                mock_run_command.assert_called_once_with(get_basic_command_options())

                # Assert that the success message was printed to stdout
                assert "Conversion successful" in mock_stdout.getvalue()

                # Assert that the function returned exit code 0
                assert exit_code == 0


def test_run_cli_error():
    """
    Tests that the run_cli function correctly handles errors and returns the appropriate exit code for failed execution.
    """
    # Create test command-line arguments
    test_args = ["convert", "input.json", "output.xlsx"]

    # Create a mock for parse_arguments that returns command options
    mock_parse_arguments = unittest.mock.MagicMock(return_value=(get_basic_command_options(), None))

    # Create a mock for run_command that returns an error response
    mock_run_command = unittest.mock.MagicMock(return_value=get_error_response("Conversion failed", get_validation_error("Invalid input file")))

    # Patch stdout to capture output
    with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        # Patch parse_arguments and run_command
        with unittest.mock.patch('src.cli.command_runner.parse_arguments', mock_parse_arguments):
            with unittest.mock.patch('src.cli.command_runner.run_command', mock_run_command):
                # Call run_cli with the test arguments
                exit_code = run_cli(test_args)

                # Assert that parse_arguments was called once with the arguments
                mock_parse_arguments.assert_called_once_with(test_args)

                # Assert that run_command was called once with the command options
                mock_run_command.assert_called_once_with(get_basic_command_options())

                # Assert that the error message was printed to stdout
                assert "Conversion failed" in mock_stdout.getvalue()

                # Assert that the function returned exit code 1
                assert exit_code == 1


def test_run_cli_argument_parsing_error():
    """
    Tests that the run_cli function correctly handles argument parsing errors.
    """
    # Create test command-line arguments
    test_args = ["convert", "input.json"]

    # Create a mock for parse_arguments that raises an exception
    mock_parse_arguments = unittest.mock.MagicMock(side_effect=Exception("Missing required arguments"))

    # Patch stderr to capture error output
    with unittest.mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
        # Patch parse_arguments
        with unittest.mock.patch('src.cli.command_runner.parse_arguments', mock_parse_arguments):
            # Call run_cli with the test arguments
            exit_code = run_cli(test_args)

            # Assert that parse_arguments was called once with the arguments
            mock_parse_arguments.assert_called_once_with(test_args)

            # Assert that an error message was printed to stderr
            assert "Missing required arguments" in mock_stderr.getvalue()

            # Assert that the function returned exit code 1
            assert exit_code == 1


def test_run_cli_unexpected_exception():
    """
    Tests that the run_cli function correctly handles unexpected exceptions during execution.
    """
    # Create test command-line arguments
    test_args = ["convert", "input.json", "output.xlsx"]

    # Create a mock for parse_arguments that returns command options
    mock_parse_arguments = unittest.mock.MagicMock(return_value=(get_basic_command_options(), None))

    # Create a mock for run_command that raises an unexpected exception
    mock_run_command = unittest.mock.MagicMock(side_effect=Exception("Unexpected error"))

    # Patch stderr to capture error output
    with unittest.mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
        # Patch parse_arguments and run_command
        with unittest.mock.patch('src.cli.command_runner.parse_arguments', mock_parse_arguments):
            with unittest.mock.patch('src.cli.command_runner.run_command', mock_run_command):
                # Call run_cli with the test arguments
                exit_code = run_cli(test_args)

                # Assert that parse_arguments was called once with the arguments
                mock_parse_arguments.assert_called_once_with(test_args)

                # Assert that run_command was called once with the command options
                mock_run_command.assert_called_once_with(get_basic_command_options())

                # Assert that an error message was printed to stderr
                assert "Unexpected error" in mock_stderr.getvalue()

                # Assert that the function returned exit code 1
                assert exit_code == 1


def test_main_function():
    """
    Tests that the main function correctly calls run_cli with sys.argv and exits with the appropriate code.
    """
    # Mock sys.argv to provide test arguments
    test_args = ["json_to_excel.py", "convert", "input.json", "output.xlsx"]

    # Mock sys.exit to prevent actual exit
    mock_sys_exit = unittest.mock.MagicMock()

    # Create a mock for run_cli that returns an exit code
    mock_run_cli = unittest.mock.MagicMock(return_value=0)

    # Patch sys.argv, sys.exit, and run_cli
    with unittest.mock.patch('sys.argv', test_args):
        with unittest.mock.patch('sys.exit', mock_sys_exit) as mock_exit:
            with unittest.mock.patch('src.cli.command_runner.run_cli', mock_run_cli):
                # Import and call the main function
                from src.cli.command_runner import main  # src/cli/command_runner.py
                main(sys.argv[1:])

                # Assert that run_cli was called once with sys.argv[1:]
                mock_run_cli.assert_called_once_with(sys.argv[1:])

                # Assert that sys.exit was called once with the exit code from run_cli
                mock_exit.assert_called_once_with(0)