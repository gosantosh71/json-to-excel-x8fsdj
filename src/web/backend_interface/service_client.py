"""
Provides a client interface for the web application to interact with the backend conversion services of the JSON to Excel Conversion Tool.
This module serves as a bridge between the web interface and the core backend functionality, handling file conversion, validation, and error management.
"""

import logging  # v: built-in - For logging client operations and errors
import os  # v: built-in - For file path operations
from typing import Dict, List, Any, Optional, Tuple  # v: built-in - For type hints in function signatures

from ...backend.services.conversion_service import ConversionService  # For converting JSON data to Excel format
from ...backend.services.validation_service import ValidationService  # For validating JSON files and content
from ...backend.models.error_response import ErrorResponse  # For handling and serializing error responses
from .serializers import ConversionOptionsSerializer  # For serializing conversion options between web and backend formats

# Initialize logger
logger = logging.getLogger(__name__)


class ServiceClient:
    """
    A client class that provides an interface for the web application to interact with backend conversion services.
    """

    def __init__(self, max_file_size_mb: Optional[int] = None, max_nesting_level: Optional[int] = None):
        """
        Initializes a new ServiceClient instance with the necessary dependencies.

        Args:
            max_file_size_mb: Maximum file size in MB for the conversion service.
            max_nesting_level: Maximum nesting level allowed for JSON structures.
        """
        # Initialize ConversionService with a new ConversionService instance
        self._conversion_service = ConversionService(max_file_size_mb=max_file_size_mb, max_nesting_level=max_nesting_level)
        # Initialize ValidationService with a new ValidationService instance
        self._validation_service = ValidationService(max_file_size_mb=max_file_size_mb, max_nesting_level=max_nesting_level)
        # Initialize ConversionOptionsSerializer with a new ConversionOptionsSerializer instance
        self._options_serializer = ConversionOptionsSerializer()
        # Set up logging for the service client
        self._logger = logger
        self._logger.info("ServiceClient initialized")

    def convert_file(self, input_path: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON file to Excel format using the backend conversion service.

        Args:
            input_path: The path to the input JSON file.
            output_path: The path to save the converted Excel file.
            options: Optional conversion options.

        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A dictionary containing conversion summary information.
            - A dictionary containing error details, if any.
        """
        # Log the start of file conversion
        self._logger.info(f"Starting file conversion: input_path={input_path}, output_path={output_path}, options={options}")

        try:
            # Process options using _process_options if provided
            processed_options = self._process_options(options)

            # Call _conversion_service.convert_json_to_excel with input_path, output_path, and processed options
            success, summary, error = self._conversion_service.convert_json_to_excel(input_path, output_path, excel_options=processed_options)

            if success:
                # If conversion is successful, return (True, summary, None)
                self._logger.info(f"File conversion successful: input_path={input_path}, output_path={output_path}")
                return True, summary, None
            else:
                # If conversion fails, convert error to dictionary and return (False, summary, error_dict)
                error_dict = error.to_dict() if error else None
                self._logger.error(f"File conversion failed: input_path={input_path}, output_path={output_path}, error={error_dict}")
                return False, summary, error_dict
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during file conversion: {e}")
            return False, {}, {"message": str(e)}

    def convert_json_string(self, json_string: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON string to Excel format using the backend conversion service.

        Args:
            json_string: The JSON data as a string.
            output_path: The path to save the converted Excel file.
            options: Optional conversion options.

        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A dictionary containing conversion summary information.
            - A dictionary containing error details, if any.
        """
        # Log the start of JSON string conversion
        self._logger.info(f"Starting JSON string conversion: output_path={output_path}, options={options}")

        try:
            # Process options using _process_options if provided
            processed_options = self._process_options(options)

            # Call _conversion_service.convert_json_string_to_excel with json_string, output_path, and processed options
            success, summary, error = self._conversion_service.convert_json_string_to_excel(json_string, output_path, excel_options=processed_options)

            if success:
                # If conversion is successful, return (True, summary, None)
                self._logger.info(f"JSON string conversion successful: output_path={output_path}")
                return True, summary, None
            else:
                # If conversion fails, convert error to dictionary and return (False, summary, error_dict)
                error_dict = error.to_dict() if error else None
                self._logger.error(f"JSON string conversion failed: output_path={output_path}, error={error_dict}")
                return False, summary, error_dict
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during JSON string conversion: {e}")
            return False, {}, {"message": str(e)}

    def convert_file_to_bytes(self, input_path: str, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON file to Excel format and returns the result as bytes.

        Args:
            input_path: The path to the input JSON file.
            options: Optional conversion options.

        Returns:
            A tuple containing:
            - The Excel content as bytes, or None on failure.
            - A dictionary containing conversion summary information.
            - A dictionary containing error details, if any.
        """
        # Log the start of file to bytes conversion
        self._logger.info(f"Starting file to bytes conversion: input_path={input_path}, options={options}")

        try:
            # Process options using _process_options if provided
            processed_options = self._process_options(options)

            # Call _conversion_service.convert_json_to_excel_bytes with input_path and processed options
            excel_bytes, summary, error = self._conversion_service.convert_json_to_excel_bytes(input_path, excel_options=processed_options)

            if excel_bytes:
                # If conversion is successful, return (excel_bytes, summary, None)
                self._logger.info(f"File to bytes conversion successful: input_path={input_path}")
                return excel_bytes, summary, None
            else:
                # If conversion fails, convert error to dictionary and return (None, summary, error_dict)
                error_dict = error.to_dict() if error else None
                self._logger.error(f"File to bytes conversion failed: input_path={input_path}, error={error_dict}")
                return None, summary, error_dict
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during file to bytes conversion: {e}")
            return None, {}, {"message": str(e)}

    def convert_json_string_to_bytes(self, json_string: str, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Converts a JSON string to Excel format and returns the result as bytes.

        Args:
            json_string: The JSON data as a string.
            options: Optional conversion options.

        Returns:
            A tuple containing:
            - The Excel content as bytes, or None on failure.
            - A dictionary containing conversion summary information.
            - A dictionary containing error details, if any.
        """
        # Log the start of JSON string to bytes conversion
        self._logger.info(f"Starting JSON string to bytes conversion: options={options}")

        try:
            # Process options using _process_options if provided
            processed_options = self._process_options(options)

            # Call _conversion_service.convert_json_string_to_bytes with json_string and processed options
            excel_bytes, summary, error = self._conversion_service.convert_json_string_to_bytes(json_string, excel_options=processed_options)

            if excel_bytes:
                # If conversion is successful, return (excel_bytes, summary, None)
                self._logger.info("JSON string to bytes conversion successful")
                return excel_bytes, summary, None
            else:
                # If conversion fails, convert error to dictionary and return (None, summary, error_dict)
                error_dict = error.to_dict() if error else None
                self._logger.error(f"JSON string to bytes conversion failed: error={error_dict}")
                return None, summary, error_dict
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during JSON string to bytes conversion: {e}")
            return None, {}, {"message": str(e)}

    def validate_json_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates a JSON file without performing the full conversion.

        Args:
            file_path: The path to the JSON file to validate.

        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A dictionary containing validation details or error information.
        """
        # Log the start of file validation
        self._logger.info(f"Starting file validation: file_path={file_path}")

        try:
            # Call _validation_service.validate_json_file with file_path
            success, errors, _ = self._validation_service.validate_json_file(file_path)

            if success:
                # If validation is successful, create validation summary and return (True, summary)
                summary = self._validation_service.create_validation_summary(_)
                self._logger.info(f"File validation successful: file_path={file_path}")
                return True, summary
            else:
                # If validation fails, convert errors to dictionaries and return (False, {'errors': error_dicts})
                error_dicts = [error.to_dict() for error in errors]
                self._logger.error(f"File validation failed: file_path={file_path}, errors={error_dicts}")
                return False, {"errors": error_dicts}
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during file validation: {e}")
            return False, {"message": str(e)}

    def validate_json_string(self, json_string: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates a JSON string without performing the full conversion.

        Args:
            json_string: The JSON string to validate.

        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A dictionary containing validation details or error information.
        """
        # Log the start of JSON string validation
        self._logger.info(f"Starting JSON string validation")

        try:
            # Call _validation_service.validate_json_string with json_string
            success, errors, _ = self._validation_service.validate_json_string(json_string)

            if success:
                # If validation is successful, create validation summary and return (True, summary)
                summary = self._validation_service.create_validation_summary(_)
                self._logger.info("JSON string validation successful")
                return True, summary
            else:
                # If validation fails, convert errors to dictionaries and return (False, {'errors': error_dicts})
                error_dicts = [error.to_dict() for error in errors]
                self._logger.error(f"JSON string validation failed: errors={error_dicts}")
                return False, {"errors": error_dicts}
        except Exception as e:
            self._logger.exception(f"An unexpected error occurred during JSON string validation: {e}")
            return False, {"message": str(e)}

    def _process_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes web interface options into backend-compatible format.

        Args:
            options: Dictionary of web interface options.

        Returns:
            Dictionary of backend-compatible options.
        """
        # If options is None, return None
        if options is None:
            return None

        # If options contains a 'conversion_options' key, extract it
        if 'conversion_options' in options:
            options = options['conversion_options']

        # Use _options_serializer.to_backend_format to convert web options to backend format
        conversion_options = self._options_serializer.deserialize(options)
        backend_options = self._options_serializer.to_backend_format(conversion_options)

        # Return the converted options as a dictionary
        return backend_options.to_dict() if backend_options else None

    def _handle_error(self, error: ErrorResponse) -> Dict[str, Any]:
        """
        Handles and formats error responses from backend services.

        Args:
            error: The ErrorResponse object.

        Returns:
            A dictionary representation of the error.
        """
        # Log the error details
        self._logger.error(f"Handling error: {error.message}")

        # Convert the ErrorResponse to a dictionary using error.to_dict()
        error_dict = error.to_dict()

        # Return the error dictionary
        return error_dict