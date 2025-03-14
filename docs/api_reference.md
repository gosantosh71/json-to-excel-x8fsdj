# JSON to Excel Conversion Tool API Reference

## Introduction

The JSON to Excel Conversion Tool provides multiple interfaces for converting JSON data to Excel format. This comprehensive API reference documents all the ways you can interact with the tool programmatically.

### API Overview

The tool offers three distinct APIs:

- **Core Conversion API**: A Python library API for direct integration into your Python applications
- **Command-Line Interface (CLI)**: A command-line tool for use in scripts and terminal environments
- **Web API**: RESTful HTTP endpoints for browser-based or remote integrations (optional component)

Each interface provides access to the same core conversion functionality with different interaction models suited to different use cases.

### API Versioning

The JSON to Excel Conversion Tool follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** version changes indicate incompatible API changes
- **MINOR** version changes add functionality in a backward-compatible manner
- **PATCH** version changes include backward-compatible bug fixes

API version information is available:
- Through the `version` attribute in the Core API
- Via the `--version` flag in the CLI
- From the `/api/version` endpoint in the Web API

## Core Conversion API

The Core Conversion API provides direct Python library access to the JSON to Excel conversion functionality.

### ConversionService

The main service class for converting JSON data to Excel format.

#### convert_json_to_excel

```python
convert_json_to_excel(input_path: str, output_path: str, excel_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]
```

Converts a JSON file to Excel format, handling the entire conversion process.

**Parameters:**
- `input_path` (str): Path to the input JSON file
- `output_path` (str): Path where the Excel file will be saved
- `excel_options` (Optional[Dict[str, Any]]): Optional configuration for Excel output

**Returns:**
- `Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]`: Success flag, conversion summary, and any error that occurred

**Example:**
```python
success, summary, error = conversion_service.convert_json_to_excel(
    'data.json', 
    'output.xlsx', 
    {'sheet_name': 'Data', 'array_handling': 'expand'}
)
```

#### convert_json_string_to_excel

```python
convert_json_string_to_excel(json_string: str, output_path: str, excel_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]
```

Converts a JSON string to Excel format, handling the entire conversion process.

**Parameters:**
- `json_string` (str): JSON content as a string
- `output_path` (str): Path where the Excel file will be saved
- `excel_options` (Optional[Dict[str, Any]]): Optional configuration for Excel output

**Returns:**
- `Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]`: Success flag, conversion summary, and any error that occurred

**Example:**
```python
success, summary, error = conversion_service.convert_json_string_to_excel(
    '{"name": "John"}', 
    'output.xlsx'
)
```

#### convert_json_to_excel_bytes

```python
convert_json_to_excel_bytes(input_path: str, excel_options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[ErrorResponse]]
```

Converts a JSON file to Excel format and returns the result as bytes.

**Parameters:**
- `input_path` (str): Path to the input JSON file
- `excel_options` (Optional[Dict[str, Any]]): Optional configuration for Excel output

**Returns:**
- `Tuple[Optional[bytes], Dict[str, Any], Optional[ErrorResponse]]`: Excel content as bytes, conversion summary, and any error that occurred

**Example:**
```python
excel_bytes, summary, error = conversion_service.convert_json_to_excel_bytes('data.json')
```

#### transform_json_to_dataframe

```python
transform_json_to_dataframe(json_data: JSONData, array_handling: str) -> Tuple[Optional[pandas.DataFrame], Optional[ErrorResponse]]
```

Transforms JSON data into a pandas DataFrame.

**Parameters:**
- `json_data` (JSONData): JSON data object to transform
- `array_handling` (str): Strategy for handling arrays ('expand' or 'join')

**Returns:**
- `Tuple[Optional[pandas.DataFrame], Optional[ErrorResponse]]`: The resulting DataFrame and any error that occurred

**Example:**
```python
dataframe, error = conversion_service.transform_json_to_dataframe(json_data, 'expand')
```

#### set_max_file_size

```python
set_max_file_size(max_file_size_mb: int) -> None
```

Sets the maximum file size limit for JSON input files.

**Parameters:**
- `max_file_size_mb` (int): Maximum file size in megabytes

**Returns:**
- `None`: Updates the file size limit in-place

**Example:**
```python
conversion_service.set_max_file_size(10)
```

#### set_max_nesting_level

```python
set_max_nesting_level(max_nesting_level: int) -> None
```

Sets the maximum nesting level for JSON structures.

**Parameters:**
- `max_nesting_level` (int): Maximum nesting level

**Returns:**
- `None`: Updates the nesting level limit in-place

**Example:**
```python
conversion_service.set_max_nesting_level(15)
```

### Excel Options

Configuration options for Excel output:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| sheet_name | str | "Sheet1" | Name of the worksheet in the Excel file |
| array_handling | str | "expand" | Strategy for handling arrays |
| header_style | dict | {"bold": True} | Styling for header row |
| auto_column_width | bool | True | Automatically adjust column widths |

**`array_handling` values:**
- `expand`: Expands arrays into multiple rows
- `join`: Joins array elements with commas in a single cell

### Error Handling

The Core API uses the `ErrorResponse` class to provide structured error information:

| Property | Type | Description |
|----------|------|-------------|
| message | str | Human-readable error message |
| error_code | int | Numeric error code |
| category | ErrorCategory | Category of the error |
| severity | ErrorSeverity | Severity level of the error |
| details | dict | Additional error details |

## Command-Line Interface

The Command-Line Interface (CLI) provides a terminal-based way to access the conversion functionality.

### Command Structure

```
python json_to_excel.py <command> [options]
```

### Commands

#### convert

Converts a JSON file to Excel format.

**Syntax:**
```
python json_to_excel.py convert <input_json_file> <output_excel_file> [options]
```

**Arguments:**
- `input_json_file`: Path to the JSON file to convert (required)
- `output_excel_file`: Path where the Excel file will be saved (required)

**Options:**
- `--sheet-name`: Name for the Excel worksheet (default: "Sheet1")
  - Example: `--sheet-name=Data`
- `--array-handling`: How to handle arrays in JSON (values: expand, join; default: expand)
  - Example: `--array-handling=join`
- `--verbose`: Enable detailed output
  - Example: `--verbose`

**Example:**
```
python json_to_excel.py convert data.json output.xlsx --sheet-name=CustomerData --verbose
```

#### validate

Validates a JSON file without converting it.

**Syntax:**
```
python json_to_excel.py validate <input_json_file> [options]
```

**Arguments:**
- `input_json_file`: Path to the JSON file to validate (required)

**Options:**
- `--verbose`: Enable detailed output
  - Example: `--verbose`

**Example:**
```
python json_to_excel.py validate data.json --verbose
```

#### info

Displays information about a JSON file.

**Syntax:**
```
python json_to_excel.py info <input_json_file> [options]
```

**Arguments:**
- `input_json_file`: Path to the JSON file to analyze (required)

**Options:**
- `--format`: Output format (values: text, json; default: text)
  - Example: `--format=json`
- `--verbose`: Enable detailed output
  - Example: `--verbose`

**Example:**
```
python json_to_excel.py info data.json --format=json
```

#### help

Displays help information.

**Syntax:**
```
python json_to_excel.py help [command]
```

**Arguments:**
- `command`: Command to get help for (optional)

**Example:**
```
python json_to_excel.py help convert
```

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Command-line argument error |
| 3 | File error (not found, permission denied, etc.) |
| 4 | JSON parsing error |
| 5 | Conversion error |

## Web API

The Web API provides RESTful endpoints for browser-based or remote access to the conversion functionality.

### API Endpoints

Base URL: `/api`

#### GET /health

Check API health status.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

#### GET /version

Get API version information.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "data": {
    "version": "1.0.0",
    "release_date": "2023-06-01"
  }
}
```

#### GET /docs

Get API documentation.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "data": {
    "endpoints": [...]
  }
}
```

### File Upload API

Base URL: `/api/uploads`

#### POST /

Upload a JSON file.

**Parameters:**
- `file` (file): JSON file to upload (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "file_id": "abc123",
    "filename": "data.json",
    "size": 1024
  }
}
```

#### GET /

List uploaded files.

**Parameters:**
- `status` (query): Filter by upload status (optional)

**Response:**
```json
{
  "status": "success",
  "data": {
    "uploads": [
      {
        "file_id": "abc123",
        "filename": "data.json"
      }
    ]
  }
}
```

#### GET /{file_id}

Get information about an uploaded file.

**Parameters:**
- `file_id` (path): ID of the uploaded file (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "file_id": "abc123",
    "filename": "data.json",
    "size": 1024,
    "upload_date": "2023-06-01T12:00:00Z"
  }
}
```

#### DELETE /{file_id}

Delete an uploaded file.

**Parameters:**
- `file_id` (path): ID of the uploaded file (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "File deleted successfully"
  }
}
```

#### POST /{file_id}/validate

Validate an uploaded JSON file.

**Parameters:**
- `file_id` (path): ID of the uploaded file (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "valid": true,
    "structure": {
      "type": "object",
      "nesting_level": 3
    }
  }
}
```

### Conversion API

Base URL: `/api/conversion`

#### POST /jobs

Create a new conversion job.

**Parameters:**
- `file_id` (form): ID of the uploaded JSON file (required)
- `sheet_name` (form): Name for the Excel worksheet (optional, default: "Sheet1")
- `array_handling` (form): How to handle arrays in JSON (optional, default: "expand", values: "expand", "join")

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "pending"
  }
}
```

#### GET /jobs/{job_id}/status

Get the status of a conversion job.

**Parameters:**
- `job_id` (path): ID of the conversion job (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "processing",
    "progress": 50
  }
}
```

#### GET /jobs/{job_id}/result

Get the result of a completed conversion job.

**Parameters:**
- `job_id` (path): ID of the conversion job (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "completed",
    "download_url": "/api/conversion/jobs/job123/download"
  }
}
```

#### GET /jobs/{job_id}/download

Download the Excel file generated by a conversion job.

**Parameters:**
- `job_id` (path): ID of the conversion job (required)

**Response:**
- Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Body: Excel file (.xlsx)

#### POST /jobs/{job_id}/cancel

Cancel a pending or in-progress conversion job.

**Parameters:**
- `job_id` (path): ID of the conversion job (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "cancelled"
  }
}
```

#### POST /validate

Validate a JSON file without performing the full conversion.

**Parameters:**
- `file_id` (form): ID of the uploaded JSON file (required)

**Response:**
```json
{
  "status": "success",
  "data": {
    "valid": true,
    "structure": {
      "type": "object",
      "nesting_level": 3
    }
  }
}
```

### Error Responses

All API endpoints follow a standard error response format:

```json
{
  "status": "error",
  "error": {
    "code": 400,
    "message": "Human-readable error message",
    "details": {}
  }
}
```

Common error codes:

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File size exceeds the maximum limit |
| 415 | Unsupported Media Type | Invalid file format |
| 500 | Internal Server Error | Server-side error during processing |

## Examples

### Core API Examples

#### Basic Conversion

```python
from json_to_excel import ConversionService

conversion_service = ConversionService()
success, summary, error = conversion_service.convert_json_to_excel('data.json', 'output.xlsx')

if success:
    print(f"Conversion completed successfully. Rows: {summary['rows']}")
else:
    print(f"Conversion failed: {error.message}")
```

#### Custom Excel Options

```python
from json_to_excel import ConversionService

conversion_service = ConversionService()

excel_options = {
    'sheet_name': 'Customer Data',
    'array_handling': 'join',
    'header_style': {'bold': True, 'bg_color': '#DDDDDD'},
    'auto_column_width': True
}

success, summary, error = conversion_service.convert_json_to_excel(
    'customers.json', 
    'customers.xlsx', 
    excel_options
)
```

#### Working with JSON Strings

```python
from json_to_excel import ConversionService

conversion_service = ConversionService()

json_string = '''
{
    "name": "John Doe",
    "email": "john@example.com",
    "orders": [
        {"id": 1, "product": "Laptop", "price": 999.99},
        {"id": 2, "product": "Mouse", "price": 24.99}
    ]
}
'''

success, summary, error = conversion_service.convert_json_string_to_excel(
    json_string, 
    'customer.xlsx'
)
```

#### Getting Excel as Bytes

```python
from json_to_excel import ConversionService

conversion_service = ConversionService()

excel_bytes, summary, error = conversion_service.convert_json_to_excel_bytes('data.json')

if excel_bytes:
    # Use the Excel bytes (e.g., send in HTTP response)
    with open('output.xlsx', 'wb') as f:
        f.write(excel_bytes)
```

### CLI Examples

#### Basic Conversion
```
python json_to_excel.py convert data.json output.xlsx
```
Convert a JSON file to Excel with default settings

#### Custom Sheet Name
```
python json_to_excel.py convert data.json output.xlsx --sheet-name="Customer Data"
```
Specify a custom name for the Excel worksheet

#### Array Handling
```
python json_to_excel.py convert data.json output.xlsx --array-handling=join
```
Join array elements with commas instead of expanding to multiple rows

#### Verbose Output
```
python json_to_excel.py convert data.json output.xlsx --verbose
```
Enable detailed output during conversion

#### Validating JSON
```
python json_to_excel.py validate data.json
```
Validate a JSON file without converting it

#### Getting JSON Information
```
python json_to_excel.py info data.json --format=json
```
Display information about a JSON file in JSON format

### Web API Examples

#### Uploading a JSON File
```
curl -X POST -F "file=@data.json" http://localhost:5000/api/uploads
```
Upload a JSON file to the server

Response:
```json
{
  "status": "success",
  "data": {
    "file_id": "abc123",
    "filename": "data.json",
    "size": 1024
  }
}
```

#### Creating a Conversion Job
```
curl -X POST -F "file_id=abc123" -F "sheet_name=Data" http://localhost:5000/api/conversion/jobs
```
Create a job to convert the uploaded JSON file

Response:
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "pending"
  }
}
```

#### Checking Job Status
```
curl http://localhost:5000/api/conversion/jobs/job123/status
```
Check the status of a conversion job

Response:
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "completed",
    "progress": 100
  }
}
```

#### Getting Job Result
```
curl http://localhost:5000/api/conversion/jobs/job123/result
```
Get the result of a completed conversion job

Response:
```json
{
  "status": "success",
  "data": {
    "job_id": "job123",
    "status": "completed",
    "download_url": "/api/conversion/jobs/job123/download"
  }
}
```

#### Downloading the Excel File
```
curl -OJ http://localhost:5000/api/conversion/jobs/job123/download
```
Download the generated Excel file