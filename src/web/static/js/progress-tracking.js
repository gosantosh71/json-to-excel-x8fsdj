/**
 * progress-tracking.js
 * 
 * JavaScript module for tracking and visualizing the progress of JSON to Excel conversion jobs
 * in the web interface. Provides real-time updates of progress bars, status messages, and
 * conversion stages as the server processes conversion jobs.
 * 
 * Dependencies:
 * - jQuery (v3.6.0+): For DOM manipulation and animation effects
 * - DOM Web API: For document and element access
 */

// Define constants for the module
const PROGRESS_UPDATE_INTERVAL = 1000; // Check progress every 1 second

// Map of conversion stages to human-readable descriptions
const CONVERSION_STAGES = {
    VALIDATING: 'Validating JSON structure',
    PARSING: 'Parsing JSON data',
    FLATTENING: 'Flattening nested structures',
    TRANSFORMING: 'Transforming data',
    GENERATING: 'Generating Excel file',
    FINALIZING: 'Finalizing output'
};

// Map of status values to CSS classes for visual styling
const STATUS_CLASSES = {
    PENDING: 'status-pending',
    VALIDATING: 'status-validating',
    PROCESSING: 'status-processing',
    COMPLETED: 'status-completed',
    FAILED: 'status-failed'
};

/**
 * ProgressTracker class that manages tracking and visualization of conversion job progress
 */
class ProgressTracker {
    /**
     * Initialize a new ProgressTracker instance
     * @param {string} jobId - The ID of the conversion job to track
     * @param {object} options - Configuration options for the tracker
     */
    constructor(jobId, options = {}) {
        // Store the job ID
        this.jobId = jobId;
        
        // Merge default options with provided options
        this.options = Object.assign({
            containerId: 'status-container',
            updateInterval: PROGRESS_UPDATE_INTERVAL,
            onProgressUpdate: null,
            onStageChange: null,
            onStatusChange: null,
            maxErrorCount: 5
        }, options);
        
        // Set instance properties
        this.containerId = this.options.containerId;
        this.updateInterval = this.options.updateInterval;
        this.currentProgress = 0;
        this.currentStage = null;
        this.currentStatus = 'PENDING';
        this.isTracking = false;
        this.updateTimer = null;
        this.errorCount = 0;
        
        // Set callback functions
        this.onProgressUpdate = typeof this.options.onProgressUpdate === 'function' 
            ? this.options.onProgressUpdate : null;
        this.onStageChange = typeof this.options.onStageChange === 'function' 
            ? this.options.onStageChange : null;
        this.onStatusChange = typeof this.options.onStatusChange === 'function' 
            ? this.options.onStatusChange : null;
            
        // Initialize the UI
        this.initializeUI();
    }
    
    /**
     * Initialize the progress tracking UI elements
     */
    initializeUI() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container element with ID '${this.containerId}' not found`);
            return;
        }
        
        // Find required UI elements
        this.progressBar = container.querySelector('.progress-bar');
        this.progressText = container.querySelector('.progress-text');
        this.statusMessage = container.querySelector('.status-message');
        this.statusIndicator = container.querySelector('.status-indicator');
        this.stageInfo = container.querySelector('.stage-info');
        
        // Initialize UI state
        updateProgressBar(0, this.containerId);
        updateStatusMessage('PENDING', null, this.containerId);
        updateStatusIndicator('PENDING', this.containerId);
        
        console.log(`Progress tracking UI initialized for job ${this.jobId}`);
    }
    
    /**
     * Start tracking progress for the job
     */
    startTracking() {
        if (this.isTracking) {
            return;
        }
        
        this.isTracking = true;
        this.errorCount = 0;
        
        // Initial progress check
        this.checkProgress();
        
        // Set up regular progress checks
        this.updateTimer = setInterval(() => {
            this.checkProgress();
        }, this.updateInterval);
        
        console.log(`Started progress tracking for job ${this.jobId}`);
    }
    
    /**
     * Stop tracking progress for the job
     */
    stopTracking() {
        if (!this.isTracking) {
            return;
        }
        
        this.isTracking = false;
        
        // Clear the update timer
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        
        console.log(`Stopped progress tracking for job ${this.jobId}`);
    }
    
    /**
     * Update the progress display with current information
     * @param {number} progress - Current progress percentage (0-100)
     * @param {string} stage - Current processing stage
     * @param {string} status - Current status
     */
    updateProgress(progress, stage, status) {
        // Store previous values to detect changes
        const progressChanged = progress !== undefined && progress !== this.currentProgress;
        const stageChanged = stage !== undefined && stage !== this.currentStage;
        const statusChanged = status !== undefined && status !== this.currentStatus;
        
        // Update progress bar if progress has changed
        if (progressChanged) {
            updateProgressBar(progress, this.containerId);
            this.currentProgress = progress;
            
            // Call progress update callback if available
            if (this.onProgressUpdate) {
                this.onProgressUpdate(progress);
            }
        }
        
        // Update stage information if stage has changed
        if (stageChanged) {
            updateStatusMessage(status || this.currentStatus, stage, this.containerId);
            this.currentStage = stage;
            
            // Call stage change callback if available
            if (this.onStageChange) {
                this.onStageChange(stage);
            }
        }
        
        // Update status indicator if status has changed
        if (statusChanged) {
            updateStatusIndicator(status, this.containerId);
            this.currentStatus = status;
            
            // Call status change callback if available
            if (this.onStatusChange) {
                this.onStatusChange(status);
            }
            
            // Stop tracking if completed or failed
            if (status === 'COMPLETED' || status === 'FAILED') {
                this.stopTracking();
            }
        }
    }
    
    /**
     * Check the current progress from the server
     */
    checkProgress() {
        if (!this.isTracking) {
            return;
        }
        
        // Make an AJAX request to get the current job status
        $.ajax({
            url: `/api/status/job/${this.jobId}`,
            method: 'GET',
            dataType: 'json',
            success: (response) => this.handleProgressResponse(response),
            error: (error) => this.handleProgressError(error)
        });
    }
    
    /**
     * Handle the response from a progress check request
     * @param {object} response - The server response object
     */
    handleProgressResponse(response) {
        // Reset error count on successful response
        this.errorCount = 0;
        
        // Check if response contains valid status information
        if (!response || typeof response !== 'object') {
            console.warn('Invalid progress response format');
            return;
        }
        
        // Extract progress information from response
        const progress = response.progress_percentage !== undefined 
            ? Math.round(response.progress_percentage) : this.currentProgress;
        const stage = response.current_stage || this.currentStage;
        const status = response.status || this.currentStatus;
        
        // Update progress display
        this.updateProgress(progress, stage, status);
    }
    
    /**
     * Handle errors during progress check requests
     * @param {object} error - The error object
     */
    handleProgressError(error) {
        console.error('Error checking progress:', error);
        
        // Increment error count
        this.errorCount++;
        
        // Stop tracking if error count exceeds maximum
        if (this.errorCount >= this.options.maxErrorCount) {
            console.error(`Maximum error count reached (${this.errorCount}). Stopping progress tracking.`);
            this.updateProgress(this.currentProgress, this.currentStage, 'FAILED');
            this.stopTracking();
        }
    }
}

/**
 * Initialize progress tracking for a specific job
 * @param {string} jobId - The ID of the job to track
 * @param {object} options - Configuration options
 * @returns {ProgressTracker} Instance of the progress tracker
 */
function initProgressTracking(jobId, options = {}) {
    const tracker = new ProgressTracker(jobId, options);
    return tracker;
}

/**
 * Update the progress bar with the current percentage
 * @param {number} percentage - The progress percentage (0-100)
 * @param {string} containerId - The ID of the container element
 */
function updateProgressBar(percentage, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const progressBar = container.querySelector('.progress-bar');
    const progressText = container.querySelector('.progress-text');
    
    if (!progressBar || !progressText) {
        console.warn('Progress bar elements not found');
        return;
    }
    
    // Ensure percentage is within valid range
    percentage = Math.min(100, Math.max(0, percentage));
    
    // Animate the progress bar update for smoother visual feedback
    const currentWidth = parseFloat(progressBar.style.width) || 0;
    animateProgressUpdate(progressBar, currentWidth, percentage, 500);
    
    // Update text immediately
    progressText.textContent = `${percentage}%`;
    
    // Apply appropriate CSS classes based on percentage
    if (percentage === 100) {
        progressBar.classList.add('complete');
        progressBar.classList.remove('in-progress');
    } else if (percentage > 0) {
        progressBar.classList.add('in-progress');
        progressBar.classList.remove('complete');
    } else {
        progressBar.classList.remove('in-progress', 'complete');
    }
}

/**
 * Update the status message with the current stage and status
 * @param {string} status - The current status
 * @param {string} stage - The current stage
 * @param {string} containerId - The ID of the container element
 */
function updateStatusMessage(status, stage, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const statusMessage = container.querySelector('.status-message');
    const stageInfo = container.querySelector('.stage-info');
    
    if (!statusMessage) {
        console.warn('Status message element not found');
        return;
    }
    
    // Get stage description
    const stageDescription = stage && CONVERSION_STAGES[stage] 
        ? CONVERSION_STAGES[stage] 
        : 'Preparing to process';
    
    // Format status message
    let message;
    if (status === 'COMPLETED') {
        message = 'Conversion completed successfully';
    } else if (status === 'FAILED') {
        message = 'Conversion failed';
    } else if (stage) {
        message = stageDescription;
    } else {
        message = 'Waiting to start conversion';
    }
    
    // Use jQuery for smooth transition effect
    $(statusMessage).fadeOut(200, function() {
        $(this).text(message).fadeIn(200);
    });
    
    // Update stage info if available
    if (stageInfo && stage) {
        $(stageInfo).fadeOut(200, function() {
            $(this).text(stageDescription).fadeIn(200);
        });
    }
}

/**
 * Update the status indicator with the current status
 * @param {string} status - The current status
 * @param {string} containerId - The ID of the container element
 */
function updateStatusIndicator(status, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const statusIndicator = container.querySelector('.status-indicator');
    
    if (!statusIndicator) {
        console.warn('Status indicator element not found');
        return;
    }
    
    // Remove all status classes
    Object.values(STATUS_CLASSES).forEach(cls => {
        statusIndicator.classList.remove(cls);
    });
    
    // Add the appropriate status class
    if (STATUS_CLASSES[status]) {
        statusIndicator.classList.add(STATUS_CLASSES[status]);
    }
    
    // Update status text
    let statusText;
    switch (status) {
        case 'PENDING':
            statusText = 'Pending';
            break;
        case 'VALIDATING':
            statusText = 'Validating';
            break;
        case 'PROCESSING':
            statusText = 'Processing';
            break;
        case 'COMPLETED':
            statusText = 'Completed';
            break;
        case 'FAILED':
            statusText = 'Failed';
            break;
        default:
            statusText = status;
    }
    
    // Use jQuery for smooth transition effect
    $(statusIndicator).fadeOut(200, function() {
        $(this).text(statusText).fadeIn(200);
    });
}

/**
 * Format a stage message based on the current stage and progress
 * @param {string} stage - The current stage
 * @param {number} progress - The current progress percentage
 * @returns {string} Formatted stage message
 */
function formatStageMessage(stage, progress) {
    const stageDescription = CONVERSION_STAGES[stage] || 'Processing';
    return `${stageDescription} (${progress}% complete)`;
}

/**
 * Animate the progress bar update for smoother visual feedback
 * @param {HTMLElement} progressBar - The progress bar element
 * @param {number} currentWidth - The current width percentage
 * @param {number} targetWidth - The target width percentage
 * @param {number} duration - The animation duration in milliseconds
 */
function animateProgressUpdate(progressBar, currentWidth, targetWidth, duration = 500) {
    // Use jQuery animation for smooth transition
    $(progressBar).stop().animate(
        { width: `${targetWidth}%` },
        {
            duration: duration,
            easing: 'swing',
            step: function(now) {
                // Update progress text during animation
                const progressText = progressBar.parentNode.querySelector('.progress-text');
                if (progressText) {
                    const roundedProgress = Math.round(now);
                    progressText.textContent = `${roundedProgress}%`;
                }
            },
            complete: function() {
                // Apply appropriate CSS classes when animation completes
                if (targetWidth === 100) {
                    progressBar.classList.add('complete');
                    
                    // Flash effect when complete
                    $(progressBar.parentNode).addClass('conversion-progress').effect('highlight', {}, 1000);
                }
            }
        }
    );
}

// Export public API
export {
    ProgressTracker,
    initProgressTracking,
    updateProgressBar,
    updateStatusMessage,
    updateStatusIndicator
};