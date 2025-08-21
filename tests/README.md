# Testing Strategy for Microsoft MCP Server

This document outlines the comprehensive testing strategy for the Microsoft Graph MCP server, including test organization, execution, and best practices.

## Test Architecture

### Test Pyramid Structure

```
       E2E Tests (5%)
      ─────────────────
    Integration Tests (15%)
   ───────────────────────
   Unit Tests (80%)
```

### Test Categories

#### 1. Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions and classes in isolation  
**Coverage**: 80%+ of test suite  
**Dependencies**: All external dependencies mocked  
**Execution**: Fast (< 1s per test), runs in CI  

**Files**:
- `test_tools.py` - MCP tool functions
- `test_email_framework.py` - Email template and framework components
- `test_auth.py` - Authentication logic (when created)
- `test_graph.py` - Graph API client logic (when created)

#### 2. Integration Tests (`tests/integration/`)
**Purpose**: Test component interactions within the application  
**Coverage**: ~15% of test suite  
**Dependencies**: External APIs mocked, internal integrations tested  
**Execution**: Medium speed (1-5s per test), runs in CI  

**Files**:
- `test_mcp_tools_integration.py` - Tool + auth + graph integration
- `test_email_framework_integration.py` - Email + MCP integration

#### 3. End-to-End Tests (`tests/test_integration_e2e.py`)
**Purpose**: Test complete workflows with real Microsoft Graph API  
**Coverage**: ~5% of test suite  
**Dependencies**: Requires real authentication and Microsoft 365 accounts  
**Execution**: Slow (10-30s per test), **NOT** run in CI by default  

## Running Tests

### Local Development

```bash
# Run all unit tests (fast)
uv run pytest tests/unit/ -v

# Run integration tests (medium speed)
uv run pytest tests/integration/ -v

# Run all tests except E2E
uv run pytest tests/ -v -m "not e2e"

# Run specific test file
uv run pytest tests/unit/test_tools.py -v

# Run with coverage
uv run pytest tests/ --cov=microsoft_mcp --cov-report=html
```

### E2E Testing (Manual)

```bash
# 1. Set environment variable
export RUN_E2E_TESTS=true

# 2. Authenticate first
uv run python authenticate.py

# 3. Run E2E tests
uv run pytest tests/test_integration_e2e.py -v -m e2e
```

### CI/CD Pipeline

```bash
# CI runs this automatically
uv run pytest tests/ -v -m "not e2e" --cov=microsoft_mcp
```

## Test Data and Fixtures

### Global Fixtures (`tests/conftest.py`)
- `mock_account` - Mock Microsoft account data
- `mock_msal_app` - Mock MSAL authentication
- `mock_graph_response` - Mock Graph API responses
- `valid_*_data` - Valid template data for email framework
- `test_data_factory` - Factory for creating test objects

### Using Fixtures

```python
def test_example(mock_account, valid_practice_report_data):
    # Test uses pre-configured mock data
    assert mock_account["username"] == "test.user@kamdental.com"
    assert "location" in valid_practice_report_data
```

## Mocking Strategy

### External Dependencies Always Mocked in Unit/Integration Tests

- **Microsoft Graph API** (`microsoft_mcp.graph`)
- **MSAL Authentication** (`microsoft_mcp.auth`)
- **Network requests** (`httpx`)
- **File system operations**
- **Time-dependent functions**

### Mock Examples

```python
# Mock authentication
@patch('microsoft_mcp.auth.get_token')
def test_with_auth(mock_get_token):
    mock_get_token.return_value = "mock-token-123"
    # Test code here

# Mock Graph API
@patch('microsoft_mcp.graph.request')
def test_with_graph(mock_request):
    mock_request.return_value = {"id": "success"}
    # Test code here

# Using fixtures
def test_with_fixtures(mock_auth_module, mock_graph_module):
    # Fixtures automatically mock the modules
    # Test code here
```

## Email Framework Testing

### Template Testing

```python
def test_practice_report_template(valid_practice_report_data):
    """Test practice report template rendering."""
    with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
        instance = MockTemplate.return_value
        instance.render.return_value = "<html>Report</html>"
        
        result = instance.render(valid_practice_report_data)
        
        assert "<html>" in result
        instance.validate_data.assert_called_once()
```

### Data Validation Testing

```python
def test_template_validation():
    """Test template data validation."""
    # Test with valid data
    valid_data = {"location": "Baytown", "financial_data": {...}}
    assert validate_template_data(valid_data) == True
    
    # Test with invalid data
    invalid_data = {"location": "Baytown"}  # Missing required fields
    assert validate_template_data(invalid_data) == False
```

## Test Markers

Use pytest markers to organize and filter tests:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.e2e
def test_e2e_complete_workflow():
    pass

@pytest.mark.slow
def test_performance_heavy():
    pass

@pytest.mark.email_framework
def test_template_rendering():
    pass
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run integration and unit tests
pytest -m "unit or integration"

# Skip slow tests
pytest -m "not slow"

# Run email framework tests only
pytest -m email_framework
```

## Test Coverage Requirements

### Coverage Targets
- **Overall coverage**: 85%+
- **Core business logic**: 95%+
- **MCP tools**: 90%+
- **Email framework**: 90%+
- **Authentication**: 80%+

### Generating Coverage Reports

```bash
# HTML report
uv run pytest --cov=microsoft_mcp --cov-report=html
open htmlcov/index.html

# Terminal report
uv run pytest --cov=microsoft_mcp --cov-report=term-missing

# Coverage badge
uv run pytest --cov=microsoft_mcp --cov-report=term --cov-fail-under=85
```

## Common Testing Patterns

### Testing MCP Tools

```python
@patch('microsoft_mcp.auth.get_token')
@patch('microsoft_mcp.graph.request')
def test_mcp_tool(mock_request, mock_token):
    # Setup mocks
    mock_token.return_value = "token"
    mock_request.return_value = {"id": "success"}
    
    # Test the tool
    result = some_mcp_tool(account_id="test", param="value")
    
    # Verify behavior
    assert result["status"] == "success"
    mock_token.assert_called_once_with("test")
    mock_request.assert_called_once()
```

### Testing Error Handling

```python
def test_error_handling():
    with patch('microsoft_mcp.graph.request') as mock_request:
        mock_request.side_effect = httpx.HTTPStatusError("403 Forbidden", ...)
        
        with pytest.raises(httpx.HTTPStatusError):
            some_function_that_calls_graph()
```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Best Practices

### Test Naming
- Use descriptive names: `test_should_send_email_when_valid_data_provided`
- Follow pattern: `test_[what]_[when]_[condition]`
- Group related tests in classes: `TestEmailSending`

### Test Structure (AAA Pattern)
```python
def test_function():
    # Arrange - Set up test data and mocks
    data = {"test": "data"}
    mock_function.return_value = "expected"
    
    # Act - Execute the function under test
    result = function_under_test(data)
    
    # Assert - Verify the results
    assert result == "expected"
    mock_function.assert_called_once_with(data)
```

### Mock Guidelines
- Mock at the boundary (external APIs, not internal functions)
- Use specific return values, not generic ones
- Verify mock calls when important
- Reset mocks between tests (handled by pytest automatically)

### Data Guidelines
- Use realistic test data
- Create data factories for complex objects
- Use fixtures for reusable data
- Keep test data minimal but valid

## Troubleshooting

### Common Issues

**"No accounts found" in tests**  
→ Tests are trying to use real authentication. Use mocks instead.

**"Missing required field" in email templates**  
→ Check template data has all required fields. See `conftest.py` fixtures.

**"Module not found" errors**  
→ Ensure imports are correctly mocked or paths are correct.

**Slow test execution**  
→ Check for unmocked network calls or file I/O operations.

### Debug Mode

```bash
# Run with verbose output
pytest -v -s

# Run single test with debugging
pytest tests/unit/test_tools.py::test_specific_function -v -s

# Run with pdb debugger
pytest --pdb
```

## Migration Guide

### From Old Integration Tests

Old tests in `tests/test_integration.py` have been moved:

- **Unit-testable logic** → `tests/unit/test_tools.py`
- **Component integration** → `tests/integration/test_mcp_tools_integration.py`
- **E2E workflows** → `tests/test_integration_e2e.py`

### Updating Existing Tests

1. **Add proper mocking** for external dependencies
2. **Use fixtures** from `conftest.py` for test data
3. **Add appropriate markers** (`@pytest.mark.unit`, etc.)
4. **Follow AAA pattern** for test structure
5. **Verify assertions** are specific and meaningful

## Continuous Improvement

### Regular Tasks
- Review test coverage reports monthly
- Update test data to match real-world scenarios
- Refactor slow or flaky tests
- Add tests for new features immediately
- Remove obsolete tests when code changes

### Metrics to Track
- Test execution time
- Test coverage percentage
- Number of flaky tests
- CI/CD pipeline success rate
- Time to fix failing tests
