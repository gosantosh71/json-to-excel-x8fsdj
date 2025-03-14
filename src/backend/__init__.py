"""
JSON to Excel Conversion Tool - Backend Module.

This module serves as the entry point for the backend components of the 
JSON to Excel Conversion Tool, exposing the core functionality for converting
JSON data to Excel format. The backend implements a pipeline architecture
with specialized components for input handling, JSON parsing, data transformation,
and Excel generation.

Version: 1.0.0
"""

# Import core components
from .input_handler import InputHandler
from .json_parser import JSONParser
from .data_transformer import DataTransformer
from .excel_generator import ExcelGenerator
from .error_handler import ErrorHandler, ErrorContext
from .services.conversion_service import ConversionService
from .services.validation_service import ValidationService
from .pipelines.conversion_pipeline import ConversionPipeline, PipelineStage, PipelineStatus
from .models.json_data import JSONData
from .models.excel_options import ExcelOptions, ArrayHandlingStrategy
from .models.error_response import ErrorResponse, ErrorCategory, ErrorSeverity

# Package metadata
__version__ = "1.0.0"
__author__ = "JSON to Excel Conversion Tool Team"

# Export public API
__all__ = [
    # Core components
    "InputHandler",
    "JSONParser", 
    "DataTransformer",
    "ExcelGenerator",
    
    # Error handling
    "ErrorHandler",
    "ErrorContext",
    "ErrorResponse",
    "ErrorCategory",
    "ErrorSeverity",
    
    # Services
    "ConversionService",
    "ValidationService",
    
    # Pipeline
    "ConversionPipeline",
    "PipelineStage",
    "PipelineStatus",
    
    # Data models
    "JSONData",
    "ExcelOptions",
    "ArrayHandlingStrategy"
]