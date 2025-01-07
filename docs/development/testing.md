# Testing Guide

This guide covers testing practices and procedures for Ollama PDF RAG.

## Overview

We use pytest for testing and maintain high test coverage to ensure code quality. Tests are organized by component and include unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── __init__.py
├── test_document.py    # Document processing tests
├── test_models.py      # Model extraction tests
└── test_rag.py        # RAG pipeline tests
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run tests with output
pytest -v

# Run specific test file
pytest tests/test_document.py

# Run specific test function
pytest tests/test_document.py::test_split_documents
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=src

# Generate detailed coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

## Writing Tests

### Test File Structure

```python
"""Test module docstring."""
import pytest
from unittest.mock import Mock, patch

def test_function_name():
    """Test docstring explaining what is being tested."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Using Fixtures

```python
@pytest.fixture
def processor():
    """Create a DocumentProcessor instance."""
    return DocumentProcessor()

def test_with_fixture(processor):
    """Test using the fixture."""
    result = processor.process_document()
    assert result is not None
```

### Mocking

```python
@patch('module.class.method')
def test_with_mock(mock_method):
    """Test using a mock."""
    mock_method.return_value = expected_value
    result = function_that_uses_method()
    assert result == expected_value
```

## Test Categories

### Unit Tests
- Test individual functions/methods
- Mock dependencies
- Fast execution
- High coverage

### Integration Tests
- Test component interactions
- Minimal mocking
- Focus on integration points

### End-to-End Tests
- Test complete workflows
- No mocking
- Slower execution
- Critical path coverage

## Best Practices

1. **Test Organization**
   - One test file per module
   - Clear test names
   - Descriptive docstrings

2. **Test Independence**
   - Tests should not depend on each other
   - Clean up after tests
   - Use fixtures for setup/teardown

3. **Test Coverage**
   - Aim for high coverage
   - Focus on critical paths
   - Test edge cases

4. **Assertions**
   - One assertion per test when possible
   - Clear failure messages
   - Test both positive and negative cases

## Continuous Integration

Tests run automatically on:
- Every push to main
- Pull requests
- Release tags

GitHub Actions configuration:
```yaml
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
```

## Common Issues

### Test Performance
- Use appropriate fixtures
- Mock expensive operations
- Parallelize test execution

### Flaky Tests
- Avoid time-dependent tests
- Use stable test data
- Handle async operations properly

### Coverage Gaps
- Identify uncovered code
- Add missing test cases
- Focus on critical functionality

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/) 