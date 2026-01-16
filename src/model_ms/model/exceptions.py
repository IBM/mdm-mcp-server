# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Custom exceptions for Model Service operations.

This module defines specific exceptions for model service errors,
providing better error handling and clearer error messages.
"""

from typing import Dict, Any, Optional


class ModelServiceError(Exception):
    """Base exception for all model service errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize model service error.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DataModelFetchError(ModelServiceError):
    """Raised when data model fetch from API fails."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        crn: Optional[str] = None,
        version: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize data model fetch error.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code from the failed request
            crn: The CRN that was being used
            version: The data model version that was requested
            details: Optional dictionary with additional error context
        """
        self.status_code = status_code
        self.crn = crn
        self.version = version
        
        error_details = details or {}
        error_details.update({
            "status_code": status_code,
            "crn": crn,
            "version": version
        })
        
        super().__init__(message, error_details)


class InvalidFormatError(ModelServiceError):
    """Raised when an invalid format is specified for data model transformation."""
    
    def __init__(
        self,
        format: str,
        valid_formats: set,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize invalid format error.
        
        Args:
            format: The invalid format that was specified
            valid_formats: Set of valid format options
            details: Optional dictionary with additional error context
        """
        self.format = format
        self.valid_formats = valid_formats
        
        message = (
            f"Invalid format '{format}'. "
            f"Must be one of: {', '.join(sorted(valid_formats))}"
        )
        
        error_details = details or {}
        error_details.update({
            "invalid_format": format,
            "valid_formats": sorted(valid_formats)
        })
        
        super().__init__(message, error_details)