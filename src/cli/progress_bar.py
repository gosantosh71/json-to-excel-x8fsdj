"""
Implements progress bar and spinner components for the CLI interface of the JSON to Excel Conversion Tool.
This module provides visual feedback during conversion operations, including determinate progress bars
for operations with known duration and indeterminate spinners for operations with unknown duration.
"""

import sys  # v: built-in
import time  # v: built-in
import threading  # v: built-in
from typing import Optional  # v: built-in

from ..backend.logger import get_logger
from .utils.console_utils import (
    is_color_supported,
    clear_line,
    get_terminal_size,
    colorize
)
from .utils.time_utils import format_time

# Initialize logger
logger = get_logger(__name__)

# Constants for progress bar rendering
PROGRESS_BAR_CHARS = {"start": "[", "end": "]", "fill": "=", "empty": " "}

# Spinner animation frames (braille patterns)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# Default progress bar length in characters
DEFAULT_BAR_LENGTH = 40

# Default refresh rate for animations in seconds
DEFAULT_REFRESH_RATE = 0.1


class ProgressBar:
    """
    A class that displays and updates a progress bar in the console for operations with known duration.
    """

    def __init__(
        self,
        total: float,
        prefix: str = "Progress:",
        suffix: str = "",
        bar_length: int = DEFAULT_BAR_LENGTH,
        use_colors: bool = None,
        show_eta: bool = True
    ):
        """
        Initializes a new ProgressBar instance with the specified parameters.

        Args:
            total: Total value representing 100% completion
            prefix: Text displayed before the progress bar
            suffix: Text displayed after the progress bar
            bar_length: Length of the progress bar in characters
            use_colors: Whether to use colors for the progress bar (auto-detect if None)
            show_eta: Whether to show ETA information
        """
        if total <= 0:
            raise ValueError("Total value must be greater than 0")
            
        self._total = total
        self._current = 0.0
        self._prefix = prefix
        self._suffix = suffix
        self._bar_length = bar_length
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        self._show_eta = show_eta
        self._start_time = None
        self._active = False

    def start(self) -> 'ProgressBar':
        """
        Starts the progress bar display.
        
        Returns:
            Returns self for method chaining
        """
        if self._active:
            logger.warning("Progress bar is already active")
            return self
            
        self._active = True
        self._start_time = time.time()
        
        # Display initial progress bar (0%)
        self.update(0.0)
        
        return self

    def update(self, current: float, suffix: Optional[str] = None) -> 'ProgressBar':
        """
        Updates the progress bar with a new value.
        
        Args:
            current: Current progress value (between 0 and total)
            suffix: Optional new suffix text to display
            
        Returns:
            Returns self for method chaining
        """
        if not self._active:
            logger.warning("Progress bar is not active")
            return self
            
        # Clamp current value between 0 and total
        self._current = max(0.0, min(current, self._total))
        
        # Update suffix if provided
        if suffix is not None:
            self._suffix = suffix
            
        # Clear the current line and print the updated bar
        clear_line()
        print(self._render_progress_bar(), end="", flush=True)
        
        return self

    def finish(self) -> None:
        """
        Completes the progress bar (sets to 100%) and adds a newline.
        """
        if not self._active:
            logger.warning("Progress bar is not active")
            return
            
        # Update to 100%
        self.update(self._total)
        
        # Add a newline to move to the next line
        print()
        
        self._active = False

    def is_active(self) -> bool:
        """
        Returns whether the progress bar is currently active.
        
        Returns:
            True if the progress bar is active, False otherwise
        """
        return self._active

    def _calculate_eta(self) -> str:
        """
        Calculates the estimated time remaining based on progress.
        
        Returns:
            Formatted ETA string
        """
        if self._start_time is None or self._current <= 0:
            return "calculating..."
            
        # Calculate elapsed time
        elapsed = time.time() - self._start_time
        
        # Calculate progress ratio
        progress_ratio = self._current / self._total
        
        # Avoid division by zero
        if progress_ratio <= 0:
            return "calculating..."
            
        # Estimate total time
        total_time = elapsed / progress_ratio
        
        # Calculate remaining time
        remaining = total_time - elapsed
        
        # Format remaining time
        return format_time(remaining)

    def _render_progress_bar(self) -> str:
        """
        Renders the progress bar string based on current progress.
        
        Returns:
            Formatted progress bar string
        """
        # Calculate percentage and render progress bar
        percent = (self._current / self._total) * 100
        filled_length = int(self._bar_length * self._current // self._total)
        empty_length = self._bar_length - filled_length
        
        # Construct the bar with start, fill, empty, and end characters
        bar = (
            PROGRESS_BAR_CHARS["start"] + 
            PROGRESS_BAR_CHARS["fill"] * filled_length + 
            PROGRESS_BAR_CHARS["empty"] * empty_length + 
            PROGRESS_BAR_CHARS["end"]
        )
        
        # Apply color to the filled portion if colors are enabled
        if self._use_colors:
            if percent < 30:
                color = "RED"
            elif percent < 70:
                color = "YELLOW"
            else:
                color = "GREEN"
                
            colored_fill = colorize(PROGRESS_BAR_CHARS["fill"] * filled_length, color)
            bar = (
                PROGRESS_BAR_CHARS["start"] + 
                colored_fill + 
                PROGRESS_BAR_CHARS["empty"] * empty_length + 
                PROGRESS_BAR_CHARS["end"]
            )
        
        # Format the complete progress line
        progress_line = f"\r{self._prefix} {bar} {percent:.1f}% {self._suffix}"
        
        # Add ETA if enabled
        if self._show_eta and self._start_time is not None:
            eta = self._calculate_eta()
            progress_line += f" (ETA: {eta})"
            
        return progress_line


class IndeterminateProgressBar:
    """
    A class that displays an animated spinner for operations with unknown duration.
    """

    def __init__(
        self,
        message: str = "Processing...",
        use_colors: bool = None,
        refresh_rate: float = DEFAULT_REFRESH_RATE
    ):
        """
        Initializes a new IndeterminateProgressBar instance.
        
        Args:
            message: Message to display alongside the spinner
            use_colors: Whether to use colors for the spinner (auto-detect if None)
            refresh_rate: Time between animation frames in seconds
        """
        self._message = message
        self._frames = SPINNER_FRAMES
        self._current_frame = 0
        self._use_colors = is_color_supported() if use_colors is None else use_colors
        self._active = False
        self._update_thread = None
        self._stop_event = threading.Event()
        self._refresh_rate = refresh_rate

    def start(self) -> 'IndeterminateProgressBar':
        """
        Starts the spinner animation.
        
        Returns:
            Returns self for method chaining
        """
        if self._active:
            logger.warning("Spinner is already active")
            return self
            
        self._active = True
        self._stop_event.clear()
        
        # Create and start a background thread for animation
        self._update_thread = threading.Thread(
            target=self._update_animation,
            daemon=True
        )
        self._update_thread.start()
        
        return self

    def stop(self, clear: bool = True) -> None:
        """
        Stops the spinner animation.
        
        Args:
            clear: Whether to clear the spinner from the console
        """
        if not self._active:
            logger.warning("Spinner is not active")
            return
            
        self._stop_event.set()
        
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join()
            
        if clear:
            clear_line()
        else:
            # Add a newline to move to the next line
            print()
            
        self._active = False

    def update_message(self, message: str) -> None:
        """
        Updates the message displayed with the spinner.
        
        Args:
            message: New message to display
        """
        self._message = message

    def is_active(self) -> bool:
        """
        Returns whether the spinner is currently active.
        
        Returns:
            True if the spinner is active, False otherwise
        """
        return self._active

    def _update_animation(self) -> None:
        """
        Background thread method that updates the animation frames.
        """
        while not self._stop_event.is_set():
            # Clear the current line
            clear_line()
            
            # Get the current animation frame
            frame = self._frames[self._current_frame]
            
            # Format display with frame and message
            display = f"\r{frame} {self._message}"
            
            # Apply color to the spinner frame if colors are enabled
            if self._use_colors:
                colored_frame = colorize(frame, "CYAN")
                display = f"\r{colored_frame} {self._message}"
                
            # Print the formatted display
            print(display, end="", flush=True)
            
            # Increment frame index (cycling through frames)
            self._current_frame = (self._current_frame + 1) % len(self._frames)
            
            # Sleep for refresh_rate seconds
            time.sleep(self._refresh_rate)
            
            # Check if we should stop
            if self._stop_event.is_set():
                break