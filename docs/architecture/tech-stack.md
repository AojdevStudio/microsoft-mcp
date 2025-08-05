# Technology Stack

## Overview

The Microsoft MCP (Model Context Protocol) server is built on a modern Python stack optimized for AI integration and Microsoft 365 connectivity.

## Core Technologies

### Runtime & Framework
- **Python 3.11+** - Primary language for MCP implementation
- **FastMCP** - MCP server framework providing the protocol implementation
- **asyncio** - Asynchronous programming for concurrent operations
- **UV** - Modern Python package manager and virtual environment tool

### Microsoft Integration
- **Microsoft Graph API v1.0** - RESTful API for Microsoft 365 services
- **MSAL (Microsoft Authentication Library)** - OAuth 2.0 authentication
- **Device Flow Authentication** - Secure authentication without storing credentials

### Data Validation & Modeling
- **Pydantic 2.x** - Data validation using Python type annotations
  - BaseModel for parameter validation
  - Field validators for custom validation logic
  - Automatic JSON schema generation
  - Performance optimized with Rust-based core

### Testing Framework
- **pytest** - Primary testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking and patching utilities

### Development Tools
- **Black** - Code formatting (line length: 100)
- **Ruff** - Fast Python linter combining multiple tools
- **mypy** - Static type checking
- **pre-commit** - Git hooks for code quality

## Architecture Patterns

### Design Patterns
- **Action-Based Dispatch** - Single tool with action parameter routing
- **Parameter Models** - Type-safe validation for all operations
- **Async/Await** - Non-blocking I/O for API calls
- **Dependency Injection** - Clean separation of concerns

### Data Patterns
- **JSON Token Storage** - Secure token caching at `~/.microsoft-mcp/tokens.json`
- **Pydantic Models** - Structured data validation
- **Type Hints** - Full type coverage for IDE support

## External Dependencies

### Required Services
- **Microsoft 365 Account** - User must have valid Microsoft account
- **Azure App Registration** - Client ID for OAuth authentication
- **Internet Connection** - Required for Graph API access

### API Endpoints
- **Graph API Base**: `https://graph.microsoft.com/v1.0`
- **Auth Endpoint**: `https://login.microsoftonline.com/common`

## Development Environment

### Required Tools
- Python 3.11 or higher
- UV package manager
- Git for version control

### Environment Variables
- `MICROSOFT_MCP_CLIENT_ID` - Azure app client ID (required)

### Project Structure
```
microsoft-mcp/
├── src/
│   └── microsoft_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server entry point
│       ├── tools.py           # Tool definitions
│       ├── auth.py            # Authentication handling
│       ├── graph.py           # Graph API wrapper
│       ├── email_params.py    # Parameter models (new)
│       ├── validation.py      # Validation utilities (new)
│       └── email_framework/   # Email templates
├── tests/
│   ├── test_email_params.py   # Parameter validation tests
│   └── test_email_operations.py
├── pyproject.toml             # Project configuration
└── uv.lock                    # Dependency lock file
```

## Performance Considerations

### Optimization Strategies
- **Pydantic Rust Core** - Fast validation performance
- **Async Operations** - Non-blocking API calls
- **Connection Pooling** - Reuse HTTP connections
- **Token Caching** - Minimize authentication overhead

### Benchmarks
- Parameter validation: <5ms target
- API response time: <2s for typical operations
- Memory footprint: Reduced 96% with consolidation

## Security Considerations

### Authentication
- OAuth 2.0 device flow (no password storage)
- Token refresh handling
- Secure token storage with file permissions

### Input Validation
- All inputs validated through Pydantic
- Email header injection prevention
- Path traversal protection

### API Security
- Rate limiting compliance
- Proper error handling without info leakage
- HTTPS only communication

## Future Considerations

### Potential Additions
- Redis for distributed caching
- Celery for background tasks
- OpenTelemetry for observability
- GraphQL for flexible querying

### Compatibility
- Python 3.11+ required
- Cross-platform (Windows, macOS, Linux)
- MCP protocol version compatibility