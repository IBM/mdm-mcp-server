# FastMCP compatibility

## Why this change is needed

The published `ibm_mdm_mcp_server==1.0.10` wheel declares
`fastmcp>=2.14.0`. An unrestricted installation can select FastMCP 4, which
removed the `fastmcp.tools.tool` module used by that wheel. The resulting
import error terminates the STDIO server before MCP initialization.

This source tree pins `fastmcp==2.14.7` in both dependency files. The token
middleware imports `ToolResult` from `fastmcp.tools.tool`, its location in
that version. The server imports `Tool` from `fastmcp.tools`.

A future compatibility range or major-version upgrade should be validated
before changing the pin.

The existing authentication policy is preserved: HTTP tool calls require a
bearer token; STDIO tool calls require an `__mdm_auth__` argument containing
`access_token`. Configuring environment variables alone does not bypass that
per-call requirement. Token validation and IBM API access are outside the
startup checks described here.

## Validate a source checkout

Use Python 3.10 or later in a dedicated virtual environment:

```bash
python -m venv .venv
.venv/bin/python -m pip install '.[dev]' build
.venv/bin/python -m pip check
.venv/bin/python -m pytest
.venv/bin/python -m build --wheel
```

`tests/test_runtime_compatibility.py` starts a real STDIO server in minimal and
full modes, initializes MCP, lists tools, and checks rejection of a tool call
without credentials. Outbound connections are blocked in the child process.
It also checks token propagation and context cleanup for both transports,
including when the tool handler raises an exception.

Install the built wheel into a separate virtual environment and repeat the
MCP initialization and `tools/list` check through the installed
`ibm_mdm_mcp_server --mode stdio` console command. This verifies the packaged
artifact rather than importing the checkout by accident.

## Release requirement

Existing PyPI 1.0.10 artifacts retain their original dependency metadata.
Merging the source fix does not change those artifacts: maintainers must
publish a new package version for ordinary package-based installations to
receive the pin. Do not replace an existing official release with a modified
artifact under the same version.
