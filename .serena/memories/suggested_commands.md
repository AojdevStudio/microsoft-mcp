# Suggested Development Commands

## Environment Setup
```bash
# Install dependencies
uv sync

# Set required environment variable
export MICROSOFT_MCP_CLIENT_ID="your-azure-app-id"

# Run authentication script
uv run scripts/authenticate.py
```

## Running the Server
```bash
# Run MCP server
uv run microsoft-mcp

# Or directly via Python module
uv run python -m microsoft_mcp.server
```

## Testing Commands
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_email_params.py

# Run tests with coverage
uv run pytest --cov=microsoft_mcp

# Run email framework tests specifically
uv run pytest tests/email-framework/

# Test email framework (generates sample emails)
uv run python -m microsoft_mcp.email_framework.test_runner
```

## Code Quality Commands
```bash
# Format code with Ruff
uvx ruff format .

# Lint and fix issues
uvx ruff check --fix --unsafe-fixes .

# Type checking (if mypy available)
uv run mypy src/microsoft_mcp

# Run all quality checks
uvx ruff check . && uvx ruff format --check .
```

## Development Utilities
```bash
# Validate nuclear integration
uv run scripts/validate_nuclear_integration.py

# Run comprehensive test suite
uv run scripts/run_tests.py
```

## Git Commands (Darwin/macOS)
```bash
# Standard git operations
git status
git add .
git commit -m "message"
git push

# View changes
git diff
git log --oneline

# Branch management
git checkout -b feature-branch
git merge main
```

## System Commands (Darwin/macOS)
```bash
# File operations
ls -la          # List files with details
find . -name "*.py"  # Find Python files
grep -r "pattern" .  # Search in files

# Process management
ps aux | grep python
kill -9 <pid>

# Directory navigation
pwd             # Print working directory
cd /path        # Change directory
```

## When Task is Completed
1. Run tests: `uv run pytest`
2. Run linting: `uvx ruff check --fix .`
3. Format code: `uvx ruff format .`
4. Type check (if available): `uv run mypy src/microsoft_mcp`
5. Verify server starts: `uv run microsoft-mcp --help`