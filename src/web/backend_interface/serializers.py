"""
Provides serialization and deserialization functionality for data exchange between the web interface
and backend components of the JSON to Excel Conversion Tool. This module handles the conversion of
complex objects to JSON-serializable formats and back, ensuring proper data transformation between
the web UI and core conversion services.
"""

import datetime  # v: built-in
import json  # v: built-in
import typing  # v: built-in
import enum  # v: built-in

from ..models.conversion_options import ConversionOptions
from ..models.job_status import JobStatus, JobStatusEnum
from ..models.upload_file import UploadFile
from ...backend.models.error_response import ErrorResponse
from ...backend.models.excel_options import ExcelOptions, ArrayHandlingStrategy


def serialize_datetime(dt: datetime.datetime) -> typing.Optional[str]:
    """
    Converts a datetime object to an ISO format string for JSON serialization.
    
    Args:
        dt: The datetime object to serialize
        
    Returns:
        ISO format string representation of the datetime or None if dt is None
    """
    if dt is None:
        return None
    return dt.isoformat()


def deserialize_datetime(dt_str: str) -> typing.Optional[datetime.datetime]:
    """
    Converts an ISO format string back to a datetime object.
    
    Args:
        dt_str: The ISO format string to deserialize
        
    Returns:
        Datetime object parsed from the string or None if dt_str is None
    """
    if dt_str is None:
        return None
    return datetime.datetime.fromisoformat(dt_str)


def serialize_enum(enum_value: enum.Enum) -> typing.Optional[str]:
    """
    Converts an enum value to its string representation for JSON serialization.
    
    Args:
        enum_value: The enum value to serialize
        
    Returns:
        String representation of the enum value or None if enum_value is None
    """
    if enum_value is None:
        return None
    return enum_value.name


def deserialize_enum(enum_str: str, enum_class: type) -> typing.Optional[enum.Enum]:
    """
    Converts a string back to an enum value of the specified enum class.
    
    Args:
        enum_str: The string representation of the enum value
        enum_class: The enum class to use for conversion
        
    Returns:
        Enum value corresponding to the string or None if enum_str is None
    """
    if enum_str is None:
        return None
    return enum_class[enum_str]


class ConversionOptionsSerializer:
    """Serializer for conversion options between web interface and backend formats."""
    
    @staticmethod
    def serialize(options: ConversionOptions) -> typing.Optional[dict]:
        """
        Serializes ConversionOptions to a JSON-compatible dictionary.
        
        Args:
            options: The ConversionOptions object to serialize
            
        Returns:
            Dictionary representation of conversion options or None if options is None
        """
        if options is None:
            return None
        return options.to_dict()
    
    @staticmethod
    def deserialize(data: dict) -> typing.Optional[ConversionOptions]:
        """
        Deserializes a dictionary to a ConversionOptions object.
        
        Args:
            data: Dictionary containing conversion options data
            
        Returns:
            ConversionOptions object created from the dictionary or None if data is None
        """
        if data is None:
            return None
        return ConversionOptions.from_dict(data)
    
    @staticmethod
    def to_backend_format(options: ConversionOptions) -> typing.Optional[ExcelOptions]:
        """
        Converts web ConversionOptions to backend ExcelOptions format.
        
        Args:
            options: The ConversionOptions object to convert
            
        Returns:
            ExcelOptions object for backend processing or None if options is None
        """
        if options is None:
            return None
        return options.to_excel_options()
    
    @staticmethod
    def from_backend_format(excel_options: ExcelOptions) -> typing.Optional[ConversionOptions]:
        """
        Converts backend ExcelOptions to web ConversionOptions format.
        
        Args:
            excel_options: The ExcelOptions object to convert
            
        Returns:
            ConversionOptions object for web interface or None if excel_options is None
        """
        if excel_options is None:
            return None
        
        # Convert ExcelOptions to dictionary
        options_dict = excel_options.to_dict()
        
        # Map backend enum values to web string representations
        if 'array_handling' in options_dict:
            if options_dict['array_handling'] == ArrayHandlingStrategy.EXPAND.value:
                options_dict['array_handling'] = 'expand'
            elif options_dict['array_handling'] == ArrayHandlingStrategy.JOIN.value:
                options_dict['array_handling'] = 'join'
        
        # Create ConversionOptions from the mapped dictionary
        return ConversionOptions.from_dict(options_dict)


class JobStatusSerializer:
    """Serializer for job status information between web interface and JSON formats."""
    
    @staticmethod
    def serialize(job_status: JobStatus) -> typing.Optional[dict]:
        """
        Serializes JobStatus to a JSON-compatible dictionary.
        
        Args:
            job_status: The JobStatus object to serialize
            
        Returns:
            Dictionary representation of job status or None if job_status is None
        """
        if job_status is None:
            return None
        
        status_dict = job_status.to_dict()
        
        # Ensure datetime is properly serialized
        if 'last_updated' in status_dict and status_dict['last_updated'] is not None:
            status_dict['last_updated'] = serialize_datetime(
                datetime.datetime.fromisoformat(status_dict['last_updated'])
            )
        
        # Ensure status enum is properly serialized
        if 'status' in status_dict and status_dict['status'] is not None:
            # It's already a string from to_dict() but we include this for consistency
            pass
        
        return status_dict
    
    @staticmethod
    def deserialize(data: dict) -> typing.Optional[JobStatus]:
        """
        Deserializes a dictionary to a JobStatus object.
        
        Args:
            data: Dictionary containing job status data
            
        Returns:
            JobStatus object created from the dictionary or None if data is None
        """
        if data is None:
            return None
        
        # Convert serialized datetime strings to datetime objects
        if 'last_updated' in data and data['last_updated'] is not None:
            data['last_updated'] = serialize_datetime(
                deserialize_datetime(data['last_updated'])
            )
        
        # Convert serialized status enum strings to enum values
        if 'status' in data and data['status'] is not None:
            # JobStatus.from_dict handles the enum conversion
            pass
        
        return JobStatus.from_dict(data)
    
    @staticmethod
    def to_api_response(job_status: JobStatus) -> dict:
        """
        Converts JobStatus to a format suitable for API responses.
        
        Args:
            job_status: The JobStatus object to convert
            
        Returns:
            API-friendly representation of job status
        """
        status_dict = JobStatusSerializer.serialize(job_status)
        
        # Format the response for API consumption (camelCase keys if needed)
        api_response = {
            'jobId': status_dict.get('job_id'),
            'status': status_dict.get('status'),
            'progressPercentage': status_dict.get('progress_percentage'),
            'message': status_dict.get('message'),
            'lastUpdated': status_dict.get('last_updated'),
        }
        
        # Include error information if present
        if 'error' in status_dict and status_dict['error']:
            api_response['error'] = status_dict['error']
        
        return api_response


class UploadFileSerializer:
    """Serializer for uploaded file information between web interface and JSON formats."""
    
    @staticmethod
    def serialize(upload_file: UploadFile) -> typing.Optional[dict]:
        """
        Serializes UploadFile to a JSON-compatible dictionary.
        
        Args:
            upload_file: The UploadFile object to serialize
            
        Returns:
            Dictionary representation of upload file or None if upload_file is None
        """
        if upload_file is None:
            return None
        
        file_dict = upload_file.to_dict()
        
        # Ensure datetime is properly serialized
        if 'upload_timestamp' in file_dict and file_dict['upload_timestamp'] is not None:
            file_dict['upload_timestamp'] = serialize_datetime(
                datetime.datetime.fromisoformat(file_dict['upload_timestamp'])
            )
        
        # Ensure status enum is properly serialized
        if 'status' in file_dict and file_dict['status'] is not None:
            # It's already a string from to_dict() but we include this for consistency
            pass
        
        return file_dict
    
    @staticmethod
    def deserialize(data: dict) -> typing.Optional[UploadFile]:
        """
        Deserializes a dictionary to an UploadFile object.
        
        Args:
            data: Dictionary containing upload file data
            
        Returns:
            UploadFile object created from the dictionary or None if data is None
        """
        if data is None:
            return None
        
        # Convert serialized datetime strings to datetime objects
        if 'upload_timestamp' in data and data['upload_timestamp'] is not None:
            data['upload_timestamp'] = serialize_datetime(
                deserialize_datetime(data['upload_timestamp'])
            )
        
        # Convert serialized status enum strings to enum values
        if 'status' in data and data['status'] is not None:
            # UploadFile.from_dict handles the enum conversion
            pass
        
        return UploadFile.from_dict(data)
    
    @staticmethod
    def to_api_response(upload_file: UploadFile) -> dict:
        """
        Converts UploadFile to a format suitable for API responses.
        
        Args:
            upload_file: The UploadFile object to convert
            
        Returns:
            API-friendly representation of upload file
        """
        file_dict = UploadFileSerializer.serialize(upload_file)
        
        # Format the response for API consumption (camelCase keys if needed)
        api_response = {
            'fileId': file_dict.get('file_id'),
            'originalFilename': file_dict.get('original_filename'),
            'secureFilename': file_dict.get('secure_filename'),
            'fileSize': file_dict.get('file_size'),
            'contentType': file_dict.get('content_type'),
            'status': file_dict.get('status'),
            'uploadTimestamp': file_dict.get('upload_timestamp'),
        }
        
        # Include validation result if present
        if 'validation_result' in file_dict and file_dict['validation_result']:
            api_response['validation'] = file_dict['validation_result']
        
        # Don't include sensitive information like file_path in the API response
        
        return api_response


class ErrorResponseSerializer:
    """Serializer for error responses between backend and web interface formats."""
    
    @staticmethod
    def serialize(error: ErrorResponse) -> typing.Optional[dict]:
        """
        Serializes ErrorResponse to a JSON-compatible dictionary.
        
        Args:
            error: The ErrorResponse object to serialize
            
        Returns:
            Dictionary representation of error response or None if error is None
        """
        if error is None:
            return None
        
        error_dict = error.to_dict()
        
        # Ensure datetime is properly serialized
        if 'timestamp' in error_dict and error_dict['timestamp'] is not None:
            error_dict['timestamp'] = serialize_datetime(
                datetime.datetime.fromisoformat(error_dict['timestamp'])
            )
        
        # Ensure category and severity enums are properly serialized
        if 'category' in error_dict and error_dict['category'] is not None:
            # It's already a string from to_dict() but we include this for consistency
            pass
        
        if 'severity' in error_dict and error_dict['severity'] is not None:
            # It's already a string from to_dict() but we include this for consistency
            pass
        
        return error_dict
    
    @staticmethod
    def deserialize(data: dict) -> typing.Optional[ErrorResponse]:
        """
        Deserializes a dictionary to an ErrorResponse object.
        
        Args:
            data: Dictionary containing error response data
            
        Returns:
            ErrorResponse object created from the dictionary or None if data is None
        """
        if data is None:
            return None
        
        # Convert serialized datetime strings to datetime objects
        if 'timestamp' in data and data['timestamp'] is not None:
            data['timestamp'] = serialize_datetime(
                deserialize_datetime(data['timestamp'])
            )
        
        # Convert serialized enum strings to enum values
        # ErrorResponse.from_dict handles the enum conversion
        
        return ErrorResponse.from_dict(data)
    
    @staticmethod
    def to_api_response(error: ErrorResponse) -> dict:
        """
        Converts ErrorResponse to a format suitable for API responses.
        
        Args:
            error: The ErrorResponse object to convert
            
        Returns:
            API-friendly representation of error response
        """
        error_dict = ErrorResponseSerializer.serialize(error)
        
        # Format the response for API consumption (camelCase keys if needed)
        api_response = {
            'errorId': error_dict.get('error_id'),
            'errorCode': error_dict.get('error_code'),
            'message': error_dict.get('message'),
            'category': error_dict.get('category'),
            'severity': error_dict.get('severity'),
            'timestamp': error_dict.get('timestamp'),
            'sourceComponent': error_dict.get('source_component'),
            'isRecoverable': error_dict.get('is_recoverable'),
            'resolutionSteps': error_dict.get('resolution_steps'),
        }
        
        # Include context information if present
        if 'context' in error_dict and error_dict['context']:
            api_response['context'] = error_dict['context']
        
        # Include user-friendly message
        api_response['userMessage'] = error.get_user_message()
        
        # Remove traceback for non-debug environments to avoid exposing technical details
        # Include it only in debug mode or for developers
        import os
        if os.environ.get('DEBUG', 'False').lower() == 'true':
            api_response['traceback'] = error_dict.get('traceback')
        
        return api_response