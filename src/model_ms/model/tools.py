# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Data model tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional, Union, Literal, List

from fastmcp import Context
from .service import ModelService

logger = logging.getLogger(__name__)

_model_service: Optional[ModelService] = None


def _get_model_service() -> ModelService:
    """Get or create the model service instance."""
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service


def get_data_model(
    ctx: Context,
    crn: Optional[str] = None,
    format: Optional[Literal["raw", "entity_attribute", "enhanced", "enhanced_compact"]] = "enhanced_compact"
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get the data model for the specified tenant.
    Data model defines the different attributes and their types for the tenant.
    It also includes whether an attribute is searchable or not.
    
    **IMPORTANT**: This tool MUST be called before using search_master_data. The search tool
    requires knowledge of the data model to construct valid property paths and understand
    available search fields.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        format: Format of the returned data model:
            - "raw": Return the raw data model as a dictionary
            - "entity_attribute": Return a simplified entity-attribute format as a list of entities
            - "enhanced": Return an enhanced entity-attribute format with complex attribute definitions
            - "enhanced_compact": Return an enhanced format without relationship types (RECOMMENDED for search)
    
    Returns:
        Data model for the specified tenant from IBM MDM, in the requested format
        
    Raises:
        CRNValidationError: If CRN validation fails
        InvalidFormatError: If invalid format is specified
        DataModelFetchError: If API request fails
        
    Examples:
        # Always call this first to understand the data structure
        # Using default On-Prem CRN
        data_model = get_data_model()
        
        # Using full CRN format
        data_model = get_data_model(
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )

        # To fetch the raw CRN
        data_model = get_data_model(
            format="raw"
        )
        
        # The session is automatically tracked via the Context object
        # Now you can use search_master_data in the same session
    """
    service = _get_model_service()
    return service.get_data_model(ctx, crn, format)
