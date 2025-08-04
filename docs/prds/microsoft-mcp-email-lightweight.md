# Microsoft MCP Email-Only Lightweight Server

## Metadata
- **Priority:** High
- **Status:** Backlog
- **Assignee:** AI Agent
- **Estimate:** 40 Story Points / 80 Hours
- **Issue ID:** MSFT-601
- **Labels:** 
  - type:feature
  - priority:high
  - agent-ready
  - architecture
  - email-focused
  - lightweight

## Problem Statement

### What
Create a lightweight, email-focused version of the Microsoft MCP server that strips away non-essential functionality while maintaining the robust email capabilities and specialized templates. This lightweight server should focus exclusively on email operations, reducing complexity, dependencies, and resource requirements while preserving the high-quality HTML formatting and template system.

### Why
The current Microsoft MCP server provides 59 tools across email, calendar, file management, and contacts. For use cases that only require email functionality, this creates unnecessary complexity, larger resource footprint, and additional dependencies. A lightweight email-only version would:

- Reduce deployment complexity and resource requirements
- Minimize attack surface by removing unused functionality  
- Simplify authentication and configuration
- Faster startup and reduced memory usage
- Easier maintenance and debugging for email-specific use cases
- Enable deployment in resource-constrained environments

### Context
The full Microsoft MCP server excels at comprehensive Microsoft 365 integration but can be overkill for email-only automation scenarios. Many AI assistants and automation workflows only need robust email capabilities with professional formatting. The existing email framework with specialized templates (practice reports, executive summaries, provider updates, alert notifications) represents significant value that should be preserved in a focused implementation.

## Acceptance Criteria

- [ ] **AC1:** Email-only server includes exactly 25+ essential email tools from the full 59-tool suite, maintaining all core email operations (list, send, reply, forward, search, manage)
- [ ] **AC2:** All four specialized email templates are fully functional: practice reports, executive summaries, provider updates, and alert notifications with identical formatting quality
- [ ] **AC3:** Professional HTML email formatting system is preserved with CSS inlining, cross-client compatibility, and automatic signature management
- [ ] **AC4:** Simplified authentication flow supports multi-account management but removes calendar/file-specific auth flows
- [ ] **AC5:** Server startup time is reduced by at least 50% compared to full server, with memory usage under 128MB baseline
- [ ] **AC6:** All email tools maintain identical API interfaces to ensure compatibility with existing client implementations
- [ ] **AC7:** Comprehensive test suite covers all email functionality with 90%+ code coverage
- [ ] **AC8:** Documentation clearly explains feature differences from full server and migration path

## Technical Requirements

### Implementation Notes

**Core Email Tools Selection (25+ tools):**
- Authentication: `list_accounts`, `authenticate_account`, `complete_authentication`
- Email Management: `list_emails`, `send_email`, `reply_to_email`, `forward_email`, `create_email_draft`, `get_email`, `search_emails`, `mark_email_as_read`
- Attachment Handling: `download_email_attachments`, `batch_download_attachments`
- Email Metadata: `get_email_headers`, `get_email_signature`, `get_email_categories`, `get_mailbox_statistics`
- Specialized Templates: `send_practice_report`, `send_executive_summary`, `send_provider_update`, `send_alert_notification`

**Architecture Decisions:**
- Maintain existing email framework structure under `src/microsoft_mcp/email_framework/`
- Keep CSS system and HTML rendering intact for professional formatting
- Preserve multi-account authentication but simplify scope requests
- Remove calendar, file management, and contact management modules entirely
- Maintain Microsoft Graph API integration patterns for consistency
- Use same error handling and rate limiting as full implementation

**Performance Optimizations:**
- Remove unused import statements and dependencies where possible
- Implement lazy loading for email templates
- Optimize Graph API scope requests to email-only permissions
- Reduce memory footprint by eliminating non-email data structures

**Security Considerations:**
- Maintain same authentication security model
- Reduce attack surface by removing unused endpoints
- Preserve token management and refresh mechanisms
- Keep audit logging for email operations

### Testing Requirements
- [ ] **Unit Tests** - Framework: pytest, Coverage: 90%+, Location: `tests/email_framework/`
- [ ] **Integration Tests** - Framework: pytest + httpx mock, Location: `tests/integration/email/`
- [ ] **E2E Tests** - Framework: pytest with live Graph API, Location: `tests/e2e/email/`
- [ ] **Performance Tests** - Memory usage, startup time, email processing throughput
- [ ] **Template Tests** - All four specialized templates with various data scenarios

### Dependencies
- **Blockers:** None - can be developed independently
- **Related:** Full Microsoft MCP server (reference implementation)
- **Files to Create:**
  - `src/microsoft_mcp_email/server.py` (new lightweight server entry point)
  - `src/microsoft_mcp_email/tools.py` (email-only tools subset)
  - `src/microsoft_mcp_email/__init__.py` (package initialization)
  - `pyproject_email.toml` (lightweight dependencies)
- **Files to Copy/Adapt:**
  - All files from `src/microsoft_mcp/email_framework/` (preserve email templates)
  - Authentication logic from `src/microsoft_mcp/auth.py` (simplified scope)
  - Graph API client from `src/microsoft_mcp/graph_client.py` (email-focused)

## Definition of Done
- [ ] All acceptance criteria met and verified
- [ ] Code reviewed and approved by senior developer
- [ ] Tests written and passing with 90%+ coverage
- [ ] Performance benchmarks meet target requirements (50% startup improvement)
- [ ] Documentation updated with clear feature comparison
- [ ] Deployed to staging environment successfully
- [ ] Manual verification of all email tools completed
- [ ] Package published with clear versioning scheme
- [ ] Migration guide created for users switching from full server

## Agent Context

### Reference Materials
- [Microsoft MCP Tools Architecture](/Users/ossieirondi/Projects/local-mcps/microsoft-mcp/docs/architecture/microsoft-mcp-tools.md)
- [Current Email Framework Implementation](/Users/ossieirondi/Projects/local-mcps/microsoft-mcp/src/microsoft_mcp/email_framework/)
- [Microsoft Graph API Email Documentation](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [Professional Email Template Examples](/Users/ossieirondi/Projects/local-mcps/microsoft-mcp/src/microsoft_mcp/email_framework/templates/)

### Integration Points
- **Authentication System**: Simplified Microsoft Graph authentication with email-only scopes
- **Email Templates**: Preserve all four specialized templates with identical functionality
- **CSS Framework**: Maintain professional HTML formatting and cross-client compatibility
- **Graph API Client**: Focused email operations with same error handling patterns
- **Multi-Account Support**: Preserve account management capabilities for email operations
- **MCP Protocol**: Maintain compatibility with existing MCP clients and tools

## Validation Steps

### Automated Verification
- [ ] Build pipeline passes for lightweight package
- [ ] All email tool tests green (unit, integration, E2E)
- [ ] Code quality checks pass with same standards as full server
- [ ] Security scans clean with reduced attack surface
- [ ] Performance benchmarks meet improvement targets
- [ ] Template rendering tests pass for all four specialized templates

### Manual Verification
1. **Authentication Flow**: Verify device flow works with email-only scopes, multi-account support functions correctly
2. **Email Operations**: Test all 25+ email tools work identically to full server implementation
3. **Template Rendering**: Verify practice reports, executive summaries, provider updates, and alert notifications render with identical quality
4. **HTML Formatting**: Confirm professional styling, signature management, and cross-client compatibility
5. **Performance Testing**: Measure startup time reduction, memory usage under load, email processing throughput
6. **Error Handling**: Test authentication failures, rate limiting, network issues maintain same behavior
7. **Attachment Handling**: Verify file attachment upload/download works correctly
8. **Search Functionality**: Test email search with various queries and filters

## Agent Execution Record

### Branch Strategy
- **Name Format:** feature/MSFT-601-email-lightweight-server
- **Linear Example:** feature/MSFT-601-email-lightweight-server

### PR Strategy
Link to this issue using: Fixes MSFT-601

### Implementation Approach

**Phase 1: Core Architecture (20 hours)**
- Create new package structure for lightweight server
- Extract and adapt authentication system for email-only scopes
- Implement email-focused Graph API client
- Set up build system and dependencies

**Phase 2: Email Tools Migration (25 hours)**
- Port all 25+ email tools from full server
- Ensure API compatibility and identical behavior
- Implement proper error handling and rate limiting
- Add comprehensive logging for email operations

**Phase 3: Template System Integration (15 hours)**
- Preserve email framework with all CSS and rendering capabilities
- Ensure all four specialized templates work identically
- Test HTML formatting and cross-client compatibility
- Validate signature management and professional styling

**Phase 4: Testing & Optimization (20 hours)**
- Implement comprehensive test suite
- Performance optimization and benchmarking
- Documentation and migration guide creation
- Security review and validation

### Completion Notes
[To be filled during implementation]

### PR Integration
- **Linear Magic Words:** Fixes MSFT-601
- **Auto Close Trigger:** PR merge to main branch
- **Status Automation:** Issue will auto-move from 'In Progress' to 'Done'

### Debug References
[To be populated during development]

### Change Log
[Track changes made during implementation]

## Bot Automation Integration

### Branch Naming for Auto-Linking
- feature/MSFT-601-email-lightweight-server

### PR Description Template
```markdown
## Description
Implements lightweight email-only version of Microsoft MCP server

**Features:**
- 25+ essential email tools with identical API compatibility
- All four specialized email templates preserved
- Professional HTML formatting and CSS system maintained
- Simplified authentication flow with email-only scopes
- 50%+ performance improvement in startup time and memory usage

**Linked Issues:**
- Fixes MSFT-601

## Testing
- [ ] Unit tests pass (90%+ coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks meet targets
- [ ] All email templates render correctly
```

## Performance Metrics

### Target Improvements
- **Startup Time**: < 2 seconds (vs ~4 seconds for full server)
- **Memory Usage**: < 128MB baseline (vs ~200MB+ for full server)
- **Package Size**: < 10MB installed (vs ~25MB+ for full server)
- **Import Time**: < 1 second for core modules
- **Dependencies**: ≤ 5 core dependencies (vs 10+ for full server)

### Success Criteria
- All email operations maintain identical functionality and performance
- Professional email formatting quality preserved
- Multi-account authentication works seamlessly
- Specialized templates render with identical visual quality
- Error handling and rate limiting maintain same robustness

This lightweight server represents a focused, efficient solution for email-only automation scenarios while preserving the professional quality and comprehensive functionality that makes the Microsoft MCP email system valuable.