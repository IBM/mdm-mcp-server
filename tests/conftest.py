# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Pytest configuration and shared fixtures.

This file contains pytest fixtures that are available to all test modules.
Fixtures defined here can be used across all tests without importing.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def reset_session_store():
    """
    Automatically clear session store before and after each test.
    
    This ensures test isolation and prevents state leakage between tests.
    """
    from common.domain.session_store import clear_all_sessions
    
    # Clear before test
    clear_all_sessions()
    
    yield
    
    # Clear after test
    clear_all_sessions()


@pytest.fixture
def mock_context():
    """
    Create a mock MCP Context object for testing.
    
    Returns:
        Mock: A mock Context object with client_id, request_id, and session attributes.
    """
    from unittest.mock import Mock
    
    ctx = Mock()
    ctx.client_id = "test-client-123"
    ctx.request_id = "test-request-456"
    ctx.session = Mock()
    return ctx


@pytest.fixture
def sample_crn_onprem():
    """Provide a sample on-premise CRN for testing."""
    return ":::::::1::"


@pytest.fixture
def sample_crn_cloud():
    """Provide a sample cloud CRN for testing."""
    return "crn:xx:xxxxx:xxxxxx:xxxxx:xx-xxxx:x/xxxxxx123445:xx12xx123xx-xxxxx-xxxxx-xxx-xxxxx::"


@pytest.fixture
def sample_data_model():
    """
    Provide a sample data model for testing search validators.
    
    Returns:
        dict: A sample data model with record types and attribute types.
    """
    return {
        "record_types": {
            "person": {
                "attributes": {
                    "legal_name": {
                        "attribute_type": "name_type",
                        "indexed": True,
                        "label": "Legal Name"
                    },
                    "age": {
                        "attribute_type": "integer",
                        "indexed": True,
                        "label": "Age"
                    },
                    "address": {
                        "attribute_type": "address_type",
                        "indexed": False,
                        "label": "Address"
                    },
                    "email": {
                        "attribute_type": "string",
                        "indexed": True,
                        "label": "Email"
                    }
                }
            }
        },
        "attribute_types": {
            "name_type": {
                "label": "Name",
                "fields": {
                    "first_name": {
                        "indexed": True,
                        "label": "First Name"
                    },
                    "last_name": {
                        "indexed": True,
                        "label": "Last Name"
                    },
                    "middle_name": {
                        "indexed": False,
                        "label": "Middle Name"
                    }
                }
            },
            "address_type": {
                "label": "Address",
                "fields": {
                    "city": {
                        "indexed": True,
                        "label": "City"
                    },
                    "street": {
                        "indexed": False,
                        "label": "Street"
                    },
                    "zip_code": {
                        "indexed": True,
                        "label": "ZIP Code"
                    }
                }
            }
        }
    }