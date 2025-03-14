#!/usr/bin/env python
"""
Setup script for the web interface component of the JSON to Excel Conversion Tool.

This script defines package metadata, dependencies, and installation configuration
to enable proper distribution and installation of the web interface module as a
Python package.
"""

import os  # v: built-in
import io  # v: built-in
import re  # v: built-in
from setuptools import setup, find_packages  # v: >=67.0.0

# Get the absolute path of the directory containing this file
here = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(here, 'README.md')
REQUIREMENTS_PATH = os.path.join(here, 'requirements.txt')

# Try to import constants directly, fall back to regex extraction if that fails
try:
    # This works in development environment
    from constants import WEB_CONSTANTS
except ImportError:
    # This works during installation when the package isn't installed yet
    def extract_constants():
        """Extract constants from constants.py without importing the module."""
        constants_path = os.path.join(here, 'constants.py')
        version = '0.0.0'
        app_name = 'JSON to Excel Conversion Tool - Web Interface'
        
        if os.path.exists(constants_path):
            with open(constants_path, 'r') as f:
                content = f.read()
            
            # Extract VERSION
            version_match = re.search(r'VERSION\s*=\s*[\'"](.+?)[\'"]', content)
            if version_match:
                version = version_match.group(1)
            
            # Extract APP_NAME
            app_name_match = re.search(r'APP_NAME\s*=\s*[\'"](.+?)[\'"]', content)
            if app_name_match:
                app_name = app_name_match.group(1)
        
        return {
            'VERSION': version,
            'APP_NAME': app_name
        }
    
    WEB_CONSTANTS = extract_constants()


def read_requirements(file_path):
    """
    Reads the requirements.txt file and returns a list of dependencies.
    
    Args:
        file_path (str): Path to the requirements.txt file
        
    Returns:
        list: List of package requirements strings
    """
    requirements = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements


def read_readme(file_path):
    """
    Reads the README.md file and returns its content as a string.
    
    Args:
        file_path (str): Path to the README file
        
    Returns:
        str: Content of the README file
    """
    if os.path.exists(file_path):
        with io.open(file_path, encoding='utf-8') as f:
            return f.read()
    return ''


setup(
    name='json-to-excel-converter-web',
    version=WEB_CONSTANTS['VERSION'],
    description='Web interface component for converting JSON data files into structured Excel spreadsheets',
    long_description=read_readme(README_PATH),
    long_description_content_type='text/markdown',
    author='Your Organization',
    author_email='contact@example.com',
    url='https://github.com/organization/json-to-excel-converter',
    packages=find_packages(exclude=['tests', 'tests.*', 'scripts']),
    include_package_data=True,
    package_data={
        'json_to_excel_web': ['templates/**/*.html', 'static/**/*', 'config/*.json'],
    },
    install_requires=read_requirements(REQUIREMENTS_PATH),
    extras_require={
        'dev': [
            'pytest>=7.3.0',
            'pytest-flask>=1.2.0',
            'black>=23.1.0',
            'flake8>=6.0.0',
        ],
        'prod': [
            'gunicorn>=20.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'json2excel-web=json_to_excel_web.run:main',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business',
        'Topic :: Utilities',
        'Framework :: Flask',
    ],
    keywords='json, excel, conversion, web, flask, data',
)