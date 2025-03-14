# JSON to Excel Conversion Tool - User Guide

This comprehensive user guide provides detailed instructions for using the JSON to Excel Conversion Tool, a utility designed to transform JSON data files into structured Excel spreadsheets. Whether you're working with simple flat JSON or complex nested structures, this guide will help you effectively use all features of the tool.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Command Line Interface](#command-line-interface)
- [Web Interface](#web-interface)
- [Working with JSON Structures](#working-with-json-structures)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Reference](#reference)

## Introduction

The JSON to Excel Conversion Tool is a Python-based utility designed to transform JSON data files into structured Excel spreadsheets. This tool addresses the common business challenge of converting semi-structured JSON data into tabular formats that are more accessible for analysis, reporting, and data manipulation.

### Key Features

- **JSON File Processing**: Read and validate JSON files from the local filesystem
- **Nested JSON Flattening**: Convert complex nested JSON structures into tabular format
- **Array Handling**: Process JSON arrays by converting them to multiple rows or columns
- **Excel File Generation**: Create properly formatted Excel files with appropriate column headers
- **Command Line Interface**: Scriptable interface for technical users and automation
- **Web Interface (Optional)**: Browser-based interface for non-technical users

### Use Cases

- Converting API responses from JSON to Excel for analysis
- Transforming JSON configuration files into readable spreadsheets
- Processing JSON exports from NoSQL databases for reporting
- Preparing JSON data for import into systems that accept Excel

## Installation

The JSON to Excel Conversion Tool can be installed using several methods depending on your needs and environment. For detailed installation instructions, please refer to the [Installation Guide](installation.md).

### Quick Installation

```bash
# Install using pip (recommended)
pip install json-to-excel-converter

# Install with web interface support
pip install json-to-excel-converter[web]
```

Alternatively, you can download standalone executables for Windows, macOS, or Linux from the [releases page](https://github.com/organization/json-to-excel-converter/releases).

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 20.04+
- **Python Version**: 3.9 or higher (for Python package installation)
- **Disk Space**: 100 MB minimum
- **Memory**: 512 MB minimum (2+ GB recommended for large files)

## Getting Started

This section provides a quick introduction to using the JSON to Excel Conversion Tool for basic conversion tasks. For more detailed examples, see the [Basic Conversion Examples](examples/basic_conversion.md).

### Basic Usage

To convert a JSON file to Excel using the command line interface:

```bash
json2excel convert data.json output.xlsx
```

This command reads the JSON file `data.json` and creates an Excel file `output.xlsx` with the converted data.

### Verifying Installation

To verify that the tool is installed correctly, run:

```bash
json2excel --version
```

This should display the version number of the installed tool.

## Command Line Interface

The Command Line Interface (CLI) provides a powerful and scriptable way to use the JSON to Excel Conversion Tool. This section covers the available commands, options, and usage patterns.

### Command Structure

```
json2excel <command> [options] [arguments]
```

### Available Commands

- `convert`: Convert a JSON file to Excel format
- `validate`: Validate a JSON file without conversion
- `info`: Display information about a JSON file
- `help`: Display help information

### Convert Command

The `convert` command is the primary function of the tool, transforming JSON files to Excel format.

```bash
json2excel convert <input_json_file> <output_excel_file> [options]
```

#### Options

- `--sheet-name NAME`: Custom name for the Excel worksheet (default: "Sheet1")
- `--array-handling {expand|join}`: How to handle arrays in JSON (default: expand)
- `--array-separator SEP`: Separator for joined arrays (default: ", ")
- `--separator SEP`: Separator for nested paths (default: ".")
- `--fields FIELDS`: Comma-separated list of fields to include
- `--max-depth N`: Maximum nesting depth to process (default: 10)
- `--chunk-size N`: Process large files in chunks of N records
- `--format-as-table`: Apply Excel table formatting
- `--auto-column-width`: Automatically adjust column widths
- `--freeze-header`: Freeze the header row
- `--verbose`: Enable detailed output

### Validate Command

The `validate` command checks if a JSON file is valid without performing conversion.

```bash
json2excel validate <json_file>
```

### Info Command

The `info` command displays information about a JSON file's structure.

```bash
json2excel info <json_file>
```

### Help Command

The `help` command displays general help or command-specific help.

```bash
# General help
json2excel help

# Command-specific help
json2excel help convert
```

### Examples

```bash
# Basic conversion
json2excel convert data.json output.xlsx

# Custom sheet name
json2excel convert data.json output.xlsx --sheet-name="Customer Data"

# Join arrays as text
json2excel convert data.json output.xlsx --array-handling=join

# Select specific fields
json2excel convert data.json output.xlsx --fields="id,name,address.city"

# Process large file in chunks
json2excel convert large_data.json output.xlsx --chunk-size=1000

# Apply Excel formatting
json2excel convert data.json output.xlsx --format-as-table --auto-column-width
```

## Web Interface

The optional Web Interface provides a user-friendly, browser-based way to use the JSON to Excel Conversion Tool. This section covers how to start the web interface and use its features.

### Starting the Web Interface

If you installed the tool with web interface support, you can start the web server with:

```bash
json2excel-web
```

Then access the interface in your web browser at: http://localhost:5000

### Using the Web Interface

1. **Upload JSON File**: Drag and drop your JSON file onto the upload area or click to browse
2. **Configure Options**: Set conversion options such as sheet name and array handling
3. **Convert**: Click the "Convert to Excel" button to process the file
4. **Download**: Once processing is complete, download the resulting Excel file

### Web Interface Features

- **Drag and Drop**: Easy file uploading with drag and drop support
- **Progress Tracking**: Visual feedback during conversion process
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Clear error messages with troubleshooting suggestions

### Configuration Options

The web interface provides the following configuration options:

- **Sheet Name**: Custom name for the Excel worksheet
- **Array Handling**: Choose between expanding arrays into rows or joining as text
- **Advanced Options**: Access to additional conversion settings

### Security Considerations

The web interface is designed for local use by default. If you plan to deploy it on a network:

- Limit access to trusted users
- Consider adding authentication
- Be aware of file size limitations
- Review the security documentation for additional measures

## Working with JSON Structures

The JSON to Excel Conversion Tool can handle various JSON structures, from simple flat objects to complex nested hierarchies. This section explains how different JSON structures are processed.

### Flat JSON

Flat JSON structures (simple key-value pairs) are converted directly to Excel with one row per object and columns for each key.

**Example JSON:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30,
  "active": true
}
```

**Resulting Excel:**

| id | name     | email               | age | active |
|----|----------|---------------------|-----|--------|
| 1  | John Doe | john.doe@example.com| 30  | TRUE   |

### Nested JSON

Nested JSON structures (objects within objects) are flattened using dot notation for column names. For detailed information, see [Handling Nested JSON](examples/handling_nested_json.md).

**Example JSON:**
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
    "state": "CA"
  }
}
```

**Resulting Excel:**

| id | name     | contact.email        | contact.phone | address.street | address.city | address.state |
|----|----------|----------------------|---------------|----------------|--------------|---------------|
| 1  | John Doe | john.doe@example.com | 555-1234      | 123 Main St    | Anytown      | CA            |

### Arrays

JSON arrays can be handled in two ways:

1. **Expand** (default): Creates multiple rows, one for each array element
2. **Join**: Combines array elements into a single cell with a separator

**Example JSON with Array:**
```json
{
  "id": 1,
  "name": "John Doe",
  "tags": ["customer", "premium", "active"]
}
```

**Expand Mode Result:**

| id | name     | tags     |
|----|----------|----------|
| 1  | John Doe | customer |
| 1  | John Doe | premium  |
| 1  | John Doe | active   |

**Join Mode Result:**

| id | name     | tags                       |
|----|----------|----------------------------|
| 1  | John Doe | customer, premium, active  |

### Arrays of Objects

Arrays containing objects are expanded into multiple rows with the object properties as columns.

**Example JSON:**
```json
{
  "id": 1,
  "name": "John Doe",
  "orders": [
    {
      "id": 101,
      "product": "Laptop",
      "price": 999.99
    },
    {
      "id": 102,
      "product": "Mouse",
      "price": 24.99
    }
  ]
}
```

**Resulting Excel:**

| id | name     | orders.id | orders.product | orders.price |
|----|----------|-----------|----------------|-------------|
| 1  | John Doe | 101       | Laptop         | 999.99      |
| 1  | John Doe | 102       | Mouse          | 24.99       |

## Advanced Features

The JSON to Excel Conversion Tool includes several advanced features for handling complex scenarios and customizing the output. This section covers these features in detail.

### Field Selection

You can select specific fields to include in the output using the `--fields` option:

```bash
json2excel convert data.json output.xlsx --fields="id,name,contact.email,address.city"
```

This is useful for large JSON structures where you only need certain fields.

### Custom Separators

By default, nested paths use a dot (`.`) as a separator. You can customize this with the `--separator` option:

```bash
json2excel convert data.json output.xlsx --separator="_"
```

This would convert nested paths like `address.city` to `address_city` in the Excel output.

### Excel Formatting

The tool provides several options for formatting the Excel output:

```bash
# Format as an Excel table with filtering
json2excel convert data.json output.xlsx --format-as-table

# Automatically adjust column widths
json2excel convert data.json output.xlsx --auto-column-width

# Freeze the header row
json2excel convert data.json output.xlsx --freeze-header
```

### Processing Large Files

For large JSON files, you can use chunked processing to manage memory usage:

```bash
json2excel convert large_data.json output.xlsx --chunk-size=1000
```

This processes the file in chunks of 1000 records at a time, reducing peak memory usage.

### Batch Processing

To convert multiple JSON files at once, you can use batch processing. See [Batch Processing Examples](examples/batch_processing.md) for detailed instructions.

### Programmatic Usage

The tool can be used programmatically in your Python code:

```python
from json_to_excel import convert_json_to_excel

# Basic conversion
convert_json_to_excel('data.json', 'output.xlsx')

# With options
convert_json_to_excel(
    'data.json',
    'output.xlsx',
    sheet_name='Customer Data',
    array_handling='join',
    format_as_table=True
)
```

For complete API documentation, see the [API Reference](api_reference.md).

## Troubleshooting

This section provides solutions to common issues you might encounter when using the JSON to Excel Conversion Tool.

### Common Error Messages

#### "File not found"

**Problem**: The specified JSON file could not be found.

**Solution**: Check the file path and ensure the file exists. Use absolute paths if necessary.

#### "Invalid JSON format"

**Problem**: The JSON file contains syntax errors.

**Solution**: Validate your JSON using a JSON validator. Common issues include missing commas, unquoted keys, or trailing commas.

#### "Memory error during processing"

**Problem**: The JSON file is too large to process in memory.

**Solution**: Use the `--chunk-size` option to process the file in smaller segments:

```bash
json2excel convert large_data.json output.xlsx --chunk-size=1000
```

#### "Excel row limit exceeded"

**Problem**: The resulting data exceeds Excel's limit of 1,048,576 rows.

**Solution**: Filter the data to reduce the number of rows, or split the output into multiple sheets/files.

### Performance Issues

#### Slow Processing for Large Files

**Problem**: Processing large JSON files takes a long time.

**Solutions**:
- Use chunked processing with `--chunk-size`
- Select only necessary fields with `--fields`
- Reduce the maximum nesting depth with `--max-depth`

#### High Memory Usage

**Problem**: The tool uses too much memory when processing files.

**Solutions**:
- Use chunked processing with `--chunk-size`
- Close other memory-intensive applications
- Upgrade your system's RAM if processing very large files regularly

### Installation Issues

#### Package Dependencies

**Problem**: Missing dependencies during installation.

**Solution**: Ensure you have the required dependencies:

```bash
pip install pandas openpyxl
```

#### Permission Errors

**Problem**: Permission denied when installing or running the tool.

**Solutions**:
- On Windows: Run the command prompt as Administrator
- On macOS/Linux: Use `sudo` or set up a virtual environment

### Getting Help

If you encounter issues not covered here:

1. Run the command with `--verbose` to get more detailed output
2. Check the logs for error details
3. Consult the [FAQ](#faq) section
4. Report issues on the project's GitHub repository

## FAQ

### General Questions

#### Q: What types of JSON files can the tool convert?
A: The tool can convert any valid JSON file, including flat structures, nested objects, and arrays. It handles both simple and complex hierarchical data.

#### Q: Is there a size limit for JSON files?
A: The tool is designed to handle files up to 5MB by default. Larger files can be processed using the chunked processing feature (`--chunk-size` option).

#### Q: Can I convert multiple JSON files at once?
A: Yes, you can use batch processing to convert multiple files. See the [Batch Processing Examples](examples/batch_processing.md) for details.

### Conversion Questions

#### Q: How are nested JSON structures handled?
A: Nested objects are flattened using dot notation for column names. For example, `{"address":{"city":"New York"}}` becomes a column named `address.city`.

#### Q: How are arrays handled in the conversion?
A: By default, arrays are expanded into multiple rows. Alternatively, you can use the `--array-handling=join` option to combine array elements into a single cell with a separator.

#### Q: Can I customize the Excel output format?
A: Yes, the tool provides several formatting options including table formatting, column width adjustment, and header freezing. See the [Advanced Features](#advanced-features) section.

#### Q: How are data types preserved in Excel?
A: The tool attempts to preserve appropriate data types in Excel. Numbers remain as numbers, booleans as booleans, etc. Dates in ISO format are converted to Excel date format.

### Technical Questions

#### Q: Can I use the tool in my own Python scripts?
A: Yes, the tool can be imported and used programmatically. See the [Programmatic Usage](#programmatic-usage) section and the [API Reference](api_reference.md).

#### Q: Does the tool support Excel's .xls format?
A: No, the tool generates .xlsx files (Excel 2007 and newer) only, as the older .xls format has significant limitations.

#### Q: Can I convert Excel back to JSON?
A: The current version only supports JSON to Excel conversion. Excel to JSON conversion is not supported.

#### Q: Is the web interface secure for production use?
A: The web interface is designed primarily for local use. For production deployment, additional security measures should be implemented, such as authentication and HTTPS.

## Reference

### Command Line Reference

```
json2excel <command> [options] [arguments]
```

#### Global Options

- `--version`: Show the version number and exit
- `--help`: Show help message and exit
- `--verbose`: Enable detailed output

#### Convert Command

```
json2excel convert <input_json_file> <output_excel_file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|--------|
| `--sheet-name NAME` | Custom name for Excel worksheet | Sheet1 |
| `--array-handling {expand|join}` | How to handle arrays | expand |
| `--array-separator SEP` | Separator for joined arrays | ", " |
| `--separator SEP` | Separator for nested paths | "." |
| `--fields FIELDS` | Comma-separated list of fields to include | All fields |
| `--max-depth N` | Maximum nesting depth to process | 10 |
| `--chunk-size N` | Process large files in chunks | None |
| `--format-as-table` | Apply Excel table formatting | False |
| `--auto-column-width` | Automatically adjust column widths | False |
| `--freeze-header` | Freeze the header row | False |

#### Validate Command

```
json2excel validate <json_file>
```

#### Info Command

```
json2excel info <json_file>
```

### Related Documentation

- [Installation Guide](installation.md): Detailed installation instructions
- [Basic Conversion Examples](examples/basic_conversion.md): Simple usage examples
- [Handling Nested JSON](examples/handling_nested_json.md): Working with complex structures
- [Batch Processing Examples](examples/batch_processing.md): Processing multiple files
- [API Reference](api_reference.md): Programmatic usage documentation

### External Resources

- [JSON Specification](https://www.json.org/): Official JSON format documentation
- [Excel File Format](https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-xlsx/): Microsoft Excel file format documentation
- [Pandas Documentation](https://pandas.pydata.org/docs/): Documentation for the Pandas library used internally
- [openpyxl Documentation](https://openpyxl.readthedocs.io/): Documentation for the Excel library used internally