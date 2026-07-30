# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Record tools for IBM MDM MCP server.
"""

import logging
from typing import Annotated, Dict, Any, List, Optional

from fastmcp import Context
from pydantic import Field
from .service import RecordService

logger = logging.getLogger(__name__)

_record_service = RecordService()

def get_record_by_id(
    ctx: Context,
    record_id: str,
    crn: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a record by `id` from IBM MDM.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        record_id: The ID of the record to retrieve
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        
    Returns:
        Record data from IBM MDM
        
    Examples:
        # Using default On-Prem CRN
        record = get_record_by_id(record_id="12345")
        
        # Using full CRN format
        record = get_record_by_id(
            record_id="12345",
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )
    """
    return _record_service.get_record_by_id(ctx, record_id, crn)


def get_records_entities_by_record_id(
    ctx: Context,
    record_id: str,
    crn: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all the entities for a given record ID.

    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        record_id: The ID of the record for which all the entities must be retrieved
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)

    Returns:
        All entities linked to the given record ID
        
    Examples:
        # Using default On-Prem CRN
        entities = get_records_entities_by_record_id(record_id="12345")
        
        # Using full CRN format
        entities = get_records_entities_by_record_id(
            record_id="12345",
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::"
        )
    """
    return _record_service.get_records_entities_by_record_id(ctx, record_id, crn)


def get_records_by_record_numbers(
    ctx: Context,
    record_ids: Annotated[List[str], Field(
        description="List of record numbers to retrieve details for"
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
    Get details for multiple records by their record numbers.

    Internally calls the search API with an OR query over all provided
    record_ids and returns full record details for each matched record_number.

    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        record_ids: List of record numbers whose details should be fetched
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        limit: Maximum number of records to return (1-50, default: 50)

    Returns:
        Search results with full record details for each matched record number

    Examples:
        get_records_by_record_numbers(record_ids=["15411783590721993", "19831783590743901", "16231783590739403"])
    """
    return _record_service.get_records_by_record_numbers(ctx, record_ids, limit, crn)


GET_RECORDS_BY_RECORD_NUMBERS_TOOL_DESCRIPTION = """
Retrieve full details for a list of records identified by their record numbers.

Builds an OR search query over all provided record_ids against the IBM MDM search API
(search_type="record") and returns the complete record for every matched record_number
in a single call.

**When to use this tool:**
- You have a collection of record numbers (e.g. from a `get_data_quality_issues` response)
  and need the full attribute details for each record.
- You want to batch-fetch all records belonging to an entity instead of calling get_record once per ID.

**Args:**
    record_ids: Non-empty list of record number strings to look up.
    crn:        Optional Cloud Resource Name (defaults to the configured tenant).
    limit:      Maximum records to return in one call (1-50, default 50).

**Returns:**
    A search result object with a `results` list — one entry per matched record —
    plus `total_count`, `limit`, and `offset` pagination metadata.
    On error an error object is returned with `error`, `status_code`, and `message` fields.

**Example:**
    get_records_by_record_numbers(record_ids=["15411783590721993", "19831783590743901", "16231783590739403"])
"""
