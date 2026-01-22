# Troubleshooting Guide

This comprehensive guide covers common issues and solutions for the IBM MDM MCP Server across installation, configuration, Claude Desktop integration, and runtime operations.

## Table of Contents

- [Installation Issues](#installation-issues)
  - [Python Version Problems](#python-version-problems)
  - [Package Installation Failures](#package-installation-failures)
  - [Virtual Environment Issues](#virtual-environment-issues)
  - [Dependency Conflicts](#dependency-conflicts)
- [Configuration Issues](#configuration-issues)
  - [Environment Variables Not Loading](#environment-variables-not-loading)
  - [Invalid Credentials](#invalid-credentials)
  - [Platform Configuration Errors](#platform-configuration-errors)
- [Claude Desktop Integration](#claude-desktop-integration)
  - [Tools Don't Appear](#tools-dont-appear-in-claude-desktop)
  - [Server Connection Failures](#server-connection-failures)
  - [Configuration File Issues](#configuration-file-issues)
  - [Path Problems](#path-problems)
- [Server Runtime Issues](#server-runtime-issues)
  - [Server Won't Start](#server-wont-start)
  - [Port Already in Use](#port-already-in-use)
  - [Server Crashes](#server-crashes)
  - [Performance Issues](#performance-issues)
- [Authentication Issues](#authentication-issues)
  - [IBM Cloud Authentication](#ibm-cloud-authentication-errors)
  - [Software Hub Authentication](#software-hub-authentication-errors)
  - [Token Expiration](#token-expiration-issues)
- [Network Issues](#network-issues)
  - [Connection Timeouts](#connection-timeouts)
  - [Firewall Blocking](#firewall-blocking)
  - [VPN Requirements](#vpn-requirements)
- [HTTP Mode Issues](#http-mode-issues)
  - [mcp-remote Problems](#mcp-remote-problems)
  - [CORS Errors](#cors-errors)
  - [Remote Server Access](#remote-server-access)
- [uvx Issues](#uvx-issues)
  - [uvx Command Not Found](#uvx-command-not-found)
  - [Package Download Failures](#package-download-failures)
  - [Cache Issues](#cache-issues)
- [Testing Issues](#testing-issues)
  - [Tests Failing](#tests-failing)
  - [Coverage Not Working](#coverage-not-working)
  - [Import Errors in Tests](#import-errors-in-tests)
- [Getting Help](#getting-help)

---

## Installation Issues

### Python Version Problems

**Issue:** Server requires Python 3.10+ but you have an older version

**Symptoms:**
- Error: "Python 3.10 or higher is required"
- Syntax errors when running the server
- Import errors for modern Python features

**Solutions:**

1. **Check your Python version:**
   ```bash
   python --version
   python3 --version
   ```

2. **Install Python 3.10 or higher:**
   - **macOS (using Homebrew):**
     ```bash
     brew install python@3.10
     ```
   - **Ubuntu/Debian:**
     ```bash
     sudo apt update
     sudo apt install python3.10 python3.10-venv
     ```
   - **Windows:** Download from [python.org](https://www.python.org/downloads/)

3. **Use the correct Python version:**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

### Package Installation Failures

**Issue:** `pip install ibm-mdm-mcp-server` fails

**Symptoms:**
- Network errors during download
- Permission denied errors
- Package not found errors

**Solutions:**

1. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Use a different index:**
   ```bash
   pip install --index-url https://pypi.org/simple/ ibm-mdm-mcp-server
   ```

3. **Install with user flag (permission issues):**
   ```bash
   pip install --user ibm-mdm-mcp-server
   ```

4. **Check network connectivity:**
   ```bash
   ping pypi.org
   ```

5. **Use a proxy if behind corporate firewall:**
   ```bash
   pip install --proxy http://proxy.company.com:8080 ibm-mdm-mcp-server
   ```

### Virtual Environment Issues

**Issue:** Virtual environment not activating or not working correctly

**Symptoms:**
- Command not found after activation
- Wrong Python version in venv
- Packages not found after installation

**Solutions:**

1. **Recreate the virtual environment:**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Verify activation:**
   ```bash
   which python  # macOS/Linux - should show .venv path
   where python  # Windows - should show .venv path
   ```

3. **Check venv Python version:**
   ```bash
   python --version
   ```

### Dependency Conflicts

**Issue:** Conflicting package versions

**Symptoms:**
- Import errors
- Version mismatch warnings
- Unexpected behavior

**Solutions:**

1. **Install in a clean environment:**
   ```bash
   python3 -m venv fresh_venv
   source fresh_venv/bin/activate
   pip install ibm-mdm-mcp-server
   ```

2. **Check for conflicts:**
   ```bash
   pip check
   ```

3. **Review installed packages:**
   ```bash
   pip list
   ```

---

## Configuration Issues

### Environment Variables Not Loading

**Issue:** Server doesn't recognize environment variables

**Symptoms:**
- "Missing required configuration" errors
- Authentication failures despite correct credentials
- Server uses default values

**Solutions:**

1. **Verify .env file location:**
   - Should be in `src/.env` or working directory
   - Check file name (not `.env.txt` or `.env.example`)

2. **Check .env file format:**
   ```env
   # Correct format (no spaces around =)
   API_CLOUD_API_KEY=your_key_here
   
   # Incorrect format
   API_CLOUD_API_KEY = your_key_here
   ```

3. **Verify environment variables are set:**
   ```bash
   # macOS/Linux
   echo $API_CLOUD_API_KEY
   
   # Windows
   echo %API_CLOUD_API_KEY%
   ```

4. **Export variables manually:**
   ```bash
   export API_CLOUD_API_KEY="your_key_here"
   ```

### Invalid Credentials

**Issue:** Credentials are rejected

**Symptoms:**
- 401 Unauthorized errors
- Authentication failed messages
- Invalid API key errors

**Solutions:**

1. **Verify credentials format:**
   - API keys should not have extra spaces
   - CRN should be complete and properly formatted
   - Passwords should not contain special characters that need escaping

2. **Test credentials directly:**
   ```bash
   # IBM Cloud
   curl -X POST "https://iam.cloud.ibm.com/identity/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"
   ```

3. **Check credential expiration:**
   - API keys may expire
   - Passwords may need rotation
   - Verify in IBM Cloud/Software Hub console

### Platform Configuration Errors

**Issue:** Wrong platform configuration

**Symptoms:**
- "Platform not supported" errors
- Wrong authentication method used
- API endpoint not found

**Solutions:**

1. **Verify platform setting:**
   ```env
   M360_TARGET_PLATFORM=cloud  # For IBM Cloud
   M360_TARGET_PLATFORM=cpd    # For Software Hub
   ```

2. **Check required variables for each platform:**
   
   **IBM Cloud requires:**
   - `API_CLOUD_BASE_URL`
   - `API_CLOUD_AUTH_URL`
   - `API_CLOUD_API_KEY`
   - `API_CLOUD_CRN`
   
   **Software Hub requires:**
   - `API_CPD_BASE_URL`
   - `API_CPD_AUTH_URL`
   - `API_USERNAME`
   - `API_PASSWORD`

---

## Claude Desktop Integration

### Tools Don't Appear in Claude Desktop

**Issue:** IBM MDM tools are not visible in Claude Desktop

**Symptoms:**
- No tools listed when asking Claude
- MCP server not showing in settings
- No response when trying to use tools

**Solutions:**

1. **Verify configuration file location:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. **Check JSON syntax:**
   ```bash
   # Validate JSON online or with:
   python -m json.tool claude_desktop_config.json
   ```

3. **Common JSON errors:**
   - Missing commas between objects
   - Trailing commas (not allowed in JSON)
   - Unescaped backslashes in Windows paths
   - Missing quotes around strings

4. **Verify paths are absolute:**
   ```json
   {
     "command": "/Users/yourname/mdm-mcp-server/.venv/bin/python",
     "args": ["/Users/yourname/mdm-mcp-server/src/server.py", "--mode", "stdio"]
   }
   ```

5. **Restart Claude Desktop properly:**
   - Completely quit (not just close window)
   - On macOS: Cmd+Q
   - On Windows: Right-click taskbar icon → Quit
   - Reopen Claude Desktop

6. **Check Claude Desktop logs:**
   - **macOS:** `~/Library/Logs/Claude/mcp*.log`
   - **Windows:** `%APPDATA%\Claude\logs\mcp*.log`
   - Look for error messages related to MCP server

### Server Connection Failures

**Issue:** Claude Desktop can't connect to the server

**Symptoms:**
- "Server not responding" errors
- Tools appear but don't work
- Timeout errors

**Solutions:**

1. **Test server manually:**
   ```bash
   # For PyPI installation
   ibm_mdm_mcp_server --mode stdio
   
   # For source installation
   python src/server.py --mode stdio
   ```

2. **Check server logs:**
   - Look for startup errors
   - Verify authentication succeeds
   - Check for missing dependencies

3. **Verify command in config:**
   ```json
   {
     "command": "ibm_mdm_mcp_server",  // For PyPI
     "command": "/path/to/python",      // For source
     "command": "uvx",                  // For uvx
     "command": "npx"                   // For HTTP mode
   }
   ```

### Configuration File Issues

**Issue:** Configuration file not being read

**Symptoms:**
- Changes don't take effect
- Server uses old configuration
- Default values being used

**Solutions:**

1. **Verify file permissions:**
   ```bash
   # macOS/Linux
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Check for multiple config files:**
   - Ensure only one config file exists
   - Delete backup or old versions

3. **Validate JSON structure:**
   ```json
   {
     "mcpServers": {
       "ibm-mdm": {
         "command": "...",
         "args": [...],
         "env": {...}
       }
     }
   }
   ```

### Path Problems

**Issue:** Paths not resolving correctly

**Symptoms:**
- "File not found" errors
- "Command not found" errors
- Python interpreter not found

**Solutions:**

1. **Use absolute paths:**
   ```bash
   # Find absolute path
   # macOS/Linux
   realpath /path/to/file
   
   # Windows
   cd /d C:\path\to\directory && cd
   ```

2. **Escape Windows paths:**
   ```json
   {
     "command": "C:\\Users\\yourname\\.venv\\Scripts\\python.exe"
   }
   ```

3. **Test paths in terminal:**
   ```bash
   # macOS/Linux
   ls -la /path/to/python
   /path/to/python --version
   
   # Windows
   dir C:\path\to\python.exe
   C:\path\to\python.exe --version
   ```

---

## Server Runtime Issues

### Server Won't Start

**Issue:** Server fails to start or crashes immediately

**Symptoms:**
- Process exits immediately
- Error messages on startup
- No response on configured port

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Must be 3.10+
   ```

2. **Verify installation:**
   ```bash
   # For PyPI
   pip show ibm-mdm-mcp-server
   
   # For source
   pip list | grep fastmcp
   ```

3. **Check for missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Review error messages:**
   - Look for specific module import errors
   - Check for configuration errors
   - Verify all required environment variables are set

5. **Test with minimal config:**
   ```bash
   # Set only required variables
   export M360_TARGET_PLATFORM=cloud
   export API_CLOUD_BASE_URL="https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/"
   # ... other required vars
   ibm_mdm_mcp_server
   ```

### Port Already in Use

**Issue:** Cannot start server because port is occupied

**Symptoms:**
- "Address already in use" error
- "Port 8000 is already allocated"
- Server fails to bind to port

**Solutions:**

1. **Find process using the port:**
   ```bash
   # macOS/Linux
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill the process:**
   ```bash
   # macOS/Linux
   lsof -ti:8000 | xargs kill -9
   
   # Windows (replace <PID> with actual process ID)
   taskkill /PID <PID> /F
   ```

3. **Use a different port:**
   ```bash
   ibm_mdm_mcp_server --port 3000
   ```

### Server Crashes

**Issue:** Server crashes during operation

**Symptoms:**
- Unexpected process termination
- Memory errors
- Segmentation faults

**Solutions:**

1. **Check system resources:**
   ```bash
   # macOS/Linux
   top
   free -h
   
   # Windows
   taskmgr
   ```

2. **Review server logs:**
   - Look for error stack traces
   - Check for memory leaks
   - Identify problematic requests

3. **Update dependencies:**
   ```bash
   pip install --upgrade ibm-mdm-mcp-server
   ```

4. **Increase system limits (if needed):**
   ```bash
   # macOS/Linux
   ulimit -n 4096
   ```

### Performance Issues

**Issue:** Server is slow or unresponsive

**Symptoms:**
- Long response times
- Timeouts
- High CPU/memory usage

**Solutions:**

1. **Check network latency:**
   ```bash
   ping api.ca-tor.dai.cloud.ibm.com
   curl -w "@-" -o /dev/null -s "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/"
   ```

2. **Monitor resource usage:**
   ```bash
   # macOS/Linux
   ps aux | grep python
   
   # Windows
   tasklist | findstr python
   ```

3. **Review token caching:**
   - Tokens should be cached automatically
   - Check if authentication happens on every request

4. **Optimize queries:**
   - Use specific filters
   - Limit result sets
   - Avoid broad searches

---

## Authentication Issues

### IBM Cloud Authentication Errors

**Issue:** Cannot authenticate with IBM Cloud

**Symptoms:**
- 401 Unauthorized
- Invalid API key
- CRN validation failures

**Solutions:**

1. **Verify API key:**
   - Check for extra spaces or newlines
   - Ensure key hasn't expired
   - Generate new key if needed

2. **Validate CRN format:**
   ```
   crn:v1:bluemix:public:mdm:region:a/account:instance::
   ```

3. **Test authentication:**
   ```bash
   curl -X POST "https://iam.cloud.ibm.com/identity/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"
   ```

4. **Check IAM permissions:**
   - Verify user has MDM access
   - Check service ID permissions
   - Review access policies

### Software Hub Authentication Errors

**Issue:** Cannot authenticate with Software Hub

**Symptoms:**
- Login failures
- Invalid credentials
- Session timeouts

**Solutions:**

1. **Verify credentials:**
   - Username is correct
   - Password doesn't contain special characters needing escaping
   - Account is not locked

2. **Test authentication:**
   ```bash
   curl -X POST "https://cpd-instance.com/icp4d-api/v1/authorize" \
     -H "Content-Type: application/json" \
     -d '{"username":"user","password":"pass"}'
   ```

3. **Check user permissions:**
   - Verify MDM access rights
   - Check role assignments
   - Review namespace access

### Token Expiration Issues

**Issue:** Tokens expire during operation

**Symptoms:**
- Intermittent authentication failures
- "Token expired" errors
- Need to restart frequently

**Solutions:**

1. **Token caching is automatic:**
   - Tokens are cached with expiry
   - Automatic refresh before expiry
   - No manual intervention needed

2. **Check token refresh:**
   - Review server logs for refresh attempts
   - Verify refresh happens 5 minutes before expiry

3. **Manual token refresh (if needed):**
   - Restart the server
   - Clear token cache (delete cache files)

---

## Network Issues

### Connection Timeouts

**Issue:** Requests timeout before completing

**Symptoms:**
- "Connection timeout" errors
- Requests take too long
- Intermittent failures

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping api.ca-tor.dai.cloud.ibm.com
   traceroute api.ca-tor.dai.cloud.ibm.com
   ```

2. **Test API endpoint:**
   ```bash
   curl -v https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/
   ```

3. **Increase timeout values:**
   - Configure in environment or code
   - Default timeouts may be too short

4. **Check for rate limiting:**
   - Review API usage
   - Check for throttling
   - Implement backoff strategy

### Firewall Blocking

**Issue:** Firewall blocks connections

**Symptoms:**
- Connection refused
- Cannot reach API endpoints
- Specific ports blocked

**Solutions:**

1. **Check firewall rules:**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # Linux
   sudo iptables -L
   
   # Windows
   netsh advfirewall show allprofiles
   ```

2. **Allow Python through firewall:**
   - Add exception for Python executable
   - Allow outbound HTTPS (port 443)

3. **Configure proxy if needed:**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

### VPN Requirements

**Issue:** VPN required but not connected

**Symptoms:**
- Cannot reach internal servers
- Connection refused to Software Hub
- Network unreachable

**Solutions:**

1. **Verify VPN connection:**
   - Check VPN client status
   - Ensure connected to correct network
   - Test internal DNS resolution

2. **Test connectivity through VPN:**
   ```bash
   ping internal-server.company.com
   nslookup internal-server.company.com
   ```

3. **Configure split tunneling (if needed):**
   - Route only necessary traffic through VPN
   - Keep internet traffic direct

---

## HTTP Mode Issues

### mcp-remote Problems

**Issue:** mcp-remote package not working

**Symptoms:**
- "mcp-remote not found"
- Connection failures
- npx errors

**Solutions:**

1. **Verify npx is installed:**
   ```bash
   npx --version
   ```

2. **Install Node.js if needed:**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version`

3. **Clear npx cache:**
   ```bash
   npx clear-npx-cache
   ```

4. **Install mcp-remote globally:**
   ```bash
   npm install -g mcp-remote
   ```

5. **Use full path to npx:**
   ```json
   {
     "command": "/usr/local/bin/npx"
   }
   ```

### CORS Errors

**Issue:** CORS errors when accessing HTTP server

**Symptoms:**
- "CORS policy" errors in browser
- Cross-origin request blocked
- Preflight request failures

**Solutions:**

1. **CORS is handled by mcp-remote:**
   - No configuration needed
   - mcp-remote handles CORS automatically

2. **For direct HTTP access:**
   - Use MCP Inspector instead
   - Don't access HTTP endpoint directly from browser

### Remote Server Access

**Issue:** Cannot connect to remote HTTP server

**Symptoms:**
- Connection refused
- Timeout errors
- DNS resolution failures

**Solutions:**

1. **Verify server is accessible:**
   ```bash
   curl -v https://your-server.com
   ```

2. **Check authentication headers:**
   ```json
   {
     "args": [
       "mcp-remote@latest",
       "https://your-server.com",
       "--header",
       "Authorization: Bearer ${TOKEN}"
     ]
   }
   ```

3. **Test with curl:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://your-server.com
   ```

---

## uvx Issues

### uvx Command Not Found

**Issue:** uvx command not available

**Symptoms:**
- "command not found: uvx"
- "uvx is not recognized"
- PATH issues

**Solutions:**

1. **Install uv:**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Verify installation:**
   ```bash
   uv --version
   uvx --version
   ```

3. **Add to PATH:**
   ```bash
   # macOS/Linux (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.cargo/bin:$PATH"
   
   # Windows (add to system PATH)
   # C:\Users\YourName\.cargo\bin
   ```

4. **Restart terminal:**
   - Close and reopen terminal
   - Source profile: `source ~/.bashrc`

### Package Download Failures

**Issue:** uvx cannot download package

**Symptoms:**
- Download errors
- Network timeouts
- Package not found

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping pypi.org
   ```

2. **Clear uvx cache:**
   ```bash
   rm -rf ~/.cache/uv
   ```

3. **Use specific version:**
   ```bash
   uvx ibm-mdm-mcp-server@1.0.9
   ```

4. **Configure proxy:**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

### Cache Issues

**Issue:** uvx using old cached version

**Symptoms:**
- Old version running despite updates
- Changes not reflected
- Stale package

**Solutions:**

1. **Clear cache:**
   ```bash
   rm -rf ~/.cache/uv
   ```

2. **Force reinstall:**
   ```bash
   uvx --reinstall ibm-mdm-mcp-server
   ```

3. **Specify version explicitly:**
   ```bash
   uvx ibm-mdm-mcp-server@latest
   ```

---

## Testing Issues

### Tests Failing

**Issue:** pytest tests fail

**Symptoms:**
- Test failures
- Import errors
- Assertion errors

**Solutions:**

1. **Ensure in project root:**
   ```bash
   cd /path/to/mdm-mcp-server
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Install test dependencies:**
   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

4. **Run tests with verbose output:**
   ```bash
   pytest tests/ -v
   ```

5. **Check for missing fixtures:**
   - Review `conftest.py`
   - Verify fixture scope
   - Check fixture dependencies

### Coverage Not Working

**Issue:** Coverage reports not generating

**Symptoms:**
- No coverage output
- Coverage command fails
- Missing coverage data

**Solutions:**

1. **Install coverage tools:**
   ```bash
   pip install pytest-cov coverage
   ```

2. **Run with coverage:**
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing
   ```

3. **Check coverage configuration:**
   - Review `pyproject.toml`
   - Verify source paths
   - Check omit patterns

4. **Generate HTML report:**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   open htmlcov/index.html
   ```

### Import Errors in Tests

**Issue:** Tests cannot import modules

**Symptoms:**
- "ModuleNotFoundError"
- "ImportError"
- "No module named 'src'"

**Solutions:**

1. **Verify project structure:**
   ```
   mdm-mcp-server/
   ├── src/
   │   └── __init__.py
   └── tests/
       └── __init__.py
   ```

2. **Install package in editable mode:**
   ```bash
   pip install -e .
   ```

3. **Check PYTHONPATH:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

4. **Run from project root:**
   ```bash
   cd /path/to/mdm-mcp-server
   pytest tests/
   ```

---

## Getting Help

If you've tried the solutions above and still have issues:

### 1. Check Documentation

- [Setup Guide](SETUP_GUIDE.md) - Installation and configuration
- [Claude Desktop Setup](CLAUDE_DESKTOP_SETUP.md) - Integration guide
- [Running Server Guide](RUNNING_SERVER.md) - Server operations
- [Testing Guide](TESTING.md) - Testing procedures
- [Architecture Guide](ARCHITECTURE.md) - Technical details

### 2. Review Logs

**Claude Desktop logs:**
- macOS: `~/Library/Logs/Claude/mcp*.log`
- Windows: `%APPDATA%\Claude\logs\mcp*.log`

**Server logs:**
- Check terminal output
- Look for stack traces
- Note error messages

### 3. Gather Information

When reporting issues, include:
- Python version: `python --version`
- Package version: `pip show ibm-mdm-mcp-server`
- Operating system and version
- Installation method (PyPI, uvx, source)
- Configuration (sanitized, no credentials)
- Error messages and logs
- Steps to reproduce

### 4. Open an Issue

[GitHub Issues](https://github.com/IBM/mdm-mcp-server/issues)

Provide:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information
- Relevant logs (sanitized)

### 5. Community Resources

- [IBM MDM Documentation](https://www.ibm.com/products/master-data-management)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [FastMCP Framework](https://gofastmcp.com)

---

**Last Updated:** 2026-01-22