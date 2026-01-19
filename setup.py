#!/usr/bin/env python3
# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
IBM MDM MCP Server - Unified Setup Script

This script automates the complete setup process for the IBM MDM MCP Server.
It handles:
- Virtual environment creation
- Dependency installation
- Environment configuration
- Claude Desktop integration (optional)
- HTTP server mode setup

Usage:
    python setup.py                    # Interactive setup
    python setup.py --http             # Setup for HTTP mode only
    python setup.py --claude           # Setup for Claude Desktop integration
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def get_platform_info() -> Tuple[str, str]:
    """Get platform information"""
    system = platform.system()
    if system == "Darwin":
        return "macOS", "macos"
    elif system == "Windows":
        return "Windows", "windows"
    elif system == "Linux":
        return "Linux", "linux"
    else:
        return system, system.lower()


def check_python_version() -> bool:
    """Check if Python version is 3.10 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.10+ required, but {version.major}.{version.minor}.{version.micro} found")
        print_error("This project requires Python 3.10 or higher due to fastmcp dependency")
        print_info("Please install Python 3.10+ from https://www.python.org/downloads/")
        return False


def is_running_in_venv() -> bool:
    """Check if currently running inside a virtual environment"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def get_system_python() -> str:
    """Get the system Python executable (not from venv)"""
    if is_running_in_venv():
        # Return the base Python that was used to create this venv
        return sys.base_prefix + ("/bin/python3" if platform.system() != "Windows" else "\\python.exe")
    return sys.executable


def restart_with_system_python():
    """Restart the script using system Python instead of venv Python"""
    system_python = get_system_python()
    print_warning("Detected running from within virtual environment")
    print_info(f"Restarting with system Python: {system_python}")
    
    # Get the script path and arguments
    script_path = Path(__file__).resolve()
    args = [system_python, str(script_path)] + sys.argv[1:]
    
    # Execute the script with system Python
    try:
        os.execv(system_python, args)
    except Exception as e:
        print_error(f"Failed to restart with system Python: {e}")
        print_info("Please run the script after deactivating the virtual environment:")
        print_info("  1. Run: deactivate")
        print_info("  2. Run: python setup.py")
        sys.exit(1)


def create_virtual_environment() -> bool:
    """Create Python virtual environment"""
    print_info("Creating virtual environment...")
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print_warning("Virtual environment already exists")
        
        # Check if we're running from within the venv we want to delete
        if is_running_in_venv():
            current_venv = Path(sys.prefix).resolve()
            target_venv = venv_path.resolve()
            
            if current_venv == target_venv:
                # Automatically restart with system Python
                restart_with_system_python()
                # If we reach here, restart failed
                return False
        
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print_info("Removing existing virtual environment...")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print_error(f"Failed to remove virtual environment: {e}")
                return False
        else:
            print_info("Using existing virtual environment")
            return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_success("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python() -> str:
    """Get path to Python executable in virtual environment"""
    system = platform.system()
    venv_path = Path(".venv")
    
    if system == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        # Try python first, then python3
        python_exe = venv_path / "bin" / "python"
        if not python_exe.exists():
            python_exe = venv_path / "bin" / "python3"
    
    return str(python_exe)


def install_dependencies() -> bool:
    """Install required dependencies"""
    print_info("Installing dependencies...")
    python_path = get_venv_python()
    
    try:
        subprocess.run(
            [python_path, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        subprocess.run(
            [python_path, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def configure_environment() -> Dict[str, str]:
    """Interactive environment configuration"""
    print_header("Environment Configuration")
    
    print("Select your IBM MDM platform:")
    print("1. IBM MDM SaaS on IBM Cloud")
    print("2. IBM MDM on Software Hub (CPD)")
    
    platform_choice = get_user_input("Enter choice (1 or 2)", "1")
    
    env_vars = {}
    
    if platform_choice == "1":
        print_info("\nConfiguring for IBM MDM SaaS on IBM Cloud...")
        env_vars["M360_TARGET_PLATFORM"] = "cloud"
        env_vars["API_CLOUD_BASE_URL"] = get_user_input(
            "Enter MDM Base URL",
            "https://api.ca-tor.dai.cloud.ibm.com/mdm/v1/"
        )
        env_vars["API_CLOUD_AUTH_URL"] = get_user_input(
            "Enter Auth URL",
            "https://iam.cloud.ibm.com/identity/token"
        )
        env_vars["API_CLOUD_API_KEY"] = get_user_input("Enter API Key")
        env_vars["API_CLOUD_CRN"] = get_user_input("Enter Instance CRN")
    else:
        print_info("\nConfiguring for IBM MDM on Software Hub...")
        env_vars["M360_TARGET_PLATFORM"] = "cpd"
        env_vars["API_CPD_BASE_URL"] = get_user_input("Enter CPD Base URL")
        env_vars["API_CPD_AUTH_URL"] = get_user_input("Enter CPD Auth URL")
        env_vars["API_USERNAME"] = get_user_input("Enter Username")
        env_vars["API_PASSWORD"] = get_user_input("Enter Password")
    
    # Tool mode configuration
    print("\nSelect tool mode:")
    print("1. Minimal (search_master_data, get_data_model)")
    print("2. Full (all tools including record/entity retrieval)")
    
    mode_choice = get_user_input("Enter choice (1 or 2)", "1")
    env_vars["MCP_TOOLS_MODE"] = "minimal" if mode_choice == "1" else "full"
    
    return env_vars


def write_env_file(env_vars: Dict[str, str]) -> bool:
    """Write environment variables to .env file"""
    print_info("Creating .env file...")
    env_path = Path("src") / ".env"
    
    try:
        with open(env_path, "w") as f:
            f.write("# IBM MDM MCP Server Configuration\n")
            f.write("# Generated by setup.py\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print_success(f".env file created at {env_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False


def get_claude_config_path() -> Optional[Path]:
    """Get Claude Desktop configuration file path"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        return None
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        return None


def configure_claude_desktop(env_vars: Dict[str, str]) -> bool:
    """Configure Claude Desktop integration"""
    print_header("Claude Desktop Configuration")
    
    config_path = get_claude_config_path()
    if not config_path:
        print_error("Could not determine Claude Desktop config path for this platform")
        return False
    
    print_info(f"Claude Desktop config: {config_path}")
    
    if not config_path.parent.exists():
        print_warning("Claude Desktop config directory not found")
        print_info("Please install Claude Desktop first: https://claude.ai/download")
        return False
    
    # Get absolute paths - ensure they exist
    project_root = Path.cwd().resolve()
    
    print_header("Building Claude Desktop Configuration")
    print_info(f"Project root: {project_root}")
    
    # Build venv Python path - use explicit string concatenation to avoid any Path issues
    if platform.system() == "Windows":
        venv_python_str = str(project_root) + "\\.venv\\Scripts\\python.exe"
    else:
        venv_python_str = str(project_root) + "/.venv/bin/python"
    
    print_info(f"Venv Python path: {venv_python_str}")
    
    # Verify Python executable exists
    if not Path(venv_python_str).exists():
        print_error(f"Python executable not found at: {venv_python_str}")
        print_info(f"Please ensure virtual environment is created")
        return False
    
    # Build server.py path
    server_path_str = str(project_root) + "/src/server.py"
    print_info(f"Server path: {server_path_str}")
    
    # Verify server.py exists
    if not Path(server_path_str).exists():
        print_error(f"server.py not found at: {server_path_str}")
        return False
    
    print_success(f"✓ Venv Python: {venv_python_str}")
    print_success(f"✓ Server script: {server_path_str}")
    
    # Create MCP server configuration - use the explicit string paths
    mcp_config = {
        "command": venv_python_str,
        "args": [server_path_str, "--mode", "stdio"],
        "env": env_vars
    }
    
    print_info("MCP Configuration:")
    print_info(f"  command: {mcp_config['command']}")
    print_info(f"  args: {mcp_config['args']}")
    
    # Read existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print_warning("Invalid JSON in existing config, creating new config")
            config = {}
    else:
        config = {}
    
    # Initialize mcpServers if not present
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check for existing IBM MDM/Match360 configurations and remove them
    servers_to_remove = []
    for server_name in config["mcpServers"].keys():
        # Check for ibm-mdm, match-360, m360, or similar variations
        server_lower = server_name.lower()
        if any(pattern in server_lower for pattern in [
            "ibm-mdm", "match-360", "match360", "ibm-match-360",
            "m360", "m360-mcp", "mdm-mcp"
        ]):
            servers_to_remove.append(server_name)
    
    # Remove all old configurations
    for server_name in servers_to_remove:
        print_info(f"Removing old configuration: {server_name}")
        del config["mcpServers"][server_name]
    
    # Add new ibm-mdm configuration
    print_info("Adding ibm-mdm configuration")
    config["mcpServers"]["ibm-mdm"] = mcp_config
    
    # Write configuration
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print_success("Claude Desktop configuration updated")
        print_warning("Please restart Claude Desktop to load the new configuration")
        return True
    except Exception as e:
        print_error(f"Failed to update Claude Desktop config: {e}")
        return False


def print_http_instructions(env_vars: Dict[str, str]):
    """Print instructions for HTTP mode"""
    print_header("HTTP Mode Setup Complete")
    
    python_path = get_venv_python()
    
    print("To start the MCP server in HTTP mode:\n")
    
    system = platform.system()
    if system == "Windows":
        print(f"  {python_path} src\\server.py --mode http --port 8000")
    else:
        print(f"  {python_path} src/server.py --mode http --port 8000")
    
    print("\nOr simply:")
    if system == "Windows":
        print(f"  {python_path} src\\server.py")
    else:
        print(f"  {python_path} src/server.py")
    
    print("\nThe server will be available at: http://localhost:8000")
    print("\nYou can test it with MCP Inspector:")
    print("  npx @modelcontextprotocol/inspector http://localhost:8000")


def print_claude_instructions():
    """Print instructions for Claude Desktop"""
    print_header("Claude Desktop Setup Complete")
    
    print("Next steps:")
    print("1. Restart Claude Desktop")
    print("2. Open a new conversation")
    print("3. Look for the IBM MDM tools in the tools panel")
    print("\nAvailable tools will appear based on your MCP_TOOLS_MODE setting")


def main():
    """Main setup function"""
    print_header("IBM MDM MCP Server - Setup Wizard")
    
    # Parse command line arguments
    args = sys.argv[1:]
    http_only = "--http" in args
    claude_only = "--claude" in args
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Get platform info
    platform_name, _ = get_platform_info()
    print_info(f"Platform: {platform_name}")
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check if .env already exists (idempotency)
    env_path = Path("src") / ".env"
    if env_path.exists():
        print_warning(".env file already exists")
        response = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if response == 'y':
            env_vars = configure_environment()
            if not write_env_file(env_vars):
                sys.exit(1)
        else:
            print_info("Using existing .env configuration")
            # Load existing env vars for Claude Desktop config
            env_vars = {}
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key] = value
            except Exception as e:
                print_error(f"Failed to read existing .env: {e}")
                sys.exit(1)
    else:
        # Configure environment
        env_vars = configure_environment()
        
        # Write .env file
        if not write_env_file(env_vars):
            sys.exit(1)
    
    # Setup mode selection
    if not http_only and not claude_only:
        print_header("Setup Mode")
        print("What would you like to set up?")
        print("1. Claude Desktop integration (STDIO mode)")
        print("2. HTTP mode (for MCP Inspector or custom clients)")
        
        mode_choice = get_user_input("Enter choice (1 or 2)", "1")
        
        if mode_choice == "1":
            claude_only = True
        elif mode_choice == "2":
            http_only = True
    
    # Configure based on mode
    if claude_only:
        if configure_claude_desktop(env_vars):
            print_claude_instructions()
    elif http_only:
        print_http_instructions(env_vars)
    
    # Final success message
    print_header("Setup Complete!")
    print_success("IBM MDM MCP Server is ready to use")
    
    print("\nConfiguration summary:")
    print(f"  Platform: {env_vars.get('M360_TARGET_PLATFORM', 'N/A')}")
    print(f"  Tool Mode: {env_vars.get('MCP_TOOLS_MODE', 'N/A')}")
    print(f"  Config file: src/.env")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        sys.exit(1)