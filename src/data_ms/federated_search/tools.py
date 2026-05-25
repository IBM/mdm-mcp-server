# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Federated search tool for IBM MDM MCP server.
"""

import logging
from typing import Annotated, Literal, Optional

from fastmcp import Context
from pydantic import Field

from .service import FederatedSearchService
from .tool_models import FederatedSearchResult, FederatedSearchResponse, FederatedSearchErrorResponse

logger = logging.getLogger(__name__)

_federated_search_service: Optional[FederatedSearchService] = None


def get_federated_search_service() -> FederatedSearchService:
    global _federated_search_service
    if _federated_search_service is None:
        _federated_search_service = FederatedSearchService()
    return _federated_search_service


def search_potential_match_issues(
    ctx: Context,
    query: dict,
    crn: Optional[str] = None,
    limit: Annotated[int, Field(ge=0, le=50, description="Maximum number of results to return (0-50). Use 0 with include_total_count=true for count-only queries.")] = 10,
    offset: Annotated[int, Field(ge=0, description="Number of results to skip for pagination")] = 0,
    include_total_count: bool = True,
    issue_type: str = "potential_match",
    timezone: str = "UTC",
    sort_order: Literal["asc", "desc"] = "desc",
) -> FederatedSearchResult:
    """
    Search for potential match issues in IBM MDM using the federated search endpoint.
    """
    service = get_federated_search_service()

    result = service.search_potential_match_issues(
        ctx=ctx,
        query=query,
        crn=crn,
        limit=limit,
        offset=offset,
        include_total_count=include_total_count,
        issue_type=issue_type,
        timezone=timezone,
        sort_order=sort_order,
    )

    if "error" in result:
        return FederatedSearchErrorResponse(**result)
    return FederatedSearchResponse(**result)


FEDERATED_SEARCH_TOOL_DESCRIPTION = """
Search for potential match issues in IBM MDM using the federated search endpoint.

Use this tool when the user asks about potential matches, duplicate records, or
potential match issues — NOT for general master data search (use search_master_data for that).

**When to use**:
- User asks: "Show me potential match issues", "Find potential duplicates", "List potential matches"
- User wants to review records that MDM flagged as potential matches for merging
- Does NOT require calling get_data_model() first

**Query structure** (same expression syntax as search_master_data):
- Browse all issues:  {"expressions": [{"property": "*", "condition": "equal", "value": "*"}]}
- Filter by a field: {"expressions": [{"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}]}

Args:
    ctx: MCP Context object (automatically injected)
    query: Search query with expressions. Use property="*", condition="equal", value="*" to list all issues.
    crn: Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)
    limit: Maximum number of results to return (0-50, default: 10). Use 0 with include_total_count=true for count-only queries.
    offset: Number of results to skip for pagination (default: 0)
    include_total_count: Whether to include total count in response (default: true)
    issue_type: Type of data quality issue to search (default: "potential_match")
    timezone: IANA timezone name for date/time values in results (default: "UTC"). Examples: "America/New_York", "Europe/London", "Asia/Tokyo"
    sort_order: Sort order for results — "asc" (oldest first) or "desc" (newest first, default)

Returns:
    Potential match issues with pagination info:
    - potential_match_issues: list of issue records
    - potential_match_issues_total: total number of matching issues (when include_total_count=true)
    - limit / offset: pagination metadata

Examples:
    1. List all potential match issues (newest first):
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]}
       )

    2. Count total potential match issues without fetching records:
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]},
           limit=0,
           include_total_count=True
       )

    3. Filter by a specific field — issues involving records with last name "Smith":
       search_potential_match_issues(
           query={"expressions": [{"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}]}
       )

    4. Fuzzy match — issues involving records with a name similar to "Johnson":
       search_potential_match_issues(
           query={"expressions": [{"property": "legal_name.last_name", "condition": "fuzzy", "value": "Johnson"}]}
       )

    5. Sort oldest-first — useful for reviewing issues in the order they were created:
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]},
           sort_order="asc"
       )

    6. Display dates in a specific timezone:
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]},
           timezone="America/New_York"
       )

    7. Paginate — second page of 10 results:
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]},
           limit=10,
           offset=10
       )

    8. Paginate in ascending order — process all issues oldest-to-newest, third page:
       search_potential_match_issues(
           query={"expressions": [{"property": "*", "condition": "equal", "value": "*"}]},
           limit=10,
           offset=20,
           sort_order="asc"
       )
"""

search_potential_match_issues.__doc__ = FEDERATED_SEARCH_TOOL_DESCRIPTION
