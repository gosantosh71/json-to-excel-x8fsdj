/* This is a CSS styling guide - comments are part of the actual styling documentation */
```

# JSON to Excel Conversion Tool - Style Guide

## Introduction

### Design Principles

- **Simplicity**: Clean, minimalist design focused on core functionality
- **Clarity**: Visual hierarchy that guides users through the conversion process
- **Accessibility**: Interfaces usable by people of all abilities
- **Responsiveness**: Optimal experience across device sizes
- **Consistency**: Unified visual language throughout the application

### File Organization

```
src/web/static/css/
├── app.css         # Core styles and global elements
├── form.css        # Form elements and validation styles
├── responsive.css  # Media queries and responsive adaptations
├── error.css       # Error page and message styling
└── components/     # Individual component styles
    ├── button.css
    ├── card.css
    ├── progress.css
    └── upload.css
```

## Theme and Variables

### Color Palette

```css
:root {
  /* Primary colors */
  --color-primary: #3498db;
  --color-primary-light: #5faee3;
  --color-primary-dark: #217dbb;
  
  /* Secondary colors */
  --color-secondary: #2ecc71;
  --color-secondary-light: #54d98c;
  --color-secondary-dark: #25a25a;
  
  /* Accent colors */
  --color-accent: #f39c12;
  --color-accent-light: #f5b041;
  --color-accent-dark: #d68910;
  
  /* Neutral colors */
  --color-text: #333333;
  --color-text-light: #666666;
  --color-text-lighter: #999999;
  --color-background: #ffffff;
  --color-background-alt: #f8f9fa;
  --color-border: #dddddd;
  
  /* Semantic colors */
  --color-success: #2ecc71;
  --color-info: #3498db;
  --color-warning: #f39c12;
  --color-error: #e74c3c;
}
```

| Color | Usage |
| ----- | ----- |
| Primary | Main brand color, buttons, links, highlights |
| Secondary | Success states, progress indicators, confirmation messages |
| Accent | Attention-grabbing elements, warnings, important calls to action |
| Text | Body text, headings, and labels with appropriate contrast |
| Background | Page backgrounds, card backgrounds, and alternating rows |
| Semantic | Success messages, errors, warnings, and information alerts |

### Typography

```css
:root {
  /* Font families */
  --font-family-base: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-family-monospace: 'Courier New', monospace;
  
  /* Font sizes */
  --font-size-base: 16px;
  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-md: 1rem;      /* 16px */
  --font-size-lg: 1.25rem;   /* 20px */
  --font-size-xl: 1.5rem;    /* 24px */
  --font-size-xxl: 2rem;     /* 32px */
  
  /* Font weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
  
  /* Line heights */
  --line-height-tight: 1.25;
  --line-height-base: 1.5;
  --line-height-loose: 1.75;
}
```

| Element | Size | Weight | Line Height |
| ------- | ---- | ------ | ----------- |
| Page Title | xxl (2rem) | Bold | Tight |
| Section Headings | xl (1.5rem) | Bold | Tight |
| Subsection Headings | lg (1.25rem) | Medium | Tight |
| Body Text | md (1rem) | Normal | Base |
| Small Text | sm (0.875rem) | Normal | Base |
| Button Text | md (1rem) | Medium | Base |

### Spacing

```css
:root {
  /* Base spacing units */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-xxl: 3rem;     /* 48px */
  
  /* Component specific spacing */
  --container-padding: var(--spacing-lg);
  --card-padding: var(--spacing-lg);
  --input-padding: var(--spacing-sm) var(--spacing-md);
  --button-padding: var(--spacing-sm) var(--spacing-lg);
}
```

- Use consistent spacing variables throughout the application
- Maintain proper spacing hierarchy (smaller spacing for related items, larger for section breaks)
- Double spacing between major sections (var(--spacing-xl) or var(--spacing-xxl))
- Standard spacing between form elements (var(--spacing-lg))

### Borders and Shadows

```css
:root {
  /* Borders */
  --border-radius-sm: 3px;
  --border-radius-md: 5px;
  --border-radius-lg: 8px;
  --border-radius-full: 9999px;
  
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 3px;
  
  --border-color: var(--color-border);
  --border-color-focus: var(--color-primary);
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Focus ring */
  --focus-ring: 0 0 0 3px rgba(52, 152, 219, 0.5);
}
```

## Layout Components

### Container

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--container-padding);
  padding-right: var(--container-padding);
}

.container-sm {
  max-width: 640px;
}

.container-md {
  max-width: 768px;
}

.container-lg {
  max-width: 1024px;
}
```

- Use `.container` for standard page layout
- Use `.container-sm` for focused content like the file upload form
- Always maintain proper padding on small screens
- Center containers in the viewport

### Card

```css
.card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--card-padding);
  margin-bottom: var(--spacing-lg);
}

.card-header {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: var(--border-width-thin) solid var(--border-color);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin: 0;
}

.card-body {
  margin-bottom: var(--spacing-md);
}

.card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-sm);
  border-top: var(--border-width-thin) solid var(--border-color);
}
```

- Use cards to contain related content and create visual separation
- Include clear visual hierarchy with card headers and footers
- Maintain consistent spacing between cards (var(--spacing-lg))
- Cards should have appropriate padding for content readability

### Navigation

```css
.header {
  background-color: var(--color-background);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-md) 0;
  margin-bottom: var(--spacing-xl);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  text-decoration: none;
}

.nav {
  display: flex;
  gap: var(--spacing-md);
}

.nav-link {
  color: var(--color-text);
  text-decoration: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  transition: background-color 0.2s ease;
}

.nav-link:hover {
  background-color: var(--color-background-alt);
}

.nav-link.active {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}
```

- Keep navigation simple and focused on essential items
- Clearly indicate the current page with `.active` class
- Include a skip-to-content link for accessibility
- Collapse navigation into a hamburger menu on mobile devices

### Footer

```css
.footer {
  background-color: var(--color-background-alt);
  padding: var(--spacing-lg) 0;
  margin-top: var(--spacing-xxl);
}

.footer-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
}

.footer-links {
  display: flex;
  gap: var(--spacing-md);
}

.footer-link {
  color: var(--color-text-light);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-copyright {
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-md);
}
```

- Keep the footer simple with minimal content
- Include links to help documentation and about page
- Stack footer items on mobile screens
- Add appropriate spacing between footer sections

## Form Elements

### File Upload Area

```css
.file-upload {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xl);
  text-align: center;
  transition: border-color 0.3s ease, background-color 0.3s ease;
  cursor: pointer;
  margin-bottom: var(--spacing-lg);
}

.file-upload:hover,
.file-upload:focus-within {
  border-color: var(--color-primary-light);
  background-color: rgba(52, 152, 219, 0.05);
}

.file-upload.drag-over {
  border-color: var(--color-primary);
  background-color: rgba(52, 152, 219, 0.1);
}

.file-upload-icon {
  font-size: 2.5rem;
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
}

.file-upload-text {
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-md);
}

.file-upload-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

/* Hide the actual file input */
.file-upload-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

- Use dashed border and icon to clearly indicate the upload area
- Provide visual feedback for hover, focus, and drag states
- Include clear instructions for both drag-and-drop and click-to-browse
- Display helpful file type and size limits in the hint text
- Ensure keyboard accessibility for the hidden file input

### Input Controls

```css
.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.form-control {
  display: block;
  width: 100%;
  padding: var(--input-padding);
  font-size: var(--font-size-md);
  line-height: var(--line-height-base);
  color: var(--color-text);
  background-color: var(--color-background);
  border: var(--border-width-thin) solid var(--border-color);
  border-radius: var(--border-radius-md);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
  border-color: var(--color-primary);
  outline: 0;
  box-shadow: var(--focus-ring);
}

.form-check {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.form-check-input {
  margin-right: var(--spacing-sm);
}

.form-check-label {
  font-weight: var(--font-weight-normal);
}

.form-hint {
  display: block;
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}
```

- Maintain consistent styling across all form elements
- Provide clear labels for all form controls
- Include helpful hint text for additional context
- Ensure strong focus states for accessibility
- Implement proper spacing between form elements

### Buttons

```css
.btn {
  display: inline-block;
  font-weight: var(--font-weight-medium);
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: var(--button-padding);
  font-size: var(--font-size-md);
  line-height: var(--line-height-base);
  border-radius: var(--border-radius-md);
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out,
              border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
}

.btn:focus {
  outline: 0;
  box-shadow: var(--focus-ring);
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Button variants */
.btn-primary {
  color: white;
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-primary:hover,
.btn-primary:focus {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.btn-secondary {
  color: white;
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
}

.btn-outline-primary {
  color: var(--color-primary);
  background-color: transparent;
  border-color: var(--color-primary);
}

.btn-outline-primary:hover,
.btn-outline-primary:focus {
  color: white;
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-danger {
  color: white;
  background-color: var(--color-error);
  border-color: var(--color-error);
}
```

| Button Type | Usage |
| ----------- | ----- |
| Primary | Main actions (Convert, Download) |
| Secondary | Positive secondary actions (Proceed) |
| Outline | Less emphasized actions (Cancel, Back) |
| Danger | Destructive actions (Remove file) |

- Use `.btn-primary` for the main conversion action
- Use `.btn-outline-primary` for cancel or back actions
- Only use `.btn-danger` for destructive actions
- Maintain appropriate spacing between grouped buttons
- Keep button text concise and action-oriented (e.g., "Convert to Excel" not "Click here to convert")

### Validation Feedback

```css
/* Valid state */
.form-control.is-valid {
  border-color: var(--color-success);
  padding-right: calc(1.5em + 0.75rem);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%232ecc71' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px;
}

/* Invalid state */
.form-control.is-invalid {
  border-color: var(--color-error);
  padding-right: calc(1.5em + 0.75rem);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23e74c3c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='6' x2='6' y2='18'%3E%3C/line%3E%3Cline x1='6' y1='6' x2='18' y2='18'%3E%3C/line%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px;
}

.invalid-feedback {
  display: none;
  width: 100%;
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-error);
}

.form-control.is-invalid ~ .invalid-feedback {
  display: block;
}
```

- Provide immediate visual feedback for validation errors
- Use consistent colors for valid and invalid states
- Position feedback messages directly below the relevant input
- Make error messages specific and actionable
- For file uploads, validate both file type and size

## Interactive Components

### Progress Indicators

```css
/* Progress bar */
.progress {
  display: flex;
  height: 0.75rem;
  overflow: hidden;
  font-size: var(--font-size-xs);
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius-full);
}

.progress-bar {
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
  text-align: center;
  white-space: nowrap;
  background-color: var(--color-primary);
  transition: width 0.6s ease;
}

/* Progress label */
.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.progress-status {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.progress-percentage {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

/* Spinner */
.spinner {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  vertical-align: text-bottom;
  border: 0.25em solid var(--color-primary-light);
  border-right-color: var(--color-primary);
  border-radius: 50%;
  animation: spinner 0.75s linear infinite;
}

@keyframes spinner {
  to {
    transform: rotate(360deg);
  }
}
```

- Use progress bars for file conversion process with known stages
- Use spinners for indeterminate loading states
- Always provide textual status along with visual indicators
- Ensure progress indicators have sufficient contrast
- Use appropriate ARIA attributes for accessibility

### Notifications

```css
/* Alert messages */
.alert {
  position: relative;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.alert-info {
  color: #0c5460;
  background-color: #d1ecf1;
  border-color: #bee5eb;
}

.alert-warning {
  color: #856404;
  background-color: #fff3cd;
  border-color: #ffeeba;
}

.alert-error {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.alert-icon {
  margin-right: var(--spacing-sm);
}

.alert-title {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-xs);
}
```

- Use alert messages for important information that should remain visible
- Match alert type to the message content (success, info, warning, error)
- Include an icon to reinforce the message type
- Provide a clear, bold title for the alert
- Keep alert messages concise and actionable

### Tooltips

```css
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip-trigger {
  cursor: help;
  border-bottom: 1px dotted var(--color-text-light);
}

.tooltip-content {
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-text);
  color: white;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  text-align: center;
  white-space: nowrap;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, visibility 0.3s;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: var(--color-text) transparent transparent transparent;
}

.tooltip:hover .tooltip-content,
.tooltip:focus .tooltip-content,
.tooltip:focus-within .tooltip-content {
  opacity: 1;
  visibility: visible;
}
```

- Use tooltips for supplementary information only
- Keep tooltip content concise and helpful
- Ensure tooltips are accessible via keyboard
- Use appropriate ARIA attributes for screen readers
- Don't hide essential information in tooltips

## Error Pages

### Error Types

```css
.error-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-xxl) var(--spacing-md);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

.error-code {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.error-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
}

.error-message {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-lg);
  max-width: 600px;
}
```

| Error Type | Icon Color | Use Case |
| ---------- | ---------- | -------- |
| Not Found | var(--color-info) | File not found, page not found |
| Validation | var(--color-warning) | Invalid JSON, format errors |
| Processing | var(--color-error) | Conversion failure, system error |
| Permission | var(--color-error) | File access errors |

### Error Components

```css
.error-details {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius-md);
  text-align: left;
  width: 100%;
  max-width: 600px;
}

.error-details-title {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.error-code-display {
  font-family: var(--font-family-monospace);
  background-color: var(--color-background-alt);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--spacing-sm);
  overflow-x: auto;
}

.error-location {
  margin-top: var(--spacing-sm);
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
}
```

### Troubleshooting Section

```css
.troubleshooting {
  width: 100%;
  max-width: 600px;
  margin-top: var(--spacing-lg);
  text-align: left;
}

.troubleshooting-title {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
}

.troubleshooting-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.troubleshooting-item {
  padding: var(--spacing-sm) 0;
  padding-left: var(--spacing-xl);
  position: relative;
}

.troubleshooting-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: calc(var(--spacing-sm) + 0.4rem);
  width: 1rem;
  height: 1rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233498db' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='9 18 15 12 9 6'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
}

.try-again-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  width: 100%;
  max-width: 600px;
  text-align: center;
}
```

- Make error pages informative and helpful
- Clearly communicate what went wrong
- Provide specific troubleshooting steps
- Include actions users can take to resolve the issue
- Use appropriate icons and colors to indicate error severity

## Responsive Design

### Breakpoints

```css
/* Mobile first approach */
/* Base styles are for mobile devices */

/* Small devices (landscape phones, 576px and up) */
@media (min-width: 576px) {
  /* sm styles */
}

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) {
  /* md styles */
}

/* Large devices (desktops, 992px and up) */
@media (min-width: 992px) {
  /* lg styles */
}

/* X-Large devices (large desktops, 1200px and up) */
@media (min-width: 1200px) {
  /* xl styles */
}
```

### Mobile Adaptations

```css
/* Base styles (mobile) */
.container {
  padding-left: var(--spacing-md);
  padding-right: var(--spacing-md);
}

.card {
  padding: var(--spacing-md);
}

.header-container {
  flex-direction: column;
  gap: var(--spacing-sm);
}

.nav {
  flex-direction: column;
  width: 100%;
}

.footer-container {
  flex-direction: column;
  gap: var(--spacing-md);
}

/* Tablet and larger */
@media (min-width: 768px) {
  .container {
    padding-left: var(--spacing-lg);
    padding-right: var(--spacing-lg);
  }
  
  .card {
    padding: var(--spacing-lg);
  }
  
  .header-container {
    flex-direction: row;
  }
  
  .nav {
    flex-direction: row;
    width: auto;
  }
  
  .footer-container {
    flex-direction: row;
  }
}
```

### Touch Optimization

```css
/* Increase touch target sizes on mobile */
@media (max-width: 767.98px) {
  .btn {
    padding: calc(var(--spacing-sm) * 1.2) calc(var(--spacing-lg) * 1.2);
    min-height: 44px; /* Minimum touch target size */
  }
  
  .form-control,
  .form-select {
    min-height: 44px;
    padding: calc(var(--spacing-sm) * 1.2) calc(var(--spacing-md) * 1.2);
  }
  
  .nav-link {
    padding: var(--spacing-sm) var(--spacing-md);
    min-height: 44px;
    display: flex;
    align-items: center;
  }
  
  /* Increase spacing between touch targets */
  .form-group {
    margin-bottom: calc(var(--spacing-lg) * 1.2);
  }
}
```

- Use a mobile-first approach to design and development
- Test on multiple device sizes and orientations
- Ensure minimum touch target size of 44px x 44px
- Adjust layout and component sizes appropriately for each screen size
- Simplify complex components on small screens

## Accessibility

### Keyboard Navigation

```css
/* Focus styles */
:focus {
  outline: none;
}

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Skip link for keyboard users */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-sm) var(--spacing-md);
  z-index: 100;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 0;
}
```

- Ensure all interactive elements are keyboard accessible
- Implement visible focus states that are easy to see
- Include a skip-to-content link at the beginning of the page
- Maintain a logical tab order that follows the visual layout
- Test the interface using keyboard navigation only

### Screen Readers

```css
/* Visually hidden elements that are still accessible to screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Extends the .sr-only class to allow the element to be focusable when navigated to via keyboard */
.sr-only-focusable:not(:focus) {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

- Use semantic HTML elements appropriately
- Add ARIA attributes when necessary for complex components
- Provide text alternatives for non-text content
- Ensure form elements have proper labels
- Test with screen readers to verify accessibility

### Focus Indicators

```css
/* High contrast focus indicators */
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
button:focus-visible,
[tabindex]:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
  box-shadow: none; /* Remove default shadow to avoid conflict */
}

/* Ensure focus is visible for all interactive elements */
a:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
}

/* Ensure checkbox and radio button focus states are visible */
.form-check-input:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
}
```

- Make focus indicators clearly visible with high contrast
- Ensure focus indicators have sufficient size and color contrast
- Don't rely solely on color to indicate focus
- Test focus visibility on different backgrounds

### Color Contrast

```css
/* Ensure text has sufficient contrast */
body {
  color: var(--color-text); /* #333333 - high contrast against white background */
}

.text-light {
  color: var(--color-text-light); /* Ensure this meets 4.5:1 contrast ratio */
}

.btn-primary,
.btn-secondary,
.btn-danger {
  color: white; /* Ensure text has good contrast against button backgrounds */
}
```

- Maintain a minimum contrast ratio of 4.5:1 for normal text
- Maintain a minimum contrast ratio of 3:1 for large text
- Don't rely solely on color to convey information
- Test using color contrast analyzers
- Verify readability across different screen sizes

## Dark Mode

### Color Adjustments

```css
/* Light theme (default) */
:root {
  --color-text: #333333;
  --color-text-light: #666666;
  --color-text-lighter: #999999;
  --color-background: #ffffff;
  --color-background-alt: #f8f9fa;
  --color-border: #dddddd;
  /* Other variables remain the same */
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #f8f9fa;
    --color-text-light: #cccccc;
    --color-text-lighter: #999999;
    --color-background: #121212;
    --color-background-alt: #222222;
    --color-border: #444444;
    
    /* Adjust primary colors to be more visible on dark background */
    --color-primary: #61a8e0;
    --color-primary-light: #7fb8e6;
    --color-primary-dark: #3c7fb5;
    
    /* Adjust other colors for dark mode */
    --color-secondary: #42d885;
    --color-secondary-light: #65e29c;
    --color-secondary-dark: #2bb16a;
    
    /* Adjust semantic colors for dark mode */
    --color-success: #42d885;
    --color-info: #61a8e0;
    --color-warning: #f7a832;
    --color-error: #e95e52;
    
    /* Adjust shadows for dark mode */
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  }
}
```

### Implementation

```css
/* Additional dark mode adjustments */
@media (prefers-color-scheme: dark) {
  /* Card adjustments */
  .card {
    background-color: #1e1e1e;
  }
  
  /* Form control adjustments */
  .form-control {
    background-color: #2c2c2c;
    color: var(--color-text);
    border-color: #444444;
  }
  
  /* Alert adjustments */
  .alert-success {
    color: #d4edda;
    background-color: rgba(40, 167, 69, 0.2);
    border-color: rgba(40, 167, 69, 0.3);
  }
  
  .alert-info {
    color: #d1ecf1;
    background-color: rgba(23, 162, 184, 0.2);
    border-color: rgba(23, 162, 184, 0.3);
  }
  
  .alert-warning {
    color: #fff3cd;
    background-color: rgba(255, 193, 7, 0.2);
    border-color: rgba(255, 193, 7, 0.3);
  }
  
  .alert-error {
    color: #f8d7da;
    background-color: rgba(220, 53, 69, 0.2);
    border-color: rgba(220, 53, 69, 0.3);
  }
}
```

- Use CSS variables to simplify theme switching
- Ensure sufficient contrast in both light and dark modes
- Test all components in dark mode for proper appearance
- Use the `prefers-color-scheme` media query for automatic switching
- Consider adding a manual toggle for user preference

## Best Practices

### CSS Organization

```css
/* File structure and organization */

/* 1. Variables and Configuration */
:root {
  /* Colors */
  --color-primary: #3498db;
  /* ...other variables... */
}

/* 2. Base/Reset Styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 3. Typography */
h1, h2, h3, h4, h5, h6 {
  margin-bottom: var(--spacing-md);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

/* 4. Layout Components */
.container { /* ... */ }
.card { /* ... */ }

/* 5. Forms */
.form-group { /* ... */ }
.form-control { /* ... */ }

/* 6. Components */
.progress { /* ... */ }
.alert { /* ... */ }

/* 7. Utilities */
.text-center { text-align: center; }
.mt-1 { margin-top: var(--spacing-xs); }
/* ...other utility classes... */

/* 8. Responsive Adjustments */
@media (min-width: 768px) {
  /* Responsive styles */
}
```

### Class Naming

```css
/* BEM (Block, Element, Modifier) naming convention */

/* Block: standalone component */
.card { /* ... */ }

/* Element: part of a block */
.card__header { /* ... */ }
.card__body { /* ... */ }
.card__footer { /* ... */ }

/* Modifier: different state or version of a block or element */
.card--featured { /* ... */ }
.card__header--centered { /* ... */ }