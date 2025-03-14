"""
Provides a specialized console logging interface for the CLI component of the JSON to Excel Conversion Tool.
This module extends the core logging functionality with console-specific formatting, color support, 
and progress indication to create a user-friendly command-line experience.
"""

import logging  # v: built-in
import os  # v: built-in
import sys  # v: built-in
import typing  # v: built-in

from ..backend.logger import get_logger
from .utils.console_utils import (
    is_color_supported,
    print_message,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_processing
)
from .progress_bar import (
    ProgressBar, 
    IndeterminateProgressBar
)

# Initialize logger for this module
logger = get_logger(__name__)

# Determine if color output is supported
USE_COLORS = is_color_supported()

# Environment variable for verbose mode
VERBOSE_ENV_VAR = "JSON2EXCEL_VERBOSE"

# Default verbose setting
DEFAULT_VERBOSE = False


def is_verbose_mode(verbose_param: typing.Optional[bool] = None) -> bool:
    """
    Determines if verbose output mode is enabled based on environment variable or parameter.
    
    Args:
        verbose_param: Optional explicit verbose setting parameter
        
    Returns:
        bool: True if verbose mode is enabled, False otherwise
    """
    # If explicit parameter is provided, use it
    if verbose_param is not None:
        return verbose_param
    
    # Check environment variable
    env_value = os.environ.get(VERBOSE_ENV_VAR, "").lower()
    
    # Check for truthy environment values
    if env_value in ("1", "true", "yes", "y"):
        return True
    
    # Return default value
    return DEFAULT_VERBOSE


class ConsoleLogHandler(logging.Handler):
    """
    A logging handler that formats log messages for console output with appropriate styling.
    """
    
    def __init__(self, use_colors: bool = None, verbose: bool = None):
        """
        Initializes a new ConsoleLogHandler with the specified display settings.
        
        Args:
            use_colors: Whether to use colored output (defaults to auto-detection)
            verbose: Whether to enable verbose output (defaults to environment setting)
        """
        super().__init__()
        
        # Store display settings
        self._use_colors = USE_COLORS if use_colors is None else use_colors
        self._verbose = is_verbose_mode(verbose)
        
        # Set log level based on verbose mode
        self.setLevel(logging.DEBUG if self._verbose else logging.INFO)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Processes and displays a log record in the console.
        
        Args:
            record: The log record to emit
        """
        try:
            # Format the log message
            msg = self.format(record)
            
            # Choose appropriate print function based on log level
            if record.levelno >= logging.ERROR:
                print_error(msg)
            elif record.levelno >= logging.WARNING:
                print_warning(msg)
            elif record.levelno >= logging.INFO:
                if hasattr(record, 'success') and record.success:
                    print_success(msg)
                elif hasattr(record, 'processing') and record.processing:
                    print_processing(msg)
                else:
                    print_info(msg)
            else:  # DEBUG
                print_message(msg, color="BLUE" if self._use_colors else None)
        
        except Exception:
            # Handle any exceptions during emission
            self.handleError(record)
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Sets the verbose mode for the handler.
        
        Args:
            verbose: Whether to enable verbose mode
        """
        self._verbose = verbose
        self.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    def set_use_colors(self, use_colors: bool) -> None:
        """
        Sets whether to use colors in log output.
        
        Args:
            use_colors: Whether to use colors
        """
        self._use_colors = use_colors


class ConsoleLogger:
    """
    A specialized logger for CLI applications with console-specific formatting and progress tracking.
    """
    
    def __init__(self, name: str, use_colors: bool = None, verbose: bool = None):
        """
        Initializes a new ConsoleLogger instance with the specified settings.
        
        Args:
            name: Name for the logger
            use_colors: Whether to use colored output (defaults to auto-detection)
            verbose: Whether to enable verbose output (defaults to environment setting)
        """
        # Get a logger instance
        self._logger = get_logger(name)
        
        # Create and configure a console handler
        self._handler = ConsoleLogHandler(use_colors, verbose)
        formatter = logging.Formatter('%(message)s')
        self._handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self._logger.addHandler(self._handler)
        
        # Store settings
        self._use_colors = USE_COLORS if use_colors is None else use_colors
        self._verbose = is_verbose_mode(verbose)
        
        # Initialize progress tracking attributes
        self._progress_bar = None
        self._spinner = None
    
    def debug(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a message at DEBUG level.
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        self._logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a message at INFO level.
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        self._logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a message at WARNING level.
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        self._logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a message at ERROR level.
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        self._logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a message at CRITICAL level.
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        self._logger.critical(message, extra=extra)
    
    def exception(self, message: str, exc_info: typing.Optional[Exception] = None, 
                  extra: typing.Optional[dict] = None) -> None:
        """
        Logs an exception with traceback information.
        
        Args:
            message: The message to log
            exc_info: Exception information
            extra: Additional log record fields
        """
        self._logger.exception(message, exc_info=exc_info, extra=extra)
    
    def success(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a success message (custom level).
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        # Log at INFO level but with success=True for formatting
        extra_data = extra or {}
        extra_data['success'] = True
        self._logger.info(message, extra=extra_data)
        
        # Also print directly for immediate visual feedback
        print_success(message)
    
    def processing(self, message: str, extra: typing.Optional[dict] = None) -> None:
        """
        Logs a processing status message (custom level).
        
        Args:
            message: The message to log
            extra: Additional log record fields
        """
        # Log at INFO level but with processing=True for formatting
        extra_data = extra or {}
        extra_data['processing'] = True
        self._logger.info(message, extra=extra_data)
        
        # Also print directly for immediate visual feedback
        print_processing(message)
    
    def start_progress(self, total: float, prefix: str = "Progress:", suffix: str = "",
                       bar_length: int = 50, show_eta: bool = True) -> None:
        """
        Starts a progress bar for tracking operation progress.
        
        Args:
            total: Total value representing 100% completion
            prefix: Text displayed before the progress bar
            suffix: Text displayed after the progress bar
            bar_length: Length of the progress bar in characters
            show_eta: Whether to show ETA information
        """
        # Stop existing progress bar if any
        if self._progress_bar and self._progress_bar.is_active():
            self.finish_progress()
        
        # Stop spinner if active
        if self._spinner and self._spinner.is_active():
            self._spinner.stop()
            self._spinner = None
        
        # Create and start a new progress bar
        self._progress_bar = ProgressBar(total, prefix, suffix, bar_length, 
                                        self._use_colors, show_eta)
        self._progress_bar.start()
    
    def update_progress(self, current: float, suffix: typing.Optional[str] = None) -> None:
        """
        Updates the active progress bar with a new value.
        
        Args:
            current: Current progress value
            suffix: Optional new suffix text
        """
        if not self._progress_bar:
            self._logger.warning("No active progress bar")
            return
        
        self._progress_bar.update(current, suffix)
    
    def finish_progress(self) -> None:
        """
        Completes the active progress bar.
        """
        if not self._progress_bar:
            self._logger.warning("No active progress bar")
            return
        
        self._progress_bar.finish()
        self._progress_bar = None
    
    def start_spinner(self, message: str) -> None:
        """
        Starts an indeterminate progress spinner for operations with unknown duration.
        
        Args:
            message: Message to display alongside the spinner
        """
        # Stop existing spinner if any
        if self._spinner and self._spinner.is_active():
            self._spinner.stop()
        
        # Stop progress bar if active
        if self._progress_bar and self._progress_bar.is_active():
            self.finish_progress()
        
        # Create and start a new spinner
        self._spinner = IndeterminateProgressBar(message, self._use_colors)
        self._spinner.start()
    
    def update_spinner_message(self, message: str) -> None:
        """
        Updates the message displayed with the active spinner.
        
        Args:
            message: New message to display
        """
        if not self._spinner:
            self._logger.warning("No active spinner")
            return
        
        self._spinner.update_message(message)
    
    def stop_spinner(self) -> None:
        """
        Stops the active progress spinner.
        """
        if not self._spinner:
            self._logger.warning("No active spinner")
            return
        
        self._spinner.stop()
        self._spinner = None
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Sets the verbose mode for the logger.
        
        Args:
            verbose: Whether to enable verbose mode
        """
        self._verbose = verbose
        self._handler.set_verbose(verbose)
    
    def set_use_colors(self, use_colors: bool) -> None:
        """
        Sets whether to use colors in log output.
        
        Args:
            use_colors: Whether to use colors
        """
        self._use_colors = use_colors
        self._handler.set_use_colors(use_colors)
    
    def is_verbose(self) -> bool:
        """
        Returns whether verbose mode is enabled.
        
        Returns:
            bool: True if verbose mode is enabled, False otherwise
        """
        return self._verbose