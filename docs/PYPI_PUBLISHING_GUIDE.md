# PyPI Publishing Guide

This guide provides step-by-step instructions for publishing the `ibm_mdm_mcp_server` package to PyPI (Python Package Index).

## Prerequisites

Before publishing to PyPI, ensure you have:

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for authentication:
   - Go to Account Settings → API tokens
   - Create a token with appropriate scope (project-specific or account-wide)
   - Save the token securely (you won't see it again)

3. **Required Tools**: Install build and publishing tools:
   ```bash
   pip install --upgrade build twine
   ```

## Package Configuration

The package is configured in [`pyproject.toml`](../pyproject.toml) with the following key details:

- **Package Name**: `ibm_mdm_mcp_server`
- **Current Version**: `1.0.9`
- **Build System**: setuptools
- **Python Version**: >=3.10

## Publishing Process

### Step 1: Update Version Number

Before publishing, update the version number in [`pyproject.toml`](../pyproject.toml):

```toml
[project]
version = "1.0.10"  # Increment according to semantic versioning
```

**Semantic Versioning Guidelines**:
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (1.X.0): New features, backward compatible
- **PATCH** (1.0.X): Bug fixes, backward compatible

### Step 2: Update CHANGELOG

Document your changes in [`CHANGELOG.md`](../CHANGELOG.md):

```markdown
## [1.0.10] - 2026-01-22

### Added
- New feature description

### Changed
- Modified functionality description

### Fixed
- Bug fix description
```

### Step 3: Clean Previous Builds

Remove any previous build artifacts:

```bash
rm -rf dist/ build/ *.egg-info
```

### Step 4: Build the Package

Build both source distribution and wheel:

```bash
python -m build
```

This creates two files in the `dist/` directory:
- `ibm_mdm_mcp_server-X.Y.Z.tar.gz` (source distribution)
- `ibm_mdm_mcp_server-X.Y.Z-py3-none-any.whl` (wheel)

### Step 5: Test on TestPyPI (Recommended)

Before publishing to production PyPI, test on TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

When prompted, use:
- **Username**: `__token__`
- **Password**: Your TestPyPI API token (including the `pypi-` prefix)

Test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ibm_mdm_mcp_server
```

> **Note**: The `--extra-index-url` flag allows pip to install dependencies from the main PyPI since they may not exist on TestPyPI.

### Step 6: Publish to PyPI

Once testing is successful, publish to production PyPI:

```bash
python -m twine upload dist/*
```

When prompted, use:
- **Username**: `__token__`
- **Password**: Your PyPI API token (including the `pypi-` prefix)

### Step 7: Verify Publication

1. Check the package page: https://pypi.org/project/ibm-mdm-mcp-server/
2. Test installation:
   ```bash
   pip install ibm_mdm_mcp_server
   ```

### Step 8: Tag the Release

Create a git tag for the release:

```bash
git tag -a v1.0.10 -m "Release version 1.0.10"
git push origin v1.0.10
```

## Using API Tokens with .pypirc

To avoid entering credentials each time, configure `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

Set appropriate permissions:

```bash
chmod 600 ~/.pypirc
```

## Automated Publishing with Makefile

The project includes a [`Makefile`](../Makefile) for common tasks. You can add publishing targets:

```makefile
.PHONY: build
build:
	rm -rf dist/ build/ *.egg-info
	python -m build

.PHONY: publish-test
publish-test: build
	python -m twine upload --repository testpypi dist/*

.PHONY: publish
publish: build
	python -m twine upload dist/*
```

Usage:

```bash
make build          # Build the package
make publish-test   # Publish to TestPyPI
make publish        # Publish to PyPI
```

## Troubleshooting

Having issues with PyPI publishing? Common issues include:

**Quick Fixes:**
- **Version Already Exists:** Increment version number in `pyproject.toml`
- **Authentication Failed:** Verify API token is correct and has proper permissions
- **Invalid Package Structure:** Ensure `pyproject.toml` is properly configured
- **Missing Dependencies:** Install required tools: `pip install --upgrade build twine`

**Validation Before Publishing:**
```bash
python -m twine check dist/*
```

📖 For comprehensive troubleshooting including installation, configuration, and runtime issues, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Best Practices

1. **Always test on TestPyPI first** before publishing to production
2. **Use semantic versioning** for version numbers
3. **Update CHANGELOG.md** with every release
4. **Tag releases in git** for version tracking
5. **Keep API tokens secure** and never commit them to version control
6. **Test installation** after publishing to ensure everything works
7. **Review package metadata** on PyPI after publishing

## Security Considerations

- **Never commit API tokens** to version control
- **Use project-scoped tokens** when possible (limits damage if compromised)
- **Rotate tokens periodically** for enhanced security
- **Set proper permissions** on `.pypirc` file (chmod 600)
- **Use 2FA** on your PyPI account for additional security

## Additional Resources

- [PyPI Official Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [TestPyPI](https://test.pypi.org/)

## Support

For issues related to this package:
- **GitHub Issues**: https://github.com/IBM/mdm-mcp-server/issues
- **Documentation**: https://github.com/IBM/mdm-mcp-server/blob/main/README.md

---

**Last Updated**: 2026-01-22  
**Package Version**: 1.0.9