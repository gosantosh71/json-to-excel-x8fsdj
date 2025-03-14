/**
 * status-polling.js
 * 
 * JavaScript module that handles polling for job status updates from the server
 * for the JSON to Excel Conversion Tool web interface. It provides functionality
 * to periodically check the status of conversion jobs and update the UI accordingly.
 * 
 * Dependencies:
 * - progress-tracking.js: For updating UI elements with status information
 * - Fetch API (Web API v2018+): For making HTTP requests to the status API endpoint
 */

import { updateProgressBar, updateStatusMessage, updateStatusIndicator } from './progress-tracking.js';

// Default polling interval in milliseconds
const DEFAULT_POLLING_INTERVAL = 2000;

// Maximum number of consecutive failed requests before giving up
const MAX_RETRY_COUNT = 5;

// Statuses that indicate the job has finished (either successfully or with an error)
const TERMINAL_STATUSES = ['COMPLETED', 'FAILED'];

/**
 * StatusPoller class that manages polling for job status updates
 */
class StatusPoller {
    /**
     * Initializes a new StatusPoller instance
     * @param {string} jobId - The ID of the conversion job to poll
     * @param {object} options - Configuration options for the poller
     */
    constructor(jobId, options = {}) {
        // Store the jobId for the conversion job
        this.jobId = jobId;
        
        // Merge default options with provided options
        this.options = Object.assign({
            pollingInterval: DEFAULT_POLLING_INTERVAL,
            statusContainerId: 'status-container',
            autoStart: true,
            onStatusChange: null,
            onComplete: null,
            onError: null
        }, options);
        
        // Set pollingInterval from options or default to DEFAULT_POLLING_INTERVAL
        this.pollingInterval = this.options.pollingInterval;
        
        // Set statusContainerId from options or default to 'status-container'
        this.statusContainerId = this.options.statusContainerId;
        
        // Set up callback functions from options (onStatusChange, onComplete, onError)
        this.onStatusChange = typeof this.options.onStatusChange === 'function' 
            ? this.options.onStatusChange : null;
        this.onComplete = typeof this.options.onComplete === 'function' 
            ? this.options.onComplete : null;
        this.onError = typeof this.options.onError === 'function' 
            ? this.options.onError : null;
        
        // Initialize isPolling to false
        this.isPolling = false;
        
        // Initialize retryCount to 0
        this.retryCount = 0;
        
        // Initialize pollTimer to null
        this.pollTimer = null;
        
        // Start polling immediately if autoStart option is true (default)
        if (this.options.autoStart) {
            this.startPolling();
        }
    }
    
    /**
     * Starts polling for job status updates
     * @returns {void} No return value
     */
    startPolling() {
        // If already polling, return immediately
        if (this.isPolling) {
            return;
        }
        
        // Set isPolling to true
        this.isPolling = true;
        
        // Call pollStatus immediately for initial status
        this.pollStatus();
        
        // Set up the poll timer to call pollStatus at regular intervals
        this.pollTimer = setInterval(() => {
            this.pollStatus();
        }, this.pollingInterval);
        
        // Log that polling has started
        console.log(`Started status polling for job ${this.jobId}`);
    }
    
    /**
     * Stops polling for job status updates
     * @returns {void} No return value
     */
    stopPolling() {
        // If not polling, return immediately
        if (!this.isPolling) {
            return;
        }
        
        // Set isPolling to false
        this.isPolling = false;
        
        // Clear the poll timer
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
        
        // Log that polling has stopped
        console.log(`Stopped status polling for job ${this.jobId}`);
    }
    
    /**
     * Polls the server for the current job status
     * @returns {void} No return value
     */
    pollStatus() {
        // If not polling, return immediately
        if (!this.isPolling) {
            return;
        }
        
        // Make a fetch request to the job status API endpoint
        fetch(formatStatusUrl(this.jobId))
            .then(response => handleStatusResponse(response))
            .then(statusData => {
                // Call handleStatusUpdate with the status data
                this.handleStatusUpdate(statusData);
                
                // Reset retry count on successful request
                this.retryCount = 0;
            })
            .catch(error => {
                // Handle errors by incrementing retry count and logging
                this.handleError(error);
            });
    }
    
    /**
     * Handles a status update from the server
     * @param {object} statusData - The status data from the server
     * @returns {void} No return value
     */
    handleStatusUpdate(statusData) {
        // Extract status, progress_percentage, and message from statusData
        const status = statusData.status;
        const progress = statusData.progress_percentage !== undefined 
            ? Math.round(statusData.progress_percentage) 
            : 0;
        const message = statusData.message || '';
        const stage = statusData.current_stage || '';
        
        // Update UI elements using progress-tracking functions
        this.updateUI(status, progress, message, stage);
        
        // Call onStatusChange callback if provided
        if (this.onStatusChange) {
            this.onStatusChange(status, statusData);
        }
        
        // If status is terminal (COMPLETED or FAILED):
        if (isTerminalStatus(status)) {
            // Stop polling
            this.stopPolling();
            
            // Call appropriate callback (onComplete or onError)
            if (status === 'COMPLETED' && this.onComplete) {
                this.onComplete(statusData);
            } else if (status === 'FAILED' && this.onError) {
                this.onError(new Error(message || 'Conversion failed'), statusData);
            }
        }
    }
    
    /**
     * Handles errors during status polling
     * @param {Error} error - The error object
     * @returns {void} No return value
     */
    handleError(error) {
        // Log the error to console
        console.error('Error polling for status:', error);
        
        // Increment retry count
        this.retryCount++;
        
        // If retry count exceeds MAX_RETRY_COUNT:
        if (this.retryCount >= MAX_RETRY_COUNT) {
            console.error(`Maximum retry count reached (${this.retryCount}). Stopping status polling.`);
            
            // Stop polling
            this.stopPolling();
            
            // Call onError callback with the error
            if (this.onError) {
                this.onError(error);
            }
            
            // Display error message in the status container
            const statusContainer = document.getElementById(this.statusContainerId);
            if (statusContainer) {
                updateStatusIndicator('FAILED', this.statusContainerId);
                updateStatusMessage('FAILED', 'Error communicating with server', this.statusContainerId);
            }
        }
    }
    
    /**
     * Updates the UI with current status information
     * @param {string} status - Current status
     * @param {number} progress - Current progress percentage
     * @param {string} message - Status message
     * @param {string} stage - Current processing stage
     * @returns {void} No return value
     */
    updateUI(status, progress, message, stage) {
        // Find the status container element
        const statusContainer = document.getElementById(this.statusContainerId);
        if (!statusContainer) {
            console.warn(`Status container with ID '${this.statusContainerId}' not found`);
            return;
        }
        
        // Update the status indicator using updateStatusIndicator
        updateStatusIndicator(status, this.statusContainerId);
        
        // Update the progress bar using updateProgressBar
        updateProgressBar(progress, this.statusContainerId);
        
        // Update the status message using updateStatusMessage
        updateStatusMessage(status, stage, this.statusContainerId);
    }
}

/**
 * Initializes status polling for a specific job
 * @param {string} jobId - The ID of the job to poll
 * @param {object} options - Configuration options
 * @returns {StatusPoller} Instance of the status poller
 */
function initStatusPolling(jobId, options = {}) {
    // Create a new StatusPoller instance with the provided jobId and options
    const poller = new StatusPoller(jobId, options);
    
    // Return the poller instance
    return poller;
}

/**
 * Formats the status API URL for a specific job
 * @param {string} jobId - The ID of the job
 * @returns {string} Formatted API URL
 */
function formatStatusUrl(jobId) {
    // Return the formatted URL string for the job status API endpoint
    return `/api/status/${jobId}`;
}

/**
 * Processes the response from a status API request
 * @param {object} response - The fetch response object
 * @returns {Promise<object>} Promise resolving to the status data
 */
function handleStatusResponse(response) {
    // Check if the response is ok (status 200-299)
    if (!response.ok) {
        // If not ok, throw an error with the status text
        throw new Error(`Status request failed: ${response.statusText}`);
    }
    
    // Parse the JSON response
    return response.json();
}

/**
 * Checks if a status represents a terminal state
 * @param {string} status - The status to check
 * @returns {boolean} True if the status is terminal
 */
function isTerminalStatus(status) {
    // Check if the status is included in the TERMINAL_STATUSES array
    return TERMINAL_STATUSES.includes(status);
}

// Export public API
export {
    initStatusPolling,
    StatusPoller
};