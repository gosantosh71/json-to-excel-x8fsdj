"""
Provides utility functions for console output formatting and user interaction in the CLI component 
of the JSON to Excel Conversion Tool. This module handles colored text output, progress indicators, 
user prompts, and formatting of various data types for display in the terminal.
"""

import os  # v: built-in
import sys  # v: built-in
import time  # v: built-in
import typing  # v: built-in
import shutil  # v: built-in
import threading  # v: built-in
import math  # v: built-in

from ...backend.logger import get_logger
from ..models.cli_response import CLIResponse, ResponseType
from ...backend.models.error_response import ErrorResponse

# Initialize logger
logger = get_logger(__name__)

# ANSI color codes
COLORS = {
    "RESET": "\033[0m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}

# Spinner animation frames
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# Progress bar characters
PROGRESS_BAR_CHARS = {
    "start": "[",
    "end": "]",
    "fill": "=",
    "empty": " "
}

# File size units
SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"]

# Time units
TIME_UNITS = ["s", "ms", "μs", "ns"]


def is_color_supported() -> bool:
    """
    Determines if the current terminal supports ANSI color codes.
    
    Returns:
        bool: True if colors are supported, False otherwise
    """
    # Check environment variables first
    if os.environ.get("NO_COLOR"):
        return False
    
    if os.environ.get("FORCE_COLOR"):
        return True
    
    # Check if stdout is a TTY
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    
    # Platform-specific checks
    if is_tty:
        if sys.platform == "win32":
            # Windows 10 build 14393+ supports ANSI colors via VT100
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.GetConsoleMode(kernel32.GetStdHandle(-11)) & 0x0004 != 0
            except (ImportError, AttributeError):
                return False
        else:
            # Unix-like platforms generally support ANSI colors
            return True
    
    return False


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Applies ANSI color codes to a string if color is supported.
    
    Args:
        text: The text to colorize
        color: The color to apply (a key from the COLORS dictionary)
        bold: Whether to make the text bold
        
    Returns:
        str: Colorized string if supported, original string otherwise
    """
    if not is_color_supported():
        return text
    
    if color not in COLORS:
        logger.warning(f"Unsupported color: {color}")
        return text
    
    result = COLORS[color] + text
    
    if bold:
        result = COLORS["BOLD"] + result
        
    # Ensure the string ends with a reset code
    if not result.endswith(COLORS["RESET"]):
        result += COLORS["RESET"]
        
    return result


def get_terminal_size() -> typing.Tuple[int, int]:
    """
    Gets the current terminal size (width, height).
    
    Returns:
        tuple: (width, height) in characters
    """
    try:
        # Use shutil for reliable cross-platform size detection
        columns, lines = shutil.get_terminal_size()
        return columns, lines
    except (AttributeError, ValueError, OSError):
        # Fallback to environment variables
        try:
            columns = int(os.environ.get("COLUMNS", 80))
            lines = int(os.environ.get("LINES", 24))
            return columns, lines
        except (ValueError, TypeError):
            # Default if all else fails
            return 80, 24


def clear_line() -> None:
    """
    Clears the current line in the terminal.
    """
    if is_color_supported():
        # Use ANSI escape sequence to clear the line
        print("\r\033[K", end="", flush=True)
    else:
        # Fallback for terminals without ANSI support
        width = get_terminal_size()[0]
        print("\r" + " " * width + "\r", end="", flush=True)


def print_message(message: str, color: str = None, bold: bool = False, end_line: bool = True) -> None:
    """
    Prints a message to the console with optional formatting.
    
    Args:
        message: The message to print
        color: Optional color to apply (a key from the COLORS dictionary)
        bold: Whether to make the text bold
        end_line: Whether to end with a newline
    """
    if color:
        message = colorize(message, color, bold)
        
    print(message, end="\n" if end_line else "", flush=True)


def print_success(message: str) -> None:
    """
    Prints a success message to the console.
    
    Args:
        message: The success message to print
    """
    message = f"[✓] {message}" if is_color_supported() else f"[SUCCESS] {message}"
    print_message(message, "GREEN")


def print_error(message: str) -> None:
    """
    Prints an error message to the console.
    
    Args:
        message: The error message to print
    """
    message = f"[!] {message}" if is_color_supported() else f"[ERROR] {message}"
    print_message(message, "RED")


def print_warning(message: str) -> None:
    """
    Prints a warning message to the console.
    
    Args:
        message: The warning message to print
    """
    message = f"[!] {message}" if is_color_supported() else f"[WARNING] {message}"
    print_message(message, "YELLOW")


def print_info(message: str) -> None:
    """
    Prints an informational message to the console.
    
    Args:
        message: The informational message to print
    """
    message = f"[i] {message}" if is_color_supported() else f"[INFO] {message}"
    print_message(message, "BLUE")


def print_processing(message: str) -> None:
    """
    Prints a processing status message to the console.
    
    Args:
        message: The processing message to print
    """
    message = f"[*] {message}" if is_color_supported() else f"[PROCESSING] {message}"
    print_message(message, "CYAN")


def print_cli_response(response: CLIResponse) -> None:
    """
    Prints a CLIResponse object to the console with appropriate formatting.
    
    Args:
        response: The CLIResponse object to print
    """
    formatted_output = response.get_formatted_output()
    
    if response.response_type == ResponseType.SUCCESS:
        print_success(formatted_output)
    elif response.response_type == ResponseType.ERROR:
        print_error(formatted_output)
    elif response.response_type == ResponseType.WARNING:
        print_warning(formatted_output)
    elif response.response_type == ResponseType.INFO:
        print_info(formatted_output)
    else:
        # Fallback for unhandled response types
        print_message(formatted_output)


def update_progress_bar(current: float, total: float, prefix: str = "", suffix: str = "", 
                        bar_length: int = 50, use_colors: bool = True) -> None:
    """
    Displays and updates a progress bar in the console.
    
    Args:
        current: Current progress value
        total: Total value for 100% completion
        prefix: Text to display before the progress bar
        suffix: Text to display after the progress bar
        bar_length: Length of the progress bar in characters
        use_colors: Whether to use colors for the progress bar
    """
    # Calculate percentage
    percent = (current / total) * 100 if total > 0 else 0
    
    # Calculate filled and empty bar segments
    filled_length = int(bar_length * current // total)
    empty_length = bar_length - filled_length
    
    # Create the progress bar
    bar = (
        PROGRESS_BAR_CHARS["start"] + 
        PROGRESS_BAR_CHARS["fill"] * filled_length + 
        PROGRESS_BAR_CHARS["empty"] * empty_length + 
        PROGRESS_BAR_CHARS["end"]
    )
    
    # Format the complete progress line
    progress_line = f"\r{prefix} {bar} {percent:.1f}% {suffix}"
    
    # Apply colors if supported and requested
    if use_colors and is_color_supported():
        if percent < 30:
            bar_color = "RED"
        elif percent < 70:
            bar_color = "YELLOW"
        else:
            bar_color = "GREEN"
        
        colored_bar = (
            PROGRESS_BAR_CHARS["start"] + 
            colorize(PROGRESS_BAR_CHARS["fill"] * filled_length, bar_color) + 
            PROGRESS_BAR_CHARS["empty"] * empty_length + 
            PROGRESS_BAR_CHARS["end"]
        )
        
        progress_line = f"\r{prefix} {colored_bar} {percent:.1f}% {suffix}"
    
    # Clear the current line and print the progress bar
    clear_line()
    print(progress_line, end="", flush=True)


def prompt_user(prompt: str, default: str = None) -> str:
    """
    Prompts the user for input with an optional default value.
    
    Args:
        prompt: The prompt message to display
        default: Optional default value to use if user provides no input
        
    Returns:
        str: User input or default value
    """
    display_prompt = prompt
    
    if default is not None:
        display_prompt = f"{prompt} [{default}]"
        
    user_input = input(f"{display_prompt}: ")
    
    if user_input == "" and default is not None:
        return default
        
    return user_input


def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """
    Prompts the user for a yes/no response.
    
    Args:
        prompt: The prompt message to display
        default: The default response (True for yes, False for no)
        
    Returns:
        bool: True for yes, False for no
    """
    if default:
        prompt_suffix = " [Y/n]"
    else:
        prompt_suffix = " [y/N]"
        
    response = prompt_user(f"{prompt}{prompt_suffix}", "y" if default else "n")
    
    # Convert to lowercase and check first character
    response = response.lower()[0] if response else ("y" if default else "n")
    
    return response == "y"


def format_file_size(size_bytes: int) -> str:
    """
    Formats a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: The file size in bytes
        
    Returns:
        str: Formatted file size string (e.g., '5.2 MB')
    """
    if size_bytes == 0:
        return "0 B"
    
    # Calculate the appropriate unit index (log base 1024)
    unit_index = min(4, int(math.log(size_bytes, 1024)))
    
    # Calculate the size in the selected unit
    size_value = size_bytes / (1024 ** unit_index)
    
    # Format with 1 decimal place and the unit
    return f"{size_value:.1f} {SIZE_UNITS[unit_index]}"


def format_time(seconds: float) -> str:
    """
    Formats a time duration in seconds to a human-readable string.
    
    Args:
        seconds: The time in seconds
        
    Returns:
        str: Formatted time string (e.g., '5.2s', '120ms')
    """
    if seconds is None:
        return "N/A"
    
    if seconds >= 1:
        # Format as seconds with 1 decimal place
        return f"{seconds:.1f}s"
    elif seconds >= 0.001:
        # Format as milliseconds
        ms = seconds * 1000
        return f"{ms:.1f}ms"
    elif seconds >= 0.000001:
        # Format as microseconds
        us = seconds * 1000000
        return f"{us:.1f}μs"
    else:
        # Format as nanoseconds
        ns = seconds * 1000000000
        return f"{ns:.1f}ns"


class ProgressSpinner:
    """
    A class that displays an animated spinner for indicating ongoing processing.
    """
    
    def __init__(self, message: str = "", use_colors: bool = None):
        """
        Initializes a new ProgressSpinner instance.
        
        Args:
            message: Message to display alongside the spinner
            use_colors: Whether to use colors (defaults to terminal capability)
        """
        self._message = message
        self._frames = SPINNER_FRAMES
        self._current_frame = 0
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        self._active = False
        self._update_thread = None
        self._stop_event = threading.Event()
    
    def start(self) -> 'ProgressSpinner':
        """
        Starts the spinner animation.
        
        Returns:
            ProgressSpinner: Self reference for method chaining
        """
        if self._active:
            return self
        
        self._active = True
        self._stop_event.clear()
        
        # Create a daemon thread for the animation
        self._update_thread = threading.Thread(
            target=self._update_animation,
            daemon=True
        )
        self._update_thread.start()
        
        return self
    
    def stop(self) -> None:
        """
        Stops the spinner animation.
        """
        if not self._active:
            return
        
        self._stop_event.set()
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)
        
        clear_line()
        self._active = False
    
    def update(self) -> None:
        """
        Updates the spinner (advances to the next frame).
        """
        if not self._active:
            return
        
        self._current_frame = (self._current_frame + 1) % len(self._frames)
    
    def update_message(self, message: str) -> None:
        """
        Updates the message displayed with the spinner.
        
        Args:
            message: New message to display
        """
        self._message = message
    
    def _update_animation(self) -> None:
        """
        Background thread method that updates the animation frames.
        """
        while not self._stop_event.is_set():
            # Clear the current line
            clear_line()
            
            # Get the current animation frame
            frame = self._frames[self._current_frame]
            
            # Apply color if supported
            if self._use_colors:
                frame = colorize(frame, "CYAN")
            
            # Print the spinner frame and message
            print(f"\r{frame} {self._message}", end="", flush=True)
            
            # Move to the next frame
            self._current_frame = (self._current_frame + 1) % len(self._frames)
            
            # Sleep briefly
            time.sleep(0.1)
            
            # Check if we should stop
            if self._stop_event.is_set():
                break
    
    def is_active(self) -> bool:
        """
        Returns whether the spinner is currently active.
        
        Returns:
            bool: True if the spinner is active, False otherwise
        """
        return self._active