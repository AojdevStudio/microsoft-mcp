# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CRITICAL: NUCLEAR SIMPLIFICATION ACTIVE - READ THIS FIRST
  BEFORE doing ANYTHING else:
  1. Check Archon Project 80714248-4b43-491b-9f4b-952b4f3b0bcc ONLY
  2. Follow nuclear timeline: Delete → Build → Deploy (6 hours total)
  3. NO migration compatibility code - DELETE migration frameworks
  4. Git revert as rollback strategy
  5. User is personally executing deletions

  NUCLEAR EXECUTION ACTIVE: Start with highest task_order in nuclear project.

# Archon Integration & Workflow

**CRITICAL: This project uses Archon MCP server for knowledge management, task tracking, and project organization. ALWAYS start with Archon MCP server task management.**

## Core Archon Workflow Principles

### The Golden Rule: Task-Driven Development with Archon

**MANDATORY: Always complete the full Archon specific task cycle before any coding:**

1. **Check Current Task** → `archon:manage_task(action="get", task_id="...")`
2. **Research for Task** → `archon:search_code_examples()` + `archon:perform_rag_query()`
3. **Implement the Task** → Write code based on research
4. **Update Task Status** → `archon:manage_task(action="update", task_id="...", update_fields={"status": "review"})`
5. **Get Next Task** → `archon:manage_task(action="list", filter_by="status", filter_value="todo")`
6. **Repeat Cycle**

**NEVER skip task updates with the Archon MCP server. NEVER code without checking current tasks first.**

## Project Scenarios & Initialization

### Scenario 1: New Project with Archon

```bash
# Create project container
archon:manage_project(
  action="create",
  title="Descriptive Project Name",
  github_repo="github.com/user/repo-name"
)

# Research → Plan → Create Tasks (see workflow below)
```

### Scenario 2: Existing Project - Adding Archon

```bash
# First, analyze existing codebase thoroughly
# Read all major files, understand architecture, identify current state
# Then create project container
archon:manage_project(action="create", title="Existing Project Name")

# Research current tech stack and create tasks for remaining work
# Focus on what needs to be built, not what already exists
```

### Scenario 3: Continuing Archon Project

```bash
# Check existing project status
archon:manage_task(action="list", filter_by="project", filter_value="[project_id]")

# Pick up where you left off - no new project creation needed
# Continue with standard development iteration workflow
```

### Universal Research & Planning Phase

**For all scenarios, research before task creation:**

```bash
# High-level patterns and architecture
archon:perform_rag_query(query="[technology] architecture patterns", match_count=5)

# Specific implementation guidance  
archon:search_code_examples(query="[specific feature] implementation", match_count=3)
```

**Create atomic, prioritized tasks:**
- Each task = 1-4 hours of focused work
- Higher `task_order` = higher priority
- Include meaningful descriptions and feature assignments

## Development Iteration Workflow

### Before Every Coding Session

**MANDATORY: Always check task status before writing any code:**

```bash
# Get current project status
archon:manage_task(
  action="list",
  filter_by="project", 
  filter_value="[project_id]",
  include_closed=false
)

# Get next priority task
archon:manage_task(
  action="list",
  filter_by="status",
  filter_value="todo",
  project_id="[project_id]"
)
```

### Task-Specific Research

**For each task, conduct focused research:**

```bash
# High-level: Architecture, security, optimization patterns
archon:perform_rag_query(
  query="JWT authentication security best practices",
  match_count=5
)

# Low-level: Specific API usage, syntax, configuration
archon:perform_rag_query(
  query="Express.js middleware setup validation",
  match_count=3
)

# Implementation examples
archon:search_code_examples(
  query="Express JWT middleware implementation",
  match_count=3
)
```

**Research Scope Examples:**
- **High-level**: "microservices architecture patterns", "database security practices"
- **Low-level**: "Zod schema validation syntax", "Cloudflare Workers KV usage", "PostgreSQL connection pooling"
- **Debugging**: "TypeScript generic constraints error", "npm dependency resolution"

### Task Execution Protocol

**1. Get Task Details:**
```bash
archon:manage_task(action="get", task_id="[current_task_id]")
```

**2. Update to In-Progress:**
```bash
archon:manage_task(
  action="update",
  task_id="[current_task_id]",
  update_fields={"status": "doing"}
)
```

**3. Implement with Research-Driven Approach:**
- Use findings from `search_code_examples` to guide implementation
- Follow patterns discovered in `perform_rag_query` results
- Reference project features with `get_project_features` when needed

**4. Complete Task:**
- When you complete a task mark it under review so that the user can confirm and test.
```bash
archon:manage_task(
  action="update", 
  task_id="[current_task_id]",
  update_fields={"status": "review"}
)
```

## Knowledge Management Integration

### Documentation Queries

**Use RAG for both high-level and specific technical guidance:**

```bash
# Architecture & patterns
archon:perform_rag_query(query="microservices vs monolith pros cons", match_count=5)

# Security considerations  
archon:perform_rag_query(query="OAuth 2.0 PKCE flow implementation", match_count=3)

# Specific API usage
archon:perform_rag_query(query="React useEffect cleanup function", match_count=2)

# Configuration & setup
archon:perform_rag_query(query="Docker multi-stage build Node.js", match_count=3)

# Debugging & troubleshooting
archon:perform_rag_query(query="TypeScript generic type inference error", match_count=2)
```

### Code Example Integration

**Search for implementation patterns before coding:**

```bash
# Before implementing any feature
archon:search_code_examples(query="React custom hook data fetching", match_count=3)

# For specific technical challenges
archon:search_code_examples(query="PostgreSQL connection pooling Node.js", match_count=2)
```

**Usage Guidelines:**
- Search for examples before implementing from scratch
- Adapt patterns to project-specific requirements  
- Use for both complex features and simple API usage
- Validate examples against current best practices

## Progress Tracking & Status Updates

### Daily Development Routine

**Start of each coding session:**

1. Check available sources: `archon:get_available_sources()`
2. Review project status: `archon:manage_task(action="list", filter_by="project", filter_value="...")`
3. Identify next priority task: Find highest `task_order` in "todo" status
4. Conduct task-specific research
5. Begin implementation

**End of each coding session:**

1. Update completed tasks to "done" status
2. Update in-progress tasks with current status
3. Create new tasks if scope becomes clearer
4. Document any architectural decisions or important findings

### Task Status Management

**Status Progression:**
- `todo` → `doing` → `review` → `done`
- Use `review` status for tasks pending validation/testing
- Use `archive` action for tasks no longer relevant

**Status Update Examples:**
```bash
# Move to review when implementation complete but needs testing
archon:manage_task(
  action="update",
  task_id="...",
  update_fields={"status": "review"}
)

# Complete task after review passes
archon:manage_task(
  action="update", 
  task_id="...",
  update_fields={"status": "done"}
)
```

## Research-Driven Development Standards

### Before Any Implementation

**Research checklist:**

- [ ] Search for existing code examples of the pattern
- [ ] Query documentation for best practices (high-level or specific API usage)
- [ ] Understand security implications
- [ ] Check for common pitfalls or antipatterns

### Knowledge Source Prioritization

**Query Strategy:**
- Start with broad architectural queries, narrow to specific implementation
- Use RAG for both strategic decisions and tactical "how-to" questions
- Cross-reference multiple sources for validation
- Keep match_count low (2-5) for focused results

## Project Feature Integration

### Feature-Based Organization

**Use features to organize related tasks:**

```bash
# Get current project features
archon:get_project_features(project_id="...")

# Create tasks aligned with features
archon:manage_task(
  action="create",
  project_id="...",
  title="...",
  feature="Authentication",  # Align with project features
  task_order=8
)
```

### Feature Development Workflow

1. **Feature Planning**: Create feature-specific tasks
2. **Feature Research**: Query for feature-specific patterns
3. **Feature Implementation**: Complete tasks in feature groups
4. **Feature Integration**: Test complete feature functionality

## Error Handling & Recovery

### When Research Yields No Results

**If knowledge queries return empty results:**

1. Broaden search terms and try again
2. Search for related concepts or technologies
3. Document the knowledge gap for future learning
4. Proceed with conservative, well-tested approaches

### When Tasks Become Unclear

**If task scope becomes uncertain:**

1. Break down into smaller, clearer subtasks
2. Research the specific unclear aspects
3. Update task descriptions with new understanding
4. Create parent-child task relationships if needed

### Project Scope Changes

**When requirements evolve:**

1. Create new tasks for additional scope
2. Update existing task priorities (`task_order`)
3. Archive tasks that are no longer relevant
4. Document scope changes in task descriptions

## Quality Assurance Integration

### Research Validation

**Always validate research findings:**
- Cross-reference multiple sources
- Verify recency of information
- Test applicability to current project context
- Document assumptions and limitations

### Task Completion Criteria

**Every task must meet these criteria before marking "done":**
- [ ] Implementation follows researched best practices
- [ ] Code follows project style guidelines
- [ ] Security considerations addressed
- [ ] Basic functionality tested
- [ ] Documentation updated if needed

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
uv run pytest tests/email-framework/

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
   - Implements pagination for large result sets (`request_paginated` with `limit` parameter)

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

### Nuclear Simplification Complete ✅

**MAJOR MILESTONE**: Nuclear simplification successfully completed with focused tool architecture:

- **✅ COMPLETE**: Reduced from monolithic 63k token unified tool to 5 focused tools (90% reduction)
- **✅ COMPLETE**: Email, Calendar, Contact, File, and Auth operations fully functional
- **✅ COMPLETE**: Action-based routing with `account_id` + `action` pattern
- **✅ COMPLETE**: Professional email framework preserved as utilities
- **✅ COMPLETE**: Multi-account support across all operations
- **✅ CRITICAL FIX**: Resolved pagination parameter mismatch bug (Dec 2024)

**Current Architecture Status:**
- 5 focused tools: `email_tool.py`, `calendar_tool.py`, `contact_tool.py`, `file_tool.py`, `auth_tool.py`
- Unified error handling and consistent API patterns
- All Microsoft Graph pagination operations now functional

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

## Recent Updates (Updated: 2024-12-25)

### Critical Bug Fixes
- **🐛 Pagination Parameter Mismatch (Dec 2024)**: Resolved critical bug where all Microsoft Graph pagination operations were failing due to parameter name mismatch (`max_items` vs `limit`). This affected email listing, contact search, file browsing, and calendar operations across all 4 core tools.

### Nuclear Simplification Completion
- **🚀 Nuclear Architecture Deployed**: Successfully replaced monolithic 63k token unified tool with 5 focused, modular tools achieving 90% token reduction
- **✅ All Operations Functional**: Email, Calendar, Contact, File, and Auth operations all working with action-based routing
- **🔧 Infrastructure Improvements**: Enhanced error handling, consistent API patterns, and reliable pagination across all Microsoft Graph operations

### Architecture Achievements
- Tool count reduced from 61+ to 5 focused tools
- Consistent `account_id` + `action` parameter pattern
- Professional email framework preserved as reusable utilities
- Multi-account support across all Microsoft 365 services
- Robust pagination system now fully operational

## Important Notes

### For Developers
- **Pagination Fixed**: All Microsoft Graph listing operations (emails, contacts, files, events) now work correctly
- **Action-Based Tools**: Use `email_operations()`, `calendar_operations()`, etc. with appropriate action parameters
- **Multi-Account Support**: Every tool requires `account_id` as the first parameter
- **Error Handling**: Consistent error response format across all operations

### For AI Assistants
- Microsoft MCP server is now production-ready for Microsoft 365 automation
- All pagination bugs resolved - email listing, contact search, and file operations work reliably
- Professional email templates available through utilities in `email_framework/`
- Comprehensive access to Microsoft Graph API through simplified, focused tools