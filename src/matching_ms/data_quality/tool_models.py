# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Pydantic models for the get_data_quality_issues tool interface.

Response shape based on GET /mdm/v1/data_quality/issues (GetDataQualityIssues schema).
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pagination links
# ---------------------------------------------------------------------------

class PageLink(BaseModel):
    """A pagination href link (first / last / next / previous)."""

    href: Optional[str] = Field(None, description="URL for the page of results")

    class Config:
        extra = "allow"


# ---------------------------------------------------------------------------
# Issue sub-objects
# ---------------------------------------------------------------------------

class ResolutionPrediction(BaseModel):
    """Remediation workflow resolution prediction attached to an issue."""

    probability: Optional[float] = Field(None, description="Prediction probability score (0–1)")
    action: Optional[str] = Field(None, description="Predicted resolution action (e.g. 'link')")

    class Config:
        extra = "allow"


class DataQualityIssueEntity(BaseModel):
    """An entity/record pair associated with a data quality issue."""

    record_number: Optional[str] = Field(None, description="Record number of the source record")
    entity_id: Optional[str] = Field(None, description="Entity identifier (e.g. 'person_entity-12345')")

    class Config:
        extra = "allow"


class DataQualityIssue(BaseModel):
    """
    A single data quality issue as returned by GET /mdm/v1/data_quality/issues.

    Example::

        {
            "type": "potential_match",
            "entity_type": "person_entity",
            "entities": [
                {"record_number": "107618727585906689", "entity_id": "person_entity-107618727577518081"},
                {"record_number": "107618727585906690", "entity_id": "person_entity-107618727577518082"}
            ],
            "created_at": "Jan 15, 2023",
            "resolution_prediction": {"probability": 0.7095238, "action": "link"},
            "id": "vs68cku9hfmp"
        }
    """

    id: Optional[str] = Field(None, description="Issue identifier")
    type: Optional[str] = Field(None, description="Issue type (e.g. 'potential_match')")
    entity_type: Optional[str] = Field(None, description="Entity type (e.g. 'person_entity')")
    created_at: Optional[str] = Field(None, description="Issue creation timestamp")
    entities: Optional[List[DataQualityIssueEntity]] = Field(
        None, description="Entities/records involved in this issue"
    )
    resolution_prediction: Optional[ResolutionPrediction] = Field(
        None, description="Resolution prediction details"
    )

    class Config:
        extra = "allow"


# ---------------------------------------------------------------------------
# Top-level response (HTTP 200)
# ---------------------------------------------------------------------------

class DataQualityIssuesResponse(BaseModel):
    """
    Successful paged response for get_data_quality_issues (HTTP 200).

    Maps directly to the API's GetDataQualityIssues schema.
    """

    offset: int = Field(..., description="Number of issues skipped before this page")
    limit: int = Field(..., description="Maximum number of issues returned per page")
    total_count: Optional[int] = Field(None, description="Total number of issues for the given entities")
    issues: List[DataQualityIssue] = Field(
        default_factory=list, description="Paged collection of data quality issues"
    )
    potential_match_records: Optional[List[str]] = Field(
        None, description="Record numbers that are potential matches"
    )
    first: Optional[PageLink] = Field(None, description="Link to the first page of results")
    last: Optional[PageLink] = Field(None, description="Link to the last page of results")
    previous: Optional[PageLink] = Field(None, description="Link to the previous page of results")
    next: Optional[PageLink] = Field(None, description="Link to the next page of results")

    class Config:
        extra = "allow"


# ---------------------------------------------------------------------------
# Error response (400 / 401 / 403 / 404 / 500)
# ---------------------------------------------------------------------------

class ApiErrorTarget(BaseModel):
    """Field target for a structured API error."""

    type: Optional[str] = Field(None, description="Target type (e.g. 'field')")
    name: Optional[str] = Field(None, description="Target name")

    class Config:
        extra = "allow"


class ApiError(BaseModel):
    """A single structured error entry from the IBM MDM API."""

    code: Optional[str] = Field(None, description="Error code")
    message: Optional[str] = Field(None, description="Human-readable error message")
    more_info: Optional[str] = Field(None, description="Link or text with additional information")
    target: Optional[ApiErrorTarget] = Field(None, description="Field or parameter that caused the error")

    class Config:
        extra = "allow"


class DataQualityIssuesErrorResponse(BaseModel):
    """
    Error response for get_data_quality_issues (HTTP 400 / 401 / 403 / 404 / 500).

    Matches the IBM MDM API error envelope::

        {"trace": "...", "status_code": 400, "errors": [{"code": "...", "message": "..."}]}

    Also accepts the MCP-internal error shape (``error`` / ``message``).
    """

    # IBM MDM API error shape
    trace: Optional[str] = Field(None, description="Trace ID for the failed request")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    errors: Optional[List[ApiError]] = Field(None, description="List of structured errors")

    # MCP-internal error shape
    error: Optional[str] = Field(None, description="Error type identifier (MCP-internal errors)")
    message: Optional[str] = Field(None, description="Human-readable message (MCP-internal errors)")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        extra = "allow"


DataQualityIssuesResult = Union[DataQualityIssuesResponse, DataQualityIssuesErrorResponse]
