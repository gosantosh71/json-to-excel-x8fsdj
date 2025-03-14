"""
Job status models for the JSON to Excel Conversion Tool web interface.

This module defines models for tracking and managing the status of JSON to Excel
conversion jobs in the web interface, including status enum values, progress tracking,
and error handling.
"""

from dataclasses import dataclass  # v: built-in
from enum import Enum  # v: built-in
from datetime import datetime  # v: built-in
from typing import Dict, Optional, Any  # v: built-in
import uuid  # v: built-in

from ...backend.models.error_response import ErrorResponse


class JobStatusEnum(Enum):
    """Enumeration of possible status values for conversion jobs in the web interface."""
    PENDING = "pending"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def is_terminal(self) -> bool:
        """
        Checks if the status represents a terminal state (completed or failed).
        
        Returns:
            bool: True if the status is terminal, False otherwise
        """
        return self in (JobStatusEnum.COMPLETED, JobStatusEnum.FAILED)


@dataclass
class JobStatus:
    """
    A data class that represents the current status of a conversion job,
    including progress percentage and status message.
    """
    job_id: str
    status: JobStatusEnum
    progress_percentage: int = 0
    message: str = ""
    last_updated: datetime = None
    error: Optional[ErrorResponse] = None
    
    def __post_init__(self):
        """Initialize default values after main initialization."""
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def update(self, status: JobStatusEnum, progress_percentage: int, message: str) -> None:
        """
        Updates the job status with new information.
        
        Args:
            status: The new status for the job
            progress_percentage: The updated progress percentage (0-100)
            message: A descriptive status message
        """
        self.status = status
        self.progress_percentage = progress_percentage
        self.message = message
        self.last_updated = datetime.now()
    
    def set_error(self, error: ErrorResponse, message: Optional[str] = None) -> None:
        """
        Sets the job status to FAILED with the provided error information.
        
        Args:
            error: The error response object containing error details
            message: Optional custom error message (defaults to error user message)
        """
        self.status = JobStatusEnum.FAILED
        self.error = error
        self.message = message or error.get_user_message()
        self.last_updated = datetime.now()
    
    def set_completed(self, message: Optional[str] = None) -> None:
        """
        Sets the job status to COMPLETED with 100% progress.
        
        Args:
            message: Optional completion message
        """
        self.status = JobStatusEnum.COMPLETED
        self.progress_percentage = 100
        self.message = message or "Conversion completed successfully"
        self.last_updated = datetime.now()
    
    def is_complete(self) -> bool:
        """
        Checks if the job has reached a terminal state (completed or failed).
        
        Returns:
            bool: True if the job is in a terminal state, False otherwise
        """
        return self.status.is_terminal()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the job status to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the job status
        """
        result = {
            'job_id': self.job_id,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'message': self.message,
            'last_updated': self.last_updated.isoformat(),
        }
        if self.error:
            result['error'] = self.error.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobStatus':
        """
        Creates a JobStatus object from a dictionary representation.
        
        Args:
            data: Dictionary containing job status data
            
        Returns:
            JobStatus: A new JobStatus instance
        """
        job_id = data.get('job_id')
        status = JobStatusEnum(data.get('status'))
        progress_percentage = data.get('progress_percentage', 0)
        message = data.get('message', '')
        
        # Convert ISO format string to datetime
        last_updated = None
        if 'last_updated' in data:
            last_updated = datetime.fromisoformat(data['last_updated'])
        
        # Create JobStatus instance
        job_status = cls(
            job_id=job_id,
            status=status,
            progress_percentage=progress_percentage,
            message=message,
            last_updated=last_updated
        )
        
        # Add error if present
        if 'error' in data and data['error']:
            job_status.error = ErrorResponse.from_dict(data['error'])
            
        return job_status