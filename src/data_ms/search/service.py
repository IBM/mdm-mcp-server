# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Search service for IBM MDM MCP server.

This module provides a service class that encapsulates search-related business logic,
separating concerns from the tool interface layer and following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional, List, Literal

from fastmcp import Context
from pydantic import ValidationError

from common.core.base_service import BaseService
from common.domain.session_store import has_fetched_data_model
from common.domain.crn_validator import CRNValidationError
from common.models.error_models import (
    create_data_model_precondition_error,
    create_validation_error,
    create_api_error
)
from data_ms.adapters.data_ms_adapter import DataMSAdapter
from .validators import validate_search_query
from .models import SearchCriteria, SearchQuery, SearchFilter

logger = logging.getLogger(__name__)


class PreconditionFailedError(Exception):
    """
    Raised when a precondition for an operation is not met.
    
    This exception carries the error response dict that should be returned to the user.
    """
    def __init__(self, error_response: Dict[str, Any]):
        self.error_response = error_response
        super().__init__(error_response.get("message", "Precondition failed"))


class SearchService(BaseService):
    """
    Service class for handling search operations.
    
    This class extends BaseService and provides search-specific functionality:
    - Data model precondition validation (overrides base class hook)
    - Search criteria building and validation
    - Search API request execution via DataMSAdapter
    
    Inherits from BaseService:
    - Session and CRN validation
    - Common error handling patterns
    
    Uses DataMSAdapter for:
    - HTTP communication with Data Microservice
    - Search endpoint operations
    
    The search_master_data function in tools.py uses these methods to perform searches.
    """
    
    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        """
        Initialize the search service with a Data MS adapter.
        
        Args:
            adapter: Optional DataMSAdapter instance (creates default if None)
        """
        super().__init__(adapter or DataMSAdapter())
        # Store typed adapter reference for type checking
        self.adapter: DataMSAdapter = self.adapter  # type: ignore
    
    def validate_additional_preconditions(
        self,
        session_id: str,
        validated_crn: str
    ) -> None:
        """
        Override base class hook to add data model precondition check.
        
        This method is called by the base class validate_session_and_crn() method
        when check_preconditions=True.
        
        Args:
            session_id: The validated session ID
            validated_crn: The validated CRN
            
        Raises:
            PreconditionFailedError: If data model hasn't been fetched
        """
        # PRECONDITION CHECK: Verify data model has been fetched for this session
        if not has_fetched_data_model(session_id):
            self.logger.error(f"Precondition failed for session {session_id}: Data model not fetched")
            raise PreconditionFailedError(
                create_data_model_precondition_error(
                    session_id=session_id,
                    crn=validated_crn
                )
            )
    
    
    def validate_query_against_model(
        self,
        session_id: str,
        query: Dict[str, Any],
        search_type: str
    ) -> None:
        """
        Validate query against the data model.
        
        Args:
            session_id: Session ID for data model validation
            query: Search query dictionary
            search_type: Type of search being performed
            
        Raises:
            PreconditionFailedError: If validation fails or data model not cached
        """
        try:
            is_valid, error_message, suggestions = validate_search_query(
                session_id=session_id,
                query=query,
                search_type=search_type
            )
            
            if not is_valid:
                self.logger.error(f"Search query validation failed: {error_message}")
                
                # Create validation error with suggestions
                validation_details = {}
                if suggestions:
                    validation_details["suggestions"] = suggestions
                    validation_details["validation_type"] = "data_model_property_validation"
                
                error_response = create_validation_error(
                    message=error_message or "Search query validation failed",
                    field="query"
                )
                
                if validation_details:
                    error_response["details"] = validation_details
                
                raise PreconditionFailedError(error_response)
            
        except ValueError as e:
            # Data model not cached
            self.logger.error(f"Data model validation failed: {str(e)}")
            raise PreconditionFailedError(
                create_data_model_precondition_error(
                    session_id=session_id,
                    crn="unknown"
                )
            )
    
    def parse_search_criteria(
        self,
        search_type: Literal["record", "relationship", "entity", "hierarchy_node"],
        query: Dict[str, Any],
        filters: Optional[List[Dict[str, Any]]]
    ) -> SearchCriteria:
        """
        Parse and construct SearchCriteria from raw inputs.
        
        Args:
            search_type: Type of data to search for
            query: Search query dictionary
            filters: Optional list of filter dictionaries
            
        Returns:
            Validated SearchCriteria object
            
        Raises:
            ValidationError: If Pydantic validation fails
        """
        # Parse the query dict into SearchQuery model
        search_query = SearchQuery(**query)
        
        # Parse filters if provided
        search_filters = None
        if filters:
            search_filters = [SearchFilter(**f) for f in filters]
        
        # Create and return search criteria
        return SearchCriteria(
            search_type=search_type,
            query=search_query,
            filters=search_filters
        )
    
    def build_search_criteria(
        self,
        session_id: str,
        search_type: Literal["record", "relationship", "entity", "hierarchy_node"],
        query: Dict[str, Any],
        filters: Optional[List[Dict[str, Any]]]
    ) -> SearchCriteria:
        """
        Build and validate search criteria from input parameters.
        
        This is an orchestrator method that:
        1. Validates query against data model (raises exception on failure)
        2. Parses and constructs SearchCriteria (raises exception on failure)
        
        Args:
            session_id: Session ID for data model validation
            search_type: Type of data to search for
            query: Search query dictionary
            filters: Optional list of filter dictionaries
            
        Returns:
            Validated SearchCriteria object
            
        Raises:
            PreconditionFailedError: If query validation fails
            ValidationError: If Pydantic validation fails
        """
        # Validate query against data model (raises PreconditionFailedError on failure)
        self.validate_query_against_model(session_id, query, search_type)
        
        # Parse and return search criteria (raises ValidationError on failure)
        return self.parse_search_criteria(search_type, query, filters)
    
    def execute_search_request(
        self,
        search_criteria: SearchCriteria,
        validated_crn: str,
        limit: int,
        offset: int,
        include_total_count: bool,
        include_attributes: Optional[List[str]] = None,
        exclude_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute the search API request and return raw response.
        
        Args:
            search_criteria: Validated search criteria
            validated_crn: Validated CRN
            limit: Maximum number of results
            offset: Number of results to skip
            include_total_count: Whether to include total count
            include_attributes: Optional list of attributes to include in results
            exclude_attributes: Optional list of attributes to exclude from results
            
        Returns:
            Raw API response data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        # Convert search criteria to dict for the API request
        search_criteria_dict = search_criteria.model_dump(exclude_none=True)
        
        # Use adapter for search request
        return self.adapter.search_master_data(
            search_criteria_dict,
            validated_crn,
            limit,
            offset,
            include_total_count,
            include_attributes,
            exclude_attributes
        )
    
    def search_master_data(
        self,
        ctx: Context,
        search_type: Literal["record", "relationship", "entity", "hierarchy_node"],
        query: Dict[str, Any],
        filters: Optional[List[Dict[str, Any]]],
        limit: int,
        offset: int,
        include_total_count: bool,
        crn: Optional[str],
        include_attributes: Optional[List[str]] = None,
        exclude_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for search operations with complete error handling.
        
        This method orchestrates the entire search workflow:
        1. Validates session and CRN (with precondition checks)
        2. Builds and validates search criteria
        3. Executes the search request
        4. Handles all error cases with appropriate responses
        
        Args:
            ctx: MCP Context object for session tracking
            search_type: Type of data to search for
            query: Search query dictionary
            filters: Optional list of filter dictionaries
            limit: Maximum number of results
            offset: Number of results to skip
            include_total_count: Whether to include total count
            crn: Optional CRN (uses default if None)
            include_attributes: Optional list of attributes to include in results
            exclude_attributes: Optional list of attributes to exclude from results
            
        Returns:
            Search results or formatted error response
        """
        try:
            # Validate session and CRN, check preconditions (including data model fetch)
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(
                ctx, crn, check_preconditions=False
            )
            
            self.logger.info(
                f"Searching {search_type} with query: {query}, "
                f"tenant: {tenant_id}, session: {session_id}"
            )
            
            # Build and validate search criteria (includes data model validation)
            # search_criteria = self.build_search_criteria(session_id, search_type, query, filters)
            search_criteria = self.parse_search_criteria(search_type, query, filters)
            
            # Execute search request and return raw response
            return self.execute_search_request(
                search_criteria,
                validated_crn,
                limit,
                offset,
                include_total_count,
                include_attributes,
                exclude_attributes
            )
            
        except CRNValidationError as e:
            # CRN validation errors already formatted
            return e.args[0] if e.args else {"error": str(e), "status_code": 400}
        
        except PreconditionFailedError as e:
            # Return the error response from the exception
            return e.error_response
        
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return create_validation_error(
                message=f"Invalid search criteria: {str(e)}",
                field="search_criteria"
            )
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            
            return create_api_error(
                message=f"Search request failed: {str(e)}",
                status_code=e.response.status_code if hasattr(e, 'response') and e.response else 500,
                api_details={
                    "response_text": e.response.text if hasattr(e, 'response') and e.response else None
                }
            )
        
        except Exception as e:
            self.logger.error(f"Unexpected error during search: {str(e)}", exc_info=True)
            return create_api_error(
                message=f"Unexpected error: {str(e)}",
                status_code=500,
                api_details={"error_type": type(e).__name__}
            )


