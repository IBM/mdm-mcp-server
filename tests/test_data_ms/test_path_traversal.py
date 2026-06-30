# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Regression tests for HackerOne report #3826800.
Verifies that path traversal payloads in record/entity identifiers are
percent-encoded before reaching the URL construction layer.
"""

import pytest
from unittest.mock import MagicMock, patch

from data_ms.adapters.data_ms_adapter import DataMSAdapter


TRAVERSAL_PAYLOADS = [
    "../../../admin",
    "../../config",
    "../entities/secret",
    "%2e%2e/admin",
    "rec-001/../../../admin",
]

CRN = "crn:v1:bluemix:public:mdm::::tenant"


@pytest.fixture
def adapter():
    auth_manager = MagicMock()
    auth_manager.get_auth_headers.return_value = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }
    return DataMSAdapter(
        api_base_url="http://mdm-backend:9080/api/v1",
        auth_manager=auth_manager,
        use_shared_auth=False,
        verify_ssl=False,
    )


@pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
def test_get_record_traversal_blocked(adapter, payload):
    """record_id traversal payloads must not escape the records/ prefix."""
    with patch.object(adapter, "execute_get") as mock_get:
        mock_get.return_value = {}
        adapter.get_record(payload, CRN)
        called_endpoint = mock_get.call_args[0][0]
        assert "../" not in called_endpoint, (
            f"Traversal sequence '../' found in endpoint: {called_endpoint}"
        )
        assert called_endpoint.startswith("records/"), (
            f"Endpoint does not start with 'records/': {called_endpoint}"
        )


@pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
def test_get_entity_traversal_blocked(adapter, payload):
    """entity_id traversal payloads must not escape the entities/ prefix."""
    with patch.object(adapter, "execute_get") as mock_get:
        mock_get.return_value = {}
        adapter.get_entity(payload, CRN)
        called_endpoint = mock_get.call_args[0][0]
        assert "../" not in called_endpoint, (
            f"Traversal sequence '../' found in endpoint: {called_endpoint}"
        )
        assert called_endpoint.startswith("entities/"), (
            f"Endpoint does not start with 'entities/': {called_endpoint}"
        )


@pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
def test_get_record_entities_traversal_blocked(adapter, payload):
    """record_id traversal payloads must not escape records/<id>/entities pattern."""
    with patch.object(adapter, "execute_get") as mock_get:
        mock_get.return_value = {}
        adapter.get_record_entities(payload, CRN)
        called_endpoint = mock_get.call_args[0][0]
        assert "../" not in called_endpoint, (
            f"Traversal sequence '../' found in endpoint: {called_endpoint}"
        )
        assert called_endpoint.startswith("records/"), (
            f"Endpoint does not start with 'records/': {called_endpoint}"
        )


def test_benign_record_id_unchanged(adapter):
    """A normal record ID must pass through without modification."""
    with patch.object(adapter, "execute_get") as mock_get:
        mock_get.return_value = {}
        adapter.get_record("rec-00123", CRN)
        called_endpoint = mock_get.call_args[0][0]
        assert called_endpoint == "records/rec-00123"


def test_benign_entity_id_unchanged(adapter):
    """A normal entity ID must pass through without modification."""
    with patch.object(adapter, "execute_get") as mock_get:
        mock_get.return_value = {}
        adapter.get_entity("entity-456", CRN)
        called_endpoint = mock_get.call_args[0][0]
        assert called_endpoint == "entities/entity-456"
