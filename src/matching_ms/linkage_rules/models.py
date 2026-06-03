# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Models for linkage rules preview in IBM MDM MCP server.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LinkageRule(BaseModel):
    """
    Model for a single linkage rule.
    
    Attributes:
        record_numbers: List of record numbers to link/unlink
        rule_type: Type of rule - 'link' or 'unlink'
        description: Optional description of the rule
    """
    record_numbers: List[str] = Field(
        ...,
        description="List of record numbers to link/unlink"
    )
    rule_type: str = Field(
        ...,
        description="Type of rule - 'link' or 'unlink'"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the rule"
    )


class LinkageRulesRequest(BaseModel):
    """
    Model for linkage rules preview request.
    
    Attributes:
        entity_type: The data type identifier of entity (e.g., person_entity, organization_entity)
        rules: Collection of linkage rules
        create_rule_for_non_existent_derived_data: Creates a rule when derived data is not present
    """
    entity_type: str = Field(
        ...,
        description="The data type identifier of entity (e.g., person_entity, organization_entity, household_entity)"
    )
    rules: List[LinkageRule] = Field(
        ...,
        description="Collection of linkage rules"
    )
    create_rule_for_non_existent_derived_data: Optional[bool] = Field(
        None,
        description="Creates a rule when derived data is not present"
    )


class LinkageRulesPreviewResponse(BaseModel):
    """
    Model for linkage rules preview response.
    
    The response contains a dictionary where:
    - Keys are entity type names (e.g., 'person_entity')
    - Values are dictionaries mapping entity IDs to lists of affected entity IDs
    """
    preview: Dict[str, Dict[str, List[str]]] = Field(
        ...,
        description="Preview of impacted entities by entity type"
    )

