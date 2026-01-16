# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for AuthenticationManager JWT decoding using PyJWT.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from common.auth.authentication_manager import AuthenticationManager
from common.auth.token_cache import TokenCache


class TestJWTDecoding:
    """Test JWT decoding functionality using PyJWT."""
    
    def create_test_jwt(self, exp_delta: timedelta) -> str:
        """
        Create a test JWT token with specified expiry.
        
        Args:
            exp_delta: Time delta from now for expiry
            
        Returns:
            JWT token string
        """
        exp_time = datetime.now() + exp_delta
        payload = {
            'exp': int(exp_time.timestamp()),
            'sub': 'test-user',
            'iat': int(datetime.now().timestamp())
        }
        # Create token without signature (algorithm='none')
        token = jwt.encode(payload, '', algorithm='none')
        return token
    
    def test_decode_valid_jwt(self):
        """Test decoding a valid JWT token."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Create token that expires in 1 hour
        token = self.create_test_jwt(timedelta(hours=1))
        
        expiry = auth_manager._decode_jwt_expiry(token)
        
        assert expiry is not None
        # Expiry should be approximately 1 hour minus buffer (120 seconds)
        expected_expiry = datetime.now() + timedelta(hours=1) - timedelta(seconds=120)
        # Allow 5 second tolerance for test execution time
        assert abs((expiry - expected_expiry).total_seconds()) < 5
    
    def test_decode_jwt_without_exp_claim(self):
        """Test decoding JWT without 'exp' claim returns None."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Create token without exp claim
        payload = {'sub': 'test-user'}
        token = jwt.encode(payload, '', algorithm='none')
        
        expiry = auth_manager._decode_jwt_expiry(token)
        
        assert expiry is None
    
    def test_decode_expired_jwt(self):
        """Test decoding an already expired JWT."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Create token that expired 1 hour ago
        token = self.create_test_jwt(timedelta(hours=-1))
        
        expiry = auth_manager._decode_jwt_expiry(token)
        
        # PyJWT with verify_exp=False will still decode expired tokens
        # The expiry datetime will be in the past
        assert expiry is not None
        # Verify the expiry is in the past (token already expired)
        assert expiry < datetime.now()
    
    def test_decode_invalid_jwt_format(self):
        """Test decoding invalid JWT format."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Invalid token format
        invalid_token = "not.a.valid.jwt.token"
        
        expiry = auth_manager._decode_jwt_expiry(invalid_token)
        
        assert expiry is None
    
    def test_decode_malformed_jwt(self):
        """Test decoding malformed JWT."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Malformed token
        malformed_token = "eyJhbGciOiJub25lIn0.invalid_payload.no_signature"
        
        expiry = auth_manager._decode_jwt_expiry(malformed_token)
        
        assert expiry is None
    
    def test_expiry_buffer_applied(self):
        """Test that expiry buffer is correctly applied."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Create token that expires in exactly 1 hour
        exp_time = datetime.now() + timedelta(hours=1)
        payload = {'exp': int(exp_time.timestamp())}
        token = jwt.encode(payload, '', algorithm='none')
        
        expiry = auth_manager._decode_jwt_expiry(token)
        
        assert expiry is not None
        # Expiry should be 120 seconds (buffer) before actual expiry
        expected_expiry = exp_time - timedelta(seconds=TokenCache.EXPIRY_BUFFER_SECONDS)
        # Allow 2 second tolerance
        assert abs((expiry - expected_expiry).total_seconds()) < 2
    
    def test_decode_jwt_with_additional_claims(self):
        """Test decoding JWT with additional claims."""
        auth_manager = AuthenticationManager(platform="local")
        
        # Create token with multiple claims
        exp_time = datetime.now() + timedelta(hours=1)
        payload = {
            'exp': int(exp_time.timestamp()),
            'sub': 'test-user',
            'iat': int(datetime.now().timestamp()),
            'aud': 'test-audience',
            'iss': 'test-issuer',
            'custom_claim': 'custom_value'
        }
        token = jwt.encode(payload, '', algorithm='none')
        
        expiry = auth_manager._decode_jwt_expiry(token)
        
        assert expiry is not None
        # Should successfully extract exp even with other claims
        expected_expiry = exp_time - timedelta(seconds=TokenCache.EXPIRY_BUFFER_SECONDS)
        assert abs((expiry - expected_expiry).total_seconds()) < 2


class TestJWTIntegration:
    """Test JWT decoding integration with token fetching."""
    
    @patch('common.auth.authentication_manager.requests.post')
    def test_cpd_token_fetch_with_jwt_decoding(self, mock_post):
        """Test CPD token fetch with JWT decoding."""
        auth_manager = AuthenticationManager(platform="cpd")
        
        # Create a valid JWT token
        exp_time = datetime.now() + timedelta(hours=12)
        payload = {'exp': int(exp_time.timestamp())}
        test_token = jwt.encode(payload, '', algorithm='none')
        
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {'token': test_token}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Fetch token
        token, expiry = auth_manager._fetch_cpd_token()
        
        assert token == test_token
        assert expiry is not None
        # Expiry should be approximately 12 hours minus buffer
        expected_expiry = exp_time - timedelta(seconds=TokenCache.EXPIRY_BUFFER_SECONDS)
        assert abs((expiry - expected_expiry).total_seconds()) < 2
    
    @patch('common.auth.authentication_manager.requests.post')
    def test_cpd_token_fetch_with_invalid_jwt(self, mock_post):
        """Test CPD token fetch with invalid JWT falls back to default."""
        auth_manager = AuthenticationManager(platform="cpd")
        
        # Mock response with invalid JWT
        mock_response = Mock()
        mock_response.json.return_value = {'token': 'invalid.jwt.token'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Fetch token
        token, expiry = auth_manager._fetch_cpd_token()
        
        assert token == 'invalid.jwt.token'
        assert expiry is not None
        # Should fall back to 12-hour default
        expected_expiry = datetime.now() + timedelta(hours=12) - timedelta(seconds=120)
        # Allow 5 second tolerance
        assert abs((expiry - expected_expiry).total_seconds()) < 5


class TestPyJWTComparison:
    """Compare PyJWT implementation with manual decoding."""
    
    def test_pyjwt_vs_manual_decoding(self):
        """Verify PyJWT produces same results as manual decoding."""
        # Create a test token
        exp_time = datetime.now() + timedelta(hours=1)
        payload = {'exp': int(exp_time.timestamp())}
        token = jwt.encode(payload, '', algorithm='none')
        
        # Decode with PyJWT (our new implementation)
        auth_manager = AuthenticationManager(platform="local")
        pyjwt_expiry = auth_manager._decode_jwt_expiry(token)
        
        # Manual decoding (old way)
        import base64
        import json
        parts = token.split('.')
        payload_part = parts[1]
        padding = 4 - len(payload_part) % 4
        if padding != 4:
            payload_part += '=' * padding
        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        manual_payload = json.loads(decoded_bytes)
        manual_exp = datetime.fromtimestamp(manual_payload['exp'])
        manual_expiry = manual_exp - timedelta(seconds=120)
        
        # Both should produce the same result
        assert pyjwt_expiry is not None
        assert abs((pyjwt_expiry - manual_expiry).total_seconds()) < 1