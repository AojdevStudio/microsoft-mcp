# Microsoft MCP Server - AI Development Protocol

## Project Context

This project is a **Microsoft Graph API integration server** that provides AI assistants with comprehensive access to Microsoft 365 services through the Model Context Protocol (MCP). It enables natural language automation of email, calendar, file management, and contact operations across multiple Microsoft accounts.

**Primary Goal**: Create a robust, secure bridge between AI systems and Microsoft's ecosystem, enabling intelligent productivity automation through conversational interfaces.

## Core Meta-Cognitive Protocols

### Project Understanding Protocol
```yaml
understand_project:
  purpose: "Microsoft Graph API server for AI assistant integration"
  key_capabilities:
    - "Email management (read, send, organize)"
    - "Calendar operations (events, availability)"
    - "File operations (OneDrive integration)"
    - "Contact management"
    - "Unified cross-service search"
  architecture:
    - "MCP server using FastMCP framework"
    - "MSAL authentication with device flow"
    - "Service layer pattern for Graph API"
    - "Tool-based command exposure"
```

### Problem Analysis Protocol
```yaml
when_analyzing_issues:
  first_check:
    - "Authentication state and token validity"
    - "Microsoft Graph API permissions/scopes"
    - "Account selection (multi-account scenarios)"
  common_patterns:
    - "Rate limiting (429 responses) - check retry logic"
    - "Token expiration - verify refresh mechanism"
    - "Permission errors - validate required scopes"
    - "Pagination issues - check nextLink handling"
```

## Development Workflow Protocols

### Primary Development Workflow
```yaml
development_flow:
  setup:
    - "Install with: uv sync"
    - "Configure .env with MICROSOFT_CLIENT_ID"
    - "Run authenticate.py for initial account setup"
  
  adding_features:
    1. "Identify Microsoft Graph endpoint needed"
    2. "Add method to MicrosoftGraph class in graph.py"
    3. "Create corresponding tool in tools.py"
    4. "Add integration test in test_integration.py"
    5. "Update README with usage example"
  
  testing:
    - "Run tests: uv run pytest -v"
    - "Check types: uv run pyright"
    - "Format code: uv run ruff format"
    - "Lint: uv run ruff check"
```

### Code Review Protocol
```yaml
review_checklist:
  microsoft_graph_integration:
    - "Correct API endpoint and version (v1.0 vs beta)"
    - "Proper scope requirements documented"
    - "Error handling for Graph API responses"
    - "Pagination support where applicable"
  
  mcp_tool_design:
    - "Clear tool names and descriptions"
    - "Consistent account_id parameter pattern"
    - "Proper input validation"
    - "Meaningful return values"
  
  authentication:
    - "Token refresh handling"
    - "Multi-account isolation"
    - "Secure token storage"
```

## Code Quality Protocols

### Analysis Tools Protocol
```yaml
quality_tools:
  type_checking:
    command: "uv run pyright"
    focus_areas:
      - "Graph API response types"
      - "Tool parameter types"
      - "Async function signatures"
  
  linting:
    command: "uv run ruff check"
    autofix: "uv run ruff check --fix"
  
  formatting:
    command: "uv run ruff format"
    check_only: "uv run ruff format --check"
  
  testing:
    all_tests: "uv run pytest -v"
    specific_test: "uv run pytest -v -k 'test_name'"
    with_output: "uv run pytest -v -s"
```

### Testing Strategy Protocol
```yaml
test_approach:
  integration_tests:
    - "Test against real Microsoft Graph API"
    - "Clean up created resources (emails, events, etc.)"
    - "Verify multi-account scenarios"
    - "Test error conditions (invalid IDs, permissions)"
  
  test_patterns:
    - "Use pytest-asyncio for async tests"
    - "Create helper functions for common operations"
    - "Ensure idempotent test execution"
    - "Test both success and failure paths"
```

## Microsoft Graph Specific Protocols

### Graph API Integration Protocol
```yaml
graph_api_patterns:
  request_handling:
    - "Use v1.0 endpoints for stable features"
    - "Use beta endpoints only when necessary"
    - "Always handle pagination with @odata.nextLink"
    - "Implement exponential backoff for retries"
  
  common_endpoints:
    mail: "/me/messages, /me/mailFolders"
    calendar: "/me/events, /me/calendar/getSchedule"
    files: "/me/drive/root, /me/drive/items"
    contacts: "/me/contacts"
    search: "/search/query"
  
  error_handling:
    - "401: Token expired or invalid"
    - "403: Insufficient permissions"
    - "429: Rate limit exceeded"
    - "404: Resource not found"
```

### Authentication Protocol
```yaml
auth_management:
  initial_setup:
    - "Register app in Azure Portal"
    - "Configure redirect URI: http://localhost:53000"
    - "Enable device code flow"
    - "Set required API permissions"
  
  token_management:
    - "Cache tokens in ~/.microsoft_mcp_token_cache.json"
    - "Refresh tokens automatically on expiry"
    - "Support multiple accounts with account_id"
    - "Clear expired tokens on failure"
  
  required_scopes:
    - "Mail.ReadWrite"
    - "Mail.Send"
    - "Calendars.ReadWrite"
    - "Contacts.ReadWrite"
    - "Files.ReadWrite.All"
    - "Sites.Read.All"
    - "offline_access"
```

## MCP Tool Development Protocols

### Tool Creation Protocol
```yaml
new_tool_pattern:
  structure:
    1. "Define tool with @server.tool()"
    2. "First parameter: account_id: str"
    3. "Clear docstring with usage example"
    4. "Input validation"
    5. "Call graph.request() with appropriate endpoint"
    6. "Return meaningful data structure"
  
  naming_convention:
    - "Verb_noun format (e.g., list_emails, create_event)"
    - "Consistent with Microsoft Graph terminology"
    - "Clear and descriptive"
  
  example:
    ```python
    @server.tool()
    async def list_emails(
        account_id: str,
        folder_name: Optional[str] = None,
        limit: int = 10
    ) -> str:
        '''List emails from the inbox'''
        # Implementation
    ```
```

### Attachment Handling Protocol
```yaml
attachment_patterns:
  upload_strategy:
    - "< 3MB: Direct upload via attachments endpoint"
    - ">= 3MB: Create upload session for chunked upload"
    - "Always encode content as base64"
    - "Set proper content-type"
  
  download_handling:
    - "Get attachment metadata first"
    - "Download content separately"
    - "Handle base64 decoding"
    - "Save with original filename"
```

## Project Management Protocols

### Task Management Protocol
```yaml
task_tracking:
  feature_development:
    - "Create issue for new Graph API integration"
    - "Document required scopes"
    - "Update README with examples"
    - "Add integration tests"
  
  bug_fixing:
    - "Reproduce with minimal example"
    - "Check Graph API documentation"
    - "Verify authentication state"
    - "Test with multiple accounts"
```

### Documentation Protocol
```yaml
documentation_updates:
  when_adding_tools:
    - "Update README with usage example"
    - "Document required permissions"
    - "Add to tool list in overview"
    - "Include error scenarios"
  
  api_changes:
    - "Update type hints"
    - "Revise docstrings"
    - "Update integration tests"
    - "Note breaking changes"
```

## Deployment and Operations Protocols

### Server Deployment Protocol
```yaml
deployment_steps:
  local_development:
    - "Use 'uv run mcp dev' for testing"
    - "Check authentication flow"
    - "Verify all tools accessible"
  
  production_setup:
    - "Set MICROSOFT_CLIENT_ID in environment"
    - "Configure token cache location"
    - "Set appropriate log levels"
    - "Monitor rate limits"
```

### Monitoring Protocol
```yaml
operational_monitoring:
  key_metrics:
    - "Authentication success rate"
    - "Graph API response times"
    - "Rate limit encounters"
    - "Token refresh frequency"
  
  error_patterns:
    - "Token expiration cascades"
    - "Permission escalation needs"
    - "API deprecation warnings"
```

## Self-Improvement Protocols

### Learning Capture Protocol
```yaml
continuous_learning:
  after_each_session:
    - "Document new Graph API endpoints used"
    - "Note permission requirements discovered"
    - "Update error handling patterns"
    - "Share authentication insights"
  
  knowledge_updates:
    - "Track Microsoft Graph API changes"
    - "Monitor new beta endpoints"
    - "Update deprecated API usage"
    - "Enhance error messages"
```

### Performance Optimization Protocol
```yaml
optimization_areas:
  api_efficiency:
    - "Batch requests where possible"
    - "Use $select to limit response data"
    - "Implement proper caching strategies"
    - "Optimize pagination chunk sizes"
  
  mcp_performance:
    - "Minimize tool response sizes"
    - "Stream large responses"
    - "Cache frequently accessed data"
    - "Reuse HTTP client connections"
```

## Quick Start Guide

1. **Initial Setup**:
   ```bash
   # Clone and install
   git clone <repo>
   cd microsoft-mcp
   uv sync
   
   # Configure
   cp .env.example .env
   # Add your MICROSOFT_CLIENT_ID
   
   # Authenticate
   uv run python scripts/authenticate.py
   ```

2. **Development Workflow**:
   ```bash
   # Run tests
   uv run pytest -v
   
   # Type check
   uv run pyright
   
   # Format code
   uv run ruff format
   
   # Start MCP server
   uv run mcp dev
   ```

3. **Adding a New Tool**:
   - Find the Graph API endpoint in Microsoft docs
   - Add method to `graph.py`
   - Create tool in `tools.py`
   - Write integration test
   - Update documentation

4. **Common Tasks**:
   - List emails: `list_emails(account_id)`
   - Send email: `send_email(account_id, to, subject, body)`
   - Create event: `create_calendar_event(account_id, subject, start, end)`
   - Search files: `search_files(account_id, query)`

## Custom Commands

### /test-auth
Test authentication for all configured accounts:
```python
for account in list_accounts():
    try:
        graph = get_graph_for_account(account["id"])
        await graph.request("/me")
        print(f"✓ {account['name']} authenticated")
    except Exception as e:
        print(f"✗ {account['name']}: {e}")
```

### /graph-explore [endpoint]
Explore Microsoft Graph API endpoints:
```python
result = await graph.request(endpoint)
print(json.dumps(result, indent=2))
```

### /check-scopes
Verify current token scopes:
```python
token = get_cached_token(account_id)
print("Current scopes:", token.get("scope", "").split())
```

## Success Metrics

- ✅ All Microsoft Graph operations properly authenticated
- ✅ Multi-account scenarios work seamlessly
- ✅ Error messages clearly indicate resolution steps
- ✅ Tests pass reliably without manual cleanup
- ✅ New tools follow established patterns
- ✅ Documentation stays current with implementation
- ✅ Rate limits handled gracefully
- ✅ Token refresh happens automatically