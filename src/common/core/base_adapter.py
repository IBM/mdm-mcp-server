# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Base adapter for IBM MDM API communication.

This module provides an abstract base class for all IBM MDM API adapters,
implementing common HTTP operations and error handling following the
Hexagonal Architecture (Ports & Adapters) pattern.

Uses AuthenticationManager for all authentication concerns via composition.
"""

import logging
import requests
from abc import ABC
from typing import Dict, Any, Optional

from config import Config
from common.auth.authentication_manager import AuthenticationManager

logger = logging.getLogger(__name__)


class BaseMDMAdapter(ABC):
    """
    Abstract base adapter for IBM MDM API communication.
    
    This class provides common HTTP operations for all IBM MDM microservice adapters:
    - GET, POST, PUT, DELETE request execution
    - Automatic authentication via AuthenticationManager
    - Automatic 401 retry with token refresh
    - Common error handling
    - SSL configuration
    - Timeout configuration
    
    Subclasses implement microservice-specific endpoints by using these base methods.
    
    Attributes:
        api_base_url: Base URL for IBM MDM APIs
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        _auth_manager: Authentication manager for handling auth
    """
    
    def __init__(
        self,
        api_base_url: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = False,
        auth_manager: Optional[AuthenticationManager] = None,
        use_shared_auth: bool = True
    ):
        """
        Initialize the base adapter.
        
        Args:
            api_base_url: Base URL for IBM MDM APIs (default from Config)
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Whether to verify SSL certificates (default: False for dev)
            auth_manager: Optional authentication manager (overrides use_shared_auth)
            use_shared_auth: Use shared auth manager (default: True for cache efficiency)
        """
        self.api_base_url = api_base_url or Config.API_BASE_URL
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.logger = logger
        
        # Authentication manager priority:
        # 1. Explicit auth_manager parameter (for testing/custom scenarios)
        # 2. Shared instance (default - maximizes cache efficiency)
        # 3. New instance (fallback - only if use_shared_auth=False)
        if auth_manager is not None:
            self._auth_manager = auth_manager
        elif use_shared_auth:
            from common.auth.authentication_manager import get_shared_auth_manager
            self._auth_manager = get_shared_auth_manager(
                timeout=timeout,
                verify_ssl=verify_ssl
            )
        else:
            self._auth_manager = AuthenticationManager(
                timeout=timeout,
                verify_ssl=verify_ssl
            )
    
    def build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint path.
        
        Args:
            endpoint: API endpoint path (e.g., "/entities/123")
            
        Returns:
            Full URL combining base URL and endpoint
        """
        # Remove leading slash from endpoint if present
        endpoint = endpoint.lstrip('/')
        return f"{self.api_base_url}/{endpoint}"
    
    def _execute_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Execute HTTP request with automatic 401 retry.
        
        If a 401 error is received, invalidates the token and retries once.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full URL to request
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # Get auth headers from auth manager
        headers = self._auth_manager.get_auth_headers()
        
        # Defensive check: ensure headers is a dict
        if headers is None:
            self.logger.error("Authentication manager returned None for headers, using empty dict")
            headers = {}
        
        # Merge with any custom headers
        if 'headers' in kwargs:
            custom_headers = kwargs['headers']
            if custom_headers is not None:
                headers.update(custom_headers)
            else:
                self.logger.warning("kwargs['headers'] is None, skipping merge")
        kwargs['headers'] = headers
        
        # Add timeout and SSL verification
        kwargs.setdefault('verify', self.verify_ssl)
        kwargs.setdefault('timeout', self.timeout)
        
        # Execute request
        response = requests.request(method, url, **kwargs)
        
        # Handle 401 by invalidating token and retrying once
        if response.status_code == 401:
            self.logger.warning("Got 401, invalidating token and retrying")
            self._auth_manager.invalidate_token()
            
            # Get fresh auth headers
            headers = self._auth_manager.get_auth_headers()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            
            # Retry request
            response = requests.request(method, url, **kwargs)
        
        return response
    
    def _log_transaction_id(self, response: requests.Response, method: str, endpoint: str) -> None:
        """
        Extract and log transaction ID from response headers.
        
        Args:
            response: The HTTP response object
            method: HTTP method used (GET, POST, etc.)
            endpoint: API endpoint called
        """
        # IBM MDM API returns transaction ID in X-Correlation-ID header
        transaction_id = response.headers.get('X-Correlation-ID')
        
        if transaction_id:
            self.logger.info(f"{method} {endpoint} - Transaction ID: {transaction_id}")
    
    def execute_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GET request to IBM MDM API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            headers: Optional custom headers (merged with auth headers)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self.build_url(endpoint)
        self.logger.debug(f"GET {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'GET',
            url,
            params=params,
            headers=headers
        )
        
        response.raise_for_status()
        
        # Log transaction ID for tracing
        self._log_transaction_id(response, 'GET', endpoint)
        
        return response.json()
    
    def execute_post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a POST request to IBM MDM API.
        
        Args:
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Optional query parameters
            headers: Optional custom headers (merged with auth headers)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self.build_url(endpoint)
        self.logger.debug(f"POST {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'POST',
            url,
            json=json_data,
            params=params,
            headers=headers
        )
        
        response.raise_for_status()
        
        # Log transaction ID for tracing
        self._log_transaction_id(response, 'POST', endpoint)
        
        return response.json()
    
    def execute_put(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a PUT request to IBM MDM API.
        
        Args:
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Optional query parameters
            headers: Optional custom headers (merged with auth headers)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self.build_url(endpoint)
        self.logger.debug(f"PUT {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'PUT',
            url,
            json=json_data,
            params=params,
            headers=headers
        )
        
        response.raise_for_status()
        
        # Log transaction ID for tracing
        self._log_transaction_id(response, 'PUT', endpoint)
        
        return response.json()
    
    def execute_delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a DELETE request to IBM MDM API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            headers: Optional custom headers (merged with auth headers)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self.build_url(endpoint)
        self.logger.debug(f"DELETE {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'DELETE',
            url,
            params=params,
            headers=headers
        )
        
        response.raise_for_status()
        
        # Log transaction ID for tracing
        self._log_transaction_id(response, 'DELETE', endpoint)
        
        return response.json()