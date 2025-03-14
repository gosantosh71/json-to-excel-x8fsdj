"""
CLI response models for the JSON to Excel Conversion Tool.

This module provides a standardized structure for representing command execution results,
including success and error responses, with metadata and formatting capabilities for
consistent user feedback.
"""

from enum import Enum  # v: built-in
from dataclasses import dataclass  # v: built-in
from typing import Dict, Optional, Any, List, Union  # v: built-in
from datetime import datetime  # v: built-in

from ...backend.models.error_response import ErrorResponse


def get_iso_timestamp() -> str:
    """
    Generates an ISO 8601 formatted timestamp for the current time.
    
    Returns:
        str: The current datetime in ISO 8601 format
    """
    return datetime.now().isoformat()


class ResponseType(Enum):
    """
    An enumeration defining the types of responses that can be returned from CLI commands.
    """
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class CLIResponse:
    """
    A data class that represents the result of a CLI command execution,
    including status, message, data, and metadata.
    """
    response_type: ResponseType
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[ErrorResponse] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata with defaults if not provided."""
        if self.metadata is None:
            self.metadata = {}
        
        # Add timestamp to metadata if not present
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = get_iso_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the CLIResponse object to a dictionary representation.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the CLIResponse object
        """
        result = {
            "response_type": self.response_type.value,
            "message": self.message,
            "data": self.data,
            "metadata": self.metadata
        }
        
        if self.error:
            result["error"] = self.error.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, response_dict: Dict[str, Any]) -> 'CLIResponse':
        """
        Creates a CLIResponse instance from a dictionary.
        
        Args:
            response_dict: Dictionary containing response data
            
        Returns:
            CLIResponse: A new CLIResponse instance
        """
        # Convert response_type string to enum
        response_type = ResponseType(response_dict.get("response_type"))
        
        # Extract basic fields
        message = response_dict.get("message", "")
        data = response_dict.get("data")
        metadata = response_dict.get("metadata", {})
        
        # Convert error dict to ErrorResponse if present
        error = None
        if "error" in response_dict and response_dict["error"]:
            error = ErrorResponse.from_dict(response_dict["error"])
        
        return cls(
            response_type=response_type,
            message=message,
            data=data,
            error=error,
            metadata=metadata
        )
    
    def get_formatted_output(self, format_type: Optional[str] = None) -> str:
        """
        Generates a formatted string representation of the response for display to the user.
        
        Args:
            format_type: Optional output format type ('json' for JSON formatting)
            
        Returns:
            str: A formatted string representation of the response
        """
        import json  # Import here to avoid circular imports
        
        if format_type == 'json':
            return json.dumps(self.to_dict(), indent=2)
        
        # Format based on response type
        if self.error:
            return self.error.get_user_message()
        
        prefix = ""
        if self.response_type == ResponseType.SUCCESS:
            prefix = "[+] "
        elif self.response_type == ResponseType.ERROR:
            prefix = "[!] "
        elif self.response_type == ResponseType.WARNING:
            prefix = "[!] "
        elif self.response_type == ResponseType.INFO:
            prefix = "[i] "
        
        return f"{prefix}{self.message}"
    
    def get_exit_code(self) -> int:
        """
        Returns the appropriate exit code based on the response type.
        
        Returns:
            int: Exit code (0 for success, non-zero for errors)
        """
        if self.response_type == ResponseType.SUCCESS or self.response_type == ResponseType.INFO:
            return 0
        elif self.response_type == ResponseType.ERROR:
            return 1
        elif self.response_type == ResponseType.WARNING:
            return 2
        return 0  # Default to 0 for unhandled cases
    
    def add_metadata(self, key: str, value: Any) -> 'CLIResponse':
        """
        Adds additional metadata to the response.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            CLIResponse: Self reference for method chaining
        """
        self.metadata[key] = value
        return self