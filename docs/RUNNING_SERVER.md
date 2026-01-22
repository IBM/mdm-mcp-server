# Running the Server Guide

This guide covers different ways to run the IBM MDM MCP Server, including operational modes, configuration options, and troubleshooting.

## Operational Modes

The server supports two operational modes:

### HTTP Mode (Testing & Development)

HTTP mode runs the server as a web service, ideal for testing and development with tools like MCP Inspector.

### STDIO Mode (Production)

STDIO mode is used for MCP client integration (like Claude Desktop). The server communicates via standard input/output instead of HTTP.

---

## Running via PyPI Installation

If you installed the package via PyPI, you can run it directly:

### Basic Usage

```bash
# Start in HTTP mode (default)
ibm_mdm_mcp_server

# Server starts at http://localhost:8000
```

### Custom Port

```bash
# Start on a custom port
ibm_mdm_mcp_server --port 3000
```

### STDIO Mode

```bash
# Start in STDIO mode (for MCP clients)
ibm_mdm_mcp_server --mode stdio
```

### Available Options

```bash
ibm_mdm_mcp_server --help
```

Options:
- `--mode` or `-m`: Operation mode (`http` or `stdio`). Default: `http`
- `--port` or `-p`: Port number for HTTP mode. Default: `8000`

---

## Running from Source

If you cloned the repository, you can run the server using Python:

### With Virtual Environment

**macOS/Linux:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the server
python src/server.py
```

**Windows:**
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the server
python src\server.py
```

### Direct Execution

**macOS/Linux:**
```bash
.venv/bin/python src/server.py
```

**Windows:**
```bash
.venv\Scripts\python src\server.py
```

### Custom Configuration

```bash
# Start on custom port
python src/server.py --port 3000

# Start in STDIO mode
python src/server.py --mode stdio
```

---

## Testing with MCP Inspector

The MCP Inspector is a useful tool for testing and debugging your MCP server.

### Setup

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector
```

### Usage

**Option 1: Auto-detection (Recommended)**
```bash
# Start your server in one terminal
ibm_mdm_mcp_server

# In another terminal, run inspector
npx @modelcontextprotocol/inspector
```

The inspector will automatically detect the running server at `http://localhost:8000`.

**Option 2: Specify URL**
```bash
# If running on a custom port
npx @modelcontextprotocol/inspector http://localhost:3000
```

### Inspector Features

- **Tool Testing**: Test individual MCP tools
- **Request/Response Inspection**: View detailed API interactions
- **Schema Validation**: Verify tool schemas
- **Error Debugging**: Identify and fix issues

---

## Running with Claude Desktop

Claude Desktop automatically manages the server lifecycle when configured properly.

### Configuration

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Using PyPI installation:**
```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "ibm_mdm_mcp_server",
      "args": ["--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cloud",
        "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
        "API_CLOUD_AUTH_URL": "https://iam.cloud.ibm.com/identity/token",
        "API_CLOUD_API_KEY": "<your_api_key>",
        "API_CLOUD_CRN": "<your_crn>",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

**Using source installation:**
```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/src/server.py", "--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cloud",
        "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
        "API_CLOUD_AUTH_URL": "https://iam.cloud.ibm.com/identity/token",
        "API_CLOUD_API_KEY": "<your_api_key>",
        "API_CLOUD_CRN": "<your_crn>",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

### Lifecycle Management

- **Start**: Claude Desktop automatically starts the server when needed
- **Stop**: Server stops when Claude Desktop closes
- **Restart**: Restart Claude Desktop to reload configuration changes

### Verification

In Claude Desktop, ask:
```
"What IBM MDM tools are available?"
```

You should see the configured tools listed.

---

## Stopping the Server

### Graceful Shutdown

**In the terminal:**
Press `Ctrl+C` to stop the server gracefully.

### Force Stop

**macOS/Linux:**
```bash
# Find the process
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

**Windows:**
```bash
# Find the process
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

---

## Environment Variables

The server reads configuration from environment variables or a `.env` file.

### Priority Order

1. Environment variables in Claude Desktop config (highest priority)
2. System environment variables
3. `.env` file in working directory
4. `.env` file in `src/` directory (lowest priority)

### Required Variables

**For IBM Cloud:**
- `M360_TARGET_PLATFORM=cloud`
- `API_CLOUD_BASE_URL`
- `API_CLOUD_AUTH_URL`
- `API_CLOUD_API_KEY`
- `API_CLOUD_CRN`

**For Software Hub:**
- `M360_TARGET_PLATFORM=cpd`
- `API_CPD_BASE_URL`
- `API_CPD_AUTH_URL`
- `API_USERNAME`
- `API_PASSWORD`

### Optional Variables

- `MCP_TOOLS_MODE`: `minimal` (default) or `full`
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`

---

## Logging

### Log Levels

Configure logging via environment variable:

```bash
export LOG_LEVEL=DEBUG
ibm_mdm_mcp_server
```

Levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Log Output

**HTTP Mode:**
Logs are written to stdout/stderr and visible in the terminal.

**STDIO Mode:**
Logs are written to Claude Desktop's log files:
- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\logs\mcp*.log`

---

## Performance Tuning

### Connection Pooling

The server uses connection pooling for efficient API communication. Default settings:
- Max connections: 100
- Max keepalive connections: 20
- Keepalive expiry: 5 seconds

### Token Caching

Authentication tokens are cached to reduce API calls:
- Cache duration: Based on token expiry
- Automatic refresh: 5 minutes before expiry

### Memory Management

For long-running servers, monitor memory usage:

```bash
# macOS/Linux
ps aux | grep ibm_mdm_mcp_server

# Windows
tasklist | findstr python
```

---

## Troubleshooting

Having issues running the server? See our comprehensive troubleshooting guide:

📖 **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Complete solutions for:

**Server Runtime Issues:**
- [Server Won't Start](TROUBLESHOOTING.md#server-wont-start)
- [Port Already in Use](TROUBLESHOOTING.md#port-already-in-use)
- [Server Crashes](TROUBLESHOOTING.md#server-crashes)
- [Performance Issues](TROUBLESHOOTING.md#performance-issues)

**Authentication Issues:**
- [IBM Cloud Authentication Errors](TROUBLESHOOTING.md#ibm-cloud-authentication-errors)
- [Software Hub Authentication Errors](TROUBLESHOOTING.md#software-hub-authentication-errors)
- [Token Expiration Issues](TROUBLESHOOTING.md#token-expiration-issues)

**Network Issues:**
- [Connection Timeouts](TROUBLESHOOTING.md#connection-timeouts)
- [Firewall Blocking](TROUBLESHOOTING.md#firewall-blocking)
- [VPN Requirements](TROUBLESHOOTING.md#vpn-requirements)

**Claude Desktop Integration:**
- [Tools Don't Appear](TROUBLESHOOTING.md#tools-dont-appear-in-claude-desktop)
- [Server Connection Failures](TROUBLESHOOTING.md#server-connection-failures)

For detailed step-by-step solutions, see the [full troubleshooting documentation](TROUBLESHOOTING.md).

---

## Advanced Configuration

### Custom Server Script

Create a custom startup script:

```bash
#!/bin/bash
# start_mdm_server.sh

# Set environment
export M360_TARGET_PLATFORM=cloud
export API_CLOUD_BASE_URL="https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/"
export API_CLOUD_AUTH_URL="https://iam.cloud.ibm.com/identity/token"
export API_CLOUD_API_KEY="your_api_key"
export API_CLOUD_CRN="your_crn"
export MCP_TOOLS_MODE=minimal
export LOG_LEVEL=INFO

# Start server
ibm_mdm_mcp_server --port 8000
```

Make it executable:
```bash
chmod +x start_mdm_server.sh
./start_mdm_server.sh
```

### Systemd Service (Linux)

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/ibm-mdm-mcp.service
[Unit]
Description=IBM MDM MCP Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/mdm-mcp-server
Environment="M360_TARGET_PLATFORM=cloud"
Environment="API_CLOUD_BASE_URL=https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/"
ExecStart=/path/to/.venv/bin/ibm_mdm_mcp_server
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ibm-mdm-mcp
sudo systemctl start ibm-mdm-mcp
sudo systemctl status ibm-mdm-mcp
```

---

## Additional Resources

- [Configuration Guide](MANUAL_INSTALLATION.md#configuration)
- [Testing Guide](TESTING.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)

---

**Need Help?** See the main [README](../README.md) or [open an issue](https://github.com/IBM/mdm-mcp-server/issues).