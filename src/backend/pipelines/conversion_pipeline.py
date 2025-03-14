"""
Implements the core conversion pipeline for the JSON to Excel Conversion Tool.

This module orchestrates the end-to-end process of converting JSON files to Excel format
by coordinating the various components including input handling, JSON parsing, data
transformation, and Excel generation.
"""

import os  # v: built-in
from typing import Dict, List, Any, Optional, Tuple, Union  # v: built-in
from enum import Enum  # v: built-in
import pandas  # v: 1.5.0+
import time  # v: built-in

from ..input_handler import InputHandler
from ..json_parser import JSONParser
from ..data_transformer import DataTransformer
from ..excel_generator import ExcelGenerator
from ..models.json_data import JSONData
from ..models.excel_options import ExcelOptions
from ..models.error_response import ErrorResponse
from ..error_handler import ErrorHandler, ErrorHandlerContext
from ..services.validation_service import ValidationService
from ..services.conversion_service import ConversionService
from ..logger import get_logger
from ..utils import timing_decorator, validate_file_path

# Initialize logger for this module
logger = get_logger(__name__)


class PipelineStage(Enum):
    """An enumeration of pipeline stages for tracking progress and status."""
    VALIDATION = "validation"
    INPUT_PROCESSING = "input_processing"
    TRANSFORMATION = "transformation"
    EXCEL_GENERATION = "excel_generation"
    COMPLETION = "completion"


class PipelineStatus(Enum):
    """An enumeration of pipeline stage statuses for tracking execution state."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


def create_pipeline_context(input_path: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Creates a context dictionary for pipeline execution with metadata and tracking information.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to the output Excel file
        options: Optional configuration options
        
    Returns:
        A context dictionary with pipeline execution metadata
    """
    # Create base context with paths and timestamp
    context = {
        "input_path": input_path,
        "output_path": output_path,
        "timestamp": time.time(),
        "start_time": time.time(),
        "options": options or {},
    }
    
    # Initialize pipeline stages tracking
    context["pipeline_stages"] = {
        PipelineStage.VALIDATION.value: {"status": PipelineStatus.PENDING.value, "time": 0},
        PipelineStage.INPUT_PROCESSING.value: {"status": PipelineStatus.PENDING.value, "time": 0},
        PipelineStage.TRANSFORMATION.value: {"status": PipelineStatus.PENDING.value, "time": 0},
        PipelineStage.EXCEL_GENERATION.value: {"status": PipelineStatus.PENDING.value, "time": 0},
        PipelineStage.COMPLETION.value: {"status": PipelineStatus.PENDING.value, "time": 0},
    }
    
    # Initialize metrics
    context["metrics"] = {
        "total_execution_time": 0,
        "json_parsing_time": 0,
        "transformation_time": 0,
        "excel_generation_time": 0,
    }
    
    return context


def update_pipeline_context(
    context: Dict[str, Any], 
    stage_name: str, 
    status: str, 
    stage_data: Optional[Dict[str, Any]] = None,
    execution_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Updates the pipeline context with stage information and metrics.
    
    Args:
        context: The pipeline context to update
        stage_name: Name of the stage being updated
        status: Status to set for the stage
        stage_data: Optional data to add to the stage
        execution_time: Optional execution time to record
        
    Returns:
        The updated context dictionary
    """
    # Update stage status and timestamp
    if stage_name in context["pipeline_stages"]:
        context["pipeline_stages"][stage_name]["status"] = status
        context["pipeline_stages"][stage_name]["updated_at"] = time.time()
        
        # Add any stage-specific data if provided
        if stage_data:
            context["pipeline_stages"][stage_name]["data"] = stage_data
    
    # Update execution time if provided
    if execution_time is not None:
        if stage_name == PipelineStage.INPUT_PROCESSING.value:
            context["metrics"]["json_parsing_time"] = execution_time
        elif stage_name == PipelineStage.TRANSFORMATION.value:
            context["metrics"]["transformation_time"] = execution_time
        elif stage_name == PipelineStage.EXCEL_GENERATION.value:
            context["metrics"]["excel_generation_time"] = execution_time
        elif stage_name == PipelineStage.COMPLETION.value:
            context["metrics"]["total_execution_time"] = time.time() - context["start_time"]
    
    return context


class ConversionPipeline:
    """
    A pipeline class that orchestrates the end-to-end process of converting JSON files to Excel format.
    """
    
    def __init__(
        self,
        input_handler: Optional[InputHandler] = None,
        data_transformer: Optional[DataTransformer] = None,
        excel_generator: Optional[ExcelGenerator] = None,
        validation_service: Optional[ValidationService] = None,
        conversion_service: Optional[ConversionService] = None
    ):
        """
        Initializes a new ConversionPipeline instance with all required components.
        
        Args:
            input_handler: Custom InputHandler instance or None to create default
            data_transformer: Custom DataTransformer instance or None to create default
            excel_generator: Custom ExcelGenerator instance or None to create default
            validation_service: Custom ValidationService instance or None to create default
            conversion_service: Custom ConversionService instance or None to create default
        """
        self._input_handler = input_handler or InputHandler()
        self._data_transformer = data_transformer or DataTransformer()
        self._excel_generator = excel_generator or ExcelGenerator()
        self._validation_service = validation_service or ValidationService()
        self._conversion_service = conversion_service or ConversionService()
        self._error_handler = ErrorHandler()
        self._logger = logger
        
        self._logger.info("ConversionPipeline initialized")
    
    @timing_decorator
    def execute(
        self, 
        input_path: str, 
        output_path: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any], Optional[ErrorResponse]]:
        """
        Executes the complete JSON to Excel conversion pipeline.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Path to the output Excel file
            options: Optional configuration options
            
        Returns:
            Success flag, pipeline results, and any error that occurred
        """
        self._logger.info(f"Starting conversion pipeline: {input_path} -> {output_path}")
        
        # Create context for pipeline execution
        context = create_pipeline_context(input_path, output_path, options)
        
        # Stage 1: Validate input and output paths
        is_valid, error = self.validate_parameters(input_path, output_path, context)
        if not is_valid:
            self._logger.error(f"Validation failed: {error.message}")
            return False, {"status": "error", "stage": PipelineStage.VALIDATION.value}, error
        
        # Stage 2: Process input JSON file
        json_data, error = self.process_input(input_path, context)
        if error:
            self._logger.error(f"Input processing failed: {error.message}")
            return False, {"status": "error", "stage": PipelineStage.INPUT_PROCESSING.value}, error
        
        # Stage 3: Transform JSON data to DataFrame
        dataframe, error = self.transform_data(json_data, options or {}, context)
        if error:
            self._logger.error(f"Data transformation failed: {error.message}")
            return False, {"status": "error", "stage": PipelineStage.TRANSFORMATION.value}, error
        
        # Stage 4: Generate Excel file
        is_generated, error = self.generate_excel(dataframe, output_path, options or {}, json_data, context)
        if not is_generated:
            self._logger.error(f"Excel generation failed: {error.message}")
            return False, {"status": "error", "stage": PipelineStage.EXCEL_GENERATION.value}, error
        
        # Stage 5: Create pipeline results
        results = self.create_pipeline_results(context, json_data, dataframe, output_path)
        
        # Update final completion status
        update_pipeline_context(
            context, 
            PipelineStage.COMPLETION.value, 
            PipelineStatus.COMPLETED.value,
            stage_data={"message": "Pipeline execution completed successfully"}
        )
        
        self._logger.info(f"Conversion pipeline completed successfully: {input_path} -> {output_path}")
        return True, results, None
    
    def validate_parameters(
        self, 
        input_path: str, 
        output_path: str,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Validates the input and output parameters for the conversion pipeline.
        
        Args:
            input_path: Path to the input JSON file
            output_path: Path to the output Excel file
            context: Pipeline execution context
            
        Returns:
            Validation result and any error that occurred
        """
        self._logger.debug(f"Validating parameters: input={input_path}, output={output_path}")
        
        # Update pipeline stage status
        update_pipeline_context(
            context, 
            PipelineStage.VALIDATION.value, 
            PipelineStatus.IN_PROGRESS.value
        )
        
        try:
            # Validate input file exists and is readable
            if not validate_file_path(input_path):
                error = ErrorResponse(
                    message=f"Invalid input file path: {input_path}",
                    error_code="E001",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="ConversionPipeline"
                )
                error.add_resolution_step("Check that the file exists and is accessible")
                error.add_resolution_step("Verify the file path is correct")
                
                update_pipeline_context(
                    context, 
                    PipelineStage.VALIDATION.value, 
                    PipelineStatus.FAILED.value,
                    stage_data={"error": error.to_dict()}
                )
                return False, error
                
            # Validate output path can be written to
            if not validate_file_path(output_path):
                error = ErrorResponse(
                    message=f"Invalid output file path: {output_path}",
                    error_code="E001",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="ConversionPipeline"
                )
                error.add_resolution_step("Check that the output directory exists and is writable")
                error.add_resolution_step("Verify the output path is valid")
                
                update_pipeline_context(
                    context, 
                    PipelineStage.VALIDATION.value, 
                    PipelineStatus.FAILED.value,
                    stage_data={"error": error.to_dict()}
                )
                return False, error
            
            # Use ValidationService to perform more detailed validation
            is_valid, validation_errors = self._validation_service.validate_conversion_parameters(
                input_path, output_path, context.get("options")
            )
            
            if not is_valid:
                error = validation_errors[0] if validation_errors else ErrorResponse(
                    message="Validation failed with unspecified errors",
                    error_code="E001",
                    category=ErrorCategory.INPUT_ERROR,
                    severity=ErrorSeverity.ERROR,
                    source_component="ConversionPipeline"
                )
                
                update_pipeline_context(
                    context, 
                    PipelineStage.VALIDATION.value, 
                    PipelineStatus.FAILED.value,
                    stage_data={"error": error.to_dict()}
                )
                return False, error
            
            # All validations passed
            update_pipeline_context(
                context, 
                PipelineStage.VALIDATION.value, 
                PipelineStatus.COMPLETED.value,
                stage_data={"message": "Validation successful"}
            )
            return True, None
            
        except Exception as e:
            error = self.handle_pipeline_error(e, context, PipelineStage.VALIDATION.value)
            return False, error
    
    def process_input(
        self, 
        input_path: str,
        context: Dict[str, Any]
    ) -> Tuple[Optional[JSONData], Optional[ErrorResponse]]:
        """
        Processes the input JSON file and creates a JSONData object.
        
        Args:
            input_path: Path to the input JSON file
            context: Pipeline execution context
            
        Returns:
            JSONData object and any error that occurred
        """
        self._logger.debug(f"Processing input file: {input_path}")
        
        # Update pipeline stage status
        update_pipeline_context(
            context, 
            PipelineStage.INPUT_PROCESSING.value, 
            PipelineStatus.IN_PROGRESS.value
        )
        
        try:
            # Process the input file with timing
            start_time = time.time()
            
            # Use InputHandler to process the input file
            with ErrorHandlerContext("InputProcessing"):
                json_data = self._input_handler.get_json_data(input_path)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update pipeline context with results
            update_pipeline_context(
                context, 
                PipelineStage.INPUT_PROCESSING.value, 
                PipelineStatus.COMPLETED.value,
                stage_data={
                    "file_size_bytes": json_data.size_bytes,
                    "complexity_level": json_data.complexity_level.name,
                    "nesting_level": json_data.max_nesting_level,
                    "contains_arrays": json_data.contains_arrays,
                    "array_paths_count": len(json_data.array_paths) if json_data.array_paths else 0
                },
                execution_time=execution_time
            )
            
            self._logger.info(
                f"Input processing completed: {input_path}, size={json_data.size_bytes} bytes, "
                f"complexity={json_data.complexity_level.name}"
            )
            return json_data, None
            
        except Exception as e:
            error = self.handle_pipeline_error(e, context, PipelineStage.INPUT_PROCESSING.value)
            return None, error
    
    def transform_data(
        self, 
        json_data: JSONData,
        options: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[Optional[pandas.DataFrame], Optional[ErrorResponse]]:
        """
        Transforms JSON data into a pandas DataFrame.
        
        Args:
            json_data: The JSON data to transform
            options: Configuration options
            context: Pipeline execution context
            
        Returns:
            DataFrame and any error that occurred
        """
        self._logger.debug(f"Transforming JSON data to DataFrame")
        
        # Update pipeline stage status
        update_pipeline_context(
            context, 
            PipelineStage.TRANSFORMATION.value, 
            PipelineStatus.IN_PROGRESS.value
        )
        
        try:
            # Get array handling strategy from options
            array_handling = options.get("array_handling", "expand")
            
            # Configure the transformer with array handling strategy
            self._data_transformer.set_options(
                ExcelOptions(array_handling=array_handling)
            )
            
            # Transform JSON data to DataFrame with timing
            start_time = time.time()
            
            # Use DataTransformer to transform JSON data
            with ErrorHandlerContext("DataTransformation"):
                df, error = self._data_transformer.transform_data(json_data)
                
                if error:
                    update_pipeline_context(
                        context, 
                        PipelineStage.TRANSFORMATION.value, 
                        PipelineStatus.FAILED.value,
                        stage_data={"error": error.to_dict()}
                    )
                    return None, error
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update pipeline context with results
            update_pipeline_context(
                context, 
                PipelineStage.TRANSFORMATION.value, 
                PipelineStatus.COMPLETED.value,
                stage_data={
                    "rows": df.shape[0],
                    "columns": df.shape[1],
                    "array_handling": array_handling
                },
                execution_time=execution_time
            )
            
            self._logger.info(
                f"Data transformation completed: {df.shape[0]} rows, {df.shape[1]} columns"
            )
            return df, None
            
        except Exception as e:
            error = self.handle_pipeline_error(e, context, PipelineStage.TRANSFORMATION.value)
            return None, error
    
    def generate_excel(
        self, 
        dataframe: pandas.DataFrame,
        output_path: str,
        options: Dict[str, Any],
        json_data: JSONData,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[ErrorResponse]]:
        """
        Generates an Excel file from the transformed DataFrame.
        
        Args:
            dataframe: The DataFrame to convert to Excel
            output_path: Path to the output Excel file
            options: Configuration options
            json_data: The original JSON data (for context)
            context: Pipeline execution context
            
        Returns:
            Success flag and any error that occurred
        """
        self._logger.debug(f"Generating Excel file: {output_path}")
        
        # Update pipeline stage status
        update_pipeline_context(
            context, 
            PipelineStage.EXCEL_GENERATION.value, 
            PipelineStatus.IN_PROGRESS.value
        )
        
        try:
            # Create Excel options from options dictionary
            excel_options = ExcelOptions.from_dict(options)
            
            # Configure the generator with Excel options
            self._excel_generator.set_options(excel_options)
            
            # Generate Excel file with timing
            start_time = time.time()
            
            # Use ExcelGenerator to generate Excel file
            with ErrorHandlerContext("ExcelGeneration"):
                success, error = self._excel_generator.generate_excel(dataframe, output_path)
                
                if not success:
                    update_pipeline_context(
                        context, 
                        PipelineStage.EXCEL_GENERATION.value, 
                        PipelineStatus.FAILED.value,
                        stage_data={"error": error.to_dict()}
                    )
                    return False, error
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update pipeline context with results
            update_pipeline_context(
                context, 
                PipelineStage.EXCEL_GENERATION.value, 
                PipelineStatus.COMPLETED.value,
                stage_data={
                    "output_path": output_path,
                    "sheet_name": excel_options.sheet_name,
                    "output_size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                },
                execution_time=execution_time
            )
            
            self._logger.info(f"Excel generation completed: {output_path}")
            return True, None
            
        except Exception as e:
            error = self.handle_pipeline_error(e, context, PipelineStage.EXCEL_GENERATION.value)
            return False, error
    
    def create_pipeline_results(
        self, 
        context: Dict[str, Any],
        json_data: JSONData,
        dataframe: pandas.DataFrame,
        output_path: str
    ) -> Dict[str, Any]:
        """
        Creates a results dictionary with pipeline execution summary and metrics.
        
        Args:
            context: Pipeline execution context
            json_data: The JSON data that was processed
            dataframe: The transformed DataFrame
            output_path: Path to the output Excel file
            
        Returns:
            A dictionary containing pipeline results
        """
        # Extract pipeline stages and metrics
        stages = context["pipeline_stages"]
        metrics = context["metrics"]
        
        # Calculate total execution time
        total_time = time.time() - context["start_time"]
        
        # Get JSON structure information
        json_structure = {
            "is_nested": json_data.is_nested,
            "max_nesting_level": json_data.max_nesting_level,
            "contains_arrays": json_data.contains_arrays,
            "array_paths": json_data.array_paths,
            "complexity_level": json_data.complexity_level.name,
            "size_bytes": json_data.size_bytes
        }
        
        # Get DataFrame statistics
        df_stats = {
            "rows": dataframe.shape[0],
            "columns": dataframe.shape[1],
            "column_names": dataframe.columns.tolist()
        }
        
        # Get file sizes
        input_size = json_data.size_bytes
        output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        # Create and return the results dictionary
        results = {
            "status": "success",
            "input": {
                "path": context["input_path"],
                "size_bytes": input_size,
                "size_mb": round(input_size / (1024 * 1024), 2),
                "structure": json_structure
            },
            "output": {
                "path": output_path,
                "size_bytes": output_size,
                "size_mb": round(output_size / (1024 * 1024), 2),
                "rows": df_stats["rows"],
                "columns": df_stats["columns"]
            },
            "performance": {
                "total_execution_time": round(total_time, 3),
                "json_parsing_time": round(metrics["json_parsing_time"], 3),
                "transformation_time": round(metrics["transformation_time"], 3),
                "excel_generation_time": round(metrics["excel_generation_time"], 3)
            },
            "pipeline_stages": stages,
            "options_used": context["options"]
        }
        
        return results
    
    def handle_pipeline_error(
        self, 
        exception: Exception,
        context: Dict[str, Any],
        stage_name: str
    ) -> ErrorResponse:
        """
        Handles errors that occur during pipeline execution.
        
        Args:
            exception: The exception that occurred
            context: Pipeline execution context
            stage_name: Name of the stage where the error occurred
            
        Returns:
            A standardized error response
        """
        self._logger.error(f"Error in pipeline stage {stage_name}: {str(exception)}", exc_info=True)
        
        # Create error response using error handler
        error_response = self._error_handler.handle_exception(
            exception,
            message=f"Error during {stage_name}: {str(exception)}"
        )
        
        # Add pipeline context to the error response
        error_response.add_context("pipeline_stage", stage_name)
        
        # Update pipeline context with error information
        update_pipeline_context(
            context, 
            stage_name, 
            PipelineStatus.FAILED.value,
            stage_data={"error": error_response.to_dict()}
        )
        
        return error_response