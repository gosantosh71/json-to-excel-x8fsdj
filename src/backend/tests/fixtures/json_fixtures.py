"""
Provides test fixtures for JSON data to be used in unit and integration tests for the JSON to
Excel conversion tool. This module contains predefined JSON structures, utility functions for
loading JSON files, and methods for creating JSONData objects for testing purposes.
"""

import json  # v: built-in
import os  # v: built-in
import pytest  # v: 7.3.0+
from pathlib import Path  # v: built-in

from ...models.json_data import JSONData
from ...adapters.file_system_adapter import FileSystemAdapter

# Global constants
FIXTURES_DIR = Path(__file__).parent
SAMPLE_DATA_DIR = FIXTURES_DIR / 'sample_data'
file_system_adapter = FileSystemAdapter()


def load_json_file(filename: str) -> dict:
    """
    Loads a JSON file from the sample data directory.

    Args:
        filename: The name of the JSON file to load

    Returns:
        The parsed JSON content
    """
    file_path = SAMPLE_DATA_DIR / filename
    return file_system_adapter.read_json(file_path)


def get_json_data_object(filename: str) -> JSONData:
    """
    Creates a JSONData object from a JSON file in the sample data directory.

    Args:
        filename: The name of the JSON file to load

    Returns:
        A JSONData object containing the parsed JSON content with structure analysis
    """
    file_path = SAMPLE_DATA_DIR / filename
    json_content = file_system_adapter.read_json(file_path)
    file_size = file_system_adapter.get_file_size(file_path)
    
    json_data = JSONData(
        content=json_content,
        source_path=str(file_path),
        size_bytes=file_size
    )
    json_data.analyze_structure()
    return json_data


def get_invalid_json_string() -> str:
    """
    Returns an invalid JSON string for testing error handling.

    Returns:
        A malformed JSON string
    """
    return '{"name": "Test", "value": 123, "missing": }'


@pytest.fixture
def flat_json():
    """
    Fixture providing a flat JSON structure for testing simple conversion scenarios.
    
    Returns:
        A dictionary with a flat JSON structure (no nesting, no arrays)
    """
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "active": True,
        "score": 85.5,
        "registered_date": "2023-01-15",
        "notes": "Regular customer"
    }


@pytest.fixture
def nested_json():
    """
    Fixture providing a nested JSON structure for testing nested object flattening.
    
    Returns:
        A dictionary with a nested JSON structure
    """
    return {
        "id": 1,
        "name": "John Doe",
        "contact": {
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "USA"
            }
        },
        "membership": {
            "status": "active",
            "level": "premium",
            "joined_date": "2022-03-15"
        }
    }


@pytest.fixture
def array_json():
    """
    Fixture providing a JSON structure with arrays for testing array normalization.
    
    Returns:
        A dictionary with JSON containing arrays
    """
    return {
        "id": 1,
        "name": "John Doe",
        "tags": ["customer", "premium", "active"],
        "scores": [85, 92, 78, 90],
        "contact_methods": ["email", "phone", "mail"],
        "orders": [
            {"id": 101, "product": "Laptop", "price": 999.99},
            {"id": 102, "product": "Mouse", "price": 24.99},
            {"id": 103, "product": "Keyboard", "price": 49.99}
        ]
    }


@pytest.fixture
def complex_json():
    """
    Fixture providing a complex JSON structure with deep nesting and arrays for
    testing advanced scenarios.
    
    Returns:
        A dictionary with a complex JSON structure
    """
    return {
        "id": 1,
        "name": "John Doe",
        "profile": {
            "personal": {
                "age": 30,
                "gender": "male",
                "contact": {
                    "email": "john.doe@example.com",
                    "phone": "555-1234",
                    "address": {
                        "street": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zip": "12345",
                        "coordinates": {
                            "latitude": 37.7749,
                            "longitude": -122.4194
                        }
                    }
                }
            },
            "professional": {
                "title": "Software Engineer",
                "department": "Engineering",
                "skills": ["Python", "JavaScript", "SQL", "Docker"],
                "projects": [
                    {
                        "name": "Project A",
                        "role": "Lead Developer",
                        "technologies": ["Python", "Flask", "PostgreSQL"],
                        "milestones": [
                            {"name": "Planning", "completed": True},
                            {"name": "Development", "completed": True},
                            {"name": "Testing", "completed": False}
                        ]
                    },
                    {
                        "name": "Project B",
                        "role": "Backend Developer",
                        "technologies": ["Python", "Django", "MongoDB"],
                        "milestones": [
                            {"name": "Planning", "completed": True},
                            {"name": "Development", "completed": False}
                        ]
                    }
                ]
            }
        },
        "orders": [
            {
                "id": 101,
                "date": "2023-01-15",
                "items": [
                    {"product_id": 1001, "name": "Laptop", "price": 999.99, "quantity": 1},
                    {"product_id": 1002, "name": "Mouse", "price": 24.99, "quantity": 2}
                ],
                "shipping": {
                    "method": "Express",
                    "cost": 15.99,
                    "tracking": "EX123456789"
                }
            },
            {
                "id": 102,
                "date": "2023-02-20",
                "items": [
                    {"product_id": 1003, "name": "Monitor", "price": 249.99, "quantity": 1},
                    {"product_id": 1004, "name": "Keyboard", "price": 49.99, "quantity": 1},
                    {"product_id": 1005, "name": "Headphones", "price": 79.99, "quantity": 1}
                ],
                "shipping": {
                    "method": "Standard",
                    "cost": 9.99,
                    "tracking": "ST987654321"
                }
            }
        ],
        "statistics": {
            "visits": [10, 15, 8, 12, 20, 25, 18],
            "purchases": [1, 0, 1, 0, 2, 1, 1],
            "spending": {
                "2023-01": 1040.97,
                "2023-02": 389.96
            }
        }
    }


@pytest.fixture
def invalid_json():
    """
    Fixture providing an invalid JSON string for testing error handling.
    
    Returns:
        A malformed JSON string that should cause parsing errors
    """
    return get_invalid_json_string()


@pytest.fixture
def flat_json_data(flat_json):
    """
    Fixture providing a JSONData object with flat JSON structure.
    
    Returns:
        A JSONData object containing flat JSON
    """
    json_data = JSONData(
        content=flat_json,
        source_path="memory/flat.json",
        size_bytes=len(json.dumps(flat_json))
    )
    json_data.analyze_structure()
    return json_data


@pytest.fixture
def nested_json_data(nested_json):
    """
    Fixture providing a JSONData object with nested JSON structure.
    
    Returns:
        A JSONData object containing nested JSON
    """
    json_data = JSONData(
        content=nested_json,
        source_path="memory/nested.json",
        size_bytes=len(json.dumps(nested_json))
    )
    json_data.analyze_structure()
    return json_data


@pytest.fixture
def array_json_data(array_json):
    """
    Fixture providing a JSONData object with JSON containing arrays.
    
    Returns:
        A JSONData object containing JSON with arrays
    """
    json_data = JSONData(
        content=array_json,
        source_path="memory/array.json",
        size_bytes=len(json.dumps(array_json))
    )
    json_data.analyze_structure()
    return json_data


@pytest.fixture
def complex_json_data(complex_json):
    """
    Fixture providing a JSONData object with complex JSON structure.
    
    Returns:
        A JSONData object containing complex JSON
    """
    json_data = JSONData(
        content=complex_json,
        source_path="memory/complex.json",
        size_bytes=len(json.dumps(complex_json))
    )
    json_data.analyze_structure()
    return json_data