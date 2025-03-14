"""
Initializes the exceptions package for the web interface component of the JSON to Excel Conversion Tool.

This module imports and re-exports all exception classes from the api_exceptions, file_exceptions,
and job_exceptions modules, providing a centralized access point for all custom exceptions
used in the web interface.
"""

# Import API-related exceptions
from .api_exceptions import (
    APIException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    MethodNotAllowedException,
    ConflictException,
    UnsupportedMediaTypeException,
    RateLimitExceededException,
    InternalServerErrorException,
    ServiceUnavailableException,
    ValidationException,
)

# Import file-related exceptions
from .file_exceptions import (
    FileException,
    FileUploadException,
    FileSizeExceededException,
    FileTypeNotAllowedException,
    FileEmptyException,
    FileCorruptedException,
    FileStorageException,
    FileDeletionException,
    InvalidJSONFileException,
    FileDownloadException,
)

# Import job-related exceptions
from .job_exceptions import (
    JobException,
    JobCreationException,
    JobNotFoundException,
    JobProcessingException,
    JobCancellationException,
    JobAlreadyCompleteException,
    JobQueueFullException,
    JobTimeoutException,
    JobResultNotFoundException,
)

# Re-export all exceptions - explicitly define what's available when using 'from web.exceptions import *'
__all__ = [
    # API exceptions
    'APIException',
    'BadRequestException',
    'UnauthorizedException',
    'ForbiddenException',
    'NotFoundException',
    'MethodNotAllowedException',
    'ConflictException',
    'UnsupportedMediaTypeException',
    'RateLimitExceededException',
    'InternalServerErrorException',
    'ServiceUnavailableException',
    'ValidationException',
    
    # File exceptions
    'FileException',
    'FileUploadException',
    'FileSizeExceededException',
    'FileTypeNotAllowedException',
    'FileEmptyException',
    'FileCorruptedException',
    'FileStorageException',
    'FileDeletionException',
    'InvalidJSONFileException',
    'FileDownloadException',
    
    # Job exceptions
    'JobException',
    'JobCreationException',
    'JobNotFoundException',
    'JobProcessingException',
    'JobCancellationException',
    'JobAlreadyCompleteException',
    'JobQueueFullException',
    'JobTimeoutException',
    'JobResultNotFoundException',
]