#!/usr/bin/env python
"""
Setup script for the backend component of the JSON to Excel Conversion Tool.

This file defines package metadata, dependencies, and installation configuration
to enable proper distribution and installation of the backend module.
"""

import os  # v: built-in
from setuptools import setup, find_packages  # v: >=67.0.0

# Try to import constants, with fallbacks in case they're not available
try:
    from constants import VERSION, APP_NAME, AUTHOR
except ImportError:
    # If constants.py import fails or AUTHOR is not defined
    VERSION = "1.0.0"
    APP_NAME = "JSON to Excel Conversion Tool"
    AUTHOR = "JSON to Excel Team"

# Define paths for README and requirements files
README_PATH = os.path.join(os.path.dirname(__file__), 'README.md')
REQUIREMENTS_PATH = os.path.join(os.path.dirname(__file__), 'requirements.txt')

def read_requirements(file_path):
    """
    Reads the requirements.txt file and returns a list of dependencies.
    
    Args:
        file_path (str): Path to the requirements.txt file
        
    Returns:
        list: List of package requirements strings
    """
    if not os.path.exists(file_path):
        # Default minimum requirements if requirements.txt is not found
        return ['pandas>=1.5.0', 'openpyxl>=3.1.0']
    
    with open(file_path, 'r') as f:
        requirements = f.readlines()
    
    # Strip whitespace and filter out empty lines and comments
    requirements = [req.strip() for req in requirements 
                   if req.strip() and not req.strip().startswith('#')]
    
    return requirements

def read_readme(file_path):
    """
    Reads the README.md file and returns its content as a string.
    
    Args:
        file_path (str): Path to the README.md file
        
    Returns:
        str: Content of the README file
    """
    if not os.path.exists(file_path):
        # Default description if README.md is not found
        return "Backend component for converting JSON data files into structured Excel spreadsheets"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

# Setup configuration
setup(
    name='json-to-excel-converter-backend',
    version=VERSION,
    description='Backend component for converting JSON data files into structured Excel spreadsheets',
    long_description=read_readme(README_PATH),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email='contact@example.com',
    url='https://github.com/organization/json-to-excel-converter',
    packages=find_packages(exclude=['tests', 'tests.*', 'scripts']),
    install_requires=read_requirements(REQUIREMENTS_PATH),
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
    ],
    entry_points={
        'console_scripts': [],
    },
)