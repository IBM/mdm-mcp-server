# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Data quality issues service for IBM MDM MCP server.

Encapsulates business logic for GET /mdm/v1/data_quality/issues,
following Hexagonal Architecture. Belongs to the Matching Microservice.
"""

import logging
import requests
from typing import Dict, Any, List, Optional

from fastmcp import Context

from common.core.base_service import BaseService
from common.domain.crn_validator import CRNValidationError
from matching_ms.adapters.matching_ms_adapter import MatchingMSAdapter

logger = logging.getLogger(__name__)


class DataQualityIssuesService(BaseService):
    """Service class for retrieving data quality issues per entity/record."""

    def __init__(self, adapter: Optional[MatchingMSAdapter] = None):
        super().__init__(adapter or MatchingMSAdapter())
        self.adapter: MatchingMSAdapter = self.adapter  # type: ignore

    def get_data_quality_issues(
        self,
        ctx: Context,
        entity_type: str,
        crn: Optional[str],
        record_number: Optional[int],
        entities: Optional[List[str]],
        limit: int,
        offset: int,
        fetch_total_count: bool,
        include_tags: bool,
        include_record_attributes: Optional[str],
        return_linked_issues: bool,
    ) -> Dict[str, Any]:
        """
        Retrieve data quality issues for given entities or record.

        Orchestrates CRN validation → adapter call → error handling.

        Args:
            ctx: MCP Context object with session information
            entity_type: Required entity type identifier (e.g. "person_entity")
            crn: Cloud Resource Name identifying the tenant (optional)
            record_number: Optional source record identifier
            entities: Optional list of entity identifiers
            limit: Number of issues to retrieve
            offset: Number of issues to skip
            fetch_total_count: Whether to return the total issue count
            include_tags: Whether to include tag details per issue
            include_record_attributes: Comma-separated record attribute names to include
            return_linked_issues: Whether to include issues where both records share an entity

        Returns:
            Paged data quality issues response or error response
        """
        try:
            session_id, validated_crn, tenant_id = self.validate_session_and_crn(ctx, crn)

            self.logger.info(
                "Retrieving data quality issues — entity_type=%s, tenant=%s, session=%s",
                entity_type,
                tenant_id,
                session_id,
            )

            return self.adapter.get_data_quality_issues(
                entity_type=entity_type,
                crn=validated_crn,
                record_number=record_number,
                entities=entities,
                limit=limit,
                offset=offset,
                fetch_total_count=fetch_total_count,
                include_tags=include_tags,
                include_record_attributes=include_record_attributes,
                return_linked_issues=return_linked_issues,
            )

        except CRNValidationError as e:
            return e.args[0] if e.args else {"error": str(e), "status_code": 400, "message": str(e)}

        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, "retrieve data quality issues", {"entity_type": entity_type})

        except Exception as e:
            return self.handle_unexpected_error(e, "retrieve data quality issues")
