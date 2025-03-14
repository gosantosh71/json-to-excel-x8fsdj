/**
 * @fileoverview Client-side form validation for the JSON to Excel Conversion Tool web interface.
 * This module validates form inputs before submission, provides real-time feedback to users,
 * and ensures data integrity before sending data to the server.
 * 
 * @version 1.0.0
 * @requires ./file-upload.js
 * @requires jQuery (optional, v3.6.0+)
 */

import { validateFile } from './file-upload.js';

/**
 * Self-contained module for form validation functionality
 */
const formValidationModule = (function() {
    // Constants for validation patterns
    const SHEET_NAME_PATTERN = /^[\w\s\-\.]{1,31}$/;
    const MAX_SHEET_NAME_LENGTH = 31;
    const VALID_ARRAY_HANDLING_OPTIONS = ['expand', 'join'];
    
    /**
     * Initializes form validation functionality for all forms with data-validate attribute
     */
    function initFormValidation() {
        // Find all forms that need validation
        const forms = document.querySelectorAll('form[data-validate]');
        
        if (forms.length === 0) {
            console.warn('No forms found with data-validate attribute.');
            return;
        }
        
        // Attach submit event listeners to each form
        forms.forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
            
            // Set up input event listeners for real-time validation
            const fields = form.querySelectorAll('input, select, textarea');
            fields.forEach(field => {
                // Set up appropriate event listeners based on field type
                field.addEventListener('input', handleFieldInput);
                field.addEventListener('change', handleFieldInput);
                field.addEventListener('blur', handleFieldInput);
                
                // Initialize validation message containers
                const fieldId = field.id || field.name;
                if (fieldId) {
                    let messageElement = document.getElementById(`${fieldId}-message`);
                    if (!messageElement) {
                        // Create message element if it doesn't exist
                        messageElement = document.createElement('div');
                        messageElement.id = `${fieldId}-message`;
                        messageElement.className = 'validation-message hidden';
                        messageElement.setAttribute('aria-live', 'polite');
                        
                        // Insert after the field
                        if (field.nextElementSibling) {
                            field.parentNode.insertBefore(messageElement, field.nextElementSibling);
                        } else {
                            field.parentNode.appendChild(messageElement);
                        }
                    }
                }
            });
        });
        
        console.log('Form validation initialized');
    }
    
    /**
     * Validates an entire form and returns validation result
     * @param {HTMLFormElement} form - The form to validate
     * @return {object} Validation result with isValid boolean and errors object
     */
    function validateForm(form) {
        if (!form) {
            return {
                isValid: false,
                errors: { general: 'Invalid form element' }
            };
        }
        
        // Initialize errors object
        const errors = {};
        let isValid = true;
        
        // Get all input, select, and textarea elements in the form
        const fields = form.querySelectorAll('input, select, textarea');
        
        // Validate each field
        fields.forEach(field => {
            // Skip hidden and disabled fields
            if (field.type === 'hidden' || field.disabled) return;
            
            // Skip file inputs (handled separately)
            if (field.type === 'file') return;
            
            // Validate the field
            const fieldValidation = validateField(field);
            
            if (!fieldValidation.isValid) {
                isValid = false;
                errors[field.name || field.id || 'unknown'] = fieldValidation.message;
                showValidationError(field, fieldValidation.message);
            } else {
                clearValidationError(field);
            }
        });
        
        // Handle file inputs separately since they need special validation
        const fileInputs = form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(fileInput => {
            if (fileInput.files && fileInput.files.length > 0) {
                const fileValidation = validateFile(fileInput.files[0]);
                if (!fileValidation.isValid) {
                    isValid = false;
                    errors[fileInput.name || fileInput.id || 'file'] = fileValidation.message;
                    showValidationError(fileInput, fileValidation.message);
                } else {
                    clearValidationError(fileInput);
                }
            } else if (fileInput.hasAttribute('data-validate-required')) {
                isValid = false;
                const message = 'Please select a file';
                errors[fileInput.name || fileInput.id || 'file'] = message;
                showValidationError(fileInput, message);
            }
        });
        
        // Form-specific validation based on form type
        if (form.hasAttribute('data-form-type')) {
            const formType = form.getAttribute('data-form-type');
            
            if (formType === 'conversion') {
                const conversionValidation = validateConversionForm(form);
                if (!conversionValidation.isValid) {
                    isValid = false;
                    Object.assign(errors, conversionValidation.errors);
                }
            }
        }
        
        return {
            isValid: isValid,
            errors: errors
        };
    }
    
    /**
     * Validates a single form field based on its attributes and type
     * @param {HTMLElement} field - The field to validate
     * @return {object} Validation result with isValid boolean and message string
     */
    function validateField(field) {
        // Get field attributes
        const value = field.value.trim();
        const isRequired = field.hasAttribute('data-validate-required') || field.required;
        const fieldType = field.type || 'text';
        const fieldName = field.getAttribute('data-validate-label') || 
                          field.getAttribute('aria-label') || 
                          field.name || 
                          field.id || 
                          'Field';
        
        // Check if field is required and has a value
        if (isRequired && value === '') {
            return {
                isValid: false,
                message: `${fieldName} is required`
            };
        }
        
        // If field is not required and empty, it's valid
        if (!isRequired && value === '') {
            return {
                isValid: true,
                message: ''
            };
        }
        
        // Validate based on field type and attributes
        switch(fieldType) {
            case 'email':
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(value)) {
                    return {
                        isValid: false,
                        message: 'Please enter a valid email address'
                    };
                }
                break;
                
            case 'number':
                if (isNaN(parseFloat(value))) {
                    return {
                        isValid: false,
                        message: 'Please enter a valid number'
                    };
                }
                
                // Check min/max constraints
                if (field.hasAttribute('data-validate-min')) {
                    const min = parseFloat(field.getAttribute('data-validate-min'));
                    if (parseFloat(value) < min) {
                        return {
                            isValid: false,
                            message: `Value must be at least ${min}`
                        };
                    }
                }
                
                if (field.hasAttribute('data-validate-max')) {
                    const max = parseFloat(field.getAttribute('data-validate-max'));
                    if (parseFloat(value) > max) {
                        return {
                            isValid: false,
                            message: `Value must not exceed ${max}`
                        };
                    }
                }
                break;
                
            case 'text':
            case 'textarea':
                // Check pattern if specified
                if (field.hasAttribute('data-validate-pattern')) {
                    const pattern = new RegExp(field.getAttribute('data-validate-pattern'));
                    if (!pattern.test(value)) {
                        return {
                            isValid: false,
                            message: field.getAttribute('data-validate-message') || 'Please enter a valid value'
                        };
                    }
                }
                
                // Check min/max length
                if (field.hasAttribute('data-validate-minlength')) {
                    const minLength = parseInt(field.getAttribute('data-validate-minlength'));
                    if (value.length < minLength) {
                        return {
                            isValid: false,
                            message: `Must be at least ${minLength} characters`
                        };
                    }
                }
                
                if (field.hasAttribute('data-validate-maxlength')) {
                    const maxLength = parseInt(field.getAttribute('data-validate-maxlength'));
                    if (value.length > maxLength) {
                        return {
                            isValid: false,
                            message: `Cannot exceed ${maxLength} characters`
                        };
                    }
                }
                break;
        }
        
        // Specific field validations based on field name or id
        if (field.id === 'sheet-name' || field.name === 'sheet_name') {
            return validateSheetName(value);
        }
        
        if (field.name === 'array_handling') {
            return validateArrayHandling(value);
        }
        
        // If we get here, field is valid
        return {
            isValid: true,
            message: ''
        };
    }
    
    /**
     * Validates a sheet name against Excel naming conventions
     * @param {string} sheetName - The sheet name to validate
     * @return {object} Validation result with isValid boolean and message string
     */
    function validateSheetName(sheetName) {
        // Check if sheet name is not empty
        if (!sheetName) {
            return {
                isValid: false,
                message: 'Sheet name is required'
            };
        }
        
        // Check sheet name length
        if (sheetName.length > MAX_SHEET_NAME_LENGTH) {
            return {
                isValid: false,
                message: `Sheet name cannot exceed ${MAX_SHEET_NAME_LENGTH} characters`
            };
        }
        
        // Check sheet name pattern
        if (!SHEET_NAME_PATTERN.test(sheetName)) {
            return {
                isValid: false,
                message: 'Sheet name can only contain letters, numbers, spaces, hyphens, and periods'
            };
        }
        
        return {
            isValid: true,
            message: ''
        };
    }
    
    /**
     * Validates array handling option selection
     * @param {string} option - The selected array handling option
     * @return {object} Validation result with isValid boolean and message string
     */
    function validateArrayHandling(option) {
        // Check if option is not empty
        if (!option) {
            return {
                isValid: false,
                message: 'Please select an array handling option'
            };
        }
        
        // Check if option is valid
        if (!VALID_ARRAY_HANDLING_OPTIONS.includes(option)) {
            return {
                isValid: false,
                message: `Invalid option. Please select either "${VALID_ARRAY_HANDLING_OPTIONS.join('" or "')}")`
            };
        }
        
        return {
            isValid: true,
            message: ''
        };
    }
    
    /**
     * Displays a validation error message for a field
     * @param {HTMLElement} field - The field with the error
     * @param {string} message - The error message to display
     */
    function showValidationError(field, message) {
        // Find the message element
        let messageElement;
        const fieldId = field.id || field.name;
        
        if (fieldId) {
            messageElement = document.getElementById(`${fieldId}-message`);
        }
        
        // If no message element found, look for one near the field
        if (!messageElement) {
            messageElement = field.nextElementSibling;
            if (!messageElement || !messageElement.classList.contains('validation-message')) {
                // Create a new message element
                messageElement = document.createElement('div');
                messageElement.className = 'validation-message';
                
                // Insert after the field
                if (field.nextElementSibling) {
                    field.parentNode.insertBefore(messageElement, field.nextElementSibling);
                } else {
                    field.parentNode.appendChild(messageElement);
                }
            }
        }
        
        // Update message and display it
        if (messageElement) {
            messageElement.textContent = message;
            messageElement.classList.add('error');
            messageElement.classList.remove('hidden');
            messageElement.setAttribute('role', 'alert');
        }
        
        // Mark the field as invalid
        field.classList.add('invalid');
        field.classList.remove('valid');
        field.setAttribute('aria-invalid', 'true');
        
        // If field is in a form group, mark the group as well
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            formGroup.classList.add('has-error');
        }
    }
    
    /**
     * Clears validation error message for a field
     * @param {HTMLElement} field - The field to clear errors for
     */
    function clearValidationError(field) {
        // Find the message element
        let messageElement;
        const fieldId = field.id || field.name;
        
        if (fieldId) {
            messageElement = document.getElementById(`${fieldId}-message`);
        }
        
        // If no message element found, look for one near the field
        if (!messageElement) {
            messageElement = field.nextElementSibling;
            if (!messageElement || !messageElement.classList.contains('validation-message')) {
                return;
            }
        }
        
        // Hide the message
        if (messageElement) {
            messageElement.classList.add('hidden');
            messageElement.classList.remove('error');
        }
        
        // Mark the field as valid
        field.classList.remove('invalid');
        field.classList.add('valid');
        field.setAttribute('aria-invalid', 'false');
        
        // If field is in a form group, update the group as well
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            formGroup.classList.remove('has-error');
        }
    }
    
    /**
     * Handles form submission event with validation
     * @param {Event} event - The submit event
     */
    function handleFormSubmit(event) {
        const form = event.currentTarget;
        
        // Prevent default form submission initially
        event.preventDefault();
        
        // Validate the form
        const validation = validateForm(form);
        
        if (!validation.isValid) {
            // Focus on first invalid field
            const firstInvalidField = form.querySelector('.invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
            }
            
            // If there's a form-level error container, update it
            const formErrorContainer = form.querySelector('.form-errors');
            if (formErrorContainer) {
                formErrorContainer.textContent = Object.values(validation.errors).join('. ');
                formErrorContainer.classList.remove('hidden');
                formErrorContainer.setAttribute('role', 'alert');
            }
            
            return;
        }
        
        // Hide form-level error container if it exists
        const formErrorContainer = form.querySelector('.form-errors');
        if (formErrorContainer) {
            formErrorContainer.classList.add('hidden');
        }
        
        // If form has data-ajax attribute, handle via AJAX
        if (form.hasAttribute('data-ajax')) {
            // AJAX submission handling would go here
            // (This would typically be handled by a separate module)
        } else {
            // Allow the form to submit
            form.submit();
        }
    }
    
    /**
     * Handles input events on form fields for real-time validation
     * @param {Event} event - The input event
     */
    function handleFieldInput(event) {
        const field = event.target;
        
        // Only validate in real-time if the field has data-validate-realtime attribute
        // or if the event type is 'blur' (validate on blur for all fields)
        if (field.hasAttribute('data-validate-realtime') || event.type === 'blur') {
            const validation = validateField(field);
            
            if (!validation.isValid) {
                showValidationError(field, validation.message);
            } else {
                clearValidationError(field);
            }
        } else {
            // Clear any existing validation errors
            clearValidationError(field);
        }
        
        // If field has dependent fields, validate them as well
        if (field.hasAttribute('data-validate-depends-on')) {
            const dependentFields = field.getAttribute('data-validate-depends-on').split(',');
            dependentFields.forEach(dependentFieldId => {
                const dependentField = document.getElementById(dependentFieldId.trim());
                if (dependentField) {
                    const validation = validateField(dependentField);
                    if (!validation.isValid) {
                        showValidationError(dependentField, validation.message);
                    } else {
                        clearValidationError(dependentField);
                    }
                }
            });
        }
    }
    
    /**
     * Performs specific validation for the conversion form
     * @param {HTMLFormElement} form - The conversion form
     * @return {object} Validation result with isValid boolean and errors object
     */
    function validateConversionForm(form) {
        const errors = {};
        let isValid = true;
        
        // Validate file input
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            if (!fileInput.files || fileInput.files.length === 0) {
                isValid = false;
                errors['file'] = 'Please select a JSON file to convert';
                showValidationError(fileInput, 'Please select a JSON file to convert');
            } else {
                const fileValidation = validateFile(fileInput.files[0]);
                if (!fileValidation.isValid) {
                    isValid = false;
                    errors['file'] = fileValidation.message;
                    showValidationError(fileInput, fileValidation.message);
                }
            }
        }
        
        // Validate sheet name
        const sheetNameInput = form.querySelector('#sheet-name, [name="sheet_name"]');
        if (sheetNameInput) {
            const sheetValidation = validateSheetName(sheetNameInput.value.trim());
            if (!sheetValidation.isValid) {
                isValid = false;
                errors['sheet_name'] = sheetValidation.message;
                showValidationError(sheetNameInput, sheetValidation.message);
            }
        }
        
        // Validate array handling
        const arrayHandlingInput = form.querySelector('[name="array_handling"]');
        if (arrayHandlingInput) {
            const arrayValidation = validateArrayHandling(arrayHandlingInput.value);
            if (!arrayValidation.isValid) {
                isValid = false;
                errors['array_handling'] = arrayValidation.message;
                showValidationError(arrayHandlingInput, arrayValidation.message);
            }
        }
        
        return {
            isValid: isValid,
            errors: errors
        };
    }
    
    // Return public API
    return {
        initFormValidation: initFormValidation,
        validateForm: validateForm,
        validateField: validateField
    };
})();

// Export the module's public API
export const initFormValidation = formValidationModule.initFormValidation;
export const validateForm = formValidationModule.validateForm;
export const validateField = formValidationModule.validateField;

// Initialize validation when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', formValidationModule.initFormValidation);

// For jQuery compatibility if jQuery is used
if (typeof jQuery !== 'undefined') {
    jQuery(document).ready(formValidationModule.initFormValidation);
}