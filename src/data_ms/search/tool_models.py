# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Pydantic models for search tool interface.

These models define the contract between MCP tools and the service layer,
providing automatic validation and type safety.
"""

from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field, field_validator


class SearchMasterDataRequest(BaseModel):
    """Request model for search_master_data tool with automatic validation."""
    
    search_type: Literal["record", "relationship", "entity", "hierarchy_node"] = Field(
        ...,
        description="Type of data to search for"
    )
    
    query: dict = Field(
        ...,
        description="Search query object containing expressions and operations"
    )
    
    filters: Optional[List[dict]] = Field(
        None,
        description="Optional list of filters to narrow down results"
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results to return (1-50)"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination"
    )
    
    include_total_count: bool = Field(
        default=True,
        description="Whether to include total count in response"
    )
    
    crn: Optional[str] = Field(
        None,
        description="Cloud Resource Name identifying the tenant"
    )
    
    include_attributes: Optional[List[str]] = Field(
        None,
        description="Optional list of attribute paths to include in results (e.g., ['legal_name.given_name', 'address.city'])"
    )
    
    exclude_attributes: Optional[List[str]] = Field(
        None,
        description="Optional list of attribute paths to exclude from results (e.g., ['legal_name.given_name', 'address.city'])"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query_structure(cls, v):
        """Validate query has required structure."""
        if not isinstance(v, dict):
            raise ValueError("Query must be a dictionary")
        if 'expressions' not in v:
            raise ValueError("Query must contain 'expressions' field")
        if not isinstance(v['expressions'], list):
            raise ValueError("Query expressions must be a list")
        if len(v['expressions']) == 0:
            raise ValueError("Query must contain at least one expression")
        return v


class SearchMasterDataResponse(BaseModel):
    """Response model for successful search_master_data operations."""
    
    results: List[dict] = Field(
        default_factory=list,
        description="List of search results"
    )
    
    total_count: int = Field(
        ...,
        description="Total number of matching results"
    )
    
    limit: int = Field(
        ...,
        description="Maximum results per page"
    )
    
    offset: int = Field(
        ...,
        description="Number of results skipped"
    )
    
    is_exact_count: bool = Field(
        default=True,
        description="Whether total count is exact"
    )
    
    first: Optional[dict] = Field(
        None,
        description="Link to first page"
    )
    
    last: Optional[dict] = Field(
        None,
        description="Link to last page"
    )


class SearchErrorResponse(BaseModel):
    """Error response model for search operations."""
    
    error: str = Field(
        ...,
        description="Error type identifier"
    )
    
    status_code: int = Field(
        ...,
        description="HTTP status code"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    details: Optional[dict] = Field(
        None,
        description="Additional error details"
    )


# Type alias for search response
SearchResponse = Union[SearchMasterDataResponse, SearchErrorResponse]

# Backward compatibility aliases
SearchRecordsRequest = SearchMasterDataRequest
SearchRecordsResponse = SearchMasterDataResponse