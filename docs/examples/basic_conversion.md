## Basic JSON to Excel Conversion Examples

This guide provides practical examples for converting JSON files to Excel format using the JSON to Excel Conversion Tool. These examples cover the most common use cases and will help you get started quickly with the tool.

## Prerequisites

Before you begin, ensure you have installed the JSON to Excel Conversion Tool. For installation instructions, see the [Installation Guide](../installation.md).

## Converting a Simple JSON File

The most basic use case is converting a simple, flat JSON file to Excel format. A flat JSON file contains only key-value pairs without nested objects or arrays.

## Command Line Interface Examples

The following examples demonstrate how to use the command line interface to convert JSON files to Excel.

## Basic Command Syntax

The basic syntax for converting a JSON file to Excel is:

```bash
json2excel convert <input_json_file> <output_excel_file>
```

This command reads the JSON file specified by `<input_json_file>` and creates an Excel file at the location specified by `<output_excel_file>`.

## Example 1: Converting a Simple JSON File

Let's convert a simple JSON file containing customer data to Excel format.

1. Create a file named `customer.json` with the following content:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30,
  "active": true
}
```

2. Run the conversion command:

```bash
json2excel convert customer.json customer.xlsx
```

3. Open the resulting `customer.xlsx` file in Excel. You should see a spreadsheet with one row of data and columns for id, name, email, age, and active.

## Example 2: Converting a JSON File with Multiple Records

Now let's convert a JSON file containing multiple records (an array of objects).

1. Create a file named `customers.json` with the following content:

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "active": true
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "age": 25,
    "active": true
  },
  {
    "id": 3,
    "name": "Bob Johnson",
    "email": "bob.johnson@example.com",
    "age": 45,
    "active": false
  }
]
```

2. Run the conversion command:

```bash
json2excel convert customers.json customers.xlsx
```

3. Open the resulting `customers.xlsx` file in Excel. You should see a spreadsheet with three rows of data and columns for id, name, email, age, and active.

## Customizing the Output

The JSON to Excel Conversion Tool provides several options to customize the output Excel file.

## Example 3: Customizing the Sheet Name

By default, the Excel file will have a sheet named "Sheet1". You can customize this using the `--sheet-name` option:

```bash
json2excel convert customers.json customers.xlsx --sheet-name="Customer Data"
```

This will create an Excel file with a sheet named "Customer Data" instead of the default "Sheet1".

## Example 4: Formatting as an Excel Table

You can format the output as an Excel table with filtering and sorting capabilities using the `--format-as-table` option:

```bash
json2excel convert customers.json customers.xlsx --format-as-table
```

This will create an Excel file with the data formatted as a table, allowing you to easily filter and sort the data within Excel.

## Example 5: Automatically Adjusting Column Widths

To make the Excel file more readable, you can automatically adjust the column widths to fit the content using the `--auto-column-width` option:

```bash
json2excel convert customers.json customers.xlsx --auto-column-width
```

This will adjust each column's width to fit its content, making the spreadsheet easier to read.

## Example 6: Combining Multiple Options

You can combine multiple options to customize the output according to your needs:

```bash
json2excel convert customers.json customers.xlsx \
  --sheet-name="Customer Data" \
  --format-as-table \
  --auto-column-width
```

This command will create an Excel file with a sheet named "Customer Data", formatted as a table, with automatically adjusted column widths.

## Verifying Conversion Results

To get more information about the conversion process, you can use the `--verbose` option:

```bash
json2excel convert customers.json customers.xlsx --verbose
```

This will display detailed information about the conversion process, including:

```
[i] Starting conversion process...
[i] Reading JSON file: customers.json
[i] JSON file size: 0.5KB
[i] Detected JSON array with 3 items
[i] Converting to Excel format...
[i] Writing Excel file: customers.xlsx
[i] Created 1 worksheet with 3 rows and 5 columns
[i] Conversion completed successfully in 0.8 seconds
```

## Handling Errors

Here are some common errors you might encounter and how to resolve them:

1. **File not found error**:

```
[!] ERROR: Could not read JSON file 'missing.json'
[!] File not found. Please check the file path and try again.
```

Resolution: Verify that the JSON file exists at the specified path.

2. **Invalid JSON format**:

```
[!] ERROR: Invalid JSON format in 'invalid.json'
[!] JSON syntax error at line 3, column 10: Expecting property name enclosed in double quotes
[!] Please verify the JSON structure and try again.
```

Resolution: Check your JSON file for syntax errors. Common issues include missing commas, unquoted keys, or trailing commas.

## Next Steps

Now that you've learned the basics of converting JSON files to Excel, you might want to explore more advanced features:

- [Handling Nested JSON Structures](./handling_nested_json.md): Learn how to convert complex nested JSON structures with objects and arrays.
- [Batch Processing](./batch_processing.md): Learn how to convert multiple JSON files in a single operation.

For more information about all available options and features, run:

```bash
json2excel help convert
```