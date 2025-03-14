/**
 * @fileoverview Drag and drop functionality for file uploads in the JSON to Excel Conversion Tool web interface.
 * @version 1.0.0
 */

/**
 * Self-contained module for implementing drag and drop functionality for file uploads.
 */
const dragDropModule = (function() {
    /**
     * Finds the file input element associated with an upload area.
     * @param {HTMLElement} uploadArea - The upload area element.
     * @return {HTMLElement|null} The associated file input element or null if not found.
     */
    function findAssociatedFileInput(uploadArea) {
        if (!uploadArea || !(uploadArea instanceof HTMLElement)) {
            console.error('Invalid upload area provided to findAssociatedFileInput');
            return null;
        }
        
        // First, look for a file input within the upload area
        let fileInput = uploadArea.querySelector('.file-input');
        
        // If not found, check if the upload area has a data-input attribute
        if (!fileInput && uploadArea.hasAttribute('data-input')) {
            const inputId = uploadArea.getAttribute('data-input');
            fileInput = document.getElementById(inputId);
        }
        
        return fileInput;
    }
    
    /**
     * Updates the visual state of the upload area based on file selection.
     * @param {HTMLElement} uploadArea - The upload area element.
     * @param {boolean} hasFile - Whether a file is selected.
     */
    function updateUploadAreaState(uploadArea, hasFile) {
        if (!uploadArea || !(uploadArea instanceof HTMLElement)) {
            console.error('Invalid upload area provided to updateUploadAreaState');
            return;
        }
        
        if (hasFile) {
            uploadArea.classList.add('has-file');
        } else {
            uploadArea.classList.remove('has-file');
        }
        
        // Update the upload message text if it exists
        const messageElement = uploadArea.querySelector('.file-upload-message');
        if (messageElement) {
            messageElement.textContent = hasFile ? 
                'File selected. Click to change.' : 
                'Drag and drop file here or click to browse';
        }
    }
    
    /**
     * Handles the dragenter event when a file is dragged over the upload area.
     * @param {DragEvent} event - The dragenter event.
     */
    function handleDragEnter(event) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.add('drag-over');
    }
    
    /**
     * Handles the dragover event when a file is being dragged over the upload area.
     * @param {DragEvent} event - The dragover event.
     */
    function handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        // Set the dropEffect to 'copy' to indicate a copy operation
        if (event.dataTransfer) {
            event.dataTransfer.dropEffect = 'copy';
        }
    }
    
    /**
     * Handles the dragleave event when a file is dragged away from the upload area.
     * @param {DragEvent} event - The dragleave event.
     */
    function handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.remove('drag-over');
    }
    
    /**
     * Validates if the file type is acceptable
     * @param {File} file - The file to validate
     * @param {HTMLElement} fileInput - The file input element with accept attribute
     * @return {boolean} Whether the file type is acceptable
     */
    function validateFileType(file, fileInput) {
        if (!fileInput || !fileInput.accept || fileInput.accept.trim() === '') {
            // If no accept attribute is specified, accept all files
            return true;
        }
        
        // Get accepted file types from the input
        const acceptedTypes = fileInput.accept.split(',').map(type => type.trim().toLowerCase());
        
        // Check file type
        const fileType = file.type.toLowerCase();
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        // Check if file type or extension is in the accepted types
        return acceptedTypes.some(type => {
            if (type === '*' || type === '*/*') {
                return true;
            } else if (type.startsWith('.')) {
                // Check file extension
                return type === fileExtension;
            } else if (type.endsWith('/*')) {
                // Check mime type group (e.g., 'image/*')
                const typeGroup = type.split('/')[0];
                return fileType.startsWith(typeGroup + '/');
            } else {
                // Check exact mime type
                return type === fileType;
            }
        });
    }
    
    /**
     * Handles the drop event when a file is dropped onto the upload area.
     * @param {DragEvent} event - The drop event.
     */
    function handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const uploadArea = event.currentTarget;
        
        // Remove the drag-over class
        uploadArea.classList.remove('drag-over');
        
        // Get the dropped files
        const files = event.dataTransfer?.files;
        
        if (files && files.length > 0) {
            const fileInput = findAssociatedFileInput(uploadArea);
            
            if (fileInput) {
                // Check if the file type is acceptable
                const file = files[0];
                if (!validateFileType(file, fileInput)) {
                    alert('File type not supported. Please select a valid JSON file.');
                    return;
                }
                
                try {
                    // Set the file to the input
                    // Use DataTransfer to set files property as it's generally read-only
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInput.files = dataTransfer.files;
                    
                    // Trigger change event on the file input
                    const changeEvent = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(changeEvent);
                    
                    // Update upload area state
                    updateUploadAreaState(uploadArea, true);
                } catch (error) {
                    console.error('Error setting file:', error);
                    alert('There was an error processing your file. Please try again.');
                }
            }
        }
    }
    
    /**
     * Handles click events on the upload area to trigger the file input.
     * @param {MouseEvent} event - The click event.
     */
    function handleClick(event) {
        const uploadArea = event.currentTarget;
        const fileInput = findAssociatedFileInput(uploadArea);
        
        if (fileInput) {
            fileInput.click();
        }
    }
    
    /**
     * Initializes drag and drop functionality for file upload areas.
     */
    function initDragDrop() {
        // Find all file upload areas
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        
        if (uploadAreas.length === 0) {
            console.warn('No file upload areas found for drag and drop initialization');
        }
        
        uploadAreas.forEach(uploadArea => {
            // Add drag event listeners
            uploadArea.addEventListener('dragenter', handleDragEnter);
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
            uploadArea.addEventListener('click', handleClick);
            
            // Set up file input change handler
            const fileInput = findAssociatedFileInput(uploadArea);
            if (fileInput) {
                fileInput.addEventListener('change', function() {
                    updateUploadAreaState(uploadArea, this.files.length > 0);
                });
                
                // Initialize state based on whether file is already selected
                updateUploadAreaState(uploadArea, fileInput.files.length > 0);
            }
            
            // Add ARIA attributes for accessibility
            uploadArea.setAttribute('role', 'button');
            uploadArea.setAttribute('aria-label', 'Upload file area. Drag and drop a file here or click to browse.');
            uploadArea.setAttribute('tabindex', '0');
            
            // Add keyboard support
            uploadArea.addEventListener('keydown', function(event) {
                // Trigger click on Enter or Space
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    handleClick(event);
                }
            });
        });
    }
    
    // Return public API
    return {
        initDragDrop: initDragDrop,
        updateUploadAreaState: updateUploadAreaState
    };
})();

// Export the module functions
export const initDragDrop = dragDropModule.initDragDrop;
export const updateUploadAreaState = dragDropModule.updateUploadAreaState;

// Initialize drag and drop functionality when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', dragDropModule.initDragDrop);