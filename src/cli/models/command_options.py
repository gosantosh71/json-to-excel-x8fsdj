"""
Defines the data model for command-line options in the JSON to Excel Conversion Tool.

This module provides a structured representation of user-provided command-line arguments,
supporting various commands like convert, validate, info, and help, along with their
respective options.
"""

from dataclasses import dataclass  # v: built-in
from enum import Enum  # v: built-in
from typing import Dict, Optional, List, Any, Union  # v: built-in
import os  # v: built-in

from ...backend.models.excel_options import ExcelOptions, ArrayHandlingStrategy
from ...backend.models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity


class CommandType(Enum):
    """
    An enumeration defining the supported command types in the CLI application.
    """
    CONVERT = "CONVERT"
    VALIDATE = "VALIDATE"
    INFO = "INFO"
    HELP = "HELP"


@dataclass
class CommandOptions:
    """
    A data class that represents the command-line options provided by the user,
    including the command type and all possible command-specific options.
    """
    command: CommandType
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    sheet_name: Optional[str] = None
    array_handling: Optional[str] = None
    verbose: Optional[bool] = False
    chunk_size: Optional[int] = None
    fields: Optional[str] = None
    format: Optional[str] = None
    help_command: Optional[str] = None
    error: Optional[ErrorResponse] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the CommandOptions object to a dictionary representation.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the CommandOptions object
        """
        result = {
            'command': self.command.value,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'sheet_name': self.sheet_name,
            'array_handling': self.array_handling,
            'verbose': self.verbose,
            'chunk_size': self.chunk_size,
            'fields': self.fields,
            'format': self.format,
            'help_command': self.help_command,
        }
        
        # Include error if it exists
        if self.error:
            result['error'] = self.error.to_dict()
            
        return result

    @classmethod
    def from_dict(cls, options_dict: Dict[str, Any]) -> 'CommandOptions':
        """
        Creates a CommandOptions instance from a dictionary.
        
        Args:
            options_dict: Dictionary containing command options
            
        Returns:
            CommandOptions: A new CommandOptions instance
        """
        # Extract command and convert to enum
        command_str = options_dict.get('command', 'HELP')
        try:
            command = CommandType(command_str)
        except ValueError:
            command = CommandType.HELP
        
        # Extract error if present and convert to ErrorResponse
        error_dict = options_dict.get('error')
        error = None
        if error_dict:
            error = ErrorResponse.from_dict(error_dict)
        
        # Extract other options with appropriate defaults
        return cls(
            command=command,
            input_file=options_dict.get('input_file'),
            output_file=options_dict.get('output_file'),
            sheet_name=options_dict.get('sheet_name'),
            array_handling=options_dict.get('array_handling'),
            verbose=options_dict.get('verbose', False),
            chunk_size=options_dict.get('chunk_size'),
            fields=options_dict.get('fields'),
            format=options_dict.get('format'),
            help_command=options_dict.get('help_command'),
            error=error
        )

    def get_excel_options(self) -> ExcelOptions:
        """
        Creates an ExcelOptions instance from the command options.
        
        Returns:
            ExcelOptions: An ExcelOptions instance configured based on command options
        """
        # Create dictionary of Excel-specific options
        excel_options_dict = {}
        
        # Add sheet_name if provided
        if self.sheet_name:
            excel_options_dict['sheet_name'] = self.sheet_name
        
        # Add array_handling if provided
        if self.array_handling:
            try:
                # Convert string to ArrayHandlingStrategy enum
                array_strategy = ArrayHandlingStrategy(self.array_handling.lower())
                excel_options_dict['array_handling'] = array_strategy
            except ValueError:
                # Default to EXPAND if invalid value provided
                excel_options_dict['array_handling'] = ArrayHandlingStrategy.EXPAND
        
        # Add additional options if provided
        additional_options = {}
        
        if self.chunk_size:
            additional_options['chunk_size'] = self.chunk_size
            
        if self.fields:
            additional_options['fields'] = self.fields
            
        if additional_options:
            excel_options_dict['additional_options'] = additional_options
            
        # Create and return ExcelOptions instance
        return ExcelOptions.from_dict(excel_options_dict)

    def validate(self) -> bool:
        """
        Validates the command options for correctness and consistency.
        
        Returns:
            bool: True if options are valid, False otherwise
        """
        # If error is already set, return False
        if self.error:
            return False
            
        # Validate based on command type
        if self.command == CommandType.CONVERT:
            # For CONVERT command, input_file and output_file are required
            if not self.input_file:
                self.error = ErrorResponse(
                    message="Input file is required for convert command",
                    error_code="CLI_ERROR",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
            if not self.output_file:
                self.error = ErrorResponse(
                    message="Output file is required for convert command",
                    error_code="CLI_ERROR",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
            # Check if input file exists
            if not os.path.isfile(self.input_file):
                self.error = ErrorResponse(
                    message=f"Input file '{self.input_file}' does not exist",
                    error_code="FILE_NOT_FOUND",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
        elif self.command == CommandType.VALIDATE:
            # For VALIDATE command, input_file is required
            if not self.input_file:
                self.error = ErrorResponse(
                    message="Input file is required for validate command",
                    error_code="CLI_ERROR",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
            # Check if input file exists
            if not os.path.isfile(self.input_file):
                self.error = ErrorResponse(
                    message=f"Input file '{self.input_file}' does not exist",
                    error_code="FILE_NOT_FOUND",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
        elif self.command == CommandType.INFO:
            # For INFO command, input_file is required
            if not self.input_file:
                self.error = ErrorResponse(
                    message="Input file is required for info command",
                    error_code="CLI_ERROR",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
                
            # Check if input file exists
            if not os.path.isfile(self.input_file):
                self.error = ErrorResponse(
                    message=f"Input file '{self.input_file}' does not exist",
                    error_code="FILE_NOT_FOUND",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="CLI"
                )
                return False
        
        # HELP command has no specific validation requirements
        
        return True