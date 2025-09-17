# Technology Stack

## Core Technologies
- **Python 3.12+** - Primary language for MCP implementation
- **FastMCP 2.8.0+** - MCP server framework providing protocol implementation
- **asyncio** - Asynchronous programming for concurrent operations
- **UV** - Modern Python package manager and virtual environment tool

## Microsoft Integration
- **Microsoft Graph API v1.0** - RESTful API for Microsoft 365 services
- **MSAL (Microsoft Authentication Library)** - OAuth 2.0 authentication
- **Device Flow Authentication** - Secure authentication without storing credentials

## Dependencies
### Runtime Dependencies
- `fastmcp>=2.8.0` - MCP protocol implementation
- `httpx>=0.28.1` - HTTP client for API calls
- `msal>=1.32.3` - Microsoft authentication
- `python-dotenv>=1.1.0` - Environment variable management

### Development Dependencies
- `pytest>=8.4.0` - Testing framework
- `pytest-asyncio>=1.0.0` - Async test support
- `pytest-cov>=6.2.1` - Code coverage
- `ruff>=0.1.0` - Fast Python linter and formatter
- `mypy>=1.7.0` - Static type checking

## Architecture Patterns
- **Action-Based Dispatch** - Single tool with action parameter routing
- **Parameter Models** - Type-safe validation for all operations (planned)
- **Async/Await** - Non-blocking I/O for API calls
- **Dependency Injection** - Clean separation of concerns

## API Integration
- **Graph API Base**: `https://graph.microsoft.com/v1.0`
- **Auth Endpoint**: `https://login.microsoftonline.com/common`
- **Token Storage**: `~/.microsoft-mcp/tokens.json` (secure file permissions)

## Performance Characteristics
- Parameter validation: <5ms target
- API response time: <2s for typical operations
- Memory footprint: Reduced 96% with nuclear architecture
- Token caching minimizes authentication overhead