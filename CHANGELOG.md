<!--
This file has been modified with the assistance of IBM Bob (AI Code Assistant)
-->

# Changelog

All notable changes to the IBM MDM MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive sample queries documentation (SAMPLES.md) with report templates and usage patterns
- Security best practices section in README for API key management
- Dashboard and visualization templates for data analysis
- Client-agnostic documentation (works with any MCP-compatible client)

### Changed
- Updated documentation to use generic placeholders instead of assuming specific entity types
- Reorganized sample queries with report templates positioned near usage patterns
- Enhanced common usage patterns with concrete, actionable examples

## [1.0.0] - 2026-01-16

### Added
- Initial public release of IBM MDM MCP Server
- Model Context Protocol (MCP) server implementation for IBM Master Data Management
- Support for IBM MDM SaaS on IBM Cloud platform
- Support for IBM MDM on Software Hub (CPD) platform
- Token-based authentication with automatic caching
- Session management with configurable session stores
- CRN (Cloud Resource Name) validation for IBM Cloud instances

#### Core Features
- **Search Functionality**: Advanced record search with flexible query parameters
- **Data Model Access**: Retrieve complete MDM data model schemas
- **Record Operations**: Get specific records by ID (full mode)
- **Entity Operations**: Retrieve entities and their associations (full mode)

#### Architecture
- Clean 3-tier layered architecture inspired by hexagonal principles
- Adapter pattern for platform-specific API implementations
- Base service and adapter classes for consistent patterns
- Pydantic models for type-safe data validation
- Comprehensive error handling and logging

#### Tools & Modes
- **Minimal Mode**: Essential tools (`search_master_data`, `get_data_model`)
- **Full Mode**: All tools including record/entity retrieval operations
- **HTTP Mode**: Server mode for testing and development
- **STDIO Mode**: Integration mode for Claude Desktop and MCP clients

#### Configuration & Setup
- Automated setup wizard (`setup.py`) for easy installation
- Virtual environment management
- Interactive configuration for both IBM Cloud and Software Hub platforms
- Claude Desktop integration with automatic config generation
- Environment-based configuration with `.env` file support

#### Testing
- Comprehensive test suite using pytest
- Unit tests for authentication, session management, and validation
- Test coverage reporting with pytest-cov
- SonarQube/SonarCloud integration for code quality analysis

#### Documentation
- Detailed README with quick start guide
- Architecture documentation (ARCHITECTURE.md)
- Setup guide (SETUP_GUIDE.md)
- API documentation and usage examples
- Troubleshooting guide

#### Security
- Secure token caching mechanism
- Environment-based credential management
- Input validation and sanitization
- CRN format validation for IBM Cloud

#### Dependencies
- Python 3.10+ requirement
- FastMCP framework for MCP server implementation
- Pydantic for data validation
- httpx for HTTP client operations
- python-dotenv for environment configuration
- PyJWT for JWT token handling

---

## Release Notes

### Version 1.0.0 (2026-01-16)

This is the initial release of the IBM MDM MCP Server, providing AI assistants with seamless access to IBM Master Data Management services through the Model Context Protocol.

**Key Highlights:**
- 🔌 Full MCP protocol support for AI assistant integration
- 🌐 Multi-platform compatibility (IBM Cloud & Software Hub)
- 🔐 Secure authentication with token caching
- 🛠️ Flexible tool modes (minimal/full)
- 📊 Type-safe implementation with Pydantic
- 🏗️ Clean, maintainable architecture
- 🚀 One-command automated setup

**Getting Started:**
```bash
git clone https://github.com/IBM/mdm-mcp-server.git
cd mdm-mcp-server
python setup.py
```

**Supported Platforms:**
- IBM MDM SaaS on IBM Cloud
- IBM MDM on Software Hub (CPD)

**Integration:**
- Claude Desktop (STDIO mode)
- MCP Inspector (HTTP mode)
- Custom MCP clients

For detailed installation and usage instructions, see the [README](README.md).

---

## Contributing

When contributing to this project, please update this CHANGELOG.md file with your changes under the `[Unreleased]` section following these categories:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

---

## Links

- [Repository](https://github.com/IBM/mdm-mcp-server)
- [Issues](https://github.com/IBM/mdm-mcp-server/issues)
- [Documentation](docs/)
- [License](LICENSE)