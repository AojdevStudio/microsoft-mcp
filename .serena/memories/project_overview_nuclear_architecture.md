# Microsoft MCP - Nuclear Architecture Overview

## Project Purpose
Microsoft Graph API integration server that provides AI assistants with comprehensive access to Microsoft 365 services through the Model Context Protocol (MCP). Enables natural language automation of email, calendar, file management, and contact operations across multiple Microsoft accounts.

## Nuclear Simplification Status ✅ COMPLETE
- **MAJOR MILESTONE**: Nuclear simplification successfully completed
- Reduced from monolithic 63k token unified tool to 5 focused tools (90% reduction)
- Tool count reduced from 61+ to 5 focused tools
- Action-based routing with `account_id` + `action` pattern implemented

## Current Architecture (Post-Nuclear)
### Core Components:
1. **MCP Server Entry Point**: `src/microsoft_mcp/server.py`
2. **Tools Module**: `src/microsoft_mcp/tools.py` - Central hub with 5 focused tools
3. **Authentication Layer**: `src/microsoft_mcp/auth.py` - Multi-account MSAL auth
4. **Graph API Client**: `src/microsoft_mcp/graph.py` - Microsoft Graph wrapper
5. **Email Framework**: `src/microsoft_mcp/email_framework/` - Professional templates

### 5 Focused Tools:
- `email_operations()` - Email management (send, list, reply, draft, delete)
- `calendar_operations()` - Calendar events and scheduling
- `contact_operations()` - Contact management
- `file_operations()` - OneDrive file operations
- `auth_operations()` - Authentication management

## Key Design Patterns
- **Multi-Account Architecture**: Every tool requires `account_id` as first parameter
- **Action-Based Routing**: Use `action` parameter to specify operation
- **Unified Error Handling**: Consistent error responses across all tools
- **Pagination Support**: Built into listing operations with `limit` parameter

## Development Status
- Nuclear simplification COMPLETE ✅
- All Microsoft Graph operations functional
- Pagination bug fixed (December 2024)
- Professional email framework preserved as utilities
- Production-ready for Microsoft 365 automation