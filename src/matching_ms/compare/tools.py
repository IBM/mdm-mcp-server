# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Compare tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional, List

from fastmcp import Context
from .service import CompareService

logger = logging.getLogger(__name__)

_compare_service = CompareService()

def compare_records(
    ctx: Context,
    entity_type: str,
    record_type: str = "person",
    record_number1: Optional[str] = None,
    record_number2: Optional[str] = None,
    records: Optional[List[Dict[str, Any]]] = None,
    crn: Optional[str] = None,
    details: str = "low"
) -> Dict[str, Any]:
    """
    Compare two records in IBM MDM to analyze their similarity and matching attributes.
    
    This tool supports two comparison modes:
    1. Compare by record numbers (using record_number1 and record_number2)
    2. Compare by record data (using records array with full record attributes)
    
    The comparison returns:
    - Overall comparison score
    - Score category (matched, potential_match, etc.)
    - Similarity percentage
    - Detailed comparison methods and their contributions
    - Post-filter methods and distances
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        entity_type: The entity type for the records (e.g., 'person_entity', 'organization_entity')
        record_type: The record type (e.g., 'person', 'organization') (default: 'person')
        record_number1: The record number of the first record (for record number comparison)
        record_number2: The record number of the second record (for record number comparison)
        records: Array of record objects with full attributes (for record data comparison)
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        details: Level of detail - 'low', 'high', or 'debug' (default: 'low')
        
    Returns:
        Comparison results from IBM MDM including:
        - score: Overall comparison score
        - score_category: Category of the match
        - similarity: Similarity percentage
        - compare_methods: Detailed comparison methods used
        - comparison_post_filter_methods: Post-filter methods applied
        
    Examples:
        # Compare by record numbers
        result = compare_records(
            entity_type="person_entity",
            record_type="person",
            record_number1="123456789",
            record_number2="123456790"
        )
        
        # Compare with full record data
        result = compare_records(
            entity_type="person_entity",
            record_type="person",
            records=[
                {
                    "record_type": "person",
                    "attributes": {
                        "record_source": "MDM",
                        "record_id": "6",
                        "legal_name": [{
                            "given_name": "Bobby",
                            "last_name": "Brown"
                        }]
                    }
                },
                {
                    "record_type": "person",
                    "attributes": {
                        "record_source": "MDMx",
                        "record_id": "7",
                        "legal_name": [{
                            "given_name": "Boby",
                            "last_name": "Brown"
                        }]
                    }
                }
            ]
        )
        
        # Compare with full CRN and debug details
        result = compare_records(
            entity_type="person_entity",
            record_type="person",
            record_number1="12345",
            record_number2="67890",
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::",
            details="debug"
        )
    """
    return _compare_service.compare_records(
        ctx,
        entity_type,
        record_type,
        record_number1,
        record_number2,
        records,
        crn,
        details
    )
