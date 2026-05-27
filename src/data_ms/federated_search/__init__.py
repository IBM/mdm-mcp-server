# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Federated search module for IBM MDM MCP server.
"""

from .tools import search_potential_match_issues, FEDERATED_SEARCH_TOOL_DESCRIPTION

__all__ = ['search_potential_match_issues', 'FEDERATED_SEARCH_TOOL_DESCRIPTION']
