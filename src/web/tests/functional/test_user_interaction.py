import pytest  # v: >=7.0.0 - Testing framework for writing and executing tests
import json  # v: built-in - For parsing JSON responses from the API
import time  # v: built-in - For adding delays in tests when needed
import unittest.mock  # v: built-in - For mocking dependencies in tests
from bs4 import BeautifulSoup  # v: >=4.9.0 - For parsing and analyzing HTML responses
import html  # v: built-in - For HTML entity handling in test assertions

from ..fixtures.conversion_fixtures import create_test_conversion_options, create_test_form_data, mock_conversion_service, create_conversion_result_summary  # src/web/tests/fixtures/conversion_fixtures.py - Fixture for creating test conversion options
from ..fixtures.file_fixtures import create_test_file_storage, create_test_json_file_storage, create_invalid_json_file_storage, setup_test_upload_folder  # src/web/tests/fixtures/file_fixtures.py - Fixture for creating test file storage objects
from ..conftest import mock_file_service, mock_storage_service, mock_job_manager, app, client  # src/web/tests/conftest.py - Fixture for creating a Flask test application

@pytest.mark.functional
def test_form_field_interactions(client, mock_file_service, create_test_json_file_storage):
    """
    Tests user interactions with form fields in the conversion options form.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a GET request to /convert/{file_id} to load the conversion form
    response = client.get(f'/convert/{file_id}')
    assert response.status_code == 200

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the sheet_name field is present with default value
    sheet_name_input = soup.find('input', {'id': 'sheet_name'})
    assert sheet_name_input is not None
    assert sheet_name_input.get('value') == 'Sheet1'

    # Verify that the array_handling radio buttons are present and selectable
    expand_radio = soup.find('input', {'id': 'array_handling-expand'})
    join_radio = soup.find('input', {'id': 'array_handling-join'})
    assert expand_radio is not None
    assert join_radio is not None

    # Verify that the format_headers checkbox is present and can be toggled
    format_headers_checkbox = soup.find('input', {'id': 'format_headers'})
    assert format_headers_checkbox is not None

    # Verify that the auto_column_width checkbox is present and can be toggled
    auto_column_width_checkbox = soup.find('input', {'id': 'auto_column_width'})
    assert auto_column_width_checkbox is not None

    # Verify that the submit button is present and enabled
    submit_button = soup.find('button', {'type': 'submit'})
    assert submit_button is not None
    assert submit_button.get('disabled') is None

@pytest.mark.functional
def test_drag_and_drop_file_upload(client, mock_file_service, create_test_json_file_storage):
    """
    Tests the drag and drop functionality for file uploads.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Send a GET request to / to load the home page
    response = client.get('/')
    assert response.status_code == 200

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the drag-drop zone element is present
    drag_drop_zone = soup.find('div', {'class': 'drop-zone'})
    assert drag_drop_zone is not None

    # Verify that the necessary JavaScript is included for drag-drop functionality
    script_tags = soup.find_all('script')
    drag_drop_script = None
    for script in script_tags:
        if 'drag-drop.js' in script.get('src', ''):
            drag_drop_script = script
            break
    assert drag_drop_script is not None

    # Mock a file drop event by sending a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Verify the response contains a valid file_id
    response_data = json.loads(response.data.decode('utf-8'))
    assert 'file' in response_data
    assert 'file_id' in response_data['file']

@pytest.mark.functional
def test_file_selection_button(client, mock_file_service, create_test_json_file_storage):
    """
    Tests the file selection button functionality for file uploads.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Send a GET request to / to load the home page
    response = client.get('/')
    assert response.status_code == 200

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the file input element is present
    file_input = soup.find('input', {'type': 'file', 'name': 'file'})
    assert file_input is not None

    # Verify that the browse button is present and properly labeled
    browse_button = soup.find('label', {'for': 'file'})
    assert browse_button is not None
    assert browse_button.text.strip() == 'Choose file'

    # Mock a file selection by sending a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Verify the response contains a valid file_id
    response_data = json.loads(response.data.decode('utf-8'))
    assert 'file' in response_data
    assert 'file_id' in response_data['file']

@pytest.mark.functional
def test_form_validation(client, mock_file_service, create_test_json_file_storage):
    """
    Tests form validation for the conversion options form.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a GET request to /convert/{file_id} to load the conversion form
    response = client.get(f'/convert/{file_id}')
    assert response.status_code == 200

    # Submit the form with an empty sheet_name
    response = client.post(f'/convert/{file_id}/process', data={'sheet_name': ''}, follow_redirects=True)
    assert b'Sheet name cannot be empty.' in response.data

    # Submit the form with an invalid array_handling value
    response = client.post(f'/convert/{file_id}/process', data={'array_handling': 'invalid'}, follow_redirects=True)
    assert b"Array handling must be either 'expand' or 'join'." in response.data

    # Submit the form with valid data
    response = client.post(f'/convert/{file_id}/process', data={'sheet_name': 'Valid Sheet', 'array_handling': 'expand'}, follow_redirects=True)
    assert response.status_code == 200

@pytest.mark.functional
def test_progress_indicator(client, mock_file_service, mock_job_manager, create_test_json_file_storage, create_test_form_data):
    """
    Tests the progress indicator during file conversion.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Configure mock_job_manager to simulate a job in progress
    mock_job_manager.create_job.return_value = (unittest.mock.Mock(job_id='test_job_id'), None)
    mock_job_manager.get_job_status.return_value = ({'status': 'processing', 'progress_percentage': 50, 'message': 'Converting JSON to Excel'}, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a POST request to /convert with the file_id and form data
    response = client.post(f'/convert/{file_id}/process', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Redirecting...' in response.data

    # Extract the job_id from the response
    soup = BeautifulSoup(response.data, 'html.parser')
    redirect_url = soup.find('a')['href']
    job_id = redirect_url.split('/')[-1]

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert response.status_code == 200
    assert b'Converting JSON to Excel' in response.data

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the progress bar element is present and properly styled
    progress_bar = soup.find('div', {'class': 'progress-bar'})
    assert progress_bar is not None
    assert progress_bar['style'] == 'width: 50%;'

    # Verify that the progress percentage is displayed
    progress_percentage = soup.find('span', {'class': 'progress-percentage'})
    assert progress_percentage is not None
    assert progress_percentage.text.strip() == '50%'

    # Verify that the current step description is displayed
    current_step = soup.find('p', {'class': 'current-step'})
    assert current_step is not None
    assert current_step.text.strip() == 'Converting JSON to Excel'

@pytest.mark.functional
def test_download_button(client, mock_file_service, mock_storage_service, mock_job_manager, mock_conversion_service, create_test_json_file_storage, create_test_form_data, create_conversion_result_summary):
    """
    Tests the download button functionality after successful conversion.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Create a conversion result summary
    conversion_summary = create_conversion_result_summary()

    # Configure mock services to return successful responses
    mock_file_service.upload_file.return_value = (test_file, None)
    mock_conversion_service.process_conversion_job.return_value = True
    mock_job_manager.create_job.return_value = (unittest.mock.Mock(job_id='test_job_id'), None)
    mock_job_manager.get_job_result.return_value = ({'status': 'completed', 'output_file': 'output.xlsx'}, None)
    mock_storage_service.get_output_file.return_value = ('/path/to/output.xlsx', 'output.xlsx', None)
    mock_job_manager.get_job_status.return_value = ({'status': 'completed', 'progress_percentage': 100, 'message': 'Conversion completed successfully'}, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a POST request to /convert with the file_id and form data
    response = client.post(f'/convert/{file_id}/process', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Redirecting...' in response.data

    # Extract the job_id from the response
    soup = BeautifulSoup(response.data, 'html.parser')
    redirect_url = soup.find('a')['href']
    job_id = redirect_url.split('/')[-1]

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert response.status_code == 200
    assert b'Conversion completed successfully' in response.data

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the download button is present and properly styled
    download_button = soup.find('a', {'class': 'download-button'})
    assert download_button is not None
    assert download_button.text.strip() == 'Download Excel File'

    # Verify that the download button links to the correct URL
    assert download_button['href'] == f'/results/{job_id}'

    # Send a GET request to the download URL
    response = client.get(f'/results/{job_id}')
    assert response.status_code == 200

    # Verify the response has the correct Content-Disposition header
    #assert response.headers['Content-Disposition'] == 'attachment; filename=output.xlsx'

@pytest.mark.functional
def test_error_message_display(client, mock_file_service, mock_job_manager, mock_conversion_service, create_invalid_json_file_storage, create_test_form_data):
    """
    Tests the display of error messages when conversion fails.
    """
    # Create an invalid JSON file storage object
    test_file = create_invalid_json_file_storage()

    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Configure mock_conversion_service to return validation failure
    mock_conversion_service.process_conversion_job.return_value = False
    mock_conversion_service.validate_conversion_input.return_value = (False, {}, {'message': 'Invalid JSON format'})
    mock_job_manager.create_job.return_value = (unittest.mock.Mock(job_id='test_job_id'), None)
    mock_job_manager.get_job_status.return_value = ({'status': 'failed', 'progress_percentage': 0, 'message': 'Conversion failed'}, None)

    # Send a POST request to /upload with the invalid file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a POST request to /convert with the file_id and form data
    response = client.post(f'/convert/{file_id}/process', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Redirecting...' in response.data

    # Extract the job_id from the response
    soup = BeautifulSoup(response.data, 'html.parser')
    redirect_url = soup.find('a')['href']
    job_id = redirect_url.split('/')[-1]

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert response.status_code == 200
    assert b'Conversion failed' in response.data

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the error message is displayed prominently
    error_message = soup.find('div', {'class': 'error-message'})
    assert error_message is not None
    assert 'Invalid JSON format' in error_message.text

    # Verify that the error details are displayed
    error_details = soup.find('div', {'class': 'error-details'})
    assert error_details is not None
    assert 'Invalid JSON format' in error_details.text

    # Verify that the troubleshooting suggestions are displayed
    troubleshooting_suggestions = soup.find('div', {'class': 'troubleshooting-suggestions'})
    assert troubleshooting_suggestions is not None
    assert 'Check that your JSON file has valid syntax' in troubleshooting_suggestions.text

    # Verify that the 'Try Again' button is present and links to the correct URL
    try_again_button = soup.find('a', {'class': 'try-again-button'})
    assert try_again_button is not None
    assert try_again_button['href'] == url_for('web.convert', file_id=file_id)

@pytest.mark.functional
def test_keyboard_navigation(client, mock_file_service, create_test_json_file_storage):
    """
    Tests keyboard navigation through the web interface for accessibility.
    """
    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (create_test_json_file_storage(), None)

    # Send a GET request to / to load the home page
    response = client.get('/')
    assert response.status_code == 200

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that all interactive elements have tabindex attributes
    interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
    for element in interactive_elements:
        assert 'tabindex' in element.attrs, f"Element {element.name} is missing tabindex attribute"

    # Verify that the tab order follows a logical sequence
    # (This requires manual inspection of the HTML structure)

    # Verify that form controls can be activated with keyboard (Enter/Space)
    # (This requires manual testing with a keyboard)

    # Verify that the file upload button is keyboard accessible
    file_upload_button = soup.find('input', {'type': 'file'})
    assert file_upload_button is not None
    assert 'tabindex' in file_upload_button.attrs

    # Verify that the conversion form fields are keyboard accessible
    # (This requires manual testing with a keyboard)

    # Verify that the submit button is keyboard accessible
    submit_button = soup.find('button', {'type': 'submit'})
    assert submit_button is not None
    assert 'tabindex' in submit_button.attrs

@pytest.mark.functional
def test_screen_reader_accessibility(client, mock_file_service, create_test_json_file_storage):
    """
    Tests screen reader accessibility of the web interface.
    """
    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (create_test_json_file_storage(), None)

    # Send a GET request to / to load the home page
    response = client.get('/')
    assert response.status_code == 200

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that all images have alt text
    img_tags = soup.find_all('img')
    for img in img_tags:
        assert 'alt' in img.attrs, f"Image {img['src']} is missing alt text"

    # Verify that form controls have associated labels
    form_controls = soup.find_all(['input', 'select', 'textarea'])
    for control in form_controls:
        if 'id' in control.attrs:
            label = soup.find('label', {'for': control['id']})
            assert label is not None, f"Form control {control['id']} is missing associated label"

    # Verify that ARIA attributes are used appropriately
    # (This requires manual inspection of the HTML structure)

    # Verify that the page has a proper heading structure
    heading_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    assert len(heading_tags) > 0, "Page is missing heading structure"

    # Verify that error messages are associated with their respective form fields
    # (This requires manual inspection of the HTML structure)

    # Verify that dynamic content updates are announced to screen readers
    # (This requires manual testing with a screen reader)

@pytest.mark.functional
def test_convert_another_file_button(client, mock_file_service, mock_storage_service, mock_job_manager, mock_conversion_service, create_test_json_file_storage, create_test_form_data, create_conversion_result_summary):
    """
    Tests the 'Convert Another File' button functionality after successful conversion.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Create a conversion result summary
    conversion_summary = create_conversion_result_summary()

    # Configure mock services to return successful responses
    mock_file_service.upload_file.return_value = (test_file, None)
    mock_conversion_service.process_conversion_job.return_value = True
    mock_job_manager.create_job.return_value = (unittest.mock.Mock(job_id='test_job_id'), None)
    mock_job_manager.get_job_result.return_value = ({'status': 'completed', 'output_file': 'output.xlsx'}, None)
    mock_storage_service.get_output_file.return_value = ('/path/to/output.xlsx', 'output.xlsx', None)
    mock_job_manager.get_job_status.return_value = ({'status': 'completed', 'progress_percentage': 100, 'message': 'Conversion completed successfully'}, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a POST request to /convert with the file_id and form data
    response = client.post(f'/convert/{file_id}/process', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Redirecting...' in response.data

    # Extract the job_id from the response
    soup = BeautifulSoup(response.data, 'html.parser')
    redirect_url = soup.find('a')['href']
    job_id = redirect_url.split('/')[-1]

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert response.status_code == 200
    assert b'Conversion completed successfully' in response.data

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the 'Convert Another File' button is present
    convert_another_button = soup.find('a', {'class': 'convert-another-button'})
    assert convert_another_button is not None

    # Click the 'Convert Another File' button by sending a GET request to its href
    response = client.get(convert_another_button['href'])
    assert response.status_code == 200

    # Verify that the response is the home page with the file upload form
    soup = BeautifulSoup(response.data, 'html.parser')
    file_input = soup.find('input', {'type': 'file', 'name': 'file'})
    assert file_input is not None

@pytest.mark.functional
def test_cancel_conversion_button(client, mock_file_service, mock_job_manager, create_test_json_file_storage, create_test_form_data):
    """
    Tests the cancel button functionality during conversion.
    """
    # Create a test JSON file storage object
    test_file = create_test_json_file_storage()

    # Create test form data for conversion options
    form_data = create_test_form_data()

    # Configure mock_file_service to return a successful upload
    mock_file_service.upload_file.return_value = (test_file, None)

    # Configure mock_job_manager to simulate a job in progress
    mock_job_manager.create_job.return_value = (unittest.mock.Mock(job_id='test_job_id'), None)
    mock_job_manager.get_job_status.return_value = ({'status': 'processing', 'progress_percentage': 50, 'message': 'Converting JSON to Excel'}, None)

    # Send a POST request to /upload with the test file
    response = client.post('/upload', data={'file': (test_file.stream, test_file.filename)})
    assert response.status_code == 200

    # Extract the file_id from the response
    response_data = json.loads(response.data.decode('utf-8'))
    file_id = response_data['file']['file_id']

    # Send a POST request to /convert with the file_id and form data
    response = client.post(f'/convert/{file_id}/process', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Redirecting...' in response.data

    # Extract the job_id from the response
    soup = BeautifulSoup(response.data, 'html.parser')
    redirect_url = soup.find('a')['href']
    job_id = redirect_url.split('/')[-1]

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert response.status_code == 200
    assert b'Converting JSON to Excel' in response.data

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify that the cancel button is present
    cancel_button = soup.find('button', {'class': 'cancel-button'})
    assert cancel_button is not None

    # Click the cancel button by sending a POST request to /cancel/{job_id}
    response = client.post(f'/api/conversion/jobs/{job_id}/cancel')
    assert response.status_code == 200

    # Send a GET request to /status/{job_id} to check job status
    response = client.get(f'/status/{job_id}')
    assert b'Job cancelled by user' in response.data