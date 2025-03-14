"""
Implements the 'info' command for the JSON to Excel Conversion Tool CLI, which analyzes and
displays detailed information about a JSON file's structure, complexity, and content preview
without performing conversion.
"""

import os  # v: built-in
from typing import Dict, Any, Optional  # v: built-in

from ..models.command_options import CommandOptions
from ..models.cli_response import CLIResponse, ResponseType
from ...backend.input_handler import InputHandler
from ...backend.json_parser import JSONParser
from ..formatters.json_preview_formatter import format_json_preview, generate_structure_preview


def execute_info_command(options: CommandOptions) -> CLIResponse:
    """
    Executes the 'info' command to analyze and display information about a JSON file.
    
    Args:
        options: Command options containing the file path and other parameters
        
    Returns:
        CLIResponse: Response containing JSON file analysis results or error information
    """
    # Validate command options
    if not options.validate():
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message="Invalid command options",
            error=options.error
        )
    
    try:
        # Create InputHandler instance for file operations
        input_handler = InputHandler()
        
        # Get basic file information
        file_info = input_handler.get_file_info(options.input_file)
        
        # Process the JSON file to get content and structure
        json_data, structure_info = input_handler.process_json_file(options.input_file)
        
        # Generate detailed structure analysis
        json_parser = JSONParser()
        detailed_structure = json_parser.get_structure_info(json_data)
        
        # Create content preview
        content_preview = format_json_preview(json_data)
        
        # Create structure preview
        structure_preview = generate_structure_preview(json_data)
        
        # Format file information for display
        formatted_file_info = format_file_info(file_info)
        
        # Format structure information for display
        formatted_structure_info = format_structure_info(detailed_structure)
        
        # Compile all information into a comprehensive result dictionary
        result = {
            "file_info": formatted_file_info,
            "structure_info": formatted_structure_info,
            "content_preview": content_preview,
            "structure_preview": structure_preview
        }
        
        # Return CLIResponse with SUCCESS status and the result data
        return CLIResponse(
            response_type=ResponseType.SUCCESS,
            message=f"Successfully analyzed JSON file: {os.path.basename(options.input_file)}",
            data=result
        )
    except Exception as e:
        # Handle errors with an ERROR response
        return CLIResponse(
            response_type=ResponseType.ERROR,
            message=f"Failed to analyze JSON file: {str(e)}"
        )


def format_file_info(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats basic file information for display.
    
    Args:
        file_info: Dictionary containing file information
        
    Returns:
        Formatted file information dictionary
    """
    # Extract relevant file information (name, size, path, etc.)
    formatted_info = {
        "name": os.path.basename(file_info.get("path", "")),
        "path": file_info.get("path", ""),
        "size": file_info.get("formatted_size", "Unknown"),
        "absolute_path": file_info.get("absolute_path", ""),
        "directory": file_info.get("directory", "")
    }
    
    # Format file timestamps in readable format
    last_modified = file_info.get("last_modified")
    if last_modified:
        from datetime import datetime
        formatted_info["last_modified"] = datetime.fromtimestamp(
            last_modified
        ).strftime("%Y-%m-%d %H:%M:%S")
    else:
        formatted_info["last_modified"] = "Unknown"
    
    return formatted_info


def format_structure_info(structure_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats JSON structure information for display.
    
    Args:
        structure_info: Dictionary containing structure information
        
    Returns:
        Formatted structure information dictionary
    """
    # Extract and format nesting level information
    max_nesting_level = structure_info.get("max_nesting_level", 0)
    nesting_assessment = "Flat"
    if max_nesting_level > 1:
        nesting_assessment = "Shallow"
    if max_nesting_level > 3:
        nesting_assessment = "Moderate"
    if max_nesting_level > 5:
        nesting_assessment = "Deep"
    if max_nesting_level > 8:
        nesting_assessment = "Very Deep"
    
    # Format array information (count, locations)
    array_count = structure_info.get("array_count", 0)
    array_paths = structure_info.get("array_paths", [])
    array_assessment = "None"
    if array_count > 0:
        array_assessment = "Simple"
    if array_count > 3:
        array_assessment = "Moderate"
    if array_count > 10:
        array_assessment = "Complex"
    
    # Calculate and include complexity score
    complexity_level = structure_info.get("complexity_level", "SIMPLE")
    complexity_score = structure_info.get("complexity_score", 0)
    
    # Determine recommended processing strategy based on structure
    strategy = structure_info.get("flattening_strategy", "nested")
    processing_recommendation = "Standard processing suitable"
    if complexity_level == "COMPLEX" or complexity_level == "VERY_COMPLEX":
        processing_recommendation = "Advanced processing recommended"
    
    formatted_info = {
        "nesting": {
            "level": max_nesting_level,
            "assessment": nesting_assessment
        },
        "arrays": {
            "count": array_count,
            "paths": array_paths[:5],  # Limit to first 5 for display
            "assessment": array_assessment
        },
        "complexity": {
            "level": complexity_level,
            "score": complexity_score
        },
        "processing": {
            "recommended_strategy": strategy,
            "assessment": processing_recommendation
        }
    }
    
    # Add truncated flag if array paths were limited
    if len(array_paths) > 5:
        formatted_info["arrays"]["truncated"] = True
        formatted_info["arrays"]["total_paths"] = len(array_paths)
    
    return formatted_info