# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)

.PHONY: help install install-dev test test-cov clean build publish publish-test lint format check-format

# Default target
help:
	@echo "IBM MDM MCP Server - Makefile Commands"
	@echo "======================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  make clean            Clean build artifacts"
	@echo "  make build            Build distribution packages"
	@echo "  make publish-test     Publish to TestPyPI"
	@echo "  make publish          Publish to PyPI (production)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linting checks"
	@echo "  make format           Format code with black"
	@echo "  make check-format     Check code formatting"
	@echo ""

# Install production dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build distribution packages
build: clean
	python -m pip install --upgrade build
	python -m build

# Publish to TestPyPI (for testing)
publish-test: build
	python -m pip install --upgrade twine
	python -m twine upload --repository testpypi dist/*
	@echo ""
	@echo "✓ Package uploaded to TestPyPI!"
	@echo ""
	@echo "Test installation (recommended method to avoid TestPyPI dependency issues):"
	@echo "  # Step 1: Install dependencies from PyPI first"
	@echo "  pip install fastmcp fastapi uvicorn pydantic pydantic-settings python-dotenv requests httpx PyJWT urllib3 Authlib"
	@echo ""
	@echo "  # Step 2: Install your package from TestPyPI "
	@echo "  pip install --index-url https://test.pypi.org/simple/ ibm_mdm_mcp_server"
	@echo ""
	

# Publish to PyPI (production)
publish: build
	python -m pip install --upgrade twine
	python -m twine upload dist/*
	@echo ""
	@echo "Package uploaded to PyPI!"
	@echo "Install with:"
	@echo "  pip install ibm_mdm_mcp_server"

# Run linting (if you add linting tools later)
lint:
	@echo "Linting not configured yet. Consider adding flake8 or ruff."

# Format code (if you add formatting tools later)
format:
	@echo "Formatting not configured yet. Consider adding black or ruff."

# Check code formatting
check-format:
	@echo "Format checking not configured yet. Consider adding black or ruff."

# Run the server in HTTP mode
run:
	python src/server.py --mode http

# Run the server in STDIO mode
run-stdio:
	python src/server.py --mode stdio

# Setup development environment
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"