"""
Provides file sanitization and validation functionality for the web interface of the JSON to Excel Conversion Tool.
This module implements security measures to prevent common file-related vulnerabilities such as path traversal,
malicious file uploads, and Excel formula injection.
"""

import os  # v: built-in
import re  # v: built-in
import json  # v: built-in
import typing  # v: built-in
from werkzeug.utils import secure_filename  # v: 2.3.0+

from ...backend.logger import get_logger
from ...backend.utils import sanitize_file_path, is_valid_extension
from ..config.upload_config import upload_config
from ..exceptions.file_exceptions import (
    FileTypeNotAllowedException, 
    FileSizeExceededException,
    FileCorruptedException
)
from ..validators.json_validators import validate_json_structure

# Initialize logger for this module
logger = get_logger(__name__)

# Global constants from configuration
ALLOWED_EXTENSIONS = upload_config['allowed_extensions']
MAX_FILE_SIZE = upload_config['max_file_size']
MAX_FILENAME_LENGTH = upload_config['security']['max_filename_length']
DISALLOW_SPECIAL_CHARS = upload_config['security']['disallow_special_chars']
CHECK_DANGEROUS_PATTERNS = upload_config['security']['content_validation']['check_dangerous_patterns']
SANITIZE_FORMULA_TRIGGERS = upload_config['security']['content_validation']['sanitize_formula_triggers']

# Excel formula triggers that need sanitization
FORMULA_TRIGGERS = ['=', '+', '-', '@', '\t', '\r', '\n']
# Patterns that could indicate malicious content
DANGEROUS_PATTERNS = ['<script', 'javascript:', 'data:text/html', 'data:application/javascript']


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent security issues and ensure compatibility.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Use werkzeug's secure_filename to do basic sanitization
    secure_name = secure_filename(filename)
    
    # Further sanitize if configured to disallow special characters
    if DISALLOW_SPECIAL_CHARS:
        # Keep only alphanumeric characters, dots, underscores, and hyphens
        secure_name = ''.join(c for c in secure_name if c.isalnum() or c in '._-')
    
    # Truncate if filename is too long
    if MAX_FILENAME_LENGTH and len(secure_name) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(secure_name)
        # Keep the extension and truncate the name part
        secure_name = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    
    # Ensure the filename is not empty after sanitization
    if not secure_name:
        secure_name = "file"
        logger.warning(f"Filename '{filename}' was sanitized to empty string, using default name")
    
    logger.debug(f"Sanitized filename: '{filename}' -> '{secure_name}'")
    return secure_name


def sanitize_json_content(content: str) -> str:
    """
    Sanitizes JSON content to remove potentially dangerous patterns.
    
    Args:
        content: JSON content to sanitize
        
    Returns:
        Sanitized JSON content
    """
    if not CHECK_DANGEROUS_PATTERNS:
        return content
    
    sanitized_content = content
    for pattern in DANGEROUS_PATTERNS:
        # Replace dangerous patterns with safe alternatives
        sanitized_content = re.sub(
            pattern, 
            f"sanitized_{pattern.replace('<', '').replace(':', '')}", 
            sanitized_content, 
            flags=re.IGNORECASE
        )
    
    if sanitized_content != content:
        logger.warning("Potentially dangerous patterns were found and sanitized in JSON content")
    
    return sanitized_content


def sanitize_excel_cell_content(value: typing.Any) -> typing.Any:
    """
    Sanitizes cell content to prevent Excel formula injection.
    
    Args:
        value: Cell content to sanitize
        
    Returns:
        Sanitized cell content
    """
    if not SANITIZE_FORMULA_TRIGGERS:
        return value
    
    # Only sanitize string values
    if not isinstance(value, str):
        return value
    
    # Check if the value starts with a formula trigger
    if any(value.startswith(trigger) for trigger in FORMULA_TRIGGERS):
        # Prefix with a single quote to prevent formula execution
        sanitized = f"'{value}"
        logger.debug(f"Sanitized potential formula in cell: '{value}' -> '{sanitized}'")
        return sanitized
    
    return value


def sanitize_json_object(json_obj: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """
    Recursively sanitizes all string values in a JSON object to prevent Excel formula injection.
    
    Args:
        json_obj: JSON object to sanitize
        
    Returns:
        Sanitized JSON object
    """
    # Create a copy to avoid modifying the original
    sanitized = {}
    
    for key, value in json_obj.items():
        if isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_json_object(value)
        elif isinstance(value, list):
            # Sanitize items in list
            sanitized_list = []
            for item in value:
                if isinstance(item, dict):
                    sanitized_list.append(sanitize_json_object(item))
                elif isinstance(item, str):
                    sanitized_list.append(sanitize_excel_cell_content(item))
                else:
                    sanitized_list.append(item)
            sanitized[key] = sanitized_list
        elif isinstance(value, str):
            # Sanitize string values
            sanitized[key] = sanitize_excel_cell_content(value)
        else:
            # Keep non-string values as is
            sanitized[key] = value
    
    return sanitized


def validate_file_type(filename: str) -> bool:
    """
    Validates that a file has an allowed extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        True if the file type is allowed, False otherwise
    """
    return is_valid_extension(filename, ALLOWED_EXTENSIONS)


def validate_file_size(file_size: int) -> bool:
    """
    Validates that a file size does not exceed the maximum allowed size.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if the file size is within limits, False otherwise
    """
    return file_size <= MAX_FILE_SIZE


class FileSanitizer:
    """
    A class that provides file sanitization and validation functionality for the web interface.
    """
    
    def __init__(self):
        """
        Initializes a new FileSanitizer instance.
        """
        self.logger = logger
        self.logger.debug("FileSanitizer initialized")
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes a filename to prevent security issues.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            Sanitized filename
        """
        sanitized = sanitize_filename(filename)
        self.logger.debug(f"Sanitized filename: '{filename}' -> '{sanitized}'")
        return sanitized
    
    def validate_file(self, filename: str, file_size: int) -> typing.Tuple[bool, typing.Optional[str]]:
        """
        Validates a file against security constraints.
        
        Args:
            filename: Name of the file to validate
            file_size: Size of the file in bytes
            
        Returns:
            Validation result and optional error message
        """
        # Check file type
        if not validate_file_type(filename):
            allowed_extensions_str = ', '.join(ALLOWED_EXTENSIONS)
            error_msg = f"File type not allowed. Allowed extensions: {allowed_extensions_str}"
            self.logger.warning(f"File type validation failed for '{filename}'")
            return False, error_msg
        
        # Check file size
        if not validate_file_size(file_size):
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            file_size_mb = file_size / (1024 * 1024)
            error_msg = f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)"
            self.logger.warning(f"File size validation failed: {file_size} bytes exceeds {MAX_FILE_SIZE} bytes")
            return False, error_msg
        
        # All validations passed
        return True, None
    
    def validate_with_exceptions(self, filename: str, file_size: int) -> bool:
        """
        Validates a file and raises appropriate exceptions for validation failures.
        
        Args:
            filename: Name of the file to validate
            file_size: Size of the file in bytes
            
        Returns:
            True if validation passes
            
        Raises:
            FileTypeNotAllowedException: If file type is not allowed
            FileSizeExceededException: If file size exceeds the maximum allowed size
        """
        is_valid, error_msg = self.validate_file(filename, file_size)
        
        if not is_valid:
            if "File type not allowed" in error_msg:
                self.logger.error(f"File type not allowed: {filename}")
                raise FileTypeNotAllowedException(
                    filename=filename,
                    allowed_extensions=ALLOWED_EXTENSIONS
                )
            elif "File size" in error_msg and "exceeds" in error_msg:
                self.logger.error(f"File size exceeded for {filename}: {file_size} bytes")
                raise FileSizeExceededException(
                    filename=filename,
                    file_size=file_size,
                    max_size=MAX_FILE_SIZE
                )
        
        return True
    
    def sanitize_json_object(self, json_obj: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Sanitizes a JSON object to prevent Excel formula injection.
        
        Args:
            json_obj: JSON object to sanitize
            
        Returns:
            Sanitized JSON object
        """
        sanitized = sanitize_json_object(json_obj)
        self.logger.debug("Sanitized JSON object to prevent formula injection")
        return sanitized
    
    def sanitize_file_content(self, file_path: str) -> typing.Tuple[typing.Optional[typing.Dict[str, typing.Any]], typing.Optional[str]]:
        """
        Reads, validates, and sanitizes the content of a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Sanitized JSON object and optional error message
        """
        # Sanitize the file path for security
        safe_path = sanitize_file_path(file_path)
        
        # Try to read and parse the file
        try:
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Sanitize content to remove dangerous patterns
            sanitized_content = sanitize_json_content(content)
            
            # Parse JSON
            try:
                json_data = json.loads(sanitized_content)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format: {str(e)}"
                self.logger.error(f"JSON parsing error in {safe_path}: {error_msg}")
                return None, error_msg
            
            # Validate JSON structure
            is_valid, error = validate_json_structure(json_data)
            if not is_valid:
                error_msg = f"JSON structure validation failed: {str(error)}"
                self.logger.error(f"JSON structure validation failed for {safe_path}: {error_msg}")
                return None, error_msg
            
            # Sanitize JSON to prevent Excel formula injection
            sanitized_json = self.sanitize_json_object(json_data)
            
            return sanitized_json, None
            
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            self.logger.error(error_msg)
            return None, error_msg
        except PermissionError:
            error_msg = f"Permission denied: Cannot read {file_path}"
            self.logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self.logger.error(f"Unexpected error reading {file_path}: {error_msg}")
            return None, error_msg
    
    def is_safe_path(self, file_path: str, base_directory: str) -> bool:
        """
        Checks if a file path is safe and within allowed directories.
        
        Args:
            file_path: Path to check
            base_directory: Base directory that should contain the path
            
        Returns:
            True if the path is safe, False otherwise
        """
        # Sanitize the path
        safe_path = sanitize_file_path(file_path)
        
        # Convert both paths to absolute paths
        abs_file_path = os.path.abspath(safe_path)
        abs_base_dir = os.path.abspath(base_directory)
        
        # Check if the file path is within the base directory
        # by ensuring it starts with the base directory path
        is_safe = abs_file_path.startswith(abs_base_dir)
        
        if not is_safe:
            self.logger.warning(f"Security: Path traversal attempt detected for path: {file_path}")
        
        return is_safe