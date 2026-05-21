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
        endpoint = f"entities/{entity_id}"
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
        endpoint = f"records/{record_id}"
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
        endpoint = f"records/{record_id}/entities"
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
    