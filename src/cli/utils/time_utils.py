"""
Provides time-related utility functions for the CLI component of the JSON to Excel Conversion Tool.
This module includes tools for measuring execution time, formatting time durations, and tracking
performance metrics to provide users with meaningful timing information during the conversion process.
"""

import time  # v: built-in
import typing  # v: built-in
import contextlib  # v: built-in

from ...backend.logger import get_logger
from .console_utils import format_time

# Initialize logger
logger = get_logger(__name__)


def time_function(func: typing.Callable) -> typing.Callable:
    """
    Decorator that measures and logs the execution time of a function.
    
    Args:
        func: The function to time
        
    Returns:
        Wrapped function that measures execution time
    """
    def wrapper(*args, **kwargs):
        # Record start time
        start_time = time.time()
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Log the execution time
        logger.debug(f"Function {func.__name__} executed in {format_elapsed_time(elapsed_time)}")
        
        return result
    
    return wrapper


def get_current_time() -> float:
    """
    Gets the current time in seconds since the epoch.
    
    Returns:
        Current time in seconds
    """
    return time.time()


def calculate_elapsed_time(start_time: float) -> float:
    """
    Calculates the elapsed time between a start time and the current time.
    
    Args:
        start_time: Starting time in seconds
        
    Returns:
        Elapsed time in seconds
    """
    current_time = time.time()
    return current_time - start_time


def format_elapsed_time(elapsed_seconds: float) -> str:
    """
    Formats an elapsed time in seconds to a human-readable string.
    
    Args:
        elapsed_seconds: Time in seconds
        
    Returns:
        Formatted time string (e.g., '5.2s', '120ms')
    """
    return format_time(elapsed_seconds)


@contextlib.contextmanager
def timing_context(operation_name: str):
    """
    Creates a context manager for timing a block of code.
    
    Args:
        operation_name: Name of the operation being timed
        
    Yields:
        None
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.debug(f"Operation '{operation_name}' completed in {format_elapsed_time(elapsed_time)}")


class ExecutionTimer:
    """
    A context manager class for measuring and reporting execution time of code blocks.
    """
    
    def __init__(self, name: str = "ExecutionTimer"):
        """
        Initializes a new ExecutionTimer instance with an optional name.
        
        Args:
            name: Name for this timer (used in logging)
        """
        self._name = name
        self._start_time = None
        self._end_time = None
        self._running = False
    
    def __enter__(self) -> 'ExecutionTimer':
        """
        Enters the context and starts the timer.
        
        Returns:
            Self reference
        """
        self._start_time = time.time()
        self._running = True
        return self
    
    def __exit__(self, exc_type: typing.Optional[typing.Type[Exception]], 
                exc_val: typing.Optional[Exception], 
                exc_tb: typing.Optional[typing.TracebackType]) -> bool:
        """
        Exits the context, stops the timer, and logs the elapsed time.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            False to propagate exceptions
        """
        self._end_time = time.time()
        self._running = False
        
        # Log the elapsed time
        logger.debug(f"Timer '{self._name}' completed in {self.elapsed_formatted()}")
        
        # Return False to propagate any exceptions
        return False
    
    def start(self) -> 'ExecutionTimer':
        """
        Starts the timer manually (alternative to using with statement).
        
        Returns:
            Self reference for method chaining
        """
        self._start_time = time.time()
        self._running = True
        return self
    
    def stop(self) -> float:
        """
        Stops the timer manually and returns the elapsed time.
        
        Returns:
            Elapsed time in seconds
            
        Raises:
            ValueError: If the timer is not running
        """
        if not self._running:
            raise ValueError("Timer is not running")
        
        self._end_time = time.time()
        self._running = False
        return self.elapsed()
    
    def reset(self) -> 'ExecutionTimer':
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
        if self._start_time is None:
            return 0.0
        
        if self._running:
            # Timer is still running, calculate time between start and now
            return time.time() - self._start_time
        else:
            # Timer has stopped, use the recorded end time
            return self._end_time - self._start_time
    
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


class OperationTimingTracker:
    """
    Tracks and stores timing information for multiple operations.
    """
    
    def __init__(self):
        """
        Initializes a new OperationTimingTracker instance.
        """
        self._timings = {}
    
    def record_timing(self, operation_name: str, execution_time: float) -> None:
        """
        Records a timing measurement for a specific operation.
        
        Args:
            operation_name: Name of the operation
            execution_time: Execution time in seconds
        """
        if operation_name not in self._timings:
            self._timings[operation_name] = []
        
        self._timings[operation_name].append(execution_time)
        logger.debug(f"Recorded timing for '{operation_name}': {format_elapsed_time(execution_time)}")
    
    def get_average_timing(self, operation_name: str) -> typing.Optional[float]:
        """
        Gets the average execution time for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Average execution time or None if no timings exist
        """
        if operation_name in self._timings and self._timings[operation_name]:
            return sum(self._timings[operation_name]) / len(self._timings[operation_name])
        return None
    
    def get_timing_summary(self) -> typing.Dict[str, typing.Dict[str, float]]:
        """
        Gets a summary of timing statistics for all tracked operations.
        
        Returns:
            Dictionary of operation timing statistics
        """
        summary = {}
        
        for operation, timings in self._timings.items():
            if not timings:
                continue
                
            summary[operation] = {
                "min": min(timings),
                "max": max(timings),
                "avg": sum(timings) / len(timings),
                "count": len(timings)
            }
        
        return summary
    
    def reset(self) -> None:
        """
        Resets all timing measurements.
        """
        self._timings = {}
        logger.debug("Operation timing tracker reset")
    
    @contextlib.contextmanager
    def time_operation(self, operation_name: str):
        """
        Context manager method for timing an operation.
        
        Args:
            operation_name: Name of the operation being timed
            
        Yields:
            None
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            self.record_timing(operation_name, elapsed_time)