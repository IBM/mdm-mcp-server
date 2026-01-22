# Claude Desktop Setup Guide

This comprehensive guide covers all methods for integrating the IBM MDM MCP Server with Claude Desktop, including PyPI package installation, uvx usage, source code setup, and HTTP mode configuration.

## Prerequisites

Before you begin, ensure you have:

- **Claude Desktop** - [Download here](https://claude.ai/download)
- **IBM MDM Credentials** - See [Setup Guide](SETUP_GUIDE.md) for obtaining credentials
- **Python 3.10+** (for most methods) - [Download here](https://www.python.org/downloads/)

---

## Table of Contents

- [Method 1: Using PyPI Package (Recommended)](#method-1-using-pypi-package-recommended)
- [Method 2: Using uvx (Easiest)](#method-2-using-uvx-easiest)
- [Method 3: From Source Code](#method-3-from-source-code)
- [Method 4: HTTP Mode (Advanced)](#method-4-http-mode-advanced)
- [Configuration Options](#configuration-options)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Method 1: Using PyPI Package (Recommended)

This method uses the published PyPI package for easy installation and updates.

### Step 1: Install the Package

```bash
pip install ibm-mdm-mcp-server
```

### Step 2: Locate Claude Desktop Config

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 3: Configure Claude Desktop

Edit the config file and add:

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
        "API_CLOUD_API_KEY": "your_api_key_here",
        "API_CLOUD_CRN": "your_crn_here",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop to activate the integration.

---

## Method 2: Using uvx (Easiest)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and runner. This method doesn't require a separate pip install step.

### Step 1: Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

📖 **For more installation options**, see the [uv installation guide](https://github.com/astral-sh/uv#installation).

### Step 2: Configure Claude Desktop

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "uvx",
      "args": ["ibm-mdm-mcp-server", "--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cloud",
        "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
        "API_CLOUD_AUTH_URL": "https://iam.cloud.ibm.com/identity/token",
        "API_CLOUD_API_KEY": "your_api_key_here",
        "API_CLOUD_CRN": "your_crn_here",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. The first time it runs, `uvx` will automatically download and cache the package.

### Benefits of uvx

- ✅ **No manual installation** - Automatically downloads the package
- ✅ **Automatic updates** - Always uses the latest version
- ✅ **Isolated environment** - Doesn't interfere with other Python packages
- ✅ **Fast execution** - Cached for quick startup

---

## Method 3: From Source Code

This method is ideal for development or when you need to customize the server.

### Step 1: Clone the Repository

```bash
git clone https://github.com/IBM/mdm-mcp-server.git
cd mdm-mcp-server
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Find Python Path

With the virtual environment activated:

**macOS/Linux:**
```bash
which python
# Example output: /Users/yourname/mdm-mcp-server/.venv/bin/python
```

**Windows:**
```bash
where python
# Example output: C:\Users\yourname\mdm-mcp-server\.venv\Scripts\python.exe
```

### Step 5: Configure Claude Desktop

Edit your Claude Desktop config file and add (use absolute paths):

```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/mdm-mcp-server/src/server.py", "--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cloud",
        "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
        "API_CLOUD_AUTH_URL": "https://iam.cloud.ibm.com/identity/token",
        "API_CLOUD_API_KEY": "your_api_key_here",
        "API_CLOUD_CRN": "your_crn_here",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

**Alternative: Using .env file**

If you prefer to keep credentials in a `.env` file:

1. Create `src/.env` with your credentials:
   ```env
   M360_TARGET_PLATFORM=cloud
   API_CLOUD_BASE_URL=https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/
   API_CLOUD_AUTH_URL=https://iam.cloud.ibm.com/identity/token
   API_CLOUD_API_KEY=your_api_key_here
   API_CLOUD_CRN=your_crn_here
   MCP_TOOLS_MODE=minimal
   ```

2. Simplify Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "ibm-mdm": {
         "command": "/absolute/path/to/.venv/bin/python",
         "args": ["/absolute/path/to/mdm-mcp-server/src/server.py", "--mode", "stdio"]
       }
     }
   }
   ```

### Step 6: Restart Claude Desktop

Close and reopen Claude Desktop to activate the integration.

---

## Method 4: HTTP Mode (Advanced)

This method runs the server as a separate HTTP service, useful for debugging or when you need more control.

### Step 1: Start the Server

**Using PyPI package:**
```bash
ibm_mdm_mcp_server --port 8000
```

**From source:**
```bash
python src/server.py --port 8000
```

The server will start at `http://localhost:8000`.

### Step 2: Configure Claude Desktop

Claude Desktop requires the `mcp-remote` package to connect to HTTP MCP servers. Edit your Claude Desktop config file:

**For local server (no authentication):**
```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "http://localhost:8000"
      ]
    }
  }
}
```

**For remote server with authentication:**
```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "https://your-server-url.com",
        "--header",
        "Authorization: Bearer ${AUTH_TOKEN}"
      ],
      "env": {
        "AUTH_TOKEN": "your_api_key_here"
      }
    }
  }
}
```

**For custom headers:**
```json
{
  "mcpServers": {
    "ibm-mdm": {
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "http://localhost:8000",
        "--header",
        "X-Custom-Header: value"
      ]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. The `mcp-remote` package will be automatically installed on first use.

### Important Notes for HTTP Mode

- ⚠️ **Server must be running** - You need to manually start the server before using Claude Desktop
- ⚠️ **Port availability** - Ensure the port is not used by other applications
- ⚠️ **Credentials** - Configure via environment variables or `.env` file when starting the server
- ⚠️ **mcp-remote required** - Claude Desktop uses `mcp-remote` to bridge HTTP to STDIO
- ✅ **Debugging** - Easier to see server logs and debug issues
- ✅ **Multiple clients** - Can be accessed by multiple MCP clients simultaneously
- ✅ **Remote servers** - Can connect to servers running on different machines
- ✅ **Custom authentication** - Support for custom headers and authentication schemes

---

## Configuration Options

### Platform Configuration

**For IBM MDM SaaS on IBM Cloud:**
```json
"env": {
  "M360_TARGET_PLATFORM": "cloud",
  "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
  "API_CLOUD_AUTH_URL": "https://iam.cloud.ibm.com/identity/token",
  "API_CLOUD_API_KEY": "your_api_key_here",
  "API_CLOUD_CRN": "your_crn_here",
  "MCP_TOOLS_MODE": "minimal"
}
```

**For IBM MDM on Software Hub:**
```json
"env": {
  "M360_TARGET_PLATFORM": "cpd",
  "API_CPD_BASE_URL": "https://cpd-xxxx.ibm.com/instance_id/mdm/v1/",
  "API_CPD_AUTH_URL": "https://cpd-xxxx.ibm.com/icp4d-api/v1/authorize",
  "API_USERNAME": "your_username",
  "API_PASSWORD": "your_password",
  "MCP_TOOLS_MODE": "minimal"
}
```

### Tool Mode Options

- **`minimal`** (default): Exposes essential tools
  - `search_master_data`
  - `get_data_model`

- **`full`**: Exposes all available tools
  - `search_master_data`
  - `get_data_model`
  - `get_record`
  - `get_entity`
  - `get_records_entities_by_record_id`

Set via: `"MCP_TOOLS_MODE": "full"`

### Regional Endpoints (IBM Cloud)

Choose the endpoint closest to your MDM instance:

| Region | Base URL |
|--------|----------|
| Toronto | `https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/` |
| Dallas | `https://api.us-south.dai.cloud.ibm.com/mdm/v1/` |
| Frankfurt | `https://api.eu-de.dai.cloud.ibm.com/mdm/v1/` |
| London | `https://api.eu-gb.dai.cloud.ibm.com/mdm/v1/` |
| Sydney | `https://api.au-syd.dai.cloud.ibm.com/mdm/v1/` |
| Tokyo | `https://api.jp-tok.dai.cloud.ibm.com/mdm/v1/` |

---

## Verification

### Step 1: Check Server Status

In Claude Desktop, look for the MCP server indicator (usually in the bottom-left corner or settings).

### Step 2: Test Integration

Ask Claude:
```
"What IBM MDM tools are available?"
```

You should see a list of available tools.

### Step 3: Test Functionality

Try a simple query:
```
"What entity types are available in my MDM system?"
```

Claude should use the `get_data_model` tool to retrieve and display the information.

---

## Troubleshooting

Having issues with Claude Desktop integration? See our comprehensive troubleshooting guide:

📖 **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Complete solutions for:

**Claude Desktop Integration Issues:**
- [Tools Don't Appear in Claude Desktop](TROUBLESHOOTING.md#tools-dont-appear-in-claude-desktop)
- [Server Connection Failures](TROUBLESHOOTING.md#server-connection-failures)
- [Configuration File Issues](TROUBLESHOOTING.md#configuration-file-issues)
- [Path Problems](TROUBLESHOOTING.md#path-problems)

**Server Issues:**
- [Server Won't Start](TROUBLESHOOTING.md#server-wont-start)
- [Authentication Errors](TROUBLESHOOTING.md#authentication-issues)
- [Performance Issues](TROUBLESHOOTING.md#performance-issues)

**uvx Issues:**
- [uvx Command Not Found](TROUBLESHOOTING.md#uvx-command-not-found)
- [Package Download Failures](TROUBLESHOOTING.md#package-download-failures)
- [Cache Issues](TROUBLESHOOTING.md#cache-issues)

**HTTP Mode Issues:**
- [mcp-remote Problems](TROUBLESHOOTING.md#mcp-remote-problems)
- [Remote Server Access](TROUBLESHOOTING.md#remote-server-access)

For detailed step-by-step solutions, see the [full troubleshooting documentation](TROUBLESHOOTING.md).

---

## Multiple Configurations

You can configure multiple MCP servers in Claude Desktop:

```json
{
  "mcpServers": {
    "ibm-mdm-production": {
      "command": "ibm_mdm_mcp_server",
      "args": ["--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cloud",
        "API_CLOUD_BASE_URL": "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/",
        "API_CLOUD_API_KEY": "prod_api_key",
        "API_CLOUD_CRN": "prod_crn",
        "MCP_TOOLS_MODE": "minimal"
      }
    },
    "ibm-mdm-development": {
      "command": "ibm_mdm_mcp_server",
      "args": ["--mode", "stdio"],
      "env": {
        "M360_TARGET_PLATFORM": "cpd",
        "API_CPD_BASE_URL": "https://dev-cpd.example.com/mdm/v1/",
        "API_USERNAME": "dev_user",
        "API_PASSWORD": "dev_password",
        "MCP_TOOLS_MODE": "full"
      }
    }
  }
}
```

---

## Security Best Practices

1. **Protect credentials:**
   - Never commit credentials to version control
   - Use environment variables or secure vaults
   - Rotate API keys regularly

2. **Use minimal permissions:**
   - Grant only necessary MDM permissions
   - Use read-only credentials when possible

3. **Secure configuration files:**
   - Set appropriate file permissions on config files
   - Don't share config files with credentials

4. **Monitor usage:**
   - Review Claude Desktop logs regularly
   - Monitor API usage in IBM Cloud/Software Hub

---

## Additional Resources

- [Setup Guide](SETUP_GUIDE.md) - Obtaining IBM MDM credentials
- [Running Server Guide](RUNNING_SERVER.md) - Server operations and modes
- [Manual Installation Guide](MANUAL_INSTALLATION.md) - Detailed installation steps
- [Testing Guide](TESTING.md) - Testing and validation
- [uv Documentation](https://github.com/astral-sh/uv) - uv package manager
- [Claude Desktop Documentation](https://claude.ai/docs) - Official Claude Desktop docs
- [MCP Protocol](https://modelcontextprotocol.io) - Model Context Protocol specification

---

**Need Help?** See the main [README](../README.md) or [open an issue](https://github.com/IBM/mdm-mcp-server/issues).