# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for TokenCache - Pure cache functionality.
"""

import pytest
from datetime import datetime, timedelta
from common.auth.token_cache import TokenCache


class TestTokenCache:
    """Test TokenCache pure caching functionality."""
    
    def test_get_returns_none_when_empty(self):
        """Test that get() returns None when cache is empty."""
        cache = TokenCache()
        assert cache.get() is None
    
    def test_set_and_get_token(self):
        """Test that token can be set and retrieved."""
        cache = TokenCache()
        token = "test-token-123"
        expiry = datetime.now() + timedelta(hours=1)
        
        cache.set(token, expiry)
        
        assert cache.get() == token
    
    def test_get_returns_none_when_expired(self):
        """Test that get() returns None when token is expired."""
        cache = TokenCache()
        token = "test-token-123"
        # Set expiry in the past
        expiry = datetime.now() - timedelta(seconds=1)
        
        cache.set(token, expiry)
        
        assert cache.get() is None
    
    def test_invalidate_clears_token(self):
        """Test that invalidate() clears the cached token."""
        cache = TokenCache()
        token = "test-token-123"
        expiry = datetime.now() + timedelta(hours=1)
        
        cache.set(token, expiry)
        assert cache.get() == token
        
        cache.invalidate()
        assert cache.get() is None
    
    def test_is_expired_returns_true_when_empty(self):
        """Test that is_expired() returns True when cache is empty."""
        cache = TokenCache()
        assert cache.is_expired() is True
    
    def test_is_expired_returns_false_when_valid(self):
        """Test that is_expired() returns False when token is valid."""
        cache = TokenCache()
        token = "test-token-123"
        expiry = datetime.now() + timedelta(hours=1)
        
        cache.set(token, expiry)
        
        assert cache.is_expired() is False
    
    def test_is_expired_returns_true_when_expired(self):
        """Test that is_expired() returns True when token is expired."""
        cache = TokenCache()
        token = "test-token-123"
        # Set expiry in the past
        expiry = datetime.now() - timedelta(seconds=1)
        
        cache.set(token, expiry)
        
        assert cache.is_expired() is True
    
    def test_expiry_buffer_constant(self):
        """Test that EXPIRY_BUFFER_SECONDS constant is defined."""
        assert TokenCache.EXPIRY_BUFFER_SECONDS == 120
    
    def test_multiple_set_overwrites(self):
        """Test that setting a new token overwrites the old one."""
        cache = TokenCache()
        
        token1 = "token-1"
        expiry1 = datetime.now() + timedelta(hours=1)
        cache.set(token1, expiry1)
        assert cache.get() == token1
        
        token2 = "token-2"
        expiry2 = datetime.now() + timedelta(hours=2)
        cache.set(token2, expiry2)
        assert cache.get() == token2