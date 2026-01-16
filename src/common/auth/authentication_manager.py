# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Authentication manager for IBM MDM API.

This module handles all authentication logic including token fetching,
JWT decoding, and platform-specific authentication for CPD and Cloud platforms.
"""

import logging
import requests
import urllib3
import base64
import jwt
import threading
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta

from config import Config
from common.auth.token_cache import TokenCache

# Disable SSL warnings when verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Module-level shared instance for singleton pattern
_shared_auth_manager: Optional['AuthenticationManager'] = None
_shared_lock = threading.Lock()


def get_shared_auth_manager(
    platform: Optional[str] = None,
    timeout: int = 30,
    verify_ssl: bool = False
) -> 'AuthenticationManager':
    """
    Get or create a shared authentication manager instance.
    
    This ensures all adapters share the same AuthenticationManager and TokenCache,
    preventing duplicate token fetches and maximizing cache efficiency.
    
    Thread-safe singleton pattern with lazy initialization.
    
    Args:
        platform: Platform type (cpd, cloud). Only used on first call.
        timeout: Request timeout. Only used on first call.
        verify_ssl: SSL verification. Only used on first call.
        
    Returns:
        Shared AuthenticationManager instance
        
    Note:
        Subsequent calls ignore parameters and return the existing instance.
        To reset, call invalidate_shared_auth_manager().
    """
    global _shared_auth_manager
    
    if _shared_auth_manager is None:
        with _shared_lock:
            # Double-check locking pattern
            if _shared_auth_manager is None:
                _shared_auth_manager = AuthenticationManager(
                    platform=platform,
                    timeout=timeout,
                    verify_ssl=verify_ssl
                )
    
    return _shared_auth_manager


def invalidate_shared_auth_manager() -> None:
    """
    Invalidate the shared authentication manager.
    
    Useful for testing or when configuration changes require a fresh instance.
    """
    global _shared_auth_manager
    
    with _shared_lock:
        if _shared_auth_manager is not None:
            # Invalidate cached token before destroying instance
            _shared_auth_manager._token_cache.invalidate()
            _shared_auth_manager = None



class AuthenticationManager:
    """
    Manages authentication for IBM MDM APIs.
    
    Responsibilities:
    - Fetch tokens from CPD and Cloud auth endpoints
    - Decode JWT tokens for expiry information
    - Manage token caching via TokenCache
    - Provide authentication headers based on platform
    
    Supports two platforms:
    - cpd: Cloud Pak for Data with JWT tokens
    - cloud: IBM Cloud with IAM tokens
    """
    
    def __init__(
        self,
        platform: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = False,
        token_cache: Optional[TokenCache] = None
    ):
        """
        Initialize authentication manager.
        
        Args:
            platform: Platform type (cpd, cloud). Defaults to Config.M360_TARGET_PLATFORM
            timeout: Request timeout for auth calls in seconds
            verify_ssl: Whether to verify SSL certificates
            token_cache: Optional token cache instance (creates new if not provided)
        """
        self.platform = platform or Config.M360_TARGET_PLATFORM
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Platform-specific configuration
        self.username = Config.API_USERNAME
        self.password = Config.API_PASSWORD
        self.cpd_auth_url = Config.API_CPD_AUTH_URL
        self.cloud_auth_url = Config.API_CLOUD_AUTH_URL
        self.cloud_api_key = Config.API_CLOUD_API_KEY
        
        # Token cache (injected or created)
        self._token_cache = token_cache or TokenCache()
        self.logger = logger
    
    def _decode_jwt_expiry(self, token: str) -> Optional[datetime]:
        """
        Decode JWT token to extract expiry time from 'exp' claim using PyJWT.
        
        This method decodes the JWT token without signature verification,
        as we trust the token received from the authentication server.
        
        Args:
            token: JWT token string
            
        Returns:
            Expiry datetime with buffer applied, or None if parsing fails
        """
        try:
            # Decode JWT without signature verification
            # We trust the token from the auth server
            decoded = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # No signature verification
                    "verify_exp": False  # We'll check expiry manually with buffer
                }
            )
            
            # Extract 'exp' claim (expiry timestamp in seconds since epoch)
            exp_timestamp = decoded.get('exp')
            if not exp_timestamp:
                self.logger.warning("No 'exp' claim found in JWT token")
                return None
            
            # Convert to datetime and subtract buffer
            expiry_time = datetime.fromtimestamp(exp_timestamp)
            buffered_expiry = expiry_time - timedelta(
                seconds=TokenCache.EXPIRY_BUFFER_SECONDS
            )
            
            self.logger.info(
                f"Token expires at {expiry_time}, "
                f"will refresh at {buffered_expiry} "
                f"({TokenCache.EXPIRY_BUFFER_SECONDS}s buffer)"
            )
            
            return buffered_expiry
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT token has already expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.error(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to decode JWT expiry: {e}")
            return None
    
    def _fetch_cpd_token(self) -> Tuple[str, datetime]:
        """
        Fetch a new access token from the CPD API.
        
        Returns:
            Tuple of (access_token, expiry_time)
        
        Raises:
            requests.exceptions.RequestException: If token fetch fails
            ValueError: If response doesn't contain token
        """
        try:
            self.logger.info("Fetching new access token from CPD API")
            
            headers = {
                "cache-control": "no-cache",
                "content-type": "application/json"
            }
            
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            response = requests.post(
                self.cpd_auth_url,
                json=payload,
                headers=headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            data = response.json()
            token = data.get("token")
            
            if not token:
                raise ValueError("No token found in response")
            
            # Extract expiry from JWT token
            expiry_time = self._decode_jwt_expiry(token)
            
            if expiry_time is None:
                # Fallback to default 12 hours if JWT parsing fails
                self.logger.warning("Could not parse JWT expiry, using 12-hour default")
                expiry_time = datetime.now() + timedelta(hours=12) - timedelta(
                    seconds=TokenCache.EXPIRY_BUFFER_SECONDS
                )
            
            self.logger.info(f"Successfully fetched CPD token, will refresh at {expiry_time}")
            
            return token, expiry_time
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch CPD access token: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching CPD token: {e}")
            raise
    
    def _fetch_cloud_token(self) -> Tuple[str, datetime]:
        """
        Fetch a new access token from the Cloud IAM API.
        
        Returns:
            Tuple of (access_token, expiry_time)
        
        Raises:
            requests.exceptions.RequestException: If token fetch fails
            ValueError: If response doesn't contain access_token
        """
        try:
            self.logger.info("Fetching new access token from Cloud IAM API")
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Form-encoded data as per the curl command
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.cloud_api_key
            }
            
            response = requests.post(
                self.cloud_auth_url,
                headers=headers,
                data=data,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            token = response_data.get("access_token")
            
            if not token:
                raise ValueError("No access_token found in response")
            
            # Cloud tokens include expiration in seconds
            expires_in = response_data.get("expires_in")
            if expires_in:
                expiry_time = datetime.now() + timedelta(seconds=expires_in) - timedelta(
                    seconds=TokenCache.EXPIRY_BUFFER_SECONDS
                )
                self.logger.info(f"Cloud token expires in {expires_in} seconds, will refresh at {expiry_time}")
            else:
                # Fallback to default 1 hour if expiry not provided
                self.logger.warning("No expires_in found in response, using 1-hour default")
                expiry_time = datetime.now() + timedelta(hours=1) - timedelta(
                    seconds=TokenCache.EXPIRY_BUFFER_SECONDS
                )
            
            self.logger.info(f"Successfully fetched Cloud token, will refresh at {expiry_time}")
            
            return token, expiry_time
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch Cloud access token: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching Cloud token: {e}")
            raise
    
    def _fetch_new_token(self) -> Tuple[str, datetime]:
        """
        Fetch a new access token based on the configured platform.
        
        Returns:
            Tuple of (access_token, expiry_time)
        
        Raises:
            ValueError: If platform doesn't support token fetching
            requests.exceptions.RequestException: If token fetch fails
        """
        if self.platform == "cloud":
            return self._fetch_cloud_token()
        elif self.platform == "cpd":
            return self._fetch_cpd_token()
        else:
            raise ValueError(f"Token fetching not supported for platform: {self.platform}")
    
    def _ensure_valid_token(self) -> str:
        """
        Ensure we have a valid token, fetching new one if needed.
        
        Returns:
            Valid access token
        
        Raises:
            requests.exceptions.RequestException: If token fetch fails
        """
        # Try to get cached token
        token = self._token_cache.get()
        
        if token is not None:
            self.logger.debug("Using cached token")
            return token
        
        # Need to fetch new token
        self.logger.info("No valid cached token, fetching new one")
        token, expiry_time = self._fetch_new_token()
        
        # Cache the new token
        self._token_cache.set(token, expiry_time)
        
        return token
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers based on platform.
        
        For CPD platform: Uses bearer token with automatic refresh
        For cloud platform: Uses bearer token with automatic refresh
        
        Returns:
            Headers dictionary with authentication
        
        Raises:
            requests.exceptions.RequestException: If token fetch fails (for cpd/cloud)
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.platform == "local":
                # Basic authentication
                if self.username and self.password:
                    auth_string = f"{self.username}:{self.password}"
                    encoded_auth = base64.b64encode(auth_string.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded_auth}"
                    self.logger.debug("Using basic authentication")
                else:
                    self.logger.warning("Local platform configured but username/password not provided")
            
            elif self.platform in ["cpd", "cloud"]:
                # Bearer token with automatic refresh
                try:
                    token = self._ensure_valid_token()
                    headers["Authorization"] = f"Bearer {token}"
                    self.logger.debug(f"Using bearer token for {self.platform}")
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Failed to get authentication token for {self.platform}: {e}")
                    raise
                except Exception as e:
                    self.logger.error(f"Unexpected error getting authentication token for {self.platform}: {e}")
                    raise
            
            else:
                self.logger.warning(f"Unknown platform: {self.platform}, proceeding without authentication")
            
            return headers
            
        except Exception as e:
            self.logger.error(f"Critical error in get_auth_headers: {e}")
            # Re-raise to ensure caller knows authentication failed
            raise
    
    def invalidate_token(self) -> None:
        """
        Invalidate cached token, forcing refresh on next access.
        
        Useful when receiving 401 errors or when token is known to be invalid.
        """
        self.logger.info("Invalidating token")
        self._token_cache.invalidate()