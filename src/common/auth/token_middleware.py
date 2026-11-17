# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
FastMCP middleware that propagates the caller's identity into a per-request ContextVar.

Two injection strategies are supported, one per transport:

HTTP (streamable_http / sse)
    The agentic-AI microservice's TokenInjectingInterceptor stamps the user's IAM
    token into the Authorization header of each MCP tool call.  This middleware
    reads that header from the Starlette request that delivered the current
    tool call (via the MCP per-message request context) and stores the bearer
    token in the per-request ContextVar.

stdio
    HTTP headers are unavailable over stdin/stdout.  Instead, the agentic-AI
    microservice's TokenInjectingInterceptor injects credentials as a special
    "__mdm_auth__" key in the tool call's arguments.  This middleware pops that
    key from the arguments before the tool function sees them, and stores the
    bearer token in the same ContextVar.

Both transports require a valid bearer token. Requests without credentials are
rejected with a PermissionError before any tool handler is invoked.
"""

import logging
from typing import Optional

import mcp.types as mt
from starlette.requests import Request

from fastmcp.server.middleware.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult

from common.auth.user_token_context import reset_user_token, set_user_token

logger = logging.getLogger(__name__)

# Must match _MDM_STDIO_CRED_KEY in mdm_mcp_tools.py (agentic-AI microservice).
_MDM_STDIO_CRED_KEY = "__mdm_auth__"


def _request_for_current_message(context: MiddlewareContext) -> Optional[Request]:
    """
    Return the HTTP request that delivered the MCP message being handled.

    In streamable-HTTP mode the MCP SDK attaches each POST's Starlette request to
    the message it carries and exposes it via the per-message RequestContext.
    FastMCP's _current_http_request ContextVar must not be used here: in a
    stateful session it still holds the session's `initialize` request, so it
    would authorize every call with the session opener's token.

    Returns None for stdio, where no HTTP request exists.
    """
    fastmcp_context = context.fastmcp_context
    if fastmcp_context is None:
        return None
    request_context = fastmcp_context.request_context
    if request_context is None:
        return None
    return request_context.request


class UserTokenMiddleware(Middleware):
    """
    Unified identity-propagation middleware for HTTP and stdio transports.

    HTTP  → reads Authorization header from the current Starlette request.
    stdio → pops __mdm_auth__ from tool call arguments, extracts access_token.

    Sets the per-request ContextVar before calling the next handler and resets
    it in the finally block so the value never leaks into the next tool call.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        from fastmcp.server.http import _current_http_request

        reset_token = None
        tool_name = context.message.name
        http_request = _request_for_current_message(context)

        if http_request is None and _current_http_request.get() is not None:
            # HTTP transport, but the HTTP request carrying this message cannot be
            # resolved. Fail closed rather than fall back to the session-opening
            # request held in _current_http_request.
            raise PermissionError(
                f"Authorization required: unable to resolve HTTP request for tool '{tool_name}'"
            )

        if http_request is not None:
            # ── HTTP transport ──────────────────────────────────────────────
            auth_header = http_request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                bearer = auth_header[len("Bearer "):]
                if bearer:
                    reset_token = set_user_token(bearer)
                else:
                    raise PermissionError(
                        f"Authorization required: Bearer token is empty for tool '{tool_name}'"
                    )
            else:
                raise PermissionError(
                    f"Authorization required: no Bearer token supplied for tool '{tool_name}'"
                )
        else:
            # ── stdio transport ─────────────────────────────────────────────
            args = dict(context.message.arguments or {})
            creds = args.pop(_MDM_STDIO_CRED_KEY, None)

            if creds:
                token = creds.get("access_token")
                if token:
                    # Strip credential key before the tool function sees the args
                    context.message.arguments = args
                    reset_token = set_user_token(token)
                else:
                    raise PermissionError(
                        f"Authorization required: '{_MDM_STDIO_CRED_KEY}' arg present but "
                        f"access_token is empty for tool '{tool_name}'"
                    )
            else:
                raise PermissionError(
                    f"Authorization required: '{_MDM_STDIO_CRED_KEY}' arg missing for tool '{tool_name}'"
                )

        try:
            return await call_next(context)
        finally:
            if reset_token is not None:
                reset_user_token(reset_token)
