"""
Unit tests for the argument parser component of the JSON to Excel Conversion Tool.

This module contains tests to verify the correct parsing, validation, and handling
of command-line arguments for various commands and scenarios.
"""

import pytest  # v: 7.3.0+
import unittest.mock as mock
import io
import sys
import os

from ../../argument_parser import parse_arguments, validate_arguments, display_help
from ../../models.command_options import CommandOptions, CommandType
from ../fixtures/cli_fixtures import (
    get_basic_command_options,
    get_complex_command_options, 
    get_invalid_command_options,
    get_validation_error
)
from ../../utils.path_utils import validate_input_file, validate_output_file


def test_parse_arguments_convert_command():
    """Tests that the parse_arguments function correctly parses the convert command with required arguments."""
    # Set up test arguments
    test_args = ['convert', 'test.json', 'output.xlsx']
    
    # Call parse_arguments with test arguments
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.CONVERT
    assert result.input_file == 'test.json'
    assert result.output_file == 'output.xlsx'
    assert result.sheet_name is None  # Default value
    assert result.array_handling is None  # Default value
    assert result.verbose is False  # Default value


def test_parse_arguments_convert_with_options():
    """Tests that the parse_arguments function correctly parses the convert command with all optional arguments."""
    # Set up test arguments with optional parameters
    test_args = [
        'convert', 
        'test.json', 
        'output.xlsx', 
        '--sheet-name=CustomSheet', 
        '--array-handling=join',
        '--verbose',
        '--chunk-size=1000',
        '--fields=id,name,address.city'
    ]
    
    # Call parse_arguments with test arguments
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.CONVERT
    assert result.input_file == 'test.json'
    assert result.output_file == 'output.xlsx'
    assert result.sheet_name == 'CustomSheet'
    assert result.array_handling == 'join'
    assert result.verbose is True
    assert result.chunk_size == 1000
    assert result.fields == 'id,name,address.city'


def test_parse_arguments_validate_command():
    """Tests that the parse_arguments function correctly parses the validate command."""
    # Set up test arguments
    test_args = ['validate', 'test.json']
    
    # Call parse_arguments with test arguments
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.VALIDATE
    assert result.input_file == 'test.json'
    assert result.verbose is False  # Default value


def test_parse_arguments_info_command():
    """Tests that the parse_arguments function correctly parses the info command."""
    # Set up test arguments
    test_args = ['info', 'test.json', '--format=json']
    
    # Call parse_arguments with test arguments
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.INFO
    assert result.input_file == 'test.json'
    assert result.format == 'json'
    assert result.verbose is False  # Default value


def test_parse_arguments_help_command():
    """Tests that the parse_arguments function correctly parses the help command."""
    # Set up test arguments
    test_args = ['help']
    
    # Call parse_arguments and mock sys.exit to prevent test from exiting
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        with mock.patch('sys.exit') as mock_exit:
            result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.HELP
    assert result.help_command is None  # No specific command help requested


def test_parse_arguments_help_with_command():
    """Tests that the parse_arguments function correctly parses the help command with a specific command argument."""
    # Set up test arguments
    test_args = ['help', 'convert']
    
    # Call parse_arguments and mock sys.exit to prevent test from exiting
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        with mock.patch('sys.exit') as mock_exit:
            result = parse_arguments()
    
    # Assert results
    assert result.command == CommandType.HELP
    assert result.help_command == 'convert'


def test_parse_arguments_invalid_command():
    """Tests that the parse_arguments function correctly handles invalid commands."""
    # Set up test arguments with an invalid command
    test_args = ['invalid_command', 'test.json']
    
    # Call parse_arguments and mock sys.exit to prevent test from exiting
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        with mock.patch('sys.exit') as mock_exit:
            with mock.patch('sys.stderr', new=io.StringIO()) as mock_stderr:
                try:
                    parse_arguments()
                except SystemExit:
                    pass
    
    # Assert that sys.exit was called
    mock_exit.assert_called_once()
    
    # Assert that error message contains expected text
    stderr_output = mock_stderr.getvalue()
    assert "invalid choice" in stderr_output.lower()


def test_parse_arguments_missing_required_args():
    """Tests that the parse_arguments function correctly handles missing required arguments."""
    # Set up test arguments missing required output_file
    test_args = ['convert', 'test.json']
    
    # Call parse_arguments and mock sys.exit to prevent test from exiting
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        with mock.patch('sys.exit') as mock_exit:
            with mock.patch('sys.stderr', new=io.StringIO()) as mock_stderr:
                try:
                    parse_arguments()
                except SystemExit:
                    pass
    
    # Assert that sys.exit was called
    mock_exit.assert_called_once()
    
    # Assert that error message contains expected text
    stderr_output = mock_stderr.getvalue()
    assert "required" in stderr_output.lower()


def test_validate_arguments_valid():
    """Tests that the validate_arguments function correctly validates valid command options."""
    # Create valid CommandOptions
    options = get_basic_command_options()
    
    # Mock validate_input_file and validate_output_file to return True
    with mock.patch('../../utils.path_utils.validate_input_file', return_value=True):
        with mock.patch('../../utils.path_utils.validate_output_file', return_value=True):
            result = validate_arguments(options)
    
    # Assert that validation passed
    assert result is True


def test_validate_arguments_invalid():
    """Tests that the validate_arguments function correctly validates invalid command options."""
    # Create invalid CommandOptions
    options = get_invalid_command_options()
    
    # Call validate_arguments
    result = validate_arguments(options)
    
    # Assert that validation failed
    assert result is False


def test_validate_arguments_invalid_input_file():
    """Tests that the validate_arguments function correctly handles invalid input file paths."""
    # Create valid CommandOptions
    options = get_basic_command_options()
    
    # Mock validate_input_file to return False and validate_output_file to return True
    with mock.patch('../../utils.path_utils.validate_input_file', return_value=False):
        with mock.patch('../../utils.path_utils.validate_output_file', return_value=True):
            result = validate_arguments(options)
    
    # Assert that validation failed
    assert result is False


def test_validate_arguments_invalid_output_file():
    """Tests that the validate_arguments function correctly handles invalid output file paths."""
    # Create valid CommandOptions
    options = get_basic_command_options()
    
    # Mock validate_input_file to return True and validate_output_file to return False
    with mock.patch('../../utils.path_utils.validate_input_file', return_value=True):
        with mock.patch('../../utils.path_utils.validate_output_file', return_value=False):
            result = validate_arguments(options)
    
    # Assert that validation failed
    assert result is False


def test_display_help_general():
    """Tests that the display_help function correctly displays general help information."""
    # Create a mock parser
    mock_parser = mock.Mock()
    
    # Call display_help with no command specified
    display_help(None, mock_parser)
    
    # Assert that print_help was called
    mock_parser.print_help.assert_called_once()


def test_display_help_specific_command():
    """Tests that the display_help function correctly displays help for a specific command."""
    # Create a mock parser
    mock_parser = mock.Mock()
    
    # Call display_help with a specific command
    with mock.patch('sys.stdout', new=io.StringIO()) as mock_stdout:
        display_help('convert', mock_parser)
    
    # Assert that the output contains expected help text for convert command
    output = mock_stdout.getvalue()
    assert "convert" in output.lower()
    assert "input_json_file" in output
    assert "output_excel_file" in output


def test_normalize_paths():
    """Tests that file paths are correctly normalized during argument parsing."""
    # Set up test arguments with relative paths
    test_args = ['convert', './test.json', '../output.xlsx']
    
    # Define mock absolute paths
    mock_input_path = '/absolute/path/to/test.json'
    mock_output_path = '/absolute/path/to/output.xlsx'
    
    # Mock os.path.abspath to return predictable paths
    def mock_abspath(path):
        if path == './test.json':
            return mock_input_path
        elif path == '../output.xlsx':
            return mock_output_path
        return path
    
    # Call parse_arguments with mocked path normalization
    with mock.patch('sys.argv', ['json_to_excel.py'] + test_args):
        with mock.patch('os.path.abspath', side_effect=mock_abspath):
            with mock.patch('../../utils.path_utils.normalize_cli_path', side_effect=mock_abspath):
                result = parse_arguments()
    
    # Assert paths were normalized
    assert result.input_file == mock_input_path
    assert result.output_file == mock_output_path