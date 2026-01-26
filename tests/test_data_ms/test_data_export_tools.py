# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Unit tests for data export tools.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from data_ms.data_exports.tool_models import (
    CreateDataExportRequest,
    DownloadDataExportRequest,
    ExportJobResponse,
    DownloadDataExportResponse,
    DataExportErrorResponse
)
from data_ms.data_exports.models import (
    ExportExpression,
    ExportSearchFilter,
    ExportSearchCriteria,
    ExportJobStatus,
    ExportJob
)


class TestCreateDataExportRequest:
    """Tests for CreateDataExportRequest model validation."""
    
    def test_valid_basic_request(self):
        """Test valid basic export request."""
        request = CreateDataExportRequest(
            export_name="test_export",
            export_type="entity",
            record_type="person",
            file_format="csv",
            compression_type="none"
        )
        assert request.export_name == "test_export"
        assert request.export_type == "entity"
        assert request.record_type == "person"
        assert request.file_format == "csv"
        assert request.compression_type == "none"
    
    def test_valid_request_with_search_criteria(self):
        """Test valid export request with search criteria."""
        request = CreateDataExportRequest(
            export_name="filtered_export",
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
        assert request.search_criteria is not None
        assert "query" in request.search_criteria
    
    def test_valid_request_with_timestamp(self):
        """Test valid export request with incremental timestamp."""
        request = CreateDataExportRequest(
            export_name="incremental_export",
            export_type="entity",
            record_type="person",
            file_format="tsv",
            compression_type="tgz",
            include_only_updated_after="2024-01-01T00:00:00Z"
        )
        assert request.include_only_updated_after == "2024-01-01T00:00:00Z"
    
    def test_default_values(self):
        """Test default values are applied correctly."""
        request = CreateDataExportRequest(
            export_name="test",
            record_type="person"
        )
        assert request.export_type == "entity"
        assert request.file_format == "csv"
        assert request.compression_type == "none"
    
    def test_invalid_export_type(self):
        """Test that invalid export_type raises validation error."""
        with pytest.raises(ValidationError):
            CreateDataExportRequest(
                export_name="test",
                export_type="invalid",
                record_type="person"
            )
    
    def test_invalid_file_format(self):
        """Test that invalid file_format raises validation error."""
        with pytest.raises(ValidationError):
            CreateDataExportRequest(
                export_name="test",
                export_type="entity",
                record_type="person",
                file_format="xml"
            )
    
    def test_invalid_compression_type(self):
        """Test that invalid compression_type raises validation error."""
        with pytest.raises(ValidationError):
            CreateDataExportRequest(
                export_name="test",
                export_type="entity",
                record_type="person",
                compression_type="gzip"
            )
    
    def test_empty_export_name(self):
        """Test that empty export_name raises validation error."""
        with pytest.raises(ValidationError):
            CreateDataExportRequest(
                export_name="",
                export_type="entity",
                record_type="person"
            )
    
    def test_invalid_search_criteria_not_dict(self):
        """Test that invalid search_criteria raises validation error."""
        with pytest.raises(ValidationError):
            CreateDataExportRequest(
                export_name="test",
                export_type="entity",
                record_type="person",
                search_criteria="invalid"
            )


class TestDownloadDataExportRequest:
    """Tests for DownloadDataExportRequest model validation."""
    
    def test_valid_request(self):
        """Test valid download request."""
        request = DownloadDataExportRequest(
            export_id="abc123-def456"
        )
        assert request.export_id == "abc123-def456"
        assert request.crn is None
    
    def test_valid_request_with_crn(self):
        """Test valid download request with CRN."""
        request = DownloadDataExportRequest(
            export_id="abc123-def456",
            crn="crn:v1:bluemix:public:mdm:us-south:a/123:456::"
        )
        assert request.crn is not None


class TestExportExpression:
    """Tests for ExportExpression model validation."""
    
    def test_valid_leaf_expression(self):
        """Test valid leaf expression."""
        expr = ExportExpression(
            property="legal_name.last_name",
            condition="equal",
            value="Smith"
        )
        assert expr.property == "legal_name.last_name"
        assert expr.condition == "equal"
        assert expr.value == "Smith"
    
    def test_valid_nested_expression(self):
        """Test valid nested expression."""
        expr = ExportExpression(
            operation="or",
            expressions=[
                ExportExpression(property="legal_name.last_name", condition="equal", value="Smith"),
                ExportExpression(property="legal_name.last_name", condition="equal", value="Jones")
            ]
        )
        assert expr.operation == "or"
        assert len(expr.expressions) == 2
    
    def test_leaf_without_condition(self):
        """Test leaf expression without condition raises error."""
        with pytest.raises(ValidationError):
            ExportExpression(
                property="legal_name.last_name",
                value="Smith"
            )
    
    def test_condition_without_value(self):
        """Test condition requiring value without value raises error."""
        with pytest.raises(ValidationError):
            ExportExpression(
                property="legal_name.last_name",
                condition="equal"
            )
    
    def test_has_value_condition_no_value_needed(self):
        """Test has_value condition doesn't require value."""
        expr = ExportExpression(
            property="email",
            condition="has_value"
        )
        assert expr.condition == "has_value"
        assert expr.value is None


class TestExportJobStatus:
    """Tests for ExportJobStatus model."""
    
    def test_valid_status(self):
        """Test valid export job status."""
        status = ExportJobStatus(
            state="running",
            message="Export in progress",
            progress=50
        )
        assert status.state == "running"
        assert status.progress == 50
    
    def test_invalid_state(self):
        """Test invalid state raises error."""
        with pytest.raises(ValidationError):
            ExportJobStatus(state="invalid_state")
    
    def test_progress_boundaries(self):
        """Test progress boundaries."""
        # Valid boundaries
        ExportJobStatus(state="running", progress=0)
        ExportJobStatus(state="running", progress=100)
        
        # Invalid boundaries
        with pytest.raises(ValidationError):
            ExportJobStatus(state="running", progress=-1)
        
        with pytest.raises(ValidationError):
            ExportJobStatus(state="running", progress=101)


class TestExportJob:
    """Tests for ExportJob model."""
    
    def test_valid_export_job(self):
        """Test valid export job."""
        job = ExportJob(
            id="abc123",
            job_name="test_export",
            status=ExportJobStatus(state="succeeded"),
            export_type="entity",
            record_type="person",
            file_format="csv",
            compression_type="none",
            record_count=1000
        )
        assert job.id == "abc123"
        assert job.record_count == 1000
    
    def test_minimal_export_job(self):
        """Test minimal export job with only required fields."""
        job = ExportJob(id="abc123")
        assert job.id == "abc123"
        assert job.job_name is None


class TestResponseModels:
    """Tests for response models."""
    
    def test_export_job_response_with_job_id(self):
        """Test ExportJobResponse model with job_id (actual API response)."""
        response = ExportJobResponse(
            job_id="23853101697575100",
            job_type="export",
            status="running",
            export_type="entity",
            file_name="23853101697575100",
            file_expired=False,
            process_ids=["ea04be1b-a63d-4966-92bf-67d1e300e5cb"],
            start_time="1769438098000"
        )
        assert response.job_id == "23853101697575100"
        assert response.export_id == "23853101697575100"  # property
        assert response.status == "running"
        assert response.job_type == "export"
    
    def test_export_job_response_with_id(self):
        """Test ExportJobResponse model with id (alternate field)."""
        response = ExportJobResponse(
            id="abc123",
            job_name="test_export",
            status="succeeded",
            export_type="entity",
            record_type="person"
        )
        assert response.id == "abc123"
        assert response.export_id == "abc123"  # property falls back to id
    
    def test_export_job_response_export_id_property(self):
        """Test export_id property prefers job_id over id."""
        response = ExportJobResponse(
            job_id="job123",
            id="id456",
            status="succeeded"
        )
        assert response.export_id == "job123"  # Prefers job_id
    
    def test_download_data_export_response(self):
        """Test DownloadDataExportResponse model with actual API fields."""
        response = DownloadDataExportResponse(
            export_id="2473561625481448",
            file_name="2473561625481448.csv",
            content_type="application/octet-stream",
            file_size=2647327,
            status="downloaded"
        )
        assert response.export_id == "2473561625481448"
        assert response.file_name == "2473561625481448.csv"
        assert response.file_size == 2647327
        assert response.status == "downloaded"
    
    def test_download_data_export_response_with_file_path(self):
        """Test DownloadDataExportResponse with file_path when saved to disk."""
        response = DownloadDataExportResponse(
            export_id="abc123",
            file_name="export.csv",
            content_type="application/octet-stream",
            file_size=1024,
            file_path="/tmp/exports/export.csv",
            status="downloaded"
        )
        assert response.file_path == "/tmp/exports/export.csv"
    
    def test_error_response(self):
        """Test DataExportErrorResponse model."""
        response = DataExportErrorResponse(
            error="ExportNotReady",
            status_code=400,
            message="Export job is not ready",
            details={"export_id": "abc123"}
        )
        assert response.error == "ExportNotReady"
        assert response.status_code == 400