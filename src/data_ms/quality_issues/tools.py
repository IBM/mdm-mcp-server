# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Quality issues tool for IBM MDM MCP server.
"""

import logging
from typing import Annotated, Optional

from fastmcp import Context
from pydantic import Field

from .service import QualityIssuesService
from .tool_models import QualityIssuesResult, QualityIssuesResponse, QualityIssuesErrorResponse

logger = logging.getLogger(__name__)

_quality_issues_service: Optional[QualityIssuesService] = None


def _get_service() -> QualityIssuesService:
    global _quality_issues_service
    if _quality_issues_service is None:
        _quality_issues_service = QualityIssuesService()
    return _quality_issues_service


def get_quality_issues(
    ctx: Context,
    issue_type: str,
    entity_type: Optional[str] = None,
    entity_type_name: Optional[str] = None,
    crn: Optional[str] = None,
    offset: Annotated[int, Field(ge=0, description="Number of quality issues to skip over")] = 0,
    limit: Annotated[int, Field(ge=1, le=50, description="Number of quality issues to return (max 50)")] = 10,
    include_total_count: bool = True,
    include_total_count_without_tasks: bool = False,
) -> QualityIssuesResult:
    """Placeholder — overridden by QUALITY_ISSUES_TOOL_DESCRIPTION below."""
    service = _get_service()

    result = service.get_quality_issues(
        ctx=ctx,
        issue_type=issue_type,
        entity_type=entity_type,
        entity_type_name=entity_type_name,
        crn=crn,
        offset=offset,
        limit=limit,
        include_total_count=include_total_count,
        include_total_count_without_tasks=include_total_count_without_tasks,
    )

    if "error" in result or "errors" in result or "trace" in result:
        return QualityIssuesErrorResponse(**result)
    return QualityIssuesResponse(**result)


QUALITY_ISSUES_TOOL_DESCRIPTION = """
Retrieve all data quality issues for a given issue type from IBM MDM in a paginated manner.

Requires the IAM action: **mdm-oc.data.read**

**When to use**:
- User asks: "Show me quality issues", "List all potential_overlay issues",
  "Get data quality issues of type <X>", "How many quality issues are there?"
- Does NOT require calling get_data_model() first.

Args:
    ctx: MCP Context object (automatically injected)
    issue_type: The type of quality issue to retrieve (required). Example: "potential_overlay"
    entity_type: Entity type to filter by (optional). Example: "record"
    entity_type_name: Entity type name as defined in the workflow configuration (optional). Example: "person"
    crn: Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)
    offset: Number of quality issues to skip over for pagination (default: 0)
    limit: Number of quality issues to return per page, maximum 50 (default: 10)
    include_total_count: Include the total issue count on pages other than the first (default: true)
    include_total_count_without_tasks: Include the total issue count excluding issues that have tasks (default: false)

Returns:
    Paged collection of quality issues with pagination links:
    - quality_issues: list of quality issue records
    - total_count: total number of matching issues (when include_total_count=true)
    - total_count_without_tasks: total count excluding issues with tasks (when include_total_count_without_tasks=true)
    - offset / limit: pagination metadata
    - first / last / next / previous: pagination href links

Examples:
    1. Retrieve the first page of potential_overlay issues:
       get_quality_issues(issue_type="potential_overlay")

    2. Filter by entity type "person" records:
       get_quality_issues(
           issue_type="potential_overlay",
           entity_type="record",
           entity_type_name="person"
       )

    3. Count total issues without fetching records:
       get_quality_issues(
           issue_type="potential_overlay",
           limit=1,
           include_total_count=True
       )

    4. Paginate — second page of 20 results:
       get_quality_issues(
           issue_type="potential_overlay",
           offset=20,
           limit=20
       )

    5. Include count of issues without associated tasks:
       get_quality_issues(
           issue_type="potential_overlay",
           include_total_count_without_tasks=True
       )
"""

get_quality_issues.__doc__ = QUALITY_ISSUES_TOOL_DESCRIPTION
