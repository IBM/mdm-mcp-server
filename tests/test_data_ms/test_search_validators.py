# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for search query validator.

This test suite verifies:
1. DataModelValidator initialization
2. Property path validation (top-level and nested)
3. Query validation (simple and complex)
4. Searchable property detection
5. Error messages and suggestions
"""

import pytest
from src.data_ms.search.validators import DataModelValidator


class TestValidatorInitialization:
    """Test DataModelValidator initialization."""

    def test_validator_initializes_with_data_model(self, sample_data_model):
        """Test that validator initializes correctly with data model."""
        validator = DataModelValidator(sample_data_model)
        
        assert validator.data_model == sample_data_model
        assert len(validator.valid_properties) > 0
        assert len(validator.searchable_properties) > 0


class TestPropertyPathValidation:
    """Test property path validation."""

    def test_valid_top_level_property(self, sample_data_model):
        """Test validation of valid top-level property that has no nested fields."""
        validator = DataModelValidator(sample_data_model)
        
        # 'age' and 'email' are simple types with no nested fields
        is_valid, error = validator.validate_property_path("age")
        
        assert is_valid
        assert error is None
        
        is_valid, error = validator.validate_property_path("email")
        
        assert is_valid
        assert error is None

    def test_valid_nested_property(self, sample_data_model):
        """Test validation of valid nested property."""
        validator = DataModelValidator(sample_data_model)
        
        is_valid, error = validator.validate_property_path("legal_name.last_name")
        
        assert is_valid
        assert error is None

    def test_invalid_property(self, sample_data_model):
        """Test validation of invalid property."""
        validator = DataModelValidator(sample_data_model)
        
        is_valid, error = validator.validate_property_path("invalid_property")
        
        assert not is_valid
        assert error is not None
        assert "does not exist" in error

    def test_non_searchable_top_level_property(self, sample_data_model):
        """Test validation of non-searchable top-level property with nested fields."""
        validator = DataModelValidator(sample_data_model)
        
        # 'address' is not indexed AND has nested fields - should suggest nested paths
        is_valid, error = validator.validate_property_path("address")
        
        assert not is_valid
        assert error is not None
        assert "incomplete path" in error.lower()

    def test_non_searchable_nested_property(self, sample_data_model):
        """Test validation of non-searchable nested property."""
        validator = DataModelValidator(sample_data_model)
        
        # 'legal_name.middle_name' is not indexed
        is_valid, error = validator.validate_property_path("legal_name.middle_name")
        
        assert not is_valid
        assert error is not None
        assert "not searchable" in error

    def test_complex_nested_path_valid(self, sample_data_model):
        """Test validation of complex nested path that is valid."""
        validator = DataModelValidator(sample_data_model)
        
        # Valid nested path
        is_valid, error = validator.validate_property_path("address.city")
        
        assert is_valid
        assert error is None

    def test_complex_nested_path_invalid_parent(self, sample_data_model):
        """Test validation of nested path with non-existent parent."""
        validator = DataModelValidator(sample_data_model)
        
        # Invalid nested path (parent doesn't exist)
        is_valid, error = validator.validate_property_path("nonexistent.field")
        
        assert not is_valid
        assert error is not None
        assert "does not exist" in error

    def test_wildcard_property_allowed(self, sample_data_model):
        """Test that wildcard '*' property is allowed for full-text search."""
        validator = DataModelValidator(sample_data_model)
        
        # Wildcard should be valid
        is_valid, error = validator.validate_property_path("*")
        
        assert is_valid
        assert error is None

    def test_incomplete_path_rejected_when_nested_exists(self, sample_data_model):
        """Test that incomplete paths like 'legal_name' are rejected when nested paths exist."""
        validator = DataModelValidator(sample_data_model)
        
        # 'legal_name' alone should be rejected if 'legal_name.last_name' exists
        is_valid, error = validator.validate_property_path("legal_name")
        
        # This should fail because legal_name has nested fields
        assert not is_valid
        assert error is not None
        assert "incomplete path" in error.lower()
        assert "legal_name.last_name" in error or "legal_name.first_name" in error


class TestSimpleQueryValidation:
    """Test validation of simple queries."""

    def test_validate_simple_query(self, sample_data_model):
        """Test validation of simple query with one expression."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
            ]
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert is_valid
        assert len(errors) == 0
        assert len(invalid_props) == 0

    def test_validate_query_with_invalid_property(self, sample_data_model):
        """Test validation of query with invalid property."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {"property": "invalid_field", "condition": "equal", "value": "test"}
            ]
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert not is_valid
        assert len(errors) > 0
        assert len(invalid_props) > 0
        assert "invalid_field" in invalid_props

    def test_validate_query_with_non_searchable_property(self, sample_data_model):
        """Test validation of query with non-searchable nested property."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {"property": "legal_name.middle_name", "condition": "equal", "value": "test"}
            ]
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert not is_valid
        assert len(errors) > 0
        assert "not searchable" in errors[0]
        # The property name should be in the error message
        assert "legal_name.middle_name" in errors[0]


class TestNestedQueryValidation:
    """Test validation of nested queries with AND/OR operations."""

    def test_validate_nested_query_with_and_or(self, sample_data_model):
        """Test validation of nested query with AND/OR operations."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {
                    "operation": "or",
                    "expressions": [
                        {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                        {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                    ]
                },
                {"property": "age", "condition": "greater_than", "value": 18}
            ],
            "operation": "and"
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert is_valid
        assert len(errors) == 0

    def test_validate_nested_query_with_invalid_property(self, sample_data_model):
        """Test validation of nested query with invalid property."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {
                    "operation": "or",
                    "expressions": [
                        {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                        {"property": "invalid_property", "condition": "equal", "value": "Jones"}
                    ]
                },
                {"property": "age", "condition": "greater_than", "value": 18}
            ],
            "operation": "and"
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert not is_valid
        assert len(errors) > 0
        assert "invalid_property" in invalid_props


class TestSearchableProperties:
    """Test searchable property detection and listing."""

    def test_get_all_searchable_properties(self, sample_data_model):
        """Test getting all searchable properties from data model."""
        validator = DataModelValidator(sample_data_model)
        
        searchable = validator.get_all_searchable_properties()
        
        assert len(searchable) > 0
        
        # Check that searchable properties are included
        property_paths = [p["property_path"] for p in searchable]
        assert "legal_name" in property_paths
        assert "legal_name.last_name" in property_paths
        assert "age" in property_paths
        assert "email" in property_paths

    def test_non_searchable_properties_excluded(self, sample_data_model):
        """Test that non-searchable properties are not in searchable list."""
        validator = DataModelValidator(sample_data_model)
        
        searchable = validator.get_all_searchable_properties()
        property_paths = [p["property_path"] for p in searchable]
        
        # Check that non-searchable properties are not included
        assert "address" not in property_paths
        assert "legal_name.middle_name" not in property_paths


class TestPropertySuggestions:
    """Test property name suggestions for typos."""

    def test_similar_property_suggestions(self, sample_data_model):
        """Test that similar properties are suggested for invalid properties."""
        validator = DataModelValidator(sample_data_model)
        
        # Test with a typo in property name
        is_valid, error = validator.validate_property_path("legal_nam")
        
        assert not is_valid
        assert error is not None
        # Should suggest the correct property name
        assert "Did you mean" in error or "legal_name" in error


@pytest.mark.validation
class TestValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_query(self, sample_data_model):
        """Test validation of empty query."""
        validator = DataModelValidator(sample_data_model)
        
        query = {"expressions": []}
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        # Empty query might be valid or invalid depending on implementation
        # Just verify it doesn't crash
        assert isinstance(is_valid, bool)

    def test_deeply_nested_query(self, sample_data_model):
        """Test validation of deeply nested query structure."""
        validator = DataModelValidator(sample_data_model)
        
        query = {
            "expressions": [
                {
                    "operation": "and",
                    "expressions": [
                        {
                            "operation": "or",
                            "expressions": [
                                {"property": "legal_name.first_name", "condition": "equal", "value": "John"},
                                {"property": "legal_name.first_name", "condition": "equal", "value": "Jane"}
                            ]
                        },
                        {"property": "age", "condition": "greater_than", "value": 18}
                    ]
                }
            ],
            "operation": "and"
        }
        
        is_valid, errors, invalid_props = validator.validate_query(query)
        
        assert is_valid
        assert len(errors) == 0