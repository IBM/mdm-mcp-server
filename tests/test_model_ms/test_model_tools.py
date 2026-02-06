# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for model tools (get_data_model).

This test suite verifies:
1. Tool function behavior with different inputs
2. Exception handling and propagation
3. Service integration
4. Session store integration
5. Format parameter handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from model_ms.model.tools import get_data_model, _get_model_service
from model_ms.model.exceptions import DataModelFetchError, InvalidFormatError
from common.domain.crn_validator import CRNValidationError


class TestGetModelService:
    """Test the lazy initialization of model service."""
    
    def test_creates_service_on_first_call(self):
        """Test that service is created on first call."""
        # Reset the global service
        import model_ms.model.tools as tools_module
        tools_module._model_service = None
        
        service = _get_model_service()
        
        assert service is not None
        assert tools_module._model_service is service
    
    def test_returns_same_instance_on_subsequent_calls(self):
        """Test that same service instance is returned on subsequent calls."""
        import model_ms.model.tools as tools_module
        tools_module._model_service = None
        
        service1 = _get_model_service()
        service2 = _get_model_service()
        
        assert service1 is service2


class TestGetDataModelSuccess:
    """Test successful data model retrieval scenarios."""
    
    @patch('model_ms.model.tools.ModelService')
    def test_get_data_model_with_defaults(self, mock_service_class, mock_context):
        """Test get_data_model with default parameters."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        expected_model = {"entity_types": [{"name": "person"}]}
        mock_service.get_data_model.return_value = expected_model
        
        # Reset global service to use our mock
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context)
        
        # Verify
        assert result == expected_model
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            None,  # crn defaults to None
            "enhanced_compact"  # format defaults to enhanced_compact
        )
    
    @patch('model_ms.model.tools.ModelService')
    def test_get_data_model_with_custom_crn(self, mock_service_class, mock_context):
        """Test get_data_model with custom CRN."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        expected_model = {"entity_types": []}
        mock_service.get_data_model.return_value = expected_model
        custom_crn = "crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context, crn=custom_crn)
        
        # Verify
        assert result == expected_model
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            custom_crn,
            "enhanced_compact"
        )
    
    @patch('model_ms.model.tools.ModelService')
    def test_get_data_model_with_raw_format(self, mock_service_class, mock_context):
        """Test get_data_model with raw format."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        expected_model = {"raw": "data"}
        mock_service.get_data_model.return_value = expected_model
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context, format="raw")
        
        # Verify
        assert result == expected_model
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            None,
            "raw"
        )
    
    @patch('model_ms.model.tools.ModelService')
    def test_get_data_model_with_entity_attribute_format(self, mock_service_class, mock_context):
        """Test get_data_model with entity_attribute format returns list."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        expected_model = [{"entity_type": "person", "attributes": []}]
        mock_service.get_data_model.return_value = expected_model
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context, format="entity_attribute")
        
        # Verify
        assert result == expected_model
        assert isinstance(result, list)
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            None,
            "entity_attribute"
        )
    
    @patch('model_ms.model.tools.ModelService')
    def test_get_data_model_with_all_parameters(self, mock_service_class, mock_context):
        """Test get_data_model with all parameters specified."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        expected_model = {"entity_types": [], "attribute_type_definitions": {}}
        mock_service.get_data_model.return_value = expected_model
        custom_crn = ":::::::1::"
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context, crn=custom_crn, format="enhanced")
        
        # Verify
        assert result == expected_model
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            custom_crn,
            "enhanced"
        )


class TestGetDataModelExceptions:
    """Test exception handling in get_data_model."""
    
    @patch('model_ms.model.tools.ModelService')
    def test_crn_validation_error_propagates(self, mock_service_class, mock_context):
        """Test that CRNValidationError is propagated from service."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.side_effect = CRNValidationError("Invalid CRN format")
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute & Verify
        with pytest.raises(CRNValidationError) as exc_info:
            get_data_model(mock_context, crn="invalid-crn")
        
        assert "Invalid CRN format" in str(exc_info.value)
    
    @patch('model_ms.model.tools.ModelService')
    def test_invalid_format_error_propagates(self, mock_service_class, mock_context):
        """Test that InvalidFormatError is propagated from service."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.side_effect = InvalidFormatError(
            "invalid_format",
            {"raw", "entity_attribute", "enhanced", "enhanced_compact"}
        )
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute & Verify
        with pytest.raises(InvalidFormatError) as exc_info:
            get_data_model(mock_context, format="invalid_format")  # type: ignore
        
        assert exc_info.value.format == "invalid_format"
    
    @patch('model_ms.model.tools.ModelService')
    def test_data_model_fetch_error_propagates(self, mock_service_class, mock_context):
        """Test that DataModelFetchError is propagated from service."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.side_effect = DataModelFetchError(
            message="API request failed",
            status_code=500,
            crn="test-crn",
            version="current"
        )
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute & Verify
        with pytest.raises(DataModelFetchError) as exc_info:
            get_data_model(mock_context)
        
        assert exc_info.value.status_code == 500
        assert "API request failed" in exc_info.value.message
    
    @patch('model_ms.model.tools.ModelService')
    def test_unexpected_exception_propagates(self, mock_service_class, mock_context):
        """Test that unexpected exceptions are propagated."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.side_effect = RuntimeError("Unexpected error")
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute & Verify
        with pytest.raises(RuntimeError) as exc_info:
            get_data_model(mock_context)
        
        assert "Unexpected error" in str(exc_info.value)


class TestGetDataModelIntegration:
    """Integration tests with real service (mocking only adapter)."""
    
    @patch('model_ms.model.service.ModelMSAdapter')
    @patch('model_ms.model.service.get_default_session_store')
    @patch('common.core.base_service.get_crn_with_precedence')
    def test_integration_with_real_service(
        self,
        mock_crn_validator,
        mock_session_store_getter,
        mock_adapter_class,
        mock_context,
        sample_data_model
    ):
        """Test get_data_model with real service but mocked adapter and CRN validator."""
        # Setup
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        mock_adapter.get_data_model.return_value = sample_data_model
        
        mock_session_store = Mock()
        mock_session_store_getter.return_value = mock_session_store
        
        # Mock CRN validation to return valid CRN and tenant
        mock_crn_validator.return_value = (":::::::1::", "tenant01")
        
        mock_context.session_id = "test-session-123"
        
        # Reset global service to create new one with our mocks
        import model_ms.model.tools as tools_module
        tools_module._model_service = None
        
        # Execute
        result = get_data_model(mock_context, format="raw")
        
        # Verify
        assert result == sample_data_model
        mock_adapter.get_data_model.assert_called_once()
        mock_session_store.register_data_model_fetch.assert_called_once()
        mock_crn_validator.assert_called_once()


class TestGetDataModelEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @patch('model_ms.model.tools.ModelService')
    def test_empty_data_model(self, mock_service_class, mock_context):
        """Test handling of empty data model."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.return_value = {}
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context)
        
        # Verify
        assert result == {}
    
    @patch('model_ms.model.tools.ModelService')
    def test_none_context_session_id(self, mock_service_class):
        """Test with context that has None session_id."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.return_value = {"data": "model"}
        
        mock_context = Mock()
        mock_context.session_id = None
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute
        result = get_data_model(mock_context)
        
        # Verify - should still work, service handles None session_id
        assert result == {"data": "model"}
        mock_service.get_data_model.assert_called_once()
    
    @patch('model_ms.model.tools.ModelService')
    def test_format_parameter_case_sensitivity(self, mock_service_class, mock_context):
        """Test that format parameter is case-sensitive."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        # Service should raise InvalidFormatError for wrong case
        mock_service.get_data_model.side_effect = InvalidFormatError(
            "RAW",
            {"raw", "entity_attribute", "enhanced", "enhanced_compact"}
        )
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute & Verify
        with pytest.raises(InvalidFormatError):
            get_data_model(mock_context, format="RAW")  # type: ignore  # Wrong case intentionally


class TestGetDataModelDocumentation:
    """Test that the function behaves as documented."""
    
    @patch('model_ms.model.tools.ModelService')
    def test_documented_example_default_crn(self, mock_service_class, mock_context):
        """Test the documented example: get_data_model()"""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.return_value = {"entity_types": []}
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute - as shown in docstring
        data_model = get_data_model(mock_context)
        
        # Verify
        assert data_model is not None
        mock_service.get_data_model.assert_called_once()
    
    @patch('model_ms.model.tools.ModelService')
    def test_documented_example_with_crn(self, mock_service_class, mock_context):
        """Test the documented example with CRN."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.return_value = {"entity_types": []}
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute - as shown in docstring
        data_model = get_data_model(
            mock_context,
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )
        
        # Verify
        assert data_model is not None
        mock_service.get_data_model.assert_called_once()
    
    @patch('model_ms.model.tools.ModelService')
    def test_documented_example_raw_format(self, mock_service_class, mock_context):
        """Test the documented example with raw format."""
        # Setup
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_data_model.return_value = {"raw": "data"}
        
        import model_ms.model.tools as tools_module
        tools_module._model_service = mock_service
        
        # Execute - as shown in docstring
        data_model = get_data_model(mock_context, format="raw")
        
        # Verify
        assert data_model is not None
        mock_service.get_data_model.assert_called_once_with(
            mock_context,
            None,
            "raw"
        )