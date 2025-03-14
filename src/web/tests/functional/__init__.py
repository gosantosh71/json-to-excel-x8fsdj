import pytest
import os
from pathlib import Path

# Constants for test directories and paths
FUNCTIONAL_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(os.path.dirname(FUNCTIONAL_TEST_DIR), 'fixtures')
SAMPLE_DATA_DIR = os.path.join(FIXTURES_DIR, 'sample_data')

# Test marker for functional tests
FUNCTIONAL_TEST_MARKER = pytest.mark.functional

# Device configurations for responsive testing
DEVICE_SIZES = [
    {'name': 'mobile', 'width': 375, 'height': 667},
    {'name': 'tablet', 'width': 768, 'height': 1024},
    {'name': 'desktop', 'width': 1366, 'height': 768}
]

# Orientation configurations
ORIENTATIONS = [
    {'name': 'portrait', 'width_multiplier': 1, 'height_multiplier': 1.7},
    {'name': 'landscape', 'width_multiplier': 1.7, 'height_multiplier': 1}
]

def pytest_mark_functional():
    """
    Decorator function that applies the functional test marker to test functions.
    
    Returns:
        function: Decorated test function with functional marker
    """
    return FUNCTIONAL_TEST_MARKER

@pytest.fixture
def setup_functional_test():
    """
    Fixture that sets up the environment for functional tests.
    
    Returns:
        dict: Dictionary with test environment configuration
    """
    config = {
        'test_dir': FUNCTIONAL_TEST_DIR,
        'fixtures_dir': FIXTURES_DIR,
        'sample_data_dir': SAMPLE_DATA_DIR,
        'device_sizes': DEVICE_SIZES,
        'orientations': ORIENTATIONS
    }
    return config

def get_sample_json_path(filename):
    """
    Utility function to get the path to a sample JSON file.
    
    Args:
        filename (str): The filename of the sample JSON file
        
    Returns:
        str: Path to the sample JSON file
    """
    return os.path.join(SAMPLE_DATA_DIR, filename)

def get_device_config(device_name):
    """
    Utility function to get the configuration for a specific device type.
    
    Args:
        device_name (str): The name of the device (mobile, tablet, desktop)
        
    Returns:
        dict: Device configuration with width and height
        
    Raises:
        ValueError: If the device name is not found in configurations
    """
    for device in DEVICE_SIZES:
        if device['name'] == device_name:
            return device
    raise ValueError(f"Device configuration not found for: {device_name}")

def get_orientation_config(orientation_name):
    """
    Utility function to get the configuration for a specific orientation.
    
    Args:
        orientation_name (str): The name of the orientation (portrait, landscape)
        
    Returns:
        dict: Orientation configuration with width and height multipliers
        
    Raises:
        ValueError: If the orientation name is not found in configurations
    """
    for orientation in ORIENTATIONS:
        if orientation['name'] == orientation_name:
            return orientation
    raise ValueError(f"Orientation configuration not found for: {orientation_name}")