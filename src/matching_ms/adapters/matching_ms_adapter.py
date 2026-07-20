# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Matching Microservice adapter for IBM MDM MCP server.

This module provides an adapter for communicating with the Matching Microservice,
handling matching operations.
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
    - Record comparison operations (compare by record numbers or record data)
    
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
        create_rule_for_non_existent_derived_data: bool = False
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
            create_rule_for_non_existent_derived_data: Whether to create rule for non-existent derived data (default: False)
            
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
        
        return self.execute_post("compare", body, params)
    
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
        
        return self.execute_post("linkage_rules_preview", body, params)
    
    def get_matching_algorithm(
        self,
        record_type: str,
        crn: str,
        template: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve the matching algorithm for a given record type.
        
        A matching algorithm contains the matching metadata for a given record type
        and is comprised of standardization, bucket generation and comparison sections.
        
        Args:
            record_type: The data type identifier of source records (e.g., 'person', 'organization', 'contract')
            crn: Cloud Resource Name identifying the tenant
            template: Response will return the default template algorithm when set to true (default: False)
            
        Returns:
            Algorithm dictionary containing:
            - locale: The request language and location
            - encryption: Asymmetric encryption configuration
            - standardizers: Collection of standardizer definitions
            - entity_types: Collection of entity type definitions
            - bucket_group_bit_length: Bit length for bucket group
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = f"algorithms/{record_type}"
        
        params = {
            "crn": crn,
            "template": str(template).lower()
        }
        
        self.logger.info(
            f"Fetching matching algorithm for record_type: {record_type}, "
            f"template: {template}, CRN: {crn}"
        )
        return self.execute_get(endpoint, params)

    def get_data_quality_issues(
        self,
        entity_type: str,
        crn: str,
        record_number: Optional[int] = None,
        entities: Optional[List[str]] = None,
        limit: int = 1,
        offset: int = 0,
        fetch_total_count: bool = True,
        include_tags: bool = False,
        include_record_attributes: Optional[str] = None,
        return_linked_issues: bool = True,
    ) -> Dict[str, Any]:
        """
        Retrieve list of data quality issues for given entities or record
        (GET /data_quality/issues).

        Args:
            entity_type: Required. Data type identifier of entity (e.g. "person_entity")
            crn: Cloud Resource Name identifying the tenant
            record_number: Unique identifier of a source record
            entities: List of entity identifiers (e.g. ["person_entity-12345678"])
            limit: Number of issues to retrieve (default: 1)
            offset: Number of issues to skip before returning results (default: 0)
            fetch_total_count: Return total issue count when True (default: True)
            include_tags: Include tag details in response (default: False)
            include_record_attributes: Comma-separated attribute names to include per entity
            return_linked_issues: Include issues where both records belong to the same entity (default: True)

        Returns:
            Paged data quality issues response dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "data_quality/issues"

        params: Dict[str, Any] = {
            "crn": crn,
            "entity_type": entity_type,
            "limit": str(limit),
            "offset": str(offset),
            "fetch_total_count": str(fetch_total_count).lower(),
            "include_tags": str(include_tags).lower(),
            "return_linked_issues": str(return_linked_issues).lower(),
        }

        if record_number is not None:
            params["record_number"] = str(record_number)

        # requests handles list params as repeated keys: ?entities=x&entities=y
        if entities:
            params["entities"] = entities

        if include_record_attributes is not None:
            params["include_record_attributes"] = include_record_attributes

        self.logger.info(
            "Fetching data quality issues for entity_type=%s, CRN=%s",
            entity_type,
            crn,
        )
        return self.execute_get(endpoint, params)
