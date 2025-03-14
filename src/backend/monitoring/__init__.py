"""
Initializes the monitoring package and exposes performance tracking functionality for the JSON to Excel Conversion Tool.

This module makes performance tracking components available to other parts of the application for monitoring
execution times, memory usage, and performance metrics.
"""

from .performance_tracker import (
    PerformanceMetric,
    PerformanceTracker,
    performance_tracker,
    get_current_memory_usage,
    track_time,
    performance_context,
    check_performance_threshold
)

# Make these components available to importers of the monitoring package
__all__ = [
    'PerformanceMetric',
    'PerformanceTracker',
    'performance_tracker',
    'get_current_memory_usage',
    'track_time',
    'performance_context',
    'check_performance_threshold',
]