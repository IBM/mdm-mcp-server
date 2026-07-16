# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Data Microservice adapter for IBM MDM MCP server.

This module provides an adapter for communicating with the Data Microservice,
handling entities, records, and search operations.
"""

import logging
from typing import Dict, Any, Optional, List
from urllib.parse import quote

from common.core.base_adapter import BaseMDMAdapter

logger = logging.getLogger(__name__)


class DataMSAdapter(BaseMDMAdapter):
    """
    Adapter for Data Microservice endpoints.
    
    This adapter provides methods for interacting with the Data Microservice:
    - Entity operations (get entity by ID)
    - Record operations (get record by ID, get entities for record)
    - Search operations (search records, entities, relationships, hierarchy nodes)
    
    All methods use the base adapter's HTTP execution methods and handle
    Data MS-specific endpoint construction and parameter formatting.
    """
    
    def get_entity(
        self,
        entity_id: str,
        crn: str
    ) -> Dict[str, Any]:
        """
        Get an entity by ID from the Data Microservice.
        
        Args:
            entity_id: The ID of the entity to retrieve
            crn: Cloud Resource Name identifying the tenant
            
        Returns:
            Entity data dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = f"entities/{quote(entity_id, safe='')}"
        params = {"crn": crn}
        
        self.logger.info(f"Fetching entity {entity_id} for CRN: {crn}")
        return self.execute_get(endpoint, params)
    
    def get_record(
        self,
        record_id: str,
        crn: str
    ) -> Dict[str, Any]:
        """
        Get a record by ID from the Data Microservice.
        
        Args:
            record_id: The ID of the record to retrieve
            crn: Cloud Resource Name identifying the tenant
            
        Returns:
            Record data dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = f"records/{quote(record_id, safe='')}"
        params = {"crn": crn}
        
        self.logger.info(f"Fetching record {record_id} for CRN: {crn}")
        return self.execute_get(endpoint, params)
    
    def get_record_entities(
        self,
        record_id: str,
        crn: str
    ) -> Dict[str, Any]:
        """
        Get all entities for a record from the Data Microservice.
        
        Args:
            record_id: The ID of the record to retrieve entities for
            crn: Cloud Resource Name identifying the tenant
            
        Returns:
            Entities data dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = f"records/{quote(record_id, safe='')}/entities"
        params = {"crn": crn}
        
        self.logger.info(f"Fetching entities for record {record_id} for CRN: {crn}")
        return self.execute_get(endpoint, params)
    
    def search_master_data(
        self,
        search_criteria: Dict[str, Any],
        crn: str,
        limit: int = 10,
        offset: int = 0,
        include_total_count: bool = True,
        include_attributes: Optional[List[str]] = None,
        exclude_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for master data (records, entities, relationships, hierarchy nodes) in the Data Microservice.
        
        Args:
            search_criteria: Search criteria dictionary containing query and filters
            crn: Cloud Resource Name identifying the tenant
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            include_total_count: Whether to include total count in response
            include_attributes: Optional list of attributes to include in results
            exclude_attributes: Optional list of attributes to exclude from results
            
        Returns:
            Search results dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "search"
        
        # Map search_type to return_type for the API
        search_type = search_criteria.get('search_type', 'record')
        return_type_map = {
            "record": "results",
            "entity": "results_as_entities",
            "hierarchy_node": "results_as_hierarchy_nodes",
            "relationship": "results"
        }
        return_type = return_type_map.get(search_type, "results")
        
        params: Dict[str, Any] = {
            "crn": crn,
            "limit": str(limit),
            "offset": str(offset),
            "include_total_count": str(include_total_count).lower(),
            "return_type": return_type
        }
        
        # Add include/exclude attributes if provided
        # Note: requests library handles lists by creating multiple params with same name
        # e.g., ?include=attr1&include=attr2
        if include_attributes:
            params["include"] = include_attributes
        
        if exclude_attributes:
            params["exclude"] = exclude_attributes
        
        self.logger.info(
            f"Searching {search_type} for CRN: {crn}, "
            f"return_type: {return_type}"
        )
        return self.execute_post(endpoint, search_criteria, params)

    def federated_search(
        self,
        query: Dict[str, Any],
        crn: str,
        limit: int = 10,
        offset: int = 0,
        include_total_count: bool = True,
        issue_type: str = "potential_match",
        timezone: str = "UTC",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Perform a federated search for data quality issues (e.g., potential matches).

        Args:
            query: Search query containing expressions (same structure as search_master_data)
            crn: Cloud Resource Name identifying the tenant
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            include_total_count: Whether to include total count in response
            issue_type: Type of data quality issue ("potential_match")
            timezone: Timezone for date/time values
            sort_order: Sort order — "asc" or "desc"

        Returns:
            Federated search results with potential_match_issues and pagination info

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "federated_search"

        params: Dict[str, Any] = {
            "crn": crn,
            "limit": str(limit),
            "offset": str(offset),
            "include_total_count": str(include_total_count).lower(),
            "issue_type": issue_type,
            "timezone": timezone,
            "sort_order": sort_order,
        }

        body = {"search_type": "issue", "query": query}

        self.logger.info(
            "Federated search for issue_type=%s, CRN=%s",
            issue_type,
            crn,
        )
        return self.execute_post(endpoint, body, params)

    def get_quality_issues(
        self,
        issue_type: str,
        crn: str,
        entity_type: Optional[str] = None,
        entity_type_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
        include_total_count: bool = True,
        include_total_count_without_tasks: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve data quality issues for a given issue type (POST /quality_issues).

        Args:
            issue_type: The type of quality issue to search for (required query param)
            crn: Cloud Resource Name identifying the tenant
            entity_type: Optional entity type to include in the request body (e.g. "record")
            entity_type_name: Optional entity type name as defined in workflow configuration
            offset: Number of issues to skip for pagination
            limit: Maximum number of issues to return (max 50)
            include_total_count: Whether to include total count on non-first pages
            include_total_count_without_tasks: Whether to include total count without tasks

        Returns:
            Paged quality issues response dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        endpoint = "quality_issues"

        params: Dict[str, Any] = {
            "crn": crn,
            "issue_type": issue_type,
            "offset": str(offset),
            "limit": str(limit),
            "include_total_count": str(include_total_count).lower(),
            "include_total_count_without_tasks": str(include_total_count_without_tasks).lower(),
        }

        body: Dict[str, Any] = {"type": issue_type}
        if entity_type is not None:
            body["type"] = entity_type  # entity_type overrides the issue_type in the body per API spec
        if entity_type_name is not None:
            body["type_name"] = entity_type_name

        self.logger.info(
            "Fetching quality issues for issue_type=%s, CRN=%s",
            issue_type,
            crn,
        )
        return self.execute_post(endpoint, body, params)
