import unittest
import os
from unittest.mock import patch, MagicMock, call

from ../../error_display import (
    display_error,
    display_exception,
    display_validation_errors,
    display_warning,
    display_cli_error,
    is_verbose_mode,
    ErrorDisplayManager
)
from ../fixtures/cli_fixtures import (
    get_validation_error,
    get_file_not_found_error,
    get_json_parsing_error,
    get_success_response,
    get_error_response
)
from ../../console_formatter import format_error
from ../../models/cli_response import CLIResponse, ResponseType


class TestDisplayError(unittest.TestCase):
    """Test case class for the display_error function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample error responses for testing
        self.validation_error = get_validation_error("Invalid input parameters")
        self.file_not_found_error = get_file_not_found_error("nonexistent.json")
        self.json_parsing_error = get_json_parsing_error("invalid.json", "Syntax error at line 42")
        
        # Set up mock objects for dependencies
        self.patcher_is_verbose = patch('src.cli.error_display.is_verbose_mode')
        self.mock_is_verbose = self.patcher_is_verbose.start()
        self.mock_is_verbose.return_value = False
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Reset any environment variables that were modified
        self.patcher_is_verbose.stop()
        
    @patch('src.cli.error_display.print_error')
    @patch('src.cli.error_display.format_error_message')
    def test_display_error_basic(self, mock_format_error, mock_print_error):
        """Test that display_error correctly formats and displays a basic error."""
        # Mock the format_error function to return a known string
        mock_format_error.return_value = "Formatted error message"
        
        # Call display_error with a validation error and verbose=False
        display_error(self.validation_error, verbose=False)
        
        # Assert that format_error was called with the correct parameters
        mock_format_error.assert_called_once()
        # Assert that print_error was called with the formatted error message
        mock_print_error.assert_called_with("Formatted error message")
        
    @patch('src.cli.error_display.print_error')
    @patch('src.cli.error_display.print_info')
    @patch('src.cli.error_display.format_error_message')
    def test_display_error_verbose(self, mock_format_error, mock_print_info, mock_print_error):
        """Test that display_error includes technical details when verbose mode is enabled."""
        # Mock the format_error function to return a known string
        mock_format_error.return_value = "Formatted error message"
        
        # Call display_error with a validation error and verbose=True
        display_error(self.validation_error, verbose=True)
        
        # Assert that format_error was called with include_details=True
        mock_format_error.assert_called_once()
        # Assert that print_error was called with the formatted error message
        mock_print_error.assert_called_with("Formatted error message")
        # Assert that print_info was called with technical details
        mock_print_info.assert_called_once()
        
    @patch('src.cli.error_display.print_error')
    @patch('src.cli.error_display.print_info')
    @patch('src.cli.error_display.format_resolution_steps')
    def test_display_error_with_resolution_steps(self, mock_format_resolution, mock_print_info, mock_print_error):
        """Test that display_error correctly displays resolution steps when available."""
        # Create an error response with resolution steps
        error_with_steps = self.validation_error
        error_with_steps.resolution_steps = ["Step 1", "Step 2"]
        mock_format_resolution.return_value = "Formatted resolution steps"
        
        # Call display_error with the error response
        display_error(error_with_steps)
        
        # Assert that print_info was called with the resolution steps
        mock_format_resolution.assert_called_with(error_with_steps.resolution_steps)


class TestDisplayException(unittest.TestCase):
    """Test case class for the display_exception function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample exceptions for testing
        self.test_exception = ValueError("Test error message")
        
    @patch('src.cli.error_display.print_error')
    def test_display_exception_basic(self, mock_print_error):
        """Test that display_exception correctly formats and displays a basic exception."""
        # Create a test exception
        exception = ValueError("Test error message")
        
        # Call display_exception with the exception and a context message
        display_exception(exception, "Error during processing")
        
        # Assert that print_error was called with a message containing the context and exception info
        mock_print_error.assert_called_once()
        called_with_arg = mock_print_error.call_args[0][0]
        self.assertIn("Error during processing", called_with_arg)
        self.assertIn("Test error message", called_with_arg)
        
    @patch('src.cli.error_display.print_error')
    @patch('src.cli.error_display.print_info')
    def test_display_exception_verbose(self, mock_print_info, mock_print_error):
        """Test that display_exception includes traceback when verbose mode is enabled."""
        # Create a test exception
        exception = ValueError("Test error message")
        
        # Call display_exception with the exception, context message, and verbose=True
        display_exception(exception, "Error during processing", verbose=True)
        
        # Assert that print_error was called with the error message
        mock_print_error.assert_called_once()
        # Assert that print_info was called with traceback information
        mock_print_info.assert_called_once()
        called_with_arg = mock_print_info.call_args[0][0]
        self.assertIn("Traceback", called_with_arg)


class TestDisplayValidationErrors(unittest.TestCase):
    """Test case class for the display_validation_errors function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample validation errors for testing
        self.validation_errors = [
            {"field": "input_file", "message": "Input file is required"},
            {"field": "output_file", "message": "Output file is required"}
        ]
        
    @patch('src.cli.error_display.print_error')
    def test_display_validation_errors(self, mock_print_error):
        """Test that display_validation_errors correctly formats and displays validation errors."""
        # Create a list of validation error dictionaries
        validation_errors = [
            {"field": "input_file", "message": "Input file is required"},
            {"field": "output_file", "message": "Output file is required"}
        ]
        
        # Call display_validation_errors with the validation errors and a context message
        display_validation_errors(validation_errors, "Validation failed")
        
        # Assert that print_error was called with the context message
        mock_print_error.assert_any_call("Validation failed")
        # Assert that print_error was called for each validation error with field and message
        for error in validation_errors:
            mock_print_error.assert_any_call(f"  Field '{error['field']}': {error['message']}")
        
    @patch('src.cli.error_display.print_error')
    def test_display_validation_errors_with_fix(self, mock_print_error):
        """Test that display_validation_errors includes suggested fixes when available."""
        # Create a list of validation error dictionaries with suggested_fix fields
        validation_errors = [
            {"field": "input_file", "message": "Input file is required", "suggested_fix": "Provide an input file path"},
            {"field": "output_file", "message": "Output file is required", "suggested_fix": "Provide an output file path"}
        ]
        
        # Call display_validation_errors with the validation errors
        display_validation_errors(validation_errors, "Validation failed")
        
        # Assert that print_error was called with messages including the suggested fixes
        for error in validation_errors:
            expected_message = f"  Field '{error['field']}': {error['message']} (Fix: {error['suggested_fix']})"
            mock_print_error.assert_any_call(expected_message)


class TestDisplayWarning(unittest.TestCase):
    """Test case class for the display_warning function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up mock objects for dependencies
        pass
        
    @patch('src.cli.error_display.print_warning')
    def test_display_warning_basic(self, mock_print_warning):
        """Test that display_warning correctly displays a basic warning message."""
        # Call display_warning with a warning message
        display_warning("This is a warning message")
        
        # Assert that print_warning was called with the warning message
        mock_print_warning.assert_called_with("This is a warning message")
        
    @patch('src.cli.error_display.print_warning')
    @patch('src.cli.error_display.print_info')
    def test_display_warning_with_details(self, mock_print_info, mock_print_warning):
        """Test that display_warning correctly displays warning details when provided."""
        # Call display_warning with a message and details dictionary
        display_warning("This is a warning message", {"source": "test", "code": 123})
        
        # Assert that print_warning was called with the warning message
        mock_print_warning.assert_called_with("This is a warning message")
        # Assert that print_info was called with the formatted details
        mock_print_info.assert_called_once()
        called_with_arg = mock_print_info.call_args[0][0]
        self.assertIn("source: test", called_with_arg)
        self.assertIn("code: 123", called_with_arg)


class TestDisplayCliError(unittest.TestCase):
    """Test case class for the display_cli_error function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up mock objects for dependencies
        pass
        
    @patch('src.cli.error_display.print_error')
    def test_display_cli_error_basic(self, mock_print_error):
        """Test that display_cli_error correctly displays a basic CLI error and returns the exit code."""
        # Call display_cli_error with a message and exit code
        exit_code = display_cli_error("Invalid command", 2)
        
        # Assert that print_error was called with the error message
        mock_print_error.assert_called_with("Invalid command")
        # Assert that the function returns the provided exit code
        self.assertEqual(exit_code, 2)
        
    @patch('src.cli.error_display.print_error')
    @patch('src.cli.error_display.print_info')
    def test_display_cli_error_with_details(self, mock_print_info, mock_print_error):
        """Test that display_cli_error correctly displays error details when verbose mode is enabled."""
        # Call display_cli_error with a message, exit code, details, and verbose=True
        exit_code = display_cli_error("Invalid command", 2, {"file": "test.json", "reason": "Not found"}, verbose=True)
        
        # Assert that print_error was called with the error message
        mock_print_error.assert_called_with("Invalid command")
        # Assert that print_info was called with the formatted details
        mock_print_info.assert_called_once()
        # Assert that the function returns the provided exit code
        self.assertEqual(exit_code, 2)


class TestIsVerboseMode(unittest.TestCase):
    """Test case class for the is_verbose_mode function."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Save original environment variables
        self.original_env = os.environ.copy()
        # Clear any existing verbose environment variables
        if 'JSON2EXCEL_VERBOSE' in os.environ:
            del os.environ['JSON2EXCEL_VERBOSE']
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
        
    def test_is_verbose_mode_param(self):
        """Test that is_verbose_mode returns the value of the verbose parameter when provided."""
        # Call is_verbose_mode with verbose_param=True
        result = is_verbose_mode(verbose_param=True)
        self.assertTrue(result)
        
        # Call is_verbose_mode with verbose_param=False
        result = is_verbose_mode(verbose_param=False)
        self.assertFalse(result)
        
    def test_is_verbose_mode_env_var(self):
        """Test that is_verbose_mode checks the environment variable when no parameter is provided."""
        # Set the JSON2EXCEL_VERBOSE environment variable to '1'
        os.environ['JSON2EXCEL_VERBOSE'] = '1'
        result = is_verbose_mode()
        self.assertTrue(result)
        
        # Set the JSON2EXCEL_VERBOSE environment variable to '0'
        os.environ['JSON2EXCEL_VERBOSE'] = '0'
        result = is_verbose_mode()
        self.assertFalse(result)
        
    def test_is_verbose_mode_default(self):
        """Test that is_verbose_mode returns the default value when no parameter or environment variable is set."""
        # Ensure the JSON2EXCEL_VERBOSE environment variable is not set
        if 'JSON2EXCEL_VERBOSE' in os.environ:
            del os.environ['JSON2EXCEL_VERBOSE']
            
        # Call is_verbose_mode with no parameters
        result = is_verbose_mode()
        
        # Assert that the function returns the DEFAULT_VERBOSE value
        self.assertIsInstance(result, bool)


class TestErrorDisplayManager(unittest.TestCase):
    """Test case class for the ErrorDisplayManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample error responses for testing
        self.validation_error = get_validation_error("Invalid input parameters")
        self.file_not_found_error = get_file_not_found_error("nonexistent.json")
        # Create sample CLI responses for testing
        self.success_response = get_success_response("Conversion completed successfully", {"rows": 100})
        self.error_response = get_error_response("Conversion failed", self.validation_error)
        
    def test_init(self):
        """Test that ErrorDisplayManager initializes with the correct settings."""
        # Create an ErrorDisplayManager with use_colors=True and verbose=True
        manager = ErrorDisplayManager(use_colors=True, verbose=True)
        self.assertTrue(manager._use_colors)
        self.assertTrue(manager._verbose)
        
        # Create an ErrorDisplayManager with use_colors=False and verbose=False
        manager = ErrorDisplayManager(use_colors=False, verbose=False)
        self.assertFalse(manager._use_colors)
        self.assertFalse(manager._verbose)
        
    @patch('src.cli.error_display.display_error')
    def test_display_error(self, mock_display_error):
        """Test that ErrorDisplayManager.display_error correctly calls the global display_error function."""
        # Create an ErrorDisplayManager with specific settings
        manager = ErrorDisplayManager(verbose=True)
        
        # Call manager.display_error with a sample error
        manager.display_error(self.validation_error)
        
        # Assert that display_error was called with the error and the manager's verbose setting
        mock_display_error.assert_called_with(self.validation_error, verbose=True)
        
    @patch('src.cli.error_display.display_exception')
    def test_display_exception(self, mock_display_exception):
        """Test that ErrorDisplayManager.display_exception correctly calls the global display_exception function."""
        # Create an ErrorDisplayManager with specific settings
        manager = ErrorDisplayManager(verbose=True)
        
        # Create a test exception
        exception = ValueError("Test error message")
        
        # Call manager.display_exception with the exception and a context message
        manager.display_exception(exception, "Error during processing")
        
        # Assert that display_exception was called with the exception, context message, and the manager's verbose setting
        mock_display_exception.assert_called_with(exception, "Error during processing", verbose=True)
        
    @patch('src.cli.error_display.display_warning')
    def test_display_warning(self, mock_display_warning):
        """Test that ErrorDisplayManager.display_warning correctly calls the global display_warning function."""
        # Create an ErrorDisplayManager with specific settings
        manager = ErrorDisplayManager()
        
        # Call manager.display_warning with a message and details
        manager.display_warning("This is a warning message", {"source": "test"})
        
        # Assert that display_warning was called with the message and details
        mock_display_warning.assert_called_with("This is a warning message", {"source": "test"})
        
    @patch('src.cli.error_display.display_cli_error')
    def test_display_cli_error(self, mock_display_cli_error):
        """Test that ErrorDisplayManager.display_cli_error correctly calls the global display_cli_error function."""
        # Set up return value for the mock
        mock_display_cli_error.return_value = 2
        
        # Create an ErrorDisplayManager with specific settings
        manager = ErrorDisplayManager(verbose=True)
        
        # Call manager.display_cli_error with a message, exit code, and details
        exit_code = manager.display_cli_error("Invalid command", 2, {"file": "test.json"})
        
        # Assert that display_cli_error was called with the message, exit code, details, and the manager's verbose setting
        mock_display_cli_error.assert_called_with("Invalid command", 2, {"file": "test.json"}, verbose=True)
        # Assert that the function returns the exit code from display_cli_error
        self.assertEqual(exit_code, 2)
        
    @patch('src.cli.error_display.print_success')
    @patch('src.cli.error_display.print_error')
    def test_display_cli_response(self, mock_print_error, mock_print_success):
        """Test that ErrorDisplayManager.display_cli_response correctly displays a CLI response."""
        # Create an ErrorDisplayManager with specific settings
        manager = ErrorDisplayManager()
        
        # Call manager.display_cli_response with the success response
        exit_code = manager.display_cli_response(self.success_response)
        
        # Assert that print_success was called with the formatted output
        mock_print_success.assert_called_once()
        # Assert that the function returns the correct exit code
        self.assertEqual(exit_code, 0)
        
        # Reset mocks
        mock_print_success.reset_mock()
        mock_print_error.reset_mock()
        
        # Call manager.display_cli_response with the error response
        exit_code = manager.display_cli_response(self.error_response)
        
        # Assert that print_error was called with the formatted output
        mock_print_error.assert_called_once()
        # Assert that the function returns the correct exit code
        self.assertEqual(exit_code, 1)
        
    def test_set_verbose(self):
        """Test that ErrorDisplayManager.set_verbose correctly updates the verbose setting."""
        # Create an ErrorDisplayManager with verbose=False
        manager = ErrorDisplayManager(verbose=False)
        self.assertFalse(manager._verbose)
        
        # Call manager.set_verbose(True)
        manager.set_verbose(True)
        self.assertTrue(manager._verbose)
        
        # Call manager.set_verbose(False)
        manager.set_verbose(False)
        self.assertFalse(manager._verbose)
        
    def test_set_use_colors(self):
        """Test that ErrorDisplayManager.set_use_colors correctly updates the color setting."""
        # Create an ErrorDisplayManager with use_colors=False
        manager = ErrorDisplayManager(use_colors=False)
        self.assertFalse(manager._use_colors)
        
        # Call manager.set_use_colors(True)
        manager.set_use_colors(True)
        self.assertTrue(manager._use_colors)
        
        # Call manager.set_use_colors(False)
        manager.set_use_colors(False)
        self.assertFalse(manager._use_colors)