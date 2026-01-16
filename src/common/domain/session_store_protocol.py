# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Session Store Protocol for dependency injection.

This module defines the interface that session store implementations must follow,
enabling dependency injection and easier testing.
"""

from typing import Protocol, Optional, Dict, Any


class SessionStoreProtocol(Protocol):
    """
    Protocol defining the interface for session store implementations.
    
    This allows for dependency injection and makes it easy to swap
    implementations or use mocks for testing.
    """
    
    def register_data_model_fetch(
        self,
        session_id: str,
        data_model: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register that a session has successfully fetched the data model.
        
        Args:
            session_id: Unique identifier for the session
            data_model: Optional data model to cache for validation purposes
        """
        ...
    
    def has_fetched_data_model(self, session_id: str) -> bool:
        """
        Check if a session has fetched the data model.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if the session has fetched the data model and it hasn't expired
        """
        ...
    
    def get_cached_data_model(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the cached data model for a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Cached data model or None if not found or expired
        """
        ...
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session from the store.
        
        Args:
            session_id: Unique identifier for the session
        """
        ...