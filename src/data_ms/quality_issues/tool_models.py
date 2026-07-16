# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Pydantic models for the get_quality_issues tool interface.

Response shape is based on the JsonQualityIssueResponse schema:
  GET/POST /mdm/v1/quality_issues
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pagination links
# ---------------------------------------------------------------------------

class PageLink(BaseModel):
    """A pagination href link returned in first / last / next / previous."""

    href: Optional[str] = Field(None, description="URL for the page of results")

    class Config:
        extra = "allow"


# ---------------------------------------------------------------------------
# Issue sub-objects
# ---------------------------------------------------------------------------

class ResolutionPrediction(BaseModel):
    """Remediation workflow resolution prediction attached to an issue."""

    probability: Optional[float] = Field(None, description="Prediction probability score (0–1)")
    action: Optional[str] = Field(None, description="Predicted resolution action")

    class Config:
        extra = "allow"


class DataQualityIssueEntity(BaseModel):
    """An entity record pair associated with a data quality issue."""

    record_number: Optional[str] = Field(None, description="Record number of the entity")
    entity_id: Optional[str] = Field(None, description="Entity identifier")

    class Config:
        extra = "allow"


class DataQualityIssue(BaseModel):
    """
    A single data quality issue as returned by the API.

    Example response item::

        {
            "issue_type": "potential_overlay",
            "type": "record",
            "type_name": "person",
            "id": "123",
            "number": "123",
            "created_at": "Jan15, 2023"
        }
    """

    id: Optional[str] = Field(None, description="Issue identifier")
    number: Optional[str] = Field(None, description="Issue number")
    issue_type: Optional[str] = Field(None, description="Type of quality issue (e.g. 'potential_overlay')")
    type: Optional[str] = Field(None, description="Entity type involved (e.g. 'record')")
    type_name: Optional[str] = Field(None, description="Entity type name as defined in the workflow configuration (e.g. 'person')")
    created_at: Optional[str] = Field(None, description="Issue creation timestamp")
    entities: Optional[List[DataQualityIssueEntity]] = Field(
        None, description="Entities associated with the issue"
    )
    resolution_prediction: Optional[ResolutionPrediction] = Field(
        None, description="Resolution prediction details"
    )

    class Config:
        extra = "allow"


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class QualityIssuesResponse(BaseModel):
    """
    Successful paged response for get_quality_issues (HTTP 200).

    Maps directly to the API's JsonQualityIssueResponse schema.
    """

    offset: int = Field(..., description="Number of elements skipped before this page")
    limit: int = Field(..., description="Maximum number of elements returned per page")
    total_count: Optional[int] = Field(None, description="Total number of quality issues")
    total_count_wo_tasks: Optional[int] = Field(
        None, description="Total count of quality issues that have no tasks created"
    )
    first: Optional[PageLink] = Field(None, description="Link to the first page of results")
    last: Optional[PageLink] = Field(None, description="Link to the last page of results")
    previous: Optional[PageLink] = Field(None, description="Link to the previous page of results")
    next: Optional[PageLink] = Field(None, description="Link to the next page of results")
    quality_issues: List[DataQualityIssue] = Field(
        default_factory=list, description="Paged collection of quality issues"
    )

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


class QualityIssuesErrorResponse(BaseModel):
    """
    Error response for get_quality_issues (HTTP 400 / 401 / 403 / 404 / 500).

    Matches the IBM MDM API error envelope::

        {
            "trace": "...",
            "status_code": 400,
            "errors": [{"code": "...", "message": "...", ...}]
        }

    Also accepts the MCP-internal error shape (``error`` / ``message``) so
    that CRN-validation and unexpected errors surface correctly.
    """

    # IBM MDM API error shape
    trace: Optional[str] = Field(None, description="Trace ID for the failed request")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    errors: Optional[List[ApiError]] = Field(None, description="List of structured errors")

    # MCP-internal error shape (CRN validation / unexpected errors)
    error: Optional[str] = Field(None, description="Error type identifier (MCP-internal errors)")
    message: Optional[str] = Field(None, description="Human-readable message (MCP-internal errors)")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        extra = "allow"


QualityIssuesResult = Union[QualityIssuesResponse, QualityIssuesErrorResponse]
