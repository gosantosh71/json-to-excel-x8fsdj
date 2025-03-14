/**
 * @fileoverview JavaScript module for handling file uploads in the JSON to Excel Conversion Tool.
 * @version 1.0.0
 */

import { updateUploadAreaState } from './drag-drop.js';

/**
 * Self-contained module for file upload functionality
 */
const fileUploadModule = (function() {
    // Constants
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
    const ALLOWED_FILE_TYPES = ['.json', 'application/json'];
    
    /**
     * Initializes file upload functionality for all file inputs in the web interface
     */
    function initFileUpload() {
        // Find all file input elements
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        if (fileInputs.length === 0) {
            console.warn('No file inputs found for initialization.');
            return;
        }
        
        // Attach change event listeners to each file input
        fileInputs.forEach(fileInput => {
            fileInput.addEventListener('change', handleFileInputChange);
            
            // Initialize upload areas if a file is already selected
            if (fileInput.files && fileInput.files.length > 0) {
                const uploadArea = fileInput.closest('.file-upload-area');
                if (uploadArea) {
                    updateUploadAreaState(uploadArea, true);
                    displayFileInfo(fileInput.files[0], uploadArea.querySelector('.file-info'));
                }
            }
        });
        
        // Set up form submit event listeners
        const forms = document.querySelectorAll('form:has(input[type="file"])');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                
                const validationResult = validateUploadForm(form);
                if (!validationResult.isValid) {
                    showUploadError(validationResult.message, form);
                    return;
                }
                
                uploadFile(form)
                    .then(response => {
                        handleUploadResponse(response, form);
                    })
                    .catch(error => {
                        showUploadError(error.message || 'Upload failed', form);
                    });
            });
        });
        
        // Initialize progress indicators
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(progressBar => {
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        });
    }
    
    /**
     * Handles the change event when a file is selected via the file input
     * @param {Event} event - The change event
     */
    function handleFileInputChange(event) {
        const fileInput = event.target;
        const file = fileInput.files && fileInput.files.length > 0 ? fileInput.files[0] : null;
        const uploadArea = fileInput.closest('.file-upload-area');
        const fileInfoContainer = uploadArea ? uploadArea.querySelector('.file-info') : null;
        
        if (!file) {
            if (uploadArea) {
                updateUploadAreaState(uploadArea, false);
            }
            return;
        }
        
        // Validate the file
        const validation = validateFile(file);
        
        if (!validation.isValid) {
            showUploadError(validation.message, uploadArea);
            resetFileInput(fileInput);
            return;
        }
        
        // Clear any previous errors
        if (uploadArea) {
            clearUploadError(uploadArea);
        }
        
        // Update upload area state and display file information
        if (uploadArea) {
            updateUploadAreaState(uploadArea, true);
        }
        
        if (fileInfoContainer) {
            displayFileInfo(file, fileInfoContainer);
        }
        
        // Enable conversion options if they were previously disabled
        const conversionOptions = document.getElementById('conversion-options');
        if (conversionOptions) {
            conversionOptions.classList.remove('disabled');
            const inputs = conversionOptions.querySelectorAll('input, select, button');
            inputs.forEach(input => {
                input.disabled = false;
            });
        }
    }
    
    /**
     * Validates a file for type and size constraints
     * @param {File} file - The file to validate
     * @return {object} Validation result with status and message
     */
    function validateFile(file) {
        if (!file) {
            return {
                isValid: false,
                message: 'No file selected.'
            };
        }
        
        // Check file type
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        const fileType = file.type.toLowerCase();
        
        const isValidType = ALLOWED_FILE_TYPES.includes(fileExtension) || 
                            ALLOWED_FILE_TYPES.includes(fileType);
        
        if (!isValidType) {
            return {
                isValid: false,
                message: 'Invalid file type. Please select a JSON file.'
            };
        }
        
        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            return {
                isValid: false,
                message: `File size exceeds the maximum limit of ${formatFileSize(MAX_FILE_SIZE)}.`
            };
        }
        
        return {
            isValid: true,
            message: 'File validation successful.'
        };
    }
    
    /**
     * Validates the upload form before submission
     * @param {HTMLFormElement} form - The form to validate
     * @return {object} Validation result with status and message
     */
    function validateUploadForm(form) {
        if (!form) {
            return {
                isValid: false,
                message: 'Invalid form.'
            };
        }
        
        // Get the file input
        const fileInput = form.querySelector('input[type="file"]');
        if (!fileInput) {
            return {
                isValid: false,
                message: 'No file input found in the form.'
            };
        }
        
        // Check if a file has been selected
        if (!fileInput.files || fileInput.files.length === 0) {
            return {
                isValid: false,
                message: 'Please select a file to upload.'
            };
        }
        
        // Validate the selected file
        const fileValidation = validateFile(fileInput.files[0]);
        if (!fileValidation.isValid) {
            return fileValidation;
        }
        
        // Check other form fields if present
        const sheetNameInput = form.querySelector('input[name="sheet_name"]');
        if (sheetNameInput && !sheetNameInput.value.trim()) {
            return {
                isValid: false,
                message: 'Please enter a sheet name.'
            };
        }
        
        return {
            isValid: true,
            message: 'Form validation successful.'
        };
    }
    
    /**
     * Uploads a file to the server using AJAX
     * @param {HTMLFormElement} form - The form containing the file input
     * @return {Promise} Promise that resolves with upload result or rejects with error
     */
    function uploadFile(form) {
        return new Promise((resolve, reject) => {
            // Validate the form
            const validationResult = validateUploadForm(form);
            if (!validationResult.isValid) {
                reject(new Error(validationResult.message));
                return;
            }
            
            const fileInput = form.querySelector('input[type="file"]');
            const file = fileInput.files[0];
            const progressBar = form.querySelector('.progress-bar');
            
            // Create FormData object for the file upload
            const formData = new FormData();
            formData.append('file', file);
            
            // Add additional form data if present
            const formElements = form.querySelectorAll('input:not([type="file"]), select, textarea');
            formElements.forEach(element => {
                if (element.name && element.value) {
                    formData.append(element.name, element.value);
                }
            });
            
            // Update UI to show loading state
            if (progressBar) {
                progressBar.parentElement.classList.remove('hidden');
                updateProgressBar(0, progressBar);
            }
            
            form.classList.add('loading');
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
            }
            
            // Create and configure XMLHttpRequest
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/uploads', true);
            
            // Set up progress handler
            xhr.upload.addEventListener('progress', function(event) {
                if (event.lengthComputable && progressBar) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    updateProgressBar(percentComplete, progressBar);
                }
            });
            
            // Set up event handlers
            xhr.addEventListener('load', function() {
                form.classList.remove('loading');
                if (submitButton) {
                    submitButton.disabled = false;
                }
                
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('Invalid server response'));
                    }
                } else {
                    let errorMessage = 'Upload failed';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMessage = response.message || errorMessage;
                    } catch (e) {
                        // If we can't parse the response, use the status text
                        errorMessage = xhr.statusText || errorMessage;
                    }
                    reject(new Error(errorMessage));
                }
            });
            
            xhr.addEventListener('error', function() {
                form.classList.remove('loading');
                if (submitButton) {
                    submitButton.disabled = false;
                }
                reject(new Error('Network error during file upload'));
            });
            
            xhr.addEventListener('abort', function() {
                form.classList.remove('loading');
                if (submitButton) {
                    submitButton.disabled = false;
                }
                reject(new Error('Upload was aborted'));
            });
            
            // Send the request
            xhr.send(formData);
        });
    }
    
    /**
     * Updates the progress bar during file upload
     * @param {number} percent - The percentage of upload completed
     * @param {HTMLElement} progressBar - The progress bar element to update
     */
    function updateProgressBar(percent, progressBar) {
        if (!progressBar) return;
        
        // Ensure percent is between 0 and 100
        percent = Math.min(100, Math.max(0, percent));
        
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
        
        if (percent === 100) {
            progressBar.classList.add('complete');
        } else {
            progressBar.classList.remove('complete');
        }
        
        // Update ARIA attributes for accessibility
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.setAttribute('aria-valuetext', `${percent}% complete`);
    }
    
    /**
     * Displays information about the selected file
     * @param {File} file - The selected file
     * @param {HTMLElement} container - The container for displaying file info
     */
    function displayFileInfo(file, container) {
        if (!file || !container) return;
        
        // Show the container if it was hidden
        container.classList.remove('hidden');
        
        // Update or create file name element
        let fileNameElement = container.querySelector('.file-name');
        if (!fileNameElement) {
            fileNameElement = document.createElement('div');
            fileNameElement.className = 'file-name';
            container.appendChild(fileNameElement);
        }
        fileNameElement.textContent = file.name;
        
        // Update or create file size element
        let fileSizeElement = container.querySelector('.file-size');
        if (!fileSizeElement) {
            fileSizeElement = document.createElement('div');
            fileSizeElement.className = 'file-size';
            container.appendChild(fileSizeElement);
        }
        fileSizeElement.textContent = formatFileSize(file.size);
        
        // Update or create file type element
        let fileTypeElement = container.querySelector('.file-type');
        if (!fileTypeElement) {
            fileTypeElement = document.createElement('div');
            fileTypeElement.className = 'file-type';
            container.appendChild(fileTypeElement);
        }
        fileTypeElement.textContent = file.type || 'application/json';
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
     * Displays an error message for file upload issues
     * @param {string} message - The error message to display
     * @param {HTMLElement} container - The container where the error should be displayed
     */
    function showUploadError(message, container) {
        if (!container) return;
        
        // Find or create error message element
        let errorElement = container.querySelector('.error-message');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            container.appendChild(errorElement);
        }
        
        // Set error message and show it
        errorElement.textContent = message;
        errorElement.setAttribute('role', 'alert');
        errorElement.classList.remove('hidden');
        
        // Add error class to container
        container.classList.add('error');
    }
    
    /**
     * Clears any displayed upload error messages
     * @param {HTMLElement} container - The container where errors are displayed
     */
    function clearUploadError(container) {
        if (!container) return;
        
        const errorElement = container.querySelector('.error-message');
        
        if (errorElement) {
            errorElement.classList.add('hidden');
            errorElement.textContent = '';
        }
        
        // Remove error class from container
        container.classList.remove('error');
    }
    
    /**
     * Resets a file input element and associated UI elements
     * @param {HTMLInputElement} fileInput - The file input to reset
     */
    function resetFileInput(fileInput) {
        if (!fileInput) return;
        
        // Reset the file input value
        fileInput.value = '';
        
        // Find the associated upload area
        const uploadArea = fileInput.closest('.file-upload-area');
        if (uploadArea) {
            // Update the upload area state
            updateUploadAreaState(uploadArea, false);
            
            // Hide file info
            const fileInfo = uploadArea.querySelector('.file-info');
            if (fileInfo) {
                fileInfo.classList.add('hidden');
            }
            
            // Reset progress bar
            const progressBar = uploadArea.querySelector('.progress-bar');
            if (progressBar) {
                updateProgressBar(0, progressBar);
                progressBar.parentElement.classList.add('hidden');
            }
            
            // Clear any error messages
            clearUploadError(uploadArea);
        }
        
        // Disable conversion options if they exist
        const conversionOptions = document.getElementById('conversion-options');
        if (conversionOptions) {
            conversionOptions.classList.add('disabled');
            const inputs = conversionOptions.querySelectorAll('input, select, button');
            inputs.forEach(input => {
                input.disabled = true;
            });
        }
    }
    
    /**
     * Handles the server response after file upload
     * @param {object} response - The server response object
     * @param {HTMLFormElement} form - The form that initiated the upload
     */
    function handleUploadResponse(response, form) {
        if (!response || !form) return;
        
        // Check if the response indicates success
        if (response.success) {
            // Store the file ID for conversion
            const fileIdInput = form.querySelector('#file-id') || document.createElement('input');
            if (!form.contains(fileIdInput)) {
                fileIdInput.type = 'hidden';
                fileIdInput.id = 'file-id';
                fileIdInput.name = 'file_id';
                form.appendChild(fileIdInput);
            }
            fileIdInput.value = response.file_id;
            
            // Update UI to show completion
            const progressBar = form.querySelector('.progress-bar');
            if (progressBar) {
                updateProgressBar(100, progressBar);
            }
            
            // Enable the conversion button
            const convertButton = document.querySelector('.convert-button');
            if (convertButton) {
                convertButton.disabled = false;
                convertButton.classList.remove('disabled');
            }
            
            // Show success message if provided
            if (response.message) {
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.textContent = response.message;
                successMessage.setAttribute('role', 'status');
                
                // Replace any existing success message
                const existingMessage = form.querySelector('.success-message');
                if (existingMessage) {
                    form.replaceChild(successMessage, existingMessage);
                } else {
                    form.appendChild(successMessage);
                }
            }
        } else {
            // Handle error
            showUploadError(response.message || 'Upload failed', form);
        }
    }
    
    // Public API
    return {
        initFileUpload: initFileUpload,
        uploadFile: uploadFile,
        validateFile: validateFile
    };
})();

// Export the module's public API
export const initFileUpload = fileUploadModule.initFileUpload;
export const uploadFile = fileUploadModule.uploadFile;
export const validateFile = fileUploadModule.validateFile;

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fileUploadModule.initFileUpload);

// For jQuery compatibility if jQuery is used
if (typeof jQuery !== 'undefined') {
    jQuery(document).ready(fileUploadModule.initFileUpload);
}