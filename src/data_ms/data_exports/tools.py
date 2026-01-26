# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Data export tools for IBM MDM MCP server.

This module provides MCP tool functions for exporting master data from IBM MDM,
including creating export jobs and downloading results.
"""

import logging
from typing import Optional

from fastmcp import Context
from .service import DataExportService
from .tool_models import (
    CreateDataExportRequest,
    DownloadDataExportRequest,
    ExportJobResponse,
    DownloadDataExportResponse,
    DataExportErrorResponse,
    CreateDataExportResponse,
    DataExportDownloadResponse
)

logger = logging.getLogger(__name__)

_export_service: Optional[DataExportService] = None


def get_export_service() -> DataExportService:
    """Get or create the data export service instance."""
    global _export_service
    if _export_service is None:
        _export_service = DataExportService()
    return _export_service


def create_data_export(
    ctx: Context,
    request: CreateDataExportRequest
) -> CreateDataExportResponse:
    """
    Creates a new data export job in IBM MDM.
    
    This tool initiates an export of master data based on the specified parameters.
    The export runs asynchronously - use download_data_export to retrieve the file 
    when the export is complete.
    
    **Supported Export Types:**
    - "entity" = Export golden records (best version after matching/merging) - DEFAULT
    - "record" = Export source records (individual records before matching)
    
    **Supported File Formats:**
    - "csv" = Comma-separated values (DEFAULT)
    - "tsv" = Tab-separated values
    - "psv" = Pipe-separated values
    
    **Supported Compression Types:**
    - "none" = No compression (DEFAULT)
    - "zip" = ZIP compression
    - "tar" = TAR archive
    - "tgz" = Gzipped TAR archive
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        request: CreateDataExportRequest containing:
            - export_name: Name for the export job (required)
            - export_type: Type of data to export - "record" or "entity" (default: "entity")
            - record_type: Record type to export, e.g., "person", "organization" (required)
            - file_format: Output file format - "csv", "tsv", or "psv" (default: "csv")
            - compression_type: Compression - "tar", "tgz", "zip", or "none" (default: "none")
            - search_criteria: Optional search criteria to filter exported data.
              If not provided, exports ALL data of the specified record_type.
              Structure: {"query": {"expressions": [...]}, "filters": [...]}
            - include_only_updated_after: Optional ISO 8601 timestamp for incremental export
            - crn: Cloud Resource Name identifying the tenant (optional, defaults to configured CRN)
    
    Returns:
        ExportJobResponse with export job details including:
        - id: Unique identifier for the export job (use this for download_data_export)
        - job_name: Name of the export job
        - status: Current status (e.g., "running", "succeeded")
        - export_type: Type of data being exported
        - record_type: Record type being exported
        - file_format: Format of the export file
        - compression_type: Compression used
        - start_time: When the job started
        
        Or DataExportErrorResponse if an error occurred.
    
    Examples:
        1. Basic entity export (all persons):
           create_data_export(
               request=CreateDataExportRequest(
                   export_name="all_persons_export",
                   export_type="entity",
                   record_type="person",
                   file_format="csv"
               )
           )
        
        2. Filtered export with search criteria:
           create_data_export(
               request=CreateDataExportRequest(
                   export_name="boston_persons",
                   export_type="entity",
                   record_type="person",
                   file_format="csv",
                   compression_type="zip",
                   search_criteria={
                       "query": {
                           "expressions": [
                               {"property": "address.city", "condition": "equal", "value": "Boston"}
                           ]
                       }
                   }
               )
           )
        
        3. Incremental export (changes since date):
           create_data_export(
               request=CreateDataExportRequest(
                   export_name="recent_updates",
                   export_type="entity",
                   record_type="person",
                   file_format="tsv",
                   include_only_updated_after="2024-01-01T00:00:00Z"
               )
           )
        
        4. Source records export with compression:
           create_data_export(
               request=CreateDataExportRequest(
                   export_name="source_records_backup",
                   export_type="record",
                   record_type="person",
                   file_format="csv",
                   compression_type="tgz"
               )
           )
    """
    service = get_export_service()
    
    result = service.create_export(
        ctx=ctx,
        export_name=request.export_name,
        export_type=request.export_type,
        record_type=request.record_type,
        file_format=request.file_format,
        compression_type=request.compression_type,
        search_criteria=request.search_criteria,
        include_only_updated_after=request.include_only_updated_after,
        crn=request.crn
    )
    
    if "error" in result:
        return DataExportErrorResponse(**result)
    else:
        return ExportJobResponse(**result)


def download_data_export(
    ctx: Context,
    request: DownloadDataExportRequest
) -> DataExportDownloadResponse:
    """
    Gets download information for a completed data export.
    
    Use this tool to obtain the download URL or file information for a completed
    export job. The export job must be in "succeeded" state.
    
    **Prerequisites:**
    - Export job must be in "succeeded" state
    - Export file must not be expired
    
    **Note:** Export files have a limited retention period. If the file has expired,
    you will need to create a new export job.
    
    Args:
        ctx: MCP Context object (automatically injected) - provides session information
        request: DownloadDataExportRequest containing:
            - export_id: The unique identifier of the export job (required)
            - crn: Cloud Resource Name identifying the tenant (optional)
    
    Returns:
        DownloadDataExportResponse containing:
        - export_id: The export job ID
        - download_url: URL to download the export file
        - file_name: Name of the export file
        - content_type: MIME type of the file
        - file_size: Size of the file in bytes
        - message: Status message
        
        Or DataExportErrorResponse if an error occurred, including:
        - ExportNotReady: Export job is not in "succeeded" state
        - ExportFileExpired: Export file has expired and is no longer available
    
    Examples:
        1. Download completed export:
           download_data_export(
               request=DownloadDataExportRequest(
                   export_id="abc123-def456-ghi789"
               )
           )
    
    Typical Workflow:
        1. Create export: create_data_export(...)
        2. Wait for export to complete (job status will show "succeeded")
        3. Download: download_data_export(export_id=...)
    """
    service = get_export_service()
    
    result = service.download_export(
        ctx=ctx,
        export_id=request.export_id,
        crn=request.crn
    )
    
    if "error" in result:
        return DataExportErrorResponse(**result)
    else:
        return DownloadDataExportResponse(**result)