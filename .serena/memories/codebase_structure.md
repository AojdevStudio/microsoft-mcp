# Codebase Structure & Architecture

## Directory Structure
```
microsoft-mcp/
├── src/microsoft_mcp/          # Main package
│   ├── server.py              # MCP server entry point
│   ├── tools.py               # Legacy tool registration (being phased out)
│   ├── auth.py                # MSAL authentication and token management
│   ├── graph.py               # Microsoft Graph API client wrapper
│   ├── email_tool.py          # Email operations (unified)
│   ├── calendar_tool.py       # Calendar operations
│   ├── contact_tool.py        # Contact management
│   ├── file_tool.py           # OneDrive file operations
│   ├── auth_tool.py           # Authentication management
│   ├── email_params.py        # Email parameter models
│   ├── validation.py          # Error formatting and validation utilities
│   └── email_framework/       # Professional email template system
├── tests/                     # Test directory
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
└── .bmad-core/               # BMad Method configuration
```

## Core Modules

### Entry Point (`server.py`)
- Minimal entry point that validates environment
- Checks `MICROSOFT_MCP_CLIENT_ID` environment variable
- Launches MCP server from `tools.py`

### Authentication Layer (`auth.py`)
- Manages MSAL authentication for multiple Microsoft accounts
- Token storage: `~/.microsoft-mcp/tokens.json`
- Functions: token refresh, device flow authentication, account management
- Classes: `Account` dataclass for account representation

### Graph API Client (`graph.py`)
- Wrapper around Microsoft Graph API endpoints
- HTTP request handling, error management, response parsing
- Pagination support for large result sets

### Email Operations (`email_tool.py`)
- Unified email operations with action-based routing
- Actions: list, send, reply, draft, delete, forward, move, mark, search, get
- Professional email template integration
- Attachment handling for both sending and drafts

### Email Framework (`email_framework/`)
- Professional template system with KamDental branding
- CSS-in-Python approach with inline style conversion
- Theme system: Baytown (blue), Humble (green), Executive (dark)
- Email client compatibility layer

## Key Design Patterns

### Action-Based Architecture
- Single tool functions with `action` parameter routing
- Pattern: `tool_name(account_id, action, data, options)`
- Reduces tool proliferation (from 61+ to 5 tools)

### Multi-Account Support
- Every tool requires `account_id` as first parameter
- Accepts: exact home_account_id, email username, or 'default'
- Account resolution with clear error messages

### Error Handling
- Consistent error response format across all tools
- Format: `{status, action, error_type, message, details, timestamp}`
- Specific exceptions with context

### Type Safety (Planned)
- Pydantic parameter models for validation
- Type hints throughout codebase
- Runtime validation for API parameters

## Import Organization
1. Standard library imports
2. Third-party imports (fastmcp, httpx, msal)
3. Local application imports (relative imports within package)

## Testing Structure
- `tests/` mirrors `src/microsoft_mcp/` structure
- Test files: `test_*.py` pattern
- Markers: unit, integration, email_framework, slow, auth, graph_api
- Quarantine directory for problematic tests
- Email framework specific test runner