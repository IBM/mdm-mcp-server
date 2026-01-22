# Testing Guide

This guide covers testing procedures, code quality checks, and continuous integration for the IBM MDM MCP Server.

## Running Tests

The project uses pytest with comprehensive test coverage.

### Basic Test Commands

**Run all tests:**
```bash
pytest tests/
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

**Run with coverage report:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Run specific test file:**
```bash
pytest tests/test_common/test_crn_validation.py -v
```

**Run specific test function:**
```bash
pytest tests/test_common/test_crn_validation.py::test_valid_crn -v
```

### Coverage Reports

**Generate HTML coverage report:**
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Generate XML coverage report (for CI/CD):**
```bash
pytest tests/ --cov=src --cov-report=xml
```

**Generate multiple report formats:**
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_common/                   # Common module tests
│   ├── test_crn_validation.py    # CRN validation tests
│   ├── test_session_store.py     # Session management tests
│   ├── test_token_cache.py       # Token caching tests
│   ├── test_authentication_manager_jwt.py
│   └── test_shared_auth_manager.py
├── test_data_ms/                  # Data microservice tests
│   └── test_search_validators.py # Search validation tests
└── test_model_ms/                 # Model microservice tests
    └── test_model_tools.py        # Model tool tests
```

## Test Categories

Tests are organized by markers for selective execution:

**Unit tests:**
```bash
pytest tests/ -m unit
```

**Integration tests:**
```bash
pytest tests/ -m integration
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test Structure

```python
import pytest
from src.common.domain.crn_validator import CRNValidator

class TestCRNValidator:
    """Test suite for CRN validation."""
    
    def test_valid_crn(self):
        """Test validation of a valid CRN."""
        crn = "crn:v1:bluemix:public:mdm:us-south:a/abc123:instance123::"
        assert CRNValidator.validate(crn) is True
    
    def test_invalid_crn_format(self):
        """Test validation fails for invalid format."""
        crn = "invalid-crn-format"
        assert CRNValidator.validate(crn) is False
    
    @pytest.mark.parametrize("crn,expected", [
        ("crn:v1:bluemix:public:mdm:us-south:a/abc:inst::", True),
        ("crn:invalid:format", False),
        ("", False),
    ])
    def test_crn_validation_parametrized(self, crn, expected):
        """Test CRN validation with multiple inputs."""
        assert CRNValidator.validate(crn) == expected
```

### Using Fixtures

Fixtures are defined in [`conftest.py`](../tests/conftest.py):

```python
import pytest

@pytest.fixture
def sample_config():
    """Provide sample configuration for tests."""
    return {
        "platform": "cloud",
        "base_url": "https://api.example.com",
    }

def test_with_fixture(sample_config):
    """Test using a fixture."""
    assert sample_config["platform"] == "cloud"
```

## Code Quality

### SonarQube Analysis

This project is configured for SonarQube/SonarCloud analysis.

**Generate coverage for SonarQube:**
```bash
pytest tests/ --cov=src --cov-report=xml
```

**Run SonarQube scan:**
```bash
sonar-scanner \
  -Dsonar.host.url=<your-sonar-url> \
  -Dsonar.login=<your-token> \
  -Dsonar.projectKey=ibm-mdm-mcp-server \
  -Dsonar.sources=src \
  -Dsonar.tests=tests \
  -Dsonar.python.coverage.reportPaths=coverage.xml
```

**SonarQube Configuration:**

The project includes a `sonar-project.properties` file (if present) with default settings. Key metrics tracked:
- Code coverage
- Code smells
- Bugs
- Vulnerabilities
- Security hotspots
- Technical debt

### Coverage Configuration

Coverage settings are defined in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Organization

1. **One test file per module**: Mirror the source structure
2. **Group related tests**: Use test classes for logical grouping
3. **Clear test names**: Describe what is being tested
4. **Arrange-Act-Assert**: Structure tests clearly

### Test Data

1. **Use fixtures**: For reusable test data
2. **Parametrize tests**: Test multiple inputs efficiently
3. **Mock external dependencies**: Isolate unit tests
4. **Clean up**: Ensure tests don't leave artifacts

### Coverage Goals

- **Minimum coverage**: 80% overall
- **Critical paths**: 100% coverage for authentication, validation
- **New code**: All new features must include tests
- **Bug fixes**: Add regression tests

## Troubleshooting

Having issues with testing? See our comprehensive troubleshooting guide:

📖 **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Complete solutions for:

**Testing Issues:**
- [Tests Failing](TROUBLESHOOTING.md#tests-failing)
- [Coverage Not Working](TROUBLESHOOTING.md#coverage-not-working)
- [Import Errors in Tests](TROUBLESHOOTING.md#import-errors-in-tests)

**Installation Issues:**
- [Python Version Problems](TROUBLESHOOTING.md#python-version-problems)
- [Package Installation Failures](TROUBLESHOOTING.md#package-installation-failures)
- [Virtual Environment Issues](TROUBLESHOOTING.md#virtual-environment-issues)

For detailed step-by-step solutions, see the [full troubleshooting documentation](TROUBLESHOOTING.md).

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Need Help?** See the main [README](../README.md) or [open an issue](https://github.com/IBM/mdm-mcp-server/issues).