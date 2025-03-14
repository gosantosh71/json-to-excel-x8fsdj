# JSON to Excel Conversion Tool

[![Build Status](https://img.shields.io/github/workflow/status/organization/json-to-excel-converter/build)](https://github.com/organization/json-to-excel-converter/actions)
[![Version](https://img.shields.io/pypi/v/json-to-excel-converter.svg)](https://pypi.org/project/json-to-excel-converter/)
[![License](https://img.shields.io/github/license/organization/json-to-excel-converter.svg)](https://github.com/organization/json-to-excel-converter/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/json-to-excel-converter.svg)](https://pypi.org/project/json-to-excel-converter/)

A powerful Python utility for converting JSON data files into structured Excel spreadsheets, supporting both flat and nested JSON structures.

![Logo](src/web/static/img/logo.png)

## Introduction

The JSON to Excel Conversion Tool addresses the common business challenge of converting semi-structured JSON data into tabular formats that are more accessible for analysis, reporting, and data manipulation. It significantly reduces the time and technical expertise required to transform JSON data into Excel format, enabling faster data analysis and decision-making processes.

### Key Benefits

- **Simplifies data extraction** from JSON sources
- **Eliminates manual conversion efforts**
- **Standardizes output format** for consistent reporting
- **Handles complex nested structures** automatically
- **Supports both technical and non-technical users**

## Features

- **JSON File Processing**: Read and validate JSON files from the local filesystem
- **Nested JSON Flattening**: Convert complex nested JSON structures into flat tabular format
  - Automatically handles nested objects with dot notation (e.g., `user.address.city`)
  - Properly formats arrays of objects as multiple rows
  - Handles arrays of primitive values with flexible options
- **Excel File Generation**: Create properly formatted Excel files with appropriate column headers
- **Command Line Interface**: Simple command-line tool for technical users and automation
- **Web Interface (Optional)**: Browser-based interface for non-technical users
- **Comprehensive Error Handling**: Clear error messages and validation for troubleshooting
- **Performance Optimized**: Efficiently processes files up to 5MB in size

## Installation

### Option 1: Python Package (PyPI)

```bash
# Basic installation
pip install json-to-excel-converter

# Install with optional web interface support
pip install json-to-excel-converter[web]
```

### Option 2: Standalone Executable

Download the appropriate executable for your platform from the [releases page](https://github.com/organization/json-to-excel-converter/releases).

**Windows:**
- Download the `.exe` installer
- Run the installer and follow the prompts
- Launch from the Start Menu

**macOS:**
- Download the `.dmg` file
- Open and drag to Applications folder
- Launch from Applications

**Linux:**
- Download the `.AppImage` or `.deb`/`.rpm` package
- Make executable (`chmod +x`) or install the package
- Run from terminal or application launcher

### Option 3: Docker

```bash
# Pull the image
docker pull organization/json-to-excel-converter:latest

# Run with volume mount for file access
docker run -v $(pwd):/data organization/json-to-excel-converter:latest /data/input.json /data/output.xlsx
```

### Option 4: From Source

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter

# Install in development mode
pip install -e .
```

## Usage

### Command Line Interface

The basic command format is:

```bash
python json_to_excel.py <input_json_file> <output_excel_file> [options]
```

**Basic usage:**

```bash
python json_to_excel.py data.json output.xlsx
```

**With options:**

```bash
python json_to_excel.py data.json output.xlsx --sheet-name="Customer Data" --array-handling=join --verbose
```

**If installed as a package:**

```bash
json2excel data.json output.xlsx
```

### Python API

You can also use the tool programmatically in your Python code:

```python
from json_to_excel import convert_json_to_excel

convert_json_to_excel('data.json', 'output.xlsx')
```

### Web Interface (Optional)

If you installed with web interface support:

1. Start the web server:
   ```bash
   json2excel-web
   ```

2. Open your browser and navigate to `http://localhost:5000`
3. Upload your JSON file using the web interface
4. Configure conversion options
5. Click "Convert to Excel" and download the result

## Command Line Interface

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| input_json_file | Path to the JSON file to convert | `data.json` |
| output_excel_file | Path where the Excel file will be saved | `output.xlsx` |

### Optional Arguments

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| --sheet-name | Custom name for Excel worksheet | Sheet1 | `--sheet-name="Customer Data"` |
| --array-handling | How to handle arrays (expand/join) | expand | `--array-handling=join` |
| --verbose | Enable detailed output | False | `--verbose` |
| --help | Show help message | N/A | `--help` |

### Examples

**Convert a simple JSON file:**
```bash
python json_to_excel.py customer.json customers.xlsx
```

**Specify a custom sheet name:**
```bash
python json_to_excel.py customer.json customers.xlsx --sheet-name="Customer List"
```

**Join array values instead of expanding to rows:**
```bash
python json_to_excel.py products.json products.xlsx --array-handling=join
```

**Show detailed processing information:**
```bash
python json_to_excel.py large-data.json output.xlsx --verbose
```

## Web Interface

The optional web interface provides a user-friendly way to convert JSON files without using the command line.

### Features

- **File Upload**: Drag and drop or select JSON files to upload
- **Conversion Options**: Configure the same options as the CLI version
- **Progress Tracking**: Visual feedback during the conversion process
- **Download Results**: Easily download the converted Excel files
- **Error Handling**: User-friendly error messages with troubleshooting tips

### Starting the Web Interface

```bash
# If installed as a package
json2excel-web

# Or from source
python -m json_to_excel.web
```

Then open your browser and navigate to `http://localhost:5000`.

## Examples

### Converting a Flat JSON Structure

Input JSON:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30,
  "active": true
}
```

Command:
```bash
python json_to_excel.py user.json user.xlsx
```

Result: Excel file with columns for id, name, email, age, and active.

### Converting Nested JSON Structure

Input JSON:
```json
{
  "id": 1,
  "name": "John Doe",
  "contact": {
    "email": "john.doe@example.com",
    "phone": "555-1234"
  },
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345"
  }
}
```

Command:
```bash
python json_to_excel.py user.json user.xlsx
```

Result: Excel file with columns for id, name, contact.email, contact.phone, address.street, address.city, address.state, and address.zip.

### Converting JSON with Arrays

Input JSON:
```json
{
  "id": 1,
  "name": "John Doe",
  "orders": [
    {"id": 101, "product": "Laptop", "price": 999.99},
    {"id": 102, "product": "Mouse", "price": 24.99}
  ]
}
```

Command (expand arrays to rows):
```bash
python json_to_excel.py user.json user.xlsx --array-handling=expand
```

Result: Excel file with two rows, each containing user information along with the respective order details.

Command (join array values):
```bash
python json_to_excel.py user.json user.xlsx --array-handling=join
```

Result: Excel file with arrays represented as comma-separated values in single cells.

## Documentation

For more detailed information, please refer to:

- [User Guide](docs/user_guide.md) - Detailed usage instructions
- [API Documentation](docs/api.md) - API reference for programmatic usage
- [Examples](docs/examples/) - Additional examples and use cases
- [FAQ](docs/faq.md) - Frequently asked questions

## Development

### Prerequisites

- Python 3.9 or higher
- pip

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Code Style

This project uses:
- [Black](https://black.readthedocs.io/) for code formatting
- [Flake8](https://flake8.pycqa.org/) for linting

```bash
# Format code
black .

# Run linting
flake8
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Testing

The project uses [pytest](https://pytest.org/) for testing.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=json_to_excel tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pandas](https://pandas.pydata.org/) - Data manipulation library
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file generation
- All contributors who have helped shape this project