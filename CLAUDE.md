# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a **Microsoft Graph API integration server** that provides AI assistants with comprehensive access to Microsoft 365 services through the Model Context Protocol (MCP). It enables natural language automation of email, calendar, file management, and contact operations across multiple Microsoft accounts.

**Primary Goal**: Create a robust, secure bridge between AI systems and Microsoft's ecosystem, enabling intelligent productivity automation through conversational interfaces.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Set required environment variable
export MICROSOFT_MCP_CLIENT_ID="your-azure-app-id"

# Run authentication script
uv run authenticate.py
```

### Running the Server
```bash
# Run MCP server
uv run microsoft-mcp

# Or directly via Python
uv run python -m microsoft_mcp.server
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_create_calendar_event.py

# Run email framework tests
uv run pytest tests/email_framework/

# Run with coverage
uv run pytest --cov=microsoft_mcp
```

### Email Framework Testing
```bash
# Run email framework test runner (generates sample emails)
uv run python -m microsoft_mcp.email_framework.test_runner
```

## High-Level Architecture

### Core Components

1. **MCP Server Entry Point**: `src/microsoft_mcp/server.py`
   - Minimal entry point that validates environment and launches the MCP server
   - All functionality is exposed through tools defined in `tools.py`

2. **Tools Module**: `src/microsoft_mcp/tools.py` 
   - Central hub containing MCP tool definitions (consolidating from 61 → 15)
   - NEW: Unified `microsoft_operations` tool with action-based routing
   - Each tool maps to Microsoft Graph API operations
   - Handles multi-account support via `account_id` parameter
   - Email actions complete (list, send, reply, draft, delete)

3. **Authentication Layer**: `src/microsoft_mcp/auth.py`
   - Manages MSAL authentication for multiple Microsoft accounts
   - Stores tokens in `~/.microsoft-mcp/tokens.json`
   - Handles token refresh and device flow authentication

4. **Graph API Client**: `src/microsoft_mcp/graph.py`
   - Wrapper around Microsoft Graph API endpoints
   - Manages HTTP requests, error handling, and response parsing
   - Implements pagination for large result sets

5. **Email Framework**: `src/microsoft_mcp/email_framework/`
   - Professional email template system with KamDental branding
   - CSS-in-Python approach with inline style conversion
   - Theme system (Baytown blue, Humble green, Executive dark)
   - Email client compatibility layer for consistent rendering

### Key Design Patterns

- **Multi-Account Architecture**: Every tool requires `account_id` as first parameter
- **Unified Error Handling**: Consistent error responses across all tools
- **Pagination Support**: Built into listing operations (emails, files, events)
- **Template Inheritance**: Email templates extend base template for consistency
- **CSS Inlining**: Automatic conversion for email client compatibility

### Current Refactoring Focus

The codebase is undergoing ultra-consolidation to:
- Reduce tool count from 61 to 15 (75% reduction) - IN PROGRESS
- **NEW**: Unified `microsoft_operations` tool with action-based routing (Story 1.2 COMPLETE)
- Email actions implemented: `email.list`, `email.send`, `email.reply`, `email.draft`, `email.delete`
- Professional email styling preserved as utilities in `email_framework/utils.py`
- Next: Calendar actions (Story 1.3), File & Contact actions (Story 1.4)
- Parameter validation framework from Story 1.1 integrated throughout

## Development Workflow

- Archive deprecated files in `.old-files/` directory (do not delete)
- Follow DRY principles to avoid code duplication
- Maintain separation of concerns between API and business logic
- All new tools must support multi-account via `account_id` parameter
- Email templates are utilities, not separate tools

### Unified Tool Usage & Migration

```python
# Example: Using the new microsoft_operations tool
result = microsoft_operations(
    account_id="user@company.com",
    action="email.send",
    data={
        "to": "recipient@example.com",
        "subject": "Monthly Report",
        "body": "Please find attached...",
        "cc": ["manager@company.com"],
        "attachments": ["/path/to/report.pdf"]
    },
    template="practice_report",  # Optional: Apply professional template
    options={"priority": "high"}
)

# Migration from old tools to unified tool:
# OLD: send_email(account_id, to, subject, body, cc, bcc, attachments)
# NEW: microsoft_operations(account_id, "email.send", data={...})

# OLD: list_emails(account_id, folder, limit, skip, search_query)  
# NEW: microsoft_operations(account_id, "email.list", data={...}, options={...})
```