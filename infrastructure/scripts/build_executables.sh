#!/bin/bash
set -e

# Script Header
echo "===================================================="
echo "Building JSON to Excel Converter Executables"
echo "===================================================="
echo

# Environment Setup
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/../..")
OUTPUT_DIR="$PROJECT_ROOT/dist"
PYINSTALLER_OPTS="--clean --noconfirm"
CLI_SPEC="$PROJECT_ROOT/pyinstaller/cli.spec"
WEB_SPEC="$PROJECT_ROOT/pyinstaller/web.spec"

# Function to check prerequisites
check_prerequisites() {
  echo "Checking prerequisites..."

  # Check if Python is installed and in PATH
  if ! command -v python3 &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.9 or higher."
    return 1
  fi

  # Check if PyInstaller is installed
  if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller not found. Please install PyInstaller."
    echo "You can install it using: pip install pyinstaller"
    return 1
  fi

  # Check if required Python packages are installed
  python3 -c "
try:
    import pandas
    import openpyxl
    import json
    import argparse
    import logging
    echo 'All python dependencies are installed'
except ImportError as e:
    print(f'Error: Required Python packages not found: {e}')
    print('Please install the required packages using: pip install -r requirements.txt')
    exit(1)
"
  return 0
}

# Function to set up the build environment
setup_environment() {
  echo "Setting up build environment..."

  # Create output directories if they don't exist
  mkdir -p "$OUTPUT_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Build directory creation failed."
    return 1
  fi

  # Set Python path to include project modules
  export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

  echo "Build environment setup complete."
  return 0
}

# Function to build the CLI executable
build_cli_executable() {
  echo "Building CLI executable..."

  # Run PyInstaller with CLI spec file
  pyinstaller $PYINSTALLER_OPTS "$CLI_SPEC"
  if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build process failed for CLI."
    return 1
  fi

  echo "CLI executable build complete."
  return 0
}

# Function to build the web executable
build_web_executable() {
  echo "Building web interface executable..."

  # Run PyInstaller with web spec file
  pyinstaller $PYINSTALLER_OPTS "$WEB_SPEC"
  if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build process failed for web interface."
    return 1
  fi

  echo "Web interface executable build complete."
  return 0
}

# Function to clean up build artifacts
cleanup_build_artifacts() {
  echo "Cleaning up build artifacts..."

  # Remove build directories
  rm -rf build
  rm -rf dist/*.spec

  # Remove PyInstaller cache files
  find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
  find . -name "*.pyc" -delete

  echo "Build artifacts cleanup complete."
}

# Main function to orchestrate the build process
main() {
  echo "===================================================="
  echo "Starting JSON to Excel Converter Executable Build"
  echo "===================================================="
  echo

  # Check prerequisites
  if ! check_prerequisites; then
    echo "Prerequisites check failed. Exiting."
    return 2
  fi

  # Set up environment
  if ! setup_environment; then
    echo "Environment setup failed. Exiting."
    return 3
  fi

  # Build CLI executable
  if ! build_cli_executable; then
    echo "CLI executable build failed. Exiting."
    return 4
  fi

  # Build web executable
  if ! build_web_executable; then
    echo "Web interface executable build failed. Exiting."
    return 5
  fi

  # Clean up build artifacts
  cleanup_build_artifacts

  echo
  echo "===================================================="
  echo "JSON to Excel Converter Executable Build Complete!"
  echo "Executables are located in the 'dist' directory."
  echo "===================================================="
  echo

  return 0
}

# Main Script Execution
main
exit $?