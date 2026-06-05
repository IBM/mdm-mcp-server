# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Linkage rule tools for IBM MDM MCP server.

This module provides MCP tool definitions for entity resolution operations.
"""

import logging
from typing import Dict, Any, Optional, Literal, List

from fastmcp import Context
from .service import LinkageRuleService

logger = logging.getLogger(__name__)

_linkage_rules_service = LinkageRuleService()


def apply_linkage_rules(
    ctx: Context,
    entity_type: str,
    rule_type: Literal["link", "unlink", "merge", "unmerge"],
    record_numbers: List[str],
    description: str,
    crn: Optional[str] = None,
    create_rule_for_non_existent_derived_data: bool = False
) -> Dict[str, Any]:
    """
    Apply a linkage rule to resolve entity relationships in IBM MDM.
    
    This tool allows you to perform entity resolution operations by applying
    linkage rules to a set of records. It supports link, unlink, merge, and
    unmerge actions to manage entity relationships.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        entity_type: The entity type (e.g., "us_bank_entity", "person", "organization")
        rule_type: The type of linkage rule to apply:
            - "link": Create a relationship link between records
            - "unlink": Remove a relationship link between records
            - "merge": Merge records into a single entity
            - "unmerge": Separate previously merged records
        record_numbers: List of record numbers to apply the rule to (minimum 2 records)
        description: Description of the rule for documentation purposes (required)
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        create_rule_for_non_existent_derived_data: Whether to create rule for non-existent derived data (default: False)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating whether the operation succeeded
            - action: The action that was performed
            - entity_state: Current state of the entities after the operation
        
    Raises:
        CRNValidationError: If CRN validation fails
        RequestException: If the API request fails
        
    Examples:
        # Link two records
        result = apply_linkage_rules(
            entity_type="us_bank_entity",
            rule_type="link",
            record_numbers=["REC001", "REC002"]
        )
        
        # Merge multiple records with description
        result = apply_linkage_rules(
            entity_type="person",
            rule_type="merge",
            record_numbers=["REC001", "REC002", "REC003"],
            description="Merging duplicate person records"
        )
        
        # Unlink records with specific CRN
        result = apply_linkage_rules(
            entity_type="organization",
            rule_type="unlink",
            record_numbers=["REC001", "REC002"],
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::",
            description="Unlinking incorrectly linked organizations"
        )
        
        # The session is automatically tracked via the Context object
    """
    return _linkage_rules_service.apply_linkage_rules(
        ctx=ctx,
        entity_type=entity_type,
        rule_type=rule_type,
        record_numbers=record_numbers,
        description=description,
        crn=crn,
        create_rule_for_non_existent_derived_data=create_rule_for_non_existent_derived_data
    )
