# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Record tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional

from fastmcp import Context
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

