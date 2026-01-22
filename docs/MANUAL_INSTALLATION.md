# Manual Installation Guide

> **Note:** Most users should use the [Quick Start](../README.md#quick-start) automated setup. Manual installation is for advanced users or custom deployments.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Installation guide](https://git-scm.com/)
- **IBM MDM Instance** - Access to IBM MDM SaaS (IBM Cloud) or IBM MDM on Software Hub with credentials ready

> 📖 **Need help getting started?** See the detailed [Setup Guide](SETUP_GUIDE.md) for step-by-step instructions on installing prerequisites and obtaining IBM MDM credentials.

> 🔐 **Security Note (IBM Cloud only):** Generate a dedicated API key specifically for this MCP server - do not reuse existing API keys from other applications.

---

## Installation Steps

### Step 1: Clone the Repository

**Option 1: HTTPS (recommended)**
```bash
git clone https://github.com/IBM/mdm-mcp-server.git
cd mdm-mcp-server
```

**Option 2: SSH (if you have SSH keys configured)**
```bash
git clone git@github.com:IBM/mdm-mcp-server.git
cd mdm-mcp-server
```

**Option 3: Download ZIP (if git is not available)**
1. Go to the repository: https://github.com/IBM/mdm-mcp-server
2. Click the green **Code** button
3. Select **Download ZIP**
4. Extract the ZIP file to your desired location
5. Open a terminal and navigate to the extracted directory:
   ```bash
   cd mdm-mcp-server-main
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

### Step 4: Configure Environment

Create and edit the `.env` file:

```bash
cp src/.env.example src/.env
# Edit src/.env with your credentials (see below)
```

**For IBM MDM SaaS on IBM Cloud:**
```env
M360_TARGET_PLATFORM=cloud
API_CLOUD_BASE_URL=<your_mdm_base_url>  # Example: https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/ (Toronto)
API_CLOUD_AUTH_URL=https://iam.cloud.ibm.com/identity/token
API_CLOUD_API_KEY=<your_api_key>
API_CLOUD_CRN=<your_instance_crn>
MCP_TOOLS_MODE=minimal
```

**For IBM MDM on Software Hub:**
```env
M360_TARGET_PLATFORM=cpd
API_CPD_BASE_URL=<your_cpd_base_url+instance_id+mdm+v1> #Example https://cpd-xxxx.ibm.com/0000000000000000/mdm/v1/
API_CPD_AUTH_URL=<your_cpd_auth_url>
API_USERNAME=<your_username>
API_PASSWORD=<your_password>
MCP_TOOLS_MODE=minimal
```

**Tool Mode Options:**
- `minimal` (default): Exposes essential tools (`search_master_data`, `get_data_model`)
- `full`: Exposes all tools including `get_record`, `get_entity`, `get_records_entities_by_record_id`

### Step 5: Test the Server (Optional)

Verify your setup works:

```bash
# Start in HTTP mode
python src/server.py

# Server should start at http://localhost:8000
# Press Ctrl+C to stop
```

---

## Claude Desktop Integration (Manual)

If you want to use the server with Claude Desktop, follow these additional steps:

### Step 1: Find Your Python Path

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

### Step 2: Locate Claude Desktop Config

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### Step 3: Add MCP Server Configuration

Edit the config file and add (replace paths with your actual paths):

**Option A: Use existing `.env` file (Recommended)**
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

The server will read credentials from your `src/.env` file.

**Option B: Override with environment variables**
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
        "API_CLOUD_API_KEY": "<your_api_key>",
        "API_CLOUD_CRN": "<your_crn>",
        "MCP_TOOLS_MODE": "minimal"
      }
    }
  }
}
```

> **Note:** The `env` section is optional. When provided, these values take precedence over the `src/.env` file. Use this to override specific settings or manage multiple configurations.

### Step 4: Restart Claude Desktop

Restart Claude Desktop. IBM MDM tools should now appear in your conversations.

### Step 5: Verify Integration

In Claude Desktop, try asking:
```
"What IBM MDM tools are available?"
```

You should see the MDM tools listed.

---

## Troubleshooting

Having issues with manual installation? See our comprehensive troubleshooting guide:

📖 **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Complete solutions for:
- Installation and configuration issues
- Claude Desktop integration problems
- Server runtime errors
- Authentication failures

---

## Next Steps

- See [Running the Server](RUNNING_SERVER.md) for operational modes
- Check [Sample Queries](SAMPLES.md) for usage examples
- Review [Architecture](ARCHITECTURE.md) for technical details
- Visit [Claude Desktop Setup](CLAUDE_DESKTOP_SETUP.md) for integration options

---

**Need Help?** See the main [README](../README.md), [Troubleshooting Guide](TROUBLESHOOTING.md), or [open an issue](https://github.com/IBM/mdm-mcp-server/issues).