"""
Help text and messages for the JSON to Excel Conversion Tool CLI.

This module contains constants and structured text for the command-line interface,
including help information, command descriptions, option details, usage examples,
and standardized error messages.
"""

# Tool information
TOOL_NAME = "JSON to Excel Conversion Tool"
VERSION = "1.0.0"

# General help text
HELP_TEXT = {
    "description": "A utility for converting JSON data files into structured Excel spreadsheets.",
    "usage": "python json_to_excel.py <command> [options]",
    "general": "Use 'python json_to_excel.py help <command>' for more information about a specific command."
}

# Command-specific help text
COMMAND_HELP = {
    "CONVERT": {
        "description": "Convert a JSON file to Excel format",
        "usage": "python json_to_excel.py convert <input_json_file> <output_excel_file> [options]",
        "options": {
            "input_json_file": "Path to the JSON file to convert",
            "output_excel_file": "Path where the Excel file will be saved",
            "--sheet-name NAME": "Custom name for the Excel worksheet (default: 'Sheet1')",
            "--array-handling MODE": "How to handle arrays in JSON. Options: expand, join (default: expand)",
            "--chunk-size SIZE": "Process large files in chunks of SIZE rows (default: auto)",
            "--fields FIELDS": "Comma-separated list of fields to include (default: all fields)"
        }
    },
    "VALIDATE": {
        "description": "Validate a JSON file without converting it",
        "usage": "python json_to_excel.py validate <input_json_file> [options]",
        "options": {
            "input_json_file": "Path to the JSON file to validate"
        }
    },
    "INFO": {
        "description": "Display information about a JSON file's structure",
        "usage": "python json_to_excel.py info <input_json_file> [options]",
        "options": {
            "input_json_file": "Path to the JSON file to analyze",
            "--format FORMAT": "Output format. Options: text, json (default: text)"
        }
    },
    "HELP": {
        "description": "Display help information",
        "usage": "python json_to_excel.py help [command]",
        "options": {
            "command": "Name of the command to get help for"
        }
    }
}

# Options common to multiple commands
COMMON_OPTIONS = {
    "--verbose": "Enable detailed output during processing",
    "--help": "Display help information for a command"
}

# Usage examples
EXAMPLES = {
    "CONVERT": [
        "python json_to_excel.py convert data.json output.xlsx",
        "python json_to_excel.py convert data.json output.xlsx --sheet-name=CustomerData",
        "python json_to_excel.py convert data.json output.xlsx --array-handling=join --verbose",
        "python json_to_excel.py convert large_data.json output.xlsx --chunk-size=1000",
        "python json_to_excel.py convert data.json output.xlsx --fields=id,name,address.city"
    ],
    "VALIDATE": [
        "python json_to_excel.py validate data.json",
        "python json_to_excel.py validate data.json --verbose"
    ],
    "INFO": [
        "python json_to_excel.py info data.json",
        "python json_to_excel.py info data.json --format=json",
        "python json_to_excel.py info data.json --verbose"
    ],
    "HELP": [
        "python json_to_excel.py help",
        "python json_to_excel.py help convert",
        "python json_to_excel.py help validate"
    ]
}

# Error messages
ERROR_MESSAGES = {
    "file_not_found": "File not found. Please check the file path and try again.",
    "invalid_json": "Invalid JSON format. Please verify the JSON structure.",
    "permission_error": "Permission denied. Please check file permissions.",
    "excel_limit": "Data exceeds Excel limits. Consider filtering or splitting the data.",
    "memory_error": "Insufficient memory to process the file. Try using --chunk-size option.",
    "unknown_error": "An unexpected error occurred."
}