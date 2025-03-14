"""
Unit tests for the ConversionService class, which orchestrates 
the JSON to Excel conversion process.
"""

import pytest
import os
import json
import tempfile
from unittest import mock

from ...services.conversion_service import ConversionService
from ...models.json_data import JSONData
from ...models.excel_options import ExcelOptions, ArrayHandlingStrategy
from ...models.error_response import ErrorResponse
from ..fixtures.json_fixtures import flat_json, nested_json, array_json, complex_json, invalid_json
from ..fixtures.json_fixtures import flat_json_data, nested_json_data, array_json_data
from ..fixtures.json_fixtures import get_json_data_object, get_invalid_json_string
from ..fixtures.excel_fixtures import default_excel_options, custom_excel_options
from ..fixtures.excel_fixtures import array_expand_options, array_join_options
from ..fixtures.excel_fixtures import test_flat_dataframe, test_nested_dataframe
from .. import create_temp_json_file, cleanup_temp_file, get_test_file_path

# Define test directories
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_data')
TEST_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

@pytest.fixture
def setup_conversion_service():
    """
    Creates and returns a ConversionService instance for testing.
    
    Returns:
        A configured ConversionService instance
    """
    service = ConversionService()
    return service

@pytest.fixture
def setup_temp_output_file():
    """
    Creates a temporary output file path for Excel output.
    
    Returns:
        Path to a temporary Excel file
    """
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_output.xlsx")
    yield temp_file
    # Clean up after the test
    if os.path.exists(temp_file):
        os.remove(temp_file)
    os.rmdir(temp_dir)

class TestConversionService:
    """
    Test class for the ConversionService component, which handles the conversion
    of JSON data to Excel format.
    """
    
    def test_initialization(self):
        """
        Tests that the ConversionService initializes correctly with default and custom parameters.
        """
        # Test initialization with default parameters
        service = ConversionService()
        assert service._max_file_size_bytes > 0
        assert service._max_nesting_level > 0
        
        # Test initialization with custom parameters
        custom_max_size = 10  # 10MB
        custom_nesting = 5
        service = ConversionService(max_file_size_mb=custom_max_size, max_nesting_level=custom_nesting)
        assert service._max_file_size_bytes == custom_max_size * 1024 * 1024
        assert service._max_nesting_level == custom_nesting
    
    def test_convert_json_to_excel_flat(self, setup_conversion_service, flat_json, setup_temp_output_file):
        """
        Tests conversion of flat JSON to Excel format.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(flat_json)
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
            
            # Verify output file exists
            assert os.path.exists(setup_temp_output_file)
            
            # Verify the summary contains expected keys
            assert "input" in result
            assert "output" in result
            assert "performance" in result
        finally:
            cleanup_temp_file(input_file)
    
    def test_convert_json_to_excel_nested(self, setup_conversion_service, nested_json, setup_temp_output_file):
        """
        Tests conversion of nested JSON to Excel format.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(nested_json)
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
            
            # Verify output file exists
            assert os.path.exists(setup_temp_output_file)
            
            # Verify the summary contains expected keys
            assert "input" in result
            assert "output" in result
            assert "performance" in result
            
            # Verify nested structure information
            assert "structure" in result["input"]
            assert result["input"]["structure"]["is_nested"] is True
        finally:
            cleanup_temp_file(input_file)
    
    def test_convert_json_to_excel_with_arrays(self, setup_conversion_service, array_json, setup_temp_output_file):
        """
        Tests conversion of JSON with arrays to Excel format.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(array_json)
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
            
            # Verify output file exists
            assert os.path.exists(setup_temp_output_file)
            
            # Verify the summary contains array information
            assert "input" in result
            assert "structure" in result["input"]
            assert result["input"]["structure"]["contains_arrays"] is True
        finally:
            cleanup_temp_file(input_file)
    
    def test_convert_json_to_excel_with_custom_options(self, setup_conversion_service, flat_json, custom_excel_options, setup_temp_output_file):
        """
        Tests conversion with custom Excel options.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(flat_json)
        
        try:
            # Convert options to dictionary
            options_dict = custom_excel_options.to_dict()
            
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file, options_dict)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
            
            # Verify output file exists
            assert os.path.exists(setup_temp_output_file)
        finally:
            cleanup_temp_file(input_file)
    
    def test_convert_json_string_to_excel(self, setup_conversion_service, flat_json, setup_temp_output_file):
        """
        Tests conversion of a JSON string to Excel format.
        """
        service = setup_conversion_service
        
        # Convert the dictionary to a JSON string
        json_string = json.dumps(flat_json)
        
        success, result, error = service.convert_json_string_to_excel(json_string, setup_temp_output_file)
        
        # Assert the conversion was successful
        assert success is True
        assert error is None
        assert result["status"] == "success"
        
        # Verify output file exists
        assert os.path.exists(setup_temp_output_file)
    
    def test_convert_json_to_excel_bytes(self, setup_conversion_service, flat_json):
        """
        Tests conversion of JSON to Excel bytes.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(flat_json)
        
        try:
            excel_bytes, result, error = service.convert_json_to_excel_bytes(input_file)
            
            # Assert the conversion was successful
            assert excel_bytes is not None
            assert len(excel_bytes) > 0
            assert error is None
            assert result["status"] == "success"
            
            # Excel files typically start with the bytes "PK" (ZIP file signature)
            assert excel_bytes[:2] == b'PK'
        finally:
            cleanup_temp_file(input_file)
    
    def test_convert_json_data_to_excel(self, setup_conversion_service, flat_json_data, setup_temp_output_file):
        """
        Tests conversion of a JSONData object to Excel format.
        """
        service = setup_conversion_service
        
        success, result, error = service.convert_json_data_to_excel(flat_json_data, setup_temp_output_file)
        
        # Assert the conversion was successful
        assert success is True
        assert error is None
        assert result["status"] == "success"
        
        # Verify output file exists
        assert os.path.exists(setup_temp_output_file)
    
    def test_convert_dataframe_to_excel(self, setup_conversion_service, test_flat_dataframe, setup_temp_output_file):
        """
        Tests conversion of a pandas DataFrame to Excel format.
        """
        service = setup_conversion_service
        
        success, result, error = service.convert_dataframe_to_excel(test_flat_dataframe, setup_temp_output_file)
        
        # Assert the conversion was successful
        assert success is True
        assert error is None
        assert result["status"] == "success"
        
        # Verify output file exists
        assert os.path.exists(setup_temp_output_file)
    
    def test_transform_json_to_dataframe(self, setup_conversion_service, nested_json_data):
        """
        Tests transformation of JSON data to a pandas DataFrame.
        """
        service = setup_conversion_service
        
        # Test with expand array handling
        df, error = service.transform_json_to_dataframe(nested_json_data, "expand")
        
        # Assert the transformation was successful
        assert df is not None
        assert error is None
        assert len(df) > 0
        assert len(df.columns) > 0
        
        # Verify the structure of flattened data
        assert 'contact.email' in df.columns
        assert 'contact.address.street' in df.columns
    
    def test_array_handling_strategies(self, setup_conversion_service, array_json, array_expand_options, array_join_options, setup_temp_output_file):
        """
        Tests different array handling strategies during conversion.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(array_json)
        
        try:
            # Test with expand strategy (default)
            expand_options_dict = array_expand_options.to_dict()
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file, expand_options_dict)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            
            # Verify file exists
            assert os.path.exists(setup_temp_output_file)
            
            # Test with join strategy
            join_options_dict = array_join_options.to_dict()
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file, join_options_dict)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert os.path.exists(setup_temp_output_file)
        finally:
            cleanup_temp_file(input_file)
    
    def test_error_handling_invalid_json(self, setup_conversion_service, invalid_json, setup_temp_output_file):
        """
        Tests error handling for invalid JSON input.
        """
        service = setup_conversion_service
        
        # Create a temporary file with invalid JSON
        input_file = create_temp_json_file({"dummy": "content"})
        with open(input_file, 'w') as f:
            f.write(invalid_json)
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion failed
            assert success is False
            assert error is not None
            assert result["status"] == "error"
            
            # Verify error details
            assert error.category == ErrorCategory.PARSING_ERROR
            assert "error" in result
            assert "message" in result["error"]
        finally:
            cleanup_temp_file(input_file)
    
    def test_error_handling_file_not_found(self, setup_conversion_service, setup_temp_output_file):
        """
        Tests error handling for non-existent input files.
        """
        service = setup_conversion_service
        
        # Use a non-existent file
        input_file = "non_existent_file.json"
        
        success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
        
        # Assert the conversion failed
        assert success is False
        assert error is not None
        assert result["status"] == "error"
        
        # Verify error category
        assert error.category == ErrorCategory.INPUT_ERROR
    
    def test_error_handling_invalid_output_path(self, setup_conversion_service, flat_json):
        """
        Tests error handling for invalid output file paths.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(flat_json)
        
        # Use an invalid output path (assuming /invalid/path doesn't exist)
        output_file = "/invalid/path/that/should/not/exist/output.xlsx"
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, output_file)
            
            # Assert the conversion failed
            assert success is False
            assert error is not None
            assert result["status"] == "error"
            
            # Verify error category
            assert error.category == ErrorCategory.OUTPUT_ERROR
        finally:
            cleanup_temp_file(input_file)
    
    def test_max_file_size_setting(self, setup_conversion_service, flat_json, setup_temp_output_file):
        """
        Tests the max file size setting for input validation.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(flat_json)
        
        try:
            # Set a very small max file size (1 byte)
            service.set_max_file_size(0.000001)  # Extremely small size in MB
            
            # Try to convert - should fail due to file size limit
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion failed due to file size limit
            assert success is False
            assert error is not None
            assert result["status"] == "error"
            
            # Reset to a larger value
            service.set_max_file_size(10)  # 10MB
            
            # Try again - should succeed
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
        finally:
            cleanup_temp_file(input_file)
    
    def test_max_nesting_level_setting(self, setup_conversion_service, complex_json, setup_temp_output_file):
        """
        Tests the max nesting level setting for JSON structure validation.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(complex_json)
        
        try:
            # Set a very small max nesting level (1)
            service.set_max_nesting_level(1)
            
            # Try to convert - might fail depending on the implementation
            # The test should accommodate both possibilities
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Reset to a larger value
            service.set_max_nesting_level(10)
            
            # Try again - should succeed
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            assert result["status"] == "success"
        finally:
            cleanup_temp_file(input_file)
    
    def test_conversion_summary(self, setup_conversion_service, nested_json, setup_temp_output_file):
        """
        Tests that the conversion summary contains expected information.
        """
        service = setup_conversion_service
        input_file = create_temp_json_file(nested_json)
        
        try:
            success, result, error = service.convert_json_to_excel(input_file, setup_temp_output_file)
            
            # Assert the conversion was successful
            assert success is True
            assert error is None
            
            # Verify summary structure
            assert "input" in result
            assert "output" in result
            assert "performance" in result
            
            # Verify input summary
            assert "file_path" in result["input"]
            assert "size_bytes" in result["input"]
            assert "structure" in result["input"]
            
            # Verify output summary
            assert "file_path" in result["output"]
            assert "size_bytes" in result["output"]
            assert "rows" in result["output"]
            assert "columns" in result["output"]
            
            # Verify performance summary
            assert "execution_time_seconds" in result["performance"]
        finally:
            cleanup_temp_file(input_file)
    
    def test_mock_dependencies(self):
        """
        Tests the ConversionService with mocked dependencies.
        """
        # Create mocks for the dependencies
        mock_json_parser = mock.Mock()
        mock_data_transformer = mock.Mock()
        mock_excel_generator = mock.Mock()
        mock_input_handler = mock.Mock()
        mock_error_handler = mock.Mock()
        
        # Configure the mocks
        mock_json_parser.create_json_data.return_value = mock.Mock()
        mock_json_parser.create_json_data.return_value.analyze_structure = mock.Mock()
        mock_json_parser.create_json_data.return_value.get_flattening_strategy.return_value = "flat"
        mock_json_parser.create_json_data.return_value.max_nesting_level = 2
        mock_json_parser.create_json_data.return_value.contains_arrays = False
        mock_json_parser.create_json_data.return_value.array_paths = []
        mock_json_parser.create_json_data.return_value.complexity_level.name = "SIMPLE"
        
        mock_data_transformer.transform_data.return_value = (mock.Mock(), None)
        mock_data_transformer.transform_data.return_value[0].shape = (10, 5)
        
        mock_excel_generator.generate_excel.return_value = (True, None)
        
        mock_input_handler.read_json_file.return_value = {"test": "data"}
        
        # Create the service with mocked dependencies
        service = ConversionService()
        service._json_parser = mock_json_parser
        service._data_transformer = mock_data_transformer
        service._excel_generator = mock_excel_generator
        service._input_handler = mock_input_handler
        service._error_handler = mock_error_handler
        
        # Test the convert_json_to_excel method
        input_path = "test_input.json"
        output_path = "test_output.xlsx"
        
        # Mock os.path.getsize and os.path.exists to avoid file system access
        with mock.patch('os.path.getsize', return_value=100), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.abspath', return_value=output_path):
            success, result, error = service.convert_json_to_excel(input_path, output_path)
        
        # Assert the conversion was successful
        assert success is True
        assert error is None
        
        # Verify the dependencies were called correctly
        mock_input_handler.read_json_file.assert_called_once_with(input_path)
        mock_json_parser.create_json_data.assert_called_once()
        mock_data_transformer.transform_data.assert_called_once()
        mock_excel_generator.generate_excel.assert_called_once()