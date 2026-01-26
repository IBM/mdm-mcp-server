# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Pydantic models for data export tool interface.

These models define the contract between MCP tools and the service layer,
providing automatic validation and type safety for export operations.
"""

from typing import Optional, List, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CreateDataExportRequest(BaseModel):
    """Request model for create_data_export tool with automatic validation."""
    
    export_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name for the export job"
    )
    
    export_type: Literal["record", "entity"] = Field(
        "entity",
        description="Type of data to export: 'record' for source records, 'entity' for golden records"
    )
    
    record_type: str = Field(
        ...,
        description="Record type to export (e.g., 'person', 'organization')"
    )
    
    file_format: Literal["csv", "tsv", "psv"] = Field(
        "csv",
        description="Format of the export file: csv (comma-separated), tsv (tab-separated), or psv (pipe-separated)"
    )
    
    compression_type: Literal["tar", "tgz", "zip", "none"] = Field(
        "none",
        description="Compression type for the export file"
    )
    
    search_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional search criteria to filter exported data. Structure: {'query': {'expressions': [...]}, 'filters': [...]}"
    )
    
    include_only_updated_after: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp to export only data updated after this date (e.g., '2024-01-01T00:00:00Z')"
    )
    
    crn: Optional[str] = Field(
        None,
        description="Cloud Resource Name identifying the tenant"
    )
    
    @field_validator('search_criteria')
    @classmethod
    def validate_search_criteria(cls, v):
        """Validate search criteria structure if provided."""
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("search_criteria must be a dictionary")
        if 'query' in v:
            query = v['query']
            if not isinstance(query, dict):
                raise ValueError("search_criteria.query must be a dictionary")
            if 'expressions' in query and not isinstance(query['expressions'], list):
                raise ValueError("search_criteria.query.expressions must be a list")
        return v


class DownloadDataExportRequest(BaseModel):
    """Request model for download_data_export tool."""
    
    export_id: str = Field(
        ...,
        description="The unique identifier of the export job to download"
    )
    
    crn: Optional[str] = Field(
        None,
        description="Cloud Resource Name identifying the tenant"
    )


class ExportJobResponse(BaseModel):
    """Response model for export job creation."""
    
    job_id: Optional[str] = Field(
        None,
        description="Unique identifier for the export job"
    )
    
    # Also support 'id' for compatibility
    id: Optional[str] = Field(
        None,
        description="Unique identifier for the export job (alias)"
    )
    
    job_name: Optional[str] = Field(
        None,
        description="Name of the export job"
    )
    
    job_type: Optional[str] = Field(
        None,
        description="Type of job (e.g., 'export')"
    )
    
    status: Optional[str] = Field(
        None,
        description="Current status of the export job (e.g., 'running', 'succeeded', 'failed')"
    )
    
    export_type: Optional[str] = Field(
        None,
        description="Type of data being exported"
    )
    
    record_type: Optional[str] = Field(
        None,
        description="Record type being exported"
    )
    
    file_format: Optional[str] = Field(
        None,
        description="Format of the export file"
    )
    
    compression_type: Optional[str] = Field(
        None,
        description="Compression type used"
    )
    
    start_time: Optional[str] = Field(
        None,
        description="Job start timestamp"
    )
    
    end_time: Optional[str] = Field(
        None,
        description="Job completion timestamp"
    )
    
    file_name: Optional[str] = Field(
        None,
        description="Name of the generated export file"
    )
    
    file_expired: Optional[bool] = Field(
        None,
        description="Whether the export file has expired"
    )
    
    record_count: Optional[int] = Field(
        None,
        description="Number of records exported"
    )
    
    process_ids: Optional[List[str]] = Field(
        None,
        description="List of process IDs associated with the job"
    )
    
    search_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Search criteria used for the export"
    )
    
    additional_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional information about the job"
    )
    
    @property
    def export_id(self) -> Optional[str]:
        """Get the export ID (prefers job_id over id)."""
        return self.job_id or self.id


class DownloadDataExportResponse(BaseModel):
    """Response model for download_data_export operations."""
    
    export_id: str = Field(
        ...,
        description="The export job ID"
    )
    
    file_name: Optional[str] = Field(
        None,
        description="Name of the export file"
    )
    
    content_type: Optional[str] = Field(
        None,
        description="MIME type of the export file"
    )
    
    file_size: Optional[int] = Field(
        None,
        description="Size of the export file in bytes"
    )
    
    file_path: Optional[str] = Field(
        None,
        description="Local path where file was saved (if save_to_path was used)"
    )
    
    status: Optional[str] = Field(
        None,
        description="Download status (e.g., 'downloaded')"
    )
    
    message: Optional[str] = Field(
        None,
        description="Status message about the download"
    )


class DataExportErrorResponse(BaseModel):
    """Error response model for data export operations."""
    
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
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )


# Type aliases for response types
CreateDataExportResponse = Union[ExportJobResponse, DataExportErrorResponse]
DataExportDownloadResponse = Union[DownloadDataExportResponse, DataExportErrorResponse]