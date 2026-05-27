# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Search tools for IBM MDM MCP server.
"""

import logging
from typing import Annotated, List, Literal, Optional, Union

from fastmcp import Context
from pydantic import Field
from .service import SearchService
from .tool_models import SearchResponse, SearchMasterDataResponse, SearchErrorResponse

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
    search_type: Annotated[Literal["record", "relationship", "entity", "hierarchy_node"], Field(
        description="Type of data to search for"
    )],
    query: Annotated[dict, Field(
        description="Search query object containing expressions and operations"
    )],
    crn: Annotated[Optional[str], Field(
        description="Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)"
    )] = None,
    filters: Annotated[Optional[List[dict]], Field(
        description="Optional list of filters to narrow down results"
    )] = None,
    limit: Annotated[int, Field(
        ge=0,
        le=50,
        description="Maximum number of results to return (0-50). Use 0 with include_total_count=true for count-only queries."
    )] = 10,
    offset: Annotated[int, Field(
        ge=0,
        description="Number of results to skip for pagination"
    )] = 0,
    include_total_count: Annotated[bool, Field(
        description="Whether to include total count in response"
    )] = True,
    include_attributes: Annotated[Optional[Union[List[str], str]], Field(
        description=("Optional list of attribute paths to include in results (e.g., ['legal_name.given_name', 'address.city'])."
                     "DO NOT set this field unless the user explicitly asks to see only specific attributes."
                     "When null (default), all attributes are returned - this is the correct behavior "
                     "for most queries. Only use this to narrow results when the user says something like "
                     "'show me only names and addresses'."
                     )
    )] = None,
    exclude_attributes: Annotated[Optional[Union[List[str], str]], Field(
        description=("Optional list of attribute paths to exclude from results (e.g., ['legal_name.given_name', 'address.city'])"
                     "DO NOT set this field unless the user explicitly asks to hide specific attributes. "
                     "When null (default), no attributes are excluded."
                     )
    )] = None,
) -> SearchResponse:
    """
    Search Master Data
   """
    if isinstance(include_attributes, str):
        include_attributes = None if include_attributes in ("*", "") else [include_attributes]
    elif isinstance(include_attributes, list) and not include_attributes:
        include_attributes = None

    if isinstance(exclude_attributes, str):
        exclude_attributes = None if exclude_attributes in ("*", "") else [exclude_attributes]
    elif isinstance(exclude_attributes, list) and not exclude_attributes:
        exclude_attributes = None

    if isinstance(filters, list) and not filters:
        filters = None

    service = get_search_service()

    result = service.search_master_data(
        ctx=ctx,
        search_type=search_type,
        query=query,
        filters=filters,
        limit=limit,
        offset=offset,
        include_total_count=include_total_count,
        crn=crn,
        include_attributes=include_attributes,
        exclude_attributes=exclude_attributes,
    )
    
    if "error" in result:
        return SearchErrorResponse(**result)
    else:
        return SearchMasterDataResponse(**result)

SEARCH_TOOL_DESCRIPTION = """
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
    search_type: Type of data to search for. Options: "record", "entity", "relationship", "hierarchy_node"
    query: The search query object containing expressions and operations. Structure:
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
    crn: Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)
    filters: Optional list of filters to narrow down results. Each filter has:
        {
            "type": "record" | "entity" | "source" | "relationship" | "data_quality" | "hierarchy_type" | "hierarchy_number" | "group",
            "values": [<list of string values>],  (for most filter types)
            "data_quality_issues": [<list of issues>]  (for data_quality type)
        }

        Data quality issues: "potential_match", "potential_overlay", "user_tasks_only", "same_source_only", "potential_duplicate"
    limit: Maximum number of results to return (0-50, default: 10). Use 0 with include_total_count=true for count-only queries.
    offset: Number of results to skip for pagination (default: 0)
    include_total_count: Whether to include total count in response (default: true)
    include_attributes: Optional list of attribute paths to include in results
    exclude_attributes: Optional list of attribute paths to exclude from results

Returns:
    Search results containing matched records with pagination info


Examples:
    1. Simple search - Find records with last name "Smith":
        search_master_data(
            search_type="record",
            query={
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
                ]
            }
        )

    2. FALLBACK ONLY - Full-text search when specific field search fails (DO NOT use as first attempt):
        search_master_data(
            search_type="record",
            query={
                "expressions": [
                    {"property": "*", "condition": "contains", "value": "Smith"}
                ]
            }
        )

    3. Multiple conditions with AND - Last name "Smith" AND city "Boston":
        search_master_data(
            search_type="entity",
            query={
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                    {"property": "address.city", "condition": "equal", "value": "Boston"}
                ],
                "operation": "and"
            }
        )

    4. Complex nested query - (Last name "Smith" OR "Jones") AND (City "Boston"):
        search_master_data(
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

    5. Search with filters - Find person records with last name "Smith":
        search_master_data(
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

    6. Search with data quality filter - Find potential duplicates:
        search_master_data(
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

    7. Advanced nested query - ((Name "Smith" OR "Jones") AND City "Boston") OR (Name "Brown" AND City "New York"):
        search_master_data(
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

    8. Browse all entities - Get sample data (use sparingly with small limit):
        search_master_data(
            search_type="entity",
            query={
                "expressions": [
                    {"property": "*", "condition": "contains", "value": "*"}
                ]
            },
            limit=10
        )
"""

search_master_data.__doc__ = SEARCH_TOOL_DESCRIPTION