"""
Constants for the JSON to Excel Conversion Tool.

This module defines all constant values used throughout the application,
ensuring consistency across different components. It includes file size limits,
allowed extensions, Excel constraints, error codes, and default configuration values.
"""

import os  # v: built-in

# Application metadata
VERSION = "1.0.0"
APP_NAME = "JSON to Excel Conversion Tool"
CONFIG_ENV_PREFIX = "JSON2EXCEL_"
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'default_config.json')
LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'logging_config.json')

# File handling constants
FILE_CONSTANTS = {
    "MAX_FILE_SIZE_BYTES": 5242880,  # 5MB
    "ALLOWED_EXTENSIONS": ["json"],
    "DEFAULT_ENCODING": "utf-8",
    "TEMP_DIRECTORY": os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'temp'),
}

# Excel-related constants
EXCEL_CONSTANTS = {
    "MAX_ROWS": 1048576,  # Excel's maximum row limit
    "MAX_COLUMNS": 16384,  # Excel's maximum column limit
    "DEFAULT_SHEET_NAME": "Sheet1",
    "EXCEL_EXTENSION": ".xlsx",
    "FORMULA_PREFIX_CHARS": ["=", "+", "-", "@"],  # Characters that could start a formula
}

# JSON processing constants
JSON_CONSTANTS = {
    "MAX_NESTING_LEVEL": 10,
    "ARRAY_HANDLING_OPTIONS": ["expand", "join"],
    "DEFAULT_ARRAY_HANDLING": "expand",
    "PATH_SEPARATOR": ".",  # Used for flattened JSON keys
    "ARRAY_JOIN_DELIMITER": ", ",  # Used when joining array values
}

# Error codes and messages
ERROR_CODES = {
    "FILE_NOT_FOUND": "E001",
    "INVALID_FILE_TYPE": "E002",
    "FILE_TOO_LARGE": "E003",
    "PERMISSION_ERROR": "E004",
    "JSON_PARSE_ERROR": "E005",
    "JSON_STRUCTURE_ERROR": "E006",
    "EXCEL_ROW_LIMIT": "E007",
    "EXCEL_COLUMN_LIMIT": "E008",
    "EXCEL_GENERATION_ERROR": "E009",
    "MEMORY_ERROR": "E010",
    "CONFIG_ERROR": "E011",
    "UNKNOWN_ERROR": "E999",
}

# Error messages that correspond to error codes
ERROR_MESSAGES = {
    ERROR_CODES["FILE_NOT_FOUND"]: "File not found. Please check the file path and try again.",
    ERROR_CODES["INVALID_FILE_TYPE"]: "Invalid file type. Only JSON files are supported.",
    ERROR_CODES["FILE_TOO_LARGE"]: "File too large. Maximum file size is {max_size} MB.",
    ERROR_CODES["PERMISSION_ERROR"]: "Permission denied. Cannot access the file.",
    ERROR_CODES["JSON_PARSE_ERROR"]: "Invalid JSON format. {detail}",
    ERROR_CODES["JSON_STRUCTURE_ERROR"]: "Unsupported JSON structure. {detail}",
    ERROR_CODES["EXCEL_ROW_LIMIT"]: "Data exceeds Excel's row limit of {max_rows}.",
    ERROR_CODES["EXCEL_COLUMN_LIMIT"]: "Data exceeds Excel's column limit of {max_columns}.",
    ERROR_CODES["EXCEL_GENERATION_ERROR"]: "Error generating Excel file: {detail}",
    ERROR_CODES["MEMORY_ERROR"]: "Not enough memory to process this file. Try a smaller file.",
    ERROR_CODES["CONFIG_ERROR"]: "Configuration error: {detail}",
    ERROR_CODES["UNKNOWN_ERROR"]: "An unexpected error occurred: {detail}",
}

# Performance thresholds and related constants
PERFORMANCE_CONSTANTS = {
    "SMALL_FILE_THRESHOLD_BYTES": 102400,  # 100KB
    "MEDIUM_FILE_THRESHOLD_BYTES": 1048576,  # 1MB
    "LARGE_FILE_THRESHOLD_BYTES": 5242880,  # 5MB
    "MAX_PROCESSING_TIME_SECONDS": {
        "small": {
            "parsing": 0.5,
            "transformation": 1.0,
            "excel_generation": 1.0,
            "total": 3.0
        },
        "medium": {
            "parsing": 2.0,
            "transformation": 3.0,
            "excel_generation": 3.0,
            "total": 10.0
        },
        "large": {
            "parsing": 5.0,
            "transformation": 10.0,
            "excel_generation": 10.0,
            "total": 30.0
        }
    },
    "RETRY_ATTEMPTS": {
        "small": 1,
        "medium": 2,
        "large": 3
    },
    "TIMEOUT_SECONDS": {
        "small": 10,
        "medium": 30,
        "large": 90
    }
}

# Default configuration values
DEFAULT_CONFIG = {
    "system": {
        "max_file_size": FILE_CONSTANTS["MAX_FILE_SIZE_BYTES"],
        "max_nesting_level": JSON_CONSTANTS["MAX_NESTING_LEVEL"],
        "temp_directory": FILE_CONSTANTS["TEMP_DIRECTORY"],
        "log_level": "INFO",
        "log_file": "json_to_excel.log"
    },
    "conversion": {
        "array_handling": JSON_CONSTANTS["DEFAULT_ARRAY_HANDLING"],
        "default_sheet_name": EXCEL_CONSTANTS["DEFAULT_SHEET_NAME"],
        "excel_format": EXCEL_CONSTANTS["EXCEL_EXTENSION"].lstrip('.')
    },
    "web_interface": {
        "enabled": False,
        "port": 5000,
        "host": "127.0.0.1",
        "upload_folder": os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads'),
        "max_upload_size": FILE_CONSTANTS["MAX_FILE_SIZE_BYTES"]
    }
}