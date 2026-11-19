# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Integration tests for UserTokenMiddleware over the streamable-HTTP transport.

Each tool call must be authorized with the bearer token carried by the HTTP
request of that call, not the token of the request that opened the session.
"""

import json

import pytest
from fastmcp import FastMCP
from starlette.testclient import TestClient

from common.auth.token_middleware import UserTokenMiddleware
from common.auth.user_token_context import get_user_token

PROTOCOL_VERSION = "2025-06-18"
ACCEPT = "application/json, text/event-stream"


def _build_app():
    mcp = FastMCP("token-middleware-test", middleware=[UserTokenMiddleware()])

    @mcp.tool
    def whoami() -> str:
        """Return the bearer token the middleware bound to this call."""
        return get_user_token() or ""

    return mcp.http_app(transport="http", json_response=True)


def _headers(token=None, session_id=None):
    headers = {"accept": ACCEPT, "content-type": "application/json"}
    if token is not None:
        headers["authorization"] = f"Bearer {token}"
    if session_id is not None:
        headers["mcp-session-id"] = session_id
    return headers


def _open_session(client, token=None):
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0"},
        },
    }
    resp = client.post("/mcp", json=init, headers=_headers(token))
    assert resp.status_code == 200, resp.text
    session_id = resp.headers["mcp-session-id"]
    client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=_headers(token, session_id),
    )
    return session_id


def _call_whoami(client, session_id, token=None, call_id=2):
    body = {
        "jsonrpc": "2.0",
        "id": call_id,
        "method": "tools/call",
        "params": {"name": "whoami", "arguments": {}},
    }
    resp = client.post("/mcp", json=body, headers=_headers(token, session_id))
    assert resp.status_code == 200, resp.text
    return resp.json()


def _tool_text(payload):
    result = payload["result"]
    return result["content"][0]["text"] if result.get("content") else ""


@pytest.fixture
def client():
    with TestClient(_build_app()) as test_client:
        yield test_client


@pytest.mark.integration
def test_tool_call_uses_its_own_bearer_not_session_openers(client):
    session_id = _open_session(client, token="ALICE_TOKEN")

    bob = _call_whoami(client, session_id, token="BOB_TOKEN", call_id=2)
    carol = _call_whoami(client, session_id, token="CAROL_TOKEN", call_id=3)

    assert _tool_text(bob) == "BOB_TOKEN"
    assert _tool_text(carol) == "CAROL_TOKEN"


@pytest.mark.integration
def test_session_opened_without_token_accepts_call_with_token(client):
    session_id = _open_session(client, token=None)

    payload = _call_whoami(client, session_id, token="ERIN_TOKEN")

    assert not payload["result"].get("isError"), json.dumps(payload)
    assert _tool_text(payload) == "ERIN_TOKEN"


@pytest.mark.integration
def test_tool_call_without_token_is_rejected(client):
    session_id = _open_session(client, token="ALICE_TOKEN")

    payload = _call_whoami(client, session_id, token=None)

    assert "error" in payload or payload["result"].get("isError"), json.dumps(payload)
    assert "ALICE_TOKEN" not in json.dumps(payload)


@pytest.mark.integration
def test_tool_call_with_empty_bearer_is_rejected(client):
    session_id = _open_session(client, token="ALICE_TOKEN")

    payload = _call_whoami(client, session_id, token="")

    assert "error" in payload or payload["result"].get("isError"), json.dumps(payload)
    assert "ALICE_TOKEN" not in json.dumps(payload)


@pytest.mark.integration
def test_stdio_credentials_in_args_are_ignored_over_http(client):
    session_id = _open_session(client, token="ALICE_TOKEN")
    body = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "whoami",
            "arguments": {"__mdm_auth__": {"access_token": "MALLORY_TOKEN"}},
        },
    }

    resp = client.post("/mcp", json=body, headers=_headers("BOB_TOKEN", session_id))
    result = resp.json()["result"]

    assert result.get("structuredContent", {}).get("result") != "MALLORY_TOKEN"


@pytest.mark.integration
def test_non_http_transport_still_uses_stdio_credentials():
    import asyncio

    from fastmcp import Client

    mcp = FastMCP("token-middleware-stdio", middleware=[UserTokenMiddleware()])

    @mcp.tool
    def whoami() -> str:
        """Return the bearer token the middleware bound to this call."""
        return get_user_token() or ""

    async def _call() -> str:
        async with Client(mcp) as client:
            result = await client.call_tool(
                "whoami", {"__mdm_auth__": {"access_token": "STDIO_TOKEN"}}
            )
            return result.data

    assert asyncio.run(_call()) == "STDIO_TOKEN"
