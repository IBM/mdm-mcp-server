# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""Exercise startup and token middleware against the installed FastMCP runtime."""

import asyncio
import os
from pathlib import Path
import sys

import mcp.types as mt
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import pytest


@pytest.mark.parametrize("tools_mode", ["minimal", "full"])
def test_stdio_startup_and_unauthenticated_call(tmp_path, tools_mode):
    """Initialize a real child server, list tools and reject a call without a token."""
    # Block outbound connections in the child so this test cannot call IBM APIs.
    (tmp_path / "sitecustomize.py").write_text(
        "import socket\n"
        "def blocked_connect(self, address):\n"
        "    raise RuntimeError('Outbound connections disabled in startup test')\n"
        "socket.socket.connect = blocked_connect\n"
        "socket.socket.connect_ex = blocked_connect\n"
    )
    src = Path(__file__).resolve().parents[1] / "src"
    env = {
        "PYTHONPATH": os.pathsep.join([str(tmp_path), str(src)]),
        "M360_TARGET_PLATFORM": "cloud",
        "MCP_TOOLS_MODE": tools_mode,
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
    }
    for name in (
        "API_CLOUD_BASE_URL", "API_CLOUD_AUTH_URL", "API_CLOUD_API_KEY",
        "API_CLOUD_CRN", "API_CPD_BASE_URL", "API_CPD_AUTH_URL",
        "API_USERNAME", "API_PASSWORD",
    ):
        env[name] = ""

    async def check():
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-c", "from server import main; main()", "--mode", "stdio"],
            env=env,
            cwd=str(tmp_path),
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "mdm-mcp-server"
                tools = {tool.name for tool in (await session.list_tools()).tools}
                assert {
                    "search_master_data", "search_potential_match_issues",
                    "get_data_quality_issues", "get_data_model",
                } <= tools
                assert ("get_record" in tools) == (tools_mode == "full")
                result = await session.call_tool("get_data_model", {})
                assert result.isError
                assert any(
                    "Authorization required" in getattr(item, "text", "")
                    for item in result.content
                )

    # wait_for also works on Python 3.10, the package's minimum Python version.
    asyncio.run(asyncio.wait_for(check(), timeout=30))


@pytest.mark.parametrize("transport", ["http", "stdio"])
@pytest.mark.parametrize("handler_fails", [False, True])
def test_token_propagation_and_cleanup(transport, handler_fails):
    from fastmcp.server.http import _current_http_request
    from fastmcp.server.middleware import MiddlewareContext
    from fastmcp.tools.tool import ToolResult
    from starlette.requests import Request

    from common.auth.token_middleware import UserTokenMiddleware
    from common.auth.user_token_context import (
        get_user_token, reset_user_token, set_user_token,
    )

    async def check():
        arguments = {"session_id": "test-session"}
        request = None
        if transport == "http":
            request = Request({
                "type": "http",
                "headers": [(b"authorization", b"Bearer test-caller-token")],
            })
        else:
            arguments["__mdm_auth__"] = {"access_token": "test-caller-token"}
        context = MiddlewareContext(
            message=mt.CallToolRequestParams(name="get_data_model", arguments=arguments)
        )

        async def call_next(received):
            assert get_user_token() == "test-caller-token"
            assert received.message.arguments == {"session_id": "test-session"}
            if handler_fails:
                raise RuntimeError("test handler failed")
            return ToolResult(content=[])

        outer_token = set_user_token("outer-token")
        http_token = _current_http_request.set(request)
        try:
            if handler_fails:
                with pytest.raises(RuntimeError, match="test handler failed"):
                    await UserTokenMiddleware().on_call_tool(context, call_next)
            else:
                await UserTokenMiddleware().on_call_tool(context, call_next)
            assert get_user_token() == "outer-token"
        finally:
            _current_http_request.reset(http_token)
            reset_user_token(outer_token)

    asyncio.run(check())
