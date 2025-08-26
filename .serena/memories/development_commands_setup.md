# Development Commands & Setup

## Environment Setup
```bash
# Install dependencies
uv sync

# Set required environment variable
export MICROSOFT_MCP_CLIENT_ID="your-azure-app-id"

# Run authentication script
uv run authenticate.py
```

## Running the Server
```bash
# Run MCP server
uv run microsoft-mcp

# Or directly via Python
uv run python -m microsoft_mcp.server
```

## Testing Commands
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_create_calendar_event.py

# Run email framework tests
uv run pytest tests/email_framework/

# Run with coverage
uv run pytest --cov=microsoft_mcp

# Run email framework test runner (generates sample emails)
uv run python -m microsoft_mcp.email_framework.test_runner
```

## File Management Guidelines
- Archive old/deprecated files in `.old-files/` directory
- DO NOT delete files - user/stakeholder handles deletions
- Follow DRY principles to avoid code duplication
- Maintain separation of concerns between API and business logic

## Development Standards
- All new tools must support multi-account via `account_id` parameter
- Follow consistent `account_id` + `action` parameter pattern
- Email templates are utilities, not separate tools
- Use unified error handling across all tools