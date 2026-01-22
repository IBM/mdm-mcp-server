<!--
This file has been modified with the assistance of IBM Bob (AI Code Assistant)
-->

# IBM MDM MCP Server - Setup Guide

This guide provides detailed information about using the automated setup script.

## Before You Begin

### Prerequisites Checklist

Before running the setup script, make sure you have:

- ✅ **Python 3.10+** installed and accessible via `python` or `python3` command
- ✅ **Git** installed (to clone the repository)
- ✅ **IBM MDM instance credentials** ready:
  - For IBM Cloud: API Key, CRN, and Base URL
  - For Software Hub: Username, Password, Base URL, and Auth URL
- ✅ **Claude Desktop** installed (optional, only if using Claude Desktop integration)

### Getting Your IBM MDM Credentials

**For IBM Cloud:**
1. Log in to [IBM Cloud Console](https://cloud.ibm.com/)
2. Navigate to your MDM service instance
3. Copy the **Base URL** from the service details
4. Create an **API Key** from [IAM API Keys](https://cloud.ibm.com/iam/apikeys)
5. Copy the **CRN** (Cloud Resource Name) from service details

**For Software Hub:**
1. Get your Software Hub instance URL from your administrator
2. Note your admin username and password
3. The auth URL is typically: `https://your-instance.com/icp4d-api/v1/authorize`

### Installing Prerequisites

**Python 3.10+:**
```bash
# Check version
python --version

# If needed, download from https://www.python.org/downloads/
```

**Claude Desktop (Optional):**
- Download from [claude.ai/download](https://claude.ai/download)
- Install for your operating system
- Launch once to create config directory

## Quick Start

The easiest way to get started is to use the automated setup wizard:

```bash
python setup_wizard.py
```

This will launch an interactive wizard that guides you through the entire setup process.

## Setup Wizard Features

The `setup_wizard.py` script automates:

1. **Virtual Environment Creation** - Creates and configures a Python virtual environment
2. **Dependency Installation** - Installs all required packages automatically
3. **Environment Configuration** - Interactive prompts for your IBM MDM credentials
4. **Claude Desktop Integration** - Automatically configures Claude Desktop (optional)
5. **HTTP Mode Setup** - Prepares the server for MCP Inspector testing (optional)

## Usage Options

### Interactive Setup (Recommended)

```bash
python setup_wizard.py
```

This mode will:
- Ask you to choose your platform (IBM Cloud or Software Hub)
- Prompt for your credentials
- Let you select tool mode (minimal or full)
- Ask which setup mode you want (Claude Desktop or HTTP)

### Claude Desktop Integration Only

```bash
python setup_wizard.py --claude
```

Use this when you want to:
- Use the MCP server exclusively with Claude Desktop
- Automatic configuration of Claude Desktop config file

After setup:
1. Restart Claude Desktop
2. Open a new conversation
3. IBM MDM tools will be available

### HTTP Mode Only

```bash
python setup_wizard.py --http
```

Use this when you want to:
- Test with MCP Inspector
- Run the server as an HTTP service
- Integrate with custom MCP clients

After setup, start the server:
```bash
# macOS/Linux
.venv/bin/python src/server.py

# Windows
.venv\Scripts\python src\server.py
```

## Platform-Specific Configuration

### IBM MDM SaaS on IBM Cloud

When prompted, you'll need:
- **Base URL**: Your IBM MDM instance URL (default: `https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/`)
- **Auth URL**: IBM Cloud IAM endpoint (default: `https://iam.cloud.ibm.com/identity/token`)
- **API Key**: Your IBM Cloud API key
- **CRN**: Cloud Resource Name for your MDM instance

### IBM MDM on Software Hub

When prompted, you'll need:
- **Base URL**: Your Software Hub instance URL
- **Auth URL**: Software Hub authentication endpoint
- **Username**: Your admin username
- **Password**: Your admin password

## Tool Modes

### Minimal Mode (Default)
Exposes essential tools:
- `search_master_data` - Search for master data (records, entities, relationships, hierarchy nodes)
- `get_data_model` - Retrieve data model schema

### Full Mode
Exposes all available tools:
- `search_master_data` - Search for master data (records, entities, relationships, hierarchy nodes)
- `get_data_model` - Retrieve data model schema
- `get_record` - Get specific record by ID
- `get_entity` - Get entity by ID
- `get_records_entities_by_record_id` - Get entities for a record

## What Gets Created

After running the setup script, you'll have:

1. **`.venv/`** - Python virtual environment with all dependencies
2. **`src/.env`** - Environment configuration file with your credentials
3. **Claude Desktop Config** (if selected) - Updated `claude_desktop_config.json`

## Troubleshooting

Having issues with setup? See our comprehensive troubleshooting guide:

📖 **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Complete solutions for:

**Installation Issues:**
- [Python Version Problems](TROUBLESHOOTING.md#python-version-problems)
- [Package Installation Failures](TROUBLESHOOTING.md#package-installation-failures)
- [Virtual Environment Issues](TROUBLESHOOTING.md#virtual-environment-issues)
- [Dependency Conflicts](TROUBLESHOOTING.md#dependency-conflicts)

**Configuration Issues:**
- [Environment Variables Not Loading](TROUBLESHOOTING.md#environment-variables-not-loading)
- [Invalid Credentials](TROUBLESHOOTING.md#invalid-credentials)
- [Platform Configuration Errors](TROUBLESHOOTING.md#platform-configuration-errors)

**Claude Desktop Integration:**
- [Tools Don't Appear](TROUBLESHOOTING.md#tools-dont-appear-in-claude-desktop)
- [Configuration File Issues](TROUBLESHOOTING.md#configuration-file-issues)

For detailed step-by-step solutions, see the [full troubleshooting documentation](TROUBLESHOOTING.md).

## Manual Configuration

If you prefer manual setup or need to modify the configuration:

1. **Edit `.env` file**:
   ```bash
   nano src/.env
   ```

2. **Edit Claude Desktop config** (if using Claude Desktop):
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

## Verification

After setup, verify your installation:

### For HTTP Mode

```bash
# Start the server
.venv/bin/python src/server.py

# In another terminal, test with curl
curl http://localhost:8000/health
```

### For Claude Desktop

1. Restart Claude Desktop
2. Open a new conversation
3. Look for IBM MDM tools in the tools panel
4. Try a simple query: "Show me the available MDM tools"

## Next Steps

After successful setup:

1. **Read the main README.md** for detailed usage instructions
2. **Check the Usage Examples** section for common scenarios
3. **Review the Architecture documentation** in `docs/ARCHITECTURE.md`
4. **Run the tests** to ensure everything works: `pytest tests/`

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for comprehensive solutions
2. Review the [Claude Desktop Setup Guide](CLAUDE_DESKTOP_SETUP.md) for integration help
3. See the [Manual Installation Guide](MANUAL_INSTALLATION.md) for alternative setup methods
4. Open an issue on [GitHub](https://github.com/IBM/mdm-mcp-server/issues)

## Advanced Usage

### Custom Virtual Environment Location

The setup script creates `.venv` in the project root. To use a different location:

```bash
# Create venv manually
python -m venv /path/to/custom/venv

# Activate it
source /path/to/custom/venv/bin/activate  # macOS/Linux
# or
\path\to\custom\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure manually
cp src/.env.example src/.env
# Edit src/.env with your credentials
```

### Environment Variables Override

You can override environment variables at runtime:

```bash
# Override platform
M360_TARGET_PLATFORM=cloud .venv/bin/python src/server.py

# Override tool mode
MCP_TOOLS_MODE=full .venv/bin/python src/server.py
```

### Multiple Configurations

To maintain multiple configurations:

```bash
# Create environment-specific files
cp src/.env src/.env.production
cp src/.env src/.env.development

# Use specific config
cp src/.env.production src/.env
python src/server.py
```

---

**Made with ❤️ by IBM**