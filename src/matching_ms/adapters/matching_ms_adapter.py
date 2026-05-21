# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Matching Microservice adapter for IBM MDM MCP server.

This module provides an adapter for communicating with the Matching Microservice,
handling linkage rule operations for entity resolution.
"""

import logging
from typing import Dict, Any, Optional, List

from common.core.base_adapter import BaseMDMAdapter

logger = logging.getLogger(__name__)


class MatchingMSAdapter(BaseMDMAdapter):
    """
    Adapter for Matching Microservice endpoints.
    
    This adapter provides methods for interacting with the Matching Microservice:
    - Linkage rule operations (apply linkage rules for entity resolution)
    
    All methods use the base adapter's HTTP execution methods and handle
    Matching MS-specific endpoint construction and parameter formatting.
    """
    
    def apply_linkage_rules(
        self,
        entity_type: str,
        rule_type: str,
        record_numbers: List[str],
        crn: str,
        description: str,
        create_rule_for_non_existent_derived_data: bool = True
    ) -> Dict[str, Any]:
        """
        Apply a linkage rule to resolve entity relationships.
        
        This method calls the PUT /mdm/v1/linkage_rules endpoint to apply
        a linkage rule decision (link, unlink, merge, unmerge) between entities.
        
        Args:
            entity_type: The entity type (e.g., "us_bank_entity")
            rule_type: Type of rule to apply (link, unlink, merge, unmerge)
            record_numbers: List of record numbers to apply the rule to
            crn: Cloud Resource Name identifying the tenant
            description: Description of the rule (required)
            create_rule_for_non_existent_derived_data: Whether to create rule for non-existent derived data (default: True)
            
        Returns:
            Response dictionary containing:
                - success: Boolean indicating operation success
                - action: The action that was performed
                - entity_state: Current state of the entities after the operation
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "linkage_rules"
        
        # Build rule object
        rule = {
            "rule_type": rule_type,
            "record_numbers": record_numbers,
            "description": description
        }
        
        # Build request body according to API specification
        request_body = {
            "entity_type": entity_type,
            "rules": [rule],
            "create_rule_for_non_existent_derived_data": create_rule_for_non_existent_derived_data
        }
        
        # Build query parameters
        params = {"crn": crn}
        
        self.logger.info(
            f"Applying linkage rule: rule_type={rule_type}, "
            f"entity_type={entity_type}, record_numbers={record_numbers}, "
            f"CRN: {crn}"
        )
        self.logger.info(f"Request body: {request_body}")
        self.logger.info(f"Query params: {params}")
        
        return self.execute_put(endpoint, request_body, params)