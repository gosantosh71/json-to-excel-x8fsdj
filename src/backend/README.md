# JSON to Excel Conversion Tool - Backend

![Tests](https://github.com/organization/json-to-excel-converter/workflows/backend-tests/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

## Introduction

The backend component of the JSON to Excel Conversion Tool provides the core functionality for converting JSON files to Excel format. It handles JSON parsing, data transformation, and Excel file generation through a modular pipeline architecture.

### Key Features

- JSON file reading and validation
- Support for both flat and nested JSON structures
- Automatic flattening of nested objects with dot notation
- Array normalization (expansion to rows or joining as text)
- Excel file generation with proper formatting
- Comprehensive error handling and reporting

## Architecture

The backend follows a pipeline architecture with these key components:

### Input Handler
Manages file access and initial validation of JSON input files.
- Verifies file existence and read permissions
- Validates file extension and basic format
- Reads file content into memory
- Handles file access errors gracefully

### JSON Parser
Validates and parses JSON content into Python data structures.
- Parses JSON strings into Python dictionaries/lists
- Validates JSON syntax and structure
- Detects and reports parsing errors
- Analyzes JSON structure (flat vs. nested)

### Data Transformer
Converts parsed JSON data into tabular format suitable for Excel.
- Flattens nested JSON structures using dot notation
- Normalizes arrays into appropriate tabular representation
- Handles different data types appropriately
- Creates a consistent tabular structure using Pandas

### Excel Generator
Creates and formats Excel files from transformed data.
- Generates Excel workbook and worksheets
- Creates appropriate column headers
- Writes data with proper formatting
- Saves Excel file to filesystem

### Error Handler
Manages error detection and reporting across all components.
- Processes exceptions from all pipeline components
- Provides contextual error messages
- Logs detailed error information
- Suggests resolution steps where possible

## Installation

### Requirements

- Python 3.9 or higher
- pip 21.0 or higher

### Setting up the development environment

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/json-to-excel-converter.git
   cd json-to-excel-converter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

   This will install the package in development mode with all required dependencies.

### Dependencies

- **pandas (v1.5.0+)**: Data manipulation and transformation
- **openpyxl (v3.1.0+)**: Excel file generation
- **pytest (v7.3.0+)**: Testing framework (dev dependency)
- **flake8 (v6.0.0+)**: Code linting (dev dependency)
- **black (v23.1.0+)**: Code formatting (dev dependency)

## Usage

### Basic Usage

```python
from json_to_excel.input_handler import InputHandler
from json_to_excel.json_parser import JSONParser
from json_to_excel.data_transformer import DataTransformer
from json_to_excel.excel_generator import ExcelGenerator

# Create the pipeline components
input_handler = InputHandler()
json_parser = JSONParser()
data_transformer = DataTransformer()
excel_generator = ExcelGenerator()

# Process a JSON file
json_content = input_handler.read_json_file('data.json')
parsed_json = json_parser.parse_json(json_content)
dataframe = data_transformer.transform_data(parsed_json)
excel_generator.generate_excel(dataframe, 'output.xlsx')
```

### Using the complete pipeline

```python
from json_to_excel.core import JsonToExcelConverter

# Create converter instance
converter = JsonToExcelConverter()

# Convert a file with default settings
converter.convert('data.json', 'output.xlsx')

# Convert with custom options
converter.convert(
    'data.json', 
    'output.xlsx',
    sheet_name='Data',
    array_handling='join'
)
```

### Error handling

```python
from json_to_excel.core import JsonToExcelConverter
from json_to_excel.exceptions import JsonToExcelError

converter = JsonToExcelConverter()

try:
    converter.convert('data.json', 'output.xlsx')
    print("Conversion successful!")
except JsonToExcelError as e:
    print(f"Error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Suggested action: {e.suggested_action}")
```

## API Reference

### Input Handler

```python
class InputHandler:
    def read_json_file(file_path: str) -> str:
        """
        Read and return the contents of a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            String containing the file contents
            
        Raises:
            FileSystemError: If the file cannot be read or doesn't exist
        """
        
    def validate_file(file_path: str) -> bool:
        """
        Validate if the file exists and has the correct extension.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if the file is valid, False otherwise
        """
```

### JSON Parser

```python
class JSONParser:
    def parse_json(json_content: str) -> dict:
        """
        Parse JSON string into a Python dictionary.
        
        Args:
            json_content: JSON string to parse
            
        Returns:
            Parsed JSON as a Python dictionary
            
        Raises:
            JSONParsingError: If the JSON is invalid or malformed
        """
        
    def analyze_structure(parsed_json: dict) -> JSONComplexity:
        """
        Analyze the structure of parsed JSON.
        
        Args:
            parsed_json: Parsed JSON as a Python dictionary
            
        Returns:
            JSONComplexity object containing structure information
        """
```

### Data Transformer

```python
class DataTransformer:
    def transform_data(parsed_json: dict) -> DataFrame:
        """
        Transform parsed JSON into a pandas DataFrame.
        
        Args:
            parsed_json: Parsed JSON as a Python dictionary
            
        Returns:
            Pandas DataFrame with flattened data
            
        Raises:
            TransformationError: If transformation fails
        """
        
    def flatten_nested_json(parsed_json: dict) -> dict:
        """
        Flatten nested JSON structure using dot notation.
        
        Args:
            parsed_json: Parsed JSON as a Python dictionary
            
        Returns:
            Flattened dictionary with dot notation paths
        """
        
    def process_arrays(json_with_arrays: dict, mode: str = 'expand') -> dict:
        """
        Process arrays in JSON structure.
        
        Args:
            json_with_arrays: JSON containing arrays
            mode: How to handle arrays ('expand' or 'join')
            
        Returns:
            Processed data with arrays handled according to mode
        """
```

### Excel Generator

```python
class ExcelGenerator:
    def generate_excel(dataframe: DataFrame, output_path: str) -> bool:
        """
        Generate Excel file from DataFrame.
        
        Args:
            dataframe: Pandas DataFrame to convert
            output_path: Path where Excel file will be saved
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ExcelGenerationError: If Excel generation fails
        """
        
    def format_excel(workbook: Workbook) -> Workbook:
        """
        Apply formatting to Excel workbook.
        
        Args:
            workbook: Excel workbook to format
            
        Returns:
            Formatted workbook
        """
```

## Configuration

The backend can be configured using a configuration file or environment variables.

### Configuration File

Create a `config.json` file in the application directory:

```json
{
  "system": {
    "max_file_size": 5242880,
    "max_nesting_level": 10,
    "temp_directory": "./temp",
    "log_level": "INFO",
    "log_file": "json_to_excel.log"
  },
  "conversion": {
    "array_handling": "expand",
    "default_sheet_name": "Sheet1",
    "excel_format": "xlsx"
  }
}
```

### Environment Variables

Configuration can also be set using environment variables:

- `JSON2EXCEL_MAX_FILE_SIZE`: Maximum file size in bytes
- `JSON2EXCEL_LOG_LEVEL`: Logging level
- `JSON2EXCEL_TEMP_DIR`: Temporary directory path
- `JSON2EXCEL_ARRAY_HANDLING`: Array handling method

### Programmatic Configuration

```python
from json_to_excel.core import JsonToExcelConverter
from json_to_excel.config import Configuration

# Create custom configuration
config = Configuration()
config.set("max_file_size", 10485760)  # 10MB
config.set("array_handling", "join")

# Create converter with custom configuration
converter = JsonToExcelConverter(config=config)
```

## Testing

The backend uses pytest for testing. The test suite includes unit tests, integration tests, and end-to-end tests.

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run with coverage report
pytest --cov=json_to_excel tests/

# Run with verbose output
pytest -v
```

### Test Data

Test data is located in the `tests/data` directory:
- `tests/data/json/`: Sample JSON files for testing
- `tests/data/excel/`: Expected Excel output files
- `tests/data/invalid/`: Invalid JSON files for error testing

### Writing Tests

Follow these guidelines when writing tests:
- Place unit tests in `tests/unit/` directory
- Follow the naming convention `test_*.py`
- Create fixtures for common test setup
- Mock external dependencies
- Aim for high test coverage (>90%)

## Performance Considerations

### Handling Large Files

For large JSON files (>5MB), consider these strategies:

1. **Chunked Processing**: For files that don't fit in memory, use:
   ```python
   converter.convert('large.json', 'output.xlsx', chunk_size=1000)
   ```

2. **Memory Optimization**: Monitor memory usage with large nested structures:
   ```python
   import tracemalloc
   
   tracemalloc.start()
   converter.convert('large.json', 'output.xlsx')
   current, peak = tracemalloc.get_traced_memory()
   print(f"Current memory usage: {current / 10**6}MB")
   print(f"Peak memory usage: {peak / 10**6}MB")
   tracemalloc.stop()
   ```

3. **Progress Tracking**: For long-running conversions, use the progress callback:
   ```python
   def progress_callback(stage, percentage):
       print(f"Stage: {stage}, Completion: {percentage}%")
       
   converter.convert('large.json', 'output.xlsx', progress_callback=progress_callback)
   ```

### Performance Benchmarks

| File Size | Complexity | Conversion Time | Memory Usage |
|-----------|------------|-----------------|--------------|
| Small (<100KB) | Flat | <1 second | <50MB |
| Medium (1MB) | Nested | 2-5 seconds | 100-200MB |
| Large (5MB) | Complex | 5-15 seconds | 300-500MB |

## Contributing

We welcome contributions to the backend codebase!

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

We use:
- Black for code formatting
- Flake8 for linting
- Type hints whenever possible

```bash
# Format code
black json_to_excel tests

# Check style
flake8 json_to_excel tests
```

### Documentation

- Document all public functions, classes, and methods
- Follow Google-style docstrings
- Update the README when adding new features

### Commit Messages

Follow the conventional commits specification:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring
- `perf:` for performance improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.