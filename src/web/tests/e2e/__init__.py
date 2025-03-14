"""
Initialization module for the end-to-end tests package of the web interface component of the JSON to Excel Conversion Tool.
This file provides common imports, constants, utility functions, and fixtures specifically for E2E testing of the web interface,
enabling comprehensive browser-based workflow testing.
"""

import os  # v: built-in - For file path operations in E2E tests
import pytest  # v: 7.3.0+ - For test fixtures and test configuration
import selenium  # v: 4.0.0+ - For browser automation in end-to-end tests
from selenium import webdriver  # v: 4.0.0+ - For controlling browser instances in tests
from selenium.webdriver.common.by import By  # v: 4.0.0+ - For locating elements in the web page
from selenium.webdriver.support.ui import WebDriverWait  # v: 4.0.0+ - For waiting for elements to appear in the page
from selenium.webdriver.support import expected_conditions  # v: 4.0.0+ - For defining conditions to wait for in tests
import time  # v: built-in - For adding delays in tests when needed
import json  # v: built-in - For parsing JSON responses from the API

from ..conftest import app, client  # src/web/tests/conftest.py - Fixture for creating a Flask test application
from ..conftest import client  # src/web/tests/conftest.py - Fixture for creating a Flask test client
from ..fixtures.file_fixtures import create_test_json_file_storage  # src/web/tests/fixtures/file_fixtures.py - Fixture for creating test JSON file storage objects
from ..fixtures.file_fixtures import setup_test_upload_folder  # src/web/tests/fixtures/file_fixtures.py - Fixture for setting up test upload folders
from ..fixtures.job_fixtures import setup_test_output_folder  # src/web/tests/fixtures/job_fixtures.py - Fixture for setting up test output folders

E2E_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT_DIR = os.path.abspath(os.path.join(E2E_TESTS_DIR, '..', '..', '..'))
WAIT_TIMEOUT = 10
BASE_URL = "http://localhost:5000"


@pytest.fixture
def setup_webdriver():
    """
    Sets up a Selenium WebDriver instance for browser testing.

    Returns:
        webdriver.Chrome: A configured Chrome WebDriver instance
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(WAIT_TIMEOUT)  # Set implicit wait timeout

    yield driver  # Provide the WebDriver instance for test use

    driver.quit()  # Quit the WebDriver after tests complete


def wait_for_element(driver: webdriver.Chrome, by: By, value: str, timeout: int = WAIT_TIMEOUT):
    """
    Helper function to wait for an element to be visible on the page.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        by (By): The method to locate the element (e.g., By.ID, By.XPATH).
        value (str): The value to use for locating the element.
        timeout (int): The maximum time to wait in seconds.

    Returns:
        WebElement: The found web element
    """
    wait = WebDriverWait(driver, timeout)
    element = wait.until(expected_conditions.visibility_of_element_located((by, value)))
    return element


def wait_for_page_load(driver: webdriver.Chrome, expected_title: str = None, timeout: int = WAIT_TIMEOUT):
    """
    Helper function to wait for a page to fully load.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        expected_title (str): The expected title of the page.
        timeout (int): The maximum time to wait in seconds.

    Returns:
        bool: True if the page loaded successfully
    """
    wait = WebDriverWait(driver, timeout)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    if expected_title:
        wait.until(expected_conditions.title_contains(expected_title))
    return True


def upload_file(driver: webdriver.Chrome, file_path: str):
    """
    Helper function to upload a file in the browser.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        file_path (str): The path to the file to upload.
    """
    file_input = driver.find_element(By.ID, "json_file")
    file_input.send_keys(file_path)
    upload_button = driver.find_element(By.ID, "upload_button")
    upload_button.click()
    wait_for_page_load(driver)


def verify_excel_download(driver: webdriver.Chrome, download_dir: str, timeout: int = WAIT_TIMEOUT):
    """
    Helper function to verify that an Excel file was downloaded successfully.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        download_dir (str): The directory where the file should be downloaded.
        timeout (int): The maximum time to wait in seconds.

    Returns:
        str: Path to the downloaded Excel file if successful, None otherwise
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        for filename in os.listdir(download_dir):
            if filename.endswith(".xlsx"):
                return os.path.join(download_dir, filename)
        time.sleep(0.5)
    return None


@pytest.fixture
def setup_e2e_test_environment():
    """
    Sets up a test environment for E2E testing with temporary directories.

    Returns:
        dict: Dictionary containing paths to test directories and files
    """
    temp_dir = setup_test_upload_folder()
    upload_dir = os.path.join(temp_dir, "uploads")
    download_dir = os.path.join(temp_dir, "downloads")
    screenshots_dir = os.path.join(temp_dir, "screenshots")

    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    })

    test_env = {
        "temp_dir": temp_dir,
        "upload_dir": upload_dir,
        "download_dir": download_dir,
        "screenshots_dir": screenshots_dir,
        "chrome_options": chrome_options
    }

    yield test_env

    # Cleanup the temporary directory after the test
    # shutil.rmtree(temp_dir)