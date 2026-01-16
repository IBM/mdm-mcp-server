# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Base service class for IBM MDM MCP server.

This module provides an abstract base class that encapsulates common service logic,
following the Template Method design pattern and Hexagonal Architecture principles.
"""

import logging
import requests
from typing import Dict, Any, Optional, Tuple
from abc import ABC

from fastmcp import Context

from common.domain.crn_validator import get_crn_with_precedence, CRNValidationError, format_crn_error_response
from common.models.error_models import create_api_error
from common.core.base_adapter import BaseMDMAdapter

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base service class providing common functionality for all services.
    
    This class implements the Template Method pattern and follows Hexagonal Architecture:
    - Common session and CRN validation
    - Common error handling patterns
    - Delegates HTTP communication to adapters (Ports & Adapters pattern)
    - Extension points for service-specific validation
    
    Subclasses must:
    - Provide an adapter instance in __init__
    - Override validate_additional_preconditions() if needed
    
    Attributes:
        adapter: The outbound adapter for API communication
        logger: Logger instance for this service
    """
    
    def __init__(self, adapter: BaseMDMAdapter):
        """
        Initialize the base service with an adapter.
        
        Args:
            adapter: The outbound adapter for API communication
        """
        self.adapter = adapter
        self.logger = logger
    
    def validate_session_and_crn(
        self,
        ctx: Context,
        crn: Optional[str],
        check_preconditions: bool = False
    ) -> Tuple[str, str, str]:
        """
        Validate session and CRN with optional precondition checks.
        
        This is a template method that:
        1. Extracts session ID from context
        2. Validates CRN
        3. Optionally calls validate_additional_preconditions() hook
        
        Args:
            ctx: MCP Context object with session information
            crn: Optional CRN to validate
            check_preconditions: Whether to check additional preconditions (default: False)
            
        Returns:
            Tuple of (session_id, validated_crn, tenant_id)
            
        Raises:
            CRNValidationError: If CRN validation fails
            Exception: If additional precondition checks fail (subclass-specific)
        """
        # Extract session identifier from context
        session_id = ctx.session_id or "default"
        
        # Validate CRN and extract tenant ID
        try:
            validated_crn, tenant_id = get_crn_with_precedence(crn)
        except CRNValidationError as e:
            self.logger.error(f"CRN validation failed: {str(e)}")
            raise CRNValidationError(format_crn_error_response(crn or "None", str(e)))
        
        # Hook for subclass-specific precondition checks
        if check_preconditions:
            self.validate_additional_preconditions(session_id, validated_crn)
        
        return session_id, validated_crn, tenant_id
    
    def validate_additional_preconditions(
        self,
        session_id: str,
        validated_crn: str
    ) -> None:
        """
        Hook method for subclasses to add additional validation.
        
        This method is called by validate_session_and_crn() when check_preconditions=True.
        Subclasses can override this to add service-specific validation logic.
        
        Args:
            session_id: The validated session ID
            validated_crn: The validated CRN
            
        Raises:
            Exception: Subclass-specific exceptions for failed preconditions
        """
        # Default implementation does nothing
        # Subclasses override this to add their own precondition checks
        pass
    
    
    def handle_api_error(
        self,
        error: requests.exceptions.RequestException,
        operation: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle API request errors with standardized logging and response formatting.
        
        Args:
            error: The request exception that occurred
            operation: Description of the operation that failed (e.g., "retrieve entity")
            context_data: Optional context data to include in error response
            
        Returns:
            Formatted error response dictionary
        """
        self.logger.error(f"Error during {operation}: {str(error)}")
        if hasattr(error, 'response') and error.response:
            self.logger.error(f"Response status: {error.response.status_code}")
            self.logger.error(f"Response body: {error.response.text}")
        
        api_details = context_data or {}
        api_details["response_text"] = error.response.text if hasattr(error, 'response') and error.response else None
        
        return create_api_error(
            message=f"Failed to {operation}: {str(error)}",
            status_code=error.response.status_code if hasattr(error, 'response') and error.response else 500,
            api_details=api_details
        )
    
    def handle_unexpected_error(
        self,
        error: Exception,
        operation: str
    ) -> Dict[str, Any]:
        """
        Handle unexpected errors with standardized logging and response formatting.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            
        Returns:
            Formatted error response dictionary
        """
        self.logger.error(f"Unexpected error during {operation}: {str(error)}", exc_info=True)
        return create_api_error(
            message=f"Unexpected error: {str(error)}",
            status_code=500,
            api_details={"error_type": type(error).__name__}
        )