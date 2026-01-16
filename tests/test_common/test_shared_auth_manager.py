# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for shared authentication manager functionality.

Verifies that multiple adapter instances share the same AuthenticationManager
and TokenCache, preventing duplicate token fetches.
"""

import pytest
from unittest.mock import Mock, patch
from src.common import get_shared_auth_manager, invalidate_shared_auth_manager
from src.common.core.base_adapter import BaseMDMAdapter


class TestSharedAuthManager:
    """Test suite for shared authentication manager."""
    
    def teardown_method(self):
        """Clean up after each test."""
        invalidate_shared_auth_manager()
    
    def test_get_shared_auth_manager_returns_singleton(self):
        """Test that get_shared_auth_manager returns the same instance."""
        auth1 = get_shared_auth_manager()
        auth2 = get_shared_auth_manager()
        
        assert auth1 is auth2, "Should return the same instance"
    
    def test_multiple_adapters_share_auth_manager(self):
        """Test that multiple adapters share the same auth manager."""
        adapter1 = BaseMDMAdapter()
        adapter2 = BaseMDMAdapter()
        
        assert adapter1._auth_manager is adapter2._auth_manager, \
            "Adapters should share the same auth manager"
    
    def test_multiple_adapters_share_token_cache(self):
        """Test that multiple adapters share the same token cache."""
        adapter1 = BaseMDMAdapter()
        adapter2 = BaseMDMAdapter()
        
        assert adapter1._auth_manager._token_cache is adapter2._auth_manager._token_cache, \
            "Adapters should share the same token cache"
    
    def test_invalidate_shared_auth_manager_resets_instance(self):
        """Test that invalidate_shared_auth_manager creates a new instance."""
        auth1 = get_shared_auth_manager()
        invalidate_shared_auth_manager()
        auth2 = get_shared_auth_manager()
        
        assert auth1 is not auth2, "Should create a new instance after invalidation"
    
    def test_custom_auth_manager_not_shared(self):
        """Test that custom auth manager is not shared."""
        from src.common.auth.authentication_manager import AuthenticationManager
        
        custom_auth = AuthenticationManager()
        adapter1 = BaseMDMAdapter(auth_manager=custom_auth)
        adapter2 = BaseMDMAdapter()
        
        assert adapter1._auth_manager is custom_auth, \
            "Should use custom auth manager"
        assert adapter1._auth_manager is not adapter2._auth_manager, \
            "Custom auth manager should not be shared"
    
    def test_use_shared_auth_false_creates_isolated_instance(self):
        """Test that use_shared_auth=False creates isolated instances."""
        adapter1 = BaseMDMAdapter(use_shared_auth=False)
        adapter2 = BaseMDMAdapter(use_shared_auth=False)
        
        assert adapter1._auth_manager is not adapter2._auth_manager, \
            "Should create separate auth managers when use_shared_auth=False"
    
    def test_shared_auth_manager_parameters_used_on_first_call(self):
        """Test that parameters are used only on first call."""
        auth1 = get_shared_auth_manager(timeout=60, verify_ssl=True)
        
        assert auth1.timeout == 60, "Should use provided timeout"
        assert auth1.verify_ssl is True, "Should use provided verify_ssl"
        
        # Second call with different parameters should return same instance
        auth2 = get_shared_auth_manager(timeout=30, verify_ssl=False)
        
        assert auth1 is auth2, "Should return same instance"
        assert auth2.timeout == 60, "Should keep original timeout"
        assert auth2.verify_ssl is True, "Should keep original verify_ssl"
    
    def test_invalidate_clears_token_cache(self):
        """Test that invalidate_shared_auth_manager clears the token cache."""
        auth = get_shared_auth_manager()
        
        # Mock the token cache invalidate method
        with patch.object(auth._token_cache, 'invalidate') as mock_invalidate:
            invalidate_shared_auth_manager()
            mock_invalidate.assert_called_once()
    
    def test_thread_safety_of_shared_instance(self):
        """Test thread-safe creation of shared instance."""
        import threading
        
        instances = []
        
        def get_instance():
            instances.append(get_shared_auth_manager())
        
        # Create multiple threads that try to get the shared instance
        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert all(inst is instances[0] for inst in instances), \
            "All threads should get the same instance"