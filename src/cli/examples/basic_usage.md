## Basic Usage Examples

Introduction to the JSON to Excel Conversion Tool

This document provides basic usage examples for the JSON to Excel Conversion Tool command-line interface. The tool allows you to convert JSON files (both flat and nested) into Excel spreadsheets.

## Installation

Instructions on how to install the tool using pip or from source code.

## Getting Help

How to access help information

Examples of using the help command and viewing command-specific help information.

## Basic Conversion

Simple JSON to Excel conversion examples

Step-by-step examples of converting a simple JSON file to Excel format using the default settings.

## Working with Sheet Names

Customizing Excel worksheet names

Examples of specifying custom sheet names for the Excel output.

## Array Handling Options

Basic array handling strategies

Introduction to the different ways arrays can be handled during conversion (expand vs. join).

## Verbose Output

Getting detailed conversion information

How to use the --verbose flag to get more detailed information during the conversion process.

## Validating JSON Files

Checking JSON validity without conversion

Examples of using the validate command to check if a JSON file is valid without performing conversion.

## Getting JSON Information

Viewing JSON file structure information

Examples of using the info command to view details about a JSON file's structure.

## Next Steps

References to more advanced documentation

Links to advanced usage and batch processing documentation. For error handling guidance, please see the project documentation on handling errors and troubleshooting conversion issues.

## Example Commands

| Description | Command |
|---|---|
| Convert a JSON file to Excel with default settings | `python json_to_excel.py convert data.json output.xlsx` |
| Convert with a custom sheet name | `python json_to_excel.py convert data.json output.xlsx --sheet-name="Customer Data"` |
| Convert with arrays joined as text | `python json_to_excel.py convert data.json output.xlsx --array-handling=join` |
| Convert with detailed progress information | `python json_to_excel.py convert data.json output.xlsx --verbose` |
| Validate a JSON file | `python json_to_excel.py validate data.json` |
| Display information about a JSON file | `python json_to_excel.py info data.json` |
| Display general help information | `python json_to_excel.py help` |
| Display help for the convert command | `python json_to_excel.py help convert` |

## Expected Outputs

| Command | Output |
|---|---|
| `python json_to_excel.py convert data.json output.xlsx` | `[i] Successfully converted data.json to output.xlsx` |
| `python json_to_excel.py convert data.json output.xlsx --verbose` | `[i] Starting conversion process...`<br>`[i] Reading JSON file: data.json`<br>`[i] JSON file size: 1.2MB`<br>`[i] Detected nested JSON structure with 3 levels`<br>`[i] Flattening nested structures...`<br>`[i] Converting to Excel format...`<br>`[i] Writing Excel file: output.xlsx`<br>`[i] Created 1 worksheet with 150 rows and 12 columns`<br>`[i] Conversion completed successfully in 2.3 seconds` |
| `python json_to_excel.py validate data.json` | `[i] JSON file 'data.json' is valid and can be converted to Excel` |
| `python json_to_excel.py info data.json` | `[i] JSON File Information:`<br>`    File: data.json`<br>`    Size: 1.2MB`<br>`    Structure: Nested (3 levels)`<br>`    Contains arrays: Yes`<br>`    Estimated rows: 150`<br>`    Estimated columns: 12` |