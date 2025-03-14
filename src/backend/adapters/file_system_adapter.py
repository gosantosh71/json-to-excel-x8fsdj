"""
Provides an abstraction layer for file system operations in the JSON to Excel Conversion Tool.

This adapter encapsulates all file I/O operations, path handling, and file validation,
ensuring consistent error handling and security practices across the application.
It serves as a boundary between the application's core logic and the underlying file system.
"""

import os  # v: built-in
import os.path  # v: built-in
import shutil  # v: built-in
import tempfile  # v: built-in
import typing  # v: built-in
import json  # v: built-in
import contextlib  # v: built-in

from ..logger import get_logger
from ..exceptions import (
    FileSystemException,
    FileNotFoundError,
    PermissionError as FilePermissionError,
    FileSizeError,
    InvalidFileTypeError
)
from ..constants import FILE_CONSTANTS
from ..config import get_config_value
from ..utils import (
    validate_file_path,
    validate_file_extension,
    get_file_size,
    sanitize_file_path,
    create_directory_if_not_exists,
    PathUtils,
    Timer,
    format_file_size
)

# Initialize logger for this module
logger = get_logger(__name__)

# Get configuration values
MAX_FILE_SIZE = get_config_value('system.max_file_size', FILE_CONSTANTS['MAX_FILE_SIZE_BYTES'])
TEMP_DIR = get_config_value('system.temp_directory', FILE_CONSTANTS['TEMP_DIRECTORY'])


class FileSystemAdapter:
    """
    Adapter class that provides an interface for file system operations with proper
    error handling and security measures.
    """

    def __init__(self, base_directory: str = None, temp_directory: str = None):
        """
        Initializes the FileSystemAdapter with base and temporary directories.

        Args:
            base_directory: Base directory for relative file paths
            temp_directory: Directory for temporary files
        """
        self.base_directory = base_directory or os.getcwd()
        self.temp_directory = temp_directory or TEMP_DIR

        # Ensure the base directory exists and is accessible
        if not os.path.exists(self.base_directory):
            try:
                os.makedirs(self.base_directory, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create base directory: {e}")
                raise FileSystemException(
                    message=f"Failed to create base directory: {self.base_directory}",
                    error_code="E004",
                    file_path=self.base_directory
                )

        # Create the temporary directory if it doesn't exist
        if not os.path.exists(self.temp_directory):
            try:
                create_directory_if_not_exists(self.temp_directory)
            except Exception as e:
                logger.error(f"Failed to create temporary directory: {e}")
                raise FileSystemException(
                    message=f"Failed to create temporary directory: {self.temp_directory}",
                    error_code="E004",
                    file_path=self.temp_directory
                )

        logger.info(f"FileSystemAdapter initialized with base_directory={self.base_directory}, temp_directory={self.temp_directory}")

    def read_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Reads the content of a file with proper error handling.

        Args:
            file_path: Path to the file to read
            encoding: File encoding to use

        Returns:
            The content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            FilePermissionError: If the file can't be accessed
            FileSizeError: If the file is too large
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate the file path
        file_path = sanitize_file_path(file_path)
        if not validate_file_path(file_path):
            raise FileSystemException(
                message=f"Invalid file path: {file_path}",
                error_code="E001",
                file_path=file_path
            )

        # Check if the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path=file_path)

        # Check if the file is accessible
        if not os.access(file_path, os.R_OK):
            raise FilePermissionError(
                file_path=file_path,
                operation="read"
            )

        # Check the file size
        try:
            file_size = get_file_size(file_path)
            if file_size > MAX_FILE_SIZE:
                raise FileSizeError(
                    file_path=file_path,
                    file_size=file_size,
                    max_size=MAX_FILE_SIZE
                )
        except Exception as e:
            if isinstance(e, FileSizeError):
                raise
            logger.error(f"Error checking file size: {e}")
            raise FileSystemException(
                message=f"Failed to check file size: {str(e)}",
                error_code="E001",
                file_path=file_path
            )

        # Read the file content
        try:
            with Timer("File read operation"):
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            logger.debug(f"Read {len(content)} characters from {file_path}")
            return content
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading file {file_path}: {e}")
            raise FileSystemException(
                message=f"File encoding error: {str(e)}",
                error_code="E001",
                file_path=file_path
            )
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise FileSystemException(
                message=f"Failed to read file: {str(e)}",
                error_code="E001",
                file_path=file_path
            )

    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Writes content to a file with proper error handling.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            encoding: File encoding to use

        Returns:
            True if the write operation was successful

        Raises:
            FilePermissionError: If the file can't be written
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate the file path
        file_path = sanitize_file_path(file_path)
        if not validate_file_path(file_path):
            raise FileSystemException(
                message=f"Invalid file path: {file_path}",
                error_code="E001",
                file_path=file_path
            )

        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                create_directory_if_not_exists(directory)
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise FileSystemException(
                    message=f"Failed to create directory: {directory}",
                    error_code="E004",
                    file_path=directory
                )

        # Write the file content
        try:
            with Timer("File write operation"):
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
            logger.debug(f"Wrote {len(content)} characters to {file_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error writing file {file_path}: {e}")
            raise FilePermissionError(
                file_path=file_path,
                operation="write"
            )
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise FileSystemException(
                message=f"Failed to write file: {str(e)}",
                error_code="E001",
                file_path=file_path
            )

    def read_json_file(self, file_path: str, encoding: str = 'utf-8') -> dict:
        """
        Reads and parses a JSON file with proper error handling.

        Args:
            file_path: Path to the JSON file to read
            encoding: File encoding to use

        Returns:
            The parsed JSON content as a dictionary

        Raises:
            InvalidFileTypeError: If the file is not a JSON file
            FileNotFoundError: If the file doesn't exist
            FilePermissionError: If the file can't be accessed
            FileSizeError: If the file is too large
            FileSystemException: For other file-related errors
        """
        # Validate that the file has a .json extension
        if not validate_file_extension(file_path, ["json"]):
            extension = os.path.splitext(file_path)[1].lstrip(".") or "unknown"
            raise InvalidFileTypeError(
                file_path=file_path,
                expected_type="json",
                actual_type=extension
            )

        # Read the file content
        content = self.read_file(file_path, encoding)

        # Parse the JSON content
        try:
            with Timer("JSON parse operation"):
                json_data = json.loads(content)
            logger.debug(f"Successfully parsed JSON from {file_path}")
            return json_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {file_path}: {e}")
            from ..exceptions import JSONParseError
            raise JSONParseError(
                message=f"JSON parsing error: {str(e)}",
                line_number=e.lineno,
                column=e.colno,
                error_details=e.msg
            )
        except Exception as e:
            logger.error(f"Error parsing JSON from {file_path}: {e}")
            raise FileSystemException(
                message=f"Failed to parse JSON: {str(e)}",
                error_code="E005",
                file_path=file_path
            )

    def write_json_file(self, file_path: str, data: dict, encoding: str = 'utf-8', pretty_print: bool = True) -> bool:
        """
        Writes JSON data to a file with proper error handling.

        Args:
            file_path: Path to the JSON file to write
            data: Data to write to the file
            encoding: File encoding to use
            pretty_print: Whether to format the JSON with indentation

        Returns:
            True if the write operation was successful

        Raises:
            InvalidFileTypeError: If the file is not a JSON file
            FilePermissionError: If the file can't be written
            FileSystemException: For other file-related errors
        """
        # Validate that the file has a .json extension
        if not validate_file_extension(file_path, ["json"]):
            extension = os.path.splitext(file_path)[1].lstrip(".") or "unknown"
            raise InvalidFileTypeError(
                file_path=file_path,
                expected_type="json",
                actual_type=extension
            )

        # Convert the data to JSON string
        try:
            indent = 4 if pretty_print else None
            json_string = json.dumps(data, indent=indent)
        except Exception as e:
            logger.error(f"Error converting data to JSON: {e}")
            raise FileSystemException(
                message=f"Failed to convert data to JSON: {str(e)}",
                error_code="E005",
                file_path=file_path
            )

        # Write the JSON string to the file
        result = self.write_file(file_path, json_string, encoding)
        logger.debug(f"Successfully wrote JSON to {file_path}")
        return result

    def file_exists(self, file_path: str) -> bool:
        """
        Checks if a file exists.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file exists, False otherwise
        """
        # Sanitize and validate the file path
        file_path = sanitize_file_path(file_path)
        if not validate_file_path(file_path):
            logger.warning(f"Invalid file path: {file_path}")
            return False

        return os.path.isfile(file_path)

    def create_temp_file(self, prefix: str = "", suffix: str = "") -> str:
        """
        Creates a temporary file and returns its path.

        Args:
            prefix: Prefix for the temporary file name
            suffix: Suffix for the temporary file name

        Returns:
            Path to the created temporary file

        Raises:
            FileSystemException: If the temporary file can't be created
        """
        # Ensure the temporary directory exists
        if not os.path.exists(self.temp_directory):
            try:
                create_directory_if_not_exists(self.temp_directory)
            except Exception as e:
                logger.error(f"Failed to create temporary directory: {e}")
                raise FileSystemException(
                    message=f"Failed to create temporary directory: {self.temp_directory}",
                    error_code="E004",
                    file_path=self.temp_directory
                )

        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_directory)
            os.close(fd)  # Close the file descriptor
            logger.debug(f"Created temporary file: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Failed to create temporary file: {e}")
            raise FileSystemException(
                message=f"Failed to create temporary file: {str(e)}",
                error_code="E004",
                file_path=self.temp_directory
            )

    def create_temp_directory(self, prefix: str = "") -> str:
        """
        Creates a temporary directory and returns its path.

        Args:
            prefix: Prefix for the temporary directory name

        Returns:
            Path to the created temporary directory

        Raises:
            FileSystemException: If the temporary directory can't be created
        """
        # Ensure the temporary directory exists
        if not os.path.exists(self.temp_directory):
            try:
                create_directory_if_not_exists(self.temp_directory)
            except Exception as e:
                logger.error(f"Failed to create temporary directory: {e}")
                raise FileSystemException(
                    message=f"Failed to create temporary directory: {self.temp_directory}",
                    error_code="E004",
                    file_path=self.temp_directory
                )

        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.temp_directory)
            logger.debug(f"Created temporary directory: {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"Failed to create temporary directory: {e}")
            raise FileSystemException(
                message=f"Failed to create temporary directory: {str(e)}",
                error_code="E004",
                file_path=self.temp_directory
            )

    def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file with proper error handling.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if the file was deleted successfully, False if the file doesn't exist

        Raises:
            FilePermissionError: If the file can't be deleted
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate the file path
        file_path = sanitize_file_path(file_path)
        if not validate_file_path(file_path):
            logger.warning(f"Invalid file path: {file_path}")
            return False

        # Check if the file exists
        if not os.path.isfile(file_path):
            logger.warning(f"File not found for deletion: {file_path}")
            return False

        try:
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error deleting file {file_path}: {e}")
            raise FilePermissionError(
                file_path=file_path,
                operation="delete"
            )
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise FileSystemException(
                message=f"Failed to delete file: {str(e)}",
                error_code="E004",
                file_path=file_path
            )

    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copies a file from source to destination with proper error handling.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Returns:
            True if the file was copied successfully

        Raises:
            FileNotFoundError: If the source file doesn't exist
            FilePermissionError: If the file can't be copied
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate both source and destination paths
        source_path = sanitize_file_path(source_path)
        destination_path = sanitize_file_path(destination_path)
        
        if not validate_file_path(source_path):
            raise FileSystemException(
                message=f"Invalid source file path: {source_path}",
                error_code="E001",
                file_path=source_path
            )
            
        if not validate_file_path(destination_path):
            raise FileSystemException(
                message=f"Invalid destination file path: {destination_path}",
                error_code="E001",
                file_path=destination_path
            )

        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(file_path=source_path)

        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination_path)
        if destination_dir and not os.path.exists(destination_dir):
            try:
                create_directory_if_not_exists(destination_dir)
            except Exception as e:
                logger.error(f"Failed to create destination directory {destination_dir}: {e}")
                raise FileSystemException(
                    message=f"Failed to create destination directory: {destination_dir}",
                    error_code="E004",
                    file_path=destination_dir
                )

        try:
            with Timer("File copy operation"):
                shutil.copy2(source_path, destination_path)
            logger.debug(f"Copied file from {source_path} to {destination_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error copying file from {source_path} to {destination_path}: {e}")
            raise FilePermissionError(
                file_path=destination_path,
                operation="write"
            )
        except Exception as e:
            logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
            raise FileSystemException(
                message=f"Failed to copy file: {str(e)}",
                error_code="E004",
                file_path=source_path
            )

    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Moves a file from source to destination with proper error handling.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Returns:
            True if the file was moved successfully

        Raises:
            FileNotFoundError: If the source file doesn't exist
            FilePermissionError: If the file can't be moved
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate both source and destination paths
        source_path = sanitize_file_path(source_path)
        destination_path = sanitize_file_path(destination_path)
        
        if not validate_file_path(source_path):
            raise FileSystemException(
                message=f"Invalid source file path: {source_path}",
                error_code="E001",
                file_path=source_path
            )
            
        if not validate_file_path(destination_path):
            raise FileSystemException(
                message=f"Invalid destination file path: {destination_path}",
                error_code="E001",
                file_path=destination_path
            )

        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(file_path=source_path)

        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination_path)
        if destination_dir and not os.path.exists(destination_dir):
            try:
                create_directory_if_not_exists(destination_dir)
            except Exception as e:
                logger.error(f"Failed to create destination directory {destination_dir}: {e}")
                raise FileSystemException(
                    message=f"Failed to create destination directory: {destination_dir}",
                    error_code="E004",
                    file_path=destination_dir
                )

        try:
            with Timer("File move operation"):
                shutil.move(source_path, destination_path)
            logger.debug(f"Moved file from {source_path} to {destination_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error moving file from {source_path} to {destination_path}: {e}")
            raise FilePermissionError(
                file_path=destination_path,
                operation="write"
            )
        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            raise FileSystemException(
                message=f"Failed to move file: {str(e)}",
                error_code="E004",
                file_path=source_path
            )

    def get_file_info(self, file_path: str) -> dict:
        """
        Gets information about a file including size, modification time, etc.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file information

        Raises:
            FileNotFoundError: If the file doesn't exist
            FileSystemException: For other file-related errors
        """
        # Sanitize and validate the file path
        file_path = sanitize_file_path(file_path)
        if not validate_file_path(file_path):
            raise FileSystemException(
                message=f"Invalid file path: {file_path}",
                error_code="E001",
                file_path=file_path
            )

        # Check if the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path=file_path)

        try:
            stats = os.stat(file_path)
            extension = os.path.splitext(file_path)[1].lstrip(".")
            
            file_info = {
                "path": file_path,
                "size": stats.st_size,
                "size_formatted": format_file_size(stats.st_size),
                "created_time": stats.st_ctime,
                "modified_time": stats.st_mtime,
                "accessed_time": stats.st_atime,
                "extension": extension,
                "filename": os.path.basename(file_path),
                "directory": os.path.dirname(file_path)
            }
            
            return file_info
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise FileSystemException(
                message=f"Failed to get file information: {str(e)}",
                error_code="E001",
                file_path=file_path
            )

    def list_directory(self, directory_path: str, pattern: str = None) -> list:
        """
        Lists files and directories in the specified directory.

        Args:
            directory_path: Path to the directory
            pattern: Optional filename pattern to filter results

        Returns:
            List of file and directory names

        Raises:
            FileNotFoundError: If the directory doesn't exist
            FilePermissionError: If the directory can't be accessed
            FileSystemException: For other directory-related errors
        """
        # Sanitize and validate the directory path
        directory_path = sanitize_file_path(directory_path)
        if not validate_file_path(directory_path):
            raise FileSystemException(
                message=f"Invalid directory path: {directory_path}",
                error_code="E001",
                file_path=directory_path
            )

        # Check if the directory exists
        if not os.path.isdir(directory_path):
            raise FileNotFoundError(file_path=directory_path)

        # Check if the directory is accessible
        if not os.access(directory_path, os.R_OK):
            raise FilePermissionError(
                file_path=directory_path,
                operation="read"
            )

        try:
            items = os.listdir(directory_path)
            
            # Apply pattern filtering if specified
            if pattern:
                import fnmatch
                items = [item for item in items if fnmatch.fnmatch(item, pattern)]
                
            return items
        except PermissionError as e:
            logger.error(f"Permission error listing directory {directory_path}: {e}")
            raise FilePermissionError(
                file_path=directory_path,
                operation="read"
            )
        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            raise FileSystemException(
                message=f"Failed to list directory: {str(e)}",
                error_code="E001",
                file_path=directory_path
            )

    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensures that a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory

        Returns:
            True if the directory exists or was created successfully

        Raises:
            FilePermissionError: If the directory can't be created
            FileSystemException: For other directory-related errors
        """
        # Sanitize and validate the directory path
        directory_path = sanitize_file_path(directory_path)
        if not validate_file_path(directory_path):
            raise FileSystemException(
                message=f"Invalid directory path: {directory_path}",
                error_code="E001",
                file_path=directory_path
            )

        # Check if the directory already exists
        if os.path.isdir(directory_path):
            return True

        try:
            create_directory_if_not_exists(directory_path)
            logger.debug(f"Created directory: {directory_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error creating directory {directory_path}: {e}")
            raise FilePermissionError(
                file_path=directory_path,
                operation="write"
            )
        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            raise FileSystemException(
                message=f"Failed to create directory: {str(e)}",
                error_code="E004",
                file_path=directory_path
            )

    def clean_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Cleans up temporary files older than the specified age.

        Args:
            max_age_hours: Maximum age of files to keep in hours

        Returns:
            Number of files deleted

        Raises:
            FileSystemException: For directory-related errors
        """
        # Ensure the temporary directory exists
        if not os.path.isdir(self.temp_directory):
            logger.warning(f"Temporary directory does not exist: {self.temp_directory}")
            return 0

        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (max_age_hours * 3600)
            
            files_deleted = 0
            
            for item in os.listdir(self.temp_directory):
                item_path = os.path.join(self.temp_directory, item)
                
                # Skip directories
                if not os.path.isfile(item_path):
                    continue
                    
                # Check modification time
                if os.path.getmtime(item_path) < cutoff_time:
                    try:
                        os.remove(item_path)
                        files_deleted += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete temporary file {item_path}: {e}")
            
            logger.info(f"Cleaned up {files_deleted} temporary files older than {max_age_hours} hours")
            return files_deleted
        except Exception as e:
            logger.error(f"Error cleaning temporary files: {e}")
            raise FileSystemException(
                message=f"Failed to clean temporary files: {str(e)}",
                error_code="E004",
                file_path=self.temp_directory
            )

    def get_safe_path(self, path: str) -> str:
        """
        Gets a safe path relative to the base directory.

        Args:
            path: Input path

        Returns:
            Safe absolute path

        Raises:
            FileSystemException: If the path is unsafe
        """
        # Sanitize the input path
        sanitized_path = sanitize_file_path(path)
        
        # Join with the base directory
        full_path = PathUtils.join_paths(self.base_directory, sanitized_path)
        
        # Verify that the resulting path is safe
        if not PathUtils.is_safe_path(full_path, self.base_directory):
            logger.error(f"Unsafe path detected: {path}")
            raise FileSystemException(
                message=f"Path traversal attempt detected: {path}",
                error_code="E001",
                file_path=path
            )
        
        return full_path


class TempFileContext:
    """
    Context manager for creating and automatically cleaning up temporary files.
    """
    
    def __init__(self, adapter: FileSystemAdapter, prefix: str = "", suffix: str = "", delete_on_exit: bool = True):
        """
        Initializes the TempFileContext with the file system adapter.

        Args:
            adapter: The FileSystemAdapter instance
            prefix: Prefix for the temporary file name
            suffix: Suffix for the temporary file name
            delete_on_exit: Whether to delete the file when exiting the context
        """
        self.adapter = adapter
        self.delete_on_exit = delete_on_exit
        self.file_path = adapter.create_temp_file(prefix, suffix)
    
    def __enter__(self) -> str:
        """
        Enters the context and returns the temporary file path.

        Returns:
            Path to the temporary file
        """
        return self.file_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context and deletes the temporary file if configured.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.delete_on_exit:
            try:
                self.adapter.delete_file(self.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {self.file_path}: {e}")
        return False  # Don't suppress exceptions


class TempDirectoryContext:
    """
    Context manager for creating and automatically cleaning up temporary directories.
    """
    
    def __init__(self, adapter: FileSystemAdapter, prefix: str = "", delete_on_exit: bool = True):
        """
        Initializes the TempDirectoryContext with the file system adapter.

        Args:
            adapter: The FileSystemAdapter instance
            prefix: Prefix for the temporary directory name
            delete_on_exit: Whether to delete the directory when exiting the context
        """
        self.adapter = adapter
        self.delete_on_exit = delete_on_exit
        self.directory_path = adapter.create_temp_directory(prefix)
    
    def __enter__(self) -> str:
        """
        Enters the context and returns the temporary directory path.

        Returns:
            Path to the temporary directory
        """
        return self.directory_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context and deletes the temporary directory if configured.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.delete_on_exit:
            try:
                shutil.rmtree(self.directory_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary directory {self.directory_path}: {e}")
        return False  # Don't suppress exceptions