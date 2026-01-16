# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Session store for tracking data model fetches across MCP tool calls.

This module maintains a global dictionary to track which sessions have
successfully fetched the data model. This ensures that search operations
can only be performed after the data model has been retrieved.
"""

import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)

# Global session store
# Key: session_id, Value: timestamp of last data model fetch
_data_model_sessions: Dict[str, datetime] = {}
# Key: session_id, Value: cached data model
_cached_data_models: Dict[str, Dict[str, Any]] = {}
_session_lock = Lock()

# Session timeout (in hours)
SESSION_TIMEOUT_HOURS = 24


def register_data_model_fetch(session_id: str, data_model: Optional[Dict[str, Any]] = None) -> None:
    """
    Register that a session has successfully fetched the data model.
    
    Args:
        session_id: Unique identifier for the session
        data_model: Optional data model to cache for validation purposes
    """
    with _session_lock:
        _data_model_sessions[session_id] = datetime.now()
        if data_model:
            _cached_data_models[session_id] = data_model
        logger.info(f"Registered data model fetch for session: {session_id}")


def has_fetched_data_model(session_id: str) -> bool:
    """
    Check if a session has fetched the data model.
    
    Args:
        session_id: Unique identifier for the session
        
    Returns:
        True if the session has fetched the data model and it hasn't expired
    """
    with _session_lock:
        if session_id not in _data_model_sessions:
            return False
        
        # Check if the session has expired
        fetch_time = _data_model_sessions[session_id]
        if datetime.now() - fetch_time > timedelta(hours=SESSION_TIMEOUT_HOURS):
            logger.warning(f"Session {session_id} data model fetch has expired")
            del _data_model_sessions[session_id]
            return False
        
        return True


def get_cached_data_model(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the cached data model for a session.
    
    Args:
        session_id: Unique identifier for the session
        
    Returns:
        Cached data model or None if not found or expired
    """
    with _session_lock:
        if session_id not in _cached_data_models:
            return None
        
        # Check if the session has expired
        if session_id in _data_model_sessions:
            fetch_time = _data_model_sessions[session_id]
            if datetime.now() - fetch_time > timedelta(hours=SESSION_TIMEOUT_HOURS):
                logger.warning(f"Session {session_id} data model cache has expired")
                if session_id in _cached_data_models:
                    del _cached_data_models[session_id]
                return None
        
        return _cached_data_models[session_id]


def clear_session(session_id: str) -> None:
    """
    Clear a session from the store.
    
    Args:
        session_id: Unique identifier for the session
    """
    with _session_lock:
        if session_id in _data_model_sessions:
            del _data_model_sessions[session_id]
        if session_id in _cached_data_models:
            del _cached_data_models[session_id]
        logger.info(f"Cleared session: {session_id}")


def get_active_sessions() -> Set[str]:
    """
    Get all active session IDs.
    
    Returns:
        Set of active session IDs
    """
    with _session_lock:
        # Clean up expired sessions
        now = datetime.now()
        expired = [
            sid for sid, fetch_time in _data_model_sessions.items()
            if now - fetch_time > timedelta(hours=SESSION_TIMEOUT_HOURS)
        ]
        for sid in expired:
            del _data_model_sessions[sid]
        
        return set(_data_model_sessions.keys())


def clear_all_sessions() -> None:
    """
    Clear all sessions from the store.
    Useful for testing or maintenance.
    """
    with _session_lock:
        _data_model_sessions.clear()
        _cached_data_models.clear()
        logger.info("Cleared all sessions")


