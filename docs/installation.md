# Installation Guide

This document provides comprehensive instructions for installing the JSON to Excel Conversion Tool using various methods. Choose the installation method that best suits your needs and environment.

## System Requirements

Before installing the JSON to Excel Conversion Tool, ensure your system meets the following requirements:

### Minimum Requirements

- Operating System: Windows 10+, macOS 10.15+, or Ubuntu 20.04+
- Processor: 1 GHz dual-core or better
- Memory: 512 MB RAM (2+ GB recommended)
- Storage: 100 MB free space
- Python: Version 3.9 or higher (if using Python package installation)

### Recommended Specifications

- Processor: 2+ GHz quad-core
- Memory: 2+ GB RAM
- Storage: 500+ MB free space
- Python: Version 3.11 or higher

## Installation Methods

The JSON to Excel Conversion Tool can be installed using one of the following methods:

### Python Package Installation

Install the tool as a Python package using pip. This method is recommended for developers and users who already have Python installed.

```bash
# Install the core package with CLI
pip install json-to-excel-converter

# Install with web interface support
pip install json-to-excel-converter[web]

# Install from source
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter
pip install .
```

### Standalone Executable Installation

Download and run the standalone executable for your platform. This method doesn't require Python to be installed.

#### Windows

1. Download the Windows installer (.exe) from the [releases page](https://github.com/organization/json-to-excel-converter/releases)
2. Run the installer and follow the on-screen instructions
3. Launch the application from the Start Menu

#### macOS

1. Download the macOS disk image (.dmg) from the [releases page](https://github.com/organization/json-to-excel-converter/releases)
2. Open the disk image and drag the application to your Applications folder
3. Launch the application from Applications

#### Linux

1. Download the Linux AppImage or package (.deb/.rpm) from the [releases page](https://github.com/organization/json-to-excel-converter/releases)
2. Make the AppImage executable: `chmod +x json-to-excel-converter.AppImage`
3. Run the application: `./json-to-excel-converter.AppImage`

Or install using the package manager:
```bash
# Debian/Ubuntu
sudo dpkg -i json-to-excel-converter.deb

# Red Hat/Fedora
sudo rpm -i json-to-excel-converter.rpm
```

### Docker Installation

Run the tool using Docker containers. This method provides a consistent environment across different platforms.

```bash
# Pull the Docker image
docker pull organization/json-to-excel-converter:latest

# Run the CLI version with volume mount for file access
docker run -v $(pwd):/data organization/json-to-excel-converter:latest /data/input.json /data/output.xlsx

# Run the web interface version
docker run -p 5000:5000 -v $(pwd):/data organization/json-to-excel-converter:web
```

#### Using Docker Compose

For a more complete setup with both CLI and web interface:

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter

# Start the services
docker-compose up
```

## Component-Specific Installation

The JSON to Excel Conversion Tool consists of multiple components that can be installed separately if needed:

### Backend Component

The core functionality for JSON parsing and Excel generation:

```bash
pip install json-to-excel-converter-backend
```

### CLI Component

The command-line interface for the tool:

```bash
pip install json-to-excel-converter-cli
```

### Web Interface Component

The optional web-based user interface:

```bash
pip install json-to-excel-converter-web
```

## Development Installation

For developers who want to contribute to the project or modify the code:

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Verifying Installation

After installation, verify that the tool is working correctly:

### CLI Verification

Run the following command to check the CLI installation:

```bash
json2excel --version
```

### Web Interface Verification

If you installed the web interface, start it and access it in your browser:

```bash
# Start the web server
json2excel-web

# Access in your browser
# http://localhost:5000
```

## Troubleshooting

If you encounter issues during installation, try the following solutions:

### Python Package Installation Issues

- Ensure you have Python 3.9 or higher installed: `python --version`
- Update pip to the latest version: `pip install --upgrade pip`
- Try installing in a virtual environment to avoid dependency conflicts
- Check for error messages in the installation output

### Executable Installation Issues

- Verify that you downloaded the correct version for your operating system
- On Windows, try running the installer as administrator
- On macOS, check if the application is blocked by Gatekeeper
- On Linux, ensure the AppImage has execute permissions

### Docker Installation Issues

- Ensure Docker is installed and running: `docker --version`
- Check if you have permission to run Docker commands
- Verify that the volume mount paths are correct
- Check Docker logs for error messages: `docker logs <container_id>`

## Next Steps

After successfully installing the JSON to Excel Conversion Tool, check out the following resources to get started:

- Learn how to perform simple JSON to Excel conversions using the provided command-line interface
- Explore the tool's features for handling both flat and nested JSON structures
- [Architecture Overview](architecture.md): For developers interested in the tool's design
- [API Reference](api_reference.md): For programmatic integration with the tool

You can also try converting your own JSON files with various complexity levels to see how the tool handles different structures. For contributing to the project, refer to the project repository's CONTRIBUTING.md file.