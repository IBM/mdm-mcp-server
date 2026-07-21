# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Entity tools for IBM MDM MCP server.
"""

import logging
from typing import Annotated, Dict, Any, List, Optional

from fastmcp import Context
from pydantic import Field
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


def get_entities_by_ids(
    ctx: Context,
    entity_ids: Annotated[List[str], Field(
        description="List of entity IDs to retrieve details for"
    )],
    crn: Annotated[Optional[str], Field(
        description="Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)"
    )] = None,
    limit: Annotated[int, Field(
        ge=1,
        le=50,
        description="Maximum number of results to return (1-50, default: 50)"
    )] = 50,
) -> Dict[str, Any]:
    """
    Get details for multiple entities by their entity IDs.

    Internally calls the search API with an OR query over all provided
    entity_ids and returns full entity details for each matched ID.

    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        entity_ids: List of entity IDs whose details should be fetched
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        limit: Maximum number of entities to return (1-50, default: 50)

    Returns:
        Search results with full entity details for each matched ID

    Examples:
        # Fetch details for three entities
        get_entities_by_ids(entity_ids=["entity-001", "entity-002", "entity-003"])

        # With explicit CRN and custom limit
        get_entities_by_ids(
            entity_ids=["entity-001", "entity-002"],
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::",
            limit=10
        )
    """
    return _entity_service.get_entities_by_ids(ctx, entity_ids, limit, crn)


GET_ENTITIES_BY_IDS_TOOL_DESCRIPTION = """
Retrieve full details for a list of entities identified by their entity IDs.

Builds an OR search query over all provided IDs against the IBM MDM search API
(search_type="record", return_type=results_as_entities) and returns the complete
entity record for every matched ID in a single call.

**When to use this tool:**
- You have a collection of entity IDs (e.g. from a previous search result) and need the full
  attribute details for each entity.
- You want to bulk-fetch entities instead of calling get_entity once per ID.

**Args:**
    entity_ids: Non-empty list of entity ID strings to look up.
    crn:        Optional Cloud Resource Name (defaults to the configured tenant).
    limit:      Maximum entities to return in one call (1-50, default 50).

**Returns:**
    A search result object with a `results` list — one entry per matched entity —
    plus `total_count`, `limit`, and `offset` pagination metadata.
    On error an error object is returned with `error`, `status_code`, and `message` fields.

**Example:**
    get_entities_by_ids(entity_ids=["entity-001", "entity-002", "entity-003"])
"""
