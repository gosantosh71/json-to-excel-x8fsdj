"""
Provides time-related utility functions and classes for the web interface of the JSON to Excel Conversion Tool.

This module includes tools for measuring execution time, tracking progress, formatting time durations,
and providing timing information for conversion operations and API responses.
"""

import time  # v: built-in
import datetime  # v: built-in
import typing  # v: built-in
import functools  # v: built-in
import asyncio  # v: built-in
import contextlib  # v: built-in

from ../../backend/logger import get_logger
from ../../backend/monitoring/performance_tracker import performance_tracker

# Initialize logger for this module
logger = get_logger(__name__)


def get_current_timestamp(format_string: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Gets the current timestamp as a formatted string.
    
    Args:
        format_string: Format string for the timestamp (default: '%Y-%m-%d %H:%M:%S')
        
    Returns:
        Formatted timestamp string
    """
    return datetime.datetime.now().strftime(format_string)


def get_iso_timestamp() -> str:
    """
    Gets the current timestamp in ISO 8601 format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.datetime.now().isoformat()


@contextlib.contextmanager
def measure_execution_time(operation_name: str):
    """
    Context manager for measuring the execution time of a code block.
    
    Args:
        operation_name: Name of the operation being timed
        
    Yields:
        Context manager for timing code
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"{operation_name} completed in {elapsed_time:.6f} seconds")
        performance_tracker.add_metric("WebInterface", operation_name, elapsed_time)


def time_function(operation_name: typing.Optional[str] = None):
    """
    Decorator that measures and logs the execution time of a function.
    
    Args:
        operation_name: Optional name for the operation (defaults to function name)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        nonlocal operation_name
        if operation_name is None:
            operation_name = func.__name__
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            logger.info(f"{operation_name} completed in {elapsed_time:.6f} seconds")
            performance_tracker.add_metric("WebInterface", operation_name, elapsed_time)
            
            return result
        return wrapper
    return decorator


def async_time_function(operation_name: typing.Optional[str] = None):
    """
    Decorator that measures and logs the execution time of an async function.
    
    Args:
        operation_name: Optional name for the operation (defaults to function name)
        
    Returns:
        Async decorator function
    """
    def decorator(func):
        nonlocal operation_name
        if operation_name is None:
            operation_name = func.__name__
            
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            logger.info(f"{operation_name} completed in {elapsed_time:.6f} seconds")
            performance_tracker.add_metric("WebInterface", operation_name, elapsed_time)
            
            return result
        return wrapper
    return decorator


def format_elapsed_time(elapsed_seconds: float) -> str:
    """
    Formats an elapsed time in seconds to a human-readable string.
    
    Args:
        elapsed_seconds: Time in seconds
        
    Returns:
        Formatted time string (e.g., '5.2s', '120ms')
    """
    if elapsed_seconds < 0.001:
        return f"{elapsed_seconds * 1000000:.0f}μs"
    elif elapsed_seconds < 1:
        return f"{elapsed_seconds * 1000:.0f}ms"
    else:
        return f"{elapsed_seconds:.1f}s"


class Timer:
    """
    A class for measuring elapsed time with start/stop functionality.
    """
    
    def __init__(self):
        """
        Initializes a new Timer instance.
        """
        self._start_time = None
        self._end_time = None
        self._running = False
    
    def start(self) -> 'Timer':
        """
        Starts the timer.
        
        Returns:
            Self reference for method chaining
        """
        self._start_time = time.time()
        self._running = True
        return self
    
    def stop(self) -> float:
        """
        Stops the timer and returns the elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if not self._running:
            raise ValueError("Timer is not running")
            
        self._end_time = time.time()
        self._running = False
        return self.elapsed()
    
    def reset(self) -> 'Timer':
        """
        Resets the timer to its initial state.
        
        Returns:
            Self reference for method chaining
        """
        self._start_time = None
        self._end_time = None
        self._running = False
        return self
    
    def elapsed(self) -> float:
        """
        Gets the elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        if self._running:
            # Timer is still running, calculate from start time to now
            return time.time() - self._start_time
        elif self._start_time and self._end_time:
            # Timer has been stopped, calculate from start to end
            return self._end_time - self._start_time
        else:
            # Timer hasn't been started
            return 0
    
    def elapsed_formatted(self) -> str:
        """
        Gets the elapsed time as a formatted string.
        
        Returns:
            Formatted elapsed time string
        """
        return format_elapsed_time(self.elapsed())
    
    def is_running(self) -> bool:
        """
        Checks if the timer is currently running.
        
        Returns:
            True if the timer is running, False otherwise
        """
        return self._running


class ExecutionTimer:
    """
    A context manager for timing code execution.
    """
    
    def __init__(self, name: str = 'ExecutionTimer'):
        """
        Initializes a new ExecutionTimer instance with an optional name.
        
        Args:
            name: Name for the timer for identification in logs
        """
        self._name = name
        self._timer = Timer()
    
    def __enter__(self) -> 'ExecutionTimer':
        """
        Enters the context and starts the timer.
        
        Returns:
            Self reference
        """
        self._timer.start()
        return self
    
    def __exit__(self, exc_type: typing.Optional[typing.Type[Exception]], 
                exc_val: typing.Optional[Exception], 
                exc_tb: typing.Optional[typing.TracebackType]) -> bool:
        """
        Exits the context, stops the timer, and logs the elapsed time.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
            
        Returns:
            False to propagate exceptions
        """
        elapsed_time = self._timer.stop()
        logger.info(f"{self._name} completed in {elapsed_time:.6f} seconds")
        performance_tracker.add_metric("WebInterface", self._name, elapsed_time)
        return False  # Propagate exceptions
    
    def elapsed(self) -> float:
        """
        Gets the elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        return self._timer.elapsed()
    
    def elapsed_formatted(self) -> str:
        """
        Gets the elapsed time as a formatted string.
        
        Returns:
            Formatted elapsed time string
        """
        return self._timer.elapsed_formatted()


class AsyncExecutionTimer:
    """
    An async context manager for timing async code execution.
    """
    
    def __init__(self, name: str = 'AsyncExecutionTimer'):
        """
        Initializes a new AsyncExecutionTimer instance with an optional name.
        
        Args:
            name: Name for the timer for identification in logs
        """
        self._name = name
        self._timer = Timer()
    
    async def __aenter__(self) -> 'AsyncExecutionTimer':
        """
        Enters the async context and starts the timer.
        
        Returns:
            Self reference
        """
        self._timer.start()
        return self
    
    async def __aexit__(self, exc_type: typing.Optional[typing.Type[Exception]], 
                      exc_val: typing.Optional[Exception], 
                      exc_tb: typing.Optional[typing.TracebackType]) -> bool:
        """
        Exits the async context, stops the timer, and logs the elapsed time.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
            
        Returns:
            False to propagate exceptions
        """
        elapsed_time = self._timer.stop()
        logger.info(f"{self._name} completed in {elapsed_time:.6f} seconds")
        performance_tracker.add_metric("WebInterface", self._name, elapsed_time)
        return False  # Propagate exceptions
    
    def elapsed(self) -> float:
        """
        Gets the elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        return self._timer.elapsed()
    
    def elapsed_formatted(self) -> str:
        """
        Gets the elapsed time as a formatted string.
        
        Returns:
            Formatted elapsed time string
        """
        return self._timer.elapsed_formatted()


class ProgressTracker:
    """
    A class for tracking progress of operations with time estimation.
    """
    
    def __init__(self):
        """
        Initializes a new ProgressTracker instance.
        """
        self._start_time = time.time()
        self._current_progress = 0.0  # 0 to 1.0
        self._current_stage = ""
        self._stage_progress = {}
    
    def update(self, progress: float, stage: typing.Optional[str] = None) -> None:
        """
        Updates the progress tracker with a new progress value and optional stage.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            stage: Optional current stage name
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
            
        self._current_progress = progress
        
        if stage is not None:
            self._current_stage = stage
            self._stage_progress[stage] = progress
            
        stage_info = f" ({self._current_stage})" if self._current_stage else ""
        logger.debug(f"Progress updated: {progress:.1%}{stage_info}")
    
    def set_progress(self, percentage: float, stage: typing.Optional[str] = None) -> None:
        """
        Sets the current progress as a percentage value.
        
        Args:
            percentage: Progress percentage between 0 and 100
            stage: Optional current stage name
        """
        self.update(percentage / 100.0, stage)
    
    def get_progress(self) -> float:
        """
        Gets the current progress as a percentage value.
        
        Returns:
            Current progress as percentage (0-100)
        """
        return self._current_progress * 100.0
    
    def get_eta(self) -> typing.Optional[float]:
        """
        Estimates the time remaining to completion in seconds.
        
        Returns:
            Estimated time remaining in seconds, or None if progress is 0
        """
        if self._current_progress <= 0:
            return None
            
        elapsed = self.get_elapsed()
        total_time_estimate = elapsed / self._current_progress
        remaining = total_time_estimate - elapsed
        
        return max(0, remaining)  # Ensure non-negative
    
    def get_eta_formatted(self) -> str:
        """
        Gets the estimated time remaining as a formatted string.
        
        Returns:
            Formatted ETA string or 'Calculating...' if not available
        """
        eta = self.get_eta()
        if eta is None:
            return "Calculating..."
        return format_elapsed_time(eta)
    
    def get_elapsed(self) -> float:
        """
        Gets the elapsed time since tracking started in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        return time.time() - self._start_time
    
    def get_elapsed_formatted(self) -> str:
        """
        Gets the elapsed time as a formatted string.
        
        Returns:
            Formatted elapsed time string
        """
        return format_elapsed_time(self.get_elapsed())
    
    def get_status_dict(self) -> dict:
        """
        Gets a dictionary with the current status information.
        
        Returns:
            Dictionary with progress, stage, elapsed, and ETA information
        """
        eta = self.get_eta()
        
        return {
            "progress": self.get_progress(),
            "stage": self._current_stage,
            "elapsed": self.get_elapsed(),
            "elapsed_formatted": self.get_elapsed_formatted(),
            "eta": eta,
            "eta_formatted": self.get_eta_formatted(),
            "stage_progress": self._stage_progress
        }