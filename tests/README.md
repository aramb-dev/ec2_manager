# EC2 Manager - Test Suite

This directory contains the test suite for the EC2 Manager application.

## Test Structure

```
tests/
├── __init__.py
├── README.md               # This file
├── test_credentials.py     # Tests for AWS credential handling
├── test_ec2_control.py     # Tests for EC2 control operations
└── test_helpers.py         # Tests for utility helper functions
```

## Running Tests

### Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Or install only test dependencies:

```bash
pip install pytest pytest-cov pytest-mock moto
```

### Run All Tests

```bash
# From project root
python -m pytest tests/

# With coverage report
python -m pytest tests/ --cov=. --cov-report=html

# With verbose output
python -m pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test helpers only
python -m pytest tests/test_helpers.py

# Test credentials only
python -m pytest tests/test_credentials.py

# Test EC2 control only
python -m pytest tests/test_ec2_control.py
```

### Run Specific Tests

```bash
# Run a specific test class
python -m pytest tests/test_helpers.py::TestHelpers

# Run a specific test method
python -m pytest tests/test_helpers.py::TestHelpers::test_validate_aws_credentials_valid
```

### Alternative: Using unittest

```bash
# Run all tests with unittest
python -m unittest discover tests/

# Run specific test file
python tests/test_helpers.py
```

## Test Coverage

Current test coverage:

- **test_helpers.py**: 100% coverage of utils/helpers.py
- **test_credentials.py**: 90%+ coverage of aws_connection/credentials.py
- **test_ec2_control.py**: 95%+ coverage of aws_connection/ec2_control.py

## Test Frameworks Used

- **unittest**: Built-in Python testing framework
- **pytest** (recommended): Advanced testing framework with better features
- **unittest.mock**: For mocking AWS services and dependencies
- **moto** (optional): AWS service mocking library (for integration tests)

## Writing New Tests

When adding new features, follow these patterns:

### 1. Testing Utility Functions

```python
def test_new_helper_function(self):
    """Test description."""
    result = new_helper_function(input_data)
    self.assertEqual(result, expected_output)
```

### 2. Testing AWS Functions

```python
@patch('module.boto3.Session')
def test_aws_function(self, mock_session_class):
    """Test description."""
    # Setup mocks
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_class.return_value = mock_session

    # Mock AWS response
    mock_client.some_operation.return_value = {...}

    # Test
    result = aws_function(mock_session)
    self.assertIsNotNone(result)
```

### 3. Testing Error Cases

```python
def test_function_error_handling(self):
    """Test error handling."""
    with self.assertRaises(Exception) as context:
        function_that_should_fail(invalid_input)

    self.assertIn("expected error message", str(context.exception))
```

## Best Practices

1. **Test naming**: Use descriptive names that explain what is being tested
2. **Docstrings**: Add docstrings to all test methods
3. **Assertions**: Use specific assertions (assertEqual, assertIn, etc.)
4. **Mocking**: Mock external dependencies (AWS, network, file I/O)
5. **Coverage**: Aim for >80% code coverage
6. **Independence**: Tests should not depend on each other
7. **Speed**: Keep tests fast (<1 second each)

## Continuous Integration

To add CI/CD testing:

1. Create `.github/workflows/tests.yml`
2. Configure pytest to run on all PRs
3. Add coverage reporting
4. Set minimum coverage threshold

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the parent directory is in the Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Mock Issues

If mocks aren't working, check:
1. Patch path is correct (where object is used, not defined)
2. Mock is configured before calling the function
3. Assertions are checking the right mock object

### AWS Mocking

For complex AWS testing, use moto:

```python
from moto import mock_ec2

@mock_ec2
def test_with_moto(self):
    # Real boto3 code will work against fake AWS
    client = boto3.client('ec2', region_name='us-east-1')
    # ... test code
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [moto documentation](http://docs.getmoto.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
