# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Model service for IBM MDM MCP server.

This module provides a service class that encapsulates model-related business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from common.domain.session_store_protocol import SessionStoreProtocol
from common.domain.default_session_store import get_default_session_store
from model_ms.adapters.model_ms_adapter import ModelMSAdapter
from .formatters import (
    transform_to_entity_attribute_format,
    transform_to_enhanced_entity_attribute_format,
    transform_to_enhanced_compact_format
)
from .exceptions import DataModelFetchError, InvalidFormatError
from .config import ModelServiceConfig

logger = logging.getLogger(__name__)

# Format transformation strategy mapping
FORMAT_TRANSFORMERS = {
    "raw": lambda dm: dm,
    "entity_attribute": transform_to_entity_attribute_format,
    "enhanced": transform_to_enhanced_entity_attribute_format,
    "enhanced_compact": transform_to_enhanced_compact_format
}


class ModelService(BaseService):
    """
    Service class for handling data model operations.
    
    This class extends BaseService and provides model-specific functionality:
    - Data model retrieval via ModelMSAdapter
    - Data model format transformation
    - Session registration for data model fetches
    - Model-specific error handling
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses ModelMSAdapter for:
    - HTTP communication with Model Microservice
    - Data model endpoint operations
    
    The get_data_model function in tools.py uses these methods to retrieve data models.
    """
    
    def __init__(
        self,
        adapter: Optional[ModelMSAdapter] = None,
        session_store: Optional[SessionStoreProtocol] = None
    ):
        """
        Initialize the model service with dependencies.
        
        Args:
            adapter: Optional ModelMSAdapter instance (creates default if None)
            session_store: Optional session store implementation (creates default if None)
        """
        super().__init__(adapter or ModelMSAdapter())
        self.adapter: ModelMSAdapter  # Type hint for IDE/type checker
        self.session_store = session_store or get_default_session_store()
    
    def fetch_data_model_from_api(
        self,
        validated_crn: str,
        version: str = ModelServiceConfig.DEFAULT_VERSION
    ) -> Dict[str, Any]:
        """
        Fetch data model from the IBM MDM API via adapter.
        
        Args:
            validated_crn: Validated Cloud Resource Name
            version: Version of the data model to retrieve
            
        Returns:
            Raw data model dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.get_data_model(validated_crn, version)
    
    def apply_format_transformation(
        self,
        data_model: Dict[str, Any],
        format: Optional[str]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Apply format transformation to the data model.
        
        Args:
            data_model: Raw data model from API
            format: Requested format type (defaults to enhanced_compact if None)
            
        Returns:
            Transformed data model in the requested format
            
        Raises:
            InvalidFormatError: If an invalid format is specified
        """
        # Default to configured default format if None
        format = format or ModelServiceConfig.DEFAULT_FORMAT
        
        # Validate format using FORMAT_TRANSFORMERS keys
        if format not in FORMAT_TRANSFORMERS:
            raise InvalidFormatError(format, set(FORMAT_TRANSFORMERS.keys()))
        
        # Apply transformation
        return FORMAT_TRANSFORMERS[format](data_model)
    
    def _truncate_response_body(
        self,
        response_text: str,
        max_length: int = ModelServiceConfig.MAX_ERROR_RESPONSE_LENGTH
    ) -> Tuple[str, bool]:
        """
        Truncate response body if it exceeds max length.
        
        Args:
            response_text: The response text to truncate
            max_length: Maximum length before truncation
            
        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        if len(response_text) <= max_length:
            return response_text, False
        return f"{response_text[:max_length]}... (truncated)", True
    
    def _build_error_details(
        self,
        error: requests.exceptions.RequestException,
        crn: str,
        version: str
    ) -> Dict[str, Any]:
        """
        Build comprehensive error details dictionary.
        
        Args:
            error: The request exception that occurred
            crn: The CRN that was being used
            version: The data model version that was requested
            
        Returns:
            Dictionary with error details
        """
        details: Dict[str, Any] = {
            "error_type": type(error).__name__,
            "crn": crn,
            "version": version,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Add response details if available
        if hasattr(error, 'response') and error.response:
            details["http_status"] = error.response.status_code
            if error.response.text:
                body, truncated = self._truncate_response_body(error.response.text)
                details["response_body"] = body
                if truncated:
                    details["response_body_truncated"] = True
        
        return details
    
    def get_data_model(
        self,
        ctx: Context,
        crn: Optional[str] = None,
        format: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get the data model for the specified tenant with format transformation.
        
        This method orchestrates the data model retrieval process:
        1. Validates session and CRN
        2. Fetches data model from API via adapter
        3. Registers successful fetch in session store
        4. Applies format transformation
        
        Args:
            ctx: MCP Context object with session information
            crn: Cloud Resource Name identifying the tenant (optional, uses default if None)
            format: Format of the returned data model (optional, defaults to "enhanced_compact")
                Valid formats: "raw", "entity_attribute", "enhanced", "enhanced_compact"
            
        Returns:
            Data model in the requested format:
            - Dict[str, Any] for "raw", "enhanced", "enhanced_compact" formats
            - List[Dict[str, Any]] for "entity_attribute" format
            
        Raises:
            CRNValidationError: If CRN validation fails
            DataModelFetchError: If API request fails
            InvalidFormatError: If invalid format is specified
            
        Examples:
            >>> service = ModelService()
            >>> # Get data model with default format
            >>> model = service.get_data_model(ctx)
            >>>
            >>> # Get data model with specific CRN and format
            >>> model = service.get_data_model(
            ...     ctx,
            ...     crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::",
            ...     format="enhanced_compact"
            ... )
            >>> print(model["entity_types"])
        """
        # Validate CRN and extract tenant ID
        session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
        
        # Use configured default format if not specified
        format = format or ModelServiceConfig.DEFAULT_FORMAT
        
        self.logger.debug(
            "Fetching data model",
            extra={
                "tenant_id": tenant_id,
                "crn": validated_crn,
                "format": format,
                "session_id": session_id
            }
        )
        
        # Fetch data model from API
        try:
            data_model = self.fetch_data_model_from_api(
                validated_crn,
                version=ModelServiceConfig.DEFAULT_VERSION
            )
            
            # Register successful data model fetch for this session
            self.session_store.register_data_model_fetch(session_id, data_model)
            
            self.logger.debug(
                "Data model fetched successfully",
                extra={"session_id": session_id, "model_size": len(str(data_model))}
            )
            
            # Apply format transformation (may raise InvalidFormatError)
            return self.apply_format_transformation(data_model, format)
        
        except requests.exceptions.RequestException as e:
            # Log detailed error information
            self.logger.error(
                "Data model fetch failed",
                extra={
                    "crn": validated_crn,
                    "status_code": getattr(getattr(e, 'response', None), 'status_code', None),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            
            # Raise custom exception with full context
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else 500
            details = self._build_error_details(
                e,
                validated_crn,
                ModelServiceConfig.DEFAULT_VERSION
            )
            
            raise DataModelFetchError(
                message=f"Failed to retrieve data model for CRN '{validated_crn}' (version: {ModelServiceConfig.DEFAULT_VERSION}): {str(e)}",
                status_code=status_code,
                crn=validated_crn,
                version=ModelServiceConfig.DEFAULT_VERSION,
                details=details
            )