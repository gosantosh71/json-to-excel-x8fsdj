/**
 * conversion.js
 * 
 * JavaScript module that handles the client-side conversion process for the JSON to Excel
 * Conversion Tool web interface. This module manages the form submission, API communication,
 * and user interface updates during the conversion process, providing real-time feedback
 * and error handling.
 * 
 * Dependencies:
 * - DOM Web API (standard): Access to the HTML document and DOM elements
 * - Fetch API (standard): Make AJAX requests to the server for conversion operations
 * - jQuery (v3.6.0+): DOM manipulation and AJAX functionality
 */

// Import from other modules
import { initProgressTracking } from './progress-tracking.js';

// Define API endpoints for conversion operations
const API_ENDPOINTS = {
    CREATE_JOB: '/api/conversion/jobs',
    JOB_STATUS: '/api/conversion/jobs/{job_id}/status',
    JOB_RESULT: '/api/conversion/jobs/{job_id}/result',
    CANCEL_JOB: '/api/conversion/jobs/{job_id}/cancel'
};

/**
 * Class that manages the conversion process and UI updates
 */
class ConversionManager {
    /**
     * Initializes a new ConversionManager instance
     */
    constructor() {
        this.currentJobId = null;
        this.progressTracker = null;
        this.isProcessing = false;
        this.elements = {};
    }
    
    /**
     * Initializes the conversion manager
     */
    init() {
        // Find and store references to UI elements
        this.elements = {
            processingContainer: document.getElementById('processing-container'),
            resultContainer: document.getElementById('result-container'),
            errorContainer: document.getElementById('error-container'),
            progressBar: document.getElementById('progress-bar'),
            statusMessage: document.getElementById('status-message'),
            cancelButton: document.getElementById('cancel-conversion')
        };
        
        // Set up event listeners
        if (this.elements.cancelButton) {
            this.elements.cancelButton.addEventListener('click', this.handleCancelConversion.bind(this));
        }
        
        // Check if there's an existing job ID on the page
        const jobIdElement = document.getElementById('job-id');
        if (jobIdElement && jobIdElement.value) {
            this.currentJobId = jobIdElement.value;
            // Initialize progress tracking
            this.trackProgress(this.currentJobId);
        }
        
        // Store reference to this instance for global access
        window.conversionManager = this;
    }
    
    /**
     * Starts a new conversion job
     * @param {FormData} formData - The form data for the conversion job
     * @returns {Promise} Promise that resolves when conversion starts
     */
    startConversion(formData) {
        // Set processing state
        this.isProcessing = true;
        
        // Update UI
        if (this.elements.processingContainer) {
            this.elements.processingContainer.style.display = 'block';
        }
        if (this.elements.resultContainer) {
            this.elements.resultContainer.style.display = 'none';
        }
        if (this.elements.errorContainer) {
            this.elements.errorContainer.style.display = 'none';
        }
        
        // Create conversion job
        return createConversionJob(formData)
            .then(jobData => {
                // Store the job ID
                this.currentJobId = jobData.job_id;
                
                // Initialize progress tracking
                this.trackProgress(this.currentJobId);
                
                return jobData;
            })
            .catch(error => {
                this.handleError(error);
                throw error;
            });
    }
    
    /**
     * Tracks the progress of a conversion job
     * @param {string} jobId - The ID of the job to track
     */
    trackProgress(jobId) {
        // Store the job ID
        this.currentJobId = jobId;
        
        // Initialize progress tracker with callbacks
        this.progressTracker = initProgressTracking(jobId, {
            containerId: 'processing-container',
            onProgressUpdate: (progress) => {
                console.log(`Progress updated: ${progress}%`);
            },
            onStageChange: (stage) => {
                console.log(`Stage changed: ${stage}`);
            },
            onStatusChange: (status) => {
                console.log(`Status changed: ${status}`);
                if (status === 'COMPLETED') {
                    // Get the job result when completed
                    getJobResult(jobId)
                        .then(result => this.handleCompletion(result))
                        .catch(error => this.handleError(error));
                } else if (status === 'FAILED') {
                    this.handleError({ message: 'Conversion failed' });
                }
            }
        });
        
        // Start tracking
        this.progressTracker.startTracking();
    }
    
    /**
     * Cancels the current conversion job
     * @returns {Promise} Promise that resolves when cancellation completes
     */
    cancelConversion() {
        if (!this.currentJobId) {
            return Promise.reject(new Error('No active job to cancel'));
        }
        
        // Call the cancel job API
        return cancelJob(this.currentJobId)
            .then(result => {
                // Stop progress tracking
                if (this.progressTracker) {
                    this.progressTracker.stopTracking();
                }
                
                // Update UI
                if (this.elements.statusMessage) {
                    this.elements.statusMessage.textContent = 'Conversion cancelled';
                }
                
                this.isProcessing = false;
                return result;
            })
            .catch(error => {
                this.handleError(error);
                throw error;
            });
    }
    
    /**
     * Handles the successful completion of a conversion job
     * @param {object} result - The conversion result data
     */
    handleCompletion(result) {
        // Update state
        this.isProcessing = false;
        
        // Stop progress tracking
        if (this.progressTracker) {
            this.progressTracker.stopTracking();
        }
        
        // Show result in UI
        showConversionResult(result, this.currentJobId);
        
        console.log('Conversion completed:', result);
    }
    
    /**
     * Handles errors during the conversion process
     * @param {object} error - The error object
     */
    handleError(error) {
        // Update state
        this.isProcessing = false;
        
        // Stop progress tracking if active
        if (this.progressTracker) {
            this.progressTracker.stopTracking();
        }
        
        // Show error in UI
        showConversionError(
            error.message || 'An error occurred during conversion',
            error,
            this.elements.errorContainer
        );
        
        console.error('Conversion error:', error);
    }
    
    /**
     * Event handler for cancel button
     * @param {Event} event - The click event
     */
    handleCancelConversion(event) {
        event.preventDefault();
        
        if (confirm('Are you sure you want to cancel this conversion?')) {
            this.cancelConversion()
                .then(() => {
                    // Redirect to home page
                    window.location.href = '/?cancelled=true';
                })
                .catch(error => {
                    alert(`Failed to cancel: ${error.message}`);
                });
        }
    }
}

/**
 * Initializes conversion functionality for the web interface
 */
function initConversion() {
    // Get the conversion form element
    const conversionForm = document.getElementById('conversion-form');
    
    // If the form exists, add event listener for submission
    if (conversionForm) {
        conversionForm.addEventListener('submit', handleConversionSubmit);
    }
    
    // Set up cancel button event listener
    const cancelButton = document.getElementById('cancel-conversion');
    if (cancelButton) {
        cancelButton.addEventListener('click', handleCancelConversion);
    }
    
    // Set up conversion options UI elements
    initializeConversionOptions();
    
    // Set up event listeners for 'Convert Another' and 'Try Again' buttons
    const convertAnotherButton = document.getElementById('convert-another');
    if (convertAnotherButton) {
        convertAnotherButton.addEventListener('click', handleConvertAnother);
    }
    
    const tryAgainButton = document.getElementById('try-again');
    if (tryAgainButton) {
        tryAgainButton.addEventListener('click', handleTryAgain);
    }
    
    // Check if we're on a processing page with an existing job
    const jobIdElement = document.getElementById('job-id');
    if (jobIdElement && jobIdElement.value) {
        const jobId = jobIdElement.value;
        // Initialize a conversion manager for this job
        const manager = new ConversionManager();
        manager.init();
        manager.trackProgress(jobId);
    }
}

/**
 * Handles the submission of the conversion form
 * @param {Event} event - The form submission event
 */
function handleConversionSubmit(event) {
    // Prevent the default form submission
    event.preventDefault();
    
    // Get the form element
    const form = event.target;
    
    // Validate the form data
    const validation = validateConversionForm(form);
    if (!validation.isValid) {
        // Show validation error
        showConversionError(validation.message, null, document.getElementById('error-container'));
        return;
    }
    
    // Show loading state
    const processingContainer = document.getElementById('processing-container');
    if (processingContainer) {
        processingContainer.style.display = 'block';
    }
    const formContainer = document.getElementById('form-container');
    if (formContainer) {
        formContainer.style.display = 'none';
    }
    
    // Collect form data
    const formData = new FormData(form);
    
    // Create a new conversion manager
    const manager = new ConversionManager();
    manager.init();
    
    // Start the conversion
    manager.startConversion(formData)
        .then(jobData => {
            // Redirect to processing page or update UI
            if (jobData && jobData.job_id) {
                // If we have a separate processing page, redirect to it
                if (window.location.pathname !== '/processing') {
                    window.location.href = `/processing?job_id=${jobData.job_id}`;
                }
            }
        })
        .catch(error => {
            // Show error
            showConversionError(
                'Failed to start conversion', 
                error, 
                document.getElementById('error-container')
            );
        });
}

/**
 * Creates a new conversion job on the server
 * @param {FormData} formData - The form data for the conversion job
 * @returns {Promise} Promise that resolves with job data or rejects with error
 */
function createConversionJob(formData) {
    return fetch(API_ENDPOINTS.CREATE_JOB, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header when using FormData, 
        // the browser will set it correctly with the boundary parameter
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data || !data.job_id) {
            throw new Error('Invalid response: missing job ID');
        }
        return data;
    });
}

/**
 * Gets the current status of a conversion job
 * @param {string} jobId - The ID of the job to check
 * @returns {Promise} Promise that resolves with job status or rejects with error
 */
function getJobStatus(jobId) {
    const url = formatEndpointUrl(API_ENDPOINTS.JOB_STATUS, jobId);
    
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Gets the result of a completed conversion job
 * @param {string} jobId - The ID of the completed job
 * @returns {Promise} Promise that resolves with job result or rejects with error
 */
function getJobResult(jobId) {
    const url = formatEndpointUrl(API_ENDPOINTS.JOB_RESULT, jobId);
    
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Cancels a conversion job
 * @param {string} jobId - The ID of the job to cancel
 * @returns {Promise} Promise that resolves with cancellation result or rejects with error
 */
function cancelJob(jobId) {
    const url = formatEndpointUrl(API_ENDPOINTS.CANCEL_JOB, jobId);
    
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    });
}

/**
 * Handles the cancellation of a conversion job
 * @param {Event} event - The click event
 */
function handleCancelConversion(event) {
    // Prevent default button action
    event.preventDefault();
    
    // Get the job ID from data attribute or hidden input
    const button = event.target;
    const jobIdInput = document.getElementById('job-id');
    const jobId = button.dataset.jobId || (jobIdInput ? jobIdInput.value : null);
    
    if (!jobId) {
        console.error('Cannot cancel job: missing job ID');
        return;
    }
    
    // Show confirmation dialog
    if (confirm('Are you sure you want to cancel this conversion?')) {
        // Get the conversion manager or create a new one
        let manager;
        if (window.conversionManager instanceof ConversionManager) {
            manager = window.conversionManager;
        } else {
            manager = new ConversionManager();
            manager.init();
            manager.currentJobId = jobId;
        }
        
        // Cancel the conversion
        manager.cancelConversion()
            .then(result => {
                // Redirect to home page or show message
                window.location.href = '/?cancelled=true';
            })
            .catch(error => {
                // Show error
                alert(`Failed to cancel conversion: ${error.message}`);
            });
    }
}

/**
 * Handles the 'Convert Another File' button click
 * @param {Event} event - The click event
 */
function handleConvertAnother(event) {
    event.preventDefault();
    // Redirect to the home/upload page
    window.location.href = '/';
}

/**
 * Handles the 'Try Again' button click after an error
 * @param {Event} event - The click event
 */
function handleTryAgain(event) {
    event.preventDefault();
    // Redirect to the home/upload page
    window.location.href = '/';
}

/**
 * Validates the conversion form data
 * @param {HTMLFormElement} form - The form element to validate
 * @returns {object} Validation result with status and message
 */
function validateConversionForm(form) {
    // Check if form exists
    if (!form) {
        return { isValid: false, message: 'Form not found' };
    }
    
    // Get file ID input (set by upload handler)
    const fileIdInput = form.querySelector('input[name="file_id"]');
    
    // Check if a file has been selected
    if (!fileIdInput || !fileIdInput.value) {
        return { isValid: false, message: 'Please select a JSON file to convert' };
    }
    
    // Validate other form fields if present
    // For example, sheet name validation, etc.
    
    return { isValid: true };
}

/**
 * Displays an error message for conversion issues
 * @param {string} message - The error message
 * @param {object} details - Additional error details
 * @param {HTMLElement} container - The container for the error message
 */
function showConversionError(message, details, container) {
    // Hide processing container if it exists
    const processingContainer = document.getElementById('processing-container');
    if (processingContainer) {
        processingContainer.style.display = 'none';
    }
    
    // Show error container
    if (container) {
        container.style.display = 'block';
    }
    
    // Update error message
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        errorMessage.textContent = message || 'An error occurred during conversion';
    }
    
    // Update error details if provided
    const errorDetails = document.getElementById('error-details');
    if (errorDetails && details) {
        let detailsText = '';
        if (typeof details === 'string') {
            detailsText = details;
        } else if (details.message) {
            detailsText = details.message;
        } else if (typeof details === 'object') {
            detailsText = JSON.stringify(details, null, 2);
        }
        errorDetails.textContent = detailsText;
        errorDetails.style.display = 'block';
    }
    
    // Show troubleshooting tips based on error type
    const troubleshootingTips = document.getElementById('troubleshooting-tips');
    if (troubleshootingTips) {
        let tips = '';
        
        if (message && message.includes('file')) {
            tips = 'Try uploading the file again or check that the file is valid JSON.';
        } else if (message && message.includes('server')) {
            tips = 'The server might be experiencing high load. Please try again later.';
        } else if (message && message.includes('JSON')) {
            tips = 'Check that your JSON file has valid syntax and structure.';
        } else {
            tips = 'Try refreshing the page and starting again. If the problem persists, contact support.';
        }
        
        troubleshootingTips.textContent = tips;
        troubleshootingTips.style.display = 'block';
    }
}

/**
 * Displays the successful conversion result
 * @param {object} result - The conversion result data
 * @param {string} jobId - The ID of the completed job
 */
function showConversionResult(result, jobId) {
    // Hide processing container
    const processingContainer = document.getElementById('processing-container');
    if (processingContainer) {
        processingContainer.style.display = 'none';
    }
    
    // Show result container
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
        resultContainer.style.display = 'block';
    }
    
    // Update result summary with conversion details
    const resultSummary = document.getElementById('result-summary');
    if (resultSummary && result) {
        let summaryContent = '';
        
        // Build summary content from result data
        if (result.input_file) {
            summaryContent += `<div>Input: ${result.input_file}`;
            if (result.input_size) {
                summaryContent += ` (${formatFileSize(result.input_size)})`;
            }
            summaryContent += '</div>';
        }
        
        if (result.output_file) {
            summaryContent += `<div>Output: ${result.output_file}`;
            if (result.output_size) {
                summaryContent += ` (${formatFileSize(result.output_size)})`;
            }
            summaryContent += '</div>';
        }
        
        if (result.rows) {
            summaryContent += `<div>Rows: ${result.rows}</div>`;
        }
        
        if (result.columns) {
            summaryContent += `<div>Columns: ${result.columns}</div>`;
        }
        
        if (result.processing_time) {
            summaryContent += `<div>Processing Time: ${result.processing_time} seconds</div>`;
        }
        
        resultSummary.innerHTML = summaryContent;
    }
    
    // Set up the download button with the correct URL
    const downloadButton = document.getElementById('download-excel');
    if (downloadButton && jobId) {
        downloadButton.href = `/download/${jobId}`;
        downloadButton.style.display = 'inline-block';
    }
    
    // Enable the 'Convert Another File' button
    const convertAnotherButton = document.getElementById('convert-another');
    if (convertAnotherButton) {
        convertAnotherButton.disabled = false;
    }
}

/**
 * Updates the progress UI with current conversion status
 * @param {object} status - The current status information
 */
function updateProgressUI(status) {
    if (!status) return;
    
    // Update progress bar
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    if (progressBar && status.progress_percentage !== undefined) {
        const percentage = Math.round(status.progress_percentage);
        progressBar.style.width = `${percentage}%`;
        
        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }
        
        // Apply appropriate CSS classes
        if (percentage === 100) {
            progressBar.classList.add('complete');
            progressBar.classList.remove('in-progress');
        } else if (percentage > 0) {
            progressBar.classList.add('in-progress');
            progressBar.classList.remove('complete');
        }
    }
    
    // Update status message
    const statusMessage = document.getElementById('status-message');
    if (statusMessage && status.current_stage) {
        statusMessage.textContent = status.current_stage;
    }
    
    // Apply CSS classes based on status
    const processingContainer = document.getElementById('processing-container');
    if (processingContainer && status.status) {
        processingContainer.className = 'processing-container';
        processingContainer.classList.add(`status-${status.status.toLowerCase()}`);
    }
}

/**
 * Formats an API endpoint URL with the job ID
 * @param {string} endpoint - The endpoint template
 * @param {string} jobId - The job ID to insert
 * @returns {string} Formatted endpoint URL
 */
function formatEndpointUrl(endpoint, jobId) {
    return endpoint.replace('{job_id}', jobId);
}

/**
 * Format file size in bytes to a human-readable format
 * @param {number} bytes - The file size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Initializes conversion options UI elements
 */
function initializeConversionOptions() {
    // Set up any interactive UI elements for conversion options
    const arrayHandlingRadios = document.querySelectorAll('input[name="array_handling"]');
    arrayHandlingRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Update any dependent UI elements based on selection
            const expandDetails = document.getElementById('expand-details');
            const joinDetails = document.getElementById('join-details');
            
            if (this.value === 'expand' && expandDetails) {
                expandDetails.style.display = 'block';
                if (joinDetails) joinDetails.style.display = 'none';
            } else if (this.value === 'join' && joinDetails) {
                joinDetails.style.display = 'block';
                if (expandDetails) expandDetails.style.display = 'none';
            }
        });
    });
}

// Create a self-contained module for conversion functionality
const conversionModule = (function() {
    return {
        init: initConversion,
        ConversionManager: ConversionManager
    };
})();

// Export public API
export {
    initConversion,
    ConversionManager
};