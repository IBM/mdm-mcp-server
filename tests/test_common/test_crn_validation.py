# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for CRN validation functionality.

Tests cover:
1. On-Prem CRN format validation
2. Full CRN format validation
3. Invalid CRN format detection
4. Tenant ID extraction
5. Default CRN handling
6. Error response formatting
7. Exception handling
"""

import pytest
from common.domain.crn_validator import (
    validate_crn,
    get_tenant_id_from_crn,
    validate_and_get_crn,
    format_crn_error_response,
    CRNValidationError,
    DEFAULT_CRN
)


class TestOnPremCRNValidation:
    """Test On-Prem CRN format validation."""

    def test_valid_onprem_crn(self, sample_crn_onprem):
        """Test that valid On-Prem CRN is accepted."""
        is_valid, tenant_id, error = validate_crn(sample_crn_onprem)
        
        assert is_valid
        assert tenant_id == "tenant01"
        assert error is None

    def test_custom_tenant_id(self):
        """Test On-Prem CRN with custom tenant ID."""
        crn = ":::::::my_custom_tenant::"
        is_valid, tenant_id, error = validate_crn(crn)
        
        assert is_valid
        assert tenant_id == "my_custom_tenant"
        assert error is None

    def test_invalid_onprem_crn_missing_tenant(self):
        """Test that On-Prem CRN without tenant ID is rejected."""
        crn = ":::::::::"
        is_valid, tenant_id, error = validate_crn(crn)
        
        assert not is_valid
        assert tenant_id is None
        assert error is not None


class TestFullCRNValidation:
    """Test full CRN format validation."""

    def test_valid_full_crn(self, sample_crn_cloud):
        """Test that valid full CRN is accepted."""
        is_valid, tenant_id, error = validate_crn(sample_crn_cloud)
        
        assert is_valid
        assert tenant_id is not None
        assert error is None

    def test_another_valid_full_crn(self):
        """Test another valid full CRN format."""
        crn = "crn:v1:production:public:mdm:eu-west:a/account123:instance456::"
        is_valid, tenant_id, error = validate_crn(crn)
        
        assert is_valid
        assert tenant_id == "instance456"
        assert error is None

    def test_invalid_full_crn_missing_tenant(self):
        """Test that full CRN without tenant ID (instance field) is rejected."""
        crn = "crn:v1:staging:public:mdm-oc:us-south:a/account123:::"
        is_valid, tenant_id, error = validate_crn(crn)
        
        assert not is_valid
        assert error is not None


class TestInvalidCRNFormats:
    """Test detection of invalid CRN formats."""

    @pytest.mark.parametrize("crn,description", [
        ("", "empty string"),
        ("invalid", "random string"),
        ("tenant01", "just tenant ID"),
        ("::tenant01::", "wrong number of colons"),
        ("crn:v1:staging", "incomplete CRN"),
    ])
    def test_invalid_crn_formats(self, crn, description):
        """Test that various invalid CRN formats are rejected."""
        is_valid, tenant_id, error = validate_crn(crn)
        
        assert not is_valid, f"Should reject {description}"
        assert error is not None

    def test_none_crn(self):
        """Test that None CRN is handled properly."""
        # validate_crn expects a string, so None should be invalid
        is_valid, tenant_id, error = validate_crn(None)  # type: ignore
        
        assert not is_valid
        assert error is not None


class TestTenantIDExtraction:
    """Test tenant ID extraction from CRNs."""

    @pytest.mark.parametrize("crn,expected_tenant_id", [
        (":::::::1::", "tenant01"),
        (":::::::production_tenant::", "production_tenant"),
        ("crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::", "instance456"),
    ])
    def test_tenant_id_extraction(self, crn, expected_tenant_id):
        """Test that tenant IDs are correctly extracted from various CRN formats."""
        tenant_id = get_tenant_id_from_crn(crn)
        assert tenant_id == expected_tenant_id

    def test_tenant_id_extraction_invalid_crn(self):
        """Test that invalid CRN raises exception during extraction."""
        with pytest.raises(CRNValidationError) as exc_info:
            get_tenant_id_from_crn("invalid")
        
        assert "Invalid CRN" in str(exc_info.value)


class TestDefaultCRNHandling:
    """Test default CRN handling."""

    def test_none_uses_default(self):
        """Test that None input uses default CRN."""
        crn, tenant_id = validate_and_get_crn(None)
        
        assert crn == DEFAULT_CRN
        assert tenant_id == "tenant01"

    def test_empty_string_uses_default(self):
        """Test that empty string uses default CRN."""
        crn, tenant_id = validate_and_get_crn("")
        
        assert crn == DEFAULT_CRN
        assert tenant_id == "tenant01"

    def test_valid_custom_crn_is_used(self):
        """Test that valid custom CRN is used instead of default."""
        custom_crn = ":::::::custom_tenant::"
        crn, tenant_id = validate_and_get_crn(custom_crn)
        
        assert crn == custom_crn
        assert tenant_id == "custom_tenant"

    def test_invalid_crn_raises_exception(self):
        """Test that invalid CRN raises exception."""
        with pytest.raises(CRNValidationError) as exc_info:
            validate_and_get_crn("invalid")
        
        assert "Invalid CRN format" in str(exc_info.value)


class TestErrorResponseFormatting:
    """Test error response formatting."""

    def test_error_response_structure(self):
        """Test that error response has correct structure."""
        invalid_crn = "invalid_crn"
        error_msg = "Invalid CRN format"
        
        error_response = format_crn_error_response(invalid_crn, error_msg)
        
        assert error_response["error"] == "CRNValidationFailed"
        assert error_response["status_code"] == 400
        assert error_response["message"] == error_msg
        assert error_response["details"]["provided_crn"] == invalid_crn
        assert error_response["details"]["default_crn"] == DEFAULT_CRN
        assert "valid_formats" in error_response["details"]

    def test_error_response_contains_valid_formats(self):
        """Test that error response includes valid format examples."""
        error_response = format_crn_error_response("invalid", "test error")
        
        valid_formats = error_response["details"]["valid_formats"]
        assert isinstance(valid_formats, list)
        assert len(valid_formats) > 0


class TestCRNValidationException:
    """Test CRN validation exception handling."""

    def test_exception_raised_for_invalid_crn(self):
        """Test that CRNValidationError is raised for invalid CRN."""
        with pytest.raises(CRNValidationError) as exc_info:
            get_tenant_id_from_crn("invalid")
        
        assert "Invalid CRN" in str(exc_info.value)

    def test_exception_raised_in_validate_and_get_crn(self):
        """Test that CRNValidationError is raised in validate_and_get_crn."""
        with pytest.raises(CRNValidationError) as exc_info:
            validate_and_get_crn("invalid")
        
        assert "Invalid CRN format" in str(exc_info.value)

    def test_exception_type(self):
        """Test that the correct exception type is raised."""
        with pytest.raises(CRNValidationError):
            get_tenant_id_from_crn("invalid")