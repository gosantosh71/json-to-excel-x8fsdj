"""
Unit tests for the console_formatter module of the JSON to Excel Conversion Tool.
This file contains test cases that verify the functionality of the ConsoleFormatter class
and related utility functions for formatting and displaying content in the command-line interface.
"""

import unittest
from unittest import mock
import pandas as pd

from ...console_formatter import (
    ConsoleFormatter,
    format_text,
    format_json,
    format_table,
    format_error,
    display_cli_response
)
from ...formatters.text_formatter import TextFormatter
from ...formatters.table_formatter import TableFormatter
from ...models.cli_response import CLIResponse, ResponseType
from ...backend.models.error_response import ErrorResponse
from ...progress_bar import ProgressBar, IndeterminateProgressBar
from ..fixtures.cli_fixtures import (
    get_success_response,
    get_error_response,
    get_validation_error
)


class TestConsoleFormatter(unittest.TestCase):
    """Test case class for testing the ConsoleFormatter class and its methods."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.formatter = ConsoleFormatter()
        self.test_message = "Test message"
        self.test_json = {"key": "value", "nested": {"item": "value"}}
        self.test_table_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        self.test_df = pd.DataFrame(self.test_table_data)
        
    def tearDown(self):
        """Clean up after each test method."""
        # Ensure any active progress bars or spinners are stopped
        if hasattr(self.formatter, '_progress_bar') and self.formatter._progress_bar is not None:
            self.formatter.finish_progress_bar()
        
        if hasattr(self.formatter, '_spinner') and self.formatter._spinner is not None:
            self.formatter.stop_spinner()
        
    def test_init(self):
        """Test the initialization of ConsoleFormatter."""
        # Test default initialization
        formatter = ConsoleFormatter()
        self.assertEqual(formatter._style, "default")
        self.assertIsNone(formatter._progress_bar)
        self.assertIsNone(formatter._spinner)
        
        # Test custom initialization
        formatter = ConsoleFormatter(style="custom_style", use_colors=False)
        self.assertEqual(formatter._style, "custom_style")
        self.assertFalse(formatter._use_colors)

    def test_print_message(self):
        """Test the print_message method with different message types."""
        with mock.patch('src.cli.console_formatter.print_success') as mock_print_success, \
             mock.patch('src.cli.console_formatter.print_error') as mock_print_error, \
             mock.patch('src.cli.console_formatter.print_warning') as mock_print_warning, \
             mock.patch('src.cli.console_formatter.print_info') as mock_print_info, \
             mock.patch('src.cli.console_formatter.print_message') as mock_print_message:
            
            # Test success message
            self.formatter.print_message("Test success", "success")
            mock_print_success.assert_called_once()
            
            # Test error message
            self.formatter.print_message("Test error", "error")
            mock_print_error.assert_called_once()
            
            # Test warning message
            self.formatter.print_message("Test warning", "warning")
            mock_print_warning.assert_called_once()
            
            # Test info message
            self.formatter.print_message("Test info", "info")
            mock_print_info.assert_called_once()
            
            # Test default message
            self.formatter.print_message("Test default", "unknown")
            mock_print_message.assert_called_once()

    def test_print_success(self):
        """Test the print_success method."""
        with mock.patch.object(self.formatter, 'print_message') as mock_print_message:
            self.formatter.print_success("Test success message")
            mock_print_message.assert_called_once_with("Test success message", "success")

    def test_print_error(self):
        """Test the print_error method."""
        with mock.patch.object(self.formatter, 'print_message') as mock_print_message:
            self.formatter.print_error("Test error message")
            mock_print_message.assert_called_once_with("Test error message", "error")

    def test_print_warning(self):
        """Test the print_warning method."""
        with mock.patch.object(self.formatter, 'print_message') as mock_print_message:
            self.formatter.print_warning("Test warning message")
            mock_print_message.assert_called_once_with("Test warning message", "warning")

    def test_print_info(self):
        """Test the print_info method."""
        with mock.patch.object(self.formatter, 'print_message') as mock_print_message:
            self.formatter.print_info("Test info message")
            mock_print_message.assert_called_once_with("Test info message", "info")

    def test_format_text(self):
        """Test the format_text method."""
        with mock.patch.object(TextFormatter, 'format_text') as mock_format_text:
            mock_format_text.return_value = "Formatted text"
            
            result = self.formatter.format_text("Test text")
            
            mock_format_text.assert_called_once_with("Test text")
            self.assertEqual(result, "Formatted text")

    def test_format_json(self):
        """Test the format_json method."""
        with mock.patch('src.cli.console_formatter.format_json_output') as mock_format_json:
            mock_format_json.return_value = "Formatted JSON"
            
            result = self.formatter.format_json(self.test_json)
            
            mock_format_json.assert_called_once_with(self.test_json, self.formatter._use_colors)
            self.assertEqual(result, "Formatted JSON")

    def test_format_table(self):
        """Test the format_table method with different data types."""
        with mock.patch('src.cli.console_formatter.format_table_output') as mock_format_table:
            mock_format_table.return_value = "Formatted table"
            
            # Test with DataFrame
            result = self.formatter.format_table(self.test_df)
            mock_format_table.assert_called_with(self.test_df, None, self.formatter._use_colors)
            self.assertEqual(result, "Formatted table")
            
            # Test with list of dictionaries
            result = self.formatter.format_table(self.test_table_data)
            mock_format_table.assert_called_with(self.test_table_data, None, self.formatter._use_colors)
            self.assertEqual(result, "Formatted table")

    def test_format_error(self):
        """Test the format_error method."""
        with mock.patch('src.cli.console_formatter.format_error_output') as mock_format_error:
            mock_format_error.return_value = "Formatted error"
            error = get_validation_error("Test validation error")
            
            result = self.formatter.format_error(error)
            
            mock_format_error.assert_called_once_with(error, False, self.formatter._use_colors)
            self.assertEqual(result, "Formatted error")

    def test_display_error(self):
        """Test the display_error method."""
        with mock.patch.object(self.formatter, 'format_error') as mock_format_error, \
             mock.patch.object(self.formatter, 'print_error') as mock_print_error:
            mock_format_error.return_value = "Formatted error message"
            error = get_validation_error("Test validation error")
            
            self.formatter.display_error(error)
            
            mock_format_error.assert_called_once_with(error, False)
            mock_print_error.assert_called_once_with("Formatted error message")

    def test_display_cli_response_success(self):
        """Test the display_cli_response method with a success response."""
        with mock.patch('src.cli.console_formatter.display_cli_response') as mock_display_cli_response:
            mock_display_cli_response.return_value = 0
            response = get_success_response("Test success", {"key": "value"})
            
            exit_code = self.formatter.display_cli_response(response)
            
            mock_display_cli_response.assert_called_once_with(
                response, False, self.formatter._use_colors
            )
            self.assertEqual(exit_code, 0)

    def test_display_cli_response_error(self):
        """Test the display_cli_response method with an error response."""
        with mock.patch('src.cli.console_formatter.display_cli_response') as mock_display_cli_response:
            mock_display_cli_response.return_value = 1
            error = get_validation_error("Test validation error")
            response = get_error_response("Test error", error)
            
            exit_code = self.formatter.display_cli_response(response, True)
            
            mock_display_cli_response.assert_called_once_with(
                response, True, self.formatter._use_colors
            )
            self.assertEqual(exit_code, 1)

    def test_start_progress(self):
        """Test the start_progress method."""
        with mock.patch('src.cli.console_formatter.ProgressBar') as MockProgressBar:
            mock_progress_bar = mock.MagicMock()
            MockProgressBar.return_value = mock_progress_bar
            
            self.formatter.start_progress_bar(100, "Processing:", "0%")
            
            MockProgressBar.assert_called_once_with(
                total=100,
                prefix="Processing:",
                suffix="0%",
                bar_length=40,
                use_colors=self.formatter._use_colors,
                show_eta=True
            )
            mock_progress_bar.start.assert_called_once()
            self.assertEqual(self.formatter._progress_bar, mock_progress_bar)

    def test_update_progress(self):
        """Test the update_progress method."""
        with mock.patch('src.cli.console_formatter.ProgressBar') as MockProgressBar:
            mock_progress_bar = mock.MagicMock()
            MockProgressBar.return_value = mock_progress_bar
            mock_progress_bar.is_active.return_value = True
            
            # Start a progress bar first
            self.formatter._progress_bar = mock_progress_bar
            
            # Update the progress
            self.formatter.update_progress_bar(50, "50%")
            
            mock_progress_bar.update.assert_called_once_with(50, "50%")

    def test_finish_progress(self):
        """Test the finish_progress method."""
        with mock.patch('src.cli.console_formatter.ProgressBar') as MockProgressBar:
            mock_progress_bar = mock.MagicMock()
            MockProgressBar.return_value = mock_progress_bar
            mock_progress_bar.is_active.return_value = True
            
            # Start a progress bar first
            self.formatter._progress_bar = mock_progress_bar
            
            # Finish the progress
            self.formatter.finish_progress_bar()
            
            mock_progress_bar.finish.assert_called_once()
            self.assertIsNone(self.formatter._progress_bar)

    def test_start_spinner(self):
        """Test the start_spinner method."""
        with mock.patch('src.cli.console_formatter.IndeterminateProgressBar') as MockSpinner:
            mock_spinner = mock.MagicMock()
            MockSpinner.return_value = mock_spinner
            
            self.formatter.start_spinner("Processing...")
            
            MockSpinner.assert_called_once_with(
                message="Processing...",
                use_colors=self.formatter._use_colors
            )
            mock_spinner.start.assert_called_once()
            self.assertEqual(self.formatter._spinner, mock_spinner)

    def test_update_spinner_message(self):
        """Test the update_spinner_message method."""
        with mock.patch('src.cli.console_formatter.IndeterminateProgressBar') as MockSpinner:
            mock_spinner = mock.MagicMock()
            MockSpinner.return_value = mock_spinner
            mock_spinner.is_active.return_value = True
            
            # Start a spinner first
            self.formatter._spinner = mock_spinner
            
            # Update the spinner message
            self.formatter.update_spinner_message("New message")
            
            mock_spinner.update_message.assert_called_once_with("New message")

    def test_stop_spinner(self):
        """Test the stop_spinner method."""
        with mock.patch('src.cli.console_formatter.IndeterminateProgressBar') as MockSpinner:
            mock_spinner = mock.MagicMock()
            MockSpinner.return_value = mock_spinner
            mock_spinner.is_active.return_value = True
            
            # Start a spinner first
            self.formatter._spinner = mock_spinner
            
            # Stop the spinner
            self.formatter.stop_spinner()
            
            mock_spinner.stop.assert_called_once()
            self.assertIsNone(self.formatter._spinner)

    def test_set_text_style(self):
        """Test the set_text_style method."""
        with mock.patch.object(TextFormatter, 'set_style') as mock_set_style:
            self.formatter.set_text_style("compact")
            mock_set_style.assert_called_once_with("compact")

    def test_set_table_style(self):
        """Test the set_table_style method."""
        with mock.patch.object(TableFormatter, 'set_style') as mock_set_style:
            self.formatter.set_table_style("grid")
            mock_set_style.assert_called_once_with("grid")

    def test_set_use_colors(self):
        """Test the set_use_colors method."""
        # Test setting to True
        self.formatter.set_use_colors(True)
        self.assertTrue(self.formatter._use_colors)
        
        # Test setting to False
        self.formatter.set_use_colors(False)
        self.assertFalse(self.formatter._use_colors)


class TestConsoleFormatterFunctions(unittest.TestCase):
    """Test case class for testing the standalone utility functions in the console_formatter module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_json = {"key": "value", "nested": {"item": "value"}}
        self.test_table_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        self.test_df = pd.DataFrame(self.test_table_data)
        
    def tearDown(self):
        """Clean up after each test method."""
        pass

    def test_format_text_function(self):
        """Test the standalone format_text function."""
        with mock.patch.object(TextFormatter, 'format_text') as mock_format_text:
            mock_format_text.return_value = "Formatted text"
            
            result = format_text("Test text", style="default", use_colors=True)
            
            self.assertEqual(result, "Formatted text")
            mock_format_text.assert_called_once_with("Test text")

    def test_format_json_function(self):
        """Test the standalone format_json function."""
        with mock.patch.object(TextFormatter, 'format_json') as mock_format_json:
            mock_format_json.return_value = "Formatted JSON"
            
            result = format_json(self.test_json, indent=2, use_colors=True)
            
            self.assertEqual(result, "Formatted JSON")
            mock_format_json.assert_called_once_with(self.test_json)

    def test_format_table_function(self):
        """Test the standalone format_table function."""
        with mock.patch.object(TableFormatter, 'format_data') as mock_format_data:
            mock_format_data.return_value = "Formatted table"
            
            result = format_table(self.test_df, headers=["name", "age"], use_colors=True)
            
            self.assertEqual(result, "Formatted table")
            mock_format_data.assert_called_once_with(self.test_df)

    def test_format_error_function(self):
        """Test the standalone format_error function."""
        with mock.patch('src.cli.console_formatter.format_error_output') as mock_format_error:
            mock_format_error.return_value = "Formatted error"
            error = get_validation_error("Test validation error")
            
            result = format_error(error, include_details=True, use_colors=True)
            
            mock_format_error.assert_called_once_with(error, True, True)
            self.assertEqual(result, "Formatted error")

    def test_format_cli_response_function(self):
        """Test the standalone format_cli_response function."""
        with mock.patch('src.cli.console_formatter.format_cli_response') as mock_format_cli_response:
            mock_format_cli_response.return_value = "Formatted response"
            response = get_success_response("Test success", {"key": "value"})
            
            result = format_cli_response(response, verbose=True, use_colors=True)
            
            self.assertEqual(result, "Formatted response")

    def test_display_cli_response_function(self):
        """Test the standalone display_cli_response function."""
        with mock.patch('src.cli.console_formatter.print_success') as mock_print_success, \
             mock.patch('src.cli.console_formatter.print_error') as mock_print_error, \
             mock.patch('src.cli.console_formatter.format_cli_response') as mock_format_cli_response:
            mock_format_cli_response.return_value = "Formatted response"
            
            # Test success response
            success_response = get_success_response("Test success", {"key": "value"})
            exit_code = display_cli_response(success_response, verbose=True, use_colors=True)
            
            mock_print_success.assert_called_once_with("Formatted response")
            self.assertEqual(exit_code, 0)
            
            # Reset mocks for error test
            mock_print_success.reset_mock()
            mock_print_error.reset_mock()
            
            # Test error response
            error = get_validation_error("Test validation error")
            error_response = get_error_response("Test error", error)
            exit_code = display_cli_response(error_response, verbose=True, use_colors=True)
            
            mock_print_error.assert_called_once_with("Formatted response")
            self.assertEqual(exit_code, 1)

    def test_create_progress_bar_function(self):
        """Test the standalone create_progress_bar function."""
        with mock.patch('src.cli.progress_bar.ProgressBar') as MockProgressBar:
            mock_progress_bar = mock.MagicMock()
            MockProgressBar.return_value = mock_progress_bar
            
            # Import here to avoid circular imports in tests
            from ...console_formatter import create_progress_bar
            
            progress_bar = create_progress_bar(
                total=100, 
                prefix="Processing:", 
                suffix="0%", 
                bar_length=50, 
                use_colors=True
            )
            
            MockProgressBar.assert_called_once()
            self.assertEqual(progress_bar, mock_progress_bar)
            # Verify that start was not called (since we're just creating, not starting)
            mock_progress_bar.start.assert_not_called()

    def test_create_spinner_function(self):
        """Test the standalone create_spinner function."""
        with mock.patch('src.cli.progress_bar.IndeterminateProgressBar') as MockSpinner:
            mock_spinner = mock.MagicMock()
            MockSpinner.return_value = mock_spinner
            
            # Import here to avoid circular imports in tests
            from ...console_formatter import create_spinner
            
            spinner = create_spinner(message="Processing...", use_colors=True)
            
            MockSpinner.assert_called_once()
            self.assertEqual(spinner, mock_spinner)
            # Verify that start was not called (since we're just creating, not starting)
            mock_spinner.start.assert_not_called()


if __name__ == '__main__':
    unittest.main()