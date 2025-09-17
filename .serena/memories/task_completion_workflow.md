# Task Completion Workflow

## Standard Development Workflow

### Before Starting Development
1. Ensure environment is set up: `uv sync`
2. Verify authentication: `uv run scripts/authenticate.py`
3. Run existing tests to ensure baseline: `uv run pytest`

### During Development
1. Follow coding standards (see coding_standards memory)
2. Write code with type hints and proper documentation
3. Create/update tests for new functionality
4. Test locally as you develop

### Task Completion Checklist

#### 1. Code Quality Validation
- [ ] **Format code**: `uvx ruff format .`
- [ ] **Fix linting issues**: `uvx ruff check --fix --unsafe-fixes .`
- [ ] **Type checking**: `uv run mypy src/microsoft_mcp` (if mypy available)
- [ ] **Code review**: Check for security issues, performance considerations

#### 2. Testing Validation
- [ ] **Run unit tests**: `uv run pytest tests/`
- [ ] **Run integration tests**: `uv run pytest -m integration`
- [ ] **Test coverage**: `uv run pytest --cov=microsoft_mcp`
- [ ] **Email framework tests**: `uv run python -m microsoft_mcp.email_framework.test_runner`
- [ ] **Manual testing**: Verify server starts correctly

#### 3. Functional Validation
- [ ] **Server startup**: `uv run microsoft-mcp --help`
- [ ] **Authentication flow**: Test account authentication if auth-related
- [ ] **API operations**: Test core functionality manually
- [ ] **Error handling**: Verify error cases work correctly

#### 4. Documentation & Git
- [ ] **Update documentation**: README, docstrings, comments as needed
- [ ] **Update CHANGELOG.md**: Add entry for significant changes
- [ ] **Git status**: `git status` to review changes
- [ ] **Commit changes**: `git add . && git commit -m "descriptive message"`

## Special Validation for Different Components

### Email Tool Changes
- Run email framework test runner
- Test sending, receiving, and template functionality
- Verify attachment handling
- Test multi-account functionality

### Authentication Changes
- Test device flow authentication
- Verify token refresh functionality
- Test multi-account scenarios
- Check token storage security

### Graph API Changes
- Test pagination functionality
- Verify error handling for API failures
- Test rate limiting behavior
- Check response parsing

## Performance Considerations
- Parameter validation should complete in <5ms
- API operations should complete in <2s for typical requests
- Memory usage should remain stable
- Token refresh should be automatic and seamless

## Security Validation
- No hardcoded secrets or credentials
- Proper input validation
- Secure token storage
- Error messages don't leak sensitive information
- Environment variables properly configured

## Final Sign-off
After completing all checklist items:
1. All tests pass
2. Code quality checks pass
3. Server starts without errors
4. Core functionality verified
5. Documentation updated
6. Changes committed to git

The task is considered complete when all validation steps pass and the feature works as intended without breaking existing functionality.