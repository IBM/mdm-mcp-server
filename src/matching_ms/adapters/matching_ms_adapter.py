# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Matching Microservice adapter for IBM MDM MCP server.

This module provides an adapter for communicating with the Matching Microservice,
handling record comparison operations.
"""

import logging
from typing import Dict, Any, Optional, List

from common.core.base_adapter import BaseMDMAdapter

logger = logging.getLogger(__name__)


class MatchingMSAdapter(BaseMDMAdapter):
    """
    Adapter for Matching Microservice endpoints.
    
    This adapter provides methods for interacting with the Matching Microservice:
    - Record comparison operations (compare by record numbers or record data)
    
    All methods use the base adapter's HTTP execution methods and handle
    Matching MS-specific endpoint construction and parameter formatting.
    """
    
    def compare_records(
        self,
        entity_type: str,
        record_type: str,
        crn: str,
        details: str = "low",
        record_number1: Optional[str] = None,
        record_number2: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compare two records in the Matching Microservice.
        
        This endpoint supports two comparison modes:
        1. Compare by record numbers: Provide record_number1 and record_number2
        2. Compare by record data: Provide records array with full record attributes
        
        The endpoint returns detailed comparison information including:
        - Overall comparison score
        - Score category (matched, potential_match, etc.)
        - Similarity percentage
        - Detailed comparison methods and their contributions
        - Post-filter methods and distances
        
        Args:
            entity_type: The entity type for the records (e.g., 'person_entity', 'organization_entity')
            record_type: The record type (e.g., 'person', 'organization')
            crn: Cloud Resource Name identifying the tenant
            details: Level of detail in response - 'low', 'high', or 'debug' (default: 'low')
            record_number1: First record number (for record number comparison)
            record_number2: Second record number (for record number comparison)
            records: Array of record objects with full attributes (for record data comparison)
            
        Returns:
            Comparison results dictionary with score, score_category, similarity, etc.
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # Build URL manually to avoid double slash issue
        # Remove trailing slash from base URL if present
        base_url = self.api_base_url.rstrip('/')
        url = f"{base_url}/compare"
        
        params = {
            "details": details,
            "crn": crn,
            "entity_type": entity_type,
            "record_type": record_type
        }
        
        # Add record numbers to params if provided (Mode 1: Compare by record numbers)
        if record_number1 is not None:
            params["record_number1"] = record_number1
        if record_number2 is not None:
            params["record_number2"] = record_number2
        
        # Prepare request body
        if records is not None and len(records) > 0:
            # Mode 2: Compare by record data - send records in body
            body = {"records": records}
            self.logger.info(
                f"Comparing {len(records)} record(s) by data "
                f"for entity_type: {entity_type}, record_type: {record_type}, CRN: {crn}"
            )
        else:
            # Mode 1: Compare by record numbers - send empty records array
            body = {"records": []}
            self.logger.info(
                f"Comparing records {record_number1} and {record_number2} "
                f"for entity_type: {entity_type}, record_type: {record_type}, CRN: {crn}"
            )
        
        # Use direct request execution instead of execute_post to use custom URL
        self.logger.debug(f"POST {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'POST',
            url,
            json=body,
            params=params
        )
        
        response.raise_for_status()
        return response.json()
    
    def preview_linkage_rules(
        self,
        entity_type: str,
        rules: List[Dict[str, Any]],
        crn: str,
        create_rule_for_non_existent_derived_data: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Preview entity composition by hypothesizing linkage rules.
        
        This endpoint provides a preview of the impacted entities by hypothesizing
        one or more manual link/unlink rules without actually applying them.
        
        Args:
            entity_type: The data type identifier of entity (e.g., 'person_entity', 'organization_entity')
            rules: Collection of linkage rules, each containing:
                - record_numbers: List of record numbers to link/unlink
                - rule_type: Type of rule - 'link' or 'unlink'
                - description: Optional description of the rule
            crn: Cloud Resource Name identifying the tenant
            create_rule_for_non_existent_derived_data: Creates a rule when derived data is not present
            
        Returns:
            Preview results dictionary mapping entity IDs to lists of affected entity IDs
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # Build URL manually to avoid double slash issue
        base_url = self.api_base_url.rstrip('/')
        url = f"{base_url}/linkage_rules_preview"
        
        params = {"crn": crn}
        
        # Prepare request body
        body: Dict[str, Any] = {
            "entity_type": entity_type,
            "rules": rules
        }
        
        if create_rule_for_non_existent_derived_data is not None:
            body["create_rule_for_non_existent_derived_data"] = create_rule_for_non_existent_derived_data
        
        self.logger.info(
            f"Previewing linkage rules for entity_type: {entity_type}, "
            f"rules count: {len(rules)}, CRN: {crn}"
        )
        
        self.logger.debug(f"POST {url} with params: {params}")
        
        response = self._execute_request_with_retry(
            'POST',
            url,
            json=body,
            params=params
        )
        
        response.raise_for_status()
        return response.json()

