# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Integration tests for data export service with mocked adapter.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import HTTPError, RequestException

from data_ms.data_exports.service import DataExportService
from data_ms.data_exports.tools import create_data_export, download_data_export, get_export_service
from data_ms.data_exports.tool_models import (
    CreateDataExportRequest,
    DownloadDataExportRequest
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = Mock()
    ctx.session_id = "test-session-123"
    return ctx


@pytest.fixture
def mock_adapter():
    """Create a mock DataMSAdapter."""
    adapter = Mock()
    return adapter


@pytest.fixture
def export_service(mock_adapter):
    """Create a DataExportService with mocked adapter."""
    service = DataExportService(adapter=mock_adapter)
    return service


class TestDataExportServiceCreateExport:
    """Tests for DataExportService.create_export method."""
    
    def test_create_export_success(self, export_service, mock_adapter, mock_context):
        """Test successful export creation with actual API response format."""
        # Setup mock response matching actual API
        mock_adapter.create_data_export.return_value = {
            "job_id": "23853101697575100",
            "job_type": "export",
            "status": "running",
            "export_type": "entity",
            "file_name": "23853101697575100",
            "file_expired": False,
            "process_ids": ["ea04be1b-a63d-4966-92bf-67d1e300e5cb"],
            "start_time": "1769438098000"
        }
        
        # Mock CRN validation - patch where it's used (in base_service)
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.create_export(
                ctx=mock_context,
                export_name="test_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none"
            )
        
        assert result["job_id"] == "23853101697575100"
        assert result["status"] == "running"
        mock_adapter.create_data_export.assert_called_once()
        
        # Verify request body uses 'format' not 'file_format'
        call_args = mock_adapter.create_data_export.call_args
        request_body = call_args[1]["export_request"]
        assert "format" in request_body
        assert "file_format" not in request_body
        assert request_body["format"] == "csv"
    
    def test_create_export_includes_default_search_criteria(self, export_service, mock_adapter, mock_context):
        """Test that export creation includes default search_criteria when not provided."""
        mock_adapter.create_data_export.return_value = {
            "job_id": "export-123",
            "status": "queued"
        }
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.create_export(
                ctx=mock_context,
                export_name="test_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none"
                # No search_criteria provided
            )
        
        # Verify default search_criteria was added (wildcard to export all)
        call_args = mock_adapter.create_data_export.call_args
        request_body = call_args[1]["export_request"]
        assert "search_criteria" in request_body
        assert request_body["search_criteria"]["search_type"] == "entity"
        assert request_body["search_criteria"]["query"]["expressions"][0]["property"] == "*"
        assert request_body["search_criteria"]["query"]["expressions"][0]["value"] == "*"
    
    def test_create_export_with_custom_search_criteria(self, export_service, mock_adapter, mock_context):
        """Test export creation with custom search criteria."""
        mock_adapter.create_data_export.return_value = {
            "job_id": "export-456",
            "status": "queued"
        }
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.create_export(
                ctx=mock_context,
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
        
        assert result["job_id"] == "export-456"
        
        # Verify custom search criteria was used
        call_args = mock_adapter.create_data_export.call_args
        request_body = call_args[1]["export_request"]
        assert "search_criteria" in request_body
        assert request_body["search_criteria"]["search_type"] == "entity"
        assert request_body["search_criteria"]["query"]["expressions"][0]["property"] == "address.city"
    
    def test_create_export_with_incremental_timestamp(self, export_service, mock_adapter, mock_context):
        """Test export creation with incremental timestamp."""
        mock_adapter.create_data_export.return_value = {
            "job_id": "export-789",
            "status": "queued"
        }
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.create_export(
                ctx=mock_context,
                export_name="incremental_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none",
                include_only_updated_after="2024-01-01T00:00:00Z"
            )
        
        # Verify timestamp was included
        call_args = mock_adapter.create_data_export.call_args
        request_body = call_args[1]["export_request"]
        assert request_body["include_only_updated_after"] == "2024-01-01T00:00:00Z"
    
    def test_create_export_api_error(self, export_service, mock_adapter, mock_context):
        """Test export creation with API error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        error = RequestException("API Error")
        error.response = mock_response
        mock_adapter.create_data_export.side_effect = error
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.create_export(
                ctx=mock_context,
                export_name="test_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none"
            )
        
        assert "error" in result
        assert result["status_code"] == 500


class TestDataExportServiceDownloadExport:
    """Tests for DataExportService.download_export method."""
    
    def test_download_export_success(self, export_service, mock_adapter, mock_context):
        """Test successful export download with actual API response format."""
        mock_adapter.download_data_export.return_value = {
            "export_id": "2473561625481448",
            "file_name": "2473561625481448.csv",
            "content_type": "application/octet-stream",
            "file_size": 2647327,
            "status": "downloaded"
        }
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.download_export(
                ctx=mock_context,
                export_id="2473561625481448"
            )
        
        assert result["export_id"] == "2473561625481448"
        assert result["file_name"] == "2473561625481448.csv"
        assert result["file_size"] == 2647327
        assert result["status"] == "downloaded"
    
    def test_download_export_with_save_path(self, export_service, mock_adapter, mock_context):
        """Test download export with save_to_path option."""
        mock_adapter.download_data_export.return_value = {
            "export_id": "export-123",
            "file_name": "export.csv",
            "content_type": "application/octet-stream",
            "file_size": 1024,
            "file_path": "/tmp/exports/export.csv",
            "status": "downloaded"
        }
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.download_export(
                ctx=mock_context,
                export_id="export-123",
                save_to_path="/tmp/exports"
            )
        
        assert result["file_path"] == "/tmp/exports/export.csv"
        
        # Verify save_to_path was passed to adapter
        call_args = mock_adapter.download_data_export.call_args
        assert call_args[1]["save_to_path"] == "/tmp/exports"
    
    def test_download_export_not_found(self, export_service, mock_adapter, mock_context):
        """Test download for non-existent export."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Export not found"
        
        error = RequestException("Not Found")
        error.response = mock_response
        mock_adapter.download_data_export.side_effect = error
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.download_export(
                ctx=mock_context,
                export_id="non-existent"
            )
        
        assert "error" in result
        assert result["status_code"] == 404
    
    def test_download_export_in_progress(self, export_service, mock_adapter, mock_context):
        """Test download when export is still in progress (503 error)."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = '{"errors": [{"code": "export_in_progress", "message": "Export is still running"}]}'
        
        error = RequestException("Service Unavailable")
        error.response = mock_response
        mock_adapter.download_data_export.side_effect = error
        
        with patch('common.core.base_service.get_crn_with_precedence') as mock_crn:
            mock_crn.return_value = ("crn:test:123", "tenant-456")
            
            result = export_service.download_export(
                ctx=mock_context,
                export_id="running-export"
            )
        
        assert "error" in result
        assert result["status_code"] == 503


class TestDataExportTools:
    """Tests for MCP tool functions."""
    
    def test_create_data_export_tool(self, mock_context):
        """Test create_data_export tool function."""
        # Reset the singleton
        import data_ms.data_exports.tools as tools_module
        tools_module._export_service = None
        
        with patch('data_ms.data_exports.tools.DataExportService') as MockService:
            mock_service = Mock()
            mock_service.create_export.return_value = {
                "job_id": "23853101697575100",
                "job_type": "export",
                "status": "running",
                "file_name": "23853101697575100"
            }
            MockService.return_value = mock_service
            
            request = CreateDataExportRequest(
                export_name="test_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none"
            )
            
            result = create_data_export(mock_context, request)
            
            assert result.job_id == "23853101697575100"
            assert result.status == "running"
            mock_service.create_export.assert_called_once()
    
    def test_create_data_export_tool_with_id_fallback(self, mock_context):
        """Test create_data_export tool when API returns 'id' instead of 'job_id'."""
        import data_ms.data_exports.tools as tools_module
        tools_module._export_service = None
        
        with patch('data_ms.data_exports.tools.DataExportService') as MockService:
            mock_service = Mock()
            mock_service.create_export.return_value = {
                "id": "export-123",
                "job_name": "test_export",
                "status": "queued"
            }
            MockService.return_value = mock_service
            
            request = CreateDataExportRequest(
                export_name="test_export",
                export_type="entity",
                record_type="person",
                file_format="csv",
                compression_type="none"
            )
            
            result = create_data_export(mock_context, request)
            
            assert result.id == "export-123"
            assert result.export_id == "export-123"  # property
    
    def test_download_data_export_tool(self, mock_context):
        """Test download_data_export tool function."""
        import data_ms.data_exports.tools as tools_module
        tools_module._export_service = None
        
        with patch('data_ms.data_exports.tools.DataExportService') as MockService:
            mock_service = Mock()
            mock_service.download_export.return_value = {
                "export_id": "2473561625481448",
                "file_name": "2473561625481448.csv",
                "content_type": "application/octet-stream",
                "file_size": 2647327,
                "status": "downloaded"
            }
            MockService.return_value = mock_service
            
            request = DownloadDataExportRequest(export_id="2473561625481448")
            result = download_data_export(mock_context, request)
            
            assert result.export_id == "2473561625481448"
            assert result.file_name == "2473561625481448.csv"
            assert result.file_size == 2647327
            assert result.status == "downloaded"


class TestDataExportAdapterMethods:
    """Tests for DataMSAdapter export methods."""
    
    def test_adapter_create_data_export(self):
        """Test adapter create_data_export method."""
        from data_ms.adapters.data_ms_adapter import DataMSAdapter
        
        with patch.object(DataMSAdapter, 'execute_post') as mock_post:
            mock_post.return_value = {
                "job_id": "23853101697575100",
                "status": "running"
            }
            
            adapter = DataMSAdapter()
            result = adapter.create_data_export(
                export_request={
                    "job_name": "test",
                    "export_type": "entity",
                    "record_type": "person",
                    "format": "csv",  # Note: API uses 'format' not 'file_format'
                    "compression_type": "none",
                    "search_criteria": {
                        "search_type": "entity",
                        "query": {"expressions": [{"property": "*", "condition": "contains", "value": "*"}]}
                    }
                },
                crn="crn:test:123"
            )
            
            assert result["job_id"] == "23853101697575100"
            mock_post.assert_called_once()
            
            # Verify endpoint
            call_args = mock_post.call_args
            assert call_args[0][0] == "data_exports"
    
    def test_adapter_download_data_export(self):
        """Test adapter download_data_export method makes HTTP request correctly."""
        from data_ms.adapters.data_ms_adapter import DataMSAdapter
        
        # Mock the requests.get call and AuthenticationManager
        with patch('data_ms.adapters.data_ms_adapter.requests.get') as mock_get, \
             patch('data_ms.adapters.data_ms_adapter.AuthenticationManager') as MockAuth, \
             patch('data_ms.adapters.data_ms_adapter.Config') as MockConfig:
            
            # Setup mocks
            MockConfig.API_BASE_URL = "https://test.example.com/mdm/v1"
            mock_auth_instance = Mock()
            mock_auth_instance.get_auth_headers.return_value = {
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
            MockAuth.return_value = mock_auth_instance
            
            # Mock response
            mock_response = Mock()
            mock_response.headers = {
                "content-disposition": 'attachment; filename="export.csv"',
                "content-type": "application/octet-stream"
            }
            mock_response.content = b"id,name\n1,Test"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            adapter = DataMSAdapter()
            result = adapter.download_data_export(
                export_id="export-123",
                crn="crn:test:123"
            )
            
            assert result["export_id"] == "export-123"
            assert result["file_name"] == "export.csv"
            assert result["content_type"] == "application/octet-stream"
            assert result["status"] == "downloaded"
            
            # Verify correct Accept header was used
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["Accept"] == "application/octet-stream"