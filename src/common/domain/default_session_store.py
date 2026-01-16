# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Default session store implementation.

This module provides a concrete implementation of SessionStoreProtocol
that wraps the existing session_store module functions.
"""

from typing import Optional, Dict, Any
from . import session_store
from .session_store_protocol import SessionStoreProtocol


class DefaultSessionStore:
    """
    Default implementation of SessionStoreProtocol.
    
    This class wraps the existing session_store module functions,
    providing a class-based interface for dependency injection.
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
        session_store.register_data_model_fetch(session_id, data_model)
    
    def has_fetched_data_model(self, session_id: str) -> bool:
        """
        Check if a session has fetched the data model.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if the session has fetched the data model and it hasn't expired
        """
        return session_store.has_fetched_data_model(session_id)
    
    def get_cached_data_model(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the cached data model for a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Cached data model or None if not found or expired
        """
        return session_store.get_cached_data_model(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session from the store.
        
        Args:
            session_id: Unique identifier for the session
        """
        session_store.clear_session(session_id)


# Singleton instance for default use
_default_session_store: Optional[DefaultSessionStore] = None


def get_default_session_store() -> SessionStoreProtocol:
    """
    Get the default session store instance (singleton).
    
    Returns:
        Default session store implementation
    """
    global _default_session_store
    if _default_session_store is None:
        _default_session_store = DefaultSessionStore()
    return _default_session_store