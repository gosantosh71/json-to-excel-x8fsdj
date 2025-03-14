"""
Provides performance tracking capabilities for the JSON to Excel Conversion Tool.

This module enables monitoring of execution times, memory usage, and performance metrics
across different components of the application, helping identify bottlenecks and ensure
optimal performance.
"""

import time  # v: built-in
import functools  # v: built-in
import psutil  # v: 5.9.0+
import typing  # v: built-in
import contextlib  # v: built-in
from dataclasses import dataclass  # v: built-in

from ..logger import get_logger
from ..constants import PERFORMANCE_CONSTANTS
from ..utils import Timer

# Initialize logger for this module
logger = get_logger(__name__)


def get_current_memory_usage() -> float:
    """
    Gets the current memory usage of the process in megabytes.
    
    Returns:
        Current memory usage in megabytes
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    # Convert from bytes to megabytes
    memory_usage_mb = memory_info.rss / (1024 * 1024)
    return memory_usage_mb


@dataclass
class PerformanceMetric:
    """
    Represents a single performance measurement with component, operation, and timing data.
    """
    component: str
    operation: str
    duration: float
    timestamp: float = None
    metadata: dict = None
    
    def __init__(self, component: str, operation: str, duration: float, metadata: dict = None):
        """
        Initializes a new PerformanceMetric instance.
        
        Args:
            component: The component being measured (e.g., 'JSONParser')
            operation: The operation being performed (e.g., 'parse_json')
            duration: The time taken to complete the operation in seconds
            metadata: Optional dictionary with additional information about the operation
        """
        self.component = component
        self.operation = operation
        self.duration = duration
        self.timestamp = time.time()
        self.metadata = metadata or {}
    
    def to_dict(self) -> dict:
        """
        Converts the metric to a dictionary representation.
        
        Returns:
            Dictionary representation of the metric
        """
        result = {
            'component': self.component,
            'operation': self.operation,
            'duration': self.duration,
            'timestamp': self.timestamp
        }
        
        if self.metadata:
            result['metadata'] = self.metadata
            
        return result
    
    def exceeds_threshold(self, file_size_bytes: int) -> bool:
        """
        Checks if this metric exceeds the performance threshold for its operation type.
        
        Args:
            file_size_bytes: Size of the file being processed
            
        Returns:
            True if the metric exceeds the threshold, False otherwise
        """
        return check_performance_threshold(
            self.component, self.operation, self.duration, file_size_bytes
        )


class PerformanceTracker:
    """
    Tracks and analyzes performance metrics across different components of the application.
    """
    
    def __init__(self):
        """
        Initializes a new PerformanceTracker instance.
        """
        self._metrics = []
        self._component_metrics = {}
    
    def add_metric(self, component: str, operation: str, duration: float, 
                  metadata: dict = None) -> PerformanceMetric:
        """
        Adds a performance metric to the tracker.
        
        Args:
            component: The component being measured
            operation: The operation being performed
            duration: The time taken to complete the operation in seconds
            metadata: Optional dictionary with additional information
            
        Returns:
            The created and added metric
        """
        metric = PerformanceMetric(component, operation, duration, metadata)
        self._metrics.append(metric)
        
        # Update component metrics dictionary
        if component not in self._component_metrics:
            self._component_metrics[component] = {}
            
        if operation not in self._component_metrics[component]:
            self._component_metrics[component][operation] = []
            
        self._component_metrics[component][operation].append(duration)
        
        logger.debug(f"Performance metric added: {component}.{operation} took {duration:.6f}s")
        
        return metric
    
    def track_operation(self, component: str, operation: str, func: callable,
                       *args, **kwargs) -> typing.Tuple[typing.Any, PerformanceMetric]:
        """
        Tracks the execution time of an operation and adds it as a metric.
        
        Args:
            component: The component being measured
            operation: The operation being performed
            func: The function to execute and measure
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            A tuple containing the result of the function and the performance metric
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        metric = self.add_metric(component, operation, duration)
        
        return result, metric
    
    def get_metrics(self) -> typing.List[PerformanceMetric]:
        """
        Gets all recorded performance metrics.
        
        Returns:
            List of all recorded metrics
        """
        return self._metrics.copy()
    
    def get_component_metrics(self, component: str) -> typing.Dict[str, typing.List[float]]:
        """
        Gets metrics for a specific component.
        
        Args:
            component: The component name
            
        Returns:
            Dictionary of operation names to lists of durations
        """
        if component in self._component_metrics:
            return self._component_metrics[component].copy()
        return {}
    
    def get_average_duration(self, component: str, operation: str) -> float:
        """
        Gets the average duration for a specific component and operation.
        
        Args:
            component: The component name
            operation: The operation name
            
        Returns:
            Average duration in seconds, or 0 if no metrics exist
        """
        metrics = self.get_component_metrics(component)
        if operation in metrics and metrics[operation]:
            return sum(metrics[operation]) / len(metrics[operation])
        return 0
    
    def get_performance_summary(self) -> typing.Dict[str, typing.Dict[str, typing.Dict[str, float]]]:
        """
        Generates a summary of performance metrics grouped by component.
        
        Returns:
            Nested dictionary of performance statistics
        """
        summary = {}
        
        for component, operations in self._component_metrics.items():
            summary[component] = {}
            
            for operation, durations in operations.items():
                if not durations:
                    continue
                    
                summary[component][operation] = {
                    'min': min(durations),
                    'max': max(durations),
                    'avg': sum(durations) / len(durations),
                    'total': sum(durations),
                    'count': len(durations)
                }
                
        return summary
    
    def reset(self) -> None:
        """
        Resets all tracked metrics.
        """
        self._metrics.clear()
        self._component_metrics.clear()
        logger.info("Performance metrics have been reset")


def track_time(component: str, operation: str):
    """
    Decorator that tracks the execution time of a function and records it as a performance metric.
    
    Args:
        component: The component name
        operation: The operation name
        
    Returns:
        Decorated function that tracks execution time
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            duration = end_time - start_time
            performance_tracker.add_metric(component, operation, duration)
            
            return result
        return wrapper
    return decorator


@contextlib.contextmanager
def performance_context(component: str, operation: str):
    """
    Context manager for tracking the performance of a code block.
    
    Args:
        component: The component name
        operation: The operation name
        
    Yields:
        None
    """
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        performance_tracker.add_metric(component, operation, duration)


def check_performance_threshold(component: str, operation: str, 
                               duration: float, file_size_bytes: int) -> bool:
    """
    Checks if a performance metric exceeds the defined threshold for its operation type and file size.
    
    Args:
        component: The component name
        operation: The operation name
        duration: The measured duration in seconds
        file_size_bytes: Size of the file being processed
        
    Returns:
        True if the metric exceeds the threshold, False otherwise
    """
    # Determine file size category
    if file_size_bytes <= PERFORMANCE_CONSTANTS["SMALL_FILE_THRESHOLD_BYTES"]:
        size_category = "small"
    elif file_size_bytes <= PERFORMANCE_CONSTANTS["MEDIUM_FILE_THRESHOLD_BYTES"]:
        size_category = "medium"
    else:
        size_category = "large"
    
    # Look up the appropriate timeout threshold
    max_processing_times = PERFORMANCE_CONSTANTS["MAX_PROCESSING_TIME_SECONDS"][size_category]
    
    # Check if the operation exists in the timeout thresholds
    # Map common operations to their category
    operation_mapping = {
        # Parsing operations
        "parse_json": "parsing",
        "validate_json": "parsing",
        "read_json_file": "parsing",
        
        # Transformation operations
        "transform_data": "transformation",
        "flatten_nested_json": "transformation",
        "normalize_arrays": "transformation",
        "create_dataframe": "transformation",
        
        # Excel generation operations
        "generate_excel": "excel_generation",
        "create_workbook": "excel_generation",
        "write_excel_file": "excel_generation",
        "format_excel": "excel_generation"
    }
    
    # Get the operation category or use "total" as default
    operation_category = operation_mapping.get(operation, "total")
    threshold = max_processing_times[operation_category]
    
    # Compare the actual duration with the threshold
    if duration > threshold:
        logger.warning(
            f"Performance threshold exceeded: {component}.{operation} took {duration:.2f}s "
            f"(threshold: {threshold:.2f}s for {operation_category} operation in {size_category} file category)"
        )
        return True
    
    return False


# Create a singleton instance of the performance tracker
performance_tracker = PerformanceTracker()