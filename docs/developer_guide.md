# Developer Guide

This comprehensive guide provides developers with the information needed to understand, modify, and extend the JSON to Excel Conversion Tool. Whether you're fixing bugs, adding features, or integrating the tool into your own projects, this guide will help you navigate the codebase and follow best practices.

## Table of Contents

- [Project Overview](#project-overview)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing Guidelines](#contributing-guidelines)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Project Overview

The JSON to Excel Conversion Tool is a Python-based utility designed to transform JSON data files into structured Excel spreadsheets. The tool follows a modular pipeline architecture with clear separation of concerns between components.

### Key Features

- JSON file reading and validation
- Nested JSON structure flattening
- Array normalization
- Excel file generation with formatting
- Command-line interface
- Optional web interface

### Architecture

The tool uses a pipeline architecture where data flows through distinct processing stages:

1. **Input Handler**: Reads and validates JSON files
2. **JSON Parser**: Parses and analyzes JSON structure
3. **Data Transformer**: Converts JSON to tabular format
4. **Excel Generator**: Creates formatted Excel output

For a detailed architecture overview, see the [Architecture Documentation](architecture.md).

### Design Principles

The project follows these key design principles:

- **Single Responsibility**: Each component handles one specific aspect of the conversion process
- **Loose Coupling**: Components interact through well-defined interfaces
- **Data Transformation Pipeline**: Clear sequential flow from input to output
- **Error Propagation**: Errors are captured and propagated through the pipeline
- **Extensibility**: The system is designed to be easily extended with new features

### Technology Stack

The project uses the following technologies:

- **Python 3.9+**: Core programming language
- **Pandas 1.5.0+**: Data manipulation and transformation
- **openpyxl 3.1.0+**: Excel file generation
- **Flask 2.3.0+**: Web interface (optional)
- **pytest 7.3.0+**: Testing framework
- **Black & Flake8**: Code formatting and linting

## Development Environment Setup

This section covers how to set up your development environment to work on the JSON to Excel Conversion Tool.

### Prerequisites

Before setting up the development environment, ensure you have the following installed:

- Python 3.9 or higher
- Git
- pip (Python package manager)
- A code editor (VS Code recommended)

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter
```

### Virtual Environment

It's recommended to use a virtual environment for development:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Development Dependencies

```bash
# Install the package in development mode with all dependencies
pip install -e ".[dev]"
```

This installs the package in editable mode, along with all development dependencies specified in the project's setup.py file.

### IDE Setup

### Visual Studio Code

If you're using VS Code, the following extensions are recommended:

- Python extension
- Pylance for improved Python language support
- Python Test Explorer for pytest integration
- Black Formatter for code formatting

Recommended settings for VS Code (`.vscode/settings.json`):

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "src"
    ]
}
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. Install and set up pre-commit:

```bash
pip install pre-commit
pre-commit install
```

This will install hooks that run before each commit to check code formatting, linting, and other quality checks.

## Project Structure

The JSON to Excel Conversion Tool is organized into the following directory structure:

### Directory Layout

```
json-to-excel-converter/
├── docs/                    # Documentation
│   ├── architecture.md      # Architecture documentation
│   ├── developer_guide.md   # This guide
│   ├── installation.md      # Installation instructions
│   ├── user_guide.md        # User documentation
│   └── examples/            # Example usage
├── src/                     # Source code
│   ├── backend/             # Core conversion functionality
│   │   ├── models/          # Data models
│   │   ├── validators/      # Validation logic
│   │   ├── formatters/      # Formatting utilities
│   │   ├── services/        # Business logic services
│   │   ├── json_parser.py   # JSON parsing component
│   │   ├── data_transformer.py # Data transformation component
│   │   ├── excel_generator.py # Excel generation component
│   │   └── error_handler.py # Error handling component
│   ├── cli/                 # Command-line interface
│   │   ├── commands/        # CLI command implementations
│   │   ├── utils/           # CLI utilities
│   │   └── json_to_excel.py # Main CLI entry point
│   └── web/                 # Web interface (optional)
│       ├── api/             # Web API endpoints
│       ├── static/          # Static assets
│       ├── templates/       # HTML templates
│       └── app.py           # Flask application
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── .github/                 # GitHub workflows
├── pyinstaller/             # PyInstaller configuration
├── setup.py                 # Package setup script
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md                # Project overview
```

### Key Files

- **src/backend/json_parser.py**: Handles JSON parsing and structure analysis
- **src/backend/data_transformer.py**: Converts JSON to tabular format
- **src/backend/excel_generator.py**: Creates Excel files from transformed data
- **src/cli/json_to_excel.py**: Main CLI entry point
- **src/web/app.py**: Flask application for web interface
- **setup.py**: Package configuration and dependencies

### Module Organization

The project is organized into three main modules:

1. **Backend**: Core conversion functionality, independent of user interfaces
2. **CLI**: Command-line interface that uses the backend
3. **Web**: Optional web interface that uses the backend

This separation allows each interface to evolve independently while sharing the core conversion logic.

## Core Components

This section provides detailed information about the core components of the JSON to Excel Conversion Tool.

### Input Handler

**Purpose**: Manages file access and initial validation of JSON input files

**Key Responsibilities**:
- Verify file existence and read permissions
- Check file extension and basic format
- Read file content into memory
- Handle file access errors gracefully

**Key Classes and Functions**:
- `InputHandler` class in `src/backend/input_handler.py`
- `read_json_file(file_path)`: Reads and validates a JSON file

**Example Usage**:
```python
from json_to_excel.backend.input_handler import InputHandler

input_handler = InputHandler()
result, error = input_handler.read_json_file('data.json')
if error:
    print(f"Error: {error.message}")
else:
    # Process the JSON content
    print(f"Successfully read JSON file with {len(result)} bytes")
```

### JSON Parser

**Purpose**: Validates and parses JSON content into Python data structures

**Key Responsibilities**:
- Parse JSON strings into Python dictionaries/lists
- Validate JSON syntax and structure
- Analyze JSON complexity (flat vs. nested)
- Detect arrays and their paths

**Key Classes and Functions**:
- `JSONParser` class in `src/backend/json_parser.py`
- `parse_string(json_string)`: Parses a JSON string
- `get_structure_info(json_data)`: Analyzes JSON structure

**Example Usage**:
```python
from json_to_excel.backend.json_parser import JSONParser

parser = JSONParser()
json_data, error = parser.parse_string(json_content)
if error:
    print(f"Error: {error.message}")
else:
    structure_info = parser.get_structure_info(json_data)
    print(f"JSON structure: {'nested' if structure_info['is_nested'] else 'flat'}")
    print(f"Contains arrays: {'yes' if structure_info['contains_arrays'] else 'no'}")
```

### Data Transformer

**Purpose**: Converts parsed JSON data into tabular format suitable for Excel

**Key Responsibilities**:
- Flatten nested JSON structures using dot notation
- Normalize arrays into appropriate tabular representation
- Handle different data types appropriately
- Create a consistent tabular structure

**Key Classes and Functions**:
- `DataTransformer` class in `src/backend/data_transformer.py`
- `transform_data(json_data)`: Transforms JSON to DataFrame
- `flatten_json(json_data)`: Flattens nested structures

**Example Usage**:
```python
from json_to_excel.backend.data_transformer import DataTransformer
from json_to_excel.backend.models.excel_options import ExcelOptions

options = ExcelOptions(array_handling='expand')
transformer = DataTransformer(options)
dataframe, error = transformer.transform_data(json_data)
if error:
    print(f"Error: {error.message}")
else:
    print(f"Transformed data has {len(dataframe)} rows and {len(dataframe.columns)} columns")
```

### Excel Generator

**Purpose**: Creates and formats Excel files from transformed data

**Key Responsibilities**:
- Generate Excel workbook and worksheets
- Create appropriate column headers
- Apply formatting based on data types
- Save Excel file to filesystem

**Key Classes and Functions**:
- `ExcelGenerator` class in `src/backend/excel_generator.py`
- `generate_excel(dataframe, output_path)`: Creates Excel file
- `format_workbook(workbook)`: Applies formatting

**Example Usage**:
```python
from json_to_excel.backend.excel_generator import ExcelGenerator
from json_to_excel.backend.models.excel_options import ExcelOptions

options = ExcelOptions(sheet_name='Data', format_as_table=True)
generator = ExcelGenerator(options)
success, error = generator.generate_excel(dataframe, 'output.xlsx')
if error:
    print(f"Error: {error.message}")
else:
    print("Excel file generated successfully")
```

### Error Handler

**Purpose**: Manages error detection and reporting across all components

**Key Responsibilities**:
- Standardize error reporting format
- Provide context-specific error messages
- Suggest resolution steps for common errors
- Log detailed error information

**Key Classes and Functions**:
- `ErrorHandler` class in `src/backend/error_handler.py`
- `ErrorResponse` class in `src/backend/models/error_response.py`
- `handle_error(error)`: Processes exceptions into structured responses

**Example Usage**:
```python
from json_to_excel.backend.error_handler import ErrorHandler

error_handler = ErrorHandler()
try:
    # Some operation that might fail
    result = process_data()
except Exception as e:
    error_response = error_handler.handle_error(e)
    print(f"Error: {error_response.user_message}")
    print(f"Suggestion: {error_response.suggested_action}")
```

### Command Line Interface

**Purpose**: Provides command-line access to conversion functionality

**Key Responsibilities**:
- Parse command-line arguments
- Execute appropriate commands
- Display results and errors
- Provide help and documentation

**Key Classes and Functions**:
- `argument_parser.py`: Parses command-line arguments
- `command_runner.py`: Executes commands
- `json_to_excel.py`: Main entry point

**Example Usage**:
```bash
# Basic conversion
json2excel convert data.json output.xlsx

# With options
json2excel convert data.json output.xlsx --sheet-name="Data" --array-handling=join
```

### Web Interface

**Purpose**: Provides browser-based access to conversion functionality

**Key Responsibilities**:
- Handle file uploads
- Process conversion requests
- Serve Excel downloads
- Provide user-friendly interface

**Key Classes and Functions**:
- `app.py`: Flask application setup
- `routes.py`: Web route definitions
- `api/` directory: API endpoints

**Example Usage**:
```bash
# Start the web server
json2excel-web

# Access in browser at http://localhost:5000
```

## Development Workflow

This section describes the recommended workflow for developing and contributing to the JSON to Excel Conversion Tool.

### Branching Strategy

The project follows a simplified Git Flow branching strategy:

- **main**: Stable production-ready code
- **develop**: Integration branch for features and fixes
- **feature/xxx**: Feature branches for new functionality
- **bugfix/xxx**: Bug fix branches
- **release/x.y.z**: Release preparation branches

Workflow:
1. Create a feature or bugfix branch from `develop`
2. Implement changes with regular commits
3. Submit a pull request to merge back into `develop`
4. After review and approval, changes are merged
5. Periodically, `develop` is merged into `main` for releases

### Coding Standards

The project follows these coding standards:

- **PEP 8**: Python style guide
- **Black**: Code formatting
- **Flake8**: Linting
- **Type Hints**: Use Python type annotations
- **Docstrings**: Google-style docstrings

Example function with proper style:

```python
def process_json_data(json_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, Optional[ErrorResponse]]:
    """Process JSON data into a pandas DataFrame.
    
    Args:
        json_data: The JSON data to process as a dictionary
        options: Optional processing options
        
    Returns:
        A tuple containing the processed DataFrame and an optional error response
        
    Raises:
        ValueError: If json_data is None or empty
    """
    if not json_data:
        raise ValueError("JSON data cannot be None or empty")
        
    # Implementation...
    
    return dataframe, None
```

### Pull Request Process

When submitting a pull request:

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new functionality
4. Ensure code is formatted with Black
5. Fill out the pull request template
6. Request review from maintainers

Pull requests should be focused on a single feature or fix to simplify review.

### Versioning

The project follows Semantic Versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

Version numbers are managed in `setup.py` and should be updated as part of the release process.

## Testing

The JSON to Excel Conversion Tool uses a comprehensive testing approach to ensure reliability and correctness.

### Testing Framework

The project uses pytest as its testing framework. Tests are organized into three categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete workflows

Test files are located in the `tests/` directory, mirroring the structure of the `src/` directory.

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run tests with coverage report
pytest --cov=src

# Run tests and generate HTML coverage report
pytest --cov=src --cov-report=html
```

### Writing Tests

When writing tests, follow these guidelines:

- Each test function should focus on a single aspect
- Use descriptive test names that explain what is being tested
- Use fixtures for common setup and teardown
- Mock external dependencies
- Include both positive and negative test cases

Example test:

```python
import pytest
from json_to_excel.backend.json_parser import JSONParser

def test_json_parser_validates_valid_json():
    # Arrange
    parser = JSONParser()
    valid_json = '{"name": "test", "value": 123}'
    
    # Act
    result, error = parser.parse_string(valid_json)
    
    # Assert
    assert error is None
    assert result is not None
    assert result["name"] == "test"
    assert result["value"] == 123

def test_json_parser_rejects_invalid_json():
    # Arrange
    parser = JSONParser()
    invalid_json = '{"name": "test", value: 123}'  # Missing quotes
    
    # Act
    result, error = parser.parse_string(invalid_json)
    
    # Assert
    assert result is None
    assert error is not None
    assert "JSON syntax error" in error.message
```

### Test Data

Test data files are stored in the `tests/fixtures/` directory, organized by test category:

- `tests/fixtures/json/`: Sample JSON files of various structures
- `tests/fixtures/excel/`: Expected Excel output files

Use these fixtures in your tests to ensure consistent test data across the test suite.

### Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline runs on every pull request and push to main branches, performing:

1. Linting with Flake8
2. Formatting check with Black
3. Running the test suite
4. Generating coverage reports

Pull requests cannot be merged if the CI pipeline fails.

## Documentation

Documentation is a critical part of the JSON to Excel Conversion Tool. This section covers how documentation is organized and how to contribute to it.

### Documentation Structure

The project documentation is organized as follows:

- **README.md**: Project overview and quick start
- **docs/installation.md**: Installation instructions
- **docs/user_guide.md**: User documentation
- **docs/developer_guide.md**: This developer guide
- **docs/architecture.md**: Detailed architecture documentation
- **docs/api_reference.md**: API reference for programmatic usage
- **docs/examples/**: Example usage scenarios

In addition, each module and function should have appropriate docstrings.

### Writing Documentation

When writing documentation:

- Use clear, concise language
- Include examples where appropriate
- Keep code samples up-to-date
- Use proper Markdown formatting
- Include diagrams for complex concepts (using Mermaid syntax)

Documentation should be updated whenever related code changes.

### Docstrings

Use Google-style docstrings for all modules, classes, and functions:

```python
def transform_json(json_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Transform JSON data into a pandas DataFrame.
    
    This function converts JSON data into a tabular format suitable for Excel output.
    It handles nested structures and arrays according to the specified options.
    
    Args:
        json_data: The JSON data to transform as a dictionary
        options: Optional transformation options with the following keys:
            - array_handling: How to handle arrays ('expand' or 'join')
            - separator: Separator for nested paths (default: '.')
    
    Returns:
        A pandas DataFrame containing the transformed data
        
    Raises:
        ValueError: If json_data is None or empty
        TransformationError: If the transformation fails
        
    Example:
        >>> data = {"name": "John", "address": {"city": "New York"}}
        >>> transform_json(data)
           name address.city
        0  John    New York
    """
```

### API Documentation

The API reference documentation is generated from docstrings and maintained in `docs/api_reference.md`. When adding or modifying public APIs, ensure the docstrings are complete and accurate.

## Contributing Guidelines

This section provides guidelines for contributing to the JSON to Excel Conversion Tool.

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment as described in [Development Environment Setup](#development-environment-setup)
4. Create a new branch for your changes
5. Make your changes following the coding standards
6. Write or update tests as needed
7. Update documentation as needed
8. Submit a pull request

### Types of Contributions

There are many ways to contribute to the project:

- **Bug fixes**: Fixing issues in the existing code
- **Feature additions**: Implementing new functionality
- **Documentation improvements**: Enhancing or correcting documentation
- **Test additions**: Improving test coverage
- **Performance improvements**: Optimizing existing code

All contributions are welcome and appreciated.

### Reporting Issues

When reporting issues:

1. Check if the issue already exists
2. Use the issue template
3. Provide a clear description of the problem
4. Include steps to reproduce
5. Include relevant information about your environment
6. If possible, suggest a solution

### Code Review Process

All pull requests undergo code review before being merged:

1. Automated checks must pass (linting, tests)
2. At least one maintainer must approve the changes
3. Feedback must be addressed before merging
4. Changes may require multiple iterations

The review process ensures code quality and consistency across the project.

## API Reference

For detailed API documentation, see the [API Reference](api_reference.md) document. This section provides a high-level overview of the main APIs.

### Backend API

The backend module provides the core conversion functionality:

```python
from json_to_excel.backend import convert_json_to_excel

# Basic conversion
result, error = convert_json_to_excel('data.json', 'output.xlsx')

# With options
from json_to_excel.backend.models.excel_options import ExcelOptions

options = ExcelOptions(
    sheet_name='Data',
    array_handling='join',
    format_as_table=True
)
result, error = convert_json_to_excel('data.json', 'output.xlsx', options)
```

### Component APIs

For more fine-grained control, you can use the individual component APIs:

```python
from json_to_excel.backend.input_handler import InputHandler
from json_to_excel.backend.json_parser import JSONParser
from json_to_excel.backend.data_transformer import DataTransformer
from json_to_excel.backend.excel_generator import ExcelGenerator

# Create component instances
input_handler = InputHandler()
parser = JSONParser()
transformer = DataTransformer()
generator = ExcelGenerator()

# Process step by step
json_content, error = input_handler.read_json_file('data.json')
if not error:
    json_data, error = parser.parse_string(json_content)
    if not error:
        dataframe, error = transformer.transform_data(json_data)
        if not error:
            success, error = generator.generate_excel(dataframe, 'output.xlsx')
```

### CLI API

The CLI module provides command-line functionality:

```python
from json_to_excel.cli.command_runner import run_cli

# Run a CLI command programmatically
exit_code = run_cli(['convert', 'data.json', 'output.xlsx', '--verbose'])
```

### Web API

The web module provides a Flask application:

```python
from json_to_excel.web.app import create_app

# Create and configure the Flask app
app = create_app('development')

# Run the app
app.run(host='0.0.0.0', port=5000)
```

## Troubleshooting

This section provides solutions to common development issues.

### Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError` when importing project modules

**Solution**: Ensure you've installed the package in development mode:
```bash
pip install -e .
```

### Test Failures

**Problem**: Tests fail with path-related errors

**Solution**: Run tests from the project root directory, not from subdirectories

### Pre-commit Hook Failures

**Problem**: Pre-commit hooks fail with formatting errors

**Solution**: Run Black manually to format your code:
```bash
black src/ tests/
```

### Debugging Tips

### Using the Python Debugger

You can use the built-in Python debugger (pdb) to debug issues:

```python
import pdb; pdb.set_trace()
```

### Verbose Logging

Enable verbose logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debugging Tests

Run pytest with the `-v` flag for verbose output and `--pdb` to enter the debugger on failure:

```bash
pytest -v --pdb
```

### Getting Help

If you encounter issues not covered here:

1. Check the project's GitHub Issues for similar problems
2. Search the project's discussions or forums
3. Reach out to the maintainers via GitHub Issues
4. Join the project's communication channels (if available)