## Advanced Usage Examples

Introduction to advanced features of the JSON to Excel Conversion Tool

This document provides advanced usage examples for the JSON to Excel Conversion Tool command-line interface. These examples demonstrate more complex operations and configurations beyond simple file conversion. This guide assumes you are already familiar with the basic conversion commands.

Working with Complex Nested Structures

Handling deeply nested JSON objects

Examples of converting JSON files with complex nested structures, including strategies for flattening hierarchical data and preserving relationships.

Advanced Array Handling

Detailed control over array processing

Advanced techniques for handling arrays in JSON data, including different normalization strategies, custom separators for joined arrays, and handling mixed array types.

Field Selection and Filtering

Extracting specific fields from JSON

How to use the --fields option to select specific JSON fields for conversion, including support for dot notation to access nested fields.

Chunked Processing

Processing large JSON files in chunks

Techniques for handling very large JSON files by processing them in manageable chunks to avoid memory limitations.

Custom Excel Formatting

Controlling Excel output appearance

Advanced options for customizing the Excel output, including column formatting, header styles, and cell formatting based on data types.

Performance Optimization

Improving conversion speed and efficiency

Tips and techniques for optimizing the performance of the conversion process, especially for large or complex JSON files.

Integration with Other Tools

Using the tool in data pipelines

Examples of integrating the JSON to Excel Conversion Tool with other data processing tools and scripts to create automated workflows.

Batch Processing

Processing multiple files efficiently

Brief overview of batch processing capabilities with a reference to the dedicated batch processing documentation.

Troubleshooting and Debugging

Resolving common issues

Advanced troubleshooting techniques, including using verbose mode, interpreting error messages, and resolving common conversion problems.

## Example Commands

| Description | Command |
|---|---|
| Select specific fields from JSON | `python json_to_excel.py convert data.json output.xlsx --fields="id,name,address.city,address.country"` |
| Process a large file in chunks | `python json_to_excel.py convert large_data.json output.xlsx --chunk-size=1000` |
| Custom array handling with separator | `python json_to_excel.py convert data.json output.xlsx --array-handling=join --array-separator="; "` |
| Apply custom column width | `python json_to_excel.py convert data.json output.xlsx --auto-column-width` |
| Format dates in Excel | `python json_to_excel.py convert data.json output.xlsx --date-format="YYYY-MM-DD"` |
| Apply table formatting | `python json_to_excel.py convert data.json output.xlsx --format-as-table` |
| Export to multiple sheets based on a field | `python json_to_excel.py convert data.json output.xlsx --split-by="category"` |
| Advanced debugging | `python json_to_excel.py convert data.json output.xlsx --verbose --debug-level=3` |

## Expected Outputs

| Command | Output |
|---|---|
| `python json_to_excel.py convert data.json output.xlsx --fields="id,name,address.city"` | `[i] Successfully converted data.json to output.xlsx`\
`[i] Selected fields: id, name, address.city`\
`[i] Excluded 8 fields from the original JSON` |
| `python json_to_excel.py convert large_data.json output.xlsx --chunk-size=1000 --verbose` | `[i] Starting conversion process...`\
`[i] Reading JSON file: large_data.json`\
`[i] JSON file size: 25.7MB`\
`[i] Processing in chunks of 1000 records`\
`[i] Processing chunk 1/26...`\
`[i] Processing chunk 2/26...`\
`...`\
`[i] Processing chunk 26/26...`\
`[i] Writing Excel file: output.xlsx`\
`[i] Created 1 worksheet with 25,782 rows and 15 columns`\
`[i] Conversion completed successfully in 12.8 seconds` |
| `python json_to_excel.py convert data.json output.xlsx --format-as-table --verbose` | `[i] Starting conversion process...`\
`[i] Reading JSON file: data.json`\
`[i] JSON file size: 1.2MB`\
`[i] Detected nested JSON structure with 3 levels`\
`[i] Flattening nested structures...`\
`[i] Converting to Excel format...`\
`[i] Applying table formatting to worksheet`\
`[i] Writing Excel file: output.xlsx`\
`[i] Created 1 worksheet with 150 rows and 12 columns`\
`[i] Conversion completed successfully in 2.5 seconds` |

## Code Examples

### Custom Field Selection

```bash
# Select only specific fields from a nested JSON structure
python json_to_excel.py convert customer_data.json customers.xlsx --fields="id,name,email,address.street,address.city,address.country"

# This will create an Excel file with only the specified fields, even from nested objects
```

### Processing Large Files

```bash
# Process a large JSON file (>10MB) in chunks to manage memory usage
python json_to_excel.py convert large_dataset.json output.xlsx --chunk-size=1000 --verbose

# The --chunk-size parameter controls how many records are processed at once
# The --verbose flag shows progress information during processing
```

### Advanced Array Handling

```bash
# Control how arrays are handled in the conversion process

# Expand arrays into multiple rows (default behavior)
python json_to_excel.py convert orders.json orders.xlsx --array-handling=expand

# Join array values into a single cell with custom separator
python json_to_excel.py convert tags.json tags.xlsx --array-handling=join --array-separator="; "

# Handle nested arrays with custom depth control
python json_to_excel.py convert complex.json complex.xlsx --array-handling=expand --max-array-depth=2
```

### Excel Formatting Options

```bash
# Apply advanced Excel formatting options

# Format the output as an Excel table with filtering and sorting
python json_to_excel.py convert data.json formatted.xlsx --format-as-table

# Automatically adjust column widths based on content
python json_to_excel.py convert data.json formatted.xlsx --auto-column-width

# Apply custom formatting to specific data types
python json_to_excel.py convert data.json formatted.xlsx --date-format="YYYY-MM-DD" --number-format="#,##0.00"

# Freeze the header row for easier navigation
python json_to_excel.py convert data.json formatted.xlsx --freeze-header
```

## Fundamental Concepts

### Nested JSON Structure Handling

JSON data often contains nested objects, represented as objects within objects. The tool flattens these structures using dot notation for field names. For example, an address field with city and country would be represented as 'address.city' and 'address.country' in the Excel output.

### Array Handling Strategies

There are two main strategies for handling arrays in JSON: 'expand' (default) creates multiple rows, one for each array element; 'join' combines array elements into a single cell with a separator. The appropriate strategy depends on your data structure and analysis needs.

### Memory Optimization

Large JSON files can consume significant memory during processing. Using chunked processing (--chunk-size option) allows the tool to process portions of the data sequentially, reducing peak memory usage at the cost of slightly longer processing time.

### Excel Limitations

Excel has inherent limitations, including a maximum of 1,048,576 rows and 16,384 columns. When working with large datasets, be aware of these limitations and consider using the splitting options or processing the data in batches.