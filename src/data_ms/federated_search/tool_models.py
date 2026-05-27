# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Pydantic models for federated search tool interface.
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


class PotentialMatchIssue(BaseModel):
    """A single potential match issue record."""

    id: Optional[str] = Field(None, description="Issue identifier")
    record_ids: Optional[List[str]] = Field(None, description="IDs of records involved")
    entity_ids: Optional[List[str]] = Field(None, description="IDs of entities involved")
    score: Optional[float] = Field(None, description="Match confidence score")
    status: Optional[str] = Field(None, description="Issue status")
    created_at: Optional[str] = Field(None, description="Issue creation timestamp")
    updated_at: Optional[str] = Field(None, description="Issue last update timestamp")

    class Config:
        extra = "allow"


class FederatedSearchResponse(BaseModel):
    """Response model for successful federated search operations."""

    potential_match_issues: List[PotentialMatchIssue] = Field(
        default_factory=list,
        description="List of potential match issues"
    )
    potential_match_issues_total: Optional[int] = Field(
        None,
        description="Total number of matching potential match issues (None when include_total_count=False)"
    )
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Number of results skipped")


class FederatedSearchErrorResponse(BaseModel):
    """Error response model for federated search operations."""

    error: str = Field(..., description="Error type identifier")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


FederatedSearchResult = Union[FederatedSearchResponse, FederatedSearchErrorResponse]
