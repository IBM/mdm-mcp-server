# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Search tools for IBM MDM MCP server.
"""

import logging
from typing import Optional

from fastmcp import Context
from .service import SearchService
from .tool_models import SearchResponse, SearchMasterDataRequest, SearchMasterDataResponse, SearchErrorResponse

logger = logging.getLogger(__name__)

_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create the search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


def search_master_data(
    ctx: Context,
    request: SearchMasterDataRequest
) -> SearchResponse:
    """
    Searches for ANY type of Master Data in IBM MDM - use search_type parameter to specify: "record", "entity", "relationship", or "hierarchy_node".
    
    **Understanding search_type**:
    - "entity" = Golden records (best version after matching/merging) - use for most queries about people, organizations, etc.
    - "record" = Source records (individual records before matching) - use only when explicitly asked for source data
    - "relationship" = Relationships between entities
    - "hierarchy_node" = Hierarchy structures
    
    Supports complex nested AND/OR queries for searching records, entities, relationships, or hierarchy nodes.
    
    **IMPORTANT PREREQUISITE**: You MUST call get_data_model() with format="enhanced_compact"
    BEFORE using this tool (at least once per session). The data model provides essential information about:
    - Available entity types and record types to search
    - Searchable attributes and their COMPLETE property paths (e.g., "legal_name.last_name")
    - Attribute data types and constraints
    
    **CRITICAL VALIDATION RULES**:
    - Property paths MUST be complete nested paths from data model (e.g., "legal_name.last_name", NOT "legal_name")
    - Validation will REJECT incomplete property paths
    - Use property="*" ONLY as fallback after specific field search fails
    - Invalid property paths will return validation errors
    
    This tool allows you to construct sophisticated search queries with nested conditions
    using AND/OR logic to find records, entities, relationships, or hierarchy nodes.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        request: SearchRecordsRequest containing:
            - search_type: Type of data to search for. Options: "record", "entity", "relationship", "hierarchy_node"
            - query: The search query object containing expressions and operations. Structure:
                {
                    "expressions": [<list of Expression objects>],
                    "operation": "and" | "or"  (optional, default: "and")
                }
                
                Each Expression can be:
                - Simple expression: {"property": "complete.nested.path", "condition": "equal", "value": "search_value"}
                  * MUST use complete paths like "legal_name.last_name", NOT "legal_name"
                  * Validation will reject incomplete paths
                - Full-text expression: {"property": "*", "condition": "contains", "value": "search_value"}
                  * Use ONLY as fallback after specific field search fails
                  * Searches ALL fields (slower but comprehensive)
                - Nested expression: {"operation": "or", "expressions": [<list of expressions>]}
                
                Available conditions:
                - "equal", "not_equal": Exact match or non-match
                - "greater_than", "greater_than_equal", "less_than", "less_than_equal": Numeric comparisons
                - "starts_with", "ends_with", "contains", "not_contains": String pattern matching
                - "fuzzy": Fuzzy text matching
                - "has_value", "has_no_value": Check for presence/absence of value
                
                Property paths MUST be complete nested paths from data model:
                - CORRECT: "legal_name.last_name", "address.city", "contact.email"
                - WRONG: "legal_name", "address", "contact" (incomplete - will be rejected)
                - Use "*" ONLY as fallback after specific search fails
                - NEVER use "*" as first attempt
            - filters: Optional list of filters to narrow down results. Each filter has:
                {
                    "type": "record" | "entity" | "source" | "relationship" | "data_quality" | "hierarchy_type" | "hierarchy_number" | "group",
                    "values": [<list of string values>],  (for most filter types)
                    "data_quality_issues": [<list of issues>]  (for data_quality type)
                }
                
                Data quality issues: "potential_match", "potential_overlay", "user_tasks_only", "same_source_only", "potential_duplicate"
            - limit: Maximum number of results to return (max 50, default: 10)
            - offset: Number of results to skip for pagination (default: 0)
            - include_total_count: Whether to include total count in response (default: true)
            - crn: Cloud Resource Name identifying the tenant (optional, defaults to On-Prem tenant)
    
    Returns:
        Search results containing matched records with pagination info
    
    Examples:
        1. Simple search - Find records with last name "Smith":
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="record",
                   query={
                       "expressions": [
                           {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                       ]
                   }
               )
           )
       
       2. FALLBACK ONLY - Full-text search when specific field search fails (DO NOT use as first attempt):
          search_master_data(
              request=SearchMasterDataRequest(
                  search_type="record",
                  query={
                      "expressions": [
                          {"property": "*", "condition": "contains", "value": "Smith"}
                      ]
                  }
              )
          )
       
       3. Multiple conditions with AND - Last name "Smith" AND city "Boston":
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="entity",
                   query={
                       "expressions": [
                           {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                           {"property": "address.city", "condition": "equal", "value": "Boston"}
                       ],
                       "operation": "and"
                   }
               )
           )
       
       4. Complex nested query - (Last name "Smith" OR "Jones") AND (City "Boston"):
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="entity",
                   query={
                       "expressions": [
                           {
                               "operation": "or",
                               "expressions": [
                                   {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                                   {"property": "legal_name.last_name", "condition": "contains", "value": "J"}
                               ]
                           },
                           {"property": "address.city", "condition": "equal", "value": "Boston"}
                       ],
                       "operation": "and"
                   }
               )
           )
       
       5. Search with filters - Find person records with last name "Smith":
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="record",
                   query={
                       "expressions": [
                           {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                       ]
                   },
                   filters=[
                       {"type": "record", "values": ["person"]}
                   ]
               )
           )
       
       6. Search with data quality filter - Find potential duplicates:
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="record",
                   query={
                       "expressions": [
                           {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                       ]
                   },
                   filters=[
                       {"type": "data_quality", "data_quality_issues": ["potential_duplicate"]}
                   ]
               )
           )
       
       7. Advanced nested query - ((Name "Smith" OR "Jones") AND City "Boston") OR (Name "Brown" AND City "New York"):
           search_master_data(
               request=SearchMasterDataRequest(
                   search_type="record",
                   query={
                       "expressions": [
                           {
                               "operation": "and",
                               "expressions": [
                                   {
                                       "operation": "or",
                                       "expressions": [
                                           {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                                           {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                                       ]
                                   },
                                   {"property": "address.city", "condition": "equal", "value": "Boston"}
                               ]
                           },
                           {
                               "operation": "and",
                               "expressions": [
                                   {"property": "legal_name.last_name", "condition": "equal", "value": "Brown"},
                                   {"property": "address.city", "condition": "equal", "value": "New York"}
                               ]
                           }
                       ],
                       "operation": "or"
                   }
               )
           )
       
       8. Browse all entities - Get sample data (use sparingly with small limit):
          search_master_data(
              request=SearchMasterDataRequest(
                  search_type="entity",
                  query={
                      "expressions": [
                          {"property": "*", "condition": "contains", "value": "*"}
                      ]
                  },
                  limit=10
              )
          )
   """
    service = get_search_service()
    
    result = service.search_master_data(
        ctx=ctx,
        search_type=request.search_type,
        query=request.query,
        filters=request.filters,
        limit=request.limit,
        offset=request.offset,
        include_total_count=request.include_total_count,
        crn=request.crn,
        include_attributes=request.include_attributes,
        exclude_attributes=request.exclude_attributes
    )
    
    if "error" in result:
        return SearchErrorResponse(**result)
    else:
        return SearchMasterDataResponse(**result)
