# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Quality issues service for IBM MDM MCP server.

This module provides a service class that encapsulates the business logic for
retrieving data quality issues, following Hexagonal Architecture.
"""

import logging
import requests
from typing import Dict, Any, Optional

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from data_ms.adapters.data_ms_adapter import DataMSAdapter

logger = logging.getLogger(__name__)


class QualityIssuesService(BaseService):
    """Service class for retrieving data quality issues."""

    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        super().__init__(adapter or DataMSAdapter())
        self.adapter: DataMSAdapter = self.adapter  # type: ignore

    def get_quality_issues(
        self,
        ctx: Context,
        issue_type: str,
        entity_type: Optional[str],
        entity_type_name: Optional[str],
        crn: Optional[str],
        offset: int,
        limit: int,
        include_total_count: bool,
        include_total_count_without_tasks: bool,
    ) -> Dict[str, Any]:
        """
        Retrieve data quality issues for a given issue type.

        Orchestrates CRN validation → adapter call → error handling.

        Args:
            ctx: MCP Context object with session information
            issue_type: The type of quality issue to search for (required query param)
            entity_type: Entity type to include in the request body (e.g. "record")
            entity_type_name: Entity type name as defined in workflow configuration
            crn: Cloud Resource Name identifying the tenant (optional)
            offset: Number of issues to skip for pagination
            limit: Maximum number of issues to return (max 50)
            include_total_count: Whether to include total count on non-first pages
            include_total_count_without_tasks: Whether to include total count without tasks

        Returns:
            Paged quality issues response or error response
        """
        try:
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)

            self.logger.info(
                "Retrieving quality issues — issue_type=%s, tenant=%s, session=%s",
                issue_type,
                tenant_id,
                session_id,
            )

            return self.adapter.get_quality_issues(
                issue_type=issue_type,
                entity_type=entity_type,
                entity_type_name=entity_type_name,
                crn=validated_crn,
                offset=offset,
                limit=limit,
                include_total_count=include_total_count,
                include_total_count_without_tasks=include_total_count_without_tasks,
            )

        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400, "message": str(e)}

        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "retrieve quality issues", {"issue_type": issue_type})

        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve quality issues")
