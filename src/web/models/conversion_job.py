"""
Defines the ConversionJob model for representing and tracking JSON to Excel conversion jobs in the web interface.
This model encapsulates all information related to a conversion job, including input file, conversion options,
status tracking, and results.
"""

from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Dict, Optional, Any, List

from .job_status import JobStatus, JobStatusEnum
from .upload_file import UploadFile
from .conversion_options import ConversionOptions
from ...backend.models.error_response import ErrorResponse


@dataclass
class ConversionJob:
    """
    A data class that represents a JSON to Excel conversion job in the web interface,
    tracking all aspects of the conversion process.
    """
    job_id: str
    input_file: UploadFile
    options: ConversionOptions
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    output_file_path: Optional[str] = None
    output_file_name: Optional[str] = None
    conversion_summary: Optional[Dict[str, Any]] = None

    def __init__(self, job_id: Optional[str] = None, input_file: UploadFile, options: ConversionOptions):
        """
        Initializes a new ConversionJob instance with the provided job information.
        
        Args:
            job_id: Optional unique identifier for the job, generated if None
            input_file: The uploaded JSON file
            options: Configuration options for the conversion
        """
        self.job_id = job_id or str(uuid.uuid4())
        self.input_file = input_file
        self.options = options
        self.status = JobStatus(job_id=self.job_id, status=JobStatusEnum.PENDING)
        self.created_at = datetime.now()
        self.completed_at = None
        self.output_file_path = None
        self.output_file_name = None
        self.conversion_summary = None

    def update_status(self, status: JobStatusEnum, progress_percentage: int, message: str) -> None:
        """
        Updates the job status with new information.
        
        Args:
            status: The new status for the job
            progress_percentage: The updated progress percentage
            message: A descriptive status message
        """
        self.status.update(status, progress_percentage, message)

    def set_completed(self, output_file_path: str, output_file_name: str, 
                     conversion_summary: Dict[str, Any], message: Optional[str] = None) -> None:
        """
        Sets the job status to completed with the provided output information.
        
        Args:
            output_file_path: Path to the generated Excel file
            output_file_name: Name of the generated Excel file
            conversion_summary: Summary of conversion results
            message: Optional completion message
        """
        self.output_file_path = output_file_path
        self.output_file_name = output_file_name
        self.conversion_summary = conversion_summary
        self.completed_at = datetime.now()
        self.status.set_completed(message)

    def set_failed(self, error: ErrorResponse, message: Optional[str] = None) -> None:
        """
        Sets the job status to failed with the provided error information.
        
        Args:
            error: Error response detailing what went wrong
            message: Optional error message
        """
        self.completed_at = datetime.now()
        self.status.set_error(error, message)

    def is_complete(self) -> bool:
        """
        Checks if the job has reached a terminal state (completed or failed).
        
        Returns:
            True if the job is in a terminal state, False otherwise
        """
        return self.status.is_complete()

    def get_input_details(self) -> Dict[str, Any]:
        """
        Gets detailed information about the input file.
        
        Returns:
            Dictionary with input file details
        """
        return self.input_file.get_file_details()

    def get_options_dict(self) -> Dict[str, Any]:
        """
        Gets the conversion options as a dictionary.
        
        Returns:
            Dictionary with conversion options
        """
        return self.options.to_dict()

    def get_status_dict(self) -> Dict[str, Any]:
        """
        Gets the current job status as a dictionary.
        
        Returns:
            Dictionary with job status information
        """
        return self.status.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ConversionJob to a dictionary representation.
        
        Returns:
            Dictionary representation of the job
        """
        result = {
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "input_file": self.get_input_details(),
            "options": self.get_options_dict(),
            "status": self.get_status_dict()
        }
        
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        
        if self.output_file_path:
            result["output_file_path"] = self.output_file_path
            
        if self.output_file_name:
            result["output_file_name"] = self.output_file_name
            
        if self.conversion_summary:
            result["conversion_summary"] = self.conversion_summary
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversionJob':
        """
        Creates a ConversionJob from a dictionary representation.
        
        Args:
            data: Dictionary containing job data
            
        Returns:
            A new ConversionJob instance
        """
        job_id = data.get("job_id")
        
        # Create UploadFile from dict
        input_file_data = data.get("input_file", {})
        input_file = UploadFile.from_dict(input_file_data)
        
        # Create ConversionOptions from dict
        options_data = data.get("options", {})
        options = ConversionOptions.from_dict(options_data)
        
        # Create the job
        job = cls(job_id=job_id, input_file=input_file, options=options)
        
        # Create JobStatus from dict
        status_data = data.get("status", {})
        job.status = JobStatus.from_dict(status_data)
        
        # Set timestamps
        if "created_at" in data and data["created_at"]:
            try:
                job.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                # Keep default value if parsing fails
                pass
            
        if "completed_at" in data and data["completed_at"]:
            try:
                job.completed_at = datetime.fromisoformat(data["completed_at"])
            except (ValueError, TypeError):
                # Keep as None if parsing fails
                pass
        
        # Set output information
        if "output_file_path" in data:
            job.output_file_path = data["output_file_path"]
            
        if "output_file_name" in data:
            job.output_file_name = data["output_file_name"]
            
        if "conversion_summary" in data:
            job.conversion_summary = data["conversion_summary"]
        
        return job

    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Gets the result of the conversion job if completed.
        
        Returns:
            Dictionary with job result information or None if not complete
        """
        if not self.is_complete():
            return None
            
        result = {
            "job_id": self.job_id,
            "status": self.status.status.value,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
        
        if self.output_file_path:
            result["output_file_path"] = self.output_file_path
            
        if self.output_file_name:
            result["output_file_name"] = self.output_file_name
            
        if self.conversion_summary:
            result["conversion_summary"] = self.conversion_summary
            
        return result

    def get_duration(self) -> Optional[float]:
        """
        Calculates the duration of the job in seconds.
        
        Returns:
            Duration in seconds or None if job is not complete
        """
        if not self.completed_at:
            return None
            
        delta = self.completed_at - self.created_at
        return delta.total_seconds()