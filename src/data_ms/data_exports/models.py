# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Pydantic models for data export requests and responses.

These models define the domain objects for data export operations,
including export job configuration, status tracking, and results.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator
from datetime import datetime


class ExportExpression(BaseModel):
    """
    An expression used to filter data for export.
    
    Supports nested expressions with AND/OR operations for complex queries.
    Similar to search expressions but used for export filtering.
    
    Examples:
        Simple expression:
            {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"}
        
        Nested expressions with OR:
            {
                "operation": "or",
                "expressions": [
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Smith"},
                    {"property": "legal_name.last_name", "condition": "equal", "value": "Jones"}
                ]
            }
    """
    property: Optional[str] = Field(
        None,
        description="The property path to filter on (e.g., 'legal_name.last_name', 'address.city')"
    )
    condition: Optional[Literal[
        "equal", "not_equal", "greater_than", "greater_than_equal",
        "less_than", "less_than_equal", "starts_with", "ends_with",
        "contains", "not_contains", "fuzzy", "has_value", "has_no_value"
    ]] = Field(
        None,
        description="The condition to apply on the property or value"
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        None,
        description="The value to filter for"
    )
    record_type: Optional[str] = Field(
        None,
        description="The record type to filter on (e.g., 'person', 'organization')"
    )
    operation: Optional[Literal["and", "or"]] = Field(
        None,
        description="The operation to use to join multiple expressions"
    )
    expressions: Optional[List['ExportExpression']] = Field(
        None,
        description="An optional list of additional expressions for nested queries"
    )
    
    @model_validator(mode='after')
    def validate_expression_structure(self) -> 'ExportExpression':
        """
        Validate that expression has valid structure.
        """
        has_property = self.property is not None
        has_operation = self.operation is not None
        has_expressions = self.expressions is not None and len(self.expressions) > 0
        
        # Check if this is a nested expression
        if has_operation and has_expressions:
            if has_property:
                raise ValueError(
                    "Nested expressions with 'operation' and 'expressions' "
                    "should not have 'property', 'condition', or 'value'."
                )
            return self
        
        # Check if this is a leaf expression
        if has_property:
            if not self.condition:
                raise ValueError(
                    f"Leaf expression with property '{self.property}' must have a 'condition'."
                )
            if self.condition not in ["has_value", "has_no_value"] and self.value is None:
                raise ValueError(
                    f"Condition '{self.condition}' requires a 'value'."
                )
            return self
        
        # Neither leaf nor nested - invalid
        raise ValueError(
            "Expression must be either a leaf expression (with 'property' and 'condition') "
            "or a nested expression (with 'operation' and 'expressions')."
        )


# Enable forward references for recursive model
ExportExpression.model_rebuild()


class ExportSearchFilter(BaseModel):
    """
    A filter to apply to export to narrow down results.
    """
    type: Literal[
        "record", "entity", "source", "relationship",
        "data_quality", "hierarchy_type", "hierarchy_number", "group"
    ] = Field(
        ...,
        description="The filter type"
    )
    values: Optional[List[str]] = Field(
        None,
        description="The values to filter upon"
    )
    data_quality_issues: Optional[List[Literal[
        "potential_match", "potential_overlay", "user_tasks_only",
        "same_source_only", "potential_duplicate"
    ]]] = Field(
        None,
        description="The data quality issues to filter by"
    )


class ExportSearchCriteria(BaseModel):
    """
    Search criteria for filtering export data.
    
    Used to define which records/entities to include in the export.
    """
    search_type: Literal["record", "entity"] = Field(
        "record",
        description="The type of data to export"
    )
    query: Optional[Dict[str, Any]] = Field(
        None,
        description="The search query containing expressions for filtering"
    )
    filters: Optional[List[ExportSearchFilter]] = Field(
        None,
        description="The search filters to apply to narrow down results"
    )


class ExportJobStatus(BaseModel):
    """
    Status information for an export job.
    """
    state: Literal[
        "queued", "running", "succeeded", "failed", "cancelled"
    ] = Field(
        ...,
        description="Current state of the export job"
    )
    message: Optional[str] = Field(
        None,
        description="Status message or error description"
    )
    progress: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Progress percentage (0-100)"
    )


class ExportJob(BaseModel):
    """
    Represents an export job with its configuration and status.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the export job"
    )
    job_name: Optional[str] = Field(
        None,
        description="User-provided name for the export job"
    )
    status: Optional[ExportJobStatus] = Field(
        None,
        description="Current status of the export job"
    )
    search_criteria: Optional[ExportSearchCriteria] = Field(
        None,
        description="Search criteria used for filtering export data"
    )
    file_format: Optional[Literal["csv", "tsv", "psv"]] = Field(
        None,
        description="Format of the export file"
    )
    compression_type: Optional[Literal["tar", "tgz", "zip", "none"]] = Field(
        None,
        description="Compression type for the export file"
    )
    export_type: Optional[Literal["record", "entity"]] = Field(
        None,
        description="Type of data being exported"
    )
    record_type: Optional[str] = Field(
        None,
        description="Record type being exported"
    )
    start_time: Optional[str] = Field(
        None,
        description="Timestamp when the export job started"
    )
    end_time: Optional[str] = Field(
        None,
        description="Timestamp when the export job completed"
    )
    file_name: Optional[str] = Field(
        None,
        description="Name of the generated export file"
    )
    file_expired: Optional[bool] = Field(
        None,
        description="Whether the export file has expired and is no longer available"
    )
    record_count: Optional[int] = Field(
        None,
        description="Number of records included in the export"
    )


class ExportJobList(BaseModel):
    """
    A list of export jobs with pagination information.
    """
    exports: List[ExportJob] = Field(
        default_factory=list,
        description="List of export jobs"
    )
    total_count: Optional[int] = Field(
        None,
        description="Total number of export jobs"
    )
    limit: Optional[int] = Field(
        None,
        description="Maximum results per page"
    )
    offset: Optional[int] = Field(
        None,
        description="Number of results skipped"
    )