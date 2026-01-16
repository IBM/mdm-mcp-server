# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Configuration constants for Model Service.

This module centralizes all configuration values used by the Model Service,
making them easy to find, modify, and potentially make configurable via
environment variables or config files.
"""


class ModelServiceConfig:
    """Configuration constants for ModelService operations."""
    
    # Data model version
    DEFAULT_VERSION = "current"
    
    # Format settings
    DEFAULT_FORMAT = "enhanced_compact"
    
    # Error response settings
    MAX_ERROR_RESPONSE_LENGTH = 500
    
    # Session settings
    SESSION_ID_DEFAULT = "default"
    
    # Logging settings
    LOG_LEVEL_ROUTINE = "debug"  # For routine operations
    LOG_LEVEL_SUCCESS = "debug"  # For successful operations
    LOG_LEVEL_ERROR = "error"    # For errors