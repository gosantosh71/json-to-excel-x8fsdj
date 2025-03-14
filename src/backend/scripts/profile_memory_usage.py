#!/usr/bin/env python
"""
A utility script for profiling memory usage during JSON to Excel conversion operations.

This script helps identify memory consumption patterns across different components
of the conversion pipeline, allowing developers to optimize memory usage and prevent
memory-related issues with large files.
"""

import os  # v: built-in
import sys  # v: built-in
import argparse  # v: built-in
import time  # v: built-in
import gc  # v: built-in
import matplotlib.pyplot as plt  # v: 3.5.0+
import pandas as pd  # v: 1.5.0+

from ..monitoring.performance_tracker import get_current_memory_usage
from ..utils import Timer
from ..json_parser import JSONParser
from ..data_transformer import DataTransformer
from ..excel_generator import ExcelGenerator
from ..logger import get_logger
from ..constants import FILE_CONSTANTS, PERFORMANCE_CONSTANTS

# Initialize logger
logger = get_logger(__name__)

# Global list to store memory snapshots
memory_snapshots = []


def take_memory_snapshot(label: str):
    """
    Records the current memory usage with a label for the operation being performed.
    
    Args:
        label: Description of the operation being performed
        
    Returns:
        A snapshot containing the label, timestamp, and memory usage in MB
    """
    memory_usage = get_current_memory_usage()
    snapshot = {
        'label': label,
        'timestamp': time.time(),
        'memory_mb': memory_usage
    }
    memory_snapshots.append(snapshot)
    logger.info(f"Memory usage at {label}: {memory_usage:.2f} MB")
    return snapshot


def profile_conversion_process(input_file: str, output_file: str):
    """
    Profiles the memory usage of the entire JSON to Excel conversion process.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output Excel file
        
    Returns:
        DataFrame containing memory usage data for each step of the conversion process
    """
    # Clear any previous snapshots
    memory_snapshots.clear()
    
    # Force garbage collection to start with a clean state
    gc.collect()
    
    # Take initial memory snapshot
    take_memory_snapshot("Initial state")
    
    # Initialize components
    json_parser = JSONParser()
    data_transformer = DataTransformer()
    excel_generator = ExcelGenerator()
    
    # Profile JSON parsing
    take_memory_snapshot("Before JSON parsing")
    with Timer("JSON parsing"):
        with open(input_file, 'r') as f:
            json_content = f.read()
        json_data, _ = json_parser.parse_string(json_content)
    take_memory_snapshot("After JSON parsing")
    
    # Profile JSON data creation
    take_memory_snapshot("Before JSON data creation")
    with Timer("JSON data creation"):
        parsed_data = json_parser.create_json_data(json_data, input_file, os.path.getsize(input_file))
    take_memory_snapshot("After JSON data creation")
    
    # Profile data transformation
    take_memory_snapshot("Before data transformation")
    with Timer("Data transformation"):
        df, _ = data_transformer.transform_data(parsed_data)
    take_memory_snapshot("After data transformation")
    
    # Profile Excel generation
    take_memory_snapshot("Before Excel generation")
    with Timer("Excel generation"):
        excel_generator.generate_excel(df, output_file)
    take_memory_snapshot("After Excel generation")
    
    # Take final memory snapshot
    take_memory_snapshot("Final state")
    
    # Convert snapshots to DataFrame
    snapshots_df = pd.DataFrame(memory_snapshots)
    
    # Calculate relative time from start
    start_time = snapshots_df['timestamp'].iloc[0]
    snapshots_df['relative_time'] = snapshots_df['timestamp'] - start_time
    
    return snapshots_df


def plot_memory_usage(memory_data: pd.DataFrame, output_path: str):
    """
    Generates a plot of memory usage across the conversion process steps.
    
    Args:
        memory_data: DataFrame containing memory usage data
        output_path: Path to save the plot
        
    Returns:
        None
    """
    plt.figure(figsize=(12, 6))
    
    # Plot memory usage over time
    plt.plot(memory_data['relative_time'], memory_data['memory_mb'], 'b-', marker='o')
    
    # Add labels for each step
    for i, row in memory_data.iterrows():
        plt.annotate(
            row['label'],
            (row['relative_time'], row['memory_mb']),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            rotation=30,
            fontsize=8
        )
    
    # Add labels and title
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage During JSON to Excel Conversion')
    plt.grid(True)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path)
    logger.info(f"Memory usage plot saved to {output_path}")


def generate_memory_report(memory_data: pd.DataFrame):
    """
    Generates a detailed report of memory usage statistics for the conversion process.
    
    Args:
        memory_data: DataFrame containing memory usage data
        
    Returns:
        Dictionary containing memory usage statistics for each conversion step
    """
    # Extract step names by looking at pairs of "Before X" and "After X" labels
    steps = []
    for i in range(0, len(memory_data) - 1, 2):
        if i + 1 < len(memory_data):
            before_label = memory_data.iloc[i]['label']
            after_label = memory_data.iloc[i + 1]['label']
            
            if before_label.startswith("Before ") and after_label.startswith("After "):
                step_name = before_label[7:]  # Remove "Before " prefix
                steps.append({
                    'step': step_name,
                    'before_idx': i,
                    'after_idx': i + 1
                })
    
    # Calculate statistics for each step
    step_stats = {}
    for step in steps:
        before_memory = memory_data.iloc[step['before_idx']]['memory_mb']
        after_memory = memory_data.iloc[step['after_idx']]['memory_mb']
        memory_increase = after_memory - before_memory
        
        before_time = memory_data.iloc[step['before_idx']]['relative_time']
        after_time = memory_data.iloc[step['after_idx']]['relative_time']
        duration = after_time - before_time
        
        step_stats[step['step']] = {
            'before_memory_mb': float(before_memory),
            'after_memory_mb': float(after_memory),
            'memory_increase_mb': float(memory_increase),
            'duration_sec': float(duration),
            'memory_per_sec': float(memory_increase / duration if duration > 0 else 0)
        }
    
    # Calculate overall statistics
    overall_stats = {
        'peak_memory_mb': float(memory_data['memory_mb'].max()),
        'initial_memory_mb': float(memory_data.iloc[0]['memory_mb']),
        'final_memory_mb': float(memory_data.iloc[-1]['memory_mb']),
        'total_memory_increase_mb': float(memory_data.iloc[-1]['memory_mb'] - memory_data.iloc[0]['memory_mb']),
        'total_duration_sec': float(memory_data.iloc[-1]['relative_time'] - memory_data.iloc[0]['relative_time'])
    }
    
    # Log summary
    logger.info(f"Memory profiling summary:")
    logger.info(f"Peak memory usage: {overall_stats['peak_memory_mb']:.2f} MB")
    logger.info(f"Total memory increase: {overall_stats['total_memory_increase_mb']:.2f} MB")
    logger.info(f"Total duration: {overall_stats['total_duration_sec']:.2f} seconds")
    
    # Combine step stats and overall stats
    report = {
        'steps': step_stats,
        'overall': overall_stats
    }
    
    return report


class MemoryProfiler:
    """
    A class that provides methods for profiling memory usage during JSON to Excel conversion.
    """
    
    def __init__(self):
        """
        Initializes a new MemoryProfiler instance.
        """
        self._snapshots = []
        self._logger = get_logger(__name__)
    
    def take_snapshot(self, label: str):
        """
        Takes a snapshot of current memory usage with a label.
        
        Args:
            label: Description of the operation being performed
            
        Returns:
            A snapshot containing the label, timestamp, and memory usage in MB
        """
        memory_usage = get_current_memory_usage()
        snapshot = {
            'label': label,
            'timestamp': time.time(),
            'memory_mb': memory_usage
        }
        self._snapshots.append(snapshot)
        self._logger.info(f"Memory usage at {label}: {memory_usage:.2f} MB")
        return snapshot
    
    def profile_process(self, input_file: str, output_file: str):
        """
        Profiles memory usage of the entire conversion process.
        
        Args:
            input_file: Path to the input JSON file
            output_file: Path to the output Excel file
            
        Returns:
            DataFrame containing memory usage data
        """
        # Clear previous snapshots
        self.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Take initial snapshot
        self.take_snapshot("Initial state")
        
        # Initialize components
        json_parser = JSONParser()
        data_transformer = DataTransformer()
        excel_generator = ExcelGenerator()
        
        # Profile JSON parsing
        self.take_snapshot("Before JSON parsing")
        with Timer("JSON parsing"):
            with open(input_file, 'r') as f:
                json_content = f.read()
            json_data, _ = json_parser.parse_string(json_content)
        self.take_snapshot("After JSON parsing")
        
        # Profile JSON data creation
        self.take_snapshot("Before JSON data creation")
        with Timer("JSON data creation"):
            parsed_data = json_parser.create_json_data(json_data, input_file, os.path.getsize(input_file))
        self.take_snapshot("After JSON data creation")
        
        # Profile data transformation
        self.take_snapshot("Before data transformation")
        with Timer("Data transformation"):
            df, _ = data_transformer.transform_data(parsed_data)
        self.take_snapshot("After data transformation")
        
        # Profile Excel generation
        self.take_snapshot("Before Excel generation")
        with Timer("Excel generation"):
            excel_generator.generate_excel(df, output_file)
        self.take_snapshot("After Excel generation")
        
        # Take final snapshot
        self.take_snapshot("Final state")
        
        # Convert snapshots to DataFrame
        return self._create_dataframe()
    
    def generate_report(self):
        """
        Generates a report of memory usage statistics.
        
        Returns:
            Dictionary containing memory usage report
        """
        # Convert snapshots to DataFrame if needed
        if not hasattr(self, '_df') or self._df is None:
            self._df = self._create_dataframe()
        
        # Extract step names and calculate statistics
        steps = []
        for i in range(0, len(self._df) - 1, 2):
            if i + 1 < len(self._df):
                before_label = self._df.iloc[i]['label']
                after_label = self._df.iloc[i + 1]['label']
                
                if before_label.startswith("Before ") and after_label.startswith("After "):
                    step_name = before_label[7:]  # Remove "Before " prefix
                    steps.append({
                        'step': step_name,
                        'before_idx': i,
                        'after_idx': i + 1
                    })
        
        # Calculate statistics for each step
        step_stats = {}
        for step in steps:
            before_memory = self._df.iloc[step['before_idx']]['memory_mb']
            after_memory = self._df.iloc[step['after_idx']]['memory_mb']
            memory_increase = after_memory - before_memory
            
            before_time = self._df.iloc[step['before_idx']]['relative_time']
            after_time = self._df.iloc[step['after_idx']]['relative_time']
            duration = after_time - before_time
            
            step_stats[step['step']] = {
                'before_memory_mb': float(before_memory),
                'after_memory_mb': float(after_memory),
                'memory_increase_mb': float(memory_increase),
                'duration_sec': float(duration),
                'memory_per_sec': float(memory_increase / duration if duration > 0 else 0)
            }
        
        # Calculate overall statistics
        overall_stats = {
            'peak_memory_mb': float(self._df['memory_mb'].max()),
            'initial_memory_mb': float(self._df.iloc[0]['memory_mb']),
            'final_memory_mb': float(self._df.iloc[-1]['memory_mb']),
            'total_memory_increase_mb': float(self._df.iloc[-1]['memory_mb'] - self._df.iloc[0]['memory_mb']),
            'total_duration_sec': float(self._df.iloc[-1]['relative_time'] - self._df.iloc[0]['relative_time'])
        }
        
        # Log summary
        self._logger.info(f"Memory profiling summary:")
        self._logger.info(f"Peak memory usage: {overall_stats['peak_memory_mb']:.2f} MB")
        self._logger.info(f"Total memory increase: {overall_stats['total_memory_increase_mb']:.2f} MB")
        self._logger.info(f"Total duration: {overall_stats['total_duration_sec']:.2f} seconds")
        
        # Combine step stats and overall stats
        return {
            'steps': step_stats,
            'overall': overall_stats
        }
    
    def plot_memory_usage(self, output_path: str):
        """
        Generates a plot of memory usage.
        
        Args:
            output_path: Path to save the plot
            
        Returns:
            None
        """
        # Convert snapshots to DataFrame if needed
        if not hasattr(self, '_df') or self._df is None:
            self._df = self._create_dataframe()
        
        plt.figure(figsize=(12, 6))
        
        # Plot memory usage over time
        plt.plot(self._df['relative_time'], self._df['memory_mb'], 'b-', marker='o')
        
        # Add labels for each step
        for i, row in self._df.iterrows():
            plt.annotate(
                row['label'],
                (row['relative_time'], row['memory_mb']),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                rotation=30,
                fontsize=8
            )
        
        # Add labels and title
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (MB)')
        plt.title('Memory Usage During JSON to Excel Conversion')
        plt.grid(True)
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(output_path)
        self._logger.info(f"Memory usage plot saved to {output_path}")
    
    def clear(self):
        """
        Clears all memory snapshots.
        
        Returns:
            None
        """
        self._snapshots = []
        if hasattr(self, '_df'):
            self._df = None
        gc.collect()
    
    def get_snapshots(self):
        """
        Gets all recorded memory snapshots.
        
        Returns:
            List of memory snapshots
        """
        return self._snapshots.copy()
    
    def _create_dataframe(self):
        """
        Creates a DataFrame from the memory snapshots.
        
        Returns:
            DataFrame with memory usage data
        """
        df = pd.DataFrame(self._snapshots)
        
        # Calculate relative time from start
        if not df.empty:
            start_time = df['timestamp'].iloc[0]
            df['relative_time'] = df['timestamp'] - start_time
        
        self._df = df
        return df


def parse_arguments():
    """
    Parses command line arguments for the memory profiling script.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Profile memory usage during JSON to Excel conversion."
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input JSON file"
    )
    
    parser.add_argument(
        "output_file",
        help="Path to the output Excel file"
    )
    
    parser.add_argument(
        "--plot",
        dest="plot_output",
        help="Path to save the memory usage plot (e.g., memory_plot.png)"
    )
    
    parser.add_argument(
        "--report",
        dest="report_output",
        help="Path to save the memory usage report in JSON format"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def main():
    """
    Main function that runs the memory profiling process.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_arguments()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        logger.error(f"Input file does not exist: {args.input_file}")
        return 1
    
    # Check if input file size exceeds maximum
    input_file_size = os.path.getsize(args.input_file)
    max_file_size = FILE_CONSTANTS["MAX_FILE_SIZE_BYTES"]
    if input_file_size > max_file_size:
        logger.warning(
            f"Input file size ({input_file_size} bytes) exceeds recommended maximum "
            f"({max_file_size} bytes). Memory usage may be high."
        )
    
    # Validate output directory
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            logger.error(f"Failed to create output directory: {output_dir}")
            logger.error(f"Error: {str(e)}")
            return 1
    
    logger.info(f"Starting memory profiling for conversion of {args.input_file} to {args.output_file}")
    
    try:
        # Profile the conversion process
        memory_data = profile_conversion_process(args.input_file, args.output_file)
        
        # Generate memory usage report
        report = generate_memory_report(memory_data)
        
        # Generate memory usage plot if requested
        if args.plot_output:
            plot_memory_usage(memory_data, args.plot_output)
        
        # Save report if requested
        if args.report_output:
            import json
            with open(args.report_output, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Memory usage report saved to {args.report_output}")
        
        logger.info("Memory profiling completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during memory profiling: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())