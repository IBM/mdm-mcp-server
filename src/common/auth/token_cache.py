# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Pure token cache module - NO HTTP logic, NO platform knowledge.

This module provides a thread-safe cache for storing access tokens with expiry tracking.
It does NOT fetch tokens or make HTTP calls - that's the responsibility of AuthenticationManager.
"""

import logging
from typing import Optional
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class TokenCache:
    """
    Thread-safe token cache with expiry tracking.
    
    Responsibilities:
    - Store token and expiry time
    - Check if token is expired
    - Thread-safe access
    
    NOT responsible for:
    - Fetching tokens (AuthenticationManager's job)
    - Platform-specific logic (AuthenticationManager's job)
    - HTTP calls (AuthenticationManager's job)
    """
    
    # Proactively expire token 2 minutes before actual expiry
    EXPIRY_BUFFER_SECONDS = 120
    
    def __init__(self):
        """Initialize empty token cache."""
        self._token: Optional[str] = None
        self._expiry_time: Optional[datetime] = None
        self._lock = Lock()
    
    def get(self) -> Optional[str]:
        """
        Get cached token if valid, None if expired or not set.
        
        Returns:
            Token string if valid, None if expired or not cached
        """
        with self._lock:
            if self._token is None or self._expiry_time is None:
                logger.debug("No cached token")
                return None
            
            if datetime.now() >= self._expiry_time:
                logger.info("Cached token expired")
                return None
            
            logger.debug("Using cached token")
            return self._token
    
    def set(self, token: str, expires_at: datetime) -> None:
        """
        Cache a token with its expiry time.
        
        Args:
            token: Access token string
            expires_at: When the token expires (should already include buffer)
        """
        with self._lock:
            self._token = token
            self._expiry_time = expires_at
            logger.info(f"Token cached, expires at {expires_at}")
    
    def invalidate(self) -> None:
        """Clear cached token, forcing refresh on next access."""
        with self._lock:
            logger.info("Invalidating cached token")
            self._token = None
            self._expiry_time = None
    
    def is_expired(self) -> bool:
        """
        Check if cached token is expired.
        
        Returns:
            True if token is expired or not set, False if valid
        """
        with self._lock:
            if self._token is None or self._expiry_time is None:
                return True
            return datetime.now() >= self._expiry_time
