"""
Initializes the pipelines package and exposes the core pipeline classes and utility functions for JSON to Excel conversion.

This module makes the ConversionPipeline class and related enums available to other modules without requiring them to import from specific pipeline modules.
"""

from .conversion_pipeline import (
    ConversionPipeline, 
    PipelineStage,
    PipelineStatus,
    create_pipeline_context,
    update_pipeline_context
)

__all__ = [
    "ConversionPipeline",
    "PipelineStage",
    "PipelineStatus",
    "create_pipeline_context",
    "update_pipeline_context"
]