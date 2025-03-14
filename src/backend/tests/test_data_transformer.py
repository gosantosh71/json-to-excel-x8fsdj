"""
Unit tests for the DataTransformer class and related functions in the data_transformer module.

This module contains tests for the transformation of JSON data into tabular format
suitable for Excel conversion, including handling of flat JSON, nested structures, and arrays.
"""

import pytest  # v: 7.3.0+
import pandas as pd  # v: 1.5.0+
import numpy as np  # v: 1.20.0+

from ..data_transformer import (
    DataTransformer,
    flatten_json,
    normalize_json_to_dataframe,
    handle_arrays
)
from ..models.json_data import JSONData
from ..models.excel_options import ArrayHandlingStrategy
from ..exceptions import TransformationException
from .fixtures.json_fixtures import (
    flat_json,
    nested_json,
    array_json,
    complex_json,
    invalid_json,
    get_json_data_object
)


def test_flatten_json_flat_structure(flat_json):
    """
    Tests that flatten_json correctly handles flat JSON structures without nesting.
    """
    result = flatten_json(flat_json)
    
    # For a flat structure, the output should be the same as the input
    assert result == flat_json
    assert len(result) == len(flat_json)
    
    # Check that all keys are preserved
    for key in flat_json:
        assert key in result
        assert result[key] == flat_json[key]


def test_flatten_json_nested_structure(nested_json):
    """
    Tests that flatten_json correctly flattens nested JSON structures using dot notation.
    """
    result = flatten_json(nested_json)
    
    # Check that top-level keys are preserved
    assert "id" in result
    assert "name" in result
    assert result["id"] == nested_json["id"]
    assert result["name"] == nested_json["name"]
    
    # Check that nested keys are flattened with dot notation
    assert "contact.email" in result
    assert "contact.phone" in result
    assert "contact.address.street" in result
    assert "contact.address.city" in result
    assert "contact.address.state" in result
    assert "contact.address.zip" in result
    assert "contact.address.country" in result
    
    # Verify values are preserved
    assert result["contact.email"] == nested_json["contact"]["email"]
    assert result["contact.address.city"] == nested_json["contact"]["address"]["city"]
    
    # Check membership section
    assert "membership.status" in result
    assert "membership.level" in result
    assert "membership.joined_date" in result
    assert result["membership.status"] == nested_json["membership"]["status"]
    
    # The flattened dict should have more keys than the original due to expansion
    # Original: id, name, contact, membership (4 keys)
    # Flattened should have: id, name, contact.email, contact.phone, contact.address.street, etc.
    original_count = 4  # top-level keys in nested_json
    nested_count = 3 + 5 + 3  # contact (3 keys), address (5 keys), membership (3 keys)
    expected_count = original_count + nested_count - 2  # -2 for the container dicts (contact, membership)
    assert len(result) == expected_count


def test_flatten_json_with_arrays(array_json):
    """
    Tests that flatten_json correctly handles arrays in JSON structures.
    """
    result = flatten_json(array_json)
    
    # Check that top-level keys are preserved
    assert "id" in result
    assert "name" in result
    
    # Check that arrays are preserved (not expanded)
    assert "tags" in result
    assert "scores" in result
    assert "orders" in result
    
    # Verify array values
    assert isinstance(result["tags"], list)
    assert isinstance(result["scores"], list)
    assert isinstance(result["orders"], list)
    assert result["tags"] == array_json["tags"]
    assert result["scores"] == array_json["scores"]
    assert result["orders"] == array_json["orders"]
    
    # The flattened structure shouldn't change the array elements
    assert len(result["orders"]) == len(array_json["orders"])


def test_flatten_json_complex_structure(complex_json):
    """
    Tests that flatten_json correctly handles complex JSON with deep nesting and arrays.
    """
    result = flatten_json(complex_json)
    
    # Check top-level keys
    assert "id" in result
    assert "name" in result
    
    # Check deeply nested paths
    assert "profile.personal.age" in result
    assert "profile.personal.contact.email" in result
    assert "profile.personal.contact.address.coordinates.latitude" in result
    
    # Check arrays in nested structures
    assert "profile.professional.skills" in result
    assert "profile.professional.projects" in result
    assert isinstance(result["profile.professional.skills"], list)
    
    # Verify some deeply nested values
    assert result["profile.personal.age"] == complex_json["profile"]["personal"]["age"]
    assert result["profile.personal.contact.address.coordinates.latitude"] == complex_json["profile"]["personal"]["contact"]["address"]["coordinates"]["latitude"]
    
    # Check nested arrays
    assert isinstance(result["profile.professional.projects"], list)
    
    # The order information should be preserved
    assert "orders" in result
    assert isinstance(result["orders"], list)
    assert "statistics.visits" in result
    assert isinstance(result["statistics.visits"], list)


def test_normalize_json_to_dataframe_flat(flat_json):
    """
    Tests that normalize_json_to_dataframe correctly converts flat JSON to DataFrame.
    """
    df = normalize_json_to_dataframe(flat_json)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    
    # Check dimensions
    assert len(df) == 1  # Should have 1 row
    assert len(df.columns) == len(flat_json)  # Should have same number of columns as keys
    
    # Check column names match JSON keys
    for key in flat_json:
        assert key in df.columns
    
    # Check values
    for key, value in flat_json.items():
        assert df.iloc[0][key] == value


def test_normalize_json_to_dataframe_nested(nested_json):
    """
    Tests that normalize_json_to_dataframe correctly converts nested JSON to DataFrame.
    """
    df = normalize_json_to_dataframe(nested_json)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    
    # Check dimensions
    assert len(df) == 1  # Should have 1 row
    
    # Check flattened column names
    assert "id" in df.columns
    assert "name" in df.columns
    assert "contact.email" in df.columns
    assert "contact.address.city" in df.columns
    
    # Check values
    assert df.iloc[0]["id"] == nested_json["id"]
    assert df.iloc[0]["name"] == nested_json["name"]
    assert df.iloc[0]["contact.email"] == nested_json["contact"]["email"]
    assert df.iloc[0]["contact.address.city"] == nested_json["contact"]["address"]["city"]


def test_normalize_json_to_dataframe_with_arrays_expand(array_json):
    """
    Tests that normalize_json_to_dataframe correctly expands arrays into multiple rows.
    """
    df = normalize_json_to_dataframe(array_json, array_handling=ArrayHandlingStrategy.EXPAND)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    
    # Check if arrays of objects are expanded
    # For array_json.orders with 3 items, should have 3 rows
    assert len(df) == len(array_json["orders"])
    
    # Check that non-array values are repeated across rows
    assert df["id"].nunique() == 1
    assert df["name"].nunique() == 1
    
    # Check expanded columns from orders
    assert "orders.id" in df.columns
    assert "orders.product" in df.columns
    assert "orders.price" in df.columns
    
    # Verify values from orders array
    for i, order in enumerate(array_json["orders"]):
        assert df.iloc[i]["orders.id"] == order["id"]
        assert df.iloc[i]["orders.product"] == order["product"]
        assert df.iloc[i]["orders.price"] == order["price"]


def test_normalize_json_to_dataframe_with_arrays_join(array_json):
    """
    Tests that normalize_json_to_dataframe correctly joins arrays into comma-separated strings.
    """
    df = normalize_json_to_dataframe(array_json, array_handling=ArrayHandlingStrategy.JOIN)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    
    # Check dimensions
    assert len(df) == 1  # Should have 1 row for JOIN strategy
    
    # Check that primitive arrays are joined
    assert "tags" in df.columns
    assert isinstance(df.iloc[0]["tags"], str)
    assert "customer, premium, active" == df.iloc[0]["tags"]
    
    # Check that numeric arrays are joined
    assert "scores" in df.columns
    assert isinstance(df.iloc[0]["scores"], str)
    assert "85, 92, 78, 90" == df.iloc[0]["scores"]
    
    # Check object arrays
    # Note: For complex objects, the string representation might vary depending on implementation
    # The test should verify that it's a string, but the exact format may need adjustments
    assert "orders" in df.columns
    assert isinstance(df.iloc[0]["orders"], str)


def test_handle_arrays_expand():
    """
    Tests that handle_arrays correctly processes arrays with the 'expand' strategy.
    """
    # Test with array of primitives
    primitive_array = [1, 2, 3, 4, 5]
    result = handle_arrays(primitive_array, ArrayHandlingStrategy.EXPAND)
    
    # For EXPAND strategy, arrays should be returned as-is
    assert result == primitive_array
    
    # Test with array of objects
    object_array = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    result = handle_arrays(object_array, ArrayHandlingStrategy.EXPAND)
    
    # Should also be returned as-is
    assert result == object_array


def test_handle_arrays_join():
    """
    Tests that handle_arrays correctly processes arrays with the 'join' strategy.
    """
    # Test with array of primitives
    primitive_array = [1, 2, 3, 4, 5]
    result = handle_arrays(primitive_array, ArrayHandlingStrategy.JOIN)
    
    # For JOIN strategy, array should be converted to a comma-separated string
    assert isinstance(result, str)
    assert result == "1, 2, 3, 4, 5"
    
    # Test with array of strings
    string_array = ["apple", "banana", "cherry"]
    result = handle_arrays(string_array, ArrayHandlingStrategy.JOIN)
    
    assert isinstance(result, str)
    assert result == "apple, banana, cherry"


def test_handle_arrays_non_array():
    """
    Tests that handle_arrays correctly handles non-array values.
    """
    # Test with string
    string_value = "test"
    result = handle_arrays(string_value, ArrayHandlingStrategy.EXPAND)
    assert result == string_value
    
    # Test with number
    number_value = 123
    result = handle_arrays(number_value, ArrayHandlingStrategy.JOIN)
    assert result == number_value
    
    # Test with boolean
    bool_value = True
    result = handle_arrays(bool_value, ArrayHandlingStrategy.EXPAND)
    assert result == bool_value
    
    # Test with None
    none_value = None
    result = handle_arrays(none_value, ArrayHandlingStrategy.JOIN)
    assert result == none_value
    
    # Test with dictionary
    dict_value = {"key": "value"}
    result = handle_arrays(dict_value, ArrayHandlingStrategy.EXPAND)
    assert result == dict_value


class TestDataTransformer:
    """
    Test class for the DataTransformer class, focusing on its methods for transforming
    JSON data into tabular format.
    """
    
    def test_init_default_array_handling(self):
        """
        Tests that DataTransformer initializes with the default array handling strategy.
        """
        transformer = DataTransformer()
        assert transformer.get_array_handling() == ArrayHandlingStrategy.EXPAND
    
    def test_init_custom_array_handling(self):
        """
        Tests that DataTransformer initializes with a custom array handling strategy.
        """
        transformer = DataTransformer(array_handling=ArrayHandlingStrategy.JOIN)
        assert transformer.get_array_handling() == ArrayHandlingStrategy.JOIN
    
    def test_set_array_handling(self):
        """
        Tests that set_array_handling correctly updates the array handling strategy.
        """
        transformer = DataTransformer()
        
        # Initial strategy should be EXPAND
        assert transformer.get_array_handling() == ArrayHandlingStrategy.EXPAND
        
        # Change to JOIN
        transformer.set_array_handling(ArrayHandlingStrategy.JOIN)
        assert transformer.get_array_handling() == ArrayHandlingStrategy.JOIN
        
        # Change back to EXPAND
        transformer.set_array_handling(ArrayHandlingStrategy.EXPAND)
        assert transformer.get_array_handling() == ArrayHandlingStrategy.EXPAND
    
    def test_set_array_handling_invalid(self):
        """
        Tests that set_array_handling raises an exception for invalid strategies.
        """
        transformer = DataTransformer()
        
        # Try to set an invalid strategy
        with pytest.raises(ValueError) as exc_info:
            transformer.set_array_handling("invalid_strategy")
        
        # Check that the error message is helpful
        assert "Invalid array handling strategy" in str(exc_info.value)
        assert "EXPAND" in str(exc_info.value)
        assert "JOIN" in str(exc_info.value)
    
    def test_transform_flat_json(self, flat_json):
        """
        Tests that transform correctly processes flat JSON data.
        """
        # Create a JSONData object for testing
        json_data = JSONData(
            content=flat_json,
            source_path="test_path",
            size_bytes=len(str(flat_json))
        )
        json_data.analyze_structure()
        
        # Create transformer and transform the data
        transformer = DataTransformer()
        result = transformer.transform(json_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check dimensions
        assert len(result) == 1  # Should have 1 row
        assert len(result.columns) == len(flat_json)  # Should have same number of columns as keys
        
        # Check values
        for key, value in flat_json.items():
            assert result.iloc[0][key] == value
    
    def test_transform_nested_json(self, nested_json):
        """
        Tests that transform correctly processes nested JSON data.
        """
        # Create a JSONData object for testing
        json_data = JSONData(
            content=nested_json,
            source_path="test_path",
            size_bytes=len(str(nested_json))
        )
        json_data.analyze_structure()
        
        # Create transformer and transform the data
        transformer = DataTransformer()
        result = transformer.transform(json_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check dimensions
        assert len(result) == 1  # Should have 1 row
        
        # Check flattened column names
        assert "id" in result.columns
        assert "name" in result.columns
        assert "contact.email" in result.columns
        assert "contact.address.city" in result.columns
        
        # Check values
        assert result.iloc[0]["id"] == nested_json["id"]
        assert result.iloc[0]["name"] == nested_json["name"]
        assert result.iloc[0]["contact.email"] == nested_json["contact"]["email"]
        assert result.iloc[0]["contact.address.city"] == nested_json["contact"]["address"]["city"]
    
    def test_transform_array_json_expand(self, array_json):
        """
        Tests that transform correctly processes JSON with arrays using the 'expand' strategy.
        """
        # Create a JSONData object for testing
        json_data = JSONData(
            content=array_json,
            source_path="test_path",
            size_bytes=len(str(array_json))
        )
        json_data.analyze_structure()
        
        # Create transformer with EXPAND strategy
        transformer = DataTransformer(array_handling=ArrayHandlingStrategy.EXPAND)
        result = transformer.transform(json_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check array expansion
        assert len(result) == len(array_json["orders"])  # Should have one row per order
        
        # Check that non-array values are repeated across rows
        assert result["id"].nunique() == 1
        assert result["name"].nunique() == 1
        
        # Check expanded columns from orders
        assert "orders.id" in result.columns
        assert "orders.product" in result.columns
        assert "orders.price" in result.columns
        
        # Verify values from orders array
        for i, order in enumerate(array_json["orders"]):
            assert result.iloc[i]["orders.id"] == order["id"]
            assert result.iloc[i]["orders.product"] == order["product"]
            assert result.iloc[i]["orders.price"] == order["price"]
    
    def test_transform_array_json_join(self, array_json):
        """
        Tests that transform correctly processes JSON with arrays using the 'join' strategy.
        """
        # Create a JSONData object for testing
        json_data = JSONData(
            content=array_json,
            source_path="test_path",
            size_bytes=len(str(array_json))
        )
        json_data.analyze_structure()
        
        # Create transformer with JOIN strategy
        transformer = DataTransformer(array_handling=ArrayHandlingStrategy.JOIN)
        result = transformer.transform(json_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check dimensions
        assert len(result) == 1  # Should have 1 row for JOIN strategy
        
        # Check that primitive arrays are joined
        assert "tags" in result.columns
        assert isinstance(result.iloc[0]["tags"], str)
        assert "customer, premium, active" == result.iloc[0]["tags"]
        
        # Check that numeric arrays are joined
        assert "scores" in result.columns
        assert isinstance(result.iloc[0]["scores"], str)
        assert "85, 92, 78, 90" == result.iloc[0]["scores"]
        
        # Check complex arrays
        assert "orders" in result.columns
        assert isinstance(result.iloc[0]["orders"], str)
    
    def test_transform_complex_json(self, complex_json):
        """
        Tests that transform correctly processes complex JSON with deep nesting and arrays.
        """
        # Create a JSONData object for testing
        json_data = JSONData(
            content=complex_json,
            source_path="test_path",
            size_bytes=len(str(complex_json))
        )
        json_data.analyze_structure()
        
        # Create transformer
        transformer = DataTransformer()
        result = transformer.transform(json_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check for deeply nested columns
        assert "profile.personal.age" in result.columns
        assert "profile.personal.contact.email" in result.columns
        assert "profile.personal.contact.address.coordinates.latitude" in result.columns
        
        # Check values
        assert result.iloc[0]["id"] == complex_json["id"]
        assert result.iloc[0]["name"] == complex_json["name"]
        assert result.iloc[0]["profile.personal.age"] == complex_json["profile"]["personal"]["age"]
        assert result.iloc[0]["profile.personal.contact.address.coordinates.latitude"] == complex_json["profile"]["personal"]["contact"]["address"]["coordinates"]["latitude"]
        
        # Since there are arrays in this JSON, check that expansion worked correctly
        # The exact number of rows will depend on the specific EXPAND implementation
        # But we should have at least as many rows as top-level arrays
        assert len(result) > 0
    
    def test_transform_error_handling(self, mocker):
        """
        Tests that transform properly handles errors during transformation.
        """
        # Create a valid JSONData object
        json_data = JSONData(
            content={"id": 1, "name": "Test"},
            source_path="test_path",
            size_bytes=100
        )
        json_data.analyze_structure()
        
        # Mock the internal transformation method to raise an exception
        mock_transform = mocker.patch.object(
            DataTransformer, 
            'transform_data', 
            side_effect=TransformationException("Test error", "E999")
        )
        
        # Create transformer
        transformer = DataTransformer()
        
        # Transform should return a tuple (None, ErrorResponse)
        result = transformer.transform(json_data)
        
        # Verify the result
        assert result[0] is None
        assert result[1] is not None
        assert "Test error" in result[1].message
    
    def test_detect_transformation_strategy(self, flat_json, nested_json, array_json):
        """
        Tests that the transformer correctly detects the appropriate transformation
        strategy based on JSON structure.
        """
        # Create JSONData objects for different JSON structures
        flat_data = JSONData(
            content=flat_json,
            source_path="flat.json",
            size_bytes=100
        )
        flat_data.analyze_structure()
        
        nested_data = JSONData(
            content=nested_json,
            source_path="nested.json",
            size_bytes=200
        )
        nested_data.analyze_structure()
        
        array_data = JSONData(
            content=array_json,
            source_path="array.json",
            size_bytes=300
        )
        array_data.analyze_structure()
        
        # Create transformer
        transformer = DataTransformer()
        
        # Check strategy detection
        assert flat_data.get_flattening_strategy() == 'flat'
        assert nested_data.get_flattening_strategy() == 'nested'
        assert array_data.get_flattening_strategy() == 'array'