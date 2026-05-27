# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Federated search service for IBM MDM MCP server.
"""

import logging
import requests
from typing import Dict, Any, Optional

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from data_ms.adapters.data_ms_adapter import DataMSAdapter

logger = logging.getLogger(__name__)


class FederatedSearchService(BaseService):
    """Service class for federated search (potential match issue) operations."""

    def __init__(self, adapter: Optional[DataMSAdapter] = None):
        super().__init__(adapter or DataMSAdapter())
        self.adapter: DataMSAdapter = self.adapter  # type: ignore

    def search_potential_match_issues(
        self,
        ctx: Context,
        query: Dict[str, Any],
        crn: Optional[str],
        limit: int,
        offset: int,
        include_total_count: bool,
        issue_type: str,
        timezone: str,
        sort_order: str,
    ) -> Dict[str, Any]:
        """
        Execute a federated search for potential match issues.

        Orchestrates CRN validation → adapter call → error handling.
        """
        try:
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)

            self.logger.info(
                "Federated search for potential match issues — "
                "issue_type=%s, tenant=%s, session=%s",
                issue_type,
                tenant_id,
                session_id,
            )

            return self.adapter.federated_search(
                query=query,
                crn=validated_crn,
                limit=limit,
                offset=offset,
                include_total_count=include_total_count,
                issue_type=issue_type,
                timezone=timezone,
                sort_order=sort_order,
            )

        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400, "message": str(e)}

        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "federated search")

        except Exception as e:
            return self.handle_unexpected_error(e, "federated search")
