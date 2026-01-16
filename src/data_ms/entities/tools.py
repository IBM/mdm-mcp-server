# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Entity tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional

from fastmcp import Context
from .service import EntityService

logger = logging.getLogger(__name__)

_entity_service = EntityService()

def get_entity(
    ctx: Context,
    entity_id: str,
    crn: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get an entity by `entity_id` from IBM MDM.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        entity_id: The ID of the entity to retrieve
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        
    Returns:
        Entity data from IBM MDM
        
    Examples:
        # Using default On-Prem CRN
        entity = get_entity(entity_id="12345")
        
        # Using full CRN format
        entity = get_entity(
            entity_id="12345",
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )
    """
    return _entity_service.get_entity(ctx, entity_id, crn)


