# JSON to Excel Conversion Tool API Documentation

## Introduction

This document provides comprehensive documentation for the JSON to Excel Conversion Tool API. The API allows developers to programmatically upload JSON files, convert them to Excel format, and download the resulting Excel files.

### Base URL

All API endpoints are relative to the base URL of your JSON to Excel Conversion Tool installation. For local development, this is typically: `http://localhost:5000/api/`

### Authentication

The API currently does not require authentication for local usage. For production deployments, standard security measures should be implemented.

### Response Format

All API responses are returned in JSON format with a consistent structure. Success responses include a `success: true` field, while error responses include `success: false` and error details.

## Core API Endpoints

The following endpoints provide basic information about the API.

### Health Check

**Endpoint:** `GET /api/health`

**Description:** Checks if the API is operational

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "API is operational",
  "status": "healthy",
  "timestamp": "2023-07-01T12:00:00Z"
}
```

### API Version

**Endpoint:** `GET /api/version`

**Description:** Returns the current API version information

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "API version information",
  "version": "1.0.0",
  "release_date": "2023-07-01"
}
```

### API Documentation

**Endpoint:** `GET /api/docs`

**Description:** Returns information about available API endpoints

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "API documentation",
  "endpoints": [
    {
      "path": "/api/health",
      "methods": ["GET"],
      "description": "Health check endpoint"
    }
    // Additional endpoints...
  ]
}
```

## File Upload API

These endpoints handle JSON file uploads and management.

### Upload JSON File

**Endpoint:** `POST /api/uploads`

**Description:** Uploads a JSON file for conversion

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | file | Yes | The JSON file to upload (multipart/form-data) |

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file": {
    "id": "f12345",
    "filename": "data.json",
    "size": 1024,
    "upload_date": "2023-07-01T12:00:00Z",
    "status": "ready"
  }
}
```

### Get Upload Details

**Endpoint:** `GET /api/uploads/{file_id}`

**Description:** Retrieves information about an uploaded file

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | path | Yes | The ID of the uploaded file |

**Response:**
```json
{
  "success": true,
  "message": "File details retrieved",
  "file": {
    "id": "f12345",
    "filename": "data.json",
    "size": 1024,
    "upload_date": "2023-07-01T12:00:00Z",
    "status": "ready",
    "content_type": "application/json"
  }
}
```

### Delete Upload

**Endpoint:** `DELETE /api/uploads/{file_id}`

**Description:** Deletes an uploaded file

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | path | Yes | The ID of the uploaded file |

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "file_id": "f12345"
}
```

### List Uploads

**Endpoint:** `GET /api/uploads`

**Description:** Lists all uploaded files

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | query | No | Filter by upload status (ready, processing, error) |

**Response:**
```json
{
  "success": true,
  "message": "2 files found",
  "files": [
    {
      "id": "f12345",
      "filename": "data1.json",
      "size": 1024,
      "upload_date": "2023-07-01T12:00:00Z",
      "status": "ready"
    },
    {
      "id": "f67890",
      "filename": "data2.json",
      "size": 2048,
      "upload_date": "2023-07-01T12:30:00Z",
      "status": "ready"
    }
  ]
}
```

### Validate Upload

**Endpoint:** `POST /api/uploads/{file_id}/validate`

**Description:** Validates an uploaded JSON file

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | path | Yes | The ID of the uploaded file |

**Response:**
```json
{
  "success": true,
  "message": "File validation complete",
  "is_valid": true,
  "details": {
    "structure": "valid",
    "size": "acceptable",
    "complexity": {
      "nesting_level": 3,
      "contains_arrays": true
    }
  }
}
```

## Conversion API

These endpoints handle the conversion of JSON files to Excel format.

### Create Conversion Job

**Endpoint:** `POST /api/conversion/jobs`

**Description:** Creates a new conversion job for an uploaded JSON file

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | form | Yes | The ID of the uploaded JSON file |
| sheet_name | form | No | Custom name for the Excel worksheet (default: Sheet1) |
| array_handling | form | No | How to handle arrays in JSON (expand or join, default: expand) |

**Response:**
```json
{
  "success": true,
  "message": "Conversion job created",
  "job": {
    "id": "j12345",
    "file_id": "f12345",
    "status": "pending",
    "created_at": "2023-07-01T12:05:00Z",
    "options": {
      "sheet_name": "Data",
      "array_handling": "expand"
    }
  }
}
```

### Get Job Status

**Endpoint:** `GET /api/conversion/jobs/{job_id}/status`

**Description:** Gets the current status of a conversion job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the conversion job |

**Response:**
```json
{
  "success": true,
  "message": "Job status retrieved",
  "status": {
    "job_id": "j12345",
    "status": "processing",
    "progress": 45,
    "current_step": "Flattening nested structures",
    "started_at": "2023-07-01T12:05:10Z",
    "estimated_completion": "2023-07-01T12:06:00Z"
  }
}
```

### Get Job Result

**Endpoint:** `GET /api/conversion/jobs/{job_id}/result`

**Description:** Gets the result of a completed conversion job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the conversion job |

**Response:**
```json
{
  "success": true,
  "message": "Excel file is ready for download",
  "download_url": "/api/conversion/jobs/j12345/download",
  "file_info": {
    "filename": "data.xlsx",
    "size": 5120,
    "created_at": "2023-07-01T12:06:00Z",
    "rows": 150,
    "columns": 12
  }
}
```

### Download Excel File

**Endpoint:** `GET /api/conversion/jobs/{job_id}/download`

**Description:** Downloads the Excel file generated by a conversion job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the conversion job |

**Response:** Binary Excel file with appropriate Content-Type and Content-Disposition headers

### Cancel Job

**Endpoint:** `POST /api/conversion/jobs/{job_id}/cancel`

**Description:** Cancels a pending or in-progress conversion job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the conversion job |

**Response:**
```json
{
  "success": true,
  "message": "Job cancelled successfully",
  "job_id": "j12345"
}
```

### Validate JSON

**Endpoint:** `POST /api/conversion/validate`

**Description:** Validates a JSON file without performing the full conversion

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | form | Yes | The ID of the uploaded JSON file |

**Response:**
```json
{
  "success": true,
  "message": "JSON validation complete",
  "is_valid": true,
  "details": {
    "structure": "valid",
    "complexity": {
      "nesting_level": 3,
      "contains_arrays": true,
      "estimated_rows": 150,
      "estimated_columns": 12
    },
    "conversion_feasibility": "suitable"
  }
}
```

## Job Management API

These endpoints provide job management capabilities.

### List Jobs

**Endpoint:** `GET /api/jobs`

**Description:** Lists all conversion jobs

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | query | No | Filter by job status (pending, processing, completed, failed) |

**Response:**
```json
{
  "success": true,
  "message": "2 jobs found",
  "jobs": [
    {
      "id": "j12345",
      "file_id": "f12345",
      "status": "completed",
      "created_at": "2023-07-01T12:05:00Z",
      "completed_at": "2023-07-01T12:06:00Z"
    },
    {
      "id": "j67890",
      "file_id": "f67890",
      "status": "processing",
      "created_at": "2023-07-01T12:35:00Z",
      "progress": 30
    }
  ]
}
```

### Get Job Details

**Endpoint:** `GET /api/jobs/{job_id}`

**Description:** Gets detailed information about a specific job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the job |

**Response:**
```json
{
  "success": true,
  "message": "Job details retrieved",
  "job": {
    "id": "j12345",
    "file_id": "f12345",
    "status": "completed",
    "created_at": "2023-07-01T12:05:00Z",
    "started_at": "2023-07-01T12:05:10Z",
    "completed_at": "2023-07-01T12:06:00Z",
    "duration_seconds": 50,
    "options": {
      "sheet_name": "Data",
      "array_handling": "expand"
    },
    "result": {
      "output_file": "data.xlsx",
      "size": 5120,
      "rows": 150,
      "columns": 12
    }
  }
}
```

### Get Queue Status

**Endpoint:** `GET /api/jobs/queue/status`

**Description:** Gets the current status of the job queue

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Queue status retrieved",
  "queue": {
    "total_jobs": 5,
    "pending": 2,
    "processing": 1,
    "completed": 1,
    "failed": 1,
    "estimated_wait_time": 120
  }
}
```

## Status API

These endpoints provide status information for jobs and the system.

### Get Job Status

**Endpoint:** `GET /api/status/job/{job_id}`

**Description:** Gets the current status of a specific job

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| job_id | path | Yes | The ID of the job |

**Response:**
```json
{
  "success": true,
  "message": "Job status retrieved",
  "status": {
    "job_id": "j12345",
    "status": "processing",
    "progress": 45,
    "current_step": "Flattening nested structures",
    "started_at": "2023-07-01T12:05:10Z",
    "estimated_completion": "2023-07-01T12:06:00Z"
  }
}
```

### Get Queue Status

**Endpoint:** `GET /api/status/queue`

**Description:** Gets the current status of the job queue

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Queue status retrieved",
  "queue": {
    "total_jobs": 5,
    "pending": 2,
    "processing": 1,
    "completed": 1,
    "failed": 1,
    "estimated_wait_time": 120
  }
}
```

### List Jobs

**Endpoint:** `GET /api/status/jobs`

**Description:** Lists all jobs with status information

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | query | No | Filter by job status (pending, processing, completed, failed) |

**Response:**
```json
{
  "success": true,
  "message": "2 jobs found",
  "jobs": [
    {
      "id": "j12345",
      "status": "completed",
      "created_at": "2023-07-01T12:05:00Z",
      "completed_at": "2023-07-01T12:06:00Z"
    },
    {
      "id": "j67890",
      "status": "processing",
      "created_at": "2023-07-01T12:35:00Z",
      "progress": 30
    }
  ]
}
```

## Error Handling

All API endpoints follow a consistent error handling pattern. Error responses include a `success: false` field and detailed error information.

### Error Response Format

Example error response:

```json
{
  "success": false,
  "error": {
    "code": "file_not_found",
    "message": "The requested file was not found",
    "details": "File with ID f12345 does not exist",
    "status_code": 404
  }
}
```

### Common Error Codes

The API uses the following common error codes:

| Code | Status Code | Description |
|------|-------------|-------------|
| invalid_request | 400 | The request was invalid or malformed |
| file_not_found | 404 | The requested file was not found |
| job_not_found | 404 | The requested job was not found |
| invalid_json | 400 | The JSON file is invalid or malformed |
| file_too_large | 413 | The file exceeds the maximum allowed size |
| conversion_error | 500 | An error occurred during conversion |
| server_error | 500 | An internal server error occurred |

## Usage Examples

The following examples demonstrate how to use the API with curl and JavaScript.

### Upload and Convert (curl)

Example of uploading a JSON file and converting it to Excel using curl:

```bash
# Upload JSON file
curl -X POST -F "file=@data.json" http://localhost:5000/api/uploads

# Create conversion job (assuming file_id f12345 was returned)
curl -X POST -F "file_id=f12345" -F "sheet_name=Data" http://localhost:5000/api/conversion/jobs

# Check job status (assuming job_id j12345 was returned)
curl http://localhost:5000/api/conversion/jobs/j12345/status

# Download result when complete
curl -o result.xlsx http://localhost:5000/api/conversion/jobs/j12345/download
```

### Upload and Convert (JavaScript)

Example of uploading a JSON file and converting it to Excel using JavaScript fetch API:

```javascript
// Upload JSON file
async function uploadAndConvert() {
  const fileInput = document.getElementById('fileInput');
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  
  // Upload file
  const uploadResponse = await fetch('http://localhost:5000/api/uploads', {
    method: 'POST',
    body: formData
  });
  const uploadResult = await uploadResponse.json();
  
  if (!uploadResult.success) {
    console.error('Upload failed:', uploadResult.error);
    return;
  }
  
  const fileId = uploadResult.file.id;
  
  // Create conversion job
  const jobFormData = new FormData();
  jobFormData.append('file_id', fileId);
  jobFormData.append('sheet_name', 'Data');
  
  const jobResponse = await fetch('http://localhost:5000/api/conversion/jobs', {
    method: 'POST',
    body: jobFormData
  });
  const jobResult = await jobResponse.json();
  
  if (!jobResult.success) {
    console.error('Job creation failed:', jobResult.error);
    return;
  }
  
  const jobId = jobResult.job.id;
  
  // Poll for job completion
  const checkStatus = async () => {
    const statusResponse = await fetch(`http://localhost:5000/api/conversion/jobs/${jobId}/status`);
    const statusResult = await statusResponse.json();
    
    if (statusResult.status.status === 'completed') {
      // Get download URL
      const resultResponse = await fetch(`http://localhost:5000/api/conversion/jobs/${jobId}/result`);
      const resultData = await resultResponse.json();
      
      // Trigger download
      window.location.href = resultData.download_url;
    } else if (statusResult.status.status === 'failed') {
      console.error('Conversion failed');
    } else {
      // Still processing, check again in 1 second
      setTimeout(checkStatus, 1000);
    }
  };
  
  checkStatus();
}
```

## Rate Limiting

To ensure fair usage of the API, rate limiting may be applied. The current limits are:

| Endpoint | Limit |
|----------|-------|
| All endpoints | 60 requests per minute per IP address |
| File upload | 10 uploads per minute per IP address |
| Conversion jobs | 5 conversion jobs per minute per IP address |

## Versioning

The API follows semantic versioning. The current version is v1.0.0. The version is included in the response of the /api/version endpoint.

Breaking changes will only be introduced in major version updates. The API version can be specified in the Accept header: `Accept: application/json; version=1.0`