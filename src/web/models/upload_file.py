"""
Defines the data model for uploaded files in the web interface of the JSON to Excel Conversion Tool.
This model encapsulates file metadata, validation status, and operations for handling uploaded JSON files securely.
"""

import os  # v: built-in
import uuid  # v: built-in
import datetime  # v: built-in
import enum  # v: built-in
from dataclasses import dataclass  # v: built-in
from typing import Dict, Optional, Tuple, Any  # v: built-in
from werkzeug.datastructures import FileStorage  # v: 2.3.0+

from ..utils.file_utils import generate_unique_filename, is_allowed_file, sanitize_filename
from ...backend.models.error_response import ErrorResponse, ErrorCategory
from ...backend.adapters.file_system_adapter import FileSystemAdapter

# Import configuration settings for file uploads
from ..config.upload_config import upload_config

# Global constants from configuration
UPLOAD_FOLDER = upload_config['upload_folder']
ALLOWED_EXTENSIONS = upload_config['allowed_extensions']
MAX_FILE_SIZE = upload_config['max_file_size']


class UploadStatus(enum.Enum):
    """Enumeration of possible upload status values for tracking the state of uploaded files."""
    PENDING = "pending"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


@dataclass
class UploadFile:
    """A data class that represents an uploaded file in the web interface with metadata and validation status."""
    file_id: str
    original_filename: str
    secure_filename: str
    file_path: str
    file_size: int
    content_type: str
    status: UploadStatus
    upload_timestamp: datetime.datetime
    validation_result: Dict
    _file_system_adapter: FileSystemAdapter

    def __init__(self, file_id: str, original_filename: str, secure_filename: str, 
                 file_path: str, file_size: int, content_type: str = "application/json", 
                 status: UploadStatus = UploadStatus.PENDING):
        """
        Initializes a new UploadFile instance with the provided file information.
        
        Args:
            file_id: Unique identifier for the file
            original_filename: Original name of the uploaded file
            secure_filename: Sanitized and unique filename for security
            file_path: Full path to the file on the server
            file_size: Size of the file in bytes
            content_type: MIME type of the file (default: application/json)
            status: Current status of the file (default: PENDING)
        """
        self.file_id = file_id if file_id else str(uuid.uuid4())
        self.original_filename = original_filename
        self.secure_filename = secure_filename or sanitize_filename(original_filename)
        self.file_path = file_path
        self.file_size = file_size
        self.content_type = content_type
        self.status = status
        self.upload_timestamp = datetime.datetime.now()
        self.validation_result = {}
        self._file_system_adapter = FileSystemAdapter()

    @classmethod
    def from_werkzeug_file(cls, file: FileStorage) -> 'UploadFile':
        """
        Creates an UploadFile instance from a Werkzeug FileStorage object (Flask file upload).
        
        Args:
            file: The uploaded file from a Flask request
            
        Returns:
            A new UploadFile instance
        """
        if not file or not file.filename:
            raise ValueError("No file provided or filename is empty")

        # Get the original filename
        original_filename = file.filename
        
        # Create a secure filename
        secure_name = sanitize_filename(original_filename)
        
        # Generate a unique filename to prevent overwriting
        unique_filename = generate_unique_filename(secure_name)
        
        # Create the full file path
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create and return the UploadFile instance
        return cls(
            file_id=str(uuid.uuid4()),
            original_filename=original_filename,
            secure_filename=unique_filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type or "application/json",
            status=UploadStatus.PENDING
        )

    def validate(self) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates the uploaded file for proper JSON format and structure.
        
        Returns:
            Tuple containing (success, error_response)
        """
        # Check if file exists
        if not os.path.exists(self.file_path):
            error = ErrorResponse(
                message=f"File not found at {self.file_path}",
                error_code="FILE_NOT_FOUND",
                category=ErrorCategory.INPUT_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="UploadFile",
                context={"file_path": self.file_path},
                resolution_steps=["Check if the file was properly uploaded", 
                                 "Try uploading the file again"]
            )
            self.status = UploadStatus.ERROR
            self.validation_result = {"success": False, "error": "File not found"}
            return False, error
            
        # Check if file has allowed extension
        if not is_allowed_file(self.original_filename):
            error = ErrorResponse(
                message=f"File extension not allowed for {self.original_filename}",
                error_code="INVALID_FILE_TYPE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="UploadFile",
                context={"filename": self.original_filename, "allowed_extensions": ALLOWED_EXTENSIONS},
                resolution_steps=["Upload a file with a supported extension (.json)"]
            )
            self.status = UploadStatus.INVALID
            self.validation_result = {"success": False, "error": "Invalid file type"}
            return False, error
            
        # Check file size
        if self.file_size > MAX_FILE_SIZE:
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            file_size_mb = self.file_size / (1024 * 1024)
            error = ErrorResponse(
                message=f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)",
                error_code="FILE_TOO_LARGE",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="UploadFile",
                context={"file_size": self.file_size, "max_size": MAX_FILE_SIZE},
                resolution_steps=["Upload a smaller file", 
                                 "Split your data into multiple files"]
            )
            self.status = UploadStatus.INVALID
            self.validation_result = {"success": False, "error": "File too large"}
            return False, error
            
        # Try to parse JSON
        try:
            self.status = UploadStatus.VALIDATING
            json_data = self._file_system_adapter.read_json_file(self.file_path)
            
            # JSON is valid
            self.status = UploadStatus.VALID
            self.validation_result = {
                "success": True,
                "is_array": isinstance(json_data, list),
                "is_nested": any(isinstance(v, dict) or isinstance(v, list) 
                                for v in json_data.values()) if isinstance(json_data, dict) else True
            }
            return True, None
            
        except Exception as e:
            # JSON parsing failed
            error_message = str(e)
            error = ErrorResponse(
                message=f"Invalid JSON format: {error_message}",
                error_code="JSON_PARSE_ERROR",
                category=ErrorCategory.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                source_component="UploadFile",
                context={"filename": self.original_filename, "error": error_message},
                resolution_steps=["Check that your JSON file has valid syntax",
                                 "Validate your JSON using an online JSON validator"]
            )
            self.status = UploadStatus.INVALID
            self.validation_result = {"success": False, "error": error_message}
            return False, error

    def get_file_details(self) -> dict:
        """
        Gets detailed information about the uploaded file.
        
        Returns:
            Dictionary with file details
        """
        file_info = {
            "id": self.file_id,
            "original_filename": self.original_filename,
            "secure_filename": self.secure_filename,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "status": self.status.value,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "file_path": self.file_path
        }
        
        # Add validation results if available
        if self.validation_result:
            file_info["validation"] = self.validation_result
            
        return file_info

    def delete_file(self) -> bool:
        """
        Deletes the physical file from the filesystem.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        if not os.path.exists(self.file_path):
            return False
            
        try:
            os.remove(self.file_path)
            return True
        except Exception:
            return False

    def to_dict(self) -> dict:
        """
        Converts the UploadFile instance to a dictionary representation.
        
        Returns:
            Dictionary representation of the upload file
        """
        return {
            "file_id": self.file_id,
            "original_filename": self.original_filename,
            "secure_filename": self.secure_filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "status": self.status.value,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "validation_result": self.validation_result
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UploadFile':
        """
        Creates an UploadFile instance from a dictionary representation.
        
        Args:
            data: Dictionary containing UploadFile data
            
        Returns:
            A new UploadFile instance
        """
        # Convert status string back to enum
        status = UploadStatus(data.get('status', UploadStatus.PENDING.value))
        
        # Convert timestamp string back to datetime
        timestamp_str = data.get('upload_timestamp')
        timestamp = datetime.datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.datetime.now()
        
        # Create instance
        instance = cls(
            file_id=data.get('file_id', str(uuid.uuid4())),
            original_filename=data.get('original_filename', ''),
            secure_filename=data.get('secure_filename', ''),
            file_path=data.get('file_path', ''),
            file_size=data.get('file_size', 0),
            content_type=data.get('content_type', 'application/json'),
            status=status
        )
        
        # Set properties that are set after initialization
        instance.upload_timestamp = timestamp
        instance.validation_result = data.get('validation_result', {})
        
        return instance

    def exists(self) -> bool:
        """
        Checks if the physical file exists on the filesystem.
        
        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(self.file_path)


# Utility function wrappers for maintaining a clean interface
def generate_unique_filename(original_filename: str) -> str:
    """
    Wrapper around the utility function to generate a unique filename for an uploaded file.
    
    Args:
        original_filename: Original filename
        
    Returns:
        A unique filename with the original extension
    """
    return generate_unique_filename(original_filename)


def is_allowed_file(filename: str) -> bool:
    """
    Wrapper around the utility function to check if a file has an allowed extension.
    
    Args:
        filename: Filename to check
        
    Returns:
        True if the file extension is allowed, False otherwise
    """
    return is_allowed_file(filename)


def sanitize_filename(filename: str) -> str:
    """
    Wrapper around the utility function to sanitize a filename for security.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        A sanitized version of the filename
    """
    return sanitize_filename(filename)