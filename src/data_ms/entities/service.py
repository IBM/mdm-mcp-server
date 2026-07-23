# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Entity service for IBM MDM MCP server.

This module provides a service class that encapsulates entity-related business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, List, Optional

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from data_ms.adapters.data_ms_adapter import DataMSAdapter
from data_ms.search.service import SearchService

logger = logging.getLogger(__name__)


class EntityService(BaseService):
    """
    Service class for handling entity operations.
    
    This class extends BaseService and provides entity-specific functionality:
    - Entity retrieval via DataMSAdapter
    - Entity-specific error handling
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses DataMSAdapter for:
    - HTTP communication with Data Microservice
    - Entity endpoint operations
    
    The get_entity function in tools.py uses these methods to retrieve entities.
    """
    
    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        """
        Initialize the entity service with a Data MS adapter.
        
        Args:
            adapter: Optional DataMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or DataMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: DataMSAdapter = self.adapter  # type: ignore
        self._search_service = SearchService(self.adapter)
    
    def fetch_entity_from_api(
        self,
        entity_id: str,
        validated_crn: str
    ) -> Dict[str, Any]:
        """
        Fetch entity from the IBM MDM API via adapter.
        
        Args:
            entity_id: The ID of the entity to retrieve
            validated_crn: Validated Cloud Resource Name
            
        Returns:
            Entity data dictionary from the API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        return self.adapter.get_entity(entity_id, validated_crn)
    
    def get_entity(
        self,
        ctx: Context,
        entity_id: str,
        crn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get an entity by ID with declarative validation and error handling.
        
        This method orchestrates the entity retrieval process:
        1. Validates session and CRN
        2. Fetches entity from API
        3. Handles errors with standardized responses
        
        Args:
            ctx: MCP Context object with session information
            entity_id: The ID of the entity to retrieve
            crn: Cloud Resource Name identifying the tenant (optional)
            
        Returns:
            Entity data from IBM MDM or error response
        """
        try:
            # Validate session and CRN
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)
            
            self.logger.info(
                f"Getting entity with ID {entity_id} for tenant: {tenant_id} "
                f"(CRN: {validated_crn}), session: {session_id}"
            )
            
            # Fetch entity from API
            return self.fetch_entity_from_api(entity_id, validated_crn)
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "retrieve entity", {"entity_id": entity_id})
        
        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve entity")

    def get_entities_by_ids(
        self,
        ctx: Context,
        entity_ids: List[str],
        limit: int = 50,
        crn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get multiple entities by their IDs using the search API.

        Builds an OR query over all provided entity_ids and calls the search
        endpoint with return_type=results_as_entities so the full entity detail
        is returned for each matching id.

        Args:
            ctx: MCP Context object with session information
            entity_ids: List of entity IDs to retrieve
            limit: Maximum number of results to return (default 50, max 50)
            crn: Cloud Resource Name identifying the tenant (optional)

        Returns:
            Search results containing matched entities or error response
        """
        try:
            validated_ids = [
                eid.strip().split("-", 1)[1] if "-" in eid.strip() else eid.strip()
                for eid in entity_ids if eid and eid.strip()
            ]
            if not validated_ids:
                return {"error": "validation_error", "status_code": 400,
                        "message": "entity_ids must be a non-empty list of strings"}

            query = {
                "operation": "or",
                "expressions": [
                    {"property": "entity_id", "condition": "equal", "value": eid}
                    for eid in validated_ids
                ]
            }

            return self._search_service.search_master_data(
                ctx=ctx,
                search_type="entity",
                query=query,
                filters=None,
                limit=min(limit, 50),
                offset=0,
                include_total_count=True,
                crn=crn,
            )

        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}

        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve entities by ids")