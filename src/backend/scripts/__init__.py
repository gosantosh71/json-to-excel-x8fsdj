"""
Initializes the scripts package for the JSON to Excel Conversion Tool,
making utility scripts accessible for development, testing, and performance analysis.
This file exposes key script functions and classes to enable benchmarking, test data
generation, and memory profiling capabilities.
"""

from .benchmark import benchmark_component, benchmark_pipeline, BenchmarkResult  # src/backend/scripts/benchmark.py
from .generate_test_data import generate_all_test_files, generate_flat_json, generate_nested_json, generate_array_json  # src/backend/scripts/generate_test_data.py
from .profile_memory_usage import profile_conversion_process, MemoryProfiler, generate_memory_report  # src/backend/scripts/profile_memory_usage.py

__all__ = [
    "benchmark_component",
    "benchmark_pipeline",
    "BenchmarkResult",
    "generate_all_test_files",
    "generate_flat_json",
    "generate_nested_json",
    "generate_array_json",
    "profile_conversion_process",
    "MemoryProfiler",
    "generate_memory_report"
]