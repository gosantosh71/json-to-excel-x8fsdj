## Batch Processing with JSON to Excel Conversion Tool

This document provides examples and guidance for batch processing multiple JSON files using the JSON to Excel Conversion Tool. Batch processing allows you to convert multiple JSON files to Excel format efficiently, saving time and effort when working with large collections of files.

## Basic Batch Processing

The tool supports processing multiple JSON files in a single operation through directory-based processing and wildcard patterns.

## Directory-Based Processing

You can process all JSON files in a directory by specifying the input and output directories.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel
```

This command converts all JSON files found in the `./data` directory and saves the corresponding Excel files to the `./excel` directory.

## Pattern-Based Processing

You can use wildcard patterns to select specific JSON files for processing based on naming patterns.

```
python json_to_excel.py batch --input-pattern="./data/customer_*.json" --output-dir=./excel
```

This command uses a wildcard pattern to convert only the JSON files that match the pattern `./data/customer_*.json` and saves the Excel files to the `./excel` directory.

## Parallel Processing

To improve performance, the tool supports parallel processing of multiple files using worker processes.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --workers=4
```

This command processes the JSON files in the `./data` directory using 4 worker processes, which can significantly reduce the total processing time on multi-core systems.

## Error Handling in Batch Mode

When processing multiple files, you can control how errors are handled with the `--continue-on-error` flag.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --continue-on-error
```

This command continues processing the remaining JSON files even if an error occurs during the conversion of one file.

## Batch Configuration Files

For complex batch processing scenarios, you can use a JSON configuration file to define processing options.

```
python json_to_excel.py batch --config=batch_config.json
```

This command uses a configuration file named `batch_config.json` to define the batch processing operation.

## Progress Reporting

The tool provides progress reporting during batch processing, showing completion status and statistics.

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --summary-report=report.txt
```

This command generates a summary report after processing all files and saves it to `report.txt`.

## Performance Optimization

Several options are available to optimize performance during batch processing, including parallel workers and memory management.

Apply the same Excel options to all files:

```
python json_to_excel.py batch --input-dir=./data --output-dir=./excel --sheet-name="Data" --array-handling=join
```

## Integration with Scripts

Batch processing can be integrated with shell scripts, Python scripts, and other automation tools.

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
    success_count = sum(1 for r in results if r["success"])
    print(f"Processed {len(results)} files: {success_count} succeeded, {len(results) - success_count} failed")
    
    # Print failures if any
    failures = [r for r in results if not r["success"]]
    if failures:
        print("\nFailed conversions:")
        for failure in failures:
            print(f"- {failure['input']}: {failure['message']}")

if __name__ == "__main__":
    main()