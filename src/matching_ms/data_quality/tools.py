# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Data quality issues tool for IBM MDM MCP server.
"""

import logging
from typing import Annotated, List, Optional

from fastmcp import Context
from pydantic import Field

from .service import DataQualityIssuesService
from .tool_models import (
    DataQualityIssuesResult,
    DataQualityIssuesResponse,
    DataQualityIssuesErrorResponse,
)

logger = logging.getLogger(__name__)

_service: Optional[DataQualityIssuesService] = None


def _get_service() -> DataQualityIssuesService:
    global _service
    if _service is None:
        _service = DataQualityIssuesService()
    return _service


def get_data_quality_issues(
    ctx: Context,
    entity_type: str,
    crn: Optional[str] = None,
    record_number: Optional[int] = None,
    entities: Optional[List[str]] = None,
    limit: Annotated[int, Field(ge=1, description="Number of issues to retrieve")] = 1,
    offset: Annotated[int, Field(ge=0, description="Number of issues to skip")] = 0,
    fetch_total_count: bool = True,
    include_tags: bool = False,
    include_record_attributes: Optional[str] = None,
    return_linked_issues: bool = True,
) -> DataQualityIssuesResult:
    """Placeholder — overridden by DATA_QUALITY_ISSUES_TOOL_DESCRIPTION below."""
    result = _get_service().get_data_quality_issues(
        ctx=ctx,
        entity_type=entity_type,
        crn=crn,
        record_number=record_number,
        entities=entities,
        limit=limit,
        offset=offset,
        fetch_total_count=fetch_total_count,
        include_tags=include_tags,
        include_record_attributes=include_record_attributes,
        return_linked_issues=return_linked_issues,
    )

    if "error" in result or "errors" in result or "trace" in result:
        return DataQualityIssuesErrorResponse(**result)
    return DataQualityIssuesResponse(**result)


DATA_QUALITY_ISSUES_TOOL_DESCRIPTION = """
Retrieve data quality issues for given entities or a record from IBM MDM.

**When to use**:
- User asks: "Show me quality issues for this entity", "Get potential match issues for person_entity",
  "What issues exist for record 12345678?", "List data quality issues for these entities"
- Does NOT require calling get_data_model() first.

Args:
    ctx: MCP Context object (automatically injected)
    entity_type: Required. Data type identifier of the entity (e.g. "person_entity", "organization_entity", "household_entity")
    crn: Cloud Resource Name identifying the tenant (optional, defaults to configured tenant)
    record_number: Unique identifier of a source record to look up issues for (optional)
    entities: List of entity identifiers to look up issues for (optional). Example: ["person_entity-12345678"]
    limit: Number of issues to retrieve (default: 1)
    offset: Number of issues to skip before returning results (default: 0)
    fetch_total_count: Return the total number of issues for the given entity ids and types (default: true)
    include_tags: Include tag details (id, name, color) in the response per issue (default: false)
    include_record_attributes: Comma-separated list of record attribute names to include per entity (optional). Example: "legal_name,primary_address"
    return_linked_issues: Include issues where both records belong to the same entity (default: true)

Returns:
    Paged collection of data quality issues:
    - issues: list of data quality issue records (type, entity_type, entities, resolution_prediction, id, created_at)
    - total_count: total number of issues for the given entities (when fetch_total_count=true)
    - potential_match_records: list of record numbers that are potential matches
    - offset / limit: pagination metadata
    - first / last / next / previous: pagination href links

Examples:
    1. Get issues for specific entity IDs :
       get_data_quality_issues(
           entity_type="person_entity",
           entities=["person_entity-107618727577518081", "person_entity-107618727577518082"]
       )

    2. Get issues for a specific record number:
       get_data_quality_issues(
           entity_type="person_entity",
           record_number=12345678
       )

    3. Paginate — second page of 10 results:
       get_data_quality_issues(
           entity_type="person_entity",
           limit=10,
           offset=10
       )

    4. Include tag details and record attributes in response:
       get_data_quality_issues(
           entity_type="person_entity",
           include_tags=True,
           include_record_attributes="legal_name,primary_address"
       )

    5. Exclude issues where both records share the same entity:
       get_data_quality_issues(
           entity_type="person_entity",
           return_linked_issues=False
       )
"""

get_data_quality_issues.__doc__ = DATA_QUALITY_ISSUES_TOOL_DESCRIPTION
