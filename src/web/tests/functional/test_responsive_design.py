"""
Implements functional tests for responsive design aspects of the JSON to Excel Conversion Tool web interface.
These tests verify that the web interface properly adapts to different screen sizes, device orientations,
and maintains usability across various devices from mobile phones to desktop computers.
"""

import pytest  # v: 7.3.0+
from selenium import webdriver  # v: 4.9.0+
from selenium.webdriver.common.by import By  # v: 4.9.0+
from selenium.webdriver.support.ui import WebDriverWait  # v: 4.9.0+
from selenium.webdriver.support import expected_conditions as EC  # v: 4.9.0+
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # v: 4.9.0+
import time  # v: built-in
from unittest.mock import patch, MagicMock  # v: built-in

from ..fixtures.file_fixtures import (
    setup_test_upload_folder,
    create_test_file_storage,
    create_test_json_file_storage
)

# Define standard device sizes for testing responsive design
DEVICE_SIZES = [
    {'name': 'mobile', 'width': 375, 'height': 667},  # iPhone 8
    {'name': 'tablet', 'width': 768, 'height': 1024},  # iPad
    {'name': 'desktop', 'width': 1366, 'height': 768}  # Standard laptop
]

# Define device orientations
ORIENTATIONS = [
    {'name': 'portrait', 'width_multiplier': 1, 'height_multiplier': 1.7},
    {'name': 'landscape', 'width_multiplier': 1.7, 'height_multiplier': 1}
]

# Define standard responsive breakpoints
BREAKPOINTS = {
    'xs': 0,    # Extra small devices
    'sm': 576,  # Small devices
    'md': 768,  # Medium devices
    'lg': 992,  # Large devices
    'xl': 1200  # Extra large devices
}


def setup_browser_test(width, height):
    """
    Helper function to set up browser automation for tests.
    
    Args:
        width: Width of the browser window
        height: Height of the browser window
        
    Returns:
        Selenium WebDriver instance
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width, height)
    driver.implicitly_wait(10)
    
    return driver


def verify_element_visibility(driver, selector):
    """
    Helper function to verify element visibility and positioning.
    
    Args:
        driver: Selenium WebDriver instance
        selector: CSS selector for the element to check
        
    Returns:
        True if element is properly visible and positioned
    """
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        
        # Check if element is displayed
        if not element.is_displayed():
            return False
        
        # Check if element is within viewport
        viewport_width = driver.execute_script("return window.innerWidth")
        viewport_height = driver.execute_script("return window.innerHeight")
        
        element_location = element.location
        element_size = element.size
        
        # Element should be within viewport
        if (element_location['x'] < 0 or 
            element_location['y'] < 0 or 
            element_location['x'] + element_size['width'] > viewport_width or
            element_location['y'] > viewport_height):
            return False
        
        # Check if element is not overlapped (simplified check)
        is_clickable = driver.execute_script(
            """
            var elem = arguments[0];
            var rect = elem.getBoundingClientRect();
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var elem2 = document.elementFromPoint(cx, cy);
            return elem.contains(elem2) || elem2.contains(elem) || elem2 === elem;
            """, 
            element
        )
        
        return is_clickable
    except NoSuchElementException:
        return False


def verify_touch_target_size(driver, selector):
    """
    Helper function to verify that interactive elements have sufficient touch target size.
    
    Args:
        driver: Selenium WebDriver instance
        selector: CSS selector for the element to check
        
    Returns:
        True if element has sufficient touch target size
    """
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        size = element.size
        
        # Check if both width and height are at least 44px (recommended minimum touch target size)
        return size['width'] >= 44 and size['height'] >= 44
    except NoSuchElementException:
        return False


def test_responsive_layout_mobile():
    """
    Tests that the web interface layout properly adapts to mobile screen sizes.
    """
    # Set up test with mobile dimensions
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify that the navigation is in mobile mode (hamburger menu)
        hamburger_visible = verify_element_visibility(driver, ".navbar-toggler")
        assert hamburger_visible, "Hamburger menu should be visible on mobile"
        
        # Verify mobile navigation is collapsed by default
        nav_collapsed = not driver.find_element(By.CSS_SELECTOR, ".navbar-collapse").is_displayed()
        assert nav_collapsed, "Navigation menu should be collapsed on mobile by default"
        
        # Verify form elements are properly sized for mobile
        form_container = driver.find_element(By.CSS_SELECTOR, "form")
        container_width = form_container.size['width']
        assert container_width <= (DEVICE_SIZES[0]['width'] - 30), "Form container should fit mobile screen"
        
        # Verify upload area is usable on mobile
        upload_area = driver.find_element(By.CSS_SELECTOR, ".upload-area")
        assert verify_element_visibility(driver, ".upload-area"), "Upload area should be visible on mobile"
        assert upload_area.size['width'] <= (DEVICE_SIZES[0]['width'] - 30), "Upload area should fit mobile screen"
        
        # Verify buttons have appropriate touch target size
        assert verify_touch_target_size(driver, "button[type='submit']"), "Submit button should have adequate touch target size"
        
        # Verify text is readable (no horizontal overflow)
        page_content = driver.find_element(By.CSS_SELECTOR, "body")
        assert page_content.size['width'] <= driver.execute_script("return window.innerWidth"), "No horizontal scrolling should be required"
        
    finally:
        driver.quit()


def test_responsive_layout_tablet():
    """
    Tests that the web interface layout properly adapts to tablet screen sizes.
    """
    # Set up test with tablet dimensions
    driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify navigation is appropriately displayed for tablet
        # On tablets, we might have either expanded nav or hamburger depending on design
        nav_elements = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-item")
        if len(nav_elements) > 0:
            # If navigation is expanded, verify it's properly displayed
            for nav_element in nav_elements:
                assert verify_element_visibility(driver, f"#{nav_element.get_attribute('id')}"), "Navigation elements should be visible on tablet"
        else:
            # If navigation is collapsed, verify hamburger menu
            assert verify_element_visibility(driver, ".navbar-toggler"), "Hamburger menu should be visible if nav is collapsed on tablet"
        
        # Verify form elements are properly sized for tablet
        form_container = driver.find_element(By.CSS_SELECTOR, "form")
        container_width = form_container.size['width']
        assert container_width <= (DEVICE_SIZES[1]['width'] - 40), "Form container should fit tablet screen"
        
        # Verify form layout uses tablet space efficiently
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input_parent = file_input.find_element(By.XPATH, "./..")  # Get parent element
        parent_width = file_input_parent.size['width']
        assert parent_width >= (DEVICE_SIZES[1]['width'] * 0.6), "File input container should use tablet width efficiently"
        
        # Verify form controls are properly sized
        options_container = driver.find_element(By.CSS_SELECTOR, ".form-options")
        options_width = options_container.size['width']
        assert options_width >= (DEVICE_SIZES[1]['width'] * 0.5), "Options container should use tablet width efficiently"
        
    finally:
        driver.quit()


def test_responsive_layout_desktop():
    """
    Tests that the web interface layout properly adapts to desktop screen sizes.
    """
    # Set up test with desktop dimensions
    driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify navigation is fully displayed on desktop
        nav_container = driver.find_element(By.CSS_SELECTOR, ".navbar-nav")
        assert nav_container.is_displayed(), "Navigation should be fully displayed on desktop"
        
        nav_elements = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-item")
        for nav_element in nav_elements:
            assert nav_element.is_displayed(), "All navigation elements should be visible on desktop"
        
        # Verify form makes good use of desktop space
        form_container = driver.find_element(By.CSS_SELECTOR, "form")
        container_width = form_container.size['width']
        
        # Form should be appropriately sized (not too narrow, not full width)
        assert container_width >= 500, "Form should have minimum width on desktop"
        assert container_width <= (DEVICE_SIZES[2]['width'] * 0.8), "Form should not be excessively wide on desktop"
        
        # Verify upload area utilizes desktop space properly
        upload_area = driver.find_element(By.CSS_SELECTOR, ".upload-area")
        assert upload_area.size['width'] >= 400, "Upload area should have adequate width on desktop"
        
        # Verify options are well-laid out
        options_elements = driver.find_elements(By.CSS_SELECTOR, ".form-group")
        for option in options_elements:
            assert option.is_displayed(), "All option elements should be visible on desktop"
            
        # Check for desktop-specific layout features (might be multi-column layout)
        layout_columns = driver.find_elements(By.CSS_SELECTOR, ".row .col, .row .col-md")
        if len(layout_columns) > 1:
            # If multi-column layout is used, verify columns are displayed side by side
            first_col = layout_columns[0]
            second_col = layout_columns[1]
            assert first_col.location['y'] == second_col.location['y'], "Columns should be side by side on desktop"
        
    finally:
        driver.quit()


def test_device_orientation_changes():
    """
    Tests that the web interface adapts properly when device orientation changes.
    """
    # Start with portrait orientation (mobile)
    portrait_width = DEVICE_SIZES[0]['width']
    portrait_height = DEVICE_SIZES[0]['height']
    driver = setup_browser_test(portrait_width, portrait_height)
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify layout in portrait orientation
        assert verify_element_visibility(driver, "form"), "Form should be visible in portrait orientation"
        assert verify_element_visibility(driver, ".upload-area"), "Upload area should be visible in portrait orientation"
        
        form_height_portrait = driver.find_element(By.CSS_SELECTOR, "form").size['height']
        
        # Switch to landscape orientation (swap width and height)
        driver.set_window_size(portrait_height, portrait_width)
        time.sleep(1)  # Allow time for layout to adjust
        
        # Verify layout adapts to landscape orientation
        assert verify_element_visibility(driver, "form"), "Form should remain visible in landscape orientation"
        assert verify_element_visibility(driver, ".upload-area"), "Upload area should remain visible in landscape orientation"
        
        form_height_landscape = driver.find_element(By.CSS_SELECTOR, "form").size['height']
        
        # Form height should be different in different orientations
        assert form_height_portrait != form_height_landscape, "Form layout should adapt to orientation change"
        
        # Verify critical elements remain accessible
        assert verify_element_visibility(driver, "button[type='submit']"), "Submit button should be visible in landscape orientation"
        
        # Verify no horizontal scrolling required in either orientation
        body_width = driver.find_element(By.CSS_SELECTOR, "body").size['width']
        viewport_width = driver.execute_script("return window.innerWidth")
        assert body_width <= viewport_width, "No horizontal scrolling should be required in landscape orientation"
        
    finally:
        driver.quit()


def test_responsive_form_elements(setup_test_upload_folder):
    """
    Tests that form elements adapt properly to different screen sizes.
    
    Args:
        setup_test_upload_folder: Pytest fixture that sets up the test upload folder
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify form elements on mobile
        form = driver.find_element(By.CSS_SELECTOR, "form")
        form_groups = form.find_elements(By.CSS_SELECTOR, ".form-group")
        
        # Form groups should stack vertically on mobile
        for i in range(1, len(form_groups)):
            assert form_groups[i].location['y'] > form_groups[i-1].location['y'], "Form groups should stack vertically on mobile"
        
        # Input fields should take full width
        file_input_container = driver.find_element(By.CSS_SELECTOR, ".custom-file, .form-file")
        file_input_width = file_input_container.size['width']
        form_width = form.size['width']
        assert file_input_width >= (form_width * 0.9), "File input should use full form width on mobile"
        
        # Labels should be positioned above inputs
        label = driver.find_element(By.CSS_SELECTOR, "label[for='sheet-name']")
        input_field = driver.find_element(By.CSS_SELECTOR, "input#sheet-name")
        assert label.location['y'] < input_field.location['y'], "Labels should be above inputs on mobile"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # On tablet, form may have a different layout
        form = driver.find_element(By.CSS_SELECTOR, "form")
        form_width = form.size['width']
        
        # Input fields should have appropriate width (not taking full width but not too narrow)
        input_field = driver.find_element(By.CSS_SELECTOR, "input#sheet-name")
        input_width = input_field.size['width']
        assert input_width >= 200, "Input fields should have minimum width on tablet"
        assert input_width <= (form_width * 0.8), "Input fields should not be excessively wide on tablet"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # On desktop, form layout may be optimized
        form = driver.find_element(By.CSS_SELECTOR, "form")
        
        # Check for possible horizontal layout of form elements on desktop
        form_groups = form.find_elements(By.CSS_SELECTOR, ".form-group")
        horizontal_layout = False
        
        for i in range(1, len(form_groups)):
            # If any form groups are side by side, we have horizontal layout
            if form_groups[i].location['y'] == form_groups[i-1].location['y']:
                horizontal_layout = True
                break
        
        # Either layout is fine, but elements should be properly aligned
        if horizontal_layout:
            # Verify elements in horizontal layout are properly aligned
            for i in range(1, len(form_groups)):
                if form_groups[i].location['y'] == form_groups[i-1].location['y']:
                    assert form_groups[i].location['x'] > form_groups[i-1].location['x'], "Horizontal form groups should be properly spaced"
        else:
            # Verify vertical layout is properly centered
            form_rect = form.rect
            viewport_width = driver.execute_script("return window.innerWidth")
            assert form_rect['x'] >= (viewport_width * 0.1), "Form should be appropriately centered on desktop"
            
    finally:
        driver.quit()


def test_responsive_file_upload_area(setup_test_upload_folder):
    """
    Tests that the file upload area adapts properly to different screen sizes.
    
    Args:
        setup_test_upload_folder: Pytest fixture that sets up the test upload folder
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Verify upload area on mobile
        upload_area = driver.find_element(By.CSS_SELECTOR, ".upload-area")
        
        # Upload area should be properly sized for mobile
        assert upload_area.size['width'] <= (DEVICE_SIZES[0]['width'] - 30), "Upload area should fit mobile screen"
        
        # Check if drag-drop instructions are visible or appropriately adapted for mobile
        dnd_instructions = driver.find_elements(By.CSS_SELECTOR, ".upload-area .drag-drop-text")
        if len(dnd_instructions) > 0:
            # If present, instructions should be visible and appropriately sized
            instruction_text = dnd_instructions[0].text
            assert "tap" in instruction_text.lower() or "click" in instruction_text.lower(), "Upload instructions should be adapted for mobile"
        
        # Browse button should be touch-friendly
        browse_button = driver.find_element(By.CSS_SELECTOR, ".upload-area button, .upload-area .btn")
        assert verify_touch_target_size(driver, ".upload-area button, .upload-area .btn"), "Browse button should have adequate touch target size"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # Verify upload area on tablet
        upload_area = driver.find_element(By.CSS_SELECTOR, ".upload-area")
        
        # Upload area should be properly sized for tablet
        assert upload_area.size['width'] >= 300, "Upload area should have minimum width on tablet"
        assert upload_area.size['width'] <= (DEVICE_SIZES[1]['width'] - 40), "Upload area should fit tablet screen"
        
        # Drag-drop should be more prominent on tablet
        dnd_instructions = driver.find_elements(By.CSS_SELECTOR, ".upload-area .drag-drop-text")
        if len(dnd_instructions) > 0:
            assert dnd_instructions[0].is_displayed(), "Drag and drop instructions should be visible on tablet"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # Verify upload area on desktop
        upload_area = driver.find_element(By.CSS_SELECTOR, ".upload-area")
        
        # Upload area should be properly sized for desktop
        assert upload_area.size['width'] >= 400, "Upload area should have adequate width on desktop"
        
        # Drag-drop should be fully featured on desktop
        dnd_instructions = driver.find_elements(By.CSS_SELECTOR, ".upload-area .drag-drop-text")
        if len(dnd_instructions) > 0:
            instruction_text = dnd_instructions[0].text
            assert "drag" in instruction_text.lower() and "drop" in instruction_text.lower(), "Full drag and drop instructions should be visible on desktop"
            assert dnd_instructions[0].value_of_css_property("font-size") != "0px", "Drag and drop text should be visible on desktop"
            
    finally:
        driver.quit()


def test_responsive_progress_indicators():
    """
    Tests that progress indicators adapt properly to different screen sizes.
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page and mock conversion process
        driver.get("http://localhost:5000/")
        
        # Use JavaScript to simulate showing progress indicators
        driver.execute_script("""
            // Create progress container if it doesn't exist
            if (!document.querySelector('.progress-container')) {
                var container = document.createElement('div');
                container.className = 'progress-container';
                
                var progressBar = document.createElement('div');
                progressBar.className = 'progress';
                progressBar.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 42%" aria-valuenow="42" aria-valuemin="0" aria-valuemax="100"></div>';
                
                var statusText = document.createElement('p');
                statusText.className = 'status-text';
                statusText.textContent = 'Converting JSON to Excel...';
                
                container.appendChild(statusText);
                container.appendChild(progressBar);
                
                document.querySelector('form').appendChild(container);
            }
        """)
        
        # Verify progress indicators on mobile
        progress_bar = driver.find_element(By.CSS_SELECTOR, ".progress")
        status_text = driver.find_element(By.CSS_SELECTOR, ".status-text")
        
        # Progress bar should be properly sized for mobile
        assert progress_bar.size['width'] <= (DEVICE_SIZES[0]['width'] - 40), "Progress bar should fit mobile screen"
        
        # Status text should be readable
        assert status_text.value_of_css_property("font-size") != "0px", "Status text should be visible"
        assert verify_element_visibility(driver, ".status-text"), "Status text should be properly positioned"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing progress indicators
        driver.execute_script("""
            // Create progress container if it doesn't exist
            if (!document.querySelector('.progress-container')) {
                var container = document.createElement('div');
                container.className = 'progress-container';
                
                var progressBar = document.createElement('div');
                progressBar.className = 'progress';
                progressBar.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 42%" aria-valuenow="42" aria-valuemin="0" aria-valuemax="100"></div>';
                
                var statusText = document.createElement('p');
                statusText.className = 'status-text';
                statusText.textContent = 'Converting JSON to Excel...';
                
                container.appendChild(statusText);
                container.appendChild(progressBar);
                
                document.querySelector('form').appendChild(container);
            }
        """)
        
        # Verify progress indicators on tablet
        progress_bar = driver.find_element(By.CSS_SELECTOR, ".progress")
        
        # Progress bar should have adequate width on tablet
        assert progress_bar.size['width'] >= 300, "Progress bar should have minimum width on tablet"
        assert progress_bar.size['width'] <= (DEVICE_SIZES[1]['width'] - 40), "Progress bar should fit tablet screen"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing progress indicators
        driver.execute_script("""
            // Create progress container if it doesn't exist
            if (!document.querySelector('.progress-container')) {
                var container = document.createElement('div');
                container.className = 'progress-container';
                
                var progressBar = document.createElement('div');
                progressBar.className = 'progress';
                progressBar.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 42%" aria-valuenow="42" aria-valuemin="0" aria-valuemax="100"></div>';
                
                var statusText = document.createElement('p');
                statusText.className = 'status-text';
                statusText.textContent = 'Converting JSON to Excel...';
                
                container.appendChild(statusText);
                container.appendChild(progressBar);
                
                document.querySelector('form').appendChild(container);
            }
        """)
        
        # Verify progress indicators on desktop
        progress_container = driver.find_element(By.CSS_SELECTOR, ".progress-container")
        
        # Progress container should be appropriately centered
        container_rect = progress_container.rect
        viewport_width = driver.execute_script("return window.innerWidth")
        assert container_rect['x'] >= (viewport_width * 0.1), "Progress container should be appropriately positioned on desktop"
        
    finally:
        driver.quit()


def test_responsive_results_display():
    """
    Tests that the conversion results display adapts properly to different screen sizes.
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page and mock completed conversion
        driver.get("http://localhost:5000/")
        
        # Use JavaScript to simulate showing results
        driver.execute_script("""
            // Create results container if it doesn't exist
            if (!document.querySelector('.results-container')) {
                var container = document.createElement('div');
                container.className = 'results-container';
                
                var successMessage = document.createElement('div');
                successMessage.className = 'alert alert-success';
                successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Success! Your JSON file has been converted to Excel.';
                
                var fileDetails = document.createElement('div');
                fileDetails.className = 'file-details';
                fileDetails.innerHTML = `
                    <h5>File Details:</h5>
                    <ul>
                        <li>Input: data.json (1.2MB)</li>
                        <li>Output: output.xlsx (856KB)</li>
                        <li>Rows: 150</li>
                        <li>Columns: 12</li>
                        <li>Processing Time: 2.3 seconds</li>
                    </ul>
                `;
                
                var downloadBtn = document.createElement('a');
                downloadBtn.className = 'btn btn-primary btn-lg';
                downloadBtn.href = '#';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Excel File';
                
                var newBtn = document.createElement('button');
                newBtn.className = 'btn btn-outline-secondary mt-3';
                newBtn.innerHTML = 'Convert Another File';
                
                container.appendChild(successMessage);
                container.appendChild(fileDetails);
                container.appendChild(downloadBtn);
                container.appendChild(newBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify results display on mobile
        file_details = driver.find_element(By.CSS_SELECTOR, ".file-details")
        download_btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
        
        # File details should be properly sized for mobile
        assert file_details.size['width'] <= (DEVICE_SIZES[0]['width'] - 30), "File details should fit mobile screen"
        
        # Download button should be touch-friendly
        assert verify_touch_target_size(driver, ".btn-primary"), "Download button should have adequate touch target size"
        
        # Button layout should be vertical on mobile
        convert_another_btn = driver.find_element(By.CSS_SELECTOR, ".btn-outline-secondary")
        assert convert_another_btn.location['y'] > download_btn.location['y'], "Buttons should stack vertically on mobile"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing results
        driver.execute_script("""
            // Create results container if it doesn't exist
            if (!document.querySelector('.results-container')) {
                var container = document.createElement('div');
                container.className = 'results-container';
                
                var successMessage = document.createElement('div');
                successMessage.className = 'alert alert-success';
                successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Success! Your JSON file has been converted to Excel.';
                
                var fileDetails = document.createElement('div');
                fileDetails.className = 'file-details';
                fileDetails.innerHTML = `
                    <h5>File Details:</h5>
                    <ul>
                        <li>Input: data.json (1.2MB)</li>
                        <li>Output: output.xlsx (856KB)</li>
                        <li>Rows: 150</li>
                        <li>Columns: 12</li>
                        <li>Processing Time: 2.3 seconds</li>
                    </ul>
                `;
                
                var downloadBtn = document.createElement('a');
                downloadBtn.className = 'btn btn-primary btn-lg';
                downloadBtn.href = '#';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Excel File';
                
                var newBtn = document.createElement('button');
                newBtn.className = 'btn btn-outline-secondary mt-3';
                newBtn.innerHTML = 'Convert Another File';
                
                container.appendChild(successMessage);
                container.appendChild(fileDetails);
                container.appendChild(downloadBtn);
                container.appendChild(newBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify results display on tablet
        results_container = driver.find_element(By.CSS_SELECTOR, ".results-container")
        
        # Results container should have appropriate width on tablet
        assert results_container.size['width'] >= 400, "Results container should have minimum width on tablet"
        assert results_container.size['width'] <= (DEVICE_SIZES[1]['width'] - 40), "Results container should fit tablet screen"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing results
        driver.execute_script("""
            // Create results container if it doesn't exist
            if (!document.querySelector('.results-container')) {
                var container = document.createElement('div');
                container.className = 'results-container';
                
                var successMessage = document.createElement('div');
                successMessage.className = 'alert alert-success';
                successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Success! Your JSON file has been converted to Excel.';
                
                var fileDetails = document.createElement('div');
                fileDetails.className = 'file-details';
                fileDetails.innerHTML = `
                    <h5>File Details:</h5>
                    <ul>
                        <li>Input: data.json (1.2MB)</li>
                        <li>Output: output.xlsx (856KB)</li>
                        <li>Rows: 150</li>
                        <li>Columns: 12</li>
                        <li>Processing Time: 2.3 seconds</li>
                    </ul>
                `;
                
                var downloadBtn = document.createElement('a');
                downloadBtn.className = 'btn btn-primary btn-lg';
                downloadBtn.href = '#';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Excel File';
                
                var newBtn = document.createElement('button');
                newBtn.className = 'btn btn-outline-secondary mt-3 ml-3';
                newBtn.innerHTML = 'Convert Another File';
                
                container.appendChild(successMessage);
                container.appendChild(fileDetails);
                container.appendChild(downloadBtn);
                container.appendChild(newBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify results display on desktop
        results_container = driver.find_element(By.CSS_SELECTOR, ".results-container")
        
        # Results container should be appropriately centered on desktop
        container_rect = results_container.rect
        viewport_width = driver.execute_script("return window.innerWidth")
        assert container_rect['x'] >= (viewport_width * 0.1), "Results container should be appropriately positioned on desktop"
        
    finally:
        driver.quit()


def test_responsive_error_display():
    """
    Tests that error messages adapt properly to different screen sizes.
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page and mock error display
        driver.get("http://localhost:5000/")
        
        # Use JavaScript to simulate showing an error message
        driver.execute_script("""
            // Create error container if it doesn't exist
            if (!document.querySelector('.error-container')) {
                var container = document.createElement('div');
                container.className = 'error-container';
                
                var errorMessage = document.createElement('div');
                errorMessage.className = 'alert alert-danger';
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error: Invalid JSON format';
                
                var errorDetails = document.createElement('div');
                errorDetails.className = 'error-details';
                errorDetails.innerHTML = `
                    <h5>Details:</h5>
                    <ul>
                        <li>File: malformed.json</li>
                        <li>Error Type: JSON Syntax Error</li>
                        <li>Location: Line 15, Column 22</li>
                        <li>Message: Expected ',' delimiter</li>
                    </ul>
                    
                    <h5>Troubleshooting:</h5>
                    <ul>
                        <li>Check your JSON file for syntax errors</li>
                        <li>Validate your JSON using a JSON validator</li>
                        <li>Ensure the file is properly formatted</li>
                    </ul>
                `;
                
                var tryAgainBtn = document.createElement('button');
                tryAgainBtn.className = 'btn btn-primary';
                tryAgainBtn.innerHTML = 'Try Again';
                
                container.appendChild(errorMessage);
                container.appendChild(errorDetails);
                container.appendChild(tryAgainBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify error display on mobile
        error_container = driver.find_element(By.CSS_SELECTOR, ".error-container")
        error_details = driver.find_element(By.CSS_SELECTOR, ".error-details")
        
        # Error container should be properly sized for mobile
        assert error_container.size['width'] <= (DEVICE_SIZES[0]['width'] - 30), "Error container should fit mobile screen"
        
        # Error details should be readable
        error_details_font_size = error_details.value_of_css_property("font-size")
        assert error_details_font_size != "0px", "Error details should be visible on mobile"
        
        # Try Again button should be touch-friendly
        assert verify_touch_target_size(driver, ".btn-primary"), "Try Again button should have adequate touch target size"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing an error message
        driver.execute_script("""
            // Create error container if it doesn't exist
            if (!document.querySelector('.error-container')) {
                var container = document.createElement('div');
                container.className = 'error-container';
                
                var errorMessage = document.createElement('div');
                errorMessage.className = 'alert alert-danger';
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error: Invalid JSON format';
                
                var errorDetails = document.createElement('div');
                errorDetails.className = 'error-details';
                errorDetails.innerHTML = `
                    <h5>Details:</h5>
                    <ul>
                        <li>File: malformed.json</li>
                        <li>Error Type: JSON Syntax Error</li>
                        <li>Location: Line 15, Column 22</li>
                        <li>Message: Expected ',' delimiter</li>
                    </ul>
                    
                    <h5>Troubleshooting:</h5>
                    <ul>
                        <li>Check your JSON file for syntax errors</li>
                        <li>Validate your JSON using a JSON validator</li>
                        <li>Ensure the file is properly formatted</li>
                    </ul>
                `;
                
                var tryAgainBtn = document.createElement('button');
                tryAgainBtn.className = 'btn btn-primary';
                tryAgainBtn.innerHTML = 'Try Again';
                
                container.appendChild(errorMessage);
                container.appendChild(errorDetails);
                container.appendChild(tryAgainBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify error display on tablet
        error_container = driver.find_element(By.CSS_SELECTOR, ".error-container")
        
        # Error container should have appropriate width on tablet
        assert error_container.size['width'] >= 400, "Error container should have minimum width on tablet"
        assert error_container.size['width'] <= (DEVICE_SIZES[1]['width'] - 40), "Error container should fit tablet screen"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # Simulate showing an error message
        driver.execute_script("""
            // Create error container if it doesn't exist
            if (!document.querySelector('.error-container')) {
                var container = document.createElement('div');
                container.className = 'error-container';
                
                var errorMessage = document.createElement('div');
                errorMessage.className = 'alert alert-danger';
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error: Invalid JSON format';
                
                var errorDetails = document.createElement('div');
                errorDetails.className = 'error-details';
                errorDetails.innerHTML = `
                    <h5>Details:</h5>
                    <ul>
                        <li>File: malformed.json</li>
                        <li>Error Type: JSON Syntax Error</li>
                        <li>Location: Line 15, Column 22</li>
                        <li>Message: Expected ',' delimiter</li>
                    </ul>
                    
                    <h5>Troubleshooting:</h5>
                    <ul>
                        <li>Check your JSON file for syntax errors</li>
                        <li>Validate your JSON using a JSON validator</li>
                        <li>Ensure the file is properly formatted</li>
                    </ul>
                `;
                
                var tryAgainBtn = document.createElement('button');
                tryAgainBtn.className = 'btn btn-primary';
                tryAgainBtn.innerHTML = 'Try Again';
                
                container.appendChild(errorMessage);
                container.appendChild(errorDetails);
                container.appendChild(tryAgainBtn);
                
                document.querySelector('form').style.display = 'none';
                document.querySelector('.container').appendChild(container);
            }
        """)
        
        # Verify error display on desktop
        error_container = driver.find_element(By.CSS_SELECTOR, ".error-container")
        
        # Error container should be appropriately centered on desktop
        container_rect = error_container.rect
        viewport_width = driver.execute_script("return window.innerWidth")
        assert container_rect['x'] >= (viewport_width * 0.1), "Error container should be appropriately positioned on desktop"
        
    finally:
        driver.quit()


def test_touch_friendly_controls():
    """
    Tests that interactive controls are properly sized for touch devices.
    """
    # Set up test with mobile dimensions
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Add mobile touch emulation
        driver.execute_script("navigator.maxTouchPoints = 5;")
        
        # Check all buttons for touch-friendly size
        buttons = driver.find_elements(By.CSS_SELECTOR, "button, .btn, input[type='submit']")
        for button in buttons:
            button_width = button.size['width']
            button_height = button.size['height']
            assert button_width >= 44, f"Button width should be at least 44px for touch, got {button_width}px"
            assert button_height >= 44, f"Button height should be at least 44px for touch, got {button_height}px"
        
        # Check interactive form controls
        form_controls = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'], input[type='radio'], select")
        for control in form_controls:
            control_parent = control.find_element(By.XPATH, "./..")  # Get parent element
            parent_width = control_parent.size['width']
            parent_height = control_parent.size['height']
            assert parent_width >= 44, f"Form control container width should be at least 44px for touch, got {parent_width}px"
            assert parent_height >= 44, f"Form control container height should be at least 44px for touch, got {parent_height}px"
        
        # Check spacing between interactive elements
        interactive_elements = driver.find_elements(By.CSS_SELECTOR, "button, .btn, input, select, a")
        for i in range(len(interactive_elements) - 1):
            element1 = interactive_elements[i]
            element2 = interactive_elements[i + 1]
            
            # Only check adjacent elements that are on the same line
            if element1.is_displayed() and element2.is_displayed() and element1.location['y'] == element2.location['y']:
                # Check horizontal spacing
                element1_right = element1.location['x'] + element1.size['width']
                element2_left = element2.location['x']
                spacing = element2_left - element1_right
                assert spacing >= 8, f"Interactive elements should have adequate spacing, got {spacing}px"
        
        # Check links for touch targets
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        for link in links:
            if link.is_displayed() and link.text.strip():  # Only visible links with text
                link_width = link.size['width']
                link_height = link.size['height']
                assert link_width >= 44 or link_height >= 44, f"Links should have at least one dimension ≥44px for touch, got {link_width}x{link_height}px"
                
        # Verify hover states on touch devices
        # Use JavaScript to check for touch-specific CSS rules
        has_touch_hover_styles = driver.execute_script("""
            var styleSheets = document.styleSheets;
            for (var i = 0; i < styleSheets.length; i++) {
                try {
                    var rules = styleSheets[i].cssRules || styleSheets[i].rules;
                    for (var j = 0; j < rules.length; j++) {
                        if (rules[j].selectorText && 
                            (rules[j].selectorText.includes('@media (hover: none)') || 
                             rules[j].selectorText.includes(':hover'))) {
                            return true;
                        }
                    }
                } catch (e) {
                    // Security error accessing cross-origin stylesheets
                    continue;
                }
            }
            return false;
        """)
        
        assert has_touch_hover_styles, "CSS should include touch-specific hover state management"
        
    finally:
        driver.quit()


def test_font_scaling():
    """
    Tests that text remains readable when browser font size is changed.
    """
    # Set up test with desktop dimensions
    driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
    
    try:
        # Navigate to home page with default font size
        driver.get("http://localhost:5000/")
        
        # Record the initial layout
        initial_layout = {
            "body_height": driver.find_element(By.CSS_SELECTOR, "body").size['height'],
            "form_height": driver.find_element(By.CSS_SELECTOR, "form").size['height'],
            "main_content_width": driver.find_element(By.CSS_SELECTOR, ".container").size['width']
        }
        
        # Increase font size by 50%
        driver.execute_script("document.body.style.fontSize = '150%';")
        time.sleep(1)  # Allow time for layout to adjust
        
        # Check if layout adapts to increased font size
        current_layout = {
            "body_height": driver.find_element(By.CSS_SELECTOR, "body").size['height'],
            "form_height": driver.find_element(By.CSS_SELECTOR, "form").size['height'],
            "main_content_width": driver.find_element(By.CSS_SELECTOR, ".container").size['width']
        }
        
        # Layout should adjust to accommodate larger text
        assert current_layout["form_height"] >= initial_layout["form_height"], "Form should expand to accommodate larger font size"
        
        # Verify elements remain visible and properly positioned
        form_elements = driver.find_elements(By.CSS_SELECTOR, "form .form-group")
        for element in form_elements:
            assert element.is_displayed(), "Form elements should remain visible with increased font size"
            
        # Verify text is not cut off
        # This is a simplified check - a more thorough check would involve measuring text vs container dimensions
        labels = driver.find_elements(By.CSS_SELECTOR, "label")
        for label in labels:
            label_text = label.text
            # Check that container is large enough for text
            label_width = label.size['width']
            # This is a rough estimate - each character is about 8-10px at normal size, 12-15px at 150%
            estimated_text_width = len(label_text) * 15
            assert label_width >= estimated_text_width * 0.8, f"Label container should accommodate text: '{label_text}'"
            
        # Verify critical buttons remain usable
        buttons = driver.find_elements(By.CSS_SELECTOR, "button, .btn")
        for button in buttons:
            if button.is_displayed():
                button_text = button.text.strip()
                if button_text:  # Only check buttons with text
                    button_width = button.size['width']
                    # This is a rough estimate - each character is about 8-10px at normal size, 12-15px at 150%
                    estimated_text_width = len(button_text) * 15
                    assert button_width >= estimated_text_width * 0.9, f"Button should accommodate text: '{button_text}'"
                
                # Verify button is still clickable
                assert verify_element_visibility(driver, f"#{button.get_attribute('id')}") if button.get_attribute('id') else True, "Button should remain clickable with increased font size"
        
    finally:
        driver.quit()


def test_responsive_navigation():
    """
    Tests that the navigation menu adapts properly to different screen sizes.
    """
    # Test on mobile first
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Check for hamburger menu on mobile
        hamburger = driver.find_elements(By.CSS_SELECTOR, ".navbar-toggler")
        if len(hamburger) > 0:
            # Verify hamburger menu is visible
            assert hamburger[0].is_displayed(), "Hamburger menu should be visible on mobile"
            
            # Verify menu is collapsed by default
            navbar_collapse = driver.find_element(By.CSS_SELECTOR, ".navbar-collapse")
            assert not navbar_collapse.is_displayed(), "Navigation menu should be collapsed on mobile by default"
            
            # Click hamburger to expand menu
            hamburger[0].click()
            time.sleep(0.5)  # Allow time for animation
            
            # Verify menu expands
            assert navbar_collapse.is_displayed(), "Navigation menu should expand when hamburger is clicked"
            
            # Verify menu items are properly sized for touch
            menu_items = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-item")
            for item in menu_items:
                assert item.size['height'] >= 44, f"Menu items should have touch-friendly height, got {item.size['height']}px"
        
        driver.quit()
        
        # Test on tablet
        driver = setup_browser_test(DEVICE_SIZES[1]['width'], DEVICE_SIZES[1]['height'])
        driver.get("http://localhost:5000/")
        
        # Check navigation on tablet
        # Depending on design, tablet may show either hamburger or horizontal nav
        navbar = driver.find_element(By.CSS_SELECTOR, ".navbar")
        hamburger = driver.find_elements(By.CSS_SELECTOR, ".navbar-toggler")
        
        if len(hamburger) > 0 and hamburger[0].is_displayed():
            # If using hamburger on tablet, verify it works correctly
            hamburger[0].click()
            time.sleep(0.5)  # Allow time for animation
            
            navbar_collapse = driver.find_element(By.CSS_SELECTOR, ".navbar-collapse")
            assert navbar_collapse.is_displayed(), "Navigation menu should expand when hamburger is clicked on tablet"
        else:
            # If showing horizontal nav, verify it's properly displayed
            nav_items = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-item")
            for item in nav_items:
                assert item.is_displayed(), "Navigation items should be visible on tablet"
                assert item.size['height'] >= 44, f"Menu items should have touch-friendly height, got {item.size['height']}px"
        
        driver.quit()
        
        # Test on desktop
        driver = setup_browser_test(DEVICE_SIZES[2]['width'], DEVICE_SIZES[2]['height'])
        driver.get("http://localhost:5000/")
        
        # Check for full navigation menu on desktop
        hamburger = driver.find_elements(By.CSS_SELECTOR, ".navbar-toggler")
        if len(hamburger) == 0 or not hamburger[0].is_displayed():
            # Navigation should be fully visible on desktop
            navbar_nav = driver.find_element(By.CSS_SELECTOR, ".navbar-nav")
            assert navbar_nav.is_displayed(), "Navigation menu should be fully visible on desktop"
            
            # Verify all nav items are visible
            nav_items = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-item")
            for item in nav_items:
                assert item.is_displayed(), "All navigation items should be visible on desktop"
                
            # Verify nav items are laid out horizontally
            if len(nav_items) >= 2:
                # Check that at least two items are on the same line
                assert nav_items[0].location['y'] == nav_items[1].location['y'], "Navigation items should be laid out horizontally on desktop"
        
    finally:
        driver.quit()


def test_viewport_meta_tag():
    """
    Tests that the viewport meta tag is properly set for responsive design.
    """
    # Set up browser test
    driver = setup_browser_test(DEVICE_SIZES[0]['width'], DEVICE_SIZES[0]['height'])
    
    try:
        # Navigate to home page
        driver.get("http://localhost:5000/")
        
        # Check for viewport meta tag
        viewport_tag = driver.find_elements(By.CSS_SELECTOR, "meta[name='viewport']")
        assert len(viewport_tag) > 0, "Viewport meta tag should be present"
        
        # Check content of viewport meta tag
        viewport_content = viewport_tag[0].get_attribute("content")
        assert "width=device-width" in viewport_content, "Viewport meta tag should include width=device-width"
        assert "initial-scale=1" in viewport_content, "Viewport meta tag should include initial-scale=1"
        
        # Verify page renders correctly on mobile
        body_width = driver.find_element(By.CSS_SELECTOR, "body").size['width']
        viewport_width = driver.execute_script("return window.innerWidth")
        
        assert body_width <= viewport_width, "Page content should fit within viewport width"
        
        # Test user-scalable settings (if specified)
        if "user-scalable=no" in viewport_content or "maximum-scale=1" in viewport_content:
            # Test if zooming is actually prevented (this is an accessibility issue, should be noted)
            # This is a simplistic check since programmatically testing zoom is difficult
            zoom_prevented = "user-scalable=no" in viewport_content or "maximum-scale=1" in viewport_content
            if zoom_prevented:
                print("Warning: Preventing user zoom may cause accessibility issues")
                
    finally:
        driver.quit()