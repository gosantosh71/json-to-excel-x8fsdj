"""
Unit tests for the StorageService class that manages file storage operations in the web interface of the JSON to Excel Conversion Tool. These tests verify the functionality of file uploads, retrievals, job management, and cleanup operations.
"""

import os
import datetime
import uuid
from unittest.mock import Mock
import pytest

from ../../services/storage_service import StorageService
from ../fixtures/file_fixtures import (
    setup_test_upload_folder,
    teardown_test_upload_folder,
    create_test_file_storage,
    create_test_json_file_storage,
    create_test_upload_file
)
from ../fixtures/job_fixtures import create_test_job, create_completed_job
from ../../models/upload_file import UploadFile
from ../../models/conversion_job import ConversionJob
from ../../models/job_status import JobStatusEnum
from ../../utils/path_utils import ensure_upload_directory, get_upload_path


@pytest.fixture
def storage_service(setup_test_upload_folder, teardown_test_upload_folder):
    """
    Pytest fixture that creates a StorageService instance for testing.
    
    Args:
        setup_test_upload_folder: Fixture that creates a test upload folder
        teardown_test_upload_folder: Fixture that cleans up the test upload folder
        
    Returns:
        A StorageService instance configured for testing
    """
    ensure_upload_directory()
    service = StorageService()
    yield service
    # Cleanup after tests are done
    service.stop_cleanup_thread()


def test_save_uploaded_file_success(storage_service, create_test_json_file_storage):
    """
    Tests that a file can be successfully uploaded and saved.
    """
    # Create a test file
    file = create_test_json_file_storage()
    
    # Call the method
    upload_file, error = storage_service.save_uploaded_file(file)
    
    # Assertions
    assert upload_file is not None
    assert error is None
    assert isinstance(upload_file, UploadFile)
    assert upload_file.file_id is not None and upload_file.file_id != ""
    assert os.path.exists(upload_file.file_path)


def test_get_upload_file_success(storage_service, create_test_json_file_storage):
    """
    Tests that an uploaded file can be retrieved by its ID.
    """
    # Save a file first
    file = create_test_json_file_storage()
    upload_file, _ = storage_service.save_uploaded_file(file)
    
    # Get the file ID
    file_id = upload_file.file_id
    
    # Call the method
    result, error = storage_service.get_upload_file(file_id)
    
    # Assertions
    assert result is not None
    assert error is None
    assert result.file_id == file_id


def test_get_upload_file_not_found(storage_service):
    """
    Tests that an error is returned when trying to get a non-existent file.
    """
    # Generate a random file ID
    file_id = str(uuid.uuid4())
    
    # Call the method
    result, error = storage_service.get_upload_file(file_id)
    
    # Assertions
    assert result is None
    assert error is not None
    assert "not found" in error.message.lower()


def test_delete_upload_file_success(storage_service, create_test_json_file_storage):
    """
    Tests that an uploaded file can be deleted.
    """
    # Save a file first
    file = create_test_json_file_storage()
    upload_file, _ = storage_service.save_uploaded_file(file)
    
    # Get the file ID and path
    file_id = upload_file.file_id
    file_path = upload_file.file_path
    
    # Verify file exists
    assert os.path.exists(file_path)
    
    # Call the method
    result, error = storage_service.delete_upload_file(file_id)
    
    # Assertions
    assert result is True
    assert error is None
    assert not os.path.exists(file_path)
    
    # Try to get the deleted file
    get_result, _ = storage_service.get_upload_file(file_id)
    assert get_result is None


def test_delete_upload_file_not_found(storage_service):
    """
    Tests that an error is returned when trying to delete a non-existent file.
    """
    # Generate a random file ID
    file_id = str(uuid.uuid4())
    
    # Call the method
    result, error = storage_service.delete_upload_file(file_id)
    
    # Assertions
    assert result is False
    assert error is not None
    assert "not found" in error.message.lower()


def test_save_conversion_job_success(storage_service, create_test_job):
    """
    Tests that a conversion job can be successfully saved.
    """
    # Create a test job
    job = create_test_job()
    
    # Call the method
    result, error = storage_service.save_conversion_job(job)
    
    # Assertions
    assert result is True
    assert error is None
    
    # Verify job was saved by retrieving it
    saved_job, error = storage_service.get_conversion_job(job.job_id)
    assert saved_job is not None
    assert error is None
    assert saved_job.job_id == job.job_id


def test_get_conversion_job_success(storage_service, create_test_job):
    """
    Tests that a conversion job can be retrieved by its ID.
    """
    # Create and save a test job
    job = create_test_job()
    storage_service.save_conversion_job(job)
    
    # Call the method
    result, error = storage_service.get_conversion_job(job.job_id)
    
    # Assertions
    assert result is not None
    assert error is None
    assert result.job_id == job.job_id


def test_get_conversion_job_not_found(storage_service):
    """
    Tests that an error is returned when trying to get a non-existent job.
    """
    # Generate a random job ID
    job_id = str(uuid.uuid4())
    
    # Call the method
    result, error = storage_service.get_conversion_job(job_id)
    
    # Assertions
    assert result is None
    assert error is not None
    assert "not found" in error.message.lower()


def test_update_conversion_job_success(storage_service, create_test_job):
    """
    Tests that a conversion job can be updated.
    """
    # Create and save a test job
    job = create_test_job()
    storage_service.save_conversion_job(job)
    
    # Update the job
    job.status.status = JobStatusEnum.COMPLETED
    
    # Call the method
    result, error = storage_service.update_conversion_job(job)
    
    # Assertions
    assert result is True
    assert error is None
    
    # Get the updated job and verify the status
    updated_job, _ = storage_service.get_conversion_job(job.job_id)
    assert updated_job.status.status == JobStatusEnum.COMPLETED


def test_update_conversion_job_not_found(storage_service, create_test_job):
    """
    Tests that an error is returned when trying to update a non-existent job.
    """
    # Create a job with a random ID that doesn't exist in storage
    job = create_test_job(job_id=str(uuid.uuid4()))
    
    # Call the method
    result, error = storage_service.update_conversion_job(job)
    
    # Assertions
    assert result is False
    assert error is not None
    assert "not found" in error.message.lower()


def test_delete_conversion_job_success(storage_service, create_test_job):
    """
    Tests that a conversion job can be deleted.
    """
    # Create and save a test job
    job = create_test_job()
    storage_service.save_conversion_job(job)
    
    # Call the method
    result, error = storage_service.delete_conversion_job(job.job_id)
    
    # Assertions
    assert result is True
    assert error is None
    
    # Try to get the deleted job
    deleted_job, error = storage_service.get_conversion_job(job.job_id)
    assert deleted_job is None
    assert error is not None


def test_delete_conversion_job_with_output_file(storage_service, create_completed_job):
    """
    Tests that a conversion job with an output file can be deleted and the output file is also deleted.
    """
    # Create a completed job with an output file
    job = create_completed_job()
    storage_service.save_conversion_job(job)
    
    # Create a mock output file at the job's output_file_path
    with open(job.output_file_path, 'w') as f:
        f.write("test output")
    
    # Assert that the output file exists
    assert os.path.exists(job.output_file_path)
    
    # Call the method
    result, error = storage_service.delete_conversion_job(job.job_id)
    
    # Assertions
    assert result is True
    assert error is None
    assert not os.path.exists(job.output_file_path)
    
    # Try to get the deleted job and assert it returns None with an error
    deleted_job, error = storage_service.get_conversion_job(job.job_id)
    assert deleted_job is None
    assert error is not None


def test_delete_conversion_job_not_found(storage_service):
    """
    Tests that an error is returned when trying to delete a non-existent job.
    """
    # Generate a random job ID that doesn't exist
    job_id = str(uuid.uuid4())
    
    # Call the method
    result, error = storage_service.delete_conversion_job(job_id)
    
    # Assertions
    assert result is False
    assert error is not None
    assert "not found" in error.message.lower()


def test_list_upload_files(storage_service, create_test_json_file_storage):
    """
    Tests that all uploaded files can be listed.
    """
    # Save multiple test files
    files = []
    for i in range(3):
        file = create_test_json_file_storage()
        upload_file, _ = storage_service.save_uploaded_file(file)
        files.append(upload_file)
    
    # Call the method
    result = storage_service.list_upload_files()
    
    # Assertions
    assert len(result) >= len(files)
    for file in files:
        assert any(f.file_id == file.file_id for f in result)
    for f in result:
        assert isinstance(f, UploadFile)


def test_list_conversion_jobs(storage_service, create_test_job):
    """
    Tests that all conversion jobs can be listed.
    """
    # Save multiple test jobs
    jobs = []
    for i in range(3):
        job = create_test_job()
        storage_service.save_conversion_job(job)
        jobs.append(job)
    
    # Call the method
    result = storage_service.list_conversion_jobs()
    
    # Assertions
    assert len(result) >= len(jobs)
    for job in jobs:
        assert any(j.job_id == job.job_id for j in result)
    for j in result:
        assert isinstance(j, ConversionJob)


def test_save_output_file_success(storage_service, create_test_job):
    """
    Tests that an output file can be saved for a conversion job.
    """
    # Create a test job
    job = create_test_job()
    storage_service.save_conversion_job(job)
    
    # Create a test output file
    output_path = os.path.join(os.path.dirname(job.input_file.file_path), "output.xlsx")
    with open(output_path, 'w') as f:
        f.write("test output")
    
    # Call the method
    result, error = storage_service.save_output_file(job.job_id, output_path, "output.xlsx")
    
    # Assertions
    assert result is True
    assert error is None
    
    # Get the updated job and verify it has the output file information
    updated_job, _ = storage_service.get_conversion_job(job.job_id)
    assert updated_job.output_file_path == output_path
    assert updated_job.output_file_name == "output.xlsx"


def test_save_output_file_job_not_found(storage_service):
    """
    Tests that an error is returned when trying to save an output file for a non-existent job.
    """
    # Generate a random job ID that doesn't exist
    job_id = str(uuid.uuid4())
    
    # Create a test output file path and name
    output_path = os.path.join(os.path.dirname(__file__), "output.xlsx")
    
    # Call the method
    result, error = storage_service.save_output_file(job_id, output_path, "output.xlsx")
    
    # Assertions
    assert result is False
    assert error is not None
    assert "not found" in error.message.lower()


def test_get_output_file_success(storage_service, create_completed_job):
    """
    Tests that an output file can be retrieved for a conversion job.
    """
    # Create a completed job with an output file
    job = create_completed_job()
    storage_service.save_conversion_job(job)
    
    # Create a mock output file at the job's output_file_path
    with open(job.output_file_path, 'w') as f:
        f.write("test output")
    
    # Call the method
    file_path, file_name, error = storage_service.get_output_file(job.job_id)
    
    # Assertions
    assert file_path == job.output_file_path
    assert file_name == job.output_file_name
    assert error is None


def test_get_output_file_job_not_found(storage_service):
    """
    Tests that an error is returned when trying to get an output file for a non-existent job.
    """
    # Generate a random job ID that doesn't exist
    job_id = str(uuid.uuid4())
    
    # Call the method
    file_path, file_name, error = storage_service.get_output_file(job_id)
    
    # Assertions
    assert file_path is None
    assert file_name is None
    assert error is not None
    assert "not found" in error.message.lower()


def test_get_output_file_no_output(storage_service, create_test_job):
    """
    Tests that an error is returned when trying to get an output file for a job that has no output file.
    """
    # Create a test job without an output file
    job = create_test_job()
    storage_service.save_conversion_job(job)
    
    # Call the method
    file_path, file_name, error = storage_service.get_output_file(job.job_id)
    
    # Assertions
    assert file_path is None
    assert file_name is None
    assert error is not None
    assert "no output file" in error.message.lower()


def test_cleanup_old_files(storage_service, create_test_json_file_storage):
    """
    Tests that old uploaded files can be cleaned up.
    """
    # Create and save multiple test files
    files = []
    for i in range(5):
        file = create_test_json_file_storage()
        upload_file, _ = storage_service.save_uploaded_file(file)
        files.append(upload_file)
    
    # Modify the file timestamps to make some files appear older
    old_files = files[:2]
    for file in old_files:
        # Set modification time to 2 hours ago
        old_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        os.utime(file.file_path, (old_time.timestamp(), old_time.timestamp()))
    
    # Call cleanup_old_files with a specific age threshold
    count, deleted_paths = storage_service.cleanup_old_files(60)  # 60 minutes = 1 hour
    
    # Assertions
    assert count == len(old_files)
    for file in old_files:
        assert file.file_path in deleted_paths
        assert not os.path.exists(file.file_path)
    
    # Assert that newer files still exist
    for file in files[2:]:
        assert os.path.exists(file.file_path)


def test_cleanup_old_jobs(storage_service, create_completed_job):
    """
    Tests that old conversion jobs can be cleaned up.
    """
    # Create and save multiple completed jobs
    jobs = []
    for i in range(5):
        job = create_completed_job()
        storage_service.save_conversion_job(job)
        jobs.append(job)
    
    # Modify the job timestamps to make some jobs appear older
    old_jobs = jobs[:2]
    for job in old_jobs:
        # Set completed_at to 2 hours ago
        job.completed_at = datetime.datetime.now() - datetime.timedelta(hours=2)
        storage_service.update_conversion_job(job)
    
    # Call cleanup_old_jobs
    count, deleted_ids = storage_service.cleanup_old_jobs()
    
    # Assertions
    assert count == len(old_jobs)
    for job in old_jobs:
        assert job.job_id in deleted_ids
        
        # Try to get the deleted job
        deleted_job, _ = storage_service.get_conversion_job(job.job_id)
        assert deleted_job is None
    
    # Assert that newer jobs still exist
    for job in jobs[2:]:
        existing_job, _ = storage_service.get_conversion_job(job.job_id)
        assert existing_job is not None