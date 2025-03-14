"""
Initializes the backend_interface package which serves as a bridge between the web interface and the core backend functionality of the JSON to Excel Conversion Tool.
This module exports key classes and functions that enable the web application to interact with the backend conversion services.
"""

from .service_client import ServiceClient  # Provides a base client interface for the web application to interact with backend conversion services
from .conversion_client import ConversionClient  # Provides a specialized client for the web interface to interact with backend conversion services
from .serializers import ConversionOptionsSerializer  # Provides serialization for conversion options between web and backend formats
from .serializers import JobStatusSerializer  # Provides serialization for job status information
from .serializers import UploadFileSerializer  # Provides serialization for uploaded file information
from .serializers import ErrorResponseSerializer  # Provides serialization for error information
from .serializers import serialize_datetime  # Utility function for serializing datetime objects
from .serializers import deserialize_datetime  # Utility function for deserializing datetime strings
from .serializers import serialize_enum  # Utility function for serializing enum values
from .serializers import deserialize_enum  # Utility function for deserializing enum values

__all__ = ["ServiceClient", "ConversionClient", "ConversionOptionsSerializer", "JobStatusSerializer", "UploadFileSerializer", "ErrorResponseSerializer", "serialize_datetime", "deserialize_datetime", "serialize_enum", "deserialize_enum"]