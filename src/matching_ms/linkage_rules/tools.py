# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Linkage rules tools for IBM MDM MCP server.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from fastmcp import Context
from .service import LinkageRulesService
from .models import LinkageRule, LinkageRulesPreviewResponse

logger = logging.getLogger(__name__)

_linkage_rules_service = LinkageRulesService()

def preview_linkage_rules(
    ctx: Context,
    entity_type: str,
    rules: List[LinkageRule],
    crn: Optional[str] = None,
    create_rule_for_non_existent_derived_data: Optional[bool] = None
) -> Union[LinkageRulesPreviewResponse, Dict[str, Any]]:
    """
    Preview entity composition by hypothesizing one or more manual link/unlink rules.
    
    This tool provides a preview of the impacted entities without actually applying the rules.
    It helps you understand what entities would be affected if you were to apply the specified
    linkage rules (link or unlink operations).
    
    The preview shows:
    - Which entities would be created or modified
    - How records would be grouped into entities
    - The impact of linking or unlinking specific records
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        entity_type: The data type identifier of entity (e.g., 'person_entity', 'organization_entity', 'household_entity')
        rules: Collection of linkage rules, each rule is a dictionary containing:
            - record_numbers: List of record numbers to link/unlink (required)
            - rule_type: Type of rule - 'link' or 'unlink' (required)
            - description: Optional description of the rule
        crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
        create_rule_for_non_existent_derived_data: Creates a rule when derived data is not present (optional)
        
    Returns:
        Preview results from IBM MDM showing impacted entities:
        - Dictionary mapping entity type to entity composition
        - Each entity ID maps to a list of entity IDs that would be affected
        
    Examples:
        # Preview unlinking a record from an entity
        result = preview_linkage_rules(
            entity_type="person_entity",
            rules=[
                {
                    "record_numbers": ["32995408531474430"],
                    "rule_type": "unlink",
                    "description": "Unlink incorrect record"
                }
            ]
        )
        
        # Preview linking multiple records together
        result = preview_linkage_rules(
            entity_type="person_entity",
            rules=[
                {
                    "record_numbers": ["123456789", "987654321"],
                    "rule_type": "link",
                    "description": "Link duplicate records"
                }
            ]
        )
        
        # Preview multiple rules at once
        result = preview_linkage_rules(
            entity_type="organization_entity",
            rules=[
                {
                    "record_numbers": ["111", "222"],
                    "rule_type": "link",
                    "description": "Link related organizations"
                },
                {
                    "record_numbers": ["333"],
                    "rule_type": "unlink",
                    "description": "Unlink incorrect organization"
                }
            ]
        )
        
        # Preview with full CRN
        result = preview_linkage_rules(
            entity_type="person_entity",
            rules=[
                {
                    "record_numbers": ["12345"],
                    "rule_type": "unlink"
                }
            ],
            crn="crn:v1:staging:public:mdm-oc:us-south:a/account123:instance456::",
            create_rule_for_non_existent_derived_data=True
        )
        
    Response Format:
        {
            "person_entity": {
                "35678330629897216": [],
                "35678327655087104": [
                    "35678330629897216",
                    "35678327655087104"
                ]
            }
        }
        
        In this example:
        - Entity "35678330629897216" would become empty (no records)
        - Entity "35678327655087104" would contain both entity IDs
    """
    # Convert Pydantic models to dictionaries for service layer
    rules_dicts = [rule.model_dump() for rule in rules]
    
    return _linkage_rules_service.preview_linkage_rules(
        ctx,
        entity_type,
        rules_dicts,
        crn,
        create_rule_for_non_existent_derived_data
    )

