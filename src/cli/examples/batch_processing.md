## Batch Processing Examples

This document provides examples and guidance for batch processing multiple JSON files using the JSON to Excel Conversion Tool command-line interface. Batch processing allows you to convert multiple JSON files to Excel format efficiently, saving time and effort when working with large collections of files.

## Basic Batch Processing

Examples of using the batch command to process multiple JSON files at once, including directory-based processing and wildcard patterns.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel
```

This command converts all JSON files found in the `./data` directory and saves the corresponding Excel files to the `./excel` directory.

```
python json_to_excel.py batch --input-pattern="./data/customer_*.json" --output-dir=./excel
```

This command uses a wildcard pattern to convert only the JSON files that match the pattern `./data/customer_*.json` and saves the Excel files to the `./excel` directory.

## Output Directory Structure

Controlling how output files are organized.

The tool preserves the directory structure of the input files in the output directory. For example, if you have the following directory structure:

```
data/
├── customer_data.json
├── orders/
│   ├── order_1.json
│   └── order_2.json
└── products.json
```

And you run the following command:

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel
```

The output directory structure will be:

```
excel/
├── customer_data.xlsx
├── orders/
│   ├── order_1.xlsx
│   └── order_2.xlsx
└── products.xlsx
```

## Parallel Processing

Using parallel processing to speed up batch conversion by utilizing multiple CPU cores, including controlling the number of worker processes and managing resource usage.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --workers=4
```

This command processes the JSON files in the `./data` directory using 4 worker processes, which can significantly reduce the total processing time on multi-core systems.

## Filtering Input Files

How to use filtering options to select specific JSON files for processing based on file patterns, size, or content characteristics.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --max-size=5MB
```

This command processes only the JSON files in the `./data` directory that are smaller than 5MB.

## Handling Errors in Batch Mode

Strategies for handling errors during batch processing, including continue-on-error behavior, error logging, and generating error reports.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --continue-on-error
```

This command continues processing the remaining JSON files even if an error occurs during the conversion of one file.

## Batch Configuration Files

How to create and use batch configuration files to define complex batch processing operations with different settings for different files.

```
python json_to_excel.py batch --config=batch_config.json
```

This command uses a configuration file named `batch_config.json` to define the batch processing operation.

## Progress Reporting

Options for monitoring and reporting progress during batch processing, including progress bars, logging, and summary reports.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --summary-report=report.txt
```

This command generates a summary report after processing all files and saves it to `report.txt`.

## Performance Optimization

Tips and techniques for optimizing batch processing performance, including memory management, chunking strategies, and parallel processing configuration.

Apply the same Excel options to all files:

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --sheet-name="Data" --array-handling=join
```

## Integration with Scripts

Examples of integrating batch processing with shell scripts, Python scripts, and other automation tools for workflow integration.

Batch Configuration File:

```json
{
  "input_directory": "./data",
  "output_directory": "./excel",
  "workers": 4,
  "continue_on_error": true,
  "default_options": {
    "sheet_name": "Data",
    "array_handling": "expand",
    "auto_column_width": true
  },
  "file_specific_options": {
    "customer_*.json": {
      "sheet_name": "Customers",
      "format_as_table": true
    },
    "orders.json": {
      "sheet_name": "Orders",
      "array_handling": "join",
      "array_separator": ", "
    }
  }
}
```

Shell Script for Batch Processing:

```bash
#!/bin/bash

# Example shell script for batch processing JSON files

# Define directories
INPUT_DIR="./data"
OUTPUT_DIR="./excel"
LOG_FILE="conversion.log"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Run batch processing with 4 worker processes
python json_to_excel.py batch \
  --input-dir=$INPUT_DIR \
  --output-dir=$OUTPUT_DIR \
  --workers=4 \
  --continue-on-error \
  --verbose > $LOG_FILE 2>&1

# Check if processing was successful
if [ $? -eq 0 ]; then
  echo "Batch processing completed successfully"
else
  echo "Batch processing encountered errors. See $LOG_FILE for details"
fi
```

Python Script for Custom Batch Processing:

```python
#!/usr/bin/env python

# Example Python script for custom batch processing

import os
import subprocess
import glob
from concurrent.futures import ProcessPoolExecutor

def convert_file(input_file, output_dir):
    """Convert a single JSON file to Excel"""
    base_name = os.path.basename(input_file)
    name_without_ext = os.path.splitext(base_name)[0]
    output_file = os.path.join(output_dir, f"{name_without_ext}.xlsx")
    
    cmd = [
        "python", "json_to_excel.py", "convert",
        input_file, output_file,
        "--sheet-name", name_without_ext,
        "--auto-column-width"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "input": input_file,
        "output": output_file,
        "success": result.returncode == 0,
        "message": result.stdout if result.returncode == 0 else result.stderr
    }

def main():
    input_dir = "./data"
    output_dir = "./excel"
    max_workers = 4
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process files in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(convert_file, file, output_dir) for file in json_files]
        for future in futures:
            results.append(future.result())
    
    # Print summary
    success_count = sum(1 for r in results if r["success"])\n    print(f"Processed {len(results)} files: {success_count} succeeded, {len(results) - success_count} failed")
    
    # Print failures if any
    failures = [r for r in results if not r["success"]]
    if failures:
        print("\nFailed conversions:")
        for failure in failures:
            print(f"- {failure['input']}: {failure['message']}")

if __name__ == "__main__":
    main()