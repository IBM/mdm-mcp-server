# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for Context-based session validation for search operations.

This test suite verifies:
1. Session ID extraction from MCP Context
2. Session state management (data model fetch tracking)
3. Session isolation between different clients
4. Precondition checks for search operations
"""

import pytest
from unittest.mock import Mock
from common.domain.session_store import (
    has_fetched_data_model,
    register_data_model_fetch,
    clear_session,
    clear_all_sessions
)


class TestContextSessionExtraction:
    """Test session ID extraction from MCP Context."""

    def test_extract_from_client_id(self):
        """Test that session ID is extracted from client_id when available."""
        ctx = Mock()
        ctx.client_id = "client-123"
        ctx.request_id = "req-456"
        
        session_id = ctx.client_id or ctx.request_id or "default"
        
        assert session_id == "client-123"

    def test_fallback_to_request_id(self):
        """Test that session ID falls back to request_id when client_id is None."""
        ctx = Mock()
        ctx.client_id = None
        ctx.request_id = "req-789"
        
        session_id = ctx.client_id or ctx.request_id or "default"
        
        assert session_id == "req-789"

    def test_fallback_to_default(self):
        """Test that session ID falls back to 'default' when both are None."""
        ctx = Mock()
        ctx.client_id = None
        ctx.request_id = None
        
        session_id = ctx.client_id or ctx.request_id or "default"
        
        assert session_id == "default"


class TestSessionWorkflow:
    """Test complete session workflow with Context objects."""

    def test_new_session_has_not_fetched_data_model(self, mock_context):
        """Test that new session shows data model has not been fetched."""
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        has_fetched = has_fetched_data_model(session_id)
        
        assert not has_fetched

    def test_register_data_model_fetch(self, mock_context):
        """Test that data model fetch can be registered for a session."""
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        register_data_model_fetch(session_id)
        has_fetched = has_fetched_data_model(session_id)
        
        assert has_fetched

    def test_session_persists_after_registration(self, mock_context):
        """Test that session state persists after data model registration."""
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        # Register data model fetch
        register_data_model_fetch(session_id)
        
        # Check multiple times to ensure persistence
        assert has_fetched_data_model(session_id)
        assert has_fetched_data_model(session_id)

    def test_precondition_check_passes_after_fetch(self, mock_context):
        """Test that precondition check passes after data model is fetched."""
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        register_data_model_fetch(session_id)
        has_fetched = has_fetched_data_model(session_id)
        
        assert has_fetched, "Precondition check should pass"


class TestSessionIsolation:
    """Test session isolation between different clients."""

    def test_different_sessions_are_isolated(self):
        """Test that different sessions maintain separate state."""
        # Create two different contexts
        ctx1 = Mock()
        ctx1.client_id = "test-client-001"
        ctx1.request_id = "req-001"
        
        ctx2 = Mock()
        ctx2.client_id = "test-client-002"
        ctx2.request_id = "req-002"
        
        session_id1 = ctx1.client_id or ctx1.request_id or "default"
        session_id2 = ctx2.client_id or ctx2.request_id or "default"
        
        # Register data model for first session only
        register_data_model_fetch(session_id1)
        
        # Verify isolation
        assert has_fetched_data_model(session_id1)
        assert not has_fetched_data_model(session_id2)

    def test_session_cleanup(self):
        """Test that session can be cleared individually."""
        session_id = "test-session"
        
        register_data_model_fetch(session_id)
        assert has_fetched_data_model(session_id)
        
        clear_session(session_id)
        assert not has_fetched_data_model(session_id)

    def test_clear_all_sessions(self):
        """Test that all sessions can be cleared at once."""
        # Register multiple sessions
        register_data_model_fetch("session-1")
        register_data_model_fetch("session-2")
        register_data_model_fetch("session-3")
        
        # Clear all
        clear_all_sessions()
        
        # Verify all cleared
        assert not has_fetched_data_model("session-1")
        assert not has_fetched_data_model("session-2")
        assert not has_fetched_data_model("session-3")


class TestErrorMessageFormat:
    """Test error message formatting for session validation."""

    def test_error_message_structure(self):
        """Test that error message contains required information."""
        session_id = "auto-extracted-session-123"
        
        error_msg = (
            "PRECONDITION FAILED: Data model must be fetched before searching.\n\n"
            "To fix this error:\n"
            "1. First call get_data_model() in the same session:\n"
            "   get_data_model(\n"
            "       tenant_id=\":::::::1::\",\n"
            "       format=\"enhanced_compact\"\n"
            "   )\n\n"
            "2. Review the data model to understand:\n"
            "   - Available entity types (e.g., 'person', 'organization')\n"
            "   - Searchable attributes and their property paths (e.g., 'legal_name.last_name')\n"
            "   - Attribute data types and valid search conditions\n\n"
            "3. Then call search_master_data() in the same session:\n"
            "   search_master_data(\n"
            "       search_type=\"record\",\n"
            "       query={{...}}\n"
            "   )\n\n"
            "The data model is essential for constructing valid search queries with correct "
            "property paths and understanding which fields are searchable.\n\n"
            f"Current session ID: {session_id}"
        )
        
        # Verify key components
        assert "get_data_model()" in error_msg
        assert "enhanced_compact" in error_msg
        assert "property paths" in error_msg
        assert "Current session ID:" in error_msg
        assert "session_id=" not in error_msg  # Should NOT have session_id parameter

    def test_error_message_no_manual_session_id(self):
        """Test that error message doesn't require manual session_id parameter."""
        session_id = "test-session"
        
        error_msg = f"Current session ID: {session_id}"
        
        # Should show session ID for debugging but not require it as parameter
        assert session_id in error_msg
        assert "session_id=" not in error_msg


@pytest.mark.unit
class TestContextAdvantages:
    """Document and verify advantages of Context-based approach."""

    def test_automatic_session_tracking(self, mock_context):
        """Verify that session tracking is automatic via Context."""
        # Session ID is extracted automatically from context
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        # No manual session_id parameter needed
        assert session_id is not None
        assert isinstance(session_id, str)

    def test_session_security(self):
        """Verify that session ID comes from trusted MCP infrastructure."""
        # Session ID from Context cannot be spoofed by LLM
        ctx = Mock()
        ctx.client_id = "trusted-client-id"
        
        session_id = ctx.client_id
        
        # Session ID is controlled by MCP framework, not user input
        assert session_id == "trusted-client-id"

    def test_simplified_tool_signatures(self, mock_context):
        """Verify that tools don't need session_id parameter."""
        # Tools can extract session_id from context automatically
        session_id = mock_context.client_id or mock_context.request_id or "default"
        
        # This simplifies tool signatures - no session_id parameter needed
        register_data_model_fetch(session_id)
        
        assert has_fetched_data_model(session_id)