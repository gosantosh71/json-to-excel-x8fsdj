/**
 * @fileoverview Main JavaScript entry point for the JSON to Excel Conversion Tool web interface.
 * This file initializes all client-side functionality, coordinates between different modules,
 * and provides common utility functions used throughout the application.
 * 
 * @version 1.0.0
 * @requires jQuery 3.6.0
 */

import { initDragDrop } from './drag-drop.js';
import { initFileUpload } from './file-upload.js';
import { initFormValidation } from './form-validation.js';
import { initProgressTracking } from './progress-tracking.js';
import { initStatusPolling } from './status-polling.js';
import { initConversion } from './conversion.js';

// Global application configuration
const APP_CONFIG = {
    DEBUG: false,
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    ANIMATION_DURATION: 300,
    NOTIFICATION_TIMEOUT: 5000
};

/**
 * Class that manages the overall application state and functionality
 */
class AppManager {
    /**
     * Initializes a new AppManager instance
     * @param {object} config - Configuration for the application
     */
    constructor(config = {}) {
        // Merge default configuration with provided config
        this.config = Object.assign({}, APP_CONFIG, config);
        // Initialize state object for tracking application state
        this.state = {};
        // Initialize elements object for storing DOM element references
        this.elements = {};
        // Initialize modules object for tracking initialized modules
        this.modules = {};
    }
    
    /**
     * Initializes the application manager
     */
    init() {
        // Find and store references to common DOM elements
        this.elements = {
            notificationContainer: document.getElementById('notification-container'),
            uploadForm: document.getElementById('upload-form'),
            conversionForm: document.getElementById('conversion-form'),
            processingContainer: document.getElementById('processing-container'),
            resultContainer: document.getElementById('result-container')
        };
        
        // Initialize core modules
        this.initModule('dragDrop', initDragDrop);
        this.initModule('fileUpload', initFileUpload);
        this.initModule('formValidation', initFormValidation);
        this.initModule('conversion', initConversion);
        
        // Set up global event listeners
        this.setupGlobalEventListeners();
        
        // Initialize page-specific functionality
        this.initPageSpecific();
        
        if (this.config.DEBUG) {
            console.log('Application initialized');
        }
    }
    
    /**
     * Initializes a specific module if not already initialized
     * @param {string} moduleName - The name of the module
     * @param {function} initFunction - The initialization function
     * @param {object} options - Options to pass to the initialization function
     * @return {boolean} True if module was initialized, false if already initialized
     */
    initModule(moduleName, initFunction, options = {}) {
        if (this.modules[moduleName]) {
            return false;
        }
        
        try {
            initFunction(options);
            this.modules[moduleName] = true;
            return true;
        } catch (error) {
            console.error(`Failed to initialize module: ${moduleName}`, error);
            return false;
        }
    }
    
    /**
     * Gets the current application state or a specific state property
     * @param {string} property - Optional property name
     * @return {any} State value or entire state object
     */
    getState(property) {
        if (property) {
            return this.state[property];
        }
        return this.state;
    }
    
    /**
     * Updates the application state
     * @param {string} property - The state property to update
     * @param {any} value - The new value
     */
    setState(property, value) {
        this.state[property] = value;
        // Trigger state change event for subscribers
        const event = new CustomEvent('appStateChange', { 
            detail: { property, value, state: this.state }
        });
        document.dispatchEvent(event);
    }
}

/**
 * Initializes the entire application by calling all module initializers
 */
function initApp() {
    // Create and initialize the app manager
    const appManager = new AppManager();
    appManager.init();
    
    // Make the app manager globally available
    window.appManager = appManager;
    
    // Set up notification system
    setupNotifications();
    
    // Set up page-specific initializations
    initPageSpecific();
    
    // Set up global event listeners
    setupGlobalEventListeners();
    
    // Log initialization
    if (APP_CONFIG.DEBUG) {
        console.log('Application initialized');
    }
}

/**
 * Initializes functionality specific to the current page
 */
function initPageSpecific() {
    const body = document.body;
    const pageName = body.dataset.page || '';
    
    switch (pageName) {
        case 'upload':
            // Initialize upload-specific functionality
            break;
        case 'processing':
            // Initialize progress tracking and status polling
            const jobId = getUrlParameter('job_id');
            if (jobId) {
                initProgressTracking(jobId);
                initStatusPolling(jobId);
            }
            break;
        case 'results':
            // Initialize result-specific functionality
            break;
        case 'error':
            // Initialize error-specific functionality
            break;
    }
}

/**
 * Sets up the notification system for displaying messages to users
 */
function setupNotifications() {
    // Find the notification container
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;
    
    // Set up close button event listeners for existing notifications
    const notifications = notificationContainer.querySelectorAll('.notification');
    notifications.forEach(notification => {
        const closeButton = notification.querySelector('.notification-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                closeNotification(notification);
            });
        }
        
        // Set up auto-dismiss for non-error notifications
        if (!notification.classList.contains('notification-error')) {
            setTimeout(() => {
                closeNotification(notification);
            }, APP_CONFIG.NOTIFICATION_TIMEOUT);
        }
    });
}

/**
 * Displays a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - The notification type (info, success, warning, error)
 * @param {object} options - Additional options for the notification
 * @return {HTMLElement} The created notification element
 */
function showNotification(message, type = 'info', options = {}) {
    // Get or create the notification container
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Create the notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Create the message element
    const messageElement = document.createElement('div');
    messageElement.className = 'notification-message';
    messageElement.textContent = message;
    notification.appendChild(messageElement);
    
    // Create the close button
    const closeButton = document.createElement('button');
    closeButton.className = 'notification-close';
    closeButton.innerHTML = '&times;';
    closeButton.setAttribute('aria-label', 'Close notification');
    notification.appendChild(closeButton);
    
    // Add event listener for close button
    closeButton.addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Add notification to container
    notificationContainer.appendChild(notification);
    
    // Set up auto-dismiss timer for non-error notifications
    if (type !== 'error' && options.timeout !== false) {
        const timeout = options.timeout || APP_CONFIG.NOTIFICATION_TIMEOUT;
        setTimeout(() => {
            closeNotification(notification);
        }, timeout);
    }
    
    return notification;
}

/**
 * Closes a notification element with animation
 * @param {HTMLElement} notification - The notification element to close
 */
function closeNotification(notification) {
    if (!notification) return;
    
    // Add the closing class for animation
    notification.classList.add('closing');
    
    // After animation completes, remove the notification
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, APP_CONFIG.ANIMATION_DURATION);
}

/**
 * Sets up global event listeners for the application
 */
function setupGlobalEventListeners() {
    // Handle unhandled Promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled Promise Rejection:', event.reason);
        
        if (APP_CONFIG.DEBUG) {
            showNotification('An unexpected error occurred. See console for details.', 'error');
        } else {
            showNotification('An unexpected error occurred. Please try again later.', 'error');
        }
    });
    
    // Set up AJAX error handling with jQuery
    $(document).ajaxError((event, jqXHR, settings, error) => {
        handleAjaxError(jqXHR);
    });
    
    // Add keyboard accessibility features
    document.addEventListener('keydown', (event) => {
        // Close notifications on Escape key
        if (event.key === 'Escape') {
            const openNotifications = document.querySelectorAll('.notification');
            openNotifications.forEach(notification => {
                closeNotification(notification);
            });
        }
    });
}

/**
 * Handles AJAX errors and displays appropriate notifications
 * @param {object} error - The error object
 */
function handleAjaxError(error) {
    // Log error details in debug mode
    if (APP_CONFIG.DEBUG) {
        console.error('AJAX Error:', error);
    }
    
    let errorMessage = 'An error occurred while communicating with the server.';
    
    // Try to extract more specific error message from response
    if (error.responseJSON && error.responseJSON.message) {
        errorMessage = error.responseJSON.message;
    } else if (error.statusText) {
        errorMessage = `Server error: ${error.statusText}`;
    }
    
    // Show appropriate error message based on status code
    switch (error.status) {
        case 400:
            errorMessage = `Bad request: ${errorMessage}`;
            break;
        case 401:
            errorMessage = 'You must be logged in to perform this action.';
            break;
        case 403:
            errorMessage = 'You do not have permission to perform this action.';
            break;
        case 404:
            errorMessage = 'The requested resource could not be found.';
            break;
        case 413:
            errorMessage = 'The file you are trying to upload is too large.';
            break;
        case 500:
            errorMessage = 'An internal server error occurred. Please try again later.';
            break;
    }
    
    // Display the error notification
    showNotification(errorMessage, 'error');
}

/**
 * Formats a file size in bytes to a human-readable string
 * @param {number} bytes - The file size in bytes
 * @return {string} Formatted file size (e.g., '2.5 MB')
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    // Return formatted size with appropriate unit
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + units[i];
}

/**
 * Creates a debounced version of a function that delays execution
 * @param {function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @return {function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Gets a parameter value from the URL query string
 * @param {string} name - The parameter name
 * @return {string} Parameter value or null if not found
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initApp);

// Initialize with jQuery as well for compatibility
if (typeof jQuery !== 'undefined') {
    jQuery(document).ready(initApp);
}

// Export public API
export {
    initApp,
    showNotification,
    formatFileSize,
    debounce,
    AppManager
};