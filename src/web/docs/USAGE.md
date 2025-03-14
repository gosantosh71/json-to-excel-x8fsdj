# JSON to Excel Conversion Tool - Web Interface Usage Guide

## Introduction

The JSON to Excel Conversion Tool provides a user-friendly web interface for converting JSON data files into structured Excel spreadsheets. This web interface is designed for users who prefer a graphical interface over command-line tools and offers a simple, intuitive way to transform JSON data into Excel format without requiring technical expertise.

This document provides comprehensive guidance on using the web interface, including step-by-step instructions, configuration options, troubleshooting tips, and frequently asked questions.

## Getting Started

To use the JSON to Excel Conversion Tool web interface:

1. Open your web browser and navigate to the tool's URL
2. The home page displays an upload area for your JSON file
3. Either drag and drop your JSON file onto the upload area or click to browse and select a file
4. Once uploaded, you'll be guided through the conversion process

The web interface is designed to be intuitive and will guide you through each step of the conversion process with clear instructions and visual feedback.

## User Interface Overview

The web interface consists of several key pages that guide you through the conversion process:

### Home/Upload Page

The landing page features:
- A clear title and description of the tool
- A drag-and-drop upload area for JSON files
- A file browser button for selecting files from your device
- Information about supported file types and size limits
- Key features of the conversion tool

![JSON to Excel Tool - Upload Page](upload_page.png)

### Conversion Options Page

After uploading a file, you'll see:
- Information about your uploaded JSON file (name, size)
- Configuration options for the conversion process
- Sheet name input field (default: Sheet1)
- Array handling options (expand or join)
- Convert and Cancel buttons

![JSON to Excel Tool - Conversion Options](conversion_options.png)

### Processing Page

During conversion, this page shows:
- A progress bar indicating conversion status
- Current processing step information
- File details (name, size)
- A cancel button to abort the conversion

![JSON to Excel Tool - Processing](processing.png)

### Results/Download Page

Upon successful conversion:
- Success message with checkmark icon
- Conversion details (input file, output file, rows, columns)
- Download button for the Excel file
- Option to convert another file

![JSON to Excel Tool - Results](results.png)

### Error Page

If an error occurs:
- Clear error message with error type
- Detailed information about what went wrong
- Troubleshooting suggestions
- Option to try again

## Conversion Workflow

The conversion process follows these steps:

### Step 1: Upload JSON File

1. On the home page, drag and drop your JSON file onto the upload area or click to browse
2. The file will be uploaded and validated
3. If the file is valid JSON and within size limits, you'll proceed to the next step
4. If there are issues with the file, you'll see an error message with details

### Step 2: Configure Conversion Options

1. On the conversion options page, review your file details
2. Enter a custom name for the Excel worksheet or use the default "Sheet1"
3. Select how you want arrays to be handled:
   - Expand arrays into rows (default): Each array item becomes a separate row
   - Join arrays as text: Array items are combined into a single cell
4. Click "Start Conversion" to proceed

### Step 3: Process Conversion

1. The processing page will show conversion progress
2. A progress bar indicates the current status
3. Status messages show the current processing step
4. You can cancel the conversion at any time
5. If successful, you'll be taken to the results page
6. If an error occurs, you'll see the error page with details

### Step 4: Download Excel File

1. On the results page, review the conversion details
2. Click the "Download Excel File" button to save the file to your device
3. The Excel file will be downloaded through your browser
4. You can then click "Convert Another File" to start a new conversion

## Configuration Options

The tool provides several options to customize how your JSON data is converted to Excel:

### Sheet Name

You can specify a custom name for the Excel worksheet. By default, the sheet is named "Sheet1".

- Must be a valid Excel sheet name (up to 31 characters)
- Cannot contain these characters: : \ / ? * [ ]
- Cannot be blank

### Array Handling

JSON arrays can be handled in two different ways:

1. **Expand arrays into rows** (default): Each array item becomes a separate row in the Excel file. This is useful for arrays of objects that represent data records.

2. **Join arrays as text**: Array items are combined into a single cell with comma separation. This is useful for simple arrays of primitive values.

The best option depends on your data structure and how you plan to use the Excel file. For data analysis, expanding arrays into rows is usually more useful.

| Option | Description | Best For |
|--------|-------------|----------|
| Expand arrays into rows | Each array item becomes a separate row | Arrays of objects, data analysis |
| Join arrays as text | Array items combined into a single cell | Simple arrays of primitive values |

## Handling Different JSON Structures

The tool can handle various JSON structures, each with different conversion behaviors:

### Flat JSON

Flat JSON structures (with no nesting) are the simplest to convert. Each top-level property becomes a column in the Excel file, and the values are placed in a single row.

Example flat JSON:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30,
  "active": true
}
```

### Nested JSON

Nested JSON objects are flattened using dot notation for the column names. For example, a nested structure like `{"user": {"name": "John"}}` will become a column named "user.name" with the value "John".

Example nested JSON:

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

### JSON with Arrays

JSON arrays are handled according to your selected array handling option:

- With "Expand arrays into rows", each array item creates a new row in the Excel file
- With "Join arrays as text", array items are combined into a single cell with comma separation

Example JSON with arrays:

```json
{
  "id": 1,
  "name": "John Doe",
  "skills": ["JavaScript", "Python", "SQL"],
  "projects": [
    {"name": "Project A", "status": "Completed"},
    {"name": "Project B", "status": "In Progress"}
  ]
}
```

## Troubleshooting

If you encounter issues while using the tool, here are solutions for common problems:

### Invalid JSON Format

**Error**: "Invalid JSON format" or "JSON parsing error"

**Possible causes**:
- Syntax errors in the JSON file (missing commas, unbalanced braces, etc.)
- Incorrect encoding
- File is not actually JSON

**Solutions**:
1. Verify that your JSON file has the correct syntax
2. Use an online JSON validator to check and fix your JSON
3. Ensure the file is properly encoded (UTF-8 recommended)
4. Check that the file has a .json extension

### File Size Limitations

**Error**: "File too large" or "Maximum file size exceeded"

**Possible causes**:
- JSON file exceeds the 5MB size limit

**Solutions**:
1. Split your JSON file into smaller files
2. Remove unnecessary data or whitespace to reduce file size
3. For very large datasets, consider using the command-line version of the tool

### Conversion Processing Issues

**Error**: "Conversion timeout" or "Processing error"

**Possible causes**:
- Complex JSON structure requiring extensive processing
- Server load or connection issues
- Memory limitations

**Solutions**:
1. Try again later when server load may be lower
2. Simplify your JSON structure if possible
3. Use a smaller file
4. Check your internet connection stability

### Excel Output Problems

**Issue**: Excel output doesn't match expectations

**Possible causes**:
- Unexpected JSON structure
- Array handling option not suitable for your data
- Very deeply nested JSON creating many columns

**Solutions**:
1. Try different array handling options (expand vs. join)
2. Check if your JSON structure is very deeply nested
3. For complex JSON structures, consider restructuring your data
4. Review the Excel file carefully to understand how the conversion was performed

| Error | Possible Cause | Solution |
|-------|---------------|----------|
| Invalid JSON format | Syntax errors in JSON file | Validate JSON syntax using an online validator |
| File too large | JSON file exceeds 5MB limit | Split file or remove unnecessary data |
| Conversion timeout | Complex JSON structure or server load | Try again or use smaller file |
| Excel format issues | Unexpected data types or structure | Try different array handling options |

## FAQ

**Is my data secure when using this tool?**
Yes. Your files are processed locally on the server and are automatically deleted after processing. We do not store or access the content of your files beyond what's needed for the conversion process.

**What happens to nested JSON structures?**
Nested JSON objects are flattened using dot notation for the column names. For example, a nested structure like {"user": {"name": "John"}} will become a column named "user.name" with the value "John".

**Can I convert Excel back to JSON?**
Currently, the tool only supports one-way conversion from JSON to Excel. Bidirectional conversion may be added in future updates.

**Is there a limit to how many files I can convert?**
There is no limit to the number of files you can convert. However, each file must be processed individually and must be under the 5MB size limit.

**Is there a command-line version of this tool?**
Yes, there is a command-line version available for advanced users and for processing larger files or batch conversions. You can find more information about it in the project documentation.

**What browsers are supported?**
The web interface works with all modern browsers including Chrome, Firefox, Safari, and Edge. For the best experience, we recommend using the latest version of your preferred browser.

**Can I use this tool offline?**
The web interface requires an internet connection. For offline use, consider installing the command-line version of the tool.

**How are arrays of objects handled?**
When using the "Expand arrays into rows" option, each object in an array will create a new row in the Excel file, with columns for each property in the objects.